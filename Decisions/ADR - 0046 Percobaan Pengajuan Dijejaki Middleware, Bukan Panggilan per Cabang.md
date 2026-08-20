> **Status**: 🟡 Kode selesai di branch, BELUM merge dan BELUM deploy (20 Agustus 2026). Ini **potongan A** dari empat potongan yang disepakati (lihat §Ruang Lingkup); B dan C belum dirancang. Implementasi ada di branch `feat/attendance-jejak-pengajuan` (bip-erp), sudah lewat review per-task dan satu review menyeluruh; gerbang dev di §9 **belum dijalankan**, jadi belum ada satu pun bukti fitur ini bekerja lewat gateway.

## Context

**20 Agustus 2026, prod.** Ada laporan pengajuan Sakit dua hari berlampir foto yang gagal. Penyelidikan menemukan `POST /request/create` dipanggil **18 kali** hari itu: **15 ditolak 400**, 3 berhasil (semuanya `Izin / Meninggalkan perkerjaan sementara`, tanpa lampiran). Pola retry-nya kentara: enam percobaan dalam 90 detik, lalu tiga lagi tujuh menit kemudian.

**Alasan penolakannya tidak bisa ditemukan sama sekali**, padahal kejadiannya baru beberapa jam sebelumnya dan seluruh infrastruktur masih hidup. Yang tersedia dan kenapa masing-masing tak cukup:

| Sumber | Isinya | Kenapa tak menjawab |
|---|---|---|
| Access log Fiber (`log/fiber/*.log`) | waktu, status, latensi, path | tak ada alasan, tak ada identitas, hilang tiap container dibuat ulang |
| Stdout (`docker logs`) | hanya `log.Println` | handler tak menulis apa pun saat menolak: nol entri |
| Firebase Performance | `httpResponseCode` per URL | agregat dan anonim |
| Firebase Crashlytics | `recordError` di 6 titik | semuanya di jalur auth, pengajuan tak dilaporkan |
| `leave_request.metadata` | `created_by` / `created_at` | hanya mencatat yang **berhasil** |

Polanya: **yang berhasil tercatat, yang gagal lenyap.** Tak ada satu pun koleksi audit di `attendance_db`; seluruh koleksinya data domain.

Dua hal lain yang memperparah, dan keduanya di luar lingkup ADR ini tapi menjelaskan kenapa pertanyaannya sampai naik:

- Alasan penolakan **ditelan dua kali di aplikasi**: `DioApi` hanya mengambil `response.statusMessage` dan membuang badan `{"error": ...}`, lalu halaman pratinjau pengajuan menampilkan string tetap "Gagal mengirim pengajuan" tanpa membaca `state.errorMessage`. Jadi karyawan tak pernah tahu apa yang salah, yang menjelaskan retry beruntun di atas. Lihat [[APP - MyBharata]].
- Latensi ke-15 penolakan itu 5-21 ms dan statusnya **400, bukan 413**, sehingga dugaan "fotonya lebih dari 4 MB" justru **gugur**: permintaan tak pernah sampai ke file-service. Lampiran terbesar yang pernah tersimpan 3,65 MB, mepet ke plafon 4 MB, jadi masalah ukuran kemungkinan nyata tapi bukan penyebab hari itu.

### Ruang Lingkup

Kebutuhan penuh dipecah empat karena mekanismenya berbeda. **ADR ini hanya A.**

- **A. Jejak percobaan di server** (ADR ini). Hanya attendance-service, tanpa menyentuh aplikasi maupun frontend.
- **B. Permukaan baca untuk HR/atasan.** Endpoint berpaginasi + RBAC + halaman [[APP - Web ERP]]. Bergantung pada A.
- **C. Telemetri dari aplikasi.** Satu-satunya cara melihat percobaan yang ditolak di HP atau tak pernah terkirim. Perlu antrean offline dan rilis app.
- **D. Retensi dan privasi.** Bukan proyek terpisah: diputus **di dalam** A karena A yang menentukan apa yang tersimpan.

## Decision

