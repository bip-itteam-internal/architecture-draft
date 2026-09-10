## Deskripsi

*Tiket Engagement kini ditugaskan **otomatis** lewat round-robin server-side, BUKAN lagi ditunjuk manual oleh Account Specialist saat membuat tiket. Ini menggantikan bagian inti [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] (§1-§3): keputusan "AS menunjuk satu pengerja" digantikan "server memilih lewat giliran", sementara penugasan ULANG (reassign manual, §4 ADR-0059) tetap seperti semula.*

- **Status**: ✅ **Berlaku, kodenya sudah di `main`** (bip-erp) — commit `012561c5` "alokasi otomatis round-robin tiket, ganti assign manual" (1 September 2026), disusul `cf766cd7` "cabut fallback lintas departemen, lewati anggota cuti/sakit" dan `14c7a955` "endpoint pratinjau giliran berikutnya" (2 September). **Belum diverifikasi lewat gateway** dev maupun prod. Dituliskan 2026-09-09, sesudah kodenya berjalan — sama seperti ADR-0058/0059, keputusan ini sempat hanya hidup sebagai komentar kode.
- **Path di repo**: `bip-erp/services/task-management/engagement_giliran.go` · `engagement_assign.go` · `engagement_settings.go` · `engagement_handlers.go` (`buatTiketEngagement`, `pratinjauGiliranBerikutnya`)
- **Tanggal**: 2026-09-01 (kode) / 2026-09-09 (didokumentasikan)

## Context

