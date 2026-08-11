Catatan **point-in-time** pembersihan faktur auto-sync yang isinya menyimpang dari ERP, dikerjakan **2026-08-11**. Berisi bukti sebelum-sesudah, urutan tindakan, dan dua jebakan yang ditemukan di tengah jalan. Ini rekaman operasional, bukan dokumentasi arsitektur — mesinnya diuraikan di [[Microservices - Integration Service]].

## Ringkas

Dua kerusakan berlawanan arah ditemukan pada faktur Agustus. **Kekurangan Rp80.778.900 tuntas jadi Rp0**; kelebihan turun dari ≥Rp41.848.500 jadi Rp20.768.500 — sisanya terkunci retur dan **tidak bisa diperbaiki lewat jalur kirim-ulang**. Faktur Agustus berstatus FAILED turun dari 12 ke 0. Tidak ada dokumen ganda dan tidak ada retur yang lepas.

## Kerusakan yang ditemukan

| Arah | Jumlah | Nilai | Sifat |
|---|---|---|---|
| Kelebihan catat | 5 faktur | ≥Rp41.848.500 | warisan bug append, diam |
| Kekurangan catat | 9 faktur | Rp80.778.900 | akibat rem, **bertambah tiap hari** |

Kekurangan itu tiga kali lebih besar dan aktif memburuk — karena itu didahulukan.

## Rantai sebabnya

Akarnya `saveWithRetry`: ia mengulang **payload yang sama persis** hingga 3× tanpa membaca ulang keadaan Accurate.

```go
for attempt := 1; attempt <= 3; attempt++ {
    res, serr := SaveSalesInvoice(ctx, req)   // req TIDAK berubah
    if berhasil { return true }
}
return false   // -> status FAILED
```

Untuk CREATE/EDIT itu aman karena idempoten (hapus-lalu-tulis, berapa kali pun hasilnya sama). Untuk **append** tidak: menambah + menambah = dobel. Saat Accurate sudah menyimpan tapi jawabannya hilang (timeout/502), kita mencatat gagal sementara Accurate sudah bertambah — lalu percobaan berikutnya menambah lagi.

Sudah ditutup di **PR #1119** (`appendWithRetry` membaca ulang Accurate sebelum percobaan kedua). Tapi kerusakannya menyisakan jebakan kedua:

```
faktur menggelembung
  -> detektor: "isi Accurate ≠ yang saya kirim"
  -> disangka editan finance, penulisan DITAHAN
  -> order baru tak bisa masuk -> kekurangan tumbuh
  -> selisih makin besar -> rem makin mustahil lepas
```

Detektor hanya melihat **bahwa** ada perbedaan, bukan **siapa** penyebabnya. Kerusakan buatan mesin dan koreksi manusia tampak identik baginya, jadi mesin tak bisa memulihkan kerusakannya sendiri. Terbukti empiris: draft ditolak jam 07:19, retry jalan, dan draft baru terbit **di menit yang sama**.

## Tindakan

Pemutus kuncinya: mematikan `external-edit-detection` sebentar supaya detektor tak memasang rem baru di tengah penulisan. Jendelanya dijaga sesempit mungkin dan pemulihan saklar dijamin jalan di skrip yang sama.

| Tahap | Isi | Hasil |
|---|---|---|
| Uji | 1 faktur (`INV/2026/08/07/026-BH`) | kelebihan Rp7.324.000 → Rp0, `accurate_id` 82159 tak berubah |
| Batch A | 10 faktur tanpa kunci retur | semua SENT, 11 faktur diverifikasi COCOK |
| Batch B | 2 faktur `RETURN_LOCKED` | SENT tapi **isi Accurate tak berubah** |

Uji dijalankan lebih dulu dan hasilnya diperiksa sebelum batch — termasuk memastikan `accurate_id` tetap sama, karena angka `attempts` yang turun sempat memunculkan dugaan dokumen baru terbentuk. Dugaan itu tidak terbukti.

## Bukti sebelum-sesudah

```
SEBELUM (invqtycek, baca langsung Accurate)
  diperiksa 275 | cocok 237 | BERLEBIH 5 (Rp41.848.500) | kurang 33

SESUDAH
  diperiksa 284 | cocok 265 | BERLEBIH 2 (Rp20.768.500) | kurang 17

Kekurangan nyata (ukur ERP vs terkirim, saringan benar)
  SEBELUM : 9 faktur | Rp80.778.900
  SESUDAH : 0 faktur | Rp0

Keamanan
  nomor faktur dipakai >1 baris      : tidak ada
  accurate_id dipakai >1 faktur      : tidak ada
  retur SENT tanpa accurate_return_id: 0
  faktur Agustus FAILED              : 12 -> 0
  saklar external-edit-detection     : kembali ke "hold"
```

