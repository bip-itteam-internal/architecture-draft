# Sistem Insentif untuk Adv dan SPV Marketing

**Status**: ⚠️ **Implemented (ada catatan)** — sejak **2026-07-30** skemanya **profit-based untuk SELURUH jabatan** (SK 010/DIR/Rev-SK6/VII/2026 & SK 011/DIR/SK6/VII/2026). Perhitungannya sudah di kode dan ter-test; yang menahan pemakaian adalah master data yang belum terisi, bukan enginenya. Backend: [[Microservices - Insentive Service]].

> ⛔ **Seluruh skema KPI-multiplier per-jabatan di bawah (§SPV Marketing s/d §CRM) sudah DICABUT** dan kodenya dihapus 2026-07-30. Dipertahankan di sini sebagai riwayat SK lama — **jangan dipakai sebagai acuan perhitungan**. Yang berlaku ada di §Skema Berlaku tepat di bawah ini.

## Skema Berlaku (profit-based, SK 010 & 011/2026)

```
Profit    = Uang Cair (Net Settlement) − HPP − Beban Iklan − Biaya Operasional
Insentif  = tarif(%) × Profit
```

**Dinilai bertingkat tiga level** — ICC → Leader → Supervisor. Satu orang bisa menempati dua level sekaligus: leader yang punya toko sendiri dinilai sebagai ICC atas tokonya **dan** sebagai Leader atas total timnya, dengan target masing-masing.

| % Pencapaian Target Profit | Tarif dari profit |
| --- | --- |
| < 80% | 0% |
| 80% – 90% | **2%** |
| > 90% – 100% | **3%** |
| > 100% – 110% | **4%** |
| > 110% | **5%** |

> ⚠️ Tabel tarif **lama** di §SPV Marketing (0/1/2/3/4%) **kurang satu poin persen** dari SK. Itu bug produksi yang sempat terkunci tes; sudah dibetulkan 2026-07-30 dan diverifikasi terhadap 4 contoh perhitungan di SK.

**Aturan turunan yang mengikat:**

1. **Gerbang retur 7%** — batas berlaku selama pencapaian **≤100%**; di atas itu retur tidak lagi menggugurkan. Rasionya dari **jumlah order** (keputusan client 2026-07-31), bukan nilai rupiah; rasio nilai tetap ditampilkan sebagai pembanding karena bisa berbeda jauh (Juli 2026: 4,12% vs 3,35%).
2. **Target diketik hanya di lingkup Supervisor**, lalu dibagi rata turun ke Leader dan ICC. Baris turunan boleh ditimpa manual. Ubah target saat periode berjalan wajib beralasan; setelah disetujui, ditolak.
3. **Dasarnya UANG CAIR, bukan harga jual** — potongan marketplace dan retur sudah terpotong di dalamnya, jadi tidak dikurangkan lagi. Retur ditampilkan untuk pemantauan dan syarat 7%, bukan sebagai pengurang.
4. **Order yang belum cair sampai tanggal 25 bulan berikutnya HANGUS** untuk periode itu. Konsekuensinya dashboard akan selalu sedikit lebih tinggi dari pembukuan Accurate — itu aturan keadilan, bukan buku besar.

**Biaya operasional** dirakit dari dua sumber yang dipisah tegas: beban karyawan dari [[Microservices - Payroll Service]] (bruto + iuran BPJS pemberi kerja — **bukan** gaji bersih yang diterima) dan beban non-gaji dari proyek [[External - Accurate]] per karyawan. Alasan lengkap + daftar akun yang dikecualikan: [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]].

### Yang masih menahan (per 2026-08-02)

