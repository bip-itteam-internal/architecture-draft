# Skor gabungan per karyawan pada form penilaian

**Tanggal**: 2026-08-10
**Status**: disetujui, siap direncanakan
**Lingkup**: `services/form-builder` (BE) + `erp-frontend` (FE, PR terpisah)

## Masalah

Analisa form penilaian sudah menghitung rata-rata **per pertanyaan** untuk tiap orang
yang dinilai (`SubjectScore.Average` di `analytics_subject.go`). Yang belum ada adalah
**satu angka** yang merangkum seluruh pertanyaan menjadi penilaian tunggal per karyawan.

Tanpa itu, pembaca laporan harus membandingkan delapan kolom sekaligus untuk menjawab
pertanyaan paling sederhana: siapa yang perlu ditindaklanjuti.

## Yang TIDAK dikerjakan

Ditulis lebih dulu karena tiga hal ini sempat masuk pembahasan lalu sengaja dikeluarkan.

- **Tidak masuk KPI.** Angkanya berhenti di layar analisa. Menyambungkannya ke `kpi_score`
  menuntut definisi yang stabil selamanya, sebab angka periode lalu harus tetap berarti
  saat rumusnya berubah. Melihatnya dulu di analisa memberi kesempatan mengoreksi rumus
  tanpa merusak riwayat siapa pun. Bila kelak dilanjutkan, polanya sudah ada:
  `kpi_sumber_kaizen.go` menarik dari form-builder lewat rute internal, dan ADR 0032
  menetapkan employee-service tetap pemilik tunggal `kpi_score`.
- **Pertanyaan `number` tidak ikut.** Hanya `scale`. Alasannya di bawah.
- **Bobot tidak menempel di seksi.** Seksi tetap murni pengelompokan tampilan, tanpa arti
  perhitungan. Bobot berjenjang (porsi aspek dikali porsi butir) menyerupai rubrik formal
  tapi menuntut dua lapis isian yang harus dijelaskan ke orang yang dinilai; ditunda sampai
  ada kebijakan yang benar-benar menuntutnya.

## Keputusan dan alasannya

### Hanya pertanyaan bertipe `scale`

Analisa yang ada memasukkan `number` dan `scale`. Untuk angka gabungan hanya `scale` yang
boleh ikut, karena hanya dia punya `ScaleMin`/`ScaleMax` sehingga bisa dinormalisasi.

Pertanyaan `number` seperti "berapa kali terlambat" tidak punya batas atas, dan
merata-ratakannya bersama skala 1..5 menghasilkan angka yang tidak berarti apa-apa.

Form yang tidak punya satu pun pertanyaan `scale` menghasilkan `Overall` kosong, bukan nol.

### Bobot per pertanyaan, angka relatif yang dinormalisasi

Kebijakan HR untuk form penilaian yang ada **sudah menyebut bobot berbeda per butir**,
jadi menundanya berarti angka yang keluar salah sejak hari pertama dan orang telanjur
memakainya.

`FormField` bertambah `Weight *float64` (bawaan 1 bila kosong). Nilainya **bobot relatif**,
bukan persentase yang wajib berjumlah 100: bobot 3 berarti tiga kali lebih berat dari 1.

Dua alasan memilih relatif:

1. **Menyunting form tidak memaksa menyetel ulang seluruh bobot.** Dengan persentase
   wajib-100, menghapus satu pertanyaan membuat totalnya 85 dan form tak sah sampai semua
   bobot lain disentuh — beban yang muncul setiap kali form berubah.
2. **Angka persen tetap bisa dimasukkan apa adanya.** Bila HR mengisi 40, 20, 10, dan 30,
   hasilnya identik dengan persentase, sebab jumlahnya memang 100.

Agar tetap bisa diaudit, builder menampilkan **persentase efektif** tiap pertanyaan yang
dihitung dari bobot relatifnya. Yang diisi bobot, yang dibaca persen.

Validasi: bobot negatif ditolak; nol diperbolehkan (artinya pertanyaan itu tidak ikut
menghitung, berguna untuk pertanyaan pelengkap); total bobot nol pada seluruh pertanyaan
`scale` menghasilkan `Overall` kosong, bukan pembagian dengan nol.

**Form lama tidak perlu migrasi**: `Weight` kosong berarti 1, dan seluruh bobot bernilai 1
menghasilkan angka yang persis sama dengan rata-rata polos.

### Rata-rata PER PENILAI, bukan per jawaban mentah

