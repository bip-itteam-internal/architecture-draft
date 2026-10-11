# HRIS - Rencana Kerja Harian (Modul)

## Deskripsi

*Karyawan mencatat pekerjaan hariannya sendiri di MyBharata. Catatan itu bergabung dengan tiket yang ditugaskan kepadanya menjadi satu daftar "hari ini". Item yang belum selesai terbawa ke hari berikutnya dengan hitungan tertunda, dan atasan efektifnya dapat melihat daftar itu untuk menegur, membantu, atau membagi ulang pekerjaan. Datanya disimpan di [[Microservices - Task Management Service]], terpisah dari tiket.*

- **Status**: 🟡 Konsep, kode belum ada. Keputusan [[ADR - 0170 Rencana Kerja Harian di Task Management dengan Pantauan Atasan Efektif]] masih 🟡 Diusulkan.
- **Implementasi**: [[Microservices - Task Management Service]] (bagian *Modul Rencana Kerja Harian*) · atasan efektif dari [[Microservices - Employee Service]]
- **Layar**: [[APP - MyBharata]]: tab **Hari Ini** di menu Tugas saja, tidak tampil di Beranda. [[APP - Web ERP]]: tab **Hari Ini** dan **Rencana Tim** di Task Management › Daftar Tugas.
- **Blueprint**: [[ANALISA - Rencana Kerja Harian]]

## Latar Belakang

- Atasan baru tahu pekerjaan bawahan macet setelah terlambat. Pekerjaan harian yang tidak berbentuk tiket tidak tercatat di sistem mana pun.
- SOP banyak posisi sudah mewajibkan laporan harian (Admin dan Leader Warehouse Packing, PPIC, Operator Produksi, Security, Host Live, Buzzer), tetapi lewat Excel, Google Sheet, formulir, atau kiriman langsung ke supervisor. Hasilnya tidak terkumpul.
- Task Management tidak cocok untuk catatan pribadi: setiap tiket lahir sebagai `Request`, punya SLA respons 24 jam, dan memberi notifikasi ke supervisor space. Dari 155 tiket yang pernah dibuat untuk diri sendiri di prod, seluruhnya backlog Tech Development dan nol dalam 30 hari terakhir (ukur 2026-10-11).

## Ruang Lingkup / Cakupan (business view)

**Cara kerja**

1. **Membuat.** Buka menu Tugas, tab Hari Ini, ketuk tombol tambah, ketik judul, simpan. Tanggal rencana otomatis hari ini dan bisa diganti ke hari lain. Tanpa prioritas, triase, atau persetujuan.
2. **Daftar hari ini.** Rencana kerja terbuka yang tanggal rencananya hari ini atau sudah lewat, rencana kerja yang diselesaikan hari ini, dan tiket yang ditugaskan ke saya yang jatuh tempo hari ini atau sudah lewat (plus tiket yang selesai hari ini). **Tiket tidak punya ceklis**: ia tampil dengan nama status aslinya (Todo, On Going, Testing "menunggu tinjauan", atau stage lain milik space-nya) dan tenggatnya, dan mengetuknya membuka halaman tiket untuk mengubah status lewat alur tiket biasa.
3. **Tertunda.** Item yang belum selesai otomatis tetap muncul di hari berikutnya dengan label "tertunda N hari", dihitung dari **tanggal rencana awal** dalam hari kalender (WIB). Mengganti tanggal rencana ke depan tidak menghapus hitungan ini, karena tanggal awal tak pernah berubah.
4. **Menyelesaikan atau membatalkan.** Centang selesai, atau batalkan. Membatalkan **tidak menghapus**: item tetap tersimpan dan terlihat oleh atasan.
5. **Bukti (pondasi).** Pemilik bisa melampirkan foto atau berkas pada item. Di tahap 1 bukti opsional. Mewajibkan bukti menyusul.
6. **Pantauan atasan.** Atasan efektif membuka ringkasan bawahannya: rencana kerja terbuka hari ini, yang tertunda tiga hari atau lebih, dan yang dibatalkan tujuh hari terakhir. Dari situ ia membuka daftar hari ini seorang bawahan. Atasan hanya membaca.

**Atasan efektif** = atasan langsung (HRIS › Personalia › Atasan Langsung). Bila kosong, supervisor departemennya, dengan aturan yang sama seperti penerima pengingat kontrak (General Affair lewat HR). Supervisor departemen tanpa atasan: rencana kerjanya hanya terlihat oleh dirinya sendiri.

