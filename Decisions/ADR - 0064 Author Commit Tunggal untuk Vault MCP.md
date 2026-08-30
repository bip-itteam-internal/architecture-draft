## Untuk Manajemen

- **Yang berubah di layar**: tidak ada. Ini keputusan tentang bagaimana tulisan manager lewat Claude dicatat di riwayat dokumentasi, dan tak seorang pun melihatnya dari aplikasi.
- **Siapa terdampak**: sembilan orang yang terdaftar boleh memakai MCP vault, dan siapa pun yang kelak menelusuri "siapa mengubah dokumen ini".
- **Tidak dijanjikan**: sesudah keputusan ini, riwayat git **tidak lagi bisa membedakan** manager satu dari yang lain lewat akun GitHub. Nama penulisnya masih tercatat, tetapi hanya sebagai teks, dan teks itu tidak diverifikasi oleh siapa pun.
- **Besaran kerja**: kecil, dan justru lebih kecil daripada alternatifnya. Keputusan ini menghapus kebutuhan menambah endpoint baru di layanan kepegawaian.

## Deskripsi

*Seluruh commit yang lahir dari tulisan manager lewat Vault MCP memakai SATU alamat email, `bharataitteam@gmail.com`, siapa pun managernya. Nama penulis tetap diisi per-manager sehingga `git log` masih menyebut siapa yang menulis, tetapi seluruhnya bermuara ke satu akun GitHub.*

- **Status**: ✅ **Accepted**, 2026-08-30. Menyimpangi Keputusan 3 di [[Microservices - Vault MCP Service]], yang berstatus mengikat dan menuntut ADR untuk diubah.
- **Path di repo**: `bip-erp/services/vault-mcp/vault_tulis.go` · `bip-erp/services/vault-mcp/konfig.go` · env `VAULT_MCP_AUTHOR_EMAIL`
- **Tanggal**: 2026-08-30

## Context

[[Microservices - Vault MCP Service]] § Keputusan yang mengikat nomor 3 menetapkan bahwa setiap tulisan menjadi commit dengan `--author` yang diambil dari identitas ERP manager yang bersangkutan. Alasannya ditulis eksplisit: `git log` menjawab siapa menulis apa, `git blame` menjawabnya per baris, dan `git revert` membatalkannya tanpa merusak riwayat, sehingga **tidak ada mekanisme audit baru yang perlu dibangun**. Dokumen itu juga menyebut ini "satu-satunya pengaman yang ada", karena keputusan pemilik adalah manager boleh menulis ke seluruh vault tanpa gerbang review.

Saat menyiapkan irisan 2 ditemukan bahwa alamat email tidak tersedia di jalur yang ada:

- **ERP JWT tidak memuat klaim email.** Klaim yang benar-benar diterbitkan gateway hanya `employee_id`, `full_name`, `username`, `system_roles`, `department`, `position`, `company_id` (`shared-library/auth/jwt.go` `SignJWT`).
- Alamatnya ada di koleksi `personal_data` dengan nama field **`email_address`**, dan field itu **tidak** ber-`omitempty` sehingga string kosong adalah nilai yang sah. Berapa dari sembilan orang di daftar-izin yang emailnya benar-benar terisi **belum diukur**.
- Satu-satunya rute internal yang membawanya, `GET /internal/aggregate/employee/:employee_id`, digerbang `RequireHRISStaff` dan mengembalikan **password hash dan pin** ikut serta. Memanggilnya untuk sekadar mengambil email berarti menarik rahasia yang tak ada hubungannya dengan menulis dokumen.

Jalan yang tersisa untuk mempertahankan Keputusan 3 adalah menambah endpoint internal sempit di employee-service, yang berarti irisan 2 menyentuh layanan lain.

Pemilik memutuskan 2026-08-30 untuk memakai satu alamat.

## Decision

Satu alamat untuk seluruh commit dari Vault MCP, dibaca dari env `VAULT_MCP_AUTHOR_EMAIL`.

Yang **tetap** per-manager: **nama** author. Bentuk commitnya `Nama Manager <bharataitteam@gmail.com>`. Yang dipilih pemilik adalah alamatnya; menyeragamkan namanya juga akan membuang keterlacakan yang masih bisa dipertahankan tanpa ongkos apa pun.

Env kosong berarti tool tulis **tidak didaftarkan sama sekali**, bukan service gagal naik. Vault MCP sudah melayani jalur baca di produksi, dan menolak naik karena env tulis belum terisi akan mematikan sesuatu yang sedang bekerja demi fitur yang belum dipakai siapa pun.

## Consequences

**Yang hilang.** `git blame` berhenti menjawab pertanyaan "siapa menulis baris ini" dengan identitas yang bisa diverifikasi. Nama di field author adalah teks yang diisi server dari sesi, dan tak ada yang memeriksanya terhadap akun GitHub mana pun. Bila dua manager menulis di dokumen yang sama, riwayatnya tetap membedakan mereka lewat nama, tetapi seluruh commit tampil sebagai milik satu akun di antarmuka GitHub.

**Yang tersisa sebagai pengaman.** `git revert` tetap bekerja penuh, dan tetap menjadi cara membatalkan tulisan yang keliru. Dok desain menyebut keterlacakan **dan** kemudahan membatalkan sebagai pasangan yang menahan kesalahan; sesudah keputusan ini yang tersisa tinggal yang kedua.

**Yang justru menjadi lebih sederhana.** Irisan 2 tidak menyentuh employee-service sama sekali. Tidak ada endpoint internal baru, tidak ada kredensial antar-service baru, dan tidak ada pertanyaan tentang apa yang harus terjadi bila `email_address` seorang manager kosong.

**Yang harus dilakukan bila keputusan ini dicabut.** Jalur yang dibatalkan tercatat di § Context: tambah endpoint internal sempit di employee-service yang mengembalikan `email_address` saja, isi `Identitas.Email` di `oauth_callback`, dan putuskan lebih dulu perilaku untuk email yang kosong. Mengukur berapa orang yang emailnya terisi adalah langkah pertamanya.

**Yang TIDAK boleh disimpulkan dari ini.** Keputusan ini tidak melonggarkan daftar-izin, tidak menghapus pemisahan scope baca dan tulis, dan tidak mengubah aturan bahwa penyaringan hak akses dikerjakan di service sumber.

## Dokumen Terkait

- [[Microservices - Vault MCP Service]], Keputusan 3 yang disimpangi keputusan ini
- [[RUN - Menyambungkan Claude ke Vault MCP]], prosedur pemakaian dan pemberian akses
- [[CORE - SSO Flow]], alur identitas yang ditumpangi, dan tempat ketiadaan klaim email berasal
