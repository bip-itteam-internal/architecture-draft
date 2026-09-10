## Deskripsi

*Psikotes **online** untuk kandidat rekrutmen: HR menerbitkan sesi, kandidat mengerjakan sendiri lewat **magic link tanpa login**, server menilai otomatis, hasilnya masuk ke **Hasil Tes** babak Psikotest. Jenis tes yang sudah dibangun: **Kraepelin** (deret angka per kolom, dinilai kecepatan/ketelitian/keajegan/ketahanan). Sisi implementasi: [[Microservices - Recruitment Service]]; kontrak endpoint: [[API - Recruitment Service]].*

- **Status**: ⚠️ **Implemented (ada catatan)** — BE + FE ada di `origin/main` (BE: 12 berkas Go di `services/recruitment`; FE kandidat sejak 2026-09-09). **Masih bergerak**: sisi career portal disentuh 2026-09-10. **Status deploy belum diukur** — jangan asumsikan sudah live, ukur dulu ([[RUN - Deploy Microservices bip-erp]]).
- **Menggantikan asumsi lama** bahwa psikotes "dilaksanakan staf HR di luar aplikasi" dan "psikotes online = fase lanjut". Keduanya sudah tidak berlaku; dokumen yang masih berbunyi begitu sudah dikoreksi ([[HRIS - Recruitment]]).
- **Diverifikasi ke `origin/main` 2026-09-10** (bukan checkout lokal — lihat catatan di bagian akhir).

## Alur Pengguna

1. Kandidat berada di babak **Psikotest**. HR menekan **Kirim Tes** di layar kandidat → `POST /candidates/:id/psikotes`.
2. Server membuat satu `psikotes_session` (soal + config **dibekukan** ke dalam sesi) dan menerbitkan **token acak**. Kandidat menerima **email** berisi magic link. Bila email gagal terkirim, HR tetap bisa **menyalin link** dari layar — penerbitan sesi tidak digagalkan oleh kegagalan email.
3. Kandidat membuka link **tanpa login**, membaca instruksi, menekan **Mulai**, lalu mengerjakan kolom demi kolom. Tiap kolom disubmit saat waktunya habis.
4. Sesi berakhir dengan salah satu dari tiga cara, dan **bedanya dicatat**: `tuntas` (semua kolom selesai), `ditinggalkan` (browser memberi tahu server lewat `sendBeacon`), `kedaluwarsa` (server menutup sendiri karena tak ada aktivitas).
5. Server menghitung metrik lalu **meng-upsert `candidate_test_result`** untuk babak Psikotest dengan `score` = skor keseluruhan dan `result` = **`Pending`**.
6. **HR yang memutuskan Pass/Fail**, lewat form Hasil Tes di detail kandidat. Sistem tidak pernah menetapkan nasib kandidat sendiri.

> ⚠️ **Langkah 5 TIDAK menggerakkan status kandidat.** Upsert dilakukan langsung ke koleksi, bukan lewat handler `POST /candidates/:id/test-result`, jadi SP-Wiring (Pass → `Pending`, Fail → `Hold`) dan perpindahan `progress` ke babak **tidak** ikut jalan. Kandidat yang sudah selesai mengerjakan tetap menunggu HR membuka form Hasil Tes. Ini konsisten dengan keputusan "sistem tidak memutuskan sendiri", tapi berarti **tidak ada pemberitahuan otomatis** bahwa hasil sudah siap dinilai.

## Model Data

**Koleksi `psikotes_session`** (`recruitment_db`) — satu kandidat mengerjakan satu kali satu jenis tes.

| Field | Catatan |
|---|---|
| `candidate_id` + `round_id` | Kunci aturan **satu kandidat satu kali tes** |
| `jenis` | `kraepelin`. Nilai inilah yang menentukan bentuk `soal`/`hasil` |
| `token` | Kunci akses magic link. 32 byte `crypto/rand`, base64url |
| `status` | `pending` → `in_progress` → `finished` |
| `config`, `soal`, `hasil` | Bertipe **bebas** (`bson.M`) |
| `col_index` | Kolom terakhir yang sudah disubmit. Hanya **maju** |
| `selesai_karena` | `tuntas` / `ditinggalkan` / `kedaluwarsa`. Diisi **sekali** |
| `issued_by`, `issued_at`, `started_at`, `finished_at`, `last_seen_at` | Jejak waktu |

**Tiga index** (`ensurePsikotesIndexes`, idempoten saat startup):
- `idx_psikotes_kandidat_babak` — **UNIK** `(candidate_id, round_id)`. Ini penjaga aturan bisnis di level **data**; pemeriksaan di handler adalah lapisan kedua yang tugasnya memberi pesan terbaca, bukan pengganti.
- `idx_psikotes_token` — **UNIK** `(token)`.
- `idx_psikotes_status` — biasa, untuk kueri operasional.

