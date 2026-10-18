# Judge Desain: gerbang layar di AI Engineering Loop

Status: rancangan, menunggu persetujuan user (2026-10-18).

## Maksud dan alasannya

Layar erp-frontend yang lolos test dan judge masih sering terasa salah begitu dibuka, dan yang
menemukannya pemilik produk dari layar, bukan gerbang. Contoh terukur di `team-memory.md` dan
`ui-checklist.md`: tombol Kembali dirakit di badan halaman (Portal KPI, erp-frontend#1292), 16 dari 24
`Sheet` menggulir judul dan aksinya, padding ganda `p-6`, dan M-04 (2026-10-14) yang merakit kartu,
tabel, dan kotak peringatan sendiri lalu ditegur dari layar prod (diperbaiki erp-frontend#2468).

Hari ini `/judge` langkah 3 sudah mengirim `ui-checklist.md` ke `loop-judge` bila diff menyentuh layar.
Itu tidak cukup karena dua hal:

1. `loop-judge` menilai brief, arsitektur, dan solusi nakal sekaligus; UI cuma satu butir dari
   perhatiannya, dan kasus M-04 lolos jenis pemeriksaan ini.
2. Tak ada yang **melihat** layarnya. Kemudahan dipakai (aksi utama, keadaan kosong/galat/loading,
   alur yang putus) dan tata letak (luber, tumpang-tindih, tema gelap) tidak terbaca dari diff, dan
   jsdom tak punya mesin layout.

Yang dibangun: satu penilai khusus layar, read-only, yang menilai diff plus tangkapan layar sungguhan,
dan boleh menggagalkan loop.

## Tujuan

- Menangkap **dua jenis** masalah sebelum PR (keputusan user): ketidakkonsistenan tampilan terhadap
  aturan tertulis, dan layar yang membingungkan dipakai.
- Temuan **kritis** judge desain **memblokir** PR, sama seperti judge biasa (keputusan user).
- Bukti layar diambil oleh skrip yang deterministik, bukan oleh agen.

## Bukan tujuan

- Bukan agen yang merancang layar. Ia menilai, tidak memperbaiki dan tidak mengusulkan desain baru.
- Bukan MyBharata (Flutter) untuk saat ini. Cara menangkap layarnya lain; tunggu erp-frontend terbukti.
- Bukan regresi piksel (membandingkan gambar sebelum/sesudah).
- Bukan pengganti review manusia di PR, dan bukan sistem desain baru.
- Tidak menyentuh dev/prod sungguhan. Layar dirender dari build worktree dengan API distub.

## Anti-tujuan (gagal walau secara teknis jalan)

- **Sering salah tuduh.** Judge yang salah tuduh akan diabaikan, dan judge yang memblokir sambil salah
  tuduh lebih buruk lagi: ia membakar percobaan perbaikan untuk masalah palsu. Catatan
  `erp-frontend-verifikasi-layar-tanpa-backend` memuat lebih dari 13 jebakan yang terbaca seperti cacat
  fitur padahal bukan (overlay yang menelan klik, tema gelap palsu, Recharts rusak oleh tangkapan
  penuh, tombol disabled tampak menyala, `Card` tanpa `data-slot`).
- **Gerbang permanen merah karena infrastruktur.** Chrome yang gagal menyala tidak boleh memblokir PR;
  itu mengulang pelajaran `pnpm test` yang tak pernah hijau sehingga penjaganya tak terdengar.
- **Dua penilai menilai aturan yang sama** dengan hasil berbeda (satu fakta satu tempat).
- **Menyalin isi `ui-checklist.md`** ke agen atau command. Rujuk path-nya.

## Batasan

- Mesin dev Windows: PowerShell, bukan Bash. Chrome di `C:\Program Files\Google\Chrome\Application\chrome.exe`.
- Run penuh (build, test) mengantre lewat `antre.ps1`. Build sudah dikerjakan gerbang deterministik
  `/judge` langkah 1; tangkapan memakai hasil build itu (`pnpm start -p <port>`), bukan `pnpm dev`.
- Jangan membunuh semua proses `chrome` (browser user ikut mati). Hentikan hanya proses berprofil uji
  dan pohon proses pemilik port `pnpm start`.
- Runner dilarang membaca prod, jadi data stub tidak boleh disalin dari prod.
- Batas percobaan loop tetap 3 total; judge desain tidak menambah percobaan.
- Kit vault: perubahan di `.agent-kit/`, bump versi, `init` menyalin ke `.claude/`.

## Yang sudah diputuskan

### Bagian-bagiannya

| Bagian | Jenis | Tugas |
|---|---|---|
| `agents/loop-judge-desain.md` | agen baru, read-only (`Read, Grep, Glob`) | menilai diff + tangkapan + ukuran DOM terhadap `ui-checklist.md`, mengembalikan verdict JSON |
| `hooks/tangkap-layar.ps1` (+ skrip Node CDP) | skrip baru | menyalakan build worktree, membuka rute dengan stub, menangkap layar dan ukuran DOM |
| manifest layar | berkas data per brief | ditulis `loop-fe`: rute yang diubah, cookie, stub API, aksi singkat |
| `commands/judge.md` | ubah | langkah tangkap + dispatch judge desain, triangulasi tiga lapis |
| `commands/kerjakan.md` | ubah | temuan desain ikut loop perbaikan; field log baru; badan PR |
| `agents/loop-fe.md` | ubah | wajib menulis manifest layar bila menyentuh layar |

### Kapan menyala

Hanya bila repo brief `erp-frontend` **dan** diff menyentuh berkas layar (komponen/halaman `.tsx` di
`src/app/` atau `src/features/` atau `src/components/`). Brief backend, docs, dan diff FE tanpa layar
(mis. hanya `lib/`, test, locale) tidak menjalankannya.

### Manifest layar (ditulis `loop-fe`)

Disimpan di luar worktree supaya tak ikut commit: `.task-plans/judge/<slug>-layar.json`. Isinya:

- `rute`: daftar path yang menampilkan perubahan (mis. `/hris/resign`), masing-masing boleh punya
  `aksi` pendek (klik teks tombol X, buka tab Y) untuk menampilkan sheet/dialog yang diubah.
- `cookie`: `system_roles` (nilai **string** per modul, bukan array), `position`, `department`, `lang`.
- `stub`: pola URL → status + body. Bentuk body diturunkan dari tipe di kode atau blok `## Kontrak`
  brief, bukan dikarang dan bukan disalin dari prod. Wajib menyertakan keadaan yang relevan untuk
  menilai lima keadaan layar: minimal **berisi** dan **kosong**; **galat** bila layar punya penanganan galat.

`loop-fe` yang menulisnya karena ia yang tahu rute dan bentuk data; judge tak boleh menulis apa pun.

### Tangkapan (skrip, bukan agen)

`tangkap-layar.ps1 -Path <wt> -Manifest <json> -Keluaran <dir>`:

- `pnpm start -p <port bebas>` atas build hasil gerbang; port 3000 bisa milik sesi lain.
- Chrome headless berprofil baru + CDP dari Node (WebSocket bawaan Node 24; tanpa puppeteer).
- Stub lewat `Fetch.fulfillRequest`, dicegat berdasarkan "bukan localhost ATAU pathname `/api/`".
  `employee/me` selalu 200; yang tak distub 500, **tidak pernah 401** (401 melempar ke `/login`).
  Header CORS + `OPTIONS` 204.
- Matriks per rute: desktop 1366 dan ponsel 390, tema terang dan gelap lewat `localStorage.theme`
  sebelum navigate (bukan `prefers-color-scheme`), bahasa `id`. Bila manifest punya beberapa keadaan
  data, tiap keadaan ditangkap di desktop terang saja supaya matriksnya tidak meledak.
- Tangkapan **viewport saja**, tak pernah `captureBeyondViewport`; halaman panjang digulir per segmen.
- Overlay pengganggu (ajakan push, panduan, tur) ditutup dulu.
- Bersama tiap gambar, skrip menulis **ukuran DOM** ke JSON: luberan (`scrollWidth > clientWidth` pada
  halaman dan wadah utama), elemen yang saling tumpang-tindih di area yang diubah, tombol `disabled`
  dan `opacity`-nya, tema aktif terbukti dari kelas `<html>`, dan rute akhir (untuk menangkap lemparan
  ke `/login`).
- Mengembalikan `ringkasan.json`: daftar tangkapan, ukuran, dan `galat` per rute.

### Judge desain (agen)

Menerima path: brief, diff, `ui-checklist.md`, `ringkasan.json` tangkapan (atau catatan tidak
tersedia), worktree. Dua sumbu:

1. **Konsistensi**: aturan tertulis `ui-checklist.md` §1 sampai §2d dan Konvensi FE di team-memory
   (komponen tim dipakai, Sheet berangka tiga, SidebarBackButton, tanpa `p-6`, Skeleton, input tanggal,
   i18n, token + mode gelap).
2. **Kemudahan dipakai**: `ui-checklist.md` §2 (satu aksi utama per area, lima keadaan layar, umpan
   balik aksi, responsif, aksesibilitas) dan alur pengguna yang disebut brief tidak putus.

Aturan anti-salah-tuduh:

- **Kritis** hanya untuk: pelanggaran aturan tertulis dengan bukti `file:line`; layar rusak yang
  **terbukti ukuran DOM** (luber, tumpang-tindih, mendarat di `/login`); keadaan layar yang tak
  ditangani padahal datanya bisa terjadi; alur di brief yang putus.
- Temuan yang hanya bersandar pada **gambar** tanpa ukuran DOM yang mendukung = informasional atau
  pertanyaan, tak pernah kritis.
- Selera ("kurang menarik", "warnanya bisa lebih baik") selalu informasional.
- Jebakan yang terbukti terbaca seperti cacat dimuat di agen sebagai daftar pendek "jangan
  dilaporkan" (tombol disabled tampak menyala, label sumbu Recharts dilewati di 390px, batang nol tak
  dirender, dll).

Keluaran: blok `<<VERDICT_DESAIN>> ... <<END>>` berbentuk sama dengan verdict `loop-judge`
(`lolos`, `temuan`, `catatan`, `ringkasan`), plus `layar_dinilai: true|false`.

### Triangulasi dan loop

- `/judge`: `lolos = gerbang AND verdict AND verdict_desain` bila judge desain menyala.
- Bila judge desain menyala, **`ui-checklist.md` tidak lagi dikirim ke `loop-judge`**. Aturan UI cuma
  punya satu penilai.
- `/kerjakan` §4: temuan kritis desain masuk "Yang harus diperbaiki (dari judge)" apa adanya, dalam
  batas 3 percobaan yang sama.
- **Tangkapan gagal tidak memblokir.** Judge desain tetap menilai dari kode saja, `layar_dinilai:
  false`, alasannya ditulis di verdict, log, dan badan PR ("layar tidak tertangkap: <alasan>").
  Yang tetap bisa memblokir di keadaan itu hanya pelanggaran aturan tertulis ber-`file:line`.
- Log `.task-plans/judge/<slug>-<n>.json` mendapat field `verdict_desain` dan `layar`
  (path `ringkasan.json` atau `"tidak tersedia: <alasan>"`).
- Badan PR memuat ringkasan judge desain dan daftar tangkapan, supaya reviewer melihat layar yang dinilai.

### Aturan tambahan (keputusan Claude, dari builder check; user boleh membantah)

1. **Mendarat di `/login` = tangkapan gagal, bukan temuan.** Hampir semua sebabnya ada di alat atau
   manifest (JWT tanpa `exp`, 401 dari URL tak distub, `system_roles` berbentuk array). **Error
   boundary** ("Terjadi Kesalahan") selalu galat kode, apa pun isi konsol dan status dokumennya: boundary
   hanya lahir dari kode aplikasi atau stub manifest, dan keduanya tanggungan eksekutor (diubah
   2026-10-18: build produksi tanpa source map, jadi syarat konsol menunjuk berkas diff tak pernah
   terpenuhi). Galat alat dan mendarat di `/login` tetap menang lebih dulu sebagai tangkapan gagal.
   Skrip tetap merekam galat konsol per rute sebagai bukti untuk judge.
2. **Manifest wajib bila diff menyentuh layar.** Yang menulisnya eksekutor mana pun yang menyentuh
   layar erp-frontend (`loop-fe`, juga `loop-test`/`loop-fix`/`loop-refactor`). Manifest tidak ada
   atau tidak sah = temuan kritis "manifest layar tidak ada", dibebankan ke eksekutor, supaya gerbang
   tidak diam-diam kosong. Manifest ikut jadi input judge desain, dan judge menilai apakah keadaan yang
   distub cukup (mis. layar daftar tanpa keadaan kosong = temuan).
3. **Satu penilai per aturan.** Saat judge desain menyala, `loop-judge` diberi instruksi melewati
   `review-checklist.md` §F (alur pengguna) dan §J (Frontend); keduanya dinilai judge desain.
   `review-checklist.md` tidak dipecah karena juga dipakai `/review` manusia. **i18n tetap milik
   `loop-judge`**: ia aturan kode yang juga berlaku untuk diff tanpa layar, dan dikeluarkan dari sumbu
   konsistensi judge desain.
4. **Hanya yang ditambahkan atau diubah diff yang bisa kritis.** Pelanggaran yang sudah ada sebelumnya
   di berkas yang sama (mis. Sheet lama, `p-6` lama) dan cacat yang terlihat di area tangkapan yang tak
   diubah = informasional, sama dengan aturan input tanggal di §J. Ini mencegah tabrakan dengan Batas brief.

### Mengukur apakah ia berguna

Salah tuduh dicatat dari dua sumber (keputusan user 2026-10-18). Mengandalkan manusia saja hampir
pasti nol data: terukur 0 `reviewDecision` dari 634 PR dalam 30 hari (`kerjakan.md` §5).

1. **Bantahan eksekutor (otomatis).** Laporan eksekutor mendapat bagian `Bantahan`: ia boleh menolak
   temuan desain dengan bukti (ukuran DOM, `file:line`, aturan yang dikutip). Pada percobaan
   berikutnya judge desain wajib memutus tiap bantahan, diterima atau ditolak, di verdict-nya.
   Bantahan diterima tercatat di log sebagai salah tuduh. Bantahan yang ditolak tetap kritis.
2. **Centang di PR (opsional, manusia).** Tiap temuan desain di badan PR tampil sebagai
   `- [ ] salah tuduh: <temuan>`. Siapa pun yang membaca PR cukup mencentangnya; `/supervise` membacanya
   lewat `gh`. Ini menangkap temuan keliru yang tidak dibantah dan tetap dituruti eksekutor.

Sesudah sekitar 10 run yang menyalakannya, `/supervise` menghitung dari log dan PR: berapa temuan
kritis desain, berapa salah tuduh (bantahan diterima + centang), dan berapa run yang tangkapannya
gagal. Angka itu dasar untuk mempertahankan pemblokiran, melonggarkan, atau mencabut.

## Diserahkan ke pembangun

- Pola tepat "berkas layar" untuk pemicu.
- Bentuk skema manifest dan `ringkasan.json` di luar butir yang disebut di atas.
- Cara skrip memilih port, batas waktu per rute, dan pembersihan proses.
- Model dan `maxTurns` agen (judge biasa memakai `opus`, 40).
- Isi persis daftar "jangan dilaporkan" agen, diambil dari catatan jebakan yang sudah ada.
- Nomor versi kit, changelog, dan bagian `team-memory.md` yang perlu menyebut gerbang baru.
