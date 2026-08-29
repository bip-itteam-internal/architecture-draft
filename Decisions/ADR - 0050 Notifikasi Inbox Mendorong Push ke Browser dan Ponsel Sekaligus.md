## Deskripsi

*Setiap dokumen inbox yang tersimpan mendorong push ke dua kanal sekaligus, browser dan ponsel, tanpa penyaringan kategori. Mencabut keputusan 2026-08-20 yang membuat daftar-izin push browser lebih pendek dari daftar kategori inbox. Mengubah apa yang sampai ke perangkat orang, karena itu ditulis sebagai ADR.*

- **Status**: ⚠️ **Implemented (ada catatan)** — sudah **merge ke `main`**, diverifikasi 27 Agustus 2026: `PushWebCategories` dan `IsPushWebCategory` tak lagi ada di `shared-library/models/notification/models.go`, dan `IsInboxCategoryValid` berdiri sendiri sebagai satu-satunya daftar-izin. **Keadaan deploy tidak diverifikasi** pada pemeriksaan itu; urutan deploy yang mengikat di bawah tetap berlaku.
- **Ruang lingkup**: `POST /inbox/send` di [[Microservices - Notification Service]], plus pencabutan panggilan `/fcm/send-*` langsung di [[Microservices - Attendance Service]], [[Microservices - Task Management Service]], dan [[Microservices - Employee Service]]. Tidak menyentuh pengiriman yang memang bukan notifikasi inbox.
- **Menggantikan**: keputusan `PushWebCategories` 2026-08-20 yang tercatat di [[Microservices - Notification Service]].

## Context

Push web menyala di produksi **2026-08-21 pukul 21.13 WIB**. Sampai penyelidikan **2026-08-22**, tak satu pun notifikasi desktop pernah muncul, dan seluruh infrastrukturnya ternyata sehat: bundel frontend memuat konfigurasi Firebase proyek `hris-my-bharata` berikut VAPID key, service account backend memakai proyek yang sama, `WEB_APP_URL` terisi, dan biner notification-service memuat kode push web.

Yang tidak ada hanyalah **kesempatan**. Hanya 3 dari 209 akun yang punya token browser, dan sejak push web hidup, ketiganya cuma menerima kategori `reminder` dan `guestbook` — dua kategori yang justru dikecualikan dari daftar-izin. Nol baris log `[PushWeb]` karena itu konsisten, bukan gejala kerusakan.

Penyelidikan yang sama membuka dua cacat struktural yang lebih besar.

**Pertama, fan-out ponsel tersebar di pengirim.** Push ponsel hanya terjadi bila service pengirim memanggil `/fcm/send-*` secara eksplisit. Dari 9 pemanggil `/inbox/send`, hanya dua yang melakukannya. Akibat konkretnya: **Surat Peringatan tidak pernah membuat ponsel berdering**, padahal ia menyangkut hak karyawan. Ini kelas bug "pengirim yang lupa" yang sudah dua kali menggigit lewat kategori inbox (`form-published` 2026-08-02, `kaizen-*` 2026-08-06).

**Kedua, kebijakan kanalnya asimetris dan tak bisa dijelaskan ke pemakai.** Notifikasi task management berdering di ponsel tapi diam di desktop; Surat Peringatan sebaliknya.

Keputusan lama beralasan bahwa desktop yang berisik membuat orang memblokir izin notifikasi secara **permanen**, karena browser tak menyediakan cara meminta ulang dari dalam aplikasi. Kekhawatiran itu sah dan mode gagalnya nyata. Yang tidak pernah dilakukan adalah **mengukurnya**.

Diukur langsung ke `notification_db` produksi **2026-08-22**, 30 hari terakhir (3.968 dokumen, sekitar 132 per hari se-organisasi):

| Yang diukur | Angka |
|---|---|
| Penerima tersibuk se-perusahaan, sekarang | 4,2 notifikasi desktop/hari |
| Penerima tersibuk se-perusahaan, bila parity | **7,4/hari** |
| Mayoritas 12 penerima tersibuk, bila parity | 3 sampai 4/hari |
| Hari terpadat satu orang (2026-07-29) | 34 notifikasi |
| Akun punya token browser | **3 dari 209** |

Puncaknya sekitar satu notifikasi per jam kerja untuk satu orang tersibuk di seluruh perusahaan. Kekhawatiran lama sepadan untuk volume yang ternyata tidak ada.

## Decision

**1. Setiap dokumen inbox mendorong push ke dua kanal, tanpa daftar-izin kategori.** `PushWebCategories` dan `IsPushWebCategory` dihapus dari `shared-library`. Aturannya jadi satu kalimat: kalau sesuatu layak masuk inbox, ia layak berdering di mana pun orangnya sedang berada.

`IsInboxCategoryValid` **tetap ada** dan menjadi satu-satunya daftar-izin kategori yang tersisa. Ia menjaga hal yang berbeda: kategori salah-ketik tetap harus ditolak 400 supaya tidak lolos jadi notifikasi tanpa ikon di [[APP - MyBharata]].

**2. Fan-out dipusatkan di `/inbox/send`.** Panggilan `/fcm/send-*` langsung dicabut dari tiap pengirim yang sudah menulis inbox. Nol service yang perlu disentuh saat pengirim baru lahir, dan kelas bug "pengirim yang lupa" tertutup untuk kedua kanal sekaligus.