> ⛔ **Mengganti spesifikasi index TIDAK terjadi lewat deploy.** Mongo menolak membuat index bernama sama dengan spesifikasi berbeda, dan penjaganya cuma `log`: build sukses, container sehat, **index lama tetap berlaku**. Kelas yang sama dengan `ensureManpowerPlanIndex`. Bila spesifikasi berubah, index lama wajib di-drop manual di dev dan prod.

### Kenapa `config`/`soal`/`hasil` bertipe bebas

Disengaja. Bentuk soal dan hasil tiap jenis tes berbeda mendasar: Kraepelin menyimpan matriks digit per kolom dan empat kategori; DISC (belum dibangun) kemungkinan kuesioner pilihan tanpa konsep benar/salah; CFIT (belum dibangun) kemungkinan skor tunggal. Menegaskan salah satu bentuk itu di lapisan bersama memaksa semua jenis lain memuat field yang tak relevan baginya. **Jenis tes baru cukup menambah file skoring/soalnya sendiri**, tanpa mengubah skema bersama.

### Kerahasiaan soal dan skor

`soal`, `hasil`, dan `token` diberi `json:"-"` **di level struct**, bukan hanya dihindari di handler. Alasannya pengaman terhadap kesalahan di masa depan: seseorang yang lupa membuat DTO terpisah tidak otomatis membocorkan kunci jawaban atau skor. Endpoint kandidat memakai **DTO publik eksplisit**, dan ada test allowlist kunci JSON yang menggigit bila field internal bocor. Laporan HR pun tidak memuat soal.

## Konfigurasi Kraepelin

Dibekukan ke dalam sesi saat terbit, supaya hasil lama tetap terbaca dengan konfigurasi yang benar-benar dipakai saat itu walau standar berubah kemudian.

| Field | Rentang | Default |
|---|---|---|
| `columns` (jumlah kolom) | 10-60 | 30 |
| `rows` (baris per kolom) | 15-60 | 40 |
| `seconds` (detik per kolom) | 10-60 | 20 |

## Endpoint

**HR** (RBAC `PermRecruitmentWork`/`PermRecruitmentView` + `isHR`):

| Method | Path | Fungsi |
|---|---|---|
| POST | `/candidates/:id/psikotes` | Terbitkan sesi. Kandidat yang **sudah punya sesi → `409`** yang menyarankan Terbitkan Ulang |
| POST | `/candidates/:id/psikotes/reissue` | Terbitkan ulang. **Alasan wajib** (kosong → `400`); sesi lama dihapus, token lama otomatis mati |
| GET | `/candidates/:id/psikotes/report` | Laporan individual (metrik + `selesai_karena`), lewat DTO eksplisit |
| GET | `/candidates/psikotes/status` | Status **massal** untuk polling tabel (banyak id sekaligus, satu kueri `$in`) |

> ⚠️ `/candidates/psikotes/status` **wajib didaftarkan sebelum** `GET /candidates/:id`, kalau tidak ia tertelan sebagai permintaan kandidat ber-id "psikotes". Ini kelas bug rute-tertelan yang sudah pernah menggigit di sini (lihat [[Microservices - Calendar Service]]); di kode ada test yang mengunci urutannya.

**Publik** (tanpa JWT, dijaga token di URL) — kelimanya dipublish gateway di bawah `/public/recruitment/psikotes/*`:

| Method | Path (service) | Fungsi |
|---|---|---|
| GET | `/public/psikotes/:token` | Buka sesi. **Tidak memuat digit soal** |
| POST | `/public/psikotes/:token/start` | Mulai. **Idempoten**: soal tidak digenerate ulang, kandidat melanjutkan dari `col_index` tersimpan |
| POST | `/public/psikotes/:token/columns/:index` | Submit satu kolom. Index sama **menimpa**; index lama **tidak menarik balik** progres; panjang jawaban ditentukan **server** |
| POST | `/public/psikotes/:token/finish` | Selesai. Panggilan kedua tidak menghitung ulang |
| POST | `/public/psikotes/:token/abandon` | Dipanggil browser lewat `navigator.sendBeacon`. Balasan **selalu** `{ok:true}` tanpa skor |

## Skoring

`ComputeKraepelinMetrics` adalah **satu-satunya** tempat skor dihitung, dipakai bersama oleh `/finish`, `/abandon`, dan sweep server.

| Kategori | Diukur dari | Ambang 3 tingkat |
|---|---|---|
| **Kecepatan** | rata-rata dikerjakan terhadap maksimum per kolom | 70 / 45 |
| **Ketelitian** | akurasi jawaban | 95 / 85 |
| **Keajegan** | coefficient of variation antar kolom (**terbalik**: makin kecil makin baik) | 20 / 40 |
| **Ketahanan** | perubahan sepertiga akhir terhadap sepertiga awal | −10 / −25 |

Skor keseluruhan = **rata-rata skor keempat kategori**, lalu dipetakan ke kategori kesimpulan.

> ⛔ **Ambang dan rumus di atas JANGAN diubah tanpa validasi psikolog** — begitu tertulis di kode, dan itu bukan formalitas: angkanya menentukan penilaian orang.