Tiap jawaban skala dinormalisasi ke 0..100 memakai batas pertanyaannya sendiri, lalu
dirata-ratakan **berbobot di dalam satu penilai** menjadi satu angka. `Overall` adalah
rata-rata **polos** dari angka-angka penilai itu.

Dua lapis ini sengaja berbeda perlakuannya. Bobot menyatakan *pertanyaan mana yang lebih
penting*, jadi tempatnya di dalam satu penilai. Antar penilai tak ada yang lebih penting —
satu orang satu suara — sehingga lapis kedua tetap polos.

⚠️ **Penyebut bobot dihitung dari pertanyaan yang DIJAWAB penilai itu, bukan dari seluruh
pertanyaan form.** Penilai yang melewati pertanyaan berbobot besar tidak lantas dianggap
memberi nilai rendah di situ; ia hanya menilai lebih sedikit hal. Memakai total bobot
seluruh form sebagai penyebut sama saja dengan menghitung pertanyaan kosong sebagai nol,
dan itu keputusan yang sudah ditolak di bagian berikutnya.

Alternatif yang ditolak: merata-ratakan seluruh jawaban mentah sekaligus. Itu membuat
penilai yang mengisi lebih banyak pertanyaan otomatis lebih berpengaruh, dan penilai yang
melewati separuh pertanyaan diam-diam mengurangi suaranya sendiri. Tak seorang pun pernah
memutuskan itu, dan ia sulit dipertahankan ketika ada yang mempersoalkan nilainya.

Satu orang satu suara juga membuat kalimat cakupan bisa ditindaklanjuti: "12 dari 20 orang
sudah menilai" menyuruh seseorang mengejar delapan orang, sedangkan "94 dari 160 jawaban"
tidak menyuruh siapa pun berbuat apa.

### Satuan: gabungan selalu 0..100, detail tetap skala asli

`Overall` selalu 0..100. `SubjectScore.Average` per pertanyaan **tidak berubah** dan tetap
memakai skala aslinya.

Alternatif yang ditolak: menampilkan skala asli bila seluruh pertanyaan seragam (mis.
"4,2" untuk form 1..5) dan beralih ke 0..100 hanya bila campur. Itu terasa lebih ramah
tapi membuat satuan satu kolom berubah-ubah tergantung isi form; dua form bersebelahan
akan menampilkan angka yang tampak sebanding padahal bukan, tanpa ada apa pun di layar
yang memberi tahu bedanya.

Karena detail per pertanyaan tetap menampilkan angka yang biasa dibaca HR, tidak ada yang
hilang. Yang gabungan sengaja dibuat berbeda supaya tidak tertukar.

### Belum dinilai berarti KOSONG, bukan nol

`Overall` bertipe `*float64` dengan `omitempty`, mengikuti `SubjectScore.Average` yang
sudah ada. Nol berarti "sudah dinilai dan hasilnya buruk" — tuduhan yang tidak dibuat
siapa pun.

Orang yang belum dinilai tetap MUNCUL di daftar dengan `Overall` kosong. Daftarnya
bertumpu pada potret, bukan pada jawaban yang masuk; kalau disusun dari jawaban saja,
orang yang paling terlewat justru lenyap dari laporan padahal dialah yang paling perlu
ditindaklanjuti.

## Perubahan kode

### Backend — `services/form-builder`

`analytics_subject.go`:

```go
type SubjectSummary struct {
    EmployeeID string
    Name       string
    Department string
    Position   string
    Responses  int
    Scores     []SubjectScore
    Overall    *float64 `json:"overall,omitempty"` // BARU, 0..100
}
```

`models_form.go` — `FormField` bertambah:

```go
Weight *float64 `bson:"weight,omitempty" json:"weight,omitempty"` // bawaan 1
```

Pointer, bukan nilai: `0` adalah bobot yang SAH (pertanyaan pelengkap yang tidak ikut
menghitung), jadi ia harus bisa dibedakan dari "tidak diisi".

Tiga fungsi murni baru, dipanggil dari `aggregateSubjects` yang sudah ada:

- `normalisasiSkala(nilai float64, min, max int) (float64, bool)` — memetakan satu jawaban
  ke 0..100. `false` bila batasnya tidak sah (`max <= min`), sehingga pertanyaan yang salah
  konfigurasi dilewati alih-alih mencemari angka.
