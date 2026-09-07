> **Status**: ⚠️ Implemented (ada catatan). Prosedur ini terbukti bisa dituntaskan, dan sejak 2026-09-05 terbukti bisa menghasilkan sesi ber-hak tulis. Yang belum: **belum ada satu pun tulisan yang benar-benar mendarat di vault lewat jalur ini**, dan sebagian besar orang di daftar-izin belum pernah menyambung. Naikkan ke ✅ setelah ada commit ber-author manager di GitHub dan satu jawaban yang jelas bersumber vault. Diukur 2026-09-06; angkanya di § Keadaan adopsi, ukur ulang sebelum dipakai.

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

Dua langkah, dan **keduanya wajib**. Yang pertama membuktikan baca, yang kedua membuktikan tulis, dan sambungan bisa lolos yang pertama sambil gagal yang kedua tanpa satu pun tanda.

**1. Baca.** Tanyakan sesuatu yang jawabannya hanya ada di vault, misalnya *"bagaimana SSO bip-erp bekerja?"*. Berhasil bila Claude **menyebut nama dokumennya** (mis. `CORE - SSO Flow`), bukan sekadar menjawab dari pengetahuan umum.

**2. Tulis.** Minta Claude membuat satu catatan kecil, lalu perhatikan jawabannya:

```
Tulis catatan baru di vault: Workspace/Inbox/<tanggal> Uji sambungan.md
Isinya satu paragraf bahwa ini uji sambungan.
```

⛔ **Daftar tool yang muncul di layar Claude BUKAN bukti hak tulis.** Sambungan ber-hak baca saja tetap menampilkan `Write note` dan `Patch note` di daftar izin, dan penolakannya baru muncul saat tool itu dipanggil. Terjadi 2026-09-01 dan terulang 2026-09-05 pada penyambungan yang sama sekali baru, jadi ini bukan sisa keadaan lama: sambungan baru pun bisa terbit ber-hak baca saja bila Claude memakai metadata yang sudah ia simpan sebelumnya.

Yang membuktikannya cuma tulisan sungguhan. Tiga hasil yang mungkin:

| Yang dijawab Claude | Artinya | Yang dilakukan |
|---|---|---|
| Menyebut `commit` **dan** `pushed: true` | Beres, hak tulis terbit dan tulisannya sampai GitHub | Selesai |
| Menyebut `commit` tapi `pushed: false` | Hak tulis terbit, tapi push ke GitHub gagal | Bukan masalah Anda. Lapor ke IT, lihat baris "belum terdorong" di § Bila gagal |
| **"sambungan ini hanya diberi hak baca"** | Hak tulis tidak terbit | Hapus connector, tambahkan lagi dari awal, lalu ulangi langkah ini |

`Workspace/Inbox/` sengaja dipakai untuk uji ini: area itu dikecualikan dari status marker, template, dan gerbang wikilink, jadi catatan uji tidak memicu peringatan konvensi dan tidak mencemari dokumen arsitektur.

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

## Irisan 2 sudah naik: connector lama harus disambung ulang

⚠️ **Berlaku sejak 2026-09-01**, saat tool tulis diaktifkan di prod. Hak tulis diminta **saat penyambungan**, tidak menyusul sendiri. Connector yang tersambung sebelum tanggal itu tetap bisa membaca, tetapi setiap percobaan menulis ditolak dengan pesan yang menyuruh menyambung ulang.

⛔ **Menyambung ulang belum tentu cukup, dan ini yang paling mudah terlewat.** Penyambungan yang sama sekali baru pun bisa terbit ber-hak baca saja, karena Claude memakai metadata OAuth yang sudah ia simpan sebelumnya. Terbukti 2026-09-05: satu sambungan baru terbit `["vault:read"]` **dua belas menit sesudah** sambungan lain di server yang sama berhasil terbit `["vault:read","vault:write"]`. Jadi penjelasan "connector lama" tidak menutup seluruh kasus ini.

