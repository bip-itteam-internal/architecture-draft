# Sistem Insentif untuk Adv dan SPV Marketing

🟡 **Konsep / Direncanakan** — skema insentif marketing (acuan SK perusahaan); sistem perhitungan terpadu masih dirancang. Backend terkait: [[Microservices - Insentive Service]].

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

Sistem insentif diputuskan dibangun **gabung ke ERP**, basis **MongoDB**, dengan **RBAC per divisi**. Sumber data per metrik:

- **Profit / total penjualan & retur** → [[External - Accurate]] (API).
- **Jumlah konversi** → [[Sales - GMV Creative]] / Dashboard TikTok (penjualan non-TikTok tidak dihitung untuk advertiser).
- **Skor KPI (individu & tim)** → [[APP - Dynamic Task Tracker]].
- **Jabatan & jumlah anggota tim** → ERP / Master Data Karyawan.

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
- [[External - Accurate]] (profit/penjualan) · [[Sales - GMV Creative]] (konversi) · [[APP - Dynamic Task Tracker]] (skor KPI)
- [[Finance - Bridging App]] · [[HRIS - Compensation & Benefits]]
