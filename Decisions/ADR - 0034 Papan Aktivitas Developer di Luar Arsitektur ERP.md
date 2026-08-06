**Status**: ✅ Diputuskan dan dijalankan 2026-08-04. Sistemnya live; rinciannya di [[IT - Papan Aktivitas Developer]].

## Context

Tim tidak punya cara melihat kontribusinya sendiri. Yang ada hanya `git-recap-tool`, satu skrip Python yang memindai repo di laptop masing-masing untuk satu author dan menghasilkan CSV. Manual, per-mesin, tidak bisa dibagi.

Audit 3 bulan (4 Mei sampai 4 Agustus 2026) atas seluruh organisasi GitHub menemukan kondisi yang membuat papan semacam ini bernilai: dari 1.702 PR, hanya 38 (2,2%) pernah di-review orang lain, 90% di-merge sendiri dengan median 2,2 menit, dan 72,4% commit datang dari dua orang. Angka-angka itu tidak terlihat oleh siapa pun sebelumnya.

Kebutuhan yang diminta: **papan peringkat yang selalu terkini, dibuka lewat satu tautan, agar tiap developer bisa mengukur dirinya sendiri terhadap tim.** Empat batasan ditetapkan pemesan di awal: pembaruan **seketika**, **gratis**, di-host **pihak ketiga**, dan **tanpa login**.

Fakta yang membatasi pilihannya:

- **Arsitektur ERP tidak cocok untuk ini.** [[CORE - API Master Gateway]] dan pola service Go + MongoDB dirancang untuk data bisnis dengan RBAC per posisi ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). Papan ini justru sengaja tanpa autentikasi.
- **"Seketika" menuntut endpoint publik yang selalu hidup.** Server ERP di balik gateway tidak menerima webhook dari luar tanpa membuka jalur baru.
- **Datanya bukan data perusahaan dalam pengertian ERP.** Isinya metadata aktivitas Git: siapa, kapan, berapa banyak. Tidak menyentuh database ERP mana pun dan tidak menghasilkan angka yang dipakai proses bisnis.
- **Ongkos memakai jalur ERP tidak sebanding.** Menambah service Go, database, rute gateway, dan RBAC untuk satu halaman baca-saja yang sengaja publik berarti membayar seluruh ongkos arsitektur tanpa memakai satu pun manfaatnya.

## Decision

**Papan aktivitas developer dibangun di luar arsitektur ERP: repo terpisah, stack terpisah, infrastruktur terpisah. Penyimpangan ini terbatas pada sistem ini dan tidak menjadi preseden.**

1. **Repo sendiri**, `bip-itteam-internal/dev-activity-board`, bukan bagian bip-erp maupun erp-frontend.
2. **Cloudflare Workers + D1 + Durable Object**, TypeScript. Bukan Go, bukan MongoDB, tidak lewat [[CORE - API Master Gateway]], tidak memakai SSO.
3. **Akses publik lewat tautan** berpotongan URL acak panjang. Itu **bukan** autentikasi dan tidak boleh dianggap begitu; ia hanya membuat alamatnya tidak gampang ditemukan orang luar. Konsisten dengan semangat [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]: ketidakjelasan alamat bukan gerbang keamanan.
4. **Judul commit tidak pernah disimpan.** Halamannya publik, dan judul commit paling sering membocorkan rencana produk. Yang tidak pernah masuk database tidak bisa bocor.
5. **Kepemilikan atas nama tim, bukan pribadi.** Akun Cloudflare dan token GitHub yang dipakai Worker memakai akun bersama tim IT, bukan akun perorangan. PAT pribadi ikut mati saat orangnya dinonaktifkan. Identitas akunnya dicatat di [[IT - Papan Aktivitas Developer]], yang tidak ikut terbit ke wiki.
6. **Tidak menyentuh data ERP.** Satu-satunya sumber adalah GitHub. Tidak ada penulisan ke database service mana pun, sehingga [[ADR - 0002 Database-per-Service]] tidak tersentuh.

**Yang ditolak beserta alasannya:**

- **Membuat service Go di bip-erp.** Akan menuntut rute gateway, RBAC, dan database untuk satu halaman baca-saja yang sengaja publik. Seluruh ongkos, tanpa manfaat.
- **Menaruhnya di server ERP.** Webhook menuntut endpoint publik selalu hidup; membuka jalur itu di server produksi menambah permukaan serang demi kebutuhan non-bisnis.
- **GitHub Actions + Pages.** Tidak ada pihak ketiga baru, tapi perbaruan sekitar satu menit (melanggar syarat "seketika") dan tiap repo harus dipasangi workflow sendiri.
- **Vercel.** Paket gratisnya melarang penggunaan komersial, dan fungsi serverless-nya tidak memegang koneksi terbuka sehingga "seketika" turun jadi polling.

## Consequences

**Konsekuensi yang diterima:**

- **Metadata aktivitas developer tersimpan di infrastruktur pihak ketiga** (Cloudflare). Bukan kredensial dan bukan data bisnis, tapi tetap data internal.
- **Siapa pun yang memegang tautan bisa membukanya**, termasuk dari luar perusahaan bila tautannya bocor. Diredam dengan tidak menyimpan judul commit dan hanya menampilkan angka agregat.
- **Stack ini tidak dikuasai tim seperti Go.** Kalau pemeliharaannya jadi beban, migrasi ke jalur ERP tetap mungkin karena datanya kecil dan sumbernya GitHub, bukan state yang unik.
- **Tidak ada jejak audit siapa membuka papan**, karena tidak ada login.

**Penyimpangan yang dicatat eksplisit:**

Sistem ini melanggar pola yang berlaku di vault ini pada hampir semua sumbu: bahasa, database, gerbang, autentikasi, dan hosting. **Itu disengaja dan terbatas pada sistem ini.** Sistem lain yang mengolah data bisnis tetap mengikuti arsitektur ERP. Bila muncul kebutuhan serupa (dashboard internal baca-saja, non-bisnis), keputusan ini boleh dirujuk, tapi **tidak otomatis berlaku** dan perlu ADR sendiri.

**Yang belum diputuskan (TBD):**

- Apakah papan ini nantinya perlu autentikasi bila isinya diperluas ke data yang lebih sensitif.
- Siapa penanggung jawab kedua bila pemegang akun bersama berhalangan. Saat ini seluruh organisasi GitHub bergantung pada **satu** akun owner, dan itu risiko yang lebih besar daripada papan ini sendiri.
- Apakah temuan dari papan ini (kesenjangan review, pemusatan kepemilikan komponen) akan ditindaklanjuti jadi kebijakan, atau berhenti sebagai informasi.

## Terkait

- [[IT - Papan Aktivitas Developer]] — implementasi, aturan perhitungan, dan batasan pemakaian angkanya
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] — semangat yang sama: ketidakjelasan alamat bukan gerbang
- [[ADR - 0002 Database-per-Service]] — tidak tersentuh, karena sistem ini tidak menulis ke database ERP
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] — model akses ERP yang sengaja tidak dipakai di sini
- [[CORE - API Master Gateway]] — gerbang yang sengaja dilewati
- [[IT - Development Apps and Tools]] · [[IT - Big Pictures]]