Karena itu § Verifikasi langkah 2 wajib dijalankan tiap kali menyambung, bukan hanya saat curiga.

## Keadaan adopsi

⚠️ **Ini potret bertanggal, bukan fakta.** Ukur ulang sebelum memakainya untuk apa pun.

Diukur **2026-09-06** di `mcp_sessions` prod:

- **4 sesi**, milik **2 orang** dari 9 yang ada di daftar-izin.
- **1 sesi ber-hak tulis.** Sisanya: satu tanpa field scope sama sekali (terbitan irisan 1) dan dua ber-`vault:read`.
- **Nol commit pernah mendarat lewat jalur ini.** Seluruh commit vault ber-email `bharataitteam@gmail.com` bernama author `BIP-ITTeam`, yakni akun tim untuk commit manual, dan yang terakhir bertanggal 2026-08-31, sehari sebelum tool tulis aktif.
- **Nol baris log permintaan** dalam 16 jam sejak container terakhir dibuat. Service ini menganggur.

Sesi seorang pemakai **menumpuk dan tidak dibersihkan**: sesi lama tetap hidup sampai `refresh_kedaluwarsa`-nya (30 hari) walau ia sudah menyambung ulang. Sesi terbitan irisan 1 yang tanpa field scope tetap bisa **membaca seluruh vault** selama masa itu, karena `BolehBaca` sengaja fail-open untuk scope kosong.

### Yang penting: audiensnya 3 orang, bukan 9

Dari 9 `employee_id` di daftar-izin per 2026-09-06, **6 di antaranya Tech Development** dan **3 di Kesekretariatan** (Direktur, Internal Audit, Corporate Secretary).

Service ini ada untuk menghapus perantara dev, jadi bagi dev ia nyaris tak menambah apa-apa: mereka sudah punya vault di Obsidian dan git. **Yang menentukan berhasil atau tidaknya adalah 3 orang Kesekretariatan itu.** Menghitung adopsi dari 9 membuat angkanya terlihat lebih buruk sekaligus salah sasaran, dan upaya onboarding yang disebar rata ke sembilan orang menghabiskan tenaga di enam orang yang tidak akan memakainya.

### Cara mengukur ulang

Dari server prod:

```
cd ~/apps/bip-erp
U=$(grep -E "^MONGO_ROOT_USER=" .env | cut -d= -f2)
P=$(grep -E "^MONGO_ROOT_PASSWORD=" .env | cut -d= -f2)
docker exec Vault-MCP-MongoDB mongosh --quiet -u "$U" -p "$P" \
  --authenticationDatabase admin vault_mcp_db --eval '
  db.mcp_sessions.find().forEach(function(d){
    print((d.identitas ? d.identitas.employee_id : "?") +
      " | scope=" + (d.scope === undefined ? "TIDAK ADA FIELD" : JSON.stringify(d.scope)) +
      " | dibuat=" + d.dibuat)
  })'
```

Bandingkan dengan `VAULT_MCP_ALLOWED_EMPLOYEES` di `.env` untuk tahu siapa yang belum menyambung. Nama container-nya **`Vault-MCP`** dan **`Vault-MCP-MongoDB`**, berhuruf besar; filter `docker ps` bersifat case-sensitive dan `--filter name=vault-mcp` akan mengembalikan kosong, yang terbaca seperti servicenya mati.

⛔ **`docker ps` hijau dan boot log berbunyi `tool tulis aktif` tidak membuktikan apa pun soal pemakaian.** Keduanya benar sepanjang 2026-09-01 sampai 2026-09-06 sementara nol tulisan terjadi.

## Dokumen Terkait

- [[Microservices - Vault MCP Service]] — desain, keputusan, dan batasannya
- [[ADR - 0064 Author Commit Tunggal untuk Vault MCP]] — kenapa semua commit memakai satu alamat email
- [[CORE - SSO Flow]] — alur login ERP yang ditumpangi prosedur ini
- [[RUN - Deploy Microservices bip-erp]] — prosedur deploy yang berlaku umum
