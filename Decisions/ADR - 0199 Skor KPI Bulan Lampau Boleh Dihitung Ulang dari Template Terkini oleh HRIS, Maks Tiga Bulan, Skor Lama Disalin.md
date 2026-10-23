# ADR - 0199 Skor KPI Bulan Lampau Boleh Dihitung Ulang dari Template Terkini oleh HRIS, Maks Tiga Bulan, Skor Lama Disalin

> **Status**: 🟢 Diterima, 2026-10-23, oleh Azzerith. Empat bentuknya dipilih lewat pilihan ganda di sesi kerja Cost Control (2026-10-23). **Kode**: BE di bip-erp PR [#3484](https://github.com/bip-itteam-internal/bip-erp/pull/3484), lolos judge, **belum merge**, belum deploy. FE erp-frontend#2769 belum dikerjakan. Mengamandemen [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] bab Consequences ("nilai otomatis yang dihitung ulang belakangan tidak retroaktif") dan [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] butir 3. Amandemen ini **hanya** membuka satu jalur bergerbang, bukan menghapus pembekuan.

## Untuk Manajemen

**Apa yang berubah di layar.**
- Di kartu skor KPI bulan lampau, HRD melihat tombol **"Hitung ulang dari template terkini"**.
- Sebelum menyimpan, sistem menampilkan pratinjau: skor lama vs skor baru per butir, beserta rinciannya.
- HRD wajib menulis alasan. Sesudah disimpan, kartu skor menampilkan keterangan "Dihitung ulang oleh X, tanggal, dari 49,13 ke 52,93".

**Siapa yang terdampak.**
- HRD: satu-satunya yang boleh menekan tombol ini.
- Atasan departemen yang menemukan skor keliru: meminta ke HRD, tidak menghitung ulang sendiri.
- Karyawan yang dihitung ulang: skornya berubah dan perubahannya terlihat.

**Apa yang TIDAK dijanjikan.**
- Hanya **tiga bulan terakhir yang sudah lewat**. Bulan yang lebih lama tetap beku.
- Hanya **satu karyawan per kali**. Tidak ada hitung ulang massal per template.
- Skor atasan yang memakai skor anggota (`skor_tim`) **tidak ikut berubah otomatis**. Bila perlu, skor atasan dihitung ulang terpisah.
- Butir manual yang tak bisa dicocokkan dengan template terkini membuat hitung ulang **ditolak**. Isi lewat form Nilai KPI biasa.

**Perkiraan besaran kerja.** Dua PR, backend lebih dulu:
1. Endpoint pratinjau dan simpan hitung ulang, plus koleksi riwayat, di employee-service.
2. Tombol, pratinjau, dan keterangan di kartu skor erp-frontend.

## Context

Kasus pemicunya 2026-10-23, Cost Control (BIP-0065-07-24).
- Skor September dibekukan dengan konfigurasi template lama. Butir "Review Cash Outflow Mingguan" (bobot 40%) masih membaca `varians_anggaran`.
- HRD baru memperbaiki template pada 2026-10-20, dan isian proyeksi kas Finance juga baru masuk sesudahnya.
- Akibatnya, skor yang tersimpan 49,13 dengan rincian varians, sedangkan hitungan dari template terkini memberi ≈ 52,93 dengan rincian akurasi forecast. Angkanya diukur di prod lewat `GET /kpi/auto-values`, hanya baca.

Jalur yang ada saat itu tidak menolong:
- **Mengubah template tidak retroaktif.** Template disalin ke `kpi_score` saat disimpan. Ini disengaja oleh [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]].
- **Finalisasi otomatis melewati yang sudah dinilai.** Sebabnya `sebabSudahDinilai` di `kpi_finalisasi.go`, dan penulisannya memakai `$setOnInsert`.
- **Form Nilai KPI tidak memberi usulan otomatis untuk periode yang sudah dinilai.** Form itu terisi nilai lama. `POST /kpi` memang menstempel ulang `auto_*` dengan template terkini, tetapi skornya tetap dihitung dari angka yang diketik penilai. Penilai harus menyalin angka baru yang tidak ditampilkan di mana pun.

## Decision

