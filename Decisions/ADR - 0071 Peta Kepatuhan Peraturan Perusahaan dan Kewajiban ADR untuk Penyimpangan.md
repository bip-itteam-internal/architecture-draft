## Untuk Manajemen

- **Yang berubah di layar**: tidak ada. Ini keputusan tentang cara mencatat aturan mana yang benar-benar dijalankan sistem, dan tak seorang pun melihatnya dari aplikasi.
- **Siapa terdampak**: HRD dan IT yang selama ini harus membaca kode untuk menjawab "sistem sebenarnya memotong berapa", dan siapa pun yang kelak menghadapi karyawan bertanya kenapa potongannya segitu.
- **Tidak dijanjikan**: peta ini **tidak** membuat sistem otomatis patuh, dan **tidak** memeriksa dirinya sendiri. Bila aturan berubah dan tak ada yang memperbarui petanya, ia akan menyimpang persis seperti dokumentasi mana pun. Ia juga tidak menjawab pertanyaan tentang orang tertentu; ia tentang aturan, bukan kasus.
- **Besaran kerja**: kecil. Tidak ada kode, tidak ada deploy, tidak ada perubahan di aplikasi. Yang dikerjakan adalah menuliskan yang sudah berjalan lalu menandai selisihnya.

## Deskripsi

*Kepatuhan sistem terhadap Peraturan Perusahaan 2026-2028 dipetakan di SATU dokumen vault yang menyandingkan tiap pasal dengan aturan yang benar-benar dijalankan, tempat nilainya tinggal, dan nilai terukur di produksi. Peta itu bukan sumber kebenaran aturan, melainkan catatan selisih; dan tiap penyimpangan yang diputuskan sadar wajib punya ADR sendiri, tidak boleh berhenti sebagai peringatan di dalam dokumen.*

- **Status**: 🟡 **Diusulkan**, 2026-09-01. Belum ada dokumen maupun ADR turunannya.
- **Path di repo**: tidak menyentuh repo kode sama sekali. Artefaknya `architecture-draft/Human Resource Information System/HRIS - Kepatuhan Peraturan Perusahaan.md` (baru) dan `architecture-draft/Workspace/ANALISA - Kepatuhan Peraturan Perusahaan.md` (baru).
- **Tanggal**: 2026-09-01

## Context

Kebutuhan yang memicu ini datang sebagai solusi: "buat MCP untuk backend supaya manajemen bisa tahu logika yang dijalankan". Wawancara menyempitkannya jadi pertanyaan yang berbeda: **apakah yang dijalankan sistem sama dengan Peraturan Perusahaan, dan di mana ia menyimpang.** Alat baca tidak menjawab itu, dan buktinya ada di bawah.

**Aturannya sendiri tidak tinggal di vault.** Sumber kebenarannya `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`, turunan teknis Peraturan Perusahaan PT Bharata Internasional Pharmaceutical 2026-2028, berukuran 6,4 KB dan terakhir disunting 2026-05-26. Dokumen itu dinyatakan **menang atas perilaku sistem**, tetapi tinggal di repo mobile sementara yang mengerjakan payroll bekerja di `bip-erp` dan `erp-frontend`. Sembilan dokumen vault sudah menautkannya, dan tiga di antaranya memakai kalimat yang hampir sama: aturannya tidak ada di vault ini.

**Sebagian aturan sudah menetes ke vault, tetapi tersebar.** Tarif potongan ada di [[HRIS - Payroll]] dan [[Microservices - Payroll Service]], ambang keterlambatan di [[HRIS - Attendance System]], sanksi di [[HRIS - Disciplinary (Surat Peringatan)]]. Tidak ada satu tempat pun yang menjawab pertanyaan utuh "sistem patuh atau tidak". ⚠️ Dokumen yang namanya paling menjanjikan justru kosong: [[HRIS - Compensation & Benefits]] berstatus 🟡 Konsep dan **tidak memuat satu angka aturan pun**, jadi keputusan ini sebagiannya berdiri di atas dokumentasi yang belum mencerminkan kenyataan.

**Sebagian besar aturan hidup sebagai komentar kode.** Pemindaian `bip-erp/services` menemukan **638 komentar beranotasi** aturan, rumus, ambang, atau larangan tersebar di **347 berkas** Go. Komentar-komentar itu berkualitas tinggi dan sudah berfungsi sebagai spesifikasi, tetapi tak seorang pun di luar developer akan membacanya.

