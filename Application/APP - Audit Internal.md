# APP - Audit Internal

## Deskripsi

*Aplikasi web berdiri sendiri di subdomainnya sendiri untuk seluruh audit internal perusahaan, masuk lewat SSO ERP tanpa akun terpisah. Isinya kertas kerja bulanan, register temuan, dan pengaturan ukuran sampel. Ia sengaja BUKAN menu di dalam ERP: pihak yang diperiksa tidak boleh memegang kunci penyimpanan bukti pemeriksaan tentang dirinya, dan audit kepatuhan yang menyusul tidak punya rumah yang masuk akal di dalam service keuangan.*

- **Stack**: Next.js (App Router) + TypeScript + shadcn/ui + TanStack Query + react-i18next — sama dengan [[APP - Web ERP]], sengaja, supaya layar yang sudah jadi dapat dipindahkan apa adanya
- **Path di repo**: repo terpisah **(baru, belum dibuat)**; backend `bip-erp/services/finance` hari ini ([[Finance - Rancangan Finance Service]]), `services/audit` sesudah pemisahan
- **Status**: 🟡 **Konsep / Direncanakan** — belum ada repo, belum ada satu baris kode. Layarnya sudah ada di `erp-frontend` ([#1429](https://github.com/bip-itteam-internal/erp-frontend/pull/1429), merged) dan berhenti dikembangkan di sana
- **Keputusan**: [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]

## Latar Belakang

Layar audit pertama dibangun sebagai tiga rute di dalam `erp-frontend` (`/audit`, `/audit/temuan`, `/audit/setelan`) dan sudah merged. Ia **belum pernah dijalankan satu kali pun** — `finance-service` tidak ada di `docker-compose.dev.yml`, jadi tak ada satu baris data pun yang pernah dimuat.

Pemindahannya diputuskan sebelum layar itu sempat dipakai, atas dua tuntutan yang baru dinyatakan: bukti pemeriksaan harus tersimpan dengan kunci yang tidak dipegang pihak yang diperiksa, dan wadahnya akan menampung seluruh audit internal termasuk kepatuhan GA. Alasan lengkapnya di ADR 0074.

## Ruang Lingkup

### Tiga layar, dipindahkan apa adanya

| Rute | Isi | Digerbang |
|---|---|---|
| `/` | Kertas kerja bulanan, 36 baris uji | `audit.view` |
| `/temuan` | Register temuan lima unsur, lintas periode | `audit.view` |
| `/setelan` | Ukuran sampel per uji | `audit.master.save` |

Aturan tampilannya **tidak berubah** dan sudah tertulis di [[Finance - Audit Internal]]: kelompok 1 naik ke atas bukan yang paling merah, baris `menunggu_data` dan `belum_diimplementasi` tidak disembunyikan, `keadaan_efektif` dibaca dari respons bukan dihitung ulang, dan tiga izin tulis digerbang terpisah.

### Yang dipindahkan, dan berapa

Diukur 2026-09-03 atas `erp-frontend`.

| Bagian | Baris | Perlakuan |
|---|---|---|
| Modul audit (`features/audit` + `app/(main)/audit`) | 1.924 | Pindah apa adanya — seluruh import relatifnya tertutup, tak satu pun menembus keluar modul |
| Test modul audit | 524 | Pindah; uji paritas locale perlu penyesuaian path |
| Primitif shadcn (15 komponen) | 1.425 | `npx shadcn add` — **nol baris ditulis** |
| Hook & util kecil | 234 | Salin |
| Infra (axios, toast, auth, i18n, shell) | 751 | Salin; blok `COMPANY_SCOPED_READS` dibuang, audit tak memakainya |
| Terjemahan `audit.*` + `common` | 281 | Ukir dari locale 10.000 baris |
| `menu-permission` | **1.476 → ~8** | Tulis ulang |
| `reconciliation-view` | **285 → ~10** | Inline satu predikat |
| `MainTable` + `Banner` + `FilterTable` | 1.187 | ⚠️ Keputusan terbuka, lihat di bawah |

**Port pragmatis ≈ 1.470 baris di luar modul audit sendiri. Port harfiah ≈ 4.030 baris.**

### ⚠️ Keputusan terbuka: tabel di-fork atau dibangun ulang

`MainTable` dipakai **124 halaman lain** di erp-frontend, `Banner` **106**. Mem-fork keduanya berarti bercabang dari sebanyak itu, dan perbaikan bug di satu sisi tidak akan menyeberang — kelas "sumber kebenaran kedua" yang berulang kali menggigit di sini.

Yang memurahkan pilihan bangun-ulang: halaman audit hanya memakai **13 dari 19 prop** `MainTable`. `columnGroups`, `footer`, `rowClassName`, `pageSizeOptions`, `description`, dan `hideExport` tak satu pun dipakai.

⚠️ **`MainTable` menyeret `exceljs`** lewat import statis, dan prop `hideExport` **tidak** menghilangkannya dari bundle.

## Autentikasi

SSO ERP lewat one-time code, jalur yang sudah dipakai produksi. Rinciannya di [[CORE - SSO Flow]].

```
app audit  →  <ERP>/login?redirect_url=<APP>/auth/callback
              ERP mint tiket   POST /auth/sso/ticket
              redirect balik   ?code=<hex 32 byte>
app audit  →  POST /auth/sso/redeem {code}  →  ERP JWT
```

Kode sekali pakai, TTL 30 detik. Subdomain `*.bharatainternasional.com` sudah otomatis lolos allowlist redirect ERP tanpa perubahan env.

⛔ **ERP JWT dipakai SEKALI di callback untuk membaca identitas, lalu dibuang.** Ia tidak punya `aud` dan tidak diperiksa audience-nya, jadi ia berlaku penuh di seluruh `/api/*` selama 72 jam tanpa refresh. Menyimpannya sebagai token sesi berarti setiap kebocoran dari aplikasi lain mana pun bisa dipakai di sini. Polanya sudah ada dan matang di `services/vault-mcp/erp.go`.

⛔ **DILARANG punya tabel pengguna atau kata sandi sendiri** ([[ADR - 0003 SSO-only Gateway]]).

### Yang wajib disiapkan, dan tidak ada SDK bersamanya

Tiap konsumen SSO menulis ulang keempatnya — belum ada paket bersama:

- Halaman `/auth/callback`, **dikecualikan dari guard** aplikasi
- Penjaga anti-loop saat logout (`?logged_out=1`); tanpanya redirect otomatis dan auto-login berputar tanpa henti
- ⛔ **PR CORS ke `api-gateway/main.go` dan deploy gateway.** Daftar origin di-**hardcode di Go**, bukan env. [[CORE - SSO Flow]] menyatakan menambah konsumen "tidak butuh perubahan backend" dan itu **salah** — Portal Karir membuktikannya, ia butuh PR #460 plus deploy gateway prod.
- Penanganan 401 setelah 72 jam; jalur SSO **tidak** menerbitkan refresh token

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Auditor internal | Posisinya **belum ada**; direncanakan | `audit_auditor` (view, tinjau, terbitkan) | Web |
| Reviewer silang | Staf dari divisi di luar yang diaudit | `audit_auditor` | Web |
| Direktur | Penerima laporan, penyetel ukuran sampel | `audit_direksi` (view, master.save) | Web |
| Pembaca | Ditunjuk per kasus | `audit_pembaca` (view) | Web |

- **Tujuan**: memastikan ketepatan angka, mendeteksi indikasi kecurangan, dan menutup peluangnya.
- **Pain point**: kertas kerja dirakit ulang dari nol tiap bulan, dan datanya diminta dari divisi yang sedang diperiksa.
- **Aksi utama**: meninjau baris yang berbunyi, menelusuri ke dokumen sumber, menandai wajar dengan alasan tertulis, atau menaikkannya jadi temuan.

⛔ **Finance bukan pemakai aplikasi ini**, melainkan pihak yang dimintai klarifikasi.
⛔ **Direktur tidak meninjau, auditor tidak menyetel ukuran sampel.** Yang menetapkan beban pemeriksaan bukan yang mengerjakannya.
⛔ **Menu ini tidak muncul untuk siapa pun sampai paketnya dipasang.** Tak ada `system_roles.audit` dan `AuditTierDefault` mengembalikan kosong — memasang paket adalah langkah deploy, bukan langkah opsional.

## Alur Pengguna

```
Auditor internal — menutup pemeriksaan bulan berjalan
  tanggal 6 jam 1 WIB   periode bulan lalu dibuka otomatis
  1. buka /            kertas kerja, kelompok 1 di atas
  2. klik baris berbunyi   panel detail: dua sisi + selisih + kondisi ideal
  3. telusuri              ⛔ DI LUAR SISTEM
  4. kembali ke panel      tandai wajar (alasan WAJIB)
                           ATAU jadikan temuan (lima unsur)
  5. temuan terbit         panel tetap terbuka + tautan ke register
  n. selesai ketika Direktur melihat daftar temuan bulan itu

Direksi — jauh lebih pendek, dan sengaja
  buka /setelan → ubah ukuran sampel → selesai
  TIDAK meninjau baris; tombol aksinya memang tidak muncul untuknya
```

⚠️ **Alur ini belum pernah ditempuh satu orang pun.** Seluruhnya dari kode dan rencana, bukan dari layar yang berjalan.

## Belum Diimplementasikan / Catatan

- **Repo, CI, dan hosting belum ada.** Semuanya TBD.
- **Nama dan alamat final belum diputuskan.** Wadahnya untuk seluruh audit internal, jadi namanya wajib membedakan diri dari [[GA - Audit Internal System]] — dua hal bernama sama tanpa pembeda sudah terbukti membingungkan permanen di [[APP - Dynamic Task Tracker]].
- **Bentuk layar untuk audit kepatuhan GA belum dirancang.** Registry 36 uji berbentuk pembanding dua sisi berangka; checklist kepatuhan berbentuk lain, dan belum diperiksa apakah keduanya muat dalam satu bentuk layar.
- ⚠️ **`showFormErrorsToast` menulis ke store yang dibaca `form-errors-modal`.** Bila modal itu tidak dipasang di layout aplikasi baru, validasi lima unsur temuan **gagal tanpa satu pun galat** — tombolnya ditekan, tidak terjadi apa-apa.
- ⚠️ **Badge shadcn stok tidak cukup.** `tampilan.ts` menuntut varian `success` dan `warning`; `npx shadcn add badge` saja akan gagal ketik-periksa.
- ⚠️ **i18n wajib, bukan opsional**, bila `MainTable`/`Banner` diport — ketiganya memanggil `useTranslation`.
- ⚠️ **`pnpm dev` rusak di path ber-spasi** (`c:\Data utama\...`), pelajaran dari [[APP - Portal Karir Bharata]]. Pratinjau andal lewat `pnpm build` + `pnpm start`.
- ⚠️ **Build wajib digagalkan bila `.env` tak ada.** Portal Karir hampir menerbitkan situs produksi yang menunjuk alamat dev secara senyap karena kodenya jatuh ke fallback.

## Dependensi & Integrasi

- [[CORE - SSO Flow]] — jalur masuk; [[CORE - API Master Gateway]] — CORS dan routing
- [[Finance - Audit Internal]] — dok domain 36 uji, semantik kolom, dan aturan layar
- [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] — keputusan pemisahan
- [[CORE - RBAC dan Permission Set]] — katalog izin `audit.*` dan tiga paket bawaan
- [[APP - Web ERP]] — asal layarnya, dan sumber komponen bersama yang dipindahkan

## Dokumen Terkait

- [[GA - Audit Internal System]] — audit kepatuhan yang direncanakan menyusul ke wadah ini
- [[APP - Dynamic Task Tracker]] · [[APP - Portal Karir Bharata]] — dua preseden aplikasi terpisah ber-SSO beserta ongkosnya
- [[RUN - Deploy Microservices bip-erp]]
