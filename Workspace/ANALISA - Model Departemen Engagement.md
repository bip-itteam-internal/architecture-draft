# ANALISA - Model Departemen Engagement

Spesifikasi teknis untuk task `t_9d06c153`. Keputusan arsitekturalnya di [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]]; konsep bisnisnya di [[Sales - Engagement Team (Modul)]].

**Dibuat**: 2026-08-29 · **Status**: siap dikerjakan, dengan satu TBD yang ditandai ⛔ di §1.

---

## 0. Masalah yang diselesaikan

Tiga cacat, satu akar: **modul ini tak tahu tiket itu milik brand siapa.**

| # | Cacat | Bukti |
|---|---|---|
| A | Daftar kandidat pengerja berisi orang yang salah | `engagement_assign.go:40` menyaring `work_data` dengan `{department: <departemen PEMANGGIL>}` |
| B | Siapa pun boleh membuat tiket engagement | `engagement_routes.go:41` — gerbangnya `requireRoles("staff","supervisor","admin")` = seluruh ERP |
| C | Siapa pun melihat SELURUH tiket lintas brand | `antrianEngagement:216`, `dashboardEngagement:771`, `detailTiket:374`, `riwayatTiket:397` — nol penyaringan |

**Konfirmasi cacat A** (diminta eksplisit): benar. `daftarKandidatPengerja(ctx, id.Department)` dipanggil dari `kandidatPengerjaHandler:859` dengan departemen pemanggil, dan `$match: {"department": departemen}` di `:50`. Account Specialist Kyura mendapat daftar berisi rekan Kyura.

⚠️ **Satu koreksi atas premisnya.** Master data menempatkan jabatan `Engagement Team` sebagai **posisi DI DALAM departemen `Kyura` dan `Beauty Hacks`** (`shared-library/models/employee/master_data.go:345,353`), dan **tidak ada departemen bernama "Engagement"** di mana pun di repo (dicari di `master_data.go`, `common/roles.go` `deptKeyToNames`, `peran_dari_jabatan.go`, dan seluruh vault). Jadi:

- **Kalau master data mencerminkan kenyataan**: requester dan pengerja **sedepartemen**, dan cacat A bukan "daftar berisi departemen yang salah" melainkan "daftar tidak menyaring jabatan sama sekali" — Account Specialist Kyura melihat SELURUH karyawan Kyura, termasuk Host Live dan Videographer yang bukan pengerja boosting. Tetap cacat, tetapi gejalanya lebih ringan dari yang diduga.
- **Kalau tim Engagement sudah dipindahkan ke departemen tersendiri** (belum tercermin di kode/seed): cacat A persis seperti yang dijelaskan — daftarnya nol anggota tim Engagement.

Rancangan di bawah **sengaja benar untuk kedua keadaan**: ia menyaring **kunci jabatan** (`position_key`), yang tidak berubah maknanya apakah pengerja duduk di satu departemen atau dua. Yang butuh konfirmasi manusia hanya nilai seed-nya (§1).

---

## 1. TBD yang harus dijawab manusia ⛔

Satu pertanyaan, dua bagian. Sisanya sudah diputuskan di ADR 0060.

> **Di produksi, karyawan dengan jabatan `Engagement Team` terdaftar di `work_data.department` apa, dan `work_data.position_key` apa?**
>
> Cara memverifikasinya (satu query, tak perlu tebakan):
> ```
> db.work_data.aggregate([
>   { $match: { $or: [ { position: /engagement/i }, { position: /buzzer/i },
>                      { position_key: { $in: ["engagement_team", "buzzer"] } } ] } },
>   { $group: { _id: { d: "$department", p: "$position", k: "$position_key" }, n: { $sum: 1 } } }
> ])
> ```
> Hasilnya menentukan dua nilai seed di §3.2. Sampai dijawab, seed memakai **kedua** kunci (`engagement_team`, `buzzer`) dan **kedua** departemen requester (`Kyura`, `Beauty Hacks`) — kombinasi yang benar untuk kedua keadaan di §0, dan dapat diubah tanpa deploy.

Yang **tidak** perlu ditanyakan lagi (sudah diputuskan di ADR 0060): aturan keterlihatan per peran, siapa boleh membuat tiket, nasib `space_id`, dan perlakuan tiket lama.

---

## 2. Perubahan model

### 2.1 `EngagementTicket` — satu field baru

`engagement_models.go`:

```go
// RequesterDepartment = departemen Account Specialist pembuat tiket, apa adanya
// seperti work_data.department ("Kyura" / "Beauty Hacks").
//
// SUMBU PENYARINGAN KETERLIHATAN. Distempel server dari header BIP-Department saat
// tiket dibuat, TIDAK PERNAH dari body: nilai yang boleh dipilih klien bukan sumbu
// keamanan — pengirimnya cukup mengubah satu field untuk membaca brief brand lain.
//
// Nama, bukan key departemen: nama itulah yang tersimpan di work_data.department dan
// yang dibandingkan modul lain (common/roles.go deptKeyToNames,
// insentive/hierarki_hris.go). Perbandingannya kanonik — nama departemen diketik
// manusia di Master Data, dan "Beauty Hacks" vs "beauty  hacks" terjadi di produksi.
//
// Kosong pada tiket sebelum migrasi. Kosong TIDAK berarti tersembunyi dari semua
// orang — lihat aturan 6 di keterlihatanFilter().
RequesterDepartment string `json:"requester_department,omitempty" bson:"requester_department,omitempty"`
```

Tidak ada field lain yang ditambah. Departemen **pengerja** sengaja tidak disimpan: ia bisa berubah (mutasi karyawan) dan tak satu pun aturan keterlihatan membutuhkannya.

### 2.2 `space_id` — dipertahankan sebagai data, dicabut sebagai wewenang

- Field `SpaceID` **tetap ada** di struct (dokumen produksi menyimpannya) dan tetap diteruskan ke `notifyMany` sebagai konteks tautan.
- `buatTiketRequest.SpaceID` **dihapus** dari body. Blok parsing `engagement_handlers.go:134-141` dibuang; tiket baru lahir dengan `space_id` nil.
- `anggotaSpaceEngagement` (`engagement_notify.go:55`) **dihapus** — tak dipanggil dari mana pun.
- Konstanta `NotifEngagementOpen` dan `NotifEngagementReleased` **dihapus** beserta baris `semuaTipeNotifEngagement()`-nya. Keduanya tak pernah dikirim.
  ⚠️ Perbaiki sekalian bug di `semuaTipeNotifEngagement():39-40`: `NotifEngagementClaimed` tercantum **dua kali** dan `NotifEngagementOpen` tak tercantum, sehingga penjaganya bolong.
- Komentar kepala `engagement_notify.go:11-16` ("menyapa SELURUH anggota space") **diperbaiki** — ia menjanjikan model yang sudah tak berlaku sejak ADR 0059.

### 2.3 Konfigurasi baru: koleksi `engagement_settings`

Dokumen tunggal (`_id: "default"`), dibaca sekali per proses lalu di-cache 5 menit.

```go
type EngagementSettings struct {
    ID string `bson:"_id"`
    // KunciJabatanPengerja = work_data.position_key anggota tim Engagement.
    //
    // DATA, bukan konstanta. Rename "Buzzer" -> "Engagement Team" (HR, 2026-08-27)
    // MENERBITKAN KEY BARU: PositionKey diturunkan dari nama, jadi key lama tak
    // ditemukan dan paket haknya lenyap tanpa satu pun galat (master_data.go:221-233,
    // dikunci master_data_test.go:282). Kunci yang di-hardcode akan mengulanginya:
    // daftar kandidat mendadak kosong, nol pesan, dan tak ada yang berbunyi salah.
    //
    // Memuat KEDUA kunci: dokumen work_data yang belum ter-migrasi masih "buzzer".
    KunciJabatanPengerja []string `bson:"kunci_jabatan_pengerja"`
    // DepartemenRequester = departemen yang boleh MEMBUAT tiket engagement.
    DepartemenRequester []string `bson:"departemen_requester"`
}
```

Seed default bila dokumen tak ada (dibuat saat start, `upsert`, tak menimpa yang sudah ada):

```go
KunciJabatanPengerja: []string{"engagement_team", "buzzer"},
DepartemenRequester:  []string{"Kyura", "Beauty Hacks"},
```

**Kenapa koleksi, bukan env var**: nilainya berubah saat HR me-rename jabatan atau menambah brand — dua peristiwa yang tak seharusnya menuntut deploy. **Kenapa bukan `master_department`**: itu master data HR; menaruh kebijakan modul di sana membuat penyunting Master Data mengubah otorisasi tanpa menyadarinya.