**Yang menentukan rupiah justru tidak terlihat di kode mana pun.** Enam angka potongan kehadiran adalah config (`payroll_config.attendance_deduction`), disunting HR dari layar. Default di kode sudah benar: `AlphaMultiplierOneDay: 1.5, // Peraturan Perusahaan Pasal 20` (`bip-erp/services/payroll/models_config.go:264`). Produksi menyetelnya **2**, disunting orang bernama pada 2026-08-21 09:54 WIB. Dampaknya terukur: 8 baris draft ber-mangkir tepat satu hari dipotong Rp 565.065, sedangkan pada 1,5x seharusnya Rp 423.799, jadi **kelebihan potong Rp 141.266**.

**Penyimpangan itu sudah ditemukan, diukur, dan ditulis lengkap sejak 2026-08-26**, berikut instruksi apa yang harus dilakukan, di `Microservices - Payroll Service.md:123-135` dan `HRIS - Payroll.md:35-40`. Enam hari kemudian nilainya masih 2 di produksi dan belum ada ADR. **Yang gagal bukan penemuannya, melainkan penutupan loopnya.** Itu sebabnya keputusan ini bukan tentang alat baca.

**Tidak ada satu pun ADR yang mengikat aturan uang dan sanksi.** Diverifikasi dengan `git grep` atas `Decisions/`, bukan hanya `Grep`: dari **73 ADR**, hanya tiga yang menyinggung kata sanksi, mangkir, potongan, atau lembur, dan ketiganya memutuskan hal lain (notifikasi push, siaran serentak, impor payroll). Padahal dua penyimpangan sadar sudah dua kali diminta diangkat jadi ADR di dokumennya sendiri.

**Kelasnya sudah menggigit.** Potongan mangkir pernah dirancang dan diimplementasikan penuh sebesar **1x**, setengah dari yang diatur Pasal 20, melewati brainstorming, `/plan`, dan `/implement` tanpa satu gerbang pun menyadarinya, dan baru tertangkap di `/review`.

## Decision

### 1. Satu dokumen peta kepatuhan, bukan tersebar

[[HRIS - Kepatuhan Peraturan Perusahaan]] menyandingkan, per aturan: **pasal** → **apa yang diatur** → **apa yang dijalankan sistem** → **di mana nilainya tinggal** (konstanta Go, config, atau master data) → **nilai terukur di produksi beserta tanggal pengukurannya** → **status**: cocok, menyimpang, atau belum diimplementasikan.

Dokumen tersebar tidak bisa menjawab "patuh atau tidak" karena tidak ada tempat untuk menaruh jawabannya. Peta ini adalah tempat itu.

### 2. Peta BUKAN sumber kebenaran aturan

Sumber kebenaran tetap `BUSINESS_LOGIC_IMPLEMENTATION.md`, dan bila keduanya bertentangan, dokumen itu yang menang. Peta ini hanya mencatat selisih.

Ini bukan formalitas. Menjadikan peta sebagai sumber kebenaran kedua akan melahirkan persis kelas kerusakan yang paling mahal di repo ini, yaitu satu fakta hidup di dua tempat lalu menyimpang diam-diam. Peta yang salah menghasilkan salah paham; peta yang **berpura-pura jadi sumber** menghasilkan salah bayar.

### 3. Nilai yang tinggal di config produksi WAJIB dicatat beserta tanggal ukur

Untuk tiap aturan yang nilainya config atau master data, peta mencatat nilai produksi, tanggal pengukuran, dan bila diketahui siapa yang menyetelnya. Alasannya struktural: angka itu **menentukan rupiah dan tidak terlihat di kode mana pun**, sehingga peta tanpa kolom ini akan tampak lengkap sambil melewatkan justru yang paling berbahaya.

Konsekuensi yang diterima sadar: kolom itu **basi sejak ditulis**. Karena itu tanggal ukurnya wajib, dan nilai tanpa tanggal diperlakukan sebagai tidak diketahui, bukan sebagai masih berlaku.

### 4. Tiap penyimpangan sadar wajib ADR sendiri

Penyimpangan yang diputuskan sengaja tidak boleh berhenti sebagai peringatan ⚠️ di dalam dokumen. Ia wajib jadi ADR terpisah yang menyebut pasal yang disimpangi, alasannya, dan siapa yang memutuskan.

Peringatan di dalam dokumen sudah terbukti tidak menutup apa pun: yang soal pengali mangkir berumur enam hari tanpa satu pun tindakan. ADR punya sifat yang tidak dimiliki peringatan, yaitu ia adalah keputusan yang bernama, bertanggal, dan bisa dicabut.

