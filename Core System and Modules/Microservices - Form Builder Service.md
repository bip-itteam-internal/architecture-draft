## Deskripsi

*Form Builder Service adalah pembuat form dinamis tanpa coding: tim IT dan HRGA menyusun form sendiri (9 tipe pertanyaan), menerbitkannya ke sasaran tertentu, membaca rekap jawabannya, dan mengekspornya ke CSV — tanpa rilis kode untuk tiap form baru. Service ini juga menyediakan satu endpoint kepatuhan yang dipakai [[Microservices - Attendance Service]] untuk menahan clock-in mobile bila ada form wajib yang belum diisi.*

- **Stack:** Go + Fiber v2 + MongoDB (database sendiri `form_builder_db`)
- **Path:** `services/form-builder`
- **Port:** 6986 (internal, `expose`; tidak dipublish ke host)
- **Status**: ⚠️ **Merged ke `main` 2026-08-01** (PR [#849](https://github.com/bip-itteam-internal/bip-erp/pull/849), merge commit `4f546f14`), backend lengkap dan teruji (122 unit test). **BELUM live di dev** per pemeriksaan 2026-08-01: `GET /health?check=form-builder` di gateway dev masih balas `400 unknown service`, artinya gateway di sana masih binary pra-merge. **FE kelola di [[APP - Web ERP]] sudah ada** (branch `feat/form-builder` di repo `erp-frontend`, **belum merge**): daftar form + builder. **Yang masih kosong**: layar analisa/export di web, dan renderer pengisian di [[APP - MyBharata]] — sehingga karyawan belum punya cara mengisi form sama sekali.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Staf/SPV IT | Tech Development | `system_roles["it"]` = staff/supervisor/admin | Web |
| Staf/SPV HRGA | General Affair | `system_roles["ga"]` = staff/supervisor/admin | Web |
| Karyawan | Semua divisi | Terautentikasi (tanpa syarat peran) | Mobile (MyBharata), Web |

- **Tujuan** — IT/HRGA: membuat form ad-hoc (survei, deklarasi, pendataan) tanpa menunggu rilis kode, lalu membaca hasilnya. Karyawan: mengisi form yang ditujukan kepadanya.
- **Pain point** — sebelum ini setiap form baru berarti satu siklus development; permintaan pendataan mendadak tak terlayani.
- **Aksi utama** — IT/HRGA: susun pertanyaan → tentukan sasaran → terbitkan → baca analisa/export. Karyawan: buka daftar form → isi → kirim.

> Peran `security` milik GA (satpam) **sengaja dikecualikan** dari pengelola form: key `ga`-nya untuk buku tamu, bukan membangun form.

## Endpoint / Fitur (Sudah Diimplementasikan)

Prefix gateway `/api/form-builder/*`. Kontrak lengkap: [[API - Form Builder Service]].

**Kelola form** (gerbang `requireFormManager`: `system_roles` `it` **atau** `ga`)
- `POST /forms` · `GET /forms` — buat & daftar form. Daftar **hanya menampilkan form milik modul yang boleh dikelola pemanggil**, jadi staf GA tak melihat form IT.
- `GET /forms/:id` · `PATCH /forms/:id` · `DELETE /forms/:id` — detail, sunting, hapus lunak (`deleted_at`).
- `PATCH /forms/:id/status` — `draft` → `published` → `closed`. Form terbit **tidak bisa mundur** ke draft.
- `owner_module` tak bisa dipindah setelah dibuat (memindahkannya akan membuat form lenyap dari daftar pemiliknya sendiri).
- **Susunan pertanyaan terkunci begitu ada jawaban masuk** (balas `409`). Menyunting field setelah orang menjawab membuat jawaban lama menunjuk pertanyaan yang sudah berubah arti, dan analisanya diam-diam jadi salah.

**Tipe pertanyaan (9)** — `short_text`, `long_text`, `number`, `date`, `time`, `dropdown`, `radio`, `checkbox`, `scale`. Validasi struktur (key unik, options wajib untuk tipe pilihan, rentang scale maksimal 10 langkah, `min ≤ max`) dan validasi jawaban (tipe cocok, nilai ∈ options, batas angka & panjang teks, format `YYYY-MM-DD` dan `HH:MM`) keduanya **fungsi murni** — teruji tanpa Mongo.

**Sasaran form (audience)** — `all`, `departments`, atau `employees`. Diresolusi dari **header identitas yang sudah dibawa gateway** (`BIP-Employee-ID`, `BIP-Department`), sehingga service ini **tak memanggil satu service pun**. Tipe sasaran yang tak dikenal **gagal-tertutup** (tidak cocok), supaya salah ketik tak pernah menahan presensi sekantor.

**Pengisian** (cukup karyawan terautentikasi)
- `GET /me/forms` — form terbit yang ditujukan ke pemanggil, lengkap dengan penanda `submitted` dan `blocks_attendance`.
- `POST /me/forms/:id/responses` — kirim jawaban. Form non-`published` ditolak, dan bukan-sasaran ditolak `403`.
- `GET /me/responses` — riwayat jawaban sendiri.
- **Idempoten**: pengiriman identik dalam 2 menit dianggap retry dan dibalas sukses tanpa insert baru. Sidiknya di-hash dari jawaban yang **kuncinya diurutkan lebih dulu**, jadi klien yang menyusun ulang payload saat retry tetap terdeteksi. Pola sejenis dipakai leave request di [[Microservices - Attendance Service]].
- `settings.single_response` membatasi satu jawaban per karyawan (balas `409`).

**Analisa & export**
- `GET /forms/:id/analytics` — hitungan per opsi (**termasuk opsi ber-nol, urut sesuai definisi form** supaya grafik tak berganti susunan tiap data bertambah), rata-rata/min/maks untuk `number` & `scale`, cuplikan 5 jawaban teks terbaru, `answered`/`skipped` per pertanyaan, tren harian, dan tingkat pengisian.
- `GET /forms/:id/responses` — daftar jawaban berhalaman.
- `GET /forms/:id/export` — CSV; satu pertanyaan = satu kolom secara konsisten, checkbox digabung `"; "` dalam satu sel, angka tanpa nol berlebih.

**Kepatuhan presensi**
- `GET /internal/compliance` — dipakai attendance-service saat clock-in. Membalas `blocking` (mode `block`) dan `warning` (mode `warn`).

## Keputusan yang menjaga presensi tetap hidup

Fitur ini menyentuh jalur clock-in, jadi beberapa keputusan sengaja konservatif:

- **Gerbang gagal-tertutup pada data cacat.** Gerbang tanpa jendela tanggal lengkap dianggap **tidak aktif** (gerbang tanpa tanggal berakhir berarti presensi tertahan selamanya bila form-nya dilupakan). Mode enum yang tak dikenal **turun kelas jadi peringatan**, bukan penahan.
- **`mode` default `warn`** saat form dibuat. Menahan presensi harus jadi pilihan yang ditulis eksplisit.
- **Jendela tanggal wajib** saat gerbang menyala.
- **Identitas `/internal/compliance` terkunci ke header.** Query param hanya dihormati bila **tak ada** identitas header sama sekali (ciri panggilan service-to-service). Tanpa aturan ini, karyawan mana pun bisa mengirim `?employee_id=<orang-lain>&company_id=<perusahaan-lain>` dan mengintip form tertunda milik orang lain menembus batas tenant — persis kelas bug di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]. Header aman dijadikan sandaran karena gateway membuang seluruh namespace `BIP-*` kiriman klien lalu mengisinya dari klaim JWT.

## Multi-perusahaan (tenant)

Ter-scope `company_id` **sejak awal**, bukan ditambal belakangan: stempel `common.CompanyID` saat menulis, `common.EffectiveCompanyID` saat membaca (override `?company=` hanya untuk admin pusat). Lihat [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

## Belum Diimplementasikan / Catatan

- **Sudah di `main`, belum live di dev.** Diperiksa 2026-08-01: gateway dev (`10.10.10.121:6969`) sehat untuk employee/attendance/recruitment tapi membalas `400 unknown service` untuk `form-builder`, jadi binary gateway di sana masih pra-merge.
- ✅ **`.env` dev dan prod SUDAH diisi (2026-08-01)**: `FORM_BUILDER_SERVICE_PORT=6986` + `MONGO_FORM_BUILDER_DB=form_builder_db`. Diverifikasi lewat `docker compose config` di kedua server — `FORM_BUILDER_MODULE_URL` merender `http://form-builder-service:6986` di blok gateway maupun attendance. Backup disimpan (`~/apps/bip-erp/.env.bak-*`). Port 6986 bebas di keduanya. **Container belum di-restart**, jadi kode yang berjalan masih pra-merge.
- ⚠️ **Kenapa dua variabel itu wajib ada SEBELUM gateway di-redeploy.** Berbeda dari attendance (yang sengaja menaruh URL form-builder DI LUAR map tervalidasi), gateway memasukkan `form-builder` ke `InternalURL` dan menjalankan `validation.ValidateInternalURL` — nilai kosong berarti **gateway panic saat boot dan SELURUH ERP ikut mati**. `docker-compose.yml` meredam ini karena nilainya dirakit dari string literal (`http://form-builder-service:${...}`) sehingga tak pernah benar-benar kosong, tapi variabel port yang hilang tetap menghasilkan URL rusak dan semua `/api/form-builder/*` gagal. Deploy gateway HARUS memakai compose yang ikut ter-merge, bukan env lama.
- **Konsumen yang sudah ada**: FE kelola di [[APP - Web ERP]] memakai `POST/GET/PATCH/DELETE /forms*`. **Endpoint `/forms/:id/analytics`, `/forms/:id/responses`, dan `/forms/:id/export` sudah siap tapi BELUM ada yang memanggilnya** — layar analisa & export menyusul.
- **Endpoint pengisian (`/me/*`) belum punya konsumen sama sekali.** Pengisian direncanakan lewat [[APP - MyBharata]] yang belum dibangun, dan web sengaja tak menyediakan halaman isi form. Konsekuensinya gerbang mode `block` belum boleh dinyalakan di produksi — lihat [[IT - Form Builder]].
- **Upload file** belum didukung (menyusul via [[Microservices - File Service]], cap 4 MB).
- **Logika percabangan** (lompat seksi berdasarkan jawaban) belum ada.
- **Jumlah sasaran tidak dihitung otomatis.** Untuk sasaran `all`/`departments`, penyebut tingkat pengisian memakai `audience.estimated_size` yang diisi manual pembuat form — service ini sengaja tak memanggil employee-service. Bila kosong, tingkat pengisian **tidak dilaporkan** (menampilkan 0% lebih menyesatkan daripada tak menampilkan apa pun).
- **Agregasi dibatasi 20.000 jawaban.** Bila terlampaui, total sebenarnya tetap dilaporkan dan hasil ditandai `truncated` + `sample_size`, sedangkan tingkat pengisian disembunyikan. Export menandai lewat header `X-Export-Truncated`.
- **`attendance_gate.start_date`/`end_date` hanya menerima RFC3339** (mis. `2026-08-01T00:00:00Z`); kiriman `"2026-08-01"` akan ditolak dengan pesan parse JSON yang tidak informatif. Perlu dibereskan saat FE dibangun.
- **RBAC masih pola `system_roles` kasar**, belum berkatalog permission-set per [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]. Form Builder menambah satu lagi ke daftar modul yang belum berkatalog.
- **Form approval yang sudah matang JANGAN dimigrasikan ke sini** (leave/overtime/koreksi presensi) — semuanya punya workflow & rantai approval sendiri. Form Builder untuk kasus baru/ad-hoc.

## Dependensi & Integrasi

- **MongoDB** `form_builder_db` — koleksi `forms`, `form_responses`. Index dibuat idempoten saat boot. Lihat [[DB - Overview and Notes]].
- [[CORE - API Master Gateway]] — satu-satunya pintu masuk; modul `form-builder` di map `InternalURL`.
- [[Microservices - Attendance Service]] — **konsumen** `GET /internal/compliance` pada jalur clock-in mobile.
- Auth mengikuti [[CORE - SSO Flow]]; identitas datang sebagai header `BIP-*`.
- **Tidak memanggil service lain.** Ini disengaja: sasaran form diresolusi dari header, sehingga tak ada entri di `InternalURL` milik service ini dan tak ada service yang bisa membuatnya gagal boot.

## Dokumen Terkait

- [[IT - Form Builder]] — konsep & latar belakang
- [[API - Form Builder Service]] — daftar endpoint
- [[Microservices - Attendance Service]] · [[CORE - API Master Gateway]] · [[DB - Overview and Notes]]
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[APP - Web ERP]] · [[APP - MyBharata]] — klien yang belum dibangun
