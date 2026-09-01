> **Status**: ⚠️ Implemented (ada catatan) — servicenya sudah hidup di prod dan **tiga sesi sudah terbentuk**, jadi prosedur ini terbukti bisa dituntaskan. Yang belum bisa dipastikan: apakah salah satu dari tiga itu seorang manager dari claude.ai, atau semuanya dev yang menguji lewat `claude mcp add`. Naikkan ke ✅ setelah ada satu manager yang jelas tersambung dan mendapat jawaban bersumber vault. Diukur 2026-08-30.

## Tujuan

Menyambungkan Claude (Desktop atau claude.ai) ke vault arsitektur, supaya seseorang bisa bertanya tentang sistem dan dijawab bersumber dokumentasi yang sebenarnya.

## Kapan dipakai

Saat seorang manager perlu akses baca ke vault lewat Claude, dan saat IT perlu memberi atau mencabut akses itu.

Dokumen ini ada karena tanpanya alur pemakainya terputus di langkah pertama: **tidak ada satu pun layar yang memberi tahu URL, Client ID, dan Secret**, dan orang yang tidak diberi tahu tak punya cara menemukannya sendiri.

## Prasyarat

- Akun ERP aktif, dan `employee_id`-nya sudah terdaftar di `VAULT_MCP_ALLOWED_EMPLOYEES` (lihat § Memberi akses).
- Langganan Claude apa pun. Pengguna Free dibatasi satu custom connector.
- URL, Client ID, dan Client Secret dari IT. **Jangan ditebak**; ketiganya diberikan IT lewat jalur pribadi, bukan grup.

## Langkah (untuk manager)

1. Buka **Claude → Settings → Connectors → Add custom connector**.
2. Isi **Remote MCP server URL** dengan alamat yang diberikan IT (`https://mcp.bharatainternasional.com/mcp`).
3. Buka **Advanced settings**, isi **OAuth Client ID** dan **OAuth Client Secret** dari IT.
4. Klik **Add**. Browser akan terbuka ke halaman login ERP.
5. Masuk dengan akun ERP Anda seperti biasa.

   ⚠️ **Anda tetap diminta mengetik password walau sedang login di Web ERP.** Halaman login ERP memang mengeluarkan sesi lama saat dibuka. Ini normal, bukan tanda ada yang salah, dan hanya terjadi saat menyambungkan connector.
6. Setelah login berhasil, browser kembali ke Claude sendiri dan connector muncul sebagai tersambung.

## Verifikasi

Tanyakan sesuatu yang jawabannya hanya ada di vault, misalnya *"bagaimana SSO bip-erp bekerja?"*. Berhasil bila Claude **menyebut nama dokumennya** (mis. `CORE - SSO Flow`), bukan sekadar menjawab dari pengetahuan umum.

## Memberi akses (untuk IT)

Akses diberikan **per orang**, bukan per role.

1. Tambahkan `employee_id`-nya ke `VAULT_MCP_ALLOWED_EMPLOYEES` di `.env` prod, dipisah koma.
2. Buat ulang containernya. **`restart` tidak cukup**, env dibaca saat container dibuat:
   ```
   docker compose up -d --force-recreate --no-deps vault-mcp
   ```
3. Kirimkan URL, Client ID, dan Client Secret ke orangnya lewat jalur pribadi.

**Mencabut akses**: hapus `employee_id`-nya lalu buat ulang containernya. Pencabutan langsung terasa; daftar-izin diperiksa ulang tiap panggilan, bukan hanya saat login.

## Bila gagal / Rollback