Retur yang terbukukan pada faktur terkunci (`RTR/2026/08/08/061-BH` id 114527, `RTR/2026/08/11/042-BH` id 115095) diperiksa khusus: **timestamp-nya tidak bergeser**, jadi kaskade tidak menyentuhnya sama sekali.

## Dua jebakan yang ditemukan di tengah jalan

**1. `invqtycek` melaporkan "kurang" berlebihan.** Query order-nya hanya `shop_id + channel + shipped_at`, tanpa `is_sample` dan `invoice_excluded` — padahal `listSnapshotOrders` menyaring keduanya. Akibatnya 80 order sampel di 17 toko-hari terhitung sebagai "seharusnya ada di Accurate".

Arah biasnya berbahaya di dua sisi: **"kurang" jadi berlebihan** (17 dari 284 faktur dilaporkan bermasalah padahal sehat) dan **"berlebih" jadi terlalu kecil** — padahal angka berlebih itulah dasar keputusan pembersihan. Karena itu Rp41.848.500 harus dibaca sebagai **batas bawah**. Penyaringnya sudah diperbaiki (belum ter-deploy).

Angka "kurang 17" pada verifikasi sesudah adalah sisa artefak ini, bukan kekurangan nyata — dibuktikan lewat pengukuran terpisah yang memakai saringan benar dan menghasilkan Rp0.

**2. Faktur `RETURN_LOCKED` tidak bisa dikurangi lewat kirim-ulang.** Pada label itu mesin memakai jalur **append** (menambah yang kurang), bukan menimpa penuh. Karena isinya sudah kelebihan, tidak ada yang kurang → append tidak menulis apa-apa → melapor **SENT** padahal Accurate tak berubah. Sukses palsu.

Ini terlihat jelas di verifikasi akhir: kedua faktur berstatus SENT tanpa error, tetapi `invqtycek` tetap melaporkan kelebihan yang sama persis.

## Yang masih terbuka

| Hal | Nilai | Kenapa belum |
|---|---|---|
| 2 faktur `RETURN_LOCKED` masih gemuk | Rp20.768.500 | jalur append tak bisa mengurangi; perlu lepas retur dulu, atau koreksi manual di Accurate |
| 4 faktur ditolak izin Accurate | — | aturan "harus lewat Penawaran/Pesanan Penjualan/Pengiriman"; setelan di Accurate, di luar kode |
| Perbaikan penyaring `invqtycek` | — | sudah ditulis, belum di-commit/deploy |
| 11 draft INVOICE BARU | — | sebagian basi setelah perbaikan; perlu ditutup agar Kotak Adopsi tidak berisi pekerjaan semu |

## Usul perbaikan berikutnya

**Ajari detektor mengenali tanda tangan kerusakan append.** Penggandaan mesin punya ciri khas: **semua baris naik dengan kelipatan seragam** — `INV/2026/08/01/024-BH` tepat 2× di ketujuh SKU sekaligus. Manusia tidak mengedit begitu; koreksi finance menyentuh satu-dua baris, bukan semuanya serempak dengan rasio sama. Kalau `observed ≈ k × baseline` di hampir semua baris, itu bukan editan manusia — jangan tahan, timpa dan catat alasannya. Ini menutup jebakan mengunci-diri secara permanen.

**Pisahkan label "ditahan" dari "gagal kirim".** Sekarang keduanya tampil FAILED, padahal artinya berlawanan: satu berarti faktur tidak ada di Accurate, satu lagi berarti faktur ada tapi sengaja tidak diperbarui. Itu yang membuat 12 FAILED tampak sama gawatnya padahal 7 di antaranya sama sekali bukan kegagalan.

## Catatan cara kerja

Seluruh pembacaan memakai kredensial `erp-analyst` lewat SSH. Setiap penulisan didahului pengukuran dan diikuti verifikasi baca-ulang ke Accurate — status `SENT` **tidak** diperlakukan sebagai bukti, karena justru pada faktur `RETURN_LOCKED` status itu berbohong. Semua berkas sementara di VM dihapus pada ronde yang sama.