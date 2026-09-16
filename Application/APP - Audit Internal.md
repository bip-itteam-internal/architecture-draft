# APP - Audit Internal

## Deskripsi

*Aplikasi web berdiri sendiri di subdomainnya sendiri untuk seluruh audit internal perusahaan, masuk lewat SSO ERP tanpa akun terpisah. Isinya kertas kerja bulanan 38 item uji petik dan register temuan. Ia sengaja BUKAN menu di dalam ERP: pihak yang diperiksa tidak boleh memegang kunci penyimpanan bukti pemeriksaan tentang dirinya, dan audit kepatuhan yang menyusul tidak punya rumah yang masuk akal di dalam service keuangan.*

- **Stack**: Next.js (App Router) + TypeScript + shadcn/ui + TanStack Query + react-i18next — sama dengan [[APP - Web ERP]], sengaja, supaya layar yang sudah jadi dapat dipindahkan apa adanya
- **Path di repo**: `audit-bharata` (**repo terpisah**, dibuat 2026-09-03); backend `bip-erp/services/finance` hari ini ([[Finance - Rancangan Finance Service]]), `services/audit` sesudah pemisahan
- **Status**: ⚠️ **Implemented (ada catatan)**, diperbarui 2026-09-15. Kontainer prod `Audit-App` (image dibuat 2026-09-11, diukur 2026-09-12) masih versi **matriks 36 uji** dengan tiga layar. Versi **uji petik** ([[ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual]]) dikerjakan di branch `feat/uji-petik-manual`, **belum merge**: dua layar, 88 test hijau, `pnpm build` sukses. CORS gateway untuk `https://audit.bharatainternasional.com` dan port dev 3012 sudah ada di `api-gateway/main.go` (koreksi 2026-09-12). ⚠️ Paket izin `Audit: *` ke akun **belum diukur ulang** sejak 2026-09-04; status terkininya **TBD**.
- **Keputusan**: [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] · [[ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual]]

## Latar Belakang

Layar audit pertama dibangun sebagai tiga rute di dalam `erp-frontend` (`/audit`, `/audit/temuan`, `/audit/setelan`), merged dan live di prod sejak 2026-09-03.

Pemindahannya diputuskan atas dua tuntutan: bukti pemeriksaan harus tersimpan dengan kunci yang tidak dipegang pihak yang diperiksa, dan wadahnya akan menampung seluruh audit internal termasuk kepatuhan GA. Alasan lengkapnya di ADR 0074.

**Rute di ERP dicabut 2026-09-15** (branch erp-frontend `feat/cabut-audit-internal-erp`, belum merge). Alamat lama `/audit*` dialihkan (307) ke aplikasi ini lewat env `NEXT_PUBLIC_AUDIT_URL`, jadi bookmark lama tidak berakhir di 404. Rinciannya di [[APP - Web ERP]].

## Ruang Lingkup

### Dua layar (versi uji petik)

| Rute | Isi | Digerbang |
|---|---|---|
| `/` | Kertas kerja bulanan: 38 item dikelompokkan bagian dan tahap, panel detail per item, dan kartu lima area di luar lingkup | `audit.view`; aksi `audit.tinjau` dan `audit.temuan.terbitkan` |
| `/temuan` | Register temuan lintas periode, terbaru di atas; `?id=<id temuan>` membuka detailnya langsung | `audit.view` |

`/setelan` (ukuran sampel per uji) **dicabut** bersama menunya: ukuran sampel kini bagian kalimat tiap item.

### Aturan tampilan

Domainnya di [[Finance - Audit Internal]]. Yang ditegakkan layar:

- **Urutan mengikuti dokumen sumber**: Accounting lalu Tax, Tahap 2 lalu Tahap 3, lalu nomor sebagai angka. Bukan menurut keadaan: auditor bekerja dari dokumen bernomor.
- **Item belum diperiksa tidak disembunyikan**, dan keadaan `belum_diperiksa` bernada netral, bukan merah.
- **`keadaan_efektif` dibaca dari respons**, tidak dihitung ulang.
- **Kalimat pembuka dan cakupan dihitung dari `jumlah_item`**, supaya kertas kerja yang barisnya kurang tak pernah terbaca "seluruhnya wajar".
- **Respons tanpa `jumlah_item`** dianggap backend sebelum ADR 0098; layar menyatakan server belum diperbarui.
- **Tombol Siapkan kertas kerja** muncul bagi pemegang `audit.tinjau` saat baris kurang dari `jumlah_item`. Pembaca melihat kalimat bahwa kertas kerja belum disiapkan auditor.
- **Panel item** berurutan kerja: keterangan item (titik awal, pembanding, kriteria, tujuan, sampel yang dituntut, metode), kesimpulan tersimpan, lampiran bukti, lalu isian sampel dan catatan. Tombol ditahan sampai keduanya terisi, dan sampai keterangan item (serta temuan lama untuk revisi) termuat; galat muatnya ditampilkan.
- **Tandai wajar tidak ditawarkan pada item bertemuan.** **Jadikan temuan** dan **Revisi temuan** lewat dialog yang menyebut item dan periodenya, dengan pengingat perluasan sampel hanya untuk metode acak. Revisi punya judul, tombol, dan toast sendiri.
- **Pemegang izin tanpa aksi pada baris itu** melihat kalimat keterangan, bukan isian tanpa tombol.

### Riwayat: yang dipindahkan dari erp-frontend (diukur 2026-09-03)

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
| `MainTable` + `Banner` + `FilterTable` | 1.187 | Dibangun ulang, lihat di bawah |