⚠️ **Konfigurasi kosong = MENUTUP, bukan membuka.** `KunciJabatanPengerja` kosong berarti nol kandidat dan nol orang berperan pengerja (fail-closed). Membuka semuanya saat konfigurasi hilang adalah kegagalan yang tak berbunyi.

### 2.4 Index

Tambah di `pastikanIndexEngagement` (`engagement_repo.go`):

```go
// Penyaringan keterlihatan per departemen requester.
{Keys: bson.D{{"requester_department", 1}, {"status", 1}, {"deadline", 1}},
 Options: options.Index().SetName("ix_dept_requester")}
```

Hapus `ix_pemegang` (`:65-68`) — kuncinya `claimed_by`, field yang tak ada di model. Ganti dengan `{assigned_to: 1, status: 1}` bernama `ix_penerima`.
⚠️ Index lama tak hilang sendiri dari Mongo; jatuhkan eksplisit (`DropOne("ix_pemegang")`, abaikan galat "index not found").

---

## 3. Perubahan perilaku per endpoint

### 3.1 Helper baru — SATU tempat, dipakai semua

Semua endpoint daftar/detail memanggil helper yang sama. Menyalin logikanya melahirkan dua definisi "boleh lihat" yang pasti menyimpang, dan penyimpangannya tak pernah muncul sebagai galat.

```go
// keterlihatanFilter mengembalikan filter Mongo untuk tiket yang boleh dilihat
// pemanggil, dan MERUPAKAN SATU-SATUNYA definisi cakupan itu.
//
// nil = tanpa batas (admin). Bukan bson.M{} kosong: nil dapat dibedakan dari
// "belum diisi" saat dibaca ulang, dan pembeda itu yang mencegah filter kosong
// diperlakukan sebagai izin penuh karena kelalaian.
func keterlihatanFilter(ctx context.Context, id Identity) (bson.M, error)
```

Aturannya (ADR 0060 §2), diterjemahkan jadi kode:

```
admin                     -> nil (semua)
supervisor                -> {"$or": [ ...aturan dasar..., {"requester_department": {"$in": scopedDivisions(id)}} ]}
anggota kolam pengerja    -> {"$or": [ ...aturan dasar..., {"requester_department": {"$in": settings.DepartemenRequester}} ]}
lainnya (Account Spec.)   -> {"$or": [ ...aturan dasar..., {"requester_department": <kanonik dept-ku>} ]}

aturan dasar (SELALU ikut, untuk semua non-admin):
  {"requester_id": id.EmployeeID}
  {"assigned_to":  id.EmployeeID}
```

**Aturan 6 — tiket tanpa `requester_department`** (tiket lama yang gagal dimigrasi): untuk supervisor dan anggota kolam pengerja, tambahkan `{"requester_department": {"$in": [nil, ""]}}` ke `$or`. Untuk Account Specialist biasa: **tidak** ditambahkan — ia tetap melihatnya lewat aturan dasar bila ia pembuatnya.
Konsekuensi yang diterima: tiket yatim terlihat lebih luas daripada tiket bermigrasi. Itu benar arahnya — kehilangan tiket dari layar semua orang jauh lebih mahal daripada satu brief lama terbaca satu orang berlebih.

**Menentukan "anggota kolam pengerja"**:

```go
// akuPengerja membaca position_key pemanggil dari work_data ERP.
//
// Header gateway hanya membawa LABEL posisi (BIP-Position), bukan position_key, dan
// label sudah terbukti berpindah tanpa pemberitahuan ("ICC" -> "Account Specialist",
// position_key_filter_test.go:21). Membandingkan label berarti aturan ini padam pada
// rename berikutnya, tanpa galat.
//
// Kegagalan baca employee_db -> false (bukan pengerja), BUKAN true. Fail-closed:
// employee-service yang sedang mati tidak boleh membuka brief semua brand.
// Cadangan terakhir: label header dicocokkan ke nama jabatan yang key-nya ada di
// KunciJabatanPengerja — menurunkan hak saat ragu, tidak menaikkannya.
func akuPengerja(ctx context.Context, id Identity) bool
```

Hasilnya di-cache per `employee_id` selama 60 detik. Tanpa cache, satu pemuatan halaman antrian menambah satu round-trip employee_db per permintaan.

### 3.2 Tabel perubahan

