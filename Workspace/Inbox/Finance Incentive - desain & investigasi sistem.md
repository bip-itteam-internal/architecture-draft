---
publish: false
---

> **Naik-kelas dari:** [[Finance - Incentive]] · **Dipindah:** 2026-06-25 · capture desain & investigasi sistem insentif (belum dibangun). Ringkasan keputusan sudah ditarik ke dok grounded.

Insentive itu pakai rumus .
Tiap-tiap rumus itu berbeda tiap jabatan marketing.

Pertanyaanya / problems :
1.	Bagaimana rumus perhitungan insentive nya ?
2.	Dari mana mengambil sumber datanya ?
		a. Tiktok Dashboard mekanisme pengambilan datanya terlalu kompleks,  pertimbangkan alternatif seperti desty.mekari
		
3.	Bagaimana arsitekturnya :
		a. Apakah gabung di erp atau finance atau terpisah ? [x]
		b. Pakai mongodb atau postgres ? [X]
		c. Bagaimana rancangan database, collection nya ? 

Jawaban :
1.	Rumus perhitungan insentive itu sudah dijelaskan di Finance – Incentive. 
2.	Dari dashboard tiktok, accurate, erp, task manager dengan detail :
	Berikut detail sumber data berdasarkan asumsi untuk tiap role marketing :
	
	### SPV Marketing
	1. insentive
	2. [[Sales - GMV Creative]]/Dashboard TikTok
	3. [[APP - Dynamic Task Tracker]]
	4. [[External - Accurate]]
	5. insentive

	### ADV Leader
	6. insentive
	7. [[APP - Dynamic Task Tracker]]
	8. insentive
	9. [[External - Accurate]]
	10. insentive

	### ADV META DAN MARKETPLACE
	11.  insentive
	12. [[APP - Dynamic Task Tracker]] dan [[Sales - GMV Creative]]/Dashboard TikTok
	13. insentive

	### ICC
	14. insentive
	15. [[APP - Dynamic Task Tracker]] dan [[Sales - GMV Creative]]/Dashboard TikTok
	16. insentive

	### HOST LIVE
	17. insentive
	18. [[APP - Dynamic Task Tracker]]
	19. insentive

	### AFFILIATOR
	20. insentive
	21. [[APP - Dynamic Task Tracker]]
	22. insentive

	### CRM
	23. insentive
	24. [[APP - Dynamic Task Tracker]]
	25. insentive

b.  **Pertimbangan Desty.omnychannel**
				Untuk pertimbangan dijabarkan data-data/parameter yang diperlukan untuk sistem intensive dari marketplace. 
				1. Tiktok Dashboard hanya mencakup data dari tiktok saja tidak dari marketplace lain sedangkan desty omnichannel bisa langsung banyak marketplace
				2. 
			Kesimpulan :
			saat ini coba tiktok dashboard karena desty perlu melakukan transaksi dengan pihaknya.
			
c. Berikut rancangan data yang diperlukan dari sumber external :
		
### 1. Data Keuangan & Penjualan (Sales & Finance Metrics)
Data ini adalah metrik absolut yang menentukan besaran uang yang akan dikali atau dibagikan.

- **Pencapaian Profit (Laba Bersih)**
    
    - **Cara Memperoleh:** Diambil melalui API dari sistem **Accurate Online**.
        
    - **Digunakan Untuk:** Menghitung insentif **SPV Marketing**. Syarat wajib pencapaian profit adalah minimal 80% dari target.
        
    - **Ekspektasi Hasil:** Angka persentase (contoh: 85.5%) dan nominal Rupiah dari profit aktual.
        
- **Total Kuantitas Penjualan & Total Retur**
    
    - **Cara Memperoleh:** Diambil melalui API **Accurate Online**.
        
    - **Digunakan Untuk:** Validasi insentif **SPV Marketing**. Insentif tidak cair jika total retur dalam satu bulan > 5% dari total kuantiti penjualan.
        
    - **Ekspektasi Hasil:** Angka bulat (Integer) untuk total barang terjual dan total barang retur.
        
- **Jumlah Konversi (Sales/Closing)**
    
    - **Cara Memperoleh:** Agregasi data dari **Sales - GMV Creative** atau Dashboard Akun Pengiklan (TikTok). Penjualan di luar TikTok (Shopee, Tokopedia, Lazada) tidak dihitung untuk Advertiser.
        
    - **Digunakan Untuk:** Menjadi angka pengali dasar untuk insentif **ADV Leader, ADV Meta, ICC, Host Live, Affiliator, dan CRM**.
        
    - **Ekspektasi Hasil:** Angka bulat (Integer), contoh: 55.000 konversi.