**1. Satu koleksi `submission_attempt` di `attendance_db`, skema tunggal untuk empat pintu dan untuk sumber klien nanti.**

Pintu yang dicakup: `POST /request/create` (Sakit/Izin/Cuti/Dinas), `POST /correction`, `POST /schedule-exchange/create`, `POST /business-trip/create`. Dibedakan lewat field `kind`, dengan `payload` berupa ringkasan per-pintu.

A dan C **wajib menulis ke koleksi yang sama**, dibedakan hanya oleh field `source` (`server` / `client`). Memisahkannya akan melahirkan dua sumber kebenaran tentang hal yang sama, dan itu kelas masalah yang sudah berulang di sistem ini. Konsekuensinya skema dirancang sekali sekarang walau C dikerjakan belakangan.

```go
// SubmissionAttempt = jejak SATU percobaan pengajuan, berhasil maupun ditolak.
// TIDAK PERNAH memuat teks alasan yang diketik karyawan, dan tidak pernah isi lampiran.
type SubmissionAttempt struct {
    ID        primitive.ObjectID `bson:"_id,omitempty"`

    AttemptID string `bson:"attempt_id,omitempty"` // dari klien; kosong utk app lama
    Source    string `bson:"source"`               // "server" | "client"

    // Distempel server dari header gateway, tak pernah dari body.
    EmployeeID string `bson:"employee_id"`
    FullName   string `bson:"full_name"`
    Department string `bson:"department"`
    Position   string `bson:"position"`
    CompanyID  string `bson:"company_id"`

    Kind    string         `bson:"kind"`              // leave | correction | schedule_exchange | business_trip
    Payload map[string]any `bson:"payload,omitempty"` // ringkasan per pintu, daftar-izin

    Attachment *AttemptAttachment `bson:"attachment,omitempty"`

    Status     int    `bson:"status"`                // status HTTP
    Outcome    string `bson:"outcome"`               // created | duplicate | rejected | unknown
    RejectCode string `bson:"reject_code,omitempty"` // stabil, untuk disaring
    RejectMsg  string `bson:"reject_msg,omitempty"`  // mentah, untuk dibaca manusia

    At        time.Time `bson:"at"`
    LatencyMs int64     `bson:"latency_ms"`
}

type AttemptAttachment struct {
    Present  bool   `bson:"present"`
    SizeByte int64  `bson:"size_byte,omitempty"`
    Mime     string `bson:"mime,omitempty"` // dari header part
    Ext      string `bson:"ext,omitempty"`  // dari nama berkas
}
```