| Gejala | Sebab yang paling mungkin |
|---|---|
| Halaman **"Akun Anda belum diberi akses"** | `employee_id`-nya belum ada di daftar-izin. Hubungi kontak yang tertera di halaman itu |
| Halaman **"Alamat kembali tidak sah"** | `redirect_uri` milik Claude belum terdaftar di `VAULT_MCP_REDIRECT_URIS`. Ambil nilai persisnya dari log service, jangan ditebak |
| Claude menggantung saat menyambung, tanpa galat | `proxy_buffering` masih menyala di proxy host NPM. Klien MCP membuka stream SSE, dan buffering menahannya sehingga terlihat seperti server mati |
| **"data vault basi"** saat bertanya | `git pull` ke repo vault gagal berturut-turut. Periksa `VAULT_MCP_REPO_URL` dan jalur keluar ke GitHub. Ini disengaja: lebih baik gagal daripada menjawab dari dokumentasi usang |
| **"refresh token sudah pernah dipakai; sesi dicabut"** | Sesi sengaja dicabut karena token dipakai dua kali. Sambungkan ulang connector dari awal |
| **"sambungan ini hanya diberi hak baca"** saat Claude mencoba menulis | Connector-nya tersambung sebelum hak tulis ada. Sambungkan ulang dari pengaturan Claude; hak tulis hanya diminta saat penyambungan, bukan menyusul sendiri |
| Claude bilang perubahan **"belum terdorong"** | Kredensial push di `VAULT_MCP_REPO_URL` tidak berhak tulis atau sudah kedaluwarsa. ⛔ **Deploy key BUKAN yang harus diperiksa**: fiturnya dimatikan di level organisasi `bip-itteam-internal`, jadi jalur push memakai fine-grained PAT di URL https, dan `VAULT_MCP_SSH_DIR` tidak berperan sama sekali. Tulisannya TIDAK hilang: ia tersimpan sebagai commit lokal dan ikut terdorong pada tulisan berikutnya yang berhasil. ⚠️ Gagalnya **senyap dari sisi baca**, karena repo `architecture-draft` publik sehingga `pull` tetap jalan dengan kredensial mati sekalipun. Cek pemiliknya dan kedaluwarsanya lewat `GET https://api.github.com/user` dengan token itu, lalu baca header `github-authentication-token-expiration`; jangan mengandalkan `git push --dry-run`, yang membalas `Everything up-to-date` tanpa pernah menguji izin tulis |
| **"dokumen ini sedang disunting orang lain"** | Ada dev yang menyunting dokumen yang sama dan perubahannya bentrok. Minta Claude membaca ulang dokumennya lalu mengulang. Server sengaja tidak menggabungkan sendiri, karena penggabungan otomatis pada dokumen acuan arsitektur menghasilkan teks yang terbaca wajar tapi isinya campuran dua maksud |

Mencabut sambungan sepenuhnya: hapus connector di sisi Claude, lalu hapus `employee_id`-nya dari daftar-izin.

## Irisan 2 sudah naik: semua connector harus disambung ulang SEKARANG

⚠️ **Berlaku sejak 2026-09-01**, saat tool tulis diaktifkan di prod. Hak tulis diminta **saat penyambungan**, tidak menyusul sendiri. Connector yang sudah tersambung sebelumnya tetap bisa membaca, tetapi setiap percobaan menulis ditolak dengan pesan yang menyuruh menyambung ulang.

Diukur 2026-09-01 di `mcp_sessions`: tiga sesi ada, satu tanpa field scope sama sekali (terbitan irisan 1, fail-closed untuk tulis) dan dua ber-scope `vault:read`. **Nol sesi ber-scope `vault:write`**, jadi sampai penyambungan ulang dilakukan, tool tulis tidak muncul untuk siapa pun meski servicenya sudah mendaftarkannya.

Beri tahu kesembilan orang di daftar-izin. Menemukannya sendiri sebagai penolakan di tengah pekerjaan terbaca sebagai fitur yang rusak, bukan sebagai langkah yang memang perlu dilakukan sekali.

## Dokumen Terkait

- [[Microservices - Vault MCP Service]] — desain, keputusan, dan batasannya
- [[ADR - 0064 Author Commit Tunggal untuk Vault MCP]] — kenapa semua commit memakai satu alamat email
- [[CORE - SSO Flow]] — alur login ERP yang ditumpangi prosedur ini
- [[RUN - Deploy Microservices bip-erp]] — prosedur deploy yang berlaku umum