- **Atribusi ICC belum lengkap** — baru 10 dari 28 toko punya mapping; 63% profit Juli tak berpemilik. Sumber pengisinya berkas LIST TOKO dari client.
- **Pengecualian omzet affiliate eksternal belum terpasang** di perhitungan (daftar putihnya sudah bisa diisi, tapi belum dipakai kode) → pencapaian di layar masih lebih tinggi dari seharusnya. Terukur Juli 2026: 71,6% nilai affiliate dari kreator eksternal.
- **Beban non-gaji baru terisi di 6 dari 62 proyek karyawan** di Accurate; sisanya masih dibukukan di proyek merek.
- **Belum ada alur approval/freeze** untuk skema profit.
- Menunggu dari luar: Lampiran SK (target sesungguhnya), dan finance melengkapi HPP.
- Terbuka untuk finance: PPN di dalam profit · target sebelum/sesudah opex · jadwal bayar SK (tgl 1/5) vs cutoff pencairan (tgl 25).

---

## Riwayat: SK lama (DICABUT)

> Bagian di bawah ini adalah isi SK sebelumnya. Disimpan sebagai riwayat; **bukan acuan perhitungan**.

Data insentive selama ini diambil dari Sales, Income, Retur, dan KPI. Semua data tersebut didapat, HR melakukan perhitungan sedemikian rupa untuk menentukan nominal sesuai dengan SK dan peraturan perusahaan. SK [[doc.pdf]] ini berisi sebagai berikut:

1. Jabatan yang berhak mendapatkan insentif diantaranya Marketing Supervisor, Advertiser (Meta, TikTok, dan Marketplace), ICC (Internal Content Creator), CRM (Customer Relation Management), Affiliate Team dan Host Live Team.
2. Insentif untuk advertiser akan diberikan di setiap tanggal 5 bulan berikutnya, sedangkan insentif untuk Marketing SPV akan diberikan di tanggal 1 bulan berikutnya setelah selesai perhitungan profit oleh bagian finance.
3. Harga jual produk hanya boleh ditentukan dan/atau diubah oleh Marketing SPV dengan persetujuan dari Direktur.
4. Tim Marketing tidak diperbolehkan mengganti harga jual di bawah harga yang telah di tentukan oleh Marketing Supervisor.
5. Insentif hanya diberikan kepada tim yang sudah menandatangani kontrak PKWT (bukan masa percobaan).
6. Surat peringatan tidak mempengaruhi insentif tim marketing.
7. Ketentuan mengenai skala target profit minimal tim marketing serta penyesuaian penerapan skema insentif diatur lebih lanjut dalam Lampiran yang merupakan bagian tidak terpisahkan dari Surat Keputusan ini.
Berikut skema insentif untuk tim marketing

## SPV Marketing
Insentif SPV didasarkan pada:
1. Insentif untuk Marketing SPV berdasarkan target profit yang telah ditentukan oleh perusahaan.
2. Insentif diperhitungkan berdasarkan profit yang diperoleh dari omset aktivitas penjualan oleh Supervisor di seluruh platform setelah dikurangi beban – beban yang perhitungannya dilakukan oleh bagian finance.
3. Nilai Rata- rata KPI > 70 untuk All Team
4. Insentif tidak dicairkan apabila total retur dalam satu bulan > 10% dari total kuantiti penjualan.
5. Insentif tidak dicairkan dan indikator lainnya tidak dihitung normal apabila pencapaian profit < 80%.
Data akumulasi dibawah ini bisa diperoleh melalui [[External - Accurate]]

| No. | % Pencapaian Target Profit (Bulan) | Insentif dari profit |
| --- | ---------------------------------- | -------------------- |
| 1.  | < 80%                              | 0%                   |
| 2.  | 80% - 89.9%                        | 1%                   |
| 3.  | 90% - 99.9%                        | 2%                   |
| 4.  | 100% - 109.9%                      | 3%                   |
| 5.  | > 110%                             | 4%                   |
*Contoh:
Jika profit tercapai 80% target tetapi tidak memenuhi syarat skor KPI rata-rata tim dan retur
10% atau salah satunya tidak tercapai, maka insentif tidak diberikan.
Apabila profit ≥ 80%, syarat ketentuan terpenuhi. Misal: Pencapaian profit di angka 81%
minimal rata-rata KPI Tim 70% dan retur sesuai ketentuan. Jadi, untuk insentif 1% profit
penjualan dapat diberikan.*