**Diputuskan: tabel dibangun ulang, bukan di-fork.** `MainTable` dipakai 124 halaman lain di erp-frontend dan `Banner` 106, sementara halaman audit hanya memakai 13 dari 19 prop `MainTable`. Ikut hilang `exceljs`, yang diseret `MainTable` lewat import statis walau `hideExport` menyala.

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
- ⛔ **CORS di `api-gateway/main.go` dan deploy gateway.** Daftar origin di-**hardcode di Go**, bukan env. Untuk aplikasi ini dikerjakan lewat bip-erp [#1690](https://github.com/bip-itteam-internal/bip-erp/pull/1690) (origin `https://audit.bharatainternasional.com` + port dev **3012**). [[CORE - SSO Flow]] pernah menyatakan menambah konsumen "tidak butuh perubahan backend" dan itu **salah** untuk konsumen berbasis peramban — Portal Karir membuktikannya lewat PR #460, dan PR #1690 membuktikannya kedua kalinya.
- Penanganan 401 setelah 72 jam; jalur SSO **tidak** menerbitkan refresh token

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Auditor internal | Posisinya **belum ada**; direncanakan | `audit_auditor` (view, tinjau, terbitkan) | Web |
| Reviewer silang | Staf dari divisi di luar yang diaudit | `audit_auditor` | Web |
| Direktur | Penerima laporan | `audit_direksi` (view; `master.save` tanpa aksi sejak ADR 0098) | Web |
| Pembaca | Ditunjuk per kasus | `audit_pembaca` (view) | Web |

- **Tujuan**: memastikan ketepatan angka, mendeteksi indikasi kecurangan, dan menutup peluangnya.
- **Pain point**: kertas kerja dirakit ulang dari nol tiap bulan, dan datanya diminta dari divisi yang sedang diperiksa.
- **Aksi utama**: menelusuri sampel tiap item ke dokumen, lalu menyimpulkan Wajar atau Temuan dengan sampel dan catatan.

⛔ **Finance bukan pemakai aplikasi ini**, melainkan pihak yang dimintai klarifikasi. Peran dan tanggung jawab Finance selengkapnya (bukan disalin di sini): [[Finance - FAT Persona]].
⛔ **Direktur tidak meninjau.** Yang membaca laporan bukan yang mengerjakan pemeriksaannya.
⛔ **Aksi tulis tidak muncul untuk siapa pun sampai paketnya dipasang.** Tak ada `system_roles.audit` dan `AuditTierDefault` mengembalikan kosong — memasang paket adalah langkah deploy, bukan langkah opsional.

## Alur Pengguna

```
Auditor internal: memeriksa satu periode
  tanggal 6 jam 01:00 WIB   periode bulan lalu dibuka otomatis
  1. buka /                 kertas kerja periode; bila barisnya kurang: "Siapkan kertas kerja"
  2. buka item              panel: titik awal, pembanding, kriteria, sampel yang dituntut
  3. telusuri               ⛔ DI LUAR SISTEM (rekening koran, gudang, dashboard, arsip pajak)
  4. kembali ke panel       isi sampel beserta cara memilih, dan catatan
                            Tandai wajar
                            ATAU Jadikan temuan -> dialog (pengingat perluas ke 10, item acak)
  5. temuan terbit          panel tetap terbuka + tautan "Lihat di register" (/temuan?id=)
  n. selesai ketika cakupan "38 dari 38 item sudah dinilai"

Direktur / Pembaca: membaca
  buka / atau /temuan -> panel hanya-baca (sampel dan catatan terlihat, tanpa tombol)

Dari ERP
  bookmark /audit atau /audit/temuan -> dialihkan ke aplikasi ini (bila NEXT_PUBLIC_AUDIT_URL terisi saat build)
```

⚠️ **Alur ini belum pernah ditempuh satu orang pun.** Seluruhnya dari kode dan test, bukan dari layar yang berjalan.

## Belum Diimplementasikan / Catatan

- **CI**: TBD, belum diperiksa.
- **Nama dan alamatnya sudah dipakai** (repo `audit-bharata`, `audit.bharatainternasional.com`). Karena wadahnya untuk seluruh audit internal, namanya tetap wajib membedakan diri dari [[GA - Audit Internal System]] — dua hal bernama sama tanpa pembeda sudah terbukti membingungkan permanen di [[APP - Dynamic Task Tracker]].
- **Bentuk layar untuk audit kepatuhan GA belum dirancang.** Registry uji petik berbentuk daftar item bervonis manusia yang terikat bagian dan tahap; belum diperiksa apakah checklist kepatuhan muat di bentuk itu.
- ⚠️ **Pemilihan sampel tidak tercatat mesin.** Yang tersimpan hanya kalimat sampel dari auditor; rinciannya di [[Finance - Audit Internal]].
- ⚠️ **`Toaster` wajib terpasang di layout.** Tanpanya penolakan isian sampel dan catatan hilang tanpa satu pun galat.
- ⚠️ **Badge shadcn stok tidak cukup.** `tampilan.ts` menuntut varian `success` dan `warning`; `npx shadcn add badge` saja akan gagal ketik-periksa.
- ⚠️ **`pnpm dev` rusak di path ber-spasi** (`c:\Data utama\...`), pelajaran dari [[APP - Portal Karir Bharata]]. Pratinjau andal lewat `pnpm build` + `pnpm start`.
- ⚠️ **Build wajib digagalkan bila `.env` tak ada.** Portal Karir hampir menerbitkan situs produksi yang menunjuk alamat dev secara senyap karena kodenya jatuh ke fallback.
- ⚠️ **Deploy versi uji petik wajib sesudah finance-service.** Layar baru di atas backend lama menyatakan server belum diperbarui; layar lama di atas backend baru ditolak saat meninjau karena tidak mengirim sampel.

## Dependensi & Integrasi

- [[CORE - SSO Flow]] — jalur masuk; [[CORE - API Master Gateway]] — CORS dan routing
- [[Finance - Audit Internal]] — dok domain: 38 item uji petik, keadaan baris, dan aturan layar
- [[API - Finance Service]] — kontrak rute `/api/finance/audit/*`
- [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]] — keputusan pemisahan · [[ADR - 0098 Audit Internal Beralih ke Uji Petik Dua Arah Manual]] — registry uji petik
- [[CORE - RBAC dan Permission Set]] — katalog izin `audit.*` dan tiga paket bawaan
- [[APP - Web ERP]] — asal layarnya, kini hanya mengalihkan alamat lama

## Dokumen Terkait

- [[GA - Audit Internal System]] — audit kepatuhan yang direncanakan menyusul ke wadah ini
- [[APP - Dynamic Task Tracker]] · [[APP - Portal Karir Bharata]] — dua preseden aplikasi terpisah ber-SSO beserta ongkosnya
- [[RUN - Deploy Microservices bip-erp]]