| Endpoint | Sekarang | Menjadi |
|---|---|---|
| `POST /engagement/tickets` | siapa pun `staff`+ | **403** bila `KanonDept(id.Department)` ∉ `DepartemenRequester`. Stempel `requester_department` = `id.Department`. `space_id` tak lagi dibaca dari body |
| `GET /engagement/tickets/queue` | nol filter | `AND keterlihatanFilter()` |
| `GET /engagement/dashboard` | nol filter | seluruh `CountDocuments` di-`AND` `keterlihatanFilter()` |
| `GET /engagement/tickets/mine` | `claimed_by` ⛔ | `assigned_to` (**catatan**: perbaikan ini milik task `t_bb4feb67` — jangan tulis ulang, cukup pastikan tak hilang saat rebase) |
| `GET /engagement/tickets/requested` | `requester_id` ✅ | tak berubah (aturan dasar sudah mencakupnya) |
| `GET /engagement/tickets/:id` | nol pemeriksaan | **403** bila tiket tak lolos `keterlihatanFilter()` |
| `GET /engagement/tickets/:id/logs` | nol pemeriksaan | idem — muat tiketnya dulu, periksa, baru baca log |
| `GET /engagement/kandidat` | rekan sedepartemen | anggota kolam pengerja lintas departemen (§3.3) |
| `POST .../:id/{start,done,close,revisi,reassign,cancel}` | periksa `assigned_to`/`requester_id` | **tak berubah** — sudah benar, dan aturan keterlihatan tak melonggarkannya |

**Kenapa transisi tak disentuh**: gerbangnya sudah relasi-terhadap-tiket (`assigned_to == aku`, `requester_id == aku`), yang lebih ketat daripada keterlihatan. Menambah pemeriksaan keterlihatan di sana hanya menduplikasi aturan yang sudah lebih sempit.

⚠️ **`reassign` punya satu lubang yang layak ditutup di task ini**: `tugaskanUlangHandler` menerima `assigned_to` apa pun tanpa memeriksa orangnya anggota kolam pengerja. Setelah §3.3, ia bisa memindahkan tiket ke orang yang formulir buat-tiket sendiri tak akan pernah menawarkannya. Tambahkan pemeriksaan yang sama dengan §3.3 di `buatTiketEngagement` dan `tugaskanUlangHandler`: **tujuan penugasan wajib anggota kolam pengerja yang aktif**, `400` bila tidak.

### 3.3 `daftarKandidatPengerja` — perubahan inti

```go
// daftarKandidatPengerja membaca anggota tim Engagement dari ERP employee_db.
//
// Disaring position_key, BUKAN departemen pemanggil. Alasan yang lama (ADR 0059 §3)
// — "departemen lebih stabil daripada jabatan" — tetap benar sebagai PERINGATAN,
// tetapi kesimpulannya keliru: ia diam-diam mengandaikan requester dan pengerja
// sedepartemen. Permintaan datang dari Account Specialist (Kyura & Beauty Hacks) dan
// dikerjakan tim Engagement; menyaring departemen pemanggil memberi daftar berisi
// Host Live dan Videographer, dan nol jaminan anggota tim Engagement ada di dalamnya.
//
// Yang membuat penyaring ini tak mengulang kegagalan rename: kuncinya position_key
// (stabil), dan daftar kuncinya DATA (engagement_settings), bukan literal di sini.
func daftarKandidatPengerja(ctx context.Context, kunci []string) ([]kandidatPengerja, error)
```

Perubahan pipeline (`engagement_assign.go:49`):

```go
{"$match": bson.M{"position_key": bson.M{"$in": kunci}}},   // ganti {"department": departemen}
// ... $lookup system_authentication, $unwind, $match akun.is_active — TAK BERUBAH
{"$project": bson.M{
    "_id": 0, "employee_id": 1, "position": 1,
    "department": 1,                                          // BARU
    "full_name": bson.M{"$ifNull": bson.A{"$akun.full_name", "$employee_id"}},
}},
{"$sort": bson.M{"department": 1, "full_name": 1}},
```

`kandidatPengerja` mendapat field `Department string`. Daftar kini lintas departemen, jadi dua orang bernama mirip dari brand berbeda harus bisa dibedakan di layar.

`pesanTanpaKandidat` tak lagi menyebut departemen (sudah bukan sumbunya):

```
"Belum ada anggota tim Engagement aktif yang bisa ditugaskan. Hubungi admin."
```

⚠️ **Jangan menambahkan parameter departemen dari query.** Aturan ADR 0059 yang tetap berlaku: kalau cakupannya bisa diminta klien, endpoint ini jadi direktori karyawan seluruh perusahaan.

---

## 4. Rancangan migrasi