[[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] memutuskan Account Specialist menunjuk satu pengerja lewat dropdown saat membuat tiket. Yang berubah sejak itu:

1. **AS tak selalu tahu siapa yang sedang longgar.** Menunjuk manual berarti AS menebak dari ingatan, dan hasilnya beban menumpuk ke satu-dua orang yang paling sering diingat — ADR-0059 sendiri sudah mencatat ini sebagai konsekuensi yang diterima ("beban tidak menyeimbangkan diri sendiri").
2. **FE tidak pernah menampilkan info beban** yang cukup untuk membuat pilihan manual itu berarti — dropdown-nya sekadar daftar nama, tanpa berapa tiket yang sedang dipegang tiap orang.
3. **Kolam pengerja kini resmi lintas departemen** ([[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] §4) — AS Kyura harus bisa "menunjuk" anggota Beauty Hacks dan sebaliknya, dan dropdown lintas-departemen tanpa info beban makin sulit dipakai bijak secara manual.

## Decision

**Server memilih pengerja lewat round-robin ATOMIK saat tiket dibuat. Klien tidak lagi mengirim `assigned_to`.**

### 1. `assigned_to` dihapus dari kontrak `POST /engagement/tickets`

Field ini **sengaja tidak ada** di `buatTiketRequest` (Go) maupun `BuatTiketPayload` (TypeScript, sejak diperbaiki 2026-09-09). Klien lama yang masih mengirimnya tidak ditolak `400` — nilainya dibaca lewat `assignedToKlienDiabaikan` dan diabaikan, dengan catatan balik `catatan` di respons 201 supaya klien yang masih mengirimnya tahu nilainya tak dihonor.

### 2. Giliran berputar PER DEPARTEMEN requester, bukan lintas kolam penuh

Berbeda dari kolam pengerja (`daftarKandidatPengerja`, lintas departemen sesuai ADR-0060 §4), **giliran round-robin default HANYA berputar di antara anggota kolam yang SEDEPARTEMEN dengan requester** (`EngagementSettings.LingkupGiliran = "departemen"`, `saringKandidatGiliran`). Requester Kyura tanpa kandidat Kyura yang tersedia **DITOLAK** (409), TIDAK melompat ke kolam Beauty Hacks — `IzinGiliranLintasDepartemen` (default `false`) adalah katup manual di data, bukan perilaku bawaan, sejak `cf766cd7` mencabut fallback lintas departemen sebelumnya (keputusan user, kartu `t_f7be6376`: "tiket Kyura tidak boleh dialokasikan ke Beauty Hacks saat orang Kyura tidak ada/cuti").

### 3. Anggota cuti/sakit sehari penuh DILEWATI dari giliran

`karyawanAbsenPenuhHariIni` menyaring kandidat yang sedang **Cuti**, **Sakit**, atau **Izin dengan subtype "Tidak masuk kerja"** (bukan seluruh Izin — izin berjam tidak menghilangkan orang dari giliran) hari itu (WIB) dari `attendance_db`, SEBELUM kursor dihitung. Gagal verifikasi (attendance_db tak terhubung) **fail-open**: alokasi tetap jalan seolah semua hadir, dicatat di log dan `Note` audit — bukan fail-closed yang menghentikan seluruh modul karena satu dependensi opsional mati.

### 4. Kursor atomik, dibaca SETELAH `$inc`, bukan sebelum

Satu dokumen `engagement_giliran` per departemen (kunci **kanonik**: trim + lipat kapital + rapatkan spasi ganda), `Kursor` naik monoton lewat SATU `FindOneAndUpdate` ber-`$inc` + `ReturnDocument(After)`. Kandidat terpilih = `kandidat[(kursor-1) % n]`. Dua create bersamaan menerima dua kursor berbeda (dijamin Mongo), jadi tak ada dua tiket yang atomik jatuh ke orang yang sama karena balapan.

### 5. Pratinjau BACA-SAJA untuk form

`GET /engagement/giliran-berikutnya` menjalankan jalur logika yang SAMA (`kandidatUntukAlokasi`, `pilihDariGiliran`) tapi membaca kursor tanpa `$inc` — memberi tahu form "siapa yang AKAN dapat tiket" tanpa menggeser giliran. Ini **perkiraan**, bukan janji: giliran bisa bergeser antara pratinjau dan create sungguhan (orang lain membuat tiket lebih dulu, atau cuti disetujui/dicabut).

## Consequences

**Yang diterima:**

- **AS kehilangan kendali langsung atas siapa mengerjakan tiketnya.** Ini pembalikan eksplisit dari filosofi inti ADR-0059 ("pemohon tetap bertanggung jawab ke client, jadi ia pantas memutuskan siapa mengerjakannya"). Diterima karena beban yang tak seimbang (konsekuensi ADR-0059 yang tak pernah ditangani) dinilai lebih mahal daripada kendali manual itu.
- **Reassign manual (ADR-0059 §4) TETAP ADA dan tak berubah** — kalau pengerja hasil round-robin berhalangan, requester/admin masih bisa memindahkannya manual lewat `tugaskanUlangHandler`, yang tetap memakai kolam penuh (`GET /engagement/kandidat`), bukan giliran.
- **FE form "Buat Request" WAJIB tak lagi menawarkan pemilihan** — dropdown assign manual yang tersisa (diperbaiki 2026-09-09, lihat commit `fix(engagement): ganti dropdown assign manual dengan pratinjau round-robin`) sempat lolos ke produksi mengirim `assigned_to` yang diam-diam dibuang server, tanpa satu pun indikasi ke pemakainya bahwa pilihannya tak dihonor.
- **Makna "kolam" dan "giliran" jadi dua sumbu berbeda** yang mudah tertukar: kolam (siapa BOLEH ditugaskan/dilihat sebagai kandidat reassign) tetap lintas departemen (ADR-0060 §4); giliran (siapa OTOMATIS dapat tiket berikutnya) default sedepartemen. Pembaca kode yang tak membedakan ini akan salah menyimpulkan "AS Kyura tak bisa dapat orang Beauty Hacks sama sekali" — padahal cuma alokasi OTOMATIS-nya yang dibatasi, bukan kemampuan reassign manualnya.

**Yang belum diputuskan (TBD):**

- **Batas WIP per anggota** saat round-robin mengarahkan tiket ke orang yang sedang longgar TAPI kebetulan sudah memegang banyak tiket lama (revisi berulang, reassign masuk). `hitungWIP` ada di kode tapi tak dipanggil dari mana pun — sama seperti dicatat ADR-0059.

## Terkait

- [[ADR - 0059 Penugasan Langsung Menggantikan Antrian Bersama]] — §1-§3 DIGANTIKAN ADR ini; §4 (reassign), §5 (revisi ke orang sama), §6 (notifikasi personal) TETAP BERLAKU
- [[ADR - 0060 Cakupan Keterlihatan Tiket Engagement]] — kolam pengerja lintas departemen (§4) yang giliran ini memakai sebagai sumber kandidat sebelum disaring per departemen
- [[Sales - Engagement Team (Modul)]] — konsep bisnis modul, status cacat terkini
- [[Microservices - Task Management Service]] · [[API - Task Management Service]]
