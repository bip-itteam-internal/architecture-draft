## Pemberitahuan

*Semua yang ada di sini hanyalah ikhtisar singkat dan gambaran kasar tentang bagaimana sistem terlihat serta bagaimana setiap bagian berinteraksi satu sama lain, hal ini memerlukan diskusi terbuka lebih lanjut bersama-sama*

## Seperti apa sistem ERP itu?

Saat ini semuanya masih berada dalam satu mono repository, ini akan dipindahkan dengan git submodules ke depannya ketika dirasa sudah tepat

Interaksi antar service dapat diinterpretasikan seperti gambar di bawah ini
![[erp-request-nutshell.png]]

### Apa yang dilakukan API Gateway?

Ini adalah entry point untuk request, yang juga menangani JWT authentication dan pengecekan propagasi routes untuk open/restricted routes

### Penjelasan tentang struktur routes API Gateway

Secara default API Gateway tidak memiliki routes-nya sendiri, dan hanya meneruskan request ke internal services sesuai kebutuhan *(dengan pengecualian authentication karena akan diproses lebih lanjut oleh API Gateway itu sendiri untuk pembuatan JWT)*

![[api-gateway-routes.png]]

Daftar struktur routes (detail lengkap):
- **/public** - Singkatan dari public routes, yang dapat diakses secara bebas oleh siapa saja
- **/health** - Ini adalah pengecekan heartbeat untuk services yang akan selalu di-resolve ke `/api/:service/` dan mengirimkan kembali informasinya
- **/api** - Singkatan dari panggilan api normal, ini akan memanggil internal services dengan syarat JWT authentication dan/atau `access-key` unik jika di-request ke salah satu open route services *(penjelasan lebih lanjut dapat dibaca di bawah)*
- **/auth** - Singkatan dari authentication, route ini akan selalu memanggil ke `/api/employee` di balik layar dan mengambil data employee lalu menandatanganinya dengan JWT pada API Gateway
- **/ext** - Singkatan dari extension atau external routes, dengan akses langsung (tanpa JWT authentication) ke services atau webhooks *(saat ini banyak dimanfaatkan untuk integrasi fingerprint)*
- **/onboarding** - Digunakan untuk akses publik (minimal) informasi dan panggilan/pengecekan fungsi helper untuk onboarding melalui aplikasi mobile 
- **/debug** dan **/dev** - Masing-masing adalah debug dan development routes, hanya tersedia pada environment dev/staging

### Apa yang dilakukan Orchestrator?

Orchestrator pada dasarnya adalah wrapper kita untuk aksi berbasis event, sebagai contoh beberapa request mungkin memerlukan pemanggilan 2 service yang berbeda, sistem ini akan melakukannya untuk Anda dalam memproses data yang dibutuhkan untuk hal tersebut

Orchestrator yang saat ini kita miliki adalah: **HRIS** dan **IT**

### Apa yang dilakukan Service?

Service adalah end-point yang berinteraksi dan terhubung dengan database-nya masing-masing, ini memastikan kemudahan dalam mengembangkan service tertentu, dan jika ternyata rusak tidak masalah, karena hanya service tersebut yang terpengaruh

Kita memiliki 2 tipe services:
- **Open route services** - request dapat dibuat dari luar dan memerlukan access/service keys, jika keys tidak disediakan maka akan fallback menggunakan JWT authentication
- **Restricted services** - request harus divalidasi menggunakan JWT authentication

## Tipe Request

Terdapat total 3 tipe request untuk sistem ERP, yang juga diberi nomor, dijelaskan di bawah ini:

1. **Direct request ke services** - Di mana Anda me-request sesuatu langsung ke services, contoh `/api/employee/status` atau `/api/file/preview`

2. **Request ke orchestrator** - Di mana Anda me-request ke orchestrator untuk melakukan aksi bisnis ke berbagai sistem, contoh `/api/hris/employee/create` di mana ia akan membuat data employee tersebut ke `employee-service` dan mengunggah file ke `file-service` serta memperbarui jadwal terbaru ke `attendance-service`