Dijalankan sekali saat start task-management service, idempoten, aman diulang.

### 4.1 Langkah

```
1. Baca seluruh engagement_tickets dengan requester_department kosong/absen.
2. Kumpulkan requester_id yang unik.
3. Satu panggilan batch ke employee_db work_data: {employee_id: {$in: [...]}} 
   -> proyeksi {employee_id, department}.
4. Per tiket: isi requester_department dari peta itu.
   Tak ketemu -> BIARKAN KOSONG. Jangan menebak dari client/campaign.
5. Log tiga angka: terisi, tanpa work_data, total.
```

**Kenapa batch, bukan per tiket**: satu round-trip per tiket membuat migrasi ratusan dokumen jadi ratusan panggilan lintas-service saat start.

**Kenapa yang gagal dibiarkan kosong, bukan diisi tebakan**: `client`/`campaign` tidak memetakan ke departemen secara pasti (satu brand bisa punya banyak client). Nilai keliru yang tampak masuk akal lebih berbahaya daripada kolom kosong — ia menyembunyikan tiket dari orang yang benar dan menampilkannya kepada yang salah, permanen.

### 4.2 Penjaga wajib: tiket lama TIDAK BOLEH hilang

Ini syarat lulus yang paling penting, dan urutan pemasangannya mengikat:

> **Pasang `keterlihatanFilter` dengan aturan 6 (kosong = terlihat oleh pengerja/supervisor/admin) LEBIH DULU, baru jalankan migrasi.**

Kalau filter dipasang tanpa aturan 6, ada jendela waktu — antara service naik dan migrasi selesai — ketika **setiap tiket lama tak terlihat siapa pun kecuali pembuat dan pengerjanya**. Dashboard supervisor kosong, dan yang membaca layar akan menyimpulkan datanya hilang.

Aturan 6 juga **tetap berlaku setelah migrasi selesai** — bukan sakelar sementara. Requester yang resign hari ini menghasilkan tiket ber-departemen kosong besok.

### 4.3 Rollback

Tak ada rollback data: migrasi hanya **menambah** field, tak menghapus/mengubah apa pun. Membatalkan keputusannya cukup dengan mengembalikan filter ke tanpa-batas; `requester_department` yang telanjur terisi menjadi field yang tak dibaca, bukan kerusakan.

---

## 5. Perubahan frontend

Kontraknya bergeser, jadi FE ikut. Cakupan minimum:

1. **`types/engagement.ts`**: `EngagementTicket` += `requester_department?: string`; `EngagementKandidat` += `department: string`.
2. **`engagement-form-modal.tsx`**: dropdown pengerja menampilkan `full_name — department`. Tanpa itu dua nama mirip dari brand berbeda tak dapat dibedakan.
3. **`kolom.tsx`**: kolom departemen requester di tab antrian (supervisor & tim Engagement kini melihat tiket dua brand bercampur).
4. **`use-engagement.ts`**: `detailTiket`/`logs` bisa membalas **403** untuk id yang sebelumnya `200` (mis. tautan lama dari notifikasi). Tampilkan pesan "tiket ini bukan cakupan Anda", bukan spinner abadi atau toast galat teknis.
5. **Formulir buat tiket** disembunyikan bagi departemen non-requester. ⚠️ Itu **kenyamanan, bukan gerbang** — gerbangnya `403` di backend (§3.2), dan tombol tersembunyi tak menghalangi siapa pun memanggil endpoint langsung.

---

## 6. Cara Verifikasi

Test yang WAJIB ada. Yang berbintang (★) diminta eksplisit oleh SPV di task.

### 6.1 Unit — `keterlihatanFilter` (fungsi murni, tanpa Mongo)

| # | Skenario | Harapan |
|---|---|---|
| 1 | ★ Account Specialist Kyura, tiket `requester_department: "Beauty Hacks"` | **tidak** cocok |
| 2 | ★ Account Specialist Kyura, tiket `requester_department: "Kyura"` | cocok |
| 3 | ★ Anggota kolam pengerja, tiket Kyura **dan** tiket Beauty Hacks | **keduanya** cocok |
| 4 | Account Specialist Beauty Hacks, tiket Kyura yang `assigned_to`-nya dia | cocok (aturan dasar menang) |
| 5 | Account Specialist Kyura, tiket Beauty Hacks yang **dia buat** | cocok (aturan dasar) |
| 6 | ★ Siapa pun non-admin, tiket `requester_department: ""` | cocok bagi pengerja/supervisor/admin; bagi Account Spec. lain **tidak** |
| 7 | supervisor `scopedDivisions=["Kyura"]`, tiket Beauty Hacks | **tidak** cocok |
| 8 | admin | filter `nil` |
| 9 | `"beauty  hacks"` vs `"Beauty Hacks"` (spasi ganda, beda kapital) | cocok — perbandingan kanonik |
| 10 | `engagement_settings` kosong/gagal dibaca | fail-closed: pemanggil **bukan** pengerja, cakupan menyempit |

