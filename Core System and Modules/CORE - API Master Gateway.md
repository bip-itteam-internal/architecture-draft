## Deskripsi

*Pembuatan satu API Gateway tunggal yang dapat me-reroute ke seluruh authentication sistem berdasarkan sistem yang sedang berjalan akan bermanfaat bagi keseluruhan sistem karena pengelolaannya menjadi lebih mudah dan terpusat*

[Baca lebih lanjut tentang implementasi API Master Gateway kami](https://github.com/bip-itteam-internal/api-gateway-test)

## Kebutuhan

- [x] Menangani authentication
- [x] Meneruskan payload untuk digunakan oleh modul pada sistem
- [x] API Gateway terpusat ke modul lain pada sistem
- [x] Fitur login dan logout (data diambil dari Employee Master Data pada collection System Authentication)
- [x] Registrasi dari pengguna yang pertama kali login dengan employee ID dan password sementara yang diberikan oleh HRD
- [x] Penyederhanaan reroute request dan internal request untuk kemudahan pengembangan
	- Reroute hanya digunakan oleh API Gateway itu sendiri
	- Internal request digunakan untuk request antar service (service-to-service)

## Forwarded Request / Reroute

Berikut adalah endpoint yang valid, propagated call atau forwarded request dari gateway ini
Daftar endpoint yang di-expose pada masing-masing modul akan dibahas kemudian

- [ ] [[DB - Overview and Notes]]
- [ ] [[Microservices - Employee Service]]
- [ ] [[Microservices - Attendance Service]]
- [ ] [[Microservices - File Service]]
- [ ] [[Microservices - Notification Service]]

Sebagian dari daftar di atas juga memiliki open-route yang berarti semua orang dapat melakukan request ke endpoint tersebut, namun tetap disertai beberapa pemeriksaan tambahan

Daftar modul yang belum diketahui per 10/17/25

- [ ] [[APP - Dynamic Task Tracker]]

### Authorization Gateway ke Endpoint Modul

API Gateway dan setiap modul berbagi secret yang cocok berupa **INTERNAL-KEY**, key ini hanya disertakan ketika request dari API Gateway diteruskan ke modul
Setiap endpoint modul akan memvalidasi **INTERNAL-KEY** gateway ini dengan miliknya sendiri, apabila key yang diberikan
hilang atau tidak benar maka akan menghasilkan error unauthorized

Database bersifat internal dan tidak di-expose, database harus disiapkan dengan benar di docker agar dapat berkomunikasi dengan API Gateway secara tepat

![[gateway-example.png]]

Baca lebih lanjut tentang [mTLS](https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/) metode authorization yang lebih aman

Beberapa informasi juga dibutuhkan untuk mengakses sebuah route, termasuk JWT dan data RBAC, yang disimpan dalam shared-library untuk fungsi reroute dan internal request

## Struktur Payload JWT / Custom Header

Payload JWT tambahan untuk mempermudah pencarian di sini alih-alih melakukan query ke database untuk informasi yang paling sering digunakan tersebut, informasi ini diteruskan sebagai header tambahan

```JSON
{
	"employee_id": "0032-03-27102025",
	"username": "aurelia_mara",
	"system_roles": {
		"it": "supervisor",
		"hris": "manager",
		"finance": "staff",
	}
}
```

Header ini digunakan untuk memeriksa route self-service dan juga untuk menetapkan metadata ke database pada saat pembuatan/modifikasi data

## Daftar Public Endpoint

*Akan didefinisikan per modul pada bagian berikutnya*