1. **Satu jalur baru, bergerbang HRIS.** Jalur ini memakai `RequireKPIDepartmentRBAC(c, "")` (departemen kosong = reach `all`), gerbang yang sama dengan penyunting template di `GET /kpi/templates`. Yang lolos: `hris` staff/supervisor, paket `kpi_semua`, serta IT supervisor/Direktur lewat super-akses yang sudah ada. Supervisor departemen (reach `division`) **ditolak**.
2. **Jangkauan maksimal tiga bulan yang sudah lewat**, dihitung terhadap bulan berjalan WIB. Pada Oktober 2026, yang boleh adalah Juli, Agustus, dan September. Bulan berjalan dan bulan yang lebih tua ditolak dengan pesan yang menyebut batasnya. Batas `3` ditulis sebagai satu konstanta bernama di backend dan dikirim ke FE lewat respons pratinjau, bukan disalin ke FE.
3. **Per karyawan per periode, selalu lewat pratinjau.**
   - `GET` pratinjau menghitung tanpa menulis.
   - `POST` menyimpan dan wajib membawa alasan.
   - Pratinjau dan simpan memakai fungsi hitung yang sama, jadi angka yang disimpan sama dengan yang dilihat.
4. **Template yang dipakai.**
   - Dipakai template master dengan `_id` yang sama dengan snapshot, dalam versi terkininya.
   - Template yang diarsip atau dihapus membuat hitung ulang **ditolak**.
   - Kecocokan jabatan diperiksa terhadap jabatan **pada periode itu** (`posisiKPIUntukPenilaian`), sama seperti `POST /kpi`.
5. **Nilai per butir.**
   - **Butir otomatis** memakai `auto_value` hasil hitung baru.
   - **Butir otomatis yang gagal dihitung** membuat seluruh hitung ulang **ditolak**, bukan disimpan sebagian. Ini sejalan dengan [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]], yang memilih tidak membekukan skor berkomponen bolong.
   - **Butir manual** memakai nilai lama bila labelnya ada di snapshot lama.
   - **Butir manual baru** yang tak punya nilai lama membuat hitung ulang **ditolak**, dengan arahan ke form Nilai KPI.
6. **Jejak: skor lama disalin utuh sebelum ditimpa.**
   - Seluruh dokumen `kpi_score` lama (template snapshot, nilai, `auto_*`, skor, metadata) disalin ke koleksi baru **`kpi_score_riwayat`** di `employee_db`.
   - Bersamanya dicatat `alasan`, `oleh`, `pada`, `skor_lama`, dan `skor_baru`.
   - Dokumen `kpi_score` yang baru membawa penanda `dihitung_ulang` berisi `oleh`, `pada`, `alasan`, `skor_lama`, dan `riwayat_id`. Kartu skor membacanya untuk menampilkan keterangan.
   - Urutannya **salin dulu, baru timpa**. Bila salinan gagal, skor lama tidak disentuh.
7. **Yang sengaja tidak dilakukan.**
   - Tidak ada hitung ulang massal.
   - Tidak ada rantai otomatis ke skor atasan (`skor_tim`).
   - Tidak ada notifikasi ke karyawan.
   - Tidak ada endpoint pembatalan. Membatalkan = hitung ulang lagi, atau koreksi manual lewat form; riwayatnya tetap utuh.

**Gerbang turunan (plan-checklist §1):**
- Portal Persetujuan: tidak, karena tidak ada tahap yang menunggu tindakan orang lain.
- Kalender: tidak.
- Copilot: tidak, karena pratinjau adalah alat koreksi HR, bukan laporan.

## Consequences

**Yang diterima sadar.**
- **Skor bulan lampau bisa bergerak**, paling jauh tiga bulan ke belakang. Rata-rata departemen ([[ADR - 0147 Rata-rata KPI Departemen Dibagi yang Sudah Dinilai, Cakupan Ditampilkan Terpisah]]) memang dihitung ulang tiap baca, jadi ikut bergeser.
- **`kpi_score` punya penulis ketiga**, sesudah `POST /kpi` dan finalisasi. Penanda `dihitung_ulang` membedakannya.
- **Skor atasan yang memakai skor anggota bisa tertinggal.** Dibiarkan, karena merambat otomatis berarti satu klik mengubah skor orang yang tidak dipilih.

**Risiko yang dijaga kode, bukan kebiasaan.**
- Pratinjau dan simpan berbagi satu fungsi murni, diuji dengan fixture yang template lama dan barunya **berbeda sumber**.
- Urutan salin-lalu-timpa diuji dengan kegagalan salinan yang disimulasikan.
- Gerbang reach diuji dengan supervisor departemen (harus 403) dan staf HRIS (harus lolos).

## Dokumen Terkait

- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
- [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]
- [[ADR - 0147 Rata-rata KPI Departemen Dibagi yang Sudah Dinilai, Cakupan Ditampilkan Terpisah]]
- [[HRIS - Otomasi Skor KPI]]
- [[Microservices - Employee Service]]