### 5. Yang belum diimplementasikan ditandai eksplisit, bukan dikosongkan

Baris kosong terbaca sebagai belum diperiksa. Aturan yang sudah diperiksa dan ternyata tidak ada implementasinya ditandai **belum diimplementasikan**, dengan pola pencarian yang dipakai untuk menyimpulkannya.

Ini penting karena sebagian besar temuan justru berbentuk ini: potongan gaji akibat SP II tidak pernah dibaca payroll, pengali lembur DJTK belum ada, dan angka jatah cuti 12 atau 14 hari tidak ada di kode mana pun.

## Consequences

**Yang didapat.** Ada satu tempat yang bisa dibuka saat manajemen bertanya "sistem menjalankan aturan apa", dan satu tempat yang bisa dibandingkan saat Peraturan Perusahaan direvisi. Penyimpangan berhenti menjadi pengetahuan yang tersimpan di kepala orang yang kebetulan mengukurnya.

**Yang TIDAK didapat, dan ini harus jelas.** Peta ini tidak memeriksa dirinya sendiri. Ia bisa basi persis seperti `BUSINESS_LOGIC_IMPLEMENTATION.md` yang tidak tersentuh sejak Mei. Kalau audit pertama menemukan banyak penyimpangan, itu justru argumen untuk membangun gerbang otomatis yang membaca config produksi lalu membandingkannya; keputusan itu sengaja **ditunda** sampai angka audit pertama ada, karena membangun pengawas sebelum tahu ada berapa yang perlu diawasi adalah menebak.

**Keterpaparan publik bertambah, meski isinya tidak baru.** Repo `architecture-draft` publik, dan aturan-aturan ini sebagian sudah ada di sana (tabel tarif potongan, SP II potong 25% gaji pokok). Yang bertambah adalah keterkumpulannya: satu dokumen berjudul kepatuhan jauh lebih mudah ditemukan daripada angka yang tersebar di enam dokumen teknis. Peta ini **tidak boleh memuat gaji atau data pribadi siapa pun**; ia memuat aturan dan nilai konfigurasi, bukan orang. Bila pemilik memutuskan repo ini ditutup, keputusan itu berdiri sendiri dan tidak dibatalkan oleh ADR ini.

**Beban yang ditambahkan ke alur kerja.** Perubahan apa pun pada aturan uang, sanksi, jatah, atau ambang disiplin kini menuntut dua hal, bukan satu: memperbarui kode atau config, dan memperbarui petanya. Beban ini nyata dan akan terasa. Ia diterima karena beban alternatifnya sudah terukur, yaitu potongan mangkir yang salah setengah dan lolos tiga gerbang.

**Yang harus dilakukan bila keputusan ini dicabut.** Hapus petanya, dan kembalikan penyimpangan sebagai peringatan di dokumen masing-masing. Yang hilang bersamanya adalah kemampuan menjawab "patuh atau tidak" tanpa membaca kode, dan kewajiban ADR untuk penyimpangan sadar.

**Yang TIDAK boleh disimpulkan dari ini.** ADR ini **tidak** memutuskan berapa seharusnya pengali mangkir di produksi. Itu keputusan HRD, bukan keputusan arsitektur, dan ia butuh ADR sendiri sesudah HRD mengonfirmasi apakah nilai 2 memang dikehendaki. ADR ini juga tidak menyetujui pembangunan MCP apa pun, tidak memindahkan sumber kebenaran aturan ke vault, dan tidak mengubah satu baris kode.

## Dokumen Terkait

- [[HRIS - Kepatuhan Peraturan Perusahaan]], peta yang diputuskan ADR ini
- [[HRIS - Payroll]], tarif potongan dan peringatan penyimpangan yang belum ditindaklanjuti
- [[Microservices - Payroll Service]], enam angka config dan dampak rupiah yang terukur
- [[HRIS - Disciplinary (Surat Peringatan)]], aturan SP yang sebagian belum punya efek apa pun
- [[HRIS - Attendance System]], dua ambang keterlambatan yang menentukan SP dan upah
- [[HRIS - Compensation & Benefits]], dokumen 🟡 Konsep yang seharusnya memuat ini
- [[HRIS - Overtime]], tarif dan batas jam yang dinyatakan belum ada
- [[HRIS - Leave Request]], jatah cuti dan kenapa kuota produksi bernilai 5
- [[ADR - 0061 Jatah Cuti Tahunan Terbit Otomatis di Ulang Tahun Kontrak]], akrual yang belum diimplementasikan