**Di luar cakupan tahap 1**: KPI dan penilaian kinerja, pengingat atau notifikasi, kewajiban bukti, feed kalender, dan penggantian otomatis laporan Excel milik SOP.

## Persona / Pengguna

Angka diukur di prod 2026-10-11 (baca saja). Bagian bertanda *(asumsi)* belum terbukti.

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Staf operasional ber-SOP laporan harian | Admin/Leader Warehouse Packing, PPIC, Operator Produksi, Security | Pemilik rencana kerja sendiri | MyBharata |
| Tim marketing | Host Live, Buzzer, Account Specialist di Beautyhacks (45 orang, 40 ber-atasan langsung) dan Kyura (30, 16 ber-atasan langsung) | Pemilik rencana kerja sendiri | MyBharata |
| Staf kantor | Finance (16), Percetakan (13), Quality (6), Procurement (3); nol ber-atasan langsung | Pemilik rencana kerja sendiri | Web ERP (sehari-hari di depan komputer *(asumsi)*) dan MyBharata |
| Penerima tiket | 14 orang yang memegang tiket aktif, kebanyakan Tech Development dan GA | Pemilik rencana kerja + tiket `assign_to` | MyBharata |
| Atasan langsung | 8 orang ber-bawahan langsung (22, 15, 12, 12, 11, 6, 4, 2 bawahan) | Baca rencana kerja bawahan efektif | MyBharata |
| Supervisor departemen (fallback) | 11 orang `is_supervisor`; mewarisi 97 karyawan tanpa atasan langsung | Baca rencana kerja bawahan efektif | MyBharata |
| HR | Pemilik data atasan langsung | Mengisi `supervisor_id` di HRIS | Web ERP |

- **Tujuan pemilik**: tidak ada pekerjaan yang terlupa, dan tidak perlu menyusun laporan harian terpisah *(asumsi: bila pemilik SOP menerimanya)*.
- **Tujuan atasan**: dalam satu layar tahu siapa yang macet hari ini, lalu menegur, membantu, atau membagi ulang.
- **Pain point**: laporan harian tersebar di Excel dan chat; keterlambatan baru terlihat ketika sudah berdampak.
- **Aksi utama**: tambah item, centang selesai, ganti tanggal, lampirkan bukti; atasan membuka ringkasan lalu rincian per orang.

⚠️ Beban pantauan tidak merata: supervisor Manufaktur praktis memantau sekitar 32 orang karena hanya 1 dari 33 karyawan Manufaktur yang ber-atasan langsung. Obatnya melengkapi atasan langsung di HRIS.

## Konsumen Data

- [[APP - MyBharata]]: daftar hari ini pemilik dan tampilan bawahan untuk atasan.
- KPI: **belum**. Bila kelak dipakai, lewat sumber KPI terdaftar di [[Microservices - Employee Service]] dengan ADR terpisah.

## Kendala

- Atasan langsung baru terisi 84 dari 181 karyawan aktif (46%). Tanpa fallback ke supervisor departemen, separuh perusahaan tidak terlihat siapa pun.
- "Tertunda" memakai hari kalender, jadi akhir pekan menambah angka untuk karyawan yang tidak bekerja di hari itu.
- Isi rencana kerja bisa memuat hal pribadi dan terlihat oleh atasan. Ini perlu disampaikan ke karyawan saat rilis.

## Belum Diputuskan (TBD)

- Siapa boleh mewajibkan bukti, dan apakah item wajib bukti ditolak saat diselesaikan tanpa bukti.
- Metrik KPI (bila ada) dan bobotnya, sesudah ada data satu sampai dua bulan.
- Pilot terbatas (misalnya marketing) atau langsung semua karyawan. Asumsi ADR: semua karyawan.
- Pengingat pagi atau notifikasi tertunda.

## Dokumen Terkait

- [[ADR - 0170 Rencana Kerja Harian di Task Management dengan Pantauan Atasan Efektif]] · [[ANALISA - Rencana Kerja Harian]]
- [[Microservices - Task Management Service]] · [[HRIS - Organization Structure]] · [[APP - MyBharata]]
- [[HRIS - Matriks KPI per Departemen]] (metrik "kelengkapan laporan harian" Buzzer yang masih manual)
