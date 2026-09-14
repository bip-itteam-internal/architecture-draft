# Checklist Antarmuka (erp-frontend · MyBharata)

> Dibaca **on-demand** saat merancang, membangun, atau mereview layar. Dirujuk dari
> `team-memory.md` § Konvensi FE / UI, `plan-checklist.md` §1, dan `review-checklist.md` §J.
> **Jangan** di-import ke `CLAUDE.md`. Update cukup `git pull architecture-draft` (tak perlu
> re-run `init`).

## Aturannya

**Layar harus menarik dan mudah dipakai, DAN dirakit dari komponen yang sudah ada.** Itu satu
aturan, bukan dua tuntutan yang saling tawar. Tampilan yang dipercantik lewat komponen tiruan,
token warna sendiri, atau salinan "versi yang lebih bagus" adalah pekerjaan ganda, dan hasilnya
justru terlihat seperti aplikasi lain.

Ini sudah terjadi, bukan kekhawatiran: `features/marketing-insight/` membangun kosakata
visualnya sendiri (token `marketing-insight-*`, `bg-white` mati sehingga mode gelap padam di
sana, dan `MarketingInsightTable` sebagai tandingan `MainTable`). Niatnya tampilan yang lebih
baik, hasilnya sistem desain kedua yang harus dirawat terpisah. Angkanya di
[[REF - Layout Dashboard erp-frontend]] § Dua sistem desain hidup berdampingan.

## 1. Cari dulu, susun dari yang ada, baru bangun

Urutannya wajib. Berhenti di langkah pertama yang cukup:

1. **Pakai apa adanya.**
2. **Susun** beberapa komponen yang ada menjadi bentuk yang dibutuhkan.
3. **Bungkus** dengan adapter LOKAL di folder fitur: memetakan props yang sudah ada, tidak
   menambah props baru ke komponen shared.
4. **Buat baru, LOKAL di folder fitur**, hanya bila tiga langkah di atas tak cukup, dengan
   alasan tertulis di rencana.

Yang dilarang di setiap langkah: tiruan look-alike, menambah prop atau varian ke komponen
shared demi satu pemanggil (aturan pemakai ketiga, `team-memory.md` § Prinsip kode), dan warna
atau jarak di luar token yang ada.

**Komponen shared yang kurang bagus diperbaiki di SUMBERNYA**, sebagai task tersendiri dengan
test penuh karena dampaknya ke semua pemakai. Menyalinnya menjadi versi yang lebih bagus
meninggalkan dua versi yang akan menyimpang diam-diam.

**Sebutkan pencarian yang dijalankan** di artefak rencana (`## Apa yang Sudah Ada`), sama
dengan `plan-checklist.md` §1. Tempat mencari:

| Repo | Di mana | Yang sudah dipakai luas |
|---|---|---|
| erp-frontend | `src/components/ui/` (primitif shadcn) | `button` (varian `outline` di 417 berkas, `ghost` 156), `card`, `badge`, `dialog`, `alert-dialog` (39), `sheet`, `custom-tabs` (45), `tooltip`, `skeleton` (201), `combobox`, `date-picker`, `chart` (`ChartContainer`, 33), `sparkline`, `mascot-state` (`MascotState`, 107: keadaan kosong, galat, tidak ditemukan) |
| erp-frontend | `src/components/` (`layout`, `table`, `form`, `modal`) | `MainTable` + `useTableState` + `FilterTable`, `Banner`, `SidebarBackButton`, `Container`, `showFormErrorsToast` |
| erp-frontend | `src/features/<modul>/components/` | marketing-analytics: `PageShell`, `KpiTile`, `BarPeringkat`, `Corong`, `TabelDrill`; dashboard HRIS/KPI: `BaganSkorBulanan` |
| MyBharata | `lib/` (widget bersama, `origin/dev`) | `ShimmerBox`, `CustomBottomSheet`, `SurfaceCard`, `AppDimens`, `EmptyState`, `CustomFormField` |

Angka erp-frontend diukur 2026-09-11 atas `origin/main`. Daftar ini titik awal, bukan katalog
lengkap: yang menentukan adalah pencarianmu sendiri (`git grep` atas `origin/main`, karena
`Grep` melewati berkas biner).

## 2. Mutu layar: kriteria yang bisa diperiksa

