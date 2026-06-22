## Deskripsi

*Dashboard ini mencantumkan semua barang yang disimpan di warehouse secara detail sehingga semuanya terorganisir dan mudah dilacak*

[Contoh dari sistem ini](https://docs.google.com/spreadsheets/d/12L5OKViT2LnQECT6ldUBkjK-xablpcZO/edit?gid=1015075572#gid=1015075572)

## Fitur

- Dashboard
	- Ikhtisar tentang semua hal yang disimpan di warehouse
- Lihat dan cari
	- Untuk melacak jumlah barang dan penempatannya di dalam warehouse
- Pembuatan entri Stock Keeping Unit baru dan barcode
	- Ini diperlukan karena barang baru pada akhirnya akan datang ke warehouse dan harus dilacak dengan benar

## Detail yang Tertunda

- [ ] Siapa yang bertanggung jawab atas sistem ini?
- [ ] Apakah warehouse sendiri dapat menjalankan dispatch order? Ini mungkin diperlukan jika kita memiliki 2 atau lebih warehouse untuk mengirim barang bolak-balik untuk pengorganisasian atau hal lainnya
- [ ] Apakah kita akan mengimplementasikan dispatch order? Sehingga order dari departemen Finance dapat langsung dijalankan dari sistem?
- [ ] Bagaimana request inbound dari sistem lain ditempatkan atau diproses?
- [ ] Bagaimana request outbound dari sistem lain ditempatkan atau diproses?

## Kebutuhan

- [ ] Master data karyawan (cari referensi, ini akan digunakan untuk menghubungkan entri mana yang dibuat oleh siapa)

## Dependencies

- [ ] Sistem logging
	- [ ] [[WH - Inbound (Receiving)]]
	- [ ] [[WH - Outbound (Sending)]]
- [ ] Sistem lain yang dapat melakukan request ke sistem ini