**3. Endpoint `/fcm/send-personal`, `/fcm/send-department`, dan `/fcm/send-broadcast` tetap hidup.** Ada pengiriman yang memang bukan notifikasi inbox dan tidak boleh dipaksa lewat jalur ini: pengingat presensi dari cron attendance, yang mengirim FCM langsung tanpa menulis inbox sama sekali.

**4. Payload ponsel dibiarkan persis seperti sebelumnya** — title dan body saja, `data` kosong, priority normal. Mengisinya dari `app_route` yang sudah tersedia di dokumen inbox menggoda, tapi itu mengubah apa yang diterima MyBharata dan menyeret repo mobile ikut diuji. Dikunci test supaya perubahannya kelak disengaja.

**5. Lonjakan diterima sebagai risiko yang diketahui.** Hari seperti 2026-07-29 akan ikut jadi popup desktop. Bila gejalanya muncul — jumlah token browser aktif menurun sesudah hari lonjakan — penanganannya adalah **peredaman burst**, bukan menghidupkan kembali daftar-izin kategori. Yang menyakitkan adalah harinya, bukan kategorinya.

## Consequences

**Yang berubah, dan diterima sadar:**

- **Tujuh staf HR mulai menerima tujuh jenis notifikasi yang belum pernah mereka terima**, sekaligus di inbox, ponsel, dan desktop. Ini bukan efek samping melainkan perbaikan bug, dijelaskan di bawah. Disepakati bahwa HR **diberi tahu sebelum deploy**.
- **Surat Peringatan akhirnya membuat ponsel berdering.** Inilah cacat yang memicu seluruh pekerjaan ini.
- **Notifikasi task management kini juga muncul di desktop**, termasuk `task-commented` dan `task-status-updated` yang sebelumnya sengaja dikecualikan.
- **Urutan deploy jadi mengikat.** `task-management`, `attendance`, dan `employee` wajib naik **sebelum** `notification-service`. Terbalik berarti jendela dobel-kirim ke seluruh perusahaan; urutan yang benar hanya menghasilkan jeda sunyi beberapa menit yang pulih sendiri. Prosedur: [[RUN - Deploy Microservices bip-erp]].

**Bug yang ikut terbongkar saat mengerjakan ini:**

- ⛔ **Perulangan inbox per-departemen tidak pernah berjalan sekali pun.** Nama departemen disambung mentah ke URL, dan `Human Resource` mengandung spasi sehingga baris permintaan HTTP terpotong dan server membalas 400. Pemanggilnya mengabaikan status, jadi kegagalannya tak meninggalkan jejak. Dibuktikan di produksi: dari 6.383 dokumen inbox sepanjang masa, enam dari tujuh judul notifikasi departemen HR berjumlah **nol**, sementara judul jalur personal berjumlah 726. Urutan perbaikannya mengikat — escape dulu, baru `/fcm/send-department` boleh dicabut, sebab sebelum itu FCM departemen adalah satu-satunya yang sampai.
- **`cronReminderKPI` mengirim broadcast FCM dan satu inbox per karyawan.** Setelah pemusatan, itu berarti seluruh karyawan menerima pengingat KPI bulanan dua kali di ponsel. Broadcast-nya dicabut.
- **`mongodb.GetCollection` memanik saat DB nil** di jalur `/inbox/send`, dan panik itu tak terlihat sebagai panik: fasthttp memutus koneksi, gateway membalas 502 tanpa petunjuk. Kini dijaga dan membalas 503 berikut log. Ditemukan oleh test handler, bukan oleh pembacaan kode.

**Yang tidak berubah:**

- Pengingat presensi dari cron attendance tetap mengirim FCM langsung tanpa menulis inbox, jadi ia tak terpengaruh sama sekali.
- Penyaringan perusahaan pada pencarian token **personal** tetap sengaja tidak ada. `/inbox/send` dipanggil pakai service key tanpa identitas karyawan, sehingga menyertakan `company_id` justru menghapus penerima yang sah. `employee_id` sudah menunjuk satu orang.

**Risiko yang dijaga kode, bukan oleh kebiasaan:**

- Kegagalan satu kanal tidak menghentikan kanal lain, dan satu token mati tidak membatalkan token lain milik orang yang sama. Keduanya dikunci test.
- Pencarian token **per-departemen** kini menyertakan `company_id`, sesuai [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]. Dipasang **sebelum** perulangannya hidup, bukan sesudah: hari ini seluruh 7 staf HR ada di BIP sehingga ia belum melindungi siapa pun, dan justru itu alasan memasangnya sekarang.
- ⚠️ Penyaring itu **inert di jalur tukar jadwal**: dokumen `shift_exchange_request` tidak punya field `company_id` sama sekali, sehingga nilainya kosong dan filternya dilewati. Turun kelasnya aman dan tercatat log, bukan senyap. Akarnya di jalur pembuatan pengajuan, di luar lingkup ADR ini.

## Dokumen Terkait

- [[Microservices - Notification Service]]
- [[Microservices - Employee Service]]
- [[Microservices - Attendance Service]]
- [[Microservices - Task Management Service]]
- [[APP - MyBharata]]
- [[APP - Web ERP]]
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]
- [[RUN - Deploy Microservices bip-erp]]