3. **Direct request ke services yang bergantung pada service lain** - Ini mulai memasuki wilayah berbahaya, di mana aksinya samar dan tidak jelas karena itu merupakan panggilan internal service-to-service. Ini tidak masalah selama bukan hal kritis, contoh `/api/attendance/team-today?department=X` akan mengambil data employees berdasarkan department ke `/api/employee-list` dan menggunakan informasi tersebut untuk mendapatkan entri terbaru attendance employee department tersebut. **Jika Anda membuat request seperti ini dan alurnya membingungkan maka itu berarti sudah waktunya memindahkannya ke orchestrator**

## Sekilas tentang struktur Repository

Di bawah ini adalah sekilas tentang code repository beserta catatannya

```
├── .env (Everything in here, need to sort this out)
├── docker-compose.yml (Main entry point and duct tape for all services)
├── Makefile (Shorten common commands, ask Pero about this)
│
├── api-gateway (Manages authenticcation and routes to existing services)
│
├── orchestrator (Manages request for multiple services at once)
│   ├── hris
│   └── it
│
├── services (ERP services, some are restricted other are open)
│   ├── attendance (Restricted)
│   ├── employee (Restricted)
│   ├── file (Open-routes and restricted)
│   └── notification (Open-routes and restricted)
│
└── shared-library (All things point into shared-library to not declare something twice, this is out duct tape for all the services. Need to move this into proper go include if needed)
    │
	├── auth (JWT authentication)
    ├── database (Currently exclusive to MongoDB)
    ├── routes (Handles gateway and internal routing)
    │
    ├── common (Common stuff for model, function and others that being ref often)
    │   ├── env.go
    │   ├── header.go
    │   ├── metadata.go
    │   ├── response.go
    │   ├── roles.go
    │   └── struct.go
    │
    ├── models (Models declaration for all services)
    │   ├── attendance
    │   ├── employee
    │   ├── inventory
    │   └── notification
    │
    ├── notification (WhatsApp and FCM library)
    ├── minio (File server)
    ├── logs
    └── validation
```

## Dari mana saya mulai?

Sebelum memulai disarankan untuk membiasakan diri dengan file-file shared-library, api gateway, lalu ke file-file boilerplate services/orchestrator

Untuk mulai membuat service baru Anda dapat melakukan hal berikut:
1. Buat folder baru untuk service Anda
2. Jalankan `go mod init 'service-name'` di dalam folder baru tersebut
3. Sesuaikan command ini agar cocok dengan path Anda untuk menautkan shared-library ke service baru Anda `go mod edit -replace github.com/bharata/shared-library=../../shared-library` dan setelah itu jalankan `go get github.com/bharata/shared-library@v0.0.0`
4. (Salin template dari service lain) Buat `main.go` untuk service Anda
5. (Salin template dari service lain) Buat `dockerfile` untuk service Anda
6. (Salin template dari service lain) Edit `docker-compose.yml`, dengan hal-hal yang diperlukan untuk service Anda
7. Tambahkan service-module-url Anda ke `api-gateway/main.go` pada hashmap `InternalURL`
8. Tambahkan variabel baru jika Anda membuatnya ke `.env`

Aksi-aksi di atas dapat diotomatisasi menggunakan shell script, tetapi untuk saat ini kita belum memilikinya maupun template boilerplate apa pun, jadi semuanya masih manual untuk sekarang

## TODO

1. Pisahkan ini menjadi git submodules, atau bahkan jadikan saja sebagai repository terpisah
2. Lupakan saja sharing shared-library dan cukup push sebagai repository standalone di mana kita dapat menyertakannya dengan mudah ke setiap services
3. Pisahkan docker-compose dan env variables ke setiap services secara benar dengan slice-nya masing-masing




## Menggunakan authentication ERP yang sudah ada untuk aplikasi eksternal

Terkadang kita tidak dapat membangun di atas ERP karena adanya batasan atau kita memiliki prototype standalone yang ingin kita bagikan secara langsung tetapi membutuhkan authentication

Oleh karena itu Anda dapat menggunakan authentication yang sudah ada pada ERP untuk aplikasi eksternal Anda seperti di bawah ini, cukup panggil fungsinya lalu simpan sebagai header untuk JWT, dan validasi setiap akses halaman sesuai kebutuhan

Sequence diagram ditampilkan di bawah ini

![[erp-external-auth-use-case.svg]]