## Penutupan Sesi: tiga jalan, satu fungsi

`selesaikanSesiPsikotes` adalah satu-satunya fungsi yang menulis status `finished`, dipanggil dari `/finish`, `/abandon`, dan sweep server. Sebelumnya logikanya hidup hanya di `/finish`; diekstrak supaya perhitungan skor tidak bercabang jadi tiga salinan yang bisa menyimpang diam-diam (**Satu Fakta Satu Tempat**).

- **Hanya sesi `in_progress`** yang boleh diproses. `finished` ditolak demi idempotensi (sendBeacon bisa terkirim lebih dari sekali). `pending` ditolak karena kandidat yang cuma membuka email lalu menutupnya **belum mengerjakan apa pun** — menghanguskan sesinya berarti ia kehilangan kesempatan tanpa pernah mengerjakan.
- **Sweep server** (ticker 1 menit) menutup sesi yang tak ada aktivitas. Ini lapis yang menentukan: `/abandon` hanya menangkap tutup-tab yang wajar, sedangkan laptop mati atau wifi putus **hanya** bisa ditutup dari sini.
- **Ambang kedaluwarsa = 6 × `seconds` config sesi itu sendiri** (default 20 detik/kolom → 2 menit), bukan angka tetap. Pengali 6 dipilih karena tiga jeda wajar bisa menumpuk pada kandidat yang masih benar-benar mengerjakan: retry jaringan, jeda alami antar kolom, dan kolom terakhir yang tak punya kolom sesudahnya untuk memaksa lanjut.
- **Idempoten terhadap dua instance**: filter update menuntut status **masih** `in_progress` di level Mongo saat update dieksekusi, bukan cuma saat dibaca. Instance yang kalah balapan tidak match, sesi ditutup tepat sekali.

## Belum Diimplementasikan / Catatan

- ⚠️ **DUA implementasi mesin tes kandidat hidup berdampingan**, dan ini perlu diputuskan:
	- `erp-frontend`: `src/app/psikotes/[token]/page.tsx` + `src/features/psikotes/` (2 commit, terakhir **2026-09-09**)
	- `career-bharata`: `src/app/psikotes/[token]/page.tsx` + `src/components/psikotes/` + `src/lib/psikotes/mesin.ts` (4 commit, terakhir **2026-09-10**)

	Email magic link menunjuk ke **`ERP_FRONTEND_URL`** + `/psikotes/<token>`, jadi yang benar-benar dibuka kandidat adalah versi **erp-frontend**, sementara yang paling aktif dikembangkan justru versi career portal. Bisa jadi ini migrasi yang sedang berjalan (env tinggal diarahkan ulang), bisa jadi dua salinan yang akan menyimpang. **Diukur 2026-09-10, ukur ulang sebelum dipakai mengambil keputusan.**
- **Jenis tes lain belum ada.** Hanya `kraepelin`. DISC dan CFIT disebut di komentar kode sebagai contoh bentuk yang berbeda, keduanya **belum dibangun**.
- **Hasil selesai tidak memberi tahu siapa pun.** Tak ada notifikasi ke HR bahwa sebuah sesi sudah tuntas dan menunggu keputusan; HR harus melihat kolom status di tabel kandidat.
- **Report PDF psikotes tidak ada.** Laporan tampil di layar HR; tak ada lampiran tersimpan di MinIO. Desain lama di [[HRIS - Recruitment]] yang menjanjikan "report PDF di MinIO" tetap belum terealisasi.
- **Status deploy belum diukur.** Fitur ini baru mendarat 2026-09-09 dan masih disentuh 2026-09-10.
- ⚠️ **Catatan cara memverifikasi.** Dokumen ini lahir dari kesalahan: checkout lokal `bip-erp` di mesin dev tertinggal **689 commit**, sehingga seluruh modul psikotes tak terlihat dan sempat dinyatakan "belum ada" di vault. Klaim tentang keadaan kode wajib diuji ke **`origin/<branch>`** (`git grep <pola> origin/main`), bukan ke berkas di disk.

## Dependensi & Integrasi

- [[Microservices - Recruitment Service]] — rumah kodenya; babak Psikotest dicari **by nama** `"Psikotest"` ber-`form_type: "test"` (id berbeda per lingkungan karena seed per environment). Babak belum ada → `400` dengan pesan jelas.
- [[Microservices - Notification Service]] — email magic link ke kandidat (template event `psikotes`), best-effort.
- [[CORE - API Master Gateway]] — mempublish kelima rute publik tanpa JWT.
- [[APP - Web ERP]] — layar HR (Kirim Tes, status inline, kurva kerja, laporan individual) dan halaman kandidat versi erp-frontend.
- [[APP - Portal Karir Bharata]] — halaman kandidat versi career portal.

## Dokumen Terkait

- [[HRIS - Recruitment]] — konsep dan keputusan HRD
- [[API - Recruitment Service]] — kontrak endpoint
- [[HRIS - Candidate Assessment]] — desain assessment lama yang sudah superseded