Bukan selera. Untuk halaman berisi angka dan bagan, komposisinya diatur
[[REF - Layout Dashboard erp-frontend]] (satu insight dominan, jarak `gap-6`/`gap-4`, alur
baca); untuk halaman daftar, skill `/migrasi-tabel-hris`; untuk warna bagan, `team-memory.md`
§ Bagan/chart. Yang di bawah berlaku untuk semua layar.

1. **Tujuan utama terbaca dari bentuk layarnya.** Pembaca tahu harus mulai dari mana tanpa
   paragraf panduan. Satu **aksi utama** per area memakai `Button` bawaan; aksi lain memakai
   varian `outline` atau `ghost`. Dua tombol utama bersebelahan berarti belum ada keputusan
   mana yang penting. Layar yang butuh paragraf penjelas adalah gejala alur
   (`plan-checklist.md` §1b).
2. **Lima keadaan dirancang, bukan hanya keadaan berisi data.**

   | Keadaan | Yang benar |
   |---|---|
   | Memuat | kerangka setinggi isi (`Skeleton` / `ShimmerBox`), bukan spinner |
   | Kosong | `MascotState` / `EmptyState` dengan satu kalimat yang membedakan "belum ada data" dari "saringan tak menemukan apa-apa", plus langkah berikutnya bila ada |
   | Galat | sebab yang bisa dibaca dan jalan keluarnya, bukan "Terjadi kesalahan" polos |
   | Terkunci (403) | kalimat tentang siapa yang boleh, bukan galat merah (contoh: blok kinerja host di Analisis Live) |
   | Sebagian | penanda terang saat data terpotong atau satu sumber gagal (contoh: penanda 5.000 sesi di halaman Live) |

3. **Setiap aksi memberi umpan balik.** Tombol terkunci dan berlabel proses selama permintaan
   berjalan. Hasilnya lewat toast `sonner`, dan galat validasi lewat `showFormErrorsToast`.
   Aksi yang tak bisa dibatalkan dikonfirmasi `AlertDialog` yang **menyebut objeknya** (nama
   akun, nama orang, jumlah baris), bukan "Anda yakin?".
4. **Konsisten lewat token yang ada, dan hidup di kedua tema.** Warna dari token tema
   (`bg-card`, `text-muted-foreground`, `--fb-seri-*` untuk deret bagan), bukan hex atau
   `bg-white`. Jarak mengikuti `Container`: tanpa `p-6` sendiri. Periksa mode gelap sebelum
   menyebut selesai.
5. **Angka mudah dibandingkan.** Kolom angka rata kanan dengan `tabular-nums`. Satuan dan
   pembandingnya tertulis (Rp, %, "dari 30 hari"). Nilai `null` berarti "tak terhitung" dan
   tampil berbeda dari 0.
6. **Responsif sampai lebar ponsel.** Grid punya breakpoint (`grid-cols-1 lg:grid-cols-3`,
   bukan `grid-cols-4` mati). Tabel lebar menggulir di wadahnya sendiri (`overflow-x-auto`),
   dan halamannya tak boleh ikut menggulir mendatar. `TabelDrill` masih melanggar ini per
   2026-09-11 (teks `sr-only` lolos dari wadah gulir), lihat [[APP - Web ERP]] § Belum
   Diimplementasikan.
7. **Terbaca semua orang.** Tiap kontrol punya label. Identitas tak bergantung warna saja
   (legend berlabel, teks di samping lencana). Fokus keyboard terlihat. Semua teks lewat `t()`
   di dua locale (ADR 0010).

## 3. Arah visual boleh dari luar, komponen tetap dari repo

Skill `frontend-design` (plugin opsional per mesin), mockup Figma, atau tangkapan layar aplikasi
lain boleh dipakai untuk **arah**: hierarki, ritme, detail yang membuat layar terasa rapi.
**Komponen, token warna, dan jarak tetap dari repo.** Bila sarannya menuntut komponen atau palet
baru, repo yang menang, dan sarannya diterjemahkan ke komponen yang ada, persis seperti
[[REF - Layout Dashboard erp-frontend]] menerjemahkan enam aturan layout ke komponen kita.

## 4. Bukti sebelum menyebut selesai

- **Lihat layarnya sungguhan**, di dev server atau tangkapan layar headless: tema terang
  **dan** gelap, lebar desktop **dan** sekitar 390px, bahasa id **dan** en. jsdom tak punya
  mesin layout, jadi test tidak membuktikan apa pun tentang tampilan.
- **Laporkan komponen yang dipakai ulang**, dan komponen baru (bila ada) beserta alasannya.
  Komponen baru tanpa alasan tertulis diperlakukan sebagai temuan review.