Index: TTL di `at` (lihat #6), lalu `{company_id, employee_id, at:-1}` untuk telusur per karyawan dan `{company_id, outcome, at:-1}` untuk menyaring yang gagal. Keduanya melayani potongan B.

**2. Dicatat lewat middleware tingkat rute, BUKAN panggilan helper di tiap cabang.**

Ini keputusan inti ADR ini. Alternatif "helper eksplisit di tiap `return`" meniru `writeAudit()` milik manufacture ([[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] #6) dan lebih presisi, tapi menuntut sekitar 30 titik panggilan di empat handler. Handler `/request/create` sendiri punya sembilan titik `return`.

**Satu titik yang kelewat berarti cabang itu tak terlihat tanpa gejala apa pun**, dan siapa pun yang menambah cabang penolakan baru bulan depan tak akan tahu harus menambahkan panggilannya. Middleware memberi kelengkapan **secara konstruksi**, bukan lewat ingatan orang.

Middleware boleh membaca form multipart yang sama dengan handler: Fiber meneruskan `c.MultipartForm()` ke fasthttp yang **menyimpan hasil parse-nya**, sehingga panggilan kedua mengembalikan objek yang sama tanpa mengurai ulang. Diverifikasi ke `fasthttp v1.68.0` `http.go:1014-1017` (versi yang dipatok `go.mod`), bukan diasumsikan.

**3. Alasan penolakan disimpan sebagai KODE STABIL, bukan disaring dari teks pesan.**

Tiap cabang menitipkan kode mesin (`SICK_NO_ATTACHMENT`, `LEAVE_SUBTYPE_INVALID`, `FILE_UPLOAD_FAILED`, dst.) lewat `c.Locals`; middleware menyimpannya bersama pesan mentahnya. Yang belum sempat diberi kode masuk sebagai `UNCLASSIFIED` **dengan pesan mentah tetap tersimpan**, sehingga kekurangannya terbaca sebagai angka, bukan sebagai lubang senyap.

Menyaring dari teks pesan **ditolak** dengan alasan yang sudah tercatat di vault ini sendiri: amandemen [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] menolak pencocokan teks `last_error` meski 900 dari 908 baris memuat kalimatnya, karena kalimatnya bisa berubah dan penandanya lalu mati diam-diam.

Katalog untuk pintu `leave`, diturunkan dari cabang yang benar-benar ada di handler (nomor baris sengaja tak dicatat di sini karena akan basi; cari lewat nama kodenya):

| Kode | Cabang | Status |
|---|---|---|
| `MULTIPART_INVALID` | body multipart gagal diurai | 400 |
| `LEAVE_TYPE_INVALID` | jenis di luar katalog | 400 |
| `LEAVE_SUBTYPE_INVALID` | subtipe di luar katalog jenis itu | 400 |
| `SICK_NO_ATTACHMENT` | Sakit tanpa surat dokter | 400 |
| `DATE_FORMAT_INVALID` | `from_date`/`to_date` bukan RFC3339 | 400 |
| `DATE_RANGE_INVALID` | `to_date` mendahului `from_date` | 400 |
| `SAME_DAY_ONLY` | Pulang cepat / Datang terlambat bukan hari ini | 400 |
| `VACATION_QUOTA_UNSET` | kuota cuti tahunan belum disetel | 400 |
| `VACATION_QUOTA_EXCEEDED` | sisa kuota cuti kurang | 400 |
| `SUPERVISOR_NOT_FOUND` | tak ada atasan yang bisa meninjau | 500 |
| `ATTACHMENT_FORMAT_INVALID` | lampiran bukan JPEG/PNG menurut Content-Type | 400 |
| `FILE_UPLOAD_FAILED` | file-service menolak (mis. lebih dari 4 MB) | diteruskan apa adanya |
| `FILE_RESPONSE_INVALID` | balasan file-service tak bisa diurai | 500 |
| `DB_INSERT_FAILED` | insert `leave_request` gagal | 500 |

`FILE_UPLOAD_FAILED` inilah yang memisahkan 413 "lebih dari 4 MB" dari 400 "format salah". Tiga pintu lain mendapat katalognya sendiri dengan pola yang sama saat dipasang.

**4. `Outcome` dipisah dari status HTTP.**

Penjaga idempoten di `/request/create` membalas **200 untuk pengajuan kembar tanpa menyimpan apa pun**. Kalau hanya status yang disimpan, "tersimpan" dan "dianggap kembar lalu dibuang" tampil identik, padahal keluhan yang paling mungkin muncul justru "kok pengajuan saya tidak ada". Handler menitipkan `created` atau `duplicate`; **2xx tanpa titipan dicatat `unknown`**.

`unknown` itu sengaja. Jalur unggah lampiran memakai `c.Status(status)` yang bisa bernilai 0 saat transport gagal, dan fasthttp menyerialkan 0 sebagai 200 OK. Dengan `outcome` terpisah, kegagalan itu muncul sebagai angka yang bisa dihitung alih-alih menyamar jadi sukses.

**5. Payload disalin lewat DAFTAR-IZIN, dan teks alasan karyawan TIDAK disalin.**

Yang disimpan: identitas, perusahaan, departemen, jabatan, jenis + subtipe, rentang tanggal, keberadaan lampiran beserta **ukuran, mime, dan ekstensi**, status, `outcome`, kode + pesan penolakan, waktu, latensi.

Yang **tidak** disimpan: isi lampiran, dan field `reason` yang diketik karyawan. Alasannya bukan sekadar kehati-hatian: **tak satu pun dari empat belas cabang penolakan memeriksa `reason`**, jadi menyimpannya menggandakan keterangan kondisi kesehatan ke koleksi kedua dengan kontrol akses berbeda **tanpa menambah kemampuan diagnosis apa pun**.

Daftar-izin, bukan daftar-larangan: field baru yang ditambahkan ke formulir nanti **tidak** otomatis ikut tersimpan. Daftar-larangan akan membocorkannya secara default, dan yang paling mungkin ditambahkan ke formulir pengajuan justru keterangan pribadi.

`mime` dan `ekstensi` disimpan berdua karena `ValidateImageFile` memutuskan dari header Content-Type sedangkan nama objek MinIO dibentuk dari ekstensi; ketidakcocokan keduanya jadi terbaca langsung.

**Amandemen (implementasi, 20 Agustus 2026): panjang dibatasi, dan `destination` disebut eksplisit.** Enumerasi di atas tidak menyebut batas panjang, dan itu lubang nyata: karyawan yang sudah login bisa mengirim satu field berisi megabyte teks lalu menulis dokumen sebesar itu ke koleksi yang hidup setahun, sementara handler menolaknya dalam milidetik. Batas yang dipasang: nilai payload **256 karakter**, `attempt_id` **64 karakter**, `reject_msg` **300 byte** dengan pemotongan aman-UTF-8. Dipotong, bukan ditolak, karena jejak yang terpangkas tetap lebih berguna daripada jejak yang hilang.

Perlu disebut jujur bahwa `destination` (pintu perjalanan dinas) adalah **teks bebas ketikan karyawan**, sama kelasnya dengan `reason` yang justru dibuang. Ia tetap disimpan karena tanpanya penolakan di pintu itu tak bisa dibedakan satu sama lain, tapi kalau kelak terbukti memuat keterangan pribadi, ia yang pertama harus dibuang dari daftar-izin.

**Amandemen: `attachment.present` selalu ada.** Bentuk awal menghasilkan `nil` untuk pintu JSON dan `{present:false}` untuk pintu multipart tanpa berkas, yaitu tiga keadaan untuk dua makna. Kueri `attachment.present = false` karena itu tidak akan pernah menemukan pintu JSON. Kini keempat pintu selalu menghasilkan objek, sehingga `present` bisa disaring apa adanya.

**6. Retensi 1 tahun lewat TTL index**, dihapus Mongo sendiri tanpa cron. Satu tahun menutup siklus sengketa payroll bulanan sekaligus review tahunan, dua momen ketika orang benar-benar membuka lagi riwayat pengajuannya. Untuk percobaan yang berhasil isinya sebagian besar sudah ada di `leave_request`; yang benar-benar data baru adalah percobaan yang **gagal**, dan itu yang dibatasi umurnya.

**7. Identitas distempel server, `attempt_id` dari klien hanya untuk korelasi.**

Identitas diambil dari header gateway (`BIP-Employee-ID` dkk.) yang sudah ditulis ulang dari klaim JWT oleh [[CORE - API Master Gateway]], tak pernah dari body. Ini penerapan langsung [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] #6: jejak yang bisa dipalsukan bukan jejak audit.

`attempt_id` dikirim klien lewat header **`X-Attempt-Id`**, sengaja **di luar namespace `BIP-`**. Gateway menghapus daftar-tertentu header identitas lalu menulisnya ulang, tapi komentar di kode menyatakan niat membuang **seluruh** namespace `BIP-*`; header bernama `BIP-Attempt-Id` akan mati diam-diam kalau niat itu suatu hari diwujudkan se-prefix. Karena nilainya datang dari klien, ia **kunci korelasi, bukan identitas**, dan dilarang dipakai untuk kontrol akses apa pun.

**8. Ditulis sinkron; galat ditelan tapi tetap di-log.**

Menulis jejak tidak boleh pernah menggagalkan pengajuan. Tapi ditelan diam-diam adalah kelas bug yang sudah dua kali menggigit sistem ini (kategori inbox notifikasi), jadi kegagalannya tetap dicetak ke log.

Sinkron, bukan goroutine, dengan tiga alasan: volumenya puluhan per hari sehingga ongkos latensinya tak terasa di atas 5-20 ms yang sudah ada; `*fiber.Ctx` **didaur ulang** begitu handler selesai sehingga memakainya di goroutine adalah use-after-free; dan fire-and-forget bertentangan dengan tujuannya, karena yang dibangun ini alat untuk membuktikan sesuatu terjadi. Insert diberi context timeout pendek supaya Mongo yang menggantung tidak ikut menggantungkan pengajuan orang.

Middleware memeriksa `mongodb.DB == nil` lalu melewat diam-diam, karena `mongodb.GetCollection` **memanik** bila DB nil dan panik di fasthttp muncul sebagai 502 tanpa petunjuk. Jejak yang mati lebih baik daripada pengajuan yang mati.

**9. Pengujian wajib menembus Fiber.**

Test fungsi murni **tidak dihitung sebagai bukti** di sini: form-builder pernah punya 183 test hijau sementara fiturnya mustahil dipakai selama tiga hari, karena tak satu pun test melewati Fiber. Semua test memakai `app.Test(httptest.NewRequest(...))` dengan body multipart sungguhan.

Yang wajib ada: handler membalas 400 **tanpa titipan** tetap melahirkan satu record ber-`UNCLASSIFIED` (menguji jaringnya, bukan penajamnya); satu test per pintu yang menembak rute sungguhan (menangkap middleware yang lepas atau tertukar urutannya); 200 ber-titipan `duplicate` wajib tercatat `duplicate`; 200 tanpa titipan wajib `unknown`; kontrol negatif privasi yang **menyerialkan seluruh record** lalu menuntut teks alasan karyawan tak muncul di mana pun (bukan memeriksa kunci yang sudah dikenal, karena yang dicegah justru kunci yang ditambahkan orang lain nanti); insert yang sengaja digagalkan tidak mengubah respons; DB nil tidak memanik.

**Amandemen (implementasi): "satu test per pintu yang menembak rute sungguhan" hanya tercapai untuk DUA dari empat pintu.** Koreksi presensi dan perjalanan dinas mendaftarkan rutenya lewat fungsi tersendiri (`registerCorrectionRoutes`, `registerBusinessTripRoutes`) sehingga bisa didaftarkan ke app kosong lalu diperiksa lewat `app.Stack()`. Dua pintu lain (`/request/create`, `/schedule-exchange/create`) didaftarkan langsung di dalam `func main()` yang panjangnya ribuan baris dan bercampur inisialisasi Mongo serta env, jadi tak bisa diuji tanpa menjalankan `main()` penuh. Keduanya dibiarkan tanpa test kehadiran, dan itu **dicatat sebagai lubang, bukan diselesaikan dengan test palsu**: kalau seseorang menyelesaikan konflik merge di `main.go` dan `attemptTrace(...)` lenyap dari salah satu rute itu, seluruh test tetap hijau dan jejaknya berhenti diam-diam. Menutupnya menuntut memindahkan pendaftaran rute keluar dari `main()`, perubahan tersendiri yang tak layak diselundupkan ke sini.

**Gerbang terakhir bukan test**: satu perjalanan sungguhan lewat gateway di dev, mengajukan Sakit dengan foto di atas 4 MB, dan membuktikan record-nya berbunyi `FILE_UPLOAD_FAILED`. Fitur ini membuktikan dirinya pada kasus yang melahirkannya.

⚠️ **Peringatan untuk yang menjalankan gerbang itu**: bila `InternalRequestMultipart` gagal di tingkat transport ia mengembalikan status **0**, dan `c.Status(0)` diserialkan fasthttp sebagai **200**. Jadi gerbang ini bisa sah menghasilkan record berbunyi status 200 / `unknown` / `FILE_UPLOAD_FAILED` alih-alih 413. Itu jejak yang BENAR, bukan jejak yang gagal, dan justru contoh kenapa `outcome` dipisah dari status di #4. Jangan salah baca sebagai bug.

## Consequences

**Yang membaik**

- Pertanyaan "kenapa pengajuan si A gagal" bisa dijawab dari data, bukan dari tebakan, dan tanpa menunggu kejadian terulang.
- Cabang penolakan yang ditambahkan nanti ikut tercatat tanpa penulisnya perlu tahu fitur ini ada.
- Perbedaan 413 "lebih dari 4 MB" dan 400 "format salah" jadi terbaca, pembedaan yang pada insiden 20 Agustus tidak bisa dibuktikan.
- Pengajuan yang dibuang penjaga idempoten berhenti menyamar sebagai sukses.

**Yang harus diterima**

- **Empat kelas kegagalan tetap tak tertangkap** dan ini harus disebut daripada ditemukan belakangan: permintaan yang ditolak gateway sebelum sampai ke attendance (JWT kedaluwarsa, RBAC); body melebihi `BodyLimit` 50 MB yang ditolak fasthttp sebelum rantai handler jalan; semua yang tidak pernah meninggalkan HP (memang potongan C); dan **handler yang PANIK, yang menghasilkan nol record**. Yang terakhir ditemukan saat review implementasi dan diterima sadar: `c.Next()` sengaja berada di LUAR blok `recover` milik middleware, karena menelan panik handler jauh lebih berbahaya daripada kehilangan satu jejak. Akibatnya satu-satunya mode gagal yang tak punya respons HTTP sama sekali juga tak punya jejak. Keempatnya bukan alasan menunda A, tapi ketiadaan record **tidak boleh dibaca sebagai "tidak pernah terjadi"**.

- **Jaminannya "satu record per permintaan yang DILIHAT attendance", bukan per ketukan orang.** `routes.Reroute` di gateway memakai `http.Client` yang bisa memutar ulang POST saat koneksi keep-alive mati, jadi satu ketukan sah bisa menghasilkan dua record. Untuk fitur ini itu justru informasi, tapi siapa pun yang menghitung dari koleksi ini perlu tahu.

- **Katalog pintu koreksi presensi berisi 16 kode, bukan 14** seperti rancangan awal. Review menemukan satu kode salah pasang (cabang jendela clock-out dititipi kode bernama guestbook) dan dua kode yang menutupi dua sebab berbeda sekaligus. Pemecahannya menambah dua kode. Ini bukti kecil bahwa penamaan kode wajib dicocokkan ke cabangnya satu per satu, bukan ditebak dari bentuknya.
- **Data lama tidak ada dan tidak bisa diisi surut.** Jejak baru dimulai saat middleware naik.
- **Field formulir baru tidak otomatis tercatat**, konsekuensi langsung dari daftar-izin di #5. Menambah field ke pengajuan berarti memutuskan sekali apakah ia layak masuk jejak.
- **TTL index yang sudah ada tidak bisa diubah masa simpannya lewat `CreateIndex`**, harus di-drop dulu. Masuk [[RUN - Deploy Microservices bip-erp]], bukan disembunyikan di kode.
- **Karyawan tetap tidak diberi tahu alasannya.** ADR ini membuat kegagalan terlihat oleh HR dan IT, bukan oleh orang yang sedang gagal. Perbaikan pesan di aplikasi berdiri sendiri di luar lingkup ini, dan tanpa itu retry beruntun seperti 20 Agustus akan terus terjadi.

## Dokumen Terkait

- [[Microservices - Attendance Service]] · [[APP - MyBharata]] · [[APP - Web ERP]]
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] (stempel server-side, penolakan pencocokan teks galat)
- [[ADR - 0002 Database-per-Service]] (sebab koleksinya tinggal di `attendance_db`, bukan service audit terpusat)
- [[CORE - API Master Gateway]] (penulisan ulang header identitas dari klaim JWT)
- [[RUN - Deploy Microservices bip-erp]] (catatan operasional TTL index)
