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
| **"data vault basi"** saat bertanya | `git pull` ke repo vault gagal berturut-turut. Periksa deploy key. Ini disengaja: lebih baik gagal daripada menjawab dari dokumentasi usang |
| **"refresh token sudah pernah dipakai; sesi dicabut"** | Sesi sengaja dicabut karena token dipakai dua kali. Sambungkan ulang connector dari awal |

Mencabut sambungan sepenuhnya: hapus connector di sisi Claude, lalu hapus `employee_id`-nya dari daftar-izin.

## Dokumen Terkait

- [[Microservices - Vault MCP Service]] — desain, keputusan, dan batasannya
- [[CORE - SSO Flow]] — alur login ERP yang ditumpangi prosedur ini
- [[RUN - Deploy Microservices bip-erp]] — prosedur deploy yang berlaku umum
