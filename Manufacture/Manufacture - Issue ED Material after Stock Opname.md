## Deskripsi

*Issue produksi: **stok material ED/rusak tercampur dengan stok bagus** di Accurate sehingga angka rancu. Accurate belum bisa memilah ED ke wadah lain; perlu dashboard stock opname (selisih + karantina + berita acara/foto, tanpa mengubah stok asli). Dijawab oleh [[Manufacture - Stock & Material Management]] (fitur Stock opname & gudang karantina).*

- **Status**: 🟡 Issue / Direncanakan (belum ada solusi di kode)

Departemen ini menggunakan Accurate Online untuk mengelola produksi dan raw material.

## Stok material yang ED atau wasted

```
Terkait manufaktur
Daftar laporan -> Tarikan data kuatitas barang per gudang
dari data yang tertera, ditampilkan stok material. material ini masih tercampur dengan stok yang sudah ED atau rusak. sehingga membuat rancu
pertanyaan:
1. apakah ada fasilitas di accurate untuk memilah stok yang sudah ED atau rusak ke wadah lain? sehingga stok yang tertera sudah clean. jawaban: setelah berkonsultasi dengan pihak Accurate, fasilitas ini belum ada
   
2. dari selisih atau perbedaan angka ini, apakah bisa dibuktikan bahwa stok ini selisih? jawab: salah satu bukti material itu rusak bisa menggunakan foto dan berita acara yang ditanda tangai pihak terkait
   
3. buat dokumen resmi yang ditanda tangani pihak stackholder yang menunjukan bahwa selisih stok ini sebenar-benarnya dan dilampirkan foto. jawaban: dibutuhkan dashboard khusus untuk stock opname
   
4. jangan rubah langsung stok yang sudah ada, cukup tampilkan berapa nilai selisihnya, alasan selisih, dan nomor serinya. jawaban: dashboard khusus bisa menjadi solusi
```

Alur yang disarankan:
![[Stok Pengecekan Fisik Flow.png]]

## Dokumen Terkait

- [[Manufacture - Stock & Material Management]] — sistem yang menjawab issue ini (Stock opname & karantina)
- [[Manufacture - Issue Material Miss Count]]