## ADV / LEADER ICC
1. Insentif advertiser berdasarkan pada skor final KPI (Key Performance Indicator).
2. Skor Final KPI (Key Performance Indicator) dinilai berdasarkan jumlah konversi dan ROI Tim ICC sesuai dengan target yang telah ditentukan oleh Marketing SPV dengan persetujuan dari Tim Finance dan Direktur.
3. Insentif tidak dicairkan apabila skor final KPI advertiser di bawah 70.
4. Insentif hanya dihitung berdasarkan jumlah konversi yang tertera pada dashboard akun pengiklan masing-masing advertiser.
5. Penjualan lain di luar marketplace tiktok seperti diantaranya shopee, tokopedia, dan Lazada tidak mempengaruhi insentif pada advertiser.
6. Skema perhitungan insentif advertiser secara bertingkat sebagai berikut:

| KPI            | Kriteria                                             | rumus                 |
| -------------- | ---------------------------------------------------- | --------------------- |
| Final skor KPI | Jika final skor KPI >= 100; maka di kali 2           | 2 x  jumlah konversi  |
| Final skor KPI | Jika final skor KPI >= 90 - <= 99.9; maka dikali 1.5 | 1.5 x jumlah konversi |
| Final skor KPI | Jika final skor KPI >= 80 - <= 89.9; maka dikali 1   | 1 x jumlah Konversi   |
| Final skor KPI | Jika final skor KPI >= 70 - <= 79.9; maka dikali 0.5 | 0.5 x jumlah konversi |
| Final skor KPI | <= 69.9                                              | 0                     |
*Contoh: Jika final score KPI 92, dengan jumlah konversi 95.400. Maka insentif yang diterima
advertiser adalah sebagai berikut:
Perhitungannya: (Finale Score x 1,5 x Jumlah Konversi )
= 92 x 1,5 x 95.400 = Rp 13.165.200; Jadi untuk insentif yang diterima yaitu sebesar Rp
13.165.200.*

## ADV META DAN MARKETPLACE SHOPEE
1. Insentif advertiser berdasarkan pada skor final KPI (Key Performance Indicator).
2. Skor Final KPI (Key Performance Indicator) dinilai berdasarkan CPA dan jumlah konversi sesuai dengan target yang telah ditentukan oleh Marketing SPV dengan persetujuan dari Tim Finance dan Direktur.
3. Insentif tidak diberikan apabila skor final KPI advertiser di bawah 70.
4. Skema perhitungan insentif advertiser sebagai berikut:

| KPI            | Kriteria                                             | rumus                 |
| -------------- | ---------------------------------------------------- | --------------------- |
| Final skor KPI | Jika final skor KPI >= 81; maka di kali 5            | 5 x  jumlah konversi  |
| Final skor KPI | Jika final skor KPI >= 70 - <= 80.9; maka dikali 2   | 2 x jumlah konversi   |
| Final skor KPI | <= 69.9                                              | 0                     |
*Contoh: Jika final score KPI 76, dengan jumlah konversi 8.300. Maka insentif yang diterima
advertiser adalah sebagai berikut:
Perhitungannya: (Finale Score x 2 x Jumlah Konversi)
= 76 x 2 x 8.300 = Rp 1.261.600; Jadi untuk insentif yang diterima yaitu sebesar Rp 1.261.600.*

## ICC (Internal Content Creator)
1. Insentif ICC berdasarkan pada skor final KPI (Key Performance Indicator).
2. Skor Final KPI (Key Performance Indicator) dinilai berdasarkan Jumlah Video dan Konversi sesuai dengan target yang telah ditentukan oleh Marketing SPV dengan persetujuan dari Tim Finance dan Direktur.
3. Insentif tidak diberikan apabila skor final KPI advertiser di bawah 70.
4. Skema perhitungan insentif Internal Content Creator tahun 2025 sebagai berikut:

| KPI            | Kriteria                                          | rumus                |
| -------------- | ------------------------------------------------- | -------------------- |
| Final skor KPI | JJika Final Skor KPI ≥ 81; maka di kali 5         | 5 x  jumlah konversi |
| Final skor KPI | Jika Final Skor KPI ≥ 70 - ≤ 80,9; maka di kali 2 | 2 x jumlah konversi  |
| Final skor KPI | <= 69.9                                           | 0                    |
*Contoh: Jika final score KPI 76, dengan jumlah konversi 7.800. Maka insentif yang diterima
advertiser adalah sebagai berikut:
Perhitungannya: (Finale Score x 2 x Jumlah Konversi)
= 76 x 2 x 7.800 = Rp 1.185.600; Jadi untuk insentif yang diterima yaitu sebesar Rp 1.185.600.*

5. Syarat khusus **ICC 2026**
	1. produksi konten
		![[ICC1.png]]
		Ini memastikan volume & kualitas pola, BUKAN kreativitas yang liar.
		1. Bonus /Insentif
			Base salary tetap.
			Bonus Bulanan berdasarkan:
			Tingkat cache quality → Rp 10.000 jika CTR ≥ 2% & Watch ≥ 30% (10.000)
			+ bonus tambahan bulanan jika ada video dijadikan GMV Max Winner
		2. Contoh angka realistis:
			Rp 10.000 / video yang CTR ≥ 2% & Watch ≥ 30% (minimal 7 hari)
			Rp 150.000 / bulan jika videonya naik ke GMV Max & ROI GMV Max ≥ 3.2 (minimal 7 hari), ada Penjualan min. 15 order ( dalam 7 Hari ), VIDEO BERLAKU 30 DARI SETELAH DI UPLOAD
			Artinya:
			- ICC punya tujuan jangka pendek (video lolos pola)
			- Dan tujuan jangka menengah (cache bagus)
			- Dan tujuan jangka panjang (menyumbang winner)
			Tidak ada KPI penjualan di level ICC. Penjualan adalah ranah GMV Max.
			*Note : Video hanya berlaku di periode bulan tsb dan video yang sudah mendapatkan insentif tidak masuk dalam perhitungan insentif bulan selanjutnya serta tidak boleh dihapus tanpa sepengetahuan atasan.*
			
			**Target video 125 / bulan**

	2. konversi nilai **KPI ICC**
		- Nilai KPI tidak mempengaruhi nominal pendapatan insentif tim Internal Content Creator, tetapi menjadi sebuah bahan evaluasi penilaian Supervisor dan Manajemen.
		- Nilai KPI menjadi penentuan untuk kenaikan gaji tim.
		- Skema Penilaian KPI Tim ICC mulai Januari 2026 sebagai berikut:
		- ![[ICC2.png]]

## HOST LIVE
1. Insentif Host Live berdasarkan pada skor final KPI Tim (Key Performance Indicator).
2. Skor Final KPI (Key Performance Indicator) dinilai berdasarkan konversi sesuai dengan target yang telah ditentukan oleh Marketing SPV dengan persetujuan dari Tim Finance dan Direktur.
3. Insentif tidak diberikan apabila skor final KPI tim host live di bawah 70.
4. Total insentif tiap tim dibagi sejumlah anggota tim. Misal anggota tim terdiri dari 5 orang.
5. Skema perhitungan insentif Host Live Team sebagai berikut:

| KPI            | Kriteria                                          | rumus                |
| -------------- | ------------------------------------------------- | -------------------- |
| Final skor KPI | JJika Final Skor KPI ≥ 81; maka di kali 5         | 5 x  jumlah konversi |
| Final skor KPI | Jika Final Skor KPI ≥ 70 - ≤ 80,9; maka di kali 2 | 2 x jumlah konversi  |
| Final skor KPI | <= 69.9                                           | 0                    |
*Contoh: Jika final score KPI 80, dengan jumlah konversi 9.500. Maka insentif yang diterima
advertiser adalah sebagai berikut:
Perhitungannya: (Finale Score x 5 x Jumlah Konversi)/Jumlah Anggota Tim
= (80 x 5 x 9.500)/5 orang = Rp 760.000; Jadi untuk insentif yang diterima setiap orang yaitu
sebesar Rp 760.000.*

## AFFILIATOR
1. Insentif Affiliator Team berdasarkan pada skor final KPI Tim (Key Performance Indicator).
2. Skor Final KPI (Key Performance Indicator) dinilai berdasarkan jumlah affiliate aktif dan konversi sesuai dengan target yang telah ditentukan oleh Marketing SPV dengan persetujuan dari Tim Finance dan Direktur.
3. Total insentif tiap tim dibagi sejumlah anggota tim. Misal anggota tim terdiri dari 4 orang.
4. Skema perhitungan insentif Affiliator Team sebagai berikut:

| KPI            | Kriteria                                          | rumus                |
| -------------- | ------------------------------------------------- | -------------------- |
| Final skor KPI | JJika Final Skor KPI ≥ 81; maka di kali 2         | 2 x  jumlah konversi |
| Final skor KPI | Jika Final Skor KPI ≥ 70 - ≤ 80,9; maka di kali 2 | 1 x jumlah konversi  |
| Final skor KPI | <= 69.9                                           | 0                    |

*Contoh: Jika final score KPI 81, dengan jumlah konversi 24.500. Maka insentif yang diterima
advertiser adalah sebagai berikut:
Perhitungannya: (Finale Score x 2 x Jumlah Konversi)/Jumlah Anggota Tim
= (81 x 2 x 24.600)/4 orang = Rp 996.300 Jadi untuk insentif yang diterima setiap orang yaitu
sebesar Rp 996.300.*


## CS

1. Insentif Customer Service Meta berdasarkan pada skor final KPI Tim (Key Performanc Indicator).
2. Skor Final KPI (Key Performance Indicator) dinilai berdasarkan closing rate 50% dan konversi sesuai dengan target yang telah ditentukan oleh Marketing SPV dengan persetujuan dari Tim Finance dan Direktur.
3. Apabila customer service dengan closing rate di bawah 50%, maka insentif tidak dicairkan dan/atau kembali ke perusahaan.
4. Insentif yang didapatkan berdasarkan akumulasi dalam satu bulan.
5. Skema perhitungan insentif Customer Service sebagai berikut:

| KPI            | Kriteria                                          | rumus                 |
| -------------- | ------------------------------------------------- | --------------------- |
| Final skor KPI | JJika Final Skor KPI ≥ 81; maka di kali 10        | 10 x  jumlah konversi |
| Final skor KPI | Jika Final Skor KPI ≥ 70 - ≤ 80,9; maka di kali 5 | 5 x jumlah konversi   |
| Final skor KPI | <= 69.9                                           | 0                     |

*Contoh: Bobot KPI 40 untuk closing rate 50% dari total lead yang masuk dan bobot KPI 60
dengan target konversi sebesar 3.400 (sesuai dengan target yang telah ditentukan serta
disetujui Tim Finance & Direktur).
Jika final score KPI 73 dengan jumlah konversi 2800. Maka insentif yang diterima advertiser
adalah sebagai berikut:
Perhitungannya: (Finale Score x 5 x Jumlah Konversi) = 73 x 5 x 2800 = Rp 1.027.765
Jadi untuk insentif yang diterima setiap orang yaitu sebesar Rp 1.027.765.*
## CRM
1. Insentif CRM berdasarkan pada skor final KPI Tim (Key Performance Indicator). 
2. Skor Final KPI (Key Performance Indicator) dinilai berdasarkan konversi sesuai dengan target yang telah ditentukan oleh SPV dengan persetujuan dari Tim Finance dan Direktur.
3. Insentif tidak diberikan apabila skor final KPI tim CRM di bawah 70.
4. Total insentif tiap tim dibagi sejumlah anggota tim. Misal anggota tim terdiri dari 5 orang.
5. Skema perhitungan insentif CRM Team sebagai berikut:

| KPI            | Kriteria                                          | rumus                |
| -------------- | ------------------------------------------------- | -------------------- |
| Final skor KPI | JJika Final Skor KPI ≥ 81; maka di kali 5         | 5 x  jumlah konversi |
| Final skor KPI | Jika Final Skor KPI ≥ 70 - ≤ 80,9; maka di kali 2 | 2 x jumlah konversi  |
| Final skor KPI | <= 69.9                                           | 0                    |
*Contoh: Jika final score KPI 80, dengan jumlah konversi 5.000. Maka insentif yang diterima
advertiser adalah sebagai berikut:
Perhitungannya: (Finale Score x 5 x Jumlah Konversi)/Jumlah Anggota Tim
= (80 x 5 x 5000)/5 orang = Rp 400.000; Jadi untuk insentif yang diterima setiap orang yaitu
sebesar Rp 400.000.*


## Sistem Finance (acuan akuntansi)
Sistem finance mencatat Sales, Income dan Retur. Namun yang menjadi acuan adalah accurate online. accurate online memiliki API yang bisa digunakan untuk mengambil data yang dibutuhkan

## Arsitektur & Sumber Data (keputusan)

Sistem insentif dibangun **gabung ke ERP**, basis **MongoDB**, dengan **RBAC per divisi**. Sumber data per komponen **skema berlaku**:

| Komponen | Sumber |
|---|---|
| Uang cair, HPP, beban iklan, retur | [[Microservices - Integration Service]] `GET /profit/incentive/summary` (per toko, basis hari kirim + cutoff 25) |
| Beban karyawan | [[Microservices - Payroll Service]] `GET /employer-cost` |
| Beban operasional non-gaji | [[External - Accurate]] per proyek, lewat integration `GET /profit/incentive/opex` |
| Struktur tim, target, daftar putih affiliate | `insentive_db` (master data di [[Microservices - Insentive Service]]) |
| Pemilik toko (ICC) | `icc_account_mappings` di integration — lihat [[Sales - ICC Account Manager Mapping]] |

**Sumber skema LAMA yang tak lagi dipakai**: skor KPI dari [[APP - Dynamic Task Tracker]] dan jumlah konversi dari [[Sales - GMV Creative]] — keduanya tak masuk rumus profit-based. KPI tetap dipakai untuk evaluasi & kenaikan gaji, bukan penentu nominal insentif.

> Rincian desain & investigasi (pertimbangan Desty, pertanyaan terbuka, rancangan field lengkap) di-capture di `Workspace/Inbox` sampai sistem dibangun — lihat catatan naik-kelas.

## Dependensi & Integrasi

- [[Sales - Incentive]]
- [[Sales - GMV Creative]]
- [[External - Accurate]]
- [[Finance - Bridging App]]
- [[APP - Dynamic Task Tracker]]

## Dokumen Terkait

- [[Sales - Incentive]] — irisan sisi marketing
- [[Microservices - Insentive Service]] — backend perhitungan insentif
- [[ADR - 0033 Beban Operasional Insentif dari Proyek Accurate]] — keputusan sumber biaya operasional
- [[Microservices - Integration Service]] (komponen profit) · [[Microservices - Payroll Service]] (beban karyawan) · [[External - Accurate]] (pembukuan)
- [[Sales - GMV Creative]] · [[APP - Dynamic Task Tracker]] — sumber skema LAMA, tak dipakai rumus profit
- [[Finance - Bridging App]] · [[HRIS - Compensation & Benefits]]
