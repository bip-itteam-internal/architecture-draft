# Latar Belakang
Terdapat sebuah sistem untuk mengelola customer dari Tiktok di Dashboard ini: [monitoring.hubcrm.bharatainternasional.com](https://monitoring.hubcrm.bharatainternasional.com/)


# Permasalahan
1. Banyak nomor telepon, alamat, dan nama yang tersensor. Data-data ini berasal dari vendor (Semarang)
2. Terdapat masalah pada blasting. Sesekali nomor Whatsapp menjadi suspended setelah mengirim pesan blasting ke 30+ nomor

# Kemungkinan solusi
1. Kolaborasi dengan vendor. memungkinkan untuk berbagi source code
2. Membuat tool kecil untuk blasting nomor berdasarkan aturan:
	1. Percakapan "Warming up". (Membuat 2 atau lebih percakapan dengan nomor kita sendiri untuk mensimulasikan percakapan manusia yang nyata)
	2. Setelah warming up, jangan kirim pesan secara bulk dalam satu waktu. pisahkan dalam interval acak. sebagai contoh kirim 1 pesan ke 1 nomor pada 08.00, pesan berikutnya pada 08.01, atau rentang waktu acak