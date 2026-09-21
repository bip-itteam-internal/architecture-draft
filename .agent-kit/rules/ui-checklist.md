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

## 2a. Sheet: rangka tetap, badan yang menggulir

Berlaku untuk setiap pemakaian `Sheet` di erp-frontend (`src/components/ui/sheet.tsx`).
Tiga hal WAJIB, dan ketiganya gagal dengan cara yang sama: tak ada galat, layarnya cuma
terasa salah.

1. **Header TIDAK ikut menggulir.** `SheetHeader` (judul, dan tombol tutup yang dipasang
   `SheetContent`) harus tetap di tempatnya sampai bawah. Panel yang judulnya hilang saat
   digulir membuat pembaca kehilangan konteks justru di titik ia paling butuh, yaitu saat
   isinya panjang.
2. **Badan punya padding kiri dan kanan.** `SheetContent` sendiri TIDAK berpadding, jadi
   badan tanpa `px-*` menempelkan isinya ke tepi panel dan ke batang gulir.
3. **Footer opsional, tetapi WAJIB begitu sheet punya aksi.** Aksi di sini berarti tombol
   yang menulis, menyetujui, menolak, mengunduh, atau menutup alur. Aksi yang ditaruh di
   ujung badan ikut tergulir, jadi ia hanya terlihat oleh yang menggulir sampai habis, dan
   panjang isi menentukan apakah tombolnya terlihat. Sheet yang benar-benar cuma menampilkan
   informasi tidak perlu footer.

### Mekanismenya (jangan ditebak, ini yang menentukan)

`SheetContent` sudah `flex flex-col`, `h-full` untuk `side` kiri/kanan, dan TANPA padding.
`SheetHeader` dan `SheetFooter` masing-masing sudah `p-4`, dan `SheetFooter` ber-`mt-auto`.
Artinya rangkanya sudah benar sejak awal, yang kurang cuma badannya.

```tsx
<SheetContent className="w-full sm:max-w-xl">   {/* JANGAN overflow-y-auto di sini */}
  <SheetHeader>
    <SheetTitle>{t("...")}</SheetTitle>
  </SheetHeader>

  <div className="flex-1 min-h-0 space-y-4 overflow-y-auto px-4 pb-4">
    {/* isi panjang */}
  </div>

  <SheetFooter>            {/* hanya bila ada aksi */}
    <Button onClick={simpan} disabled={sedangSimpan}>{t("...")}</Button>
  </SheetFooter>
</SheetContent>
```

Acuan kode yang sudah benar: `ga/peminjaman/components/peminjaman-detail-sheet.tsx`,
`marketing/live-support-sesi/components/sheet-rincian-sesi.tsx`,
`pengajuan-barang/components/sheet-detail-pengajuan.tsx`.

⛔ **Anti-pola: `overflow-y-auto` ditempel di `SheetContent`.** Seluruh isi jadi satu area
gulir, jadi header ikut naik dan footer (kalau ada) ikut tenggelam. Bentuknya menyamar
sebagai penyetelan lebar yang wajar, misalnya `className="w-full overflow-y-auto sm:max-w-xl"`,
sehingga terbaca seperti keputusan tata letak, bukan seperti header yang dikorbankan.

⚠️ `min-h-0` ditulis bersama `flex-1` walau `overflow-y-auto` pada elemen yang sama sudah
membuat batas minimum otomatisnya nol. Tanpa itu, memindahkan gulirnya satu tingkat ke
dalam mengembalikan bug yang sama persis (`team-memory.md` § Jebakan tabel/filter).

⚠️ `side="top"` dan `side="bottom"` memakai `h-auto`, bukan `h-full`. Kolom flex yang
tingginya tak terikat membuat `flex-1` tak membatasi apa pun, jadi badannya tumbuh setinggi
isi dan tak ada yang menggulir. Sheet atas/bawah wajib memberi `max-h-*` pada `SheetContent`.

### Keadaan terukur (2026-09-18, `origin/main`)

Dari 24 berkas pemakai `Sheet` (di luar primitifnya sendiri dan `ui/sidebar.tsx`):

| Yang diukur | Hasil |
|---|---|
| `overflow-y-auto` di `SheetContent`, jadi header ikut tergulir | **16 dari 24** |
| badan gulir punya padding mendatar | 13 dari 24 |
| memakai `SheetFooter` | **0 dari 24** |

Jadi aturan ini menggambarkan tujuan, bukan keadaan sekarang. **Sheet baru dan sheet yang
sedang disentuh wajib mengikutinya**; menyapu 16 berkas sekaligus adalah task tersendiri,
bukan sisipan ke perubahan lain. Jangan membaca daftar di atas sebagai izin meniru tetangga:
mayoritas di sini justru yang salah.

### Membuktikannya

jsdom tak punya mesin layout, jadi test tidak bisa membuktikan sesuatu bisa digulir atau
tetap di tempat. Yang bisa dikunci test cuma anti-polanya lewat assertion kelas, dan itu
wajib dibuktikan dengan kontrol negatif (kembalikan bugnya sebentar, pastikan testnya merah
pada assertion yang diklaimnya). Buktinya tetap layar: buka sheet dengan data yang lebih
panjang dari tinggi jendela, gulir sampai dasar, lalu pastikan judulnya masih terlihat dan
tombol aksinya masih terjangkau tanpa menggulir balik.

