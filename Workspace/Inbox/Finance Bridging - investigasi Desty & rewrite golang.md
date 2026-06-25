---
publish: false
---

> **Naik-kelas dari:** [[Finance - Bridging App]] · **Dipindah:** 2026-06-25 · investigasi rewrite Golang + pertimbangan Desty (eksplorasi, belum diputuskan).

## issue Finance: 
1. insentive [[Finance - Incentive]]
2. rewrite ke golang
3. platform integration (Tiktok, Shopee, Lazada dan Kiriminaja)
solusi: bisa menggunakan Desty namun belum dicoba

solusi:
A.  pelajari Desty dari Mekari. bandingkan dengan sistem finance internal.
    Desty omni channel:
    * menjadi admin toko
    * mengatur pesanan
    * mengatur pengiriman
    * mengatur pengembalian
    * mengatur gudang
    * mengatur inventori
    * mengatur promosi
    * mengatur produk
    * reporting
    * pengaturan toko
    * pengaturan pelanggan (censored)

    pertimbangkan migrasi. jawab pertanyaan berikut:
    1.  Tiktok: sales, income, return.
        a.  Sync sales dari toko? ✔️
            *   di internal, sync sales menggunakan mekanisme upload
                mekanisme upload sales, sync sales dan sync accurate
                1.  upload sales: import file excel ke sistem.
                    solusi: bisa diintegrasikan langsung ke Tiktok API
                2.  sync sales: kenapa harus sync sales?
                    solusi: karena kebutuhan finance adalah daily
                3.  sync accurate: kenapa menggunakan date range?
                    solusi: karena kebutuhan. 
                    untuk mengantisipasi sync accurate yang gagal. 
                    bisa disimpan di tempat khusus tanpa menghambat 
                    sales yang berhasil.

            *   di desty, sync otomatis. tidak hanya sales, tapi pengambalian dan income (mekari journal)

        b.  Informasi sales apa saja yang diambil dari Tiktok ke Desty?
            * sama seperti di sistem internal:
              1.  No. Pesanan
              2.  Nama toko
              3.  Metode pembayaran
              4.  Customer (Nama, Telepon, Alamat, Email)
              5.  Tanggal Pesanan
              6.  Kirim sebelum
              7.  Status (Semua pesanan, belum dibayar, pesanan baru, 
	              siap dikirim, dikirim, selesai, pembatalan, pengembalian)
              8.  Kurir
              9.  Nomor Resi
              10. Produk: Nama produk, SKU, Variant, Qty, Harga satuan, 
	              harga dibayar, subtotal, 
                  refund, diskon penjual, dll
              11. Riwayat pesanan. misal: Sedang diproses, Dikirim, Sampai

        c.  sync income dari toko? ada di mekari journal. (perlu investigasi)
            Income di Mekari journal masuk dalam fitur akuntan, perlu login

        e.  sync retur (pengembalian)
            1.  Di Desty.app, retur langsung sync secara API ke Tiktok
            2.  ada 3 macam: Retur, Refund, dan Penggantian
            3.  Masing-masing tipe retur, ada 5 Status: Pending, Diproses, 
		        Dalam Sengketa, Selesai, Dibatalkan