### 2. Data Kinerja Karyawan (KPI & Performance Metrics)

Data ini digunakan sebagai "Faktor Pengali" (Multiplier) atau gerbang validasi pencairan insentif.

- **Final Skor KPI (Individu)**
    
    - **Cara Memperoleh:** Diambil dari aplikasi internal **Dynamic Task Tracker**. Skor ini merupakan hasil penilaian dari konversi, CPA, atau jumlah video.
        
    - **Digunakan Untuk:** Penentu multiplier untuk **ADV Leader, ADV Meta, dan ICC**. Insentif tidak cair jika skor di bawah 70.
        
    - **Ekspektasi Hasil:** Angka desimal (contoh: 92.5).
        
- **Final Skor KPI (Tim)**
    
    - **Cara Memperoleh:** Diambil dari **Dynamic Task Tracker**.
        
    - **Digunakan Untuk:** Penentu insentif untuk peran berbasis tim yaitu **Host Live, Affiliator, dan CRM**. Serta validasi untuk **SPV Marketing** (rata-rata KPI tim harus > 70).
        
    - **Ekspektasi Hasil:** Angka desimal rata-rata per tim (contoh: 80.0).
        

### 3. Data Khusus Kualitas Konten (Khusus ICC)

Data ini digunakan murni untuk menghitung bonus tambahan di luar hitungan konversi dasar untuk tim Internal Content Creator.

- **Metrik Kualitas Video (CTR & Watch Time)**
    
    - **Cara Memperoleh:** Diambil dari analitik platform (TikTok Dashboard).
        
    - **Digunakan Untuk:** Memberikan bonus Rp 10.000 per video jika CTR ≥ 2% dan Watch ≥ 30% selama minimal 7 hari.
        
    - **Ekspektasi Hasil:** Daftar (Array) ID Video yang memenuhi syarat beserta total nominal bonusnya (contoh: 15 video kualifikasi = Rp 150.000).
        
- **Status GMV Max Winner**
    
    - **Cara Memperoleh:** Diambil dari data penjualan / TikTok Dashboard.
        
    - **Digunakan Untuk:** Memberikan bonus tambahan bulanan sebesar Rp 150.000 per video jika ROI GMV Max ≥ 3.2 dan menghasilkan minimal 15 order dalam 7 hari (berlaku 30 hari setelah upload).
        
    - **Ekspektasi Hasil:** Jumlah video yang menjadi _Winner_ bulan tersebut.
        

### 4. Data Struktur Organisasi (HR/ERP Data)

Data ini memastikan uang dibagikan kepada orang yang tepat dengan pembagi yang tepat.

- **Jabatan Karyawan (Role)**
    
    - **Cara Memperoleh:** Dari sistem ERP / Master Data Karyawan (MongoDB).
        
    - **Digunakan Untuk:** Menentukan rute rumus mana yang akan dieksekusi oleh sistem (misal: membedakan apakah karyawan pakai rumus ADV Leader atau ICC).
        
    - **Ekspektasi Hasil:** String ID Jabatan atau Nama Jabatan saat periode insentif berjalan.
        
- **Jumlah Anggota Tim**
    
    - **Cara Memperoleh:** Dari sistem ERP / Task Tracker.
        
    - **Digunakan Untuk:** Menjadi angka pembagi hitungan total insentif untuk tim **Host Live, Affiliator, dan CRM**.
        
    - **Ekspektasi Hasil:** Angka bulat (Integer), contoh: 5 orang.

3.	jawaban 
		a.  Gabung ke ERP
		b.  Menggunakan monggoDB

Catatan :
- Butuh RBAC untuk membatasi akses user berdasarkan divisinya
- perlu pengetahuan GMV itu apakah sama dengan dashboard tiktok jika sama maka data-data yang dari dashboard tiktok tidak perlu diambil lagi => Asumsi salah karena GMV tidak mengambil data dari dashboard TIKTOK. Perlu mendalami bagaimana mengambil data - data yang diperlukan dari tiktok dashboard
- task manager jelas perlu diperbarui jika ingin dibuat realtim mengikut fitur insentive atau jika ingin targer cepat paling dibuat input manual tanpa refactor task manager