- `bobotField(f FormField) float64` — `1` bila `Weight` nil, nilainya bila terisi.
- `skorPenilai(nilai []float64, bobot []float64) (float64, bool)` — rata-rata berbobot,
  penyebutnya jumlah bobot pertanyaan yang DIJAWAB. `false` bila tak ada jawaban skala
  atau total bobotnya nol.
- `skorGabungan(perPenilai []float64) *float64` — rata-rata polos.

`validate.go` menolak `Weight` negatif, sejalan dengan validasi field lain yang menolak
saat MENULIS dan mengabaikan saat MEMBACA.

Tidak ada endpoint baru. Tidak ada perubahan skema penyimpanan selain field opsional.

### Frontend — `erp-frontend`, PR terpisah

Dua bagian, dan ini lebih besar dari rencana awal karena bobot menuntut layar:

1. **Builder** — isian bobot pada tiap pertanyaan `scale`, plus **persentase efektif** yang
   dihitung dari bobot relatif dan ditampilkan di sebelahnya. Yang diisi bobot, yang dibaca
   persen; tanpa itu bobot relatif tak bisa diaudit siapa pun.
2. **Analisa** — satu kolom di tabel rekap, judulnya menyebut satuan eksplisit
   (**"Skor (0–100)"**). Sel kosong untuk yang belum dinilai, bukan nol atau tanda hubung
   yang ambigu.

Seluruh teks baru lewat `react-i18next` dengan key di `id.ts` dan `en.ts` sesuai ADR 0010.

BE naik lebih dulu, sesuai konvensi tim untuk perubahan kontrak.

## Test

Fungsi murni, jadi seluruhnya bisa diuji tanpa Mongo maupun HTTP.

| Kasus | Yang dikunci |
|---|---|
| Form skala seragam 1..5 | `Overall` benar dan berada di 0..100 |
| Form campur 1..5 dan 1..10 | normalisasi bekerja; jawaban tertinggi di kedua skala sama-sama jadi 100 |
| Penilai melewati sebagian pertanyaan | rata-ratanya dihitung dari yang dijawab saja, suaranya tetap satu |
| Satu penilai menjawab 8 soal, satu lagi 1 soal | keduanya berbobot sama pada `Overall` |
| Penilai mengisi form tapi TAK menjawab satu pun soal skala | ia dilewati, bukan dihitung sebagai 0 — mengisi kolom teks saja tidak berarti memberi nilai nol |
| Bobot 3 vs 1 pada dua pertanyaan | pertanyaan berbobot 3 benar-benar tiga kali lebih berpengaruh |
| Bobot diisi 40/20/10/30 (berjumlah 100) | hasilnya identik dengan perlakuan persentase |
| Bobot diisi 4/2/1/3 (kelipatan yang sama) | hasilnya SAMA dengan 40/20/10/30 — inilah arti relatif |
| Semua `Weight` nil (form lama) | hasilnya identik dengan rata-rata polos, membuktikan tak perlu migrasi |
| Penilai melewati pertanyaan BERBOBOT BESAR | penyebutnya ikut mengecil; ia tak dianggap memberi nilai rendah di pertanyaan itu |
| Satu pertanyaan berbobot 0 | tidak memengaruhi hasil, dan tidak membuat pembagian dengan nol |
| SELURUH pertanyaan `scale` berbobot 0 | `Overall` nil, bukan panik atau NaN |
| `Weight` negatif | ditolak saat menyimpan form |
| Belum dinilai siapa pun | `Overall` nil, orangnya tetap muncul di daftar |
| Form tanpa pertanyaan `scale` | `Overall` nil, bukan 0 |
| Pertanyaan `number` ada di form | tidak ikut memengaruhi `Overall` |
| `scale_max <= scale_min` | pertanyaan itu dilewati, sisanya tetap terhitung |

## Risiko

**Angka yang tampak berwibawa padahal tipis.** Satu penilai sudah cukup memunculkan
`Overall`. Kolom `Responses` yang sudah ada duduk di sebelahnya dan menjawab itu, jadi
tidak ditambahkan ambang minimum — memilih ambang berarti memutuskan berapa penilai yang
cukup, dan itu belum pernah diputuskan siapa pun.

**Rata-rata menyembunyikan sebaran.** Nilai 70 bisa berarti semua penilai memberi 70, atau
separuh memberi 40 dan separuh 100. Dua keadaan itu menuntut tindakan berbeda. Diterima
untuk sekarang; kalau ternyata mengganggu, penambahan yang tepat adalah menampilkan sebaran
di detail per pertanyaan, bukan mengganti rumus gabungannya.
