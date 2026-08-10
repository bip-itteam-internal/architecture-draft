---
name: deploy-bip-erp
description: Gunakan saat men-deploy service bip-erp ke dev atau prod, saat memverifikasi apakah sebuah merge sudah benar-benar mendarat, atau saat gejala aneh muncul setelah deploy (502, notifikasi tak tiba, menu hilang, fitur tak bereaksi). Menentukan container mana saja yang harus naik, urutannya, dan gerbang verifikasi yang membuktikan fiturnya jalan.
---

# Deploy bip-erp

**Ini lapisan keputusan, bukan prosedur.** Prosedur, perintah, dan troubleshooting-nya ada di
**[[RUN - Deploy Microservices bip-erp]]** di vault. Baca runbook itu **sekarang**, jangan
bekerja dari ingatan. Bila skill ini dan runbook berbeda, **runbook yang menang** dan skill
ini yang salah.

Yang dikerjakan skill ini adalah tiga hal yang selama ini ada di kepala orang dan sering
terlewat: **container mana saja yang harus naik**, **urutannya**, dan **bukti apa yang
membuktikan deploy-nya berhasil**.

---

## 1. Tentukan lingkungannya dulu

| | DEV | PROD |
|---|---|---|
| Cara deploy | Pipeline jalan sendiri setelah merge ke `main` | **Selalu manual.** Merge ke `main` tidak menyentuh prod sama sekali |
| Boleh dipercaya? | **Tidak.** Lihat §5 | Kamu yang menjalankan, jadi kamu tahu |

**Jangan pernah mengatakan "sudah ter-deploy" hanya karena PR-nya merged.** Untuk prod itu
salah begitu saja. Untuk dev itu belum tentu benar.

---

## 2. Tentukan daftar container

Mulai dari service yang berubah, lalu tambahkan yang tertarik ikut. Ini bagian yang paling
sering meleset, dan gagalnya hampir selalu **senyap**.

**Selalu tambahkan bila:**

- **Kategori inbox baru** → `notification-service` **wajib** ikut naik bersama service
  pengirimnya. `notification.InboxCategories` adalah daftar-izin yang terkompilasi ke dalam
  biner tiap service; yang tak di-rebuild memegang salinan lama dan menolak `400`, sementara
  pengiriman bersifat best-effort yang hanya nge-log. Sudah menggigit dua kali. Rinciannya
  di runbook §3a.
- **`shared-library/` berubah** → **setiap service yang membaca bagian yang berubah** harus
  ikut naik, bukan cuma yang kamu sunting. Ini kopling lewat biner, bukan lewat API, jadi
  tak ada yang mengingatkanmu.
- **Klaim JWT atau `common.PayloadJWT` berubah** → `api-gateway` ikut. Gateway mem-parse
  balasan lalu menandatangani ulang token; gateway basi akan **membuang klaim yang tak
  dikenalnya** tanpa pesan apa pun. Peringatan: gateway memanggil `ValidateInternalURL`
  untuk seluruh `InternalURL` saat start, jadi bila ada `*_MODULE_URL` yang kosong ia akan
  restart-loop dan tak bisa dibangun ulang sama sekali. Periksa env-nya lengkap **sebelum**
  menyentuh gateway.
- **Env baru ditambahkan** → container yang membacanya harus **dibuat ulang**, bukan
  di-restart. Env dibaca saat container DIBUAT.
- **Kontrak API berubah** → **BE dulu, FE belakangan**. FE punya fallback aman bila field
  baru belum ada; sebaliknya tidak.

**Urutan bila dua service saling memanggil:** penyedia API naik lebih dulu, konsumennya
menyusul.

Sebelum lanjut, **sebutkan daftar container final beserta alasannya** ke user. Kalau
daftarnya cuma satu padahal salah satu kondisi di atas terpenuhi, kamu melewatkan sesuatu.

---

## 3. Sebelum menjalankan

- **Cek apakah pipeline sedang membangun.** Dua `docker compose build` paralel di project
  compose yang sama berebut tag image, dan `up -d` milik pipeline di tengah build kamu
  membuat container jalan dengan image yang bukan hasil build terakhir. `docker ps` tidak
  menunjukkan apa pun soal ini.
- **Cek sisa disk di dev.** Build cache gampang menumpuk sampai puluhan GB dan membuat build
  gagal di tengah. Membersihkannya makan waktu dan memperlambat pipeline yang sedang jalan,
  jadi jangan dilakukan sambil menunggu deploy.
