
# Latar Belakang

Kalodata adalah 3rd party software yang melakukan rangking konten dan iklan Tiktok. Marketing bisa memanfaatkan data ini sebagai acuan iklan & konten apa yang dibuat.

## Production
https://gmv-creative.bharatainternasional.com

## Update
#### 13 Januari 2026
   a. Nama adv
   b. filtering per column
   c. Persentase watch time 30% dari 50%: 
	Total impression | > Views 50% | Target KPI
	3015		           |1000               | 33%

# Permasalahan
1. Kalodata cukup mahal. 
   ![[kalodata-pricing.png]]

2. Data Kalodata tidak lengkap. Tidak ada CTR, average watch time
   ```json
	   {
		"success": true,
		  "data": [
		    {
		      "video_id": "video123",
		      "video_title": "Top 10 Tech Products Review",
		      "belonged_creator_id": "creator456",
		      "belonged_creator_handle": "techreviewer",
		      "revenue": 3500.25,
		      "views": 250000,
		      "revenue_growth_rate": 15.5,
		      "ads_roas": 4.2,
		      "digg_count": 15000,
		      "share_count": 2500,
		      "comment_count": 800,
		      "ad_revenue_ratio": 0.35,
		      "ad_view_ratio": 0.12,
		      "creator_debut": "2024-01-15"
		    }
		  ],
		  "message": "string",
		  "debug": {},
		  "cached": true,
		  "code": "string
	   }
    ```
    
3. Claim akurasi 75 - 80 % 
# Pertimbangan
1. tetap menggunakan Kalodata namun export data manual tanpa berlangganan API. Jika dihitung:
	* API per 6 bulan = Rp. 250 juta = Rp 40 Juta / bulan (solusi jangka panjang untuk AI)
		* Cara ini cepat karena bisa diotomasi dari hulu ke hilir. namun apakah sepadan dengan anggaran yang dikeluarkan
	* dashboard Rp 8 juta per tahun = Rp. 600 rb / bulan (solusi jangka pendek)
		* cara ini lebih murah karena ada member tim yang melakukan export data setiap hari melalui dashboard. kemudian di import ke sistem kita. namun perlu effort lebih 
2. Menggunakan 3rd party lain
# Pengembangan
url: https://gmv-creative.bharatainternasional.com
repo: https://github.com/bip-itteam-internal/Bharata-Internal-tiktok