### 6.2 Unit — kandidat & pembuatan

| # | Skenario | Harapan |
|---|---|---|
| 11 | pipeline `daftarKandidatPengerja` | `$match` memakai `position_key: {$in: ...}`, **bukan** `department`; `department` ikut di `$project` |
| 12 | pemanggil dari departemen non-requester `POST /tickets` | `403` |
| 13 | pemanggil Kyura `POST /tickets` | `201`, dan `requester_department == "Kyura"` |
| 14 | body membawa `requester_department: "Beauty Hacks"` | **diabaikan**; tersimpan `"Kyura"` (dari header) |
| 15 | `assigned_to` menunjuk orang di luar kolam pengerja (buat **dan** reassign) | `400` |
| 16 | `semuaTipeNotifEngagement()` | tiap tipe muncul **tepat sekali**, dan seluruh konstanta `Notif*` tercakup |

### 6.3 Migrasi

| # | Skenario | Harapan |
|---|---|---|
| 17 | ★ tiket lama tanpa `requester_department`, migrasi **belum** jalan | tetap terlihat oleh pembuat, pengerja, kolam pengerja, supervisor, admin |
| 18 | migrasi dijalankan dua kali | hasil identik, nol tulis di putaran kedua |
| 19 | `requester_id` tak punya `work_data` | field tetap kosong, tiket tetap terlihat (aturan 6), tercatat di log |

### 6.4 Perintah

```bash
cd services/task-management && go vet ./... && go test ./...
cd ../../shared-library && go vet ./... && go test ./...
cd ../erp-frontend && pnpm lint && pnpm test
```

⚠️ **Test hijau di modul ini menyesatkan** — seluruh test engagement berhenti sebelum menyentuh Mongo, sehingga kelas cacat "query menunjuk field yang tak pernah ditulis" (persis cacat `claimed_by`) mustahil tertangkap. Karena itu §6.1 sengaja menguji **bentuk filter yang dihasilkan**, bukan hasil query — itulah yang bisa dijaga tanpa database.

### 6.5 Verifikasi manual lewat gateway (sebelum PR ditandai siap)

Modul ini **belum pernah diverifikasi lewat gateway sama sekali**. Minimal, dengan tiga akun (Account Specialist Kyura, Account Specialist Beauty Hacks, anggota tim Engagement):

1. Kyura membuat tiket → muncul di `queue` miliknya dan tim Engagement, **tidak** muncul di `queue` Beauty Hacks.
2. Beauty Hacks membuka `/engagement/tickets/<id-kyura>` langsung lewat URL → **403**.
3. Dropdown pengerja di formulir Kyura memuat anggota tim Engagement (bukan nol, bukan seluruh karyawan Kyura).
4. Akun Finance memanggil `POST /engagement/tickets` → **403**.

---

## 7. Yang SENGAJA di luar cakupan

- **Bukti pengerjaan** (`attachments`) — task `t_bb4feb67`.
- **`pekerjaanSaya` memakai `claimed_by`** — juga `t_bb4feb67`. Disebut di §3.2 hanya supaya tak hilang saat rebase.
- **Saringan `?prioritas=` yang diabaikan**, `assigned_name` yang tak pernah diisi, retry nomor tiket ganda — cacat lain dari audit, bukan bagian model departemen.
- **Batas WIP per anggota** dan **notifikasi siaran ke space** — TBD lama di ADR 0059; ADR 0060 §6 memutuskan `space_id` tak lagi jadi sumber keanggotaan, sehingga notifikasi siaran ke space **gugur dengan sendirinya**. WIP tetap TBD.

## Dokumen Terkait

- [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] — keputusan yang dieksekusi spesifikasi ini
- [[Sales - Engagement Team (Modul)]] · [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] · [[ADR - 0058 Tiket Engagement Memakai Koleksi dan State Machine Sendiri]]
- [[Microservices - Task Management Service]] · [[API - Task Management Service]] · [[Microservices - Employee Service]]
