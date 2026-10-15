> Detail ingatan tim, dibaca **ON-DEMAND** dari indeks `../team-memory.md`. Jangan di-import ke `CLAUDE.md`; update cukup `git pull architecture-draft`. Induk: `## Gotchas backend Go (berlaku SEMUA service bip-erp)`.

### ⛔ Memanggil endpoint DAFTAR service lain: tiga kegagalan senyap, semuanya dalam satu hari

Modul audit memanggil `/accounting/*` milik integration-service dan kena **ketiganya berturut-turut** (2026-09-06). Tak satu pun melempar galat, ketiganya menghasilkan angka yang masuk akal, dan yang paling berbahaya justru terdengar paling meyakinkan.

| Yang keliru | Gejalanya | Akibat nyata |
|---|---|---|
| Membaca `data` sebagai array | `cannot unmarshal object into []T` | 3 uji `gagal_tarik` entah berapa lama |
| Nama field ditebak Indonesia | field nol, TANPA galat | 24 dari 25 aset nyaris ditandai melanggar |
| Halaman pertama = populasi | angka wajar, kalimat percaya diri | "Seluruh **25** jurnal punya keterangan" atas **7.371** |

Aturan yang berlaku untuk endpoint daftar service mana pun:

- ⛔ **`data` TIDAK PERNAH array telanjang.** integration-service selalu membungkusnya dalam kunci bernama beserta metadata: `data.jurnal[]`, `data.aset[]`, `data.aging{}`. Yang mengirim struct tunggal (`akun-saldo`) memang menaruhnya langsung di `data` — jadi bentuknya berbeda per endpoint dan **wajib dilihat, bukan diasumsikan**. Kunci yang tak ada harus jadi **galat**, bukan daftar kosong: daftar kosong mendarat di "bersih" dan pemeriksaan yang tak membaca satu baris pun terbaca sebagai lolos.
- ⛔ **Nama field mengikuti SUMBERNYA, bukan ejaan modul Anda.** Yang meneruskan Accurate memakai `number`/`transDate`/`description`; yang sudah dinormalkan memakai Indonesia (`nomor`, `biaya_perolehan`). Bahkan dalam satu respons bisa campur. Salah nama tidak melempar apa pun — ia menghasilkan nol, dan nol yang menyamar sebagai data itulah yang menerbitkan temuan palsu.
- ⛔ **BERPAGINASI, bawaannya 25.** Permintaan tanpa `page`/`page_size` mengembalikan 25 baris pertama, dan `total` di responsnya adalah satu-satunya yang memberi tahu ada berapa sebenarnya. **Jangan pernah memperlakukan satu halaman sebagai populasi.** Batas atas `page_size` = 100. Menarik sampai lengkap WAJIB punya dua penjaga: berhenti sebelum `total` adalah **galat** (hasil sebagian mengembalikan bug yang sama dengan angka lebih besar), dan paginasi yang diabaikan endpoint harus dihentikan berbatas — kalau tidak penarikan berputar sampai gateway memutusnya dan terbaca sebagai "audit lambat".

- ⛔ **`"data": null` BUKAN balasan rusak, dan pengurai ber-pointer tak bisa membedakannya dari kunci yang HILANG.** Amplop integration-service memakai `Data any` ber-`omitempty` (`internal/interface/http/response.go`), sedangkan repositorinya mengembalikan **slice nil** saat nol dokumen (`var result []T` lalu `cursor.All`, yang berakhir `sliceVal.Slice(0, index)` sehingga slice nil tetap nil). Slice nil di dalam interface non-nil **tidak dibuang `omitempty`** — ia terbit sebagai `null`. Konsumen yang menulis `Data *[]T` lalu menguji `== nil` untuk menandai "kunci hilang" karena itu **ikut menangkap jalur normalnya**: setiap pemanggil yang memang tak punya baris menerima galat, bukan daftar kosong. Terjadi 2026-09-16 di cakupan toko komplain gudang (warehouse memanggil `/icc/mappings/me`): setiap orang marketing yang tak memegang toko akan menerima **500** saat membuka layarnya, persis kebalikan dari kegagalan yang hendak dicegah butir pertama di atas. Yang benar **`json.RawMessage`**: kunci absen tetap galat, `null` jadi nol baris, bentuk yang bukan array tetap galat. ⚠️ Butir pertama ("kunci yang tak ada harus jadi galat") tetap berlaku dan tidak dibatalkan — yang ditambahkan di sini cuma bahwa `null` ada di sisi seberangnya, dan keduanya wajib dibedakan secara eksplisit.

⚠️ **Tak satu pun dari ketiganya bisa ditangkap test yang memalsukan sumbernya**, dan itu inti pelajarannya. `sumberTiruan` mengembalikan struct Go langsung, jadi 149 test hijau sementara tiga uji tak pernah menarik satu baris pun. Yang menangkapnya cuma dua hal: **test kontrak yang mengurai rekaman respons sungguhan** apa adanya (`services/finance/audit_kontrak_test.go`), dan **mengukur ke sumbernya lalu membandingkan dengan yang dicatat konsumen**.

⚠️ Menarik populasi penuh ada ongkosnya: 7.371 jurnal = 74 permintaan, **terukur 21 detik** di dev. Batas gateway 30 detik, jadi tombol yang memicunya lewat gateway ada di ambang sementara penjadwal yang memanggil langsung tidak. Bila kelak menggigit, gejalanya **502 di tombol sementara penarikan terjadwal tetap berhasil** — kombinasi yang membingungkan kalau tak diketahui dari awal.