> MyBharata beda: `CustomBottomSheet` sudah memasang paddingnya sendiri, jadi menambah
> padding lagi di dalamnya justru ganda. Bagian ini soal `Sheet` erp-frontend.

## 2b. Menu sidebar: induk tidak dinamai jabatan

Berlaku untuk setiap induk (item ber-`items[]` tanpa `url`) di
`components/layout/sidebar-menus.tsx`.

**Induk menamai URUSAN yang dibagi anak-anaknya, atau HUBUNGAN halaman itu dengan
pembacanya (milik saya vs milik tim). Yang dilarang adalah menjadikan JABATAN sebagai
sumbu: satu induk per posisi, diisi apa pun yang posisi itu kerjakan.**

Ujinya satu pertanyaan, dijawab sebelum menambah induk atau memindahkan menu ke dalamnya:
kalau nanti ada halaman baru yang dikerjakan posisi itu tetapi urusannya lain, apakah ia
masuk ke induk ini? Jawaban "iya, kan orangnya sama" berarti sumbunya jabatan, tolak.
Jawaban "tidak, urusannya beda" berarti sumbunya urusan, aman.

Nama induk yang KEBETULAN sama dengan nama jabatan tidak melanggar apa pun, selama yang
dinamainya memang urusannya. "Personalia" dan "Live Support" keduanya begitu.

### Kenapa sumbu jabatan rusak

1. **Satu orang satu posisi.** Tiap pembaca melihat tepat satu induk yang relevan dan
   sisanya tersaring izin, jadi induk itu cuma menambah satu klik tanpa menyembunyikan apa
   pun. `ratakanIndukTipis` malah membubarkannya di bawah `AMBANG_SARANG` (3) anak
   TERLIHAT, jadi ia bubar justru bagi orang yang dinamainya. Induk yang audiens aslinya
   berhak atas dua anak menyetel `ambangSarang: 2` sendiri, seperti "Live Support".
2. **Halaman dipakai lintas posisi.** Halaman yang dibaca SPV, Leader, dan staf pemegang
   paket tak punya rumah tunggal di sumbu jabatan, jadi ia harus diduplikasi. Dua entri ke
   URL yang sama sudah ada satu di kategori MARKETING ("Komplain ke Gudang" bagi pemegang
   peran marketing DAN warehouse), dan komentarnya sendiri mencatatnya sebagai cacat yang
   belum dibereskan, bukan sebagai pola yang boleh ditiru.
3. **Nama jabatan berubah lewat master data, dan sudah terbukti berubah.** "ICC" jadi
   "Account Specialist" (2026-08-25). Induk bernama jabatan menjadi sumber kebenaran kedua
   untuk nama jabatan, dan menyimpangnya tanpa satu pun galat (`team-memory.md`
   § Prinsip kode: satu fakta satu tempat).
4. **Sumbu jabatan SUDAH dikerjakan `perm` dan paket Hak per Posisi.** Memasangnya lagi
   sebagai sumbu bentuk menu mengulang `menu_hidden` yang dicabut ADR 0051, yang aturannya
   `tampil = boleh DAN tidak disembunyikan` membuat permission set yang sudah dipasang tak
   pernah terlihat. `sidebar-menu-shape.ts` sudah menuliskan prinsipnya: menyandarkan
   bentuk sidebar pada nama role akan salah persis di kasus yang paling penting.

### Keadaan terukur (2026-09-21, `origin/main`)

29 induk di seluruh sidebar, dan tak satu pun memakai jabatan sebagai sumbu. 27 menamai
urusan atau bidang kerja (Personalia, Program Culture, People Development, Recruitment,
Operasional Gudang, Order & Dokumen, Pengawasan, Pembelian, Master & Referensi, Task
Management, Live Support, Laba per Level, Analisis, dan seterusnya); 2 menamai hubungan
dengan pembacanya ("Pekerjaan Saya", "Kelola Tim").

**"Live Support" satu-satunya yang namanya juga nama jabatan**, dan ia lolos uji di atas:
keempat anaknya urusan siaran live, dan audiensnya justru empat yang berbeda (penjadwal
shift, pemantau sesi, penyetor, penyetuju departemen). Jadi ia bukan preseden
induk-per-posisi, dan komentarnya di `sidebar-menus.tsx` menyebutkan itu.

Arahnya sudah pernah diputuskan sekali di kode: induk "Kelola Tim" sengaja menggantikan
induk "ICC" (2026-09-17) dengan alasan tertulis "menyebut jabatan lama alih-alih
pekerjaannya".

### Yang TIDAK dijaga test

Aturan ini tak bisa dicek mesin tanpa daftar nama jabatan, dan daftar itu sendiri berubah
lewat master data, yaitu masalah nomor 3 di atas. Penjaganya review, bukan test. Yang
DIJAGA test adalah bentuk hasilnya per persona (`live-support-persona.test.ts`,
`sidebar-pekerjaan-saya.test.ts`), dan itu tetap wajib untuk induk baru: kunci apa yang
TERLIHAT oleh tiap persona, bukan sekadar bahwa induknya ada.

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