- **Perhatikan `--no-deps`.** Wajib di jam rawan supaya blast radius tinggal container
  targetnya, **tapi jangan dipakai bila dependensinya sedang mati** karena ia melewati
  health-gating. Alasan lengkapnya di runbook §2.

---

## 4. Gerbang verifikasi

**`docker ps` sehat dan `/health` hijau BUKAN bukti.** Keduanya hijau sepanjang seluruh
kejadian yang melahirkan runbook ini.

Wajib, berurutan:

1. **Buktikan binernya memuat kode baru**, bukan sekadar repo servernya benar. Cari string
   unik dari perubahan kamu di dalam biner yang sedang jalan. Nol berarti container masih
   memegang build lama meski `git log` di server sudah benar.
2. **Picu fiturnya sungguhan lewat gateway**, bukan lewat unit test dan bukan lewat panggilan
   langsung ke port service. Gateway membuang prefix `/api/<module>`, jadi hanya jalur ini
   yang membuktikan rutenya benar.
3. **Untuk notifikasi: kirim satu yang sungguhan dan pastikan ia muncul di kotak masuk
   penerimanya.** Ini satu-satunya cara membedakan "sudah naik" dari "belum".
4. **Angka nol diperlakukan sebagai pertanyaan.** Fitur live tapi 0 dokumen, 0 notifikasi,
   daftar kosong: itu indikasi rantai yang putus, bukan kabar baik.

Baru setelah keempatnya lewat, katakan deploy-nya berhasil.

---

## 5. Kalau gejalanya aneh, curigai biner basi lebih dulu

Sebelum menuduh logika RBAC, gerbang, atau kode siapa pun: **pastikan biner yang berjalan
memang memuat logika itu.** Membaca kode di repo tidak cukup untuk menyimpulkan perilaku
sebuah lingkungan.

Ini sudah memakan berjam-jam pelacakan ke arah yang keliru, karena gejalanya menunjuk ke
tempat yang salah: menu tetap hilang meski paket sudah dipasang dan sudah login ulang
berkali-kali, dan tuduhan pertama jatuh ke logika RBAC padahal masalahnya gateway memegang
image lama. Bandingkan umur image dengan tanggal commit yang menambah field yang sedang
dicari. Runbook §3a memuat perintahnya.

Jebakan lain yang sudah terbukti:

- **Merge tidak selalu berarti terbangun.** Pipeline yang mendeteksi perubahan dari commit
  terakhir saja bisa melewatkan sebuah service ketika PR lain menyusul beberapa menit
  kemudian.
- **Service yang baru pertama kali ada** bisa tidak dikenali pipeline. Jangan menunggu;
  bangun manual lalu verifikasi.
- **Nomor PR bukan urutan merge.** Jangan menyimpulkan server tertinggal dari nomor PR;
  bandingkan commit.
- **Balasan gateway dev membedakan tiga hal**: service tak dikenal, service dikenal tapi tak
  terjangkau, dan rute ada tapi path-nya salah di service. Ketiganya bukan hal yang sama;
  runbook §5 memetakan gejala ke akarnya.
- **Service bisa ada di compose produksi tapi tidak di compose dev**, sementara
  `*_MODULE_URL`-nya tetap terpasang di gateway dev. URL-nya ada, container-nya tidak, dan
  panggilannya mati di resolusi DNS. Perbaikannya menambah service ke compose dev, bukan
  mengubah kode.

---

## 6. Jangan

- **Jangan menyalin isi runbook ke sini atau ke tempat lain.** Vault adalah sumber
  kebenarannya; salinan kedua akan menyimpang tanpa ada yang sadar.
- **Jangan menyentuh prod tanpa diminta eksplisit.** Host, user, app dir, dan kunci SSH prod
  ada di dok IT vault, dan tiap orang memakai kuncinya sendiri.
- **Jangan menyalakan feature flag yang dorman** hanya karena kamu men-deploy service-nya.
  Beberapa flag memicu aksi nyata dan tak bisa dibatalkan ke pihak luar. Runbook §3b
  menyebut yang mana.
- **Jangan `git reset --hard` di server** untuk memperbaiki service yang terlewat. Repo-nya
  biasanya sudah di commit yang benar; yang perlu cuma rebuild satu service itu.
- **Jangan menganggap perbaikan selesai sampai gerbang §4 lewat.** Deploy yang tidak
  diverifikasi secara fungsional sama saja dengan belum deploy.
