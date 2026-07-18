> **Status:** ✅ Terverifikasi end-to-end di localhost (16 Juli 2026) pada **dua keadaan awal**: (a) data **pra-sync** (453 kode lama) dan (b) replika keadaan **dev yang sudah menumpuk** (926 baris: kode lama + kode Accurate berdampingan). Keduanya menghasilkan 484 baris & 0 duplikat — termasuk **lewat UI**: klik tombol → dialog rencana → Database Master 987 → 546 tanpa reload halaman, lalu koreksi satuan/faktor via form edit. **DEV (10.10.10.121) SUDAH dijalankan 17 Juli 2026** via skrip curl-di-VM (langkah data per-environment + trio align + sync + saldo force): hasil akhir **488 bahan + 44 FG, 0 yatim, 0 tanpa-padanan, 0 satuan-perlu-dicek**. Temuan penting dari dev: salinan Accurate dev (858 item, sync live) lebih baru dari snapshot lokal 14 Juli (878) — **finance sedang bersih-bersih Accurate**: duplikat typo `PJB-13`/`PJB-013` (dua-duanya "Cadeo") sudah dihapus sisi typo-nya, `PJK-017` & 18 kode produk non-HPP ikut dihapus. Tindak lanjut finance: (a) HPP `product_costs` masih memakai `PJB-13` → betulkan ke `PJB-013`, sesudahnya cukup klik Sync HPP di WMS (align memindahkan otomatis, nama "Cadeo" unik); (b) konfirmasi `PJK-017` — masih di HPP tapi sudah tak di Accurate. **Prod belum** — wajib backup + ronde CEK + konfirmasi finance dulu.

> **Aman dijalankan walau master sudah terlanjur menumpuk** — align mengenali baris kanonik yang sudah dibuat sync dan tidak menjumlahkan stoknya (kode lama & kode Accurate menghitung barang fisik yang sama). Prinsip yang dipakai: **kuantitas ikut Accurate, atribut master (satuan/kategori/min_stok) ikut data terkurasi WMS** — satuan pada baris kanonik hasil sync cuma tebakan dari prefix, jadi tak boleh menggusur data gudang (prefix `BBO` menebak GRAM, padahal CANGKANG KAPSUL memang PCS).

> **Kenapa runbook ini ada:** penyelarasan kode bahan pertama kali dikerjakan sebagai skrip `mongosh` ad-hoc di satu mesin, jadi **tidak ikut ter-deploy**. Akibatnya di environment lain kode bahan masih mnemonik, dan menekan **Sync Master Bahan** menyisipkan kode Accurate di samping baris lama → **master menumpuk** (terukur: 453 → 926 baris, 441 di antaranya barang yang sama). Migrasinya kini jadi endpoint; urutan di bawah wajib diikuti.

## Tujuan

Menyelaraskan kode bahan WMS ([[Microservices - Manufacture Service]]) dari mnemonik internal (`PEGA`, `AMY`, `AC1000`) ke **kode item Accurate** (`BBO-030`, `BBK-001`), beserta seluruh rujukannya, supaya stok bahan bisa disinkronkan dari [[External - Accurate]].

## Kapan dipakai

- Environment baru / environment yang master bahannya masih memakai kode lama (dev, prod).
- Gejala: hasil `POST /master-bahan/sync-accurate` memuat `perlu_align` tidak kosong, atau master bahan terlihat dobel (satu bahan muncul dua kali: kode lama + kode Accurate — mis. `AC1000` **dan** `BBK-001` sama-sama "ACCARE 1000"). Contoh nyata di dev 16 Juli 2026: Database Master menampilkan **1021** item, padahal sehatnya **~544** (= ~482 bahan + 62 barang jadi). Kode **produk jadi** lama (NEI, FAY, …) punya masalah yang sama persis — bereskan dengan tombol **Sync Barang Jadi & Bundle dari HPP** (juga self-healing, dialognya sama; backend `POST /master-product/align-hpp`).

## Prasyarat

- Manufacture service sudah memuat endpoint `align-accurate` (lihat [[API - Manufacture Service]]).
- [[Microservices - Integration Service]] bisa dihubungi & `accurate_stocks` sudah terisi (endpoint `/accurate/stocks/list` mengembalikan data). Align **membaca** dari salinan lokal itu, tidak memanggil Accurate langsung.
- **Backup `manufacture_db` dulu** — align menulis ulang `_id` dan menghapus baris lama.

```
mongodump -u <user> -p <pass> --authenticationDatabase admin -d manufacture_db -o /tmp/bk
```

## Cara termudah: lewat UI (sejak FE `856067d2`)

Tombol **Sync Master Bahan (Accurate)** di WMS → Manajemen Stok → tab Sync Master kini **self-healing**: bila masih ada kode bahan lama, ia menampilkan rencananya di dialog konfirmasi (berapa dipindah/digabung/dibiarkan) → setelah disetujui menjalankan **align → sync master → sync stok** sekaligus. Batal = tidak terjadi apa-apa. Data dimuat ulang **otomatis** setelah sync (banner "Memuat data master…" tampil di tab Database Master) — tidak perlu reload halaman; dulu refresh pasca-sync menampilkan stok 0 & menghilangkan barang jadi tanpa indikator, sehingga data tampak "belum terbaca".

Tombol **Sync Barang Jadi & Bundle dari HPP** berperilaku sama untuk kode **produk jadi** lama (NEI, FAY, …): dialog rencana → align (`/master-product/align-hpp`) → sync-hpp. Tombol **Sync Stok** menawarkan pembersihan baris stok/saldo awal **yatim** (dialog merah — satu-satunya yang menghapus; `/stok/align`). Jalankan ketiganya (urutan bebas).

Penutup: bila saldo awal **bulan berjalan** masih berisi angka era sebelum Accurate (dipotret sebelum stok pindah sumber), jalankan `POST /saldo-awal/snapshot?force=true` sekali — membuang snapshot bulan ini lalu memotret ulang dari stok terkini. (Belum ada tombolnya; via API/curl.)

Sesudahnya, betulkan satuan yang dilaporkan di hasil sync (`satuan perlu dicek`) lewat **form edit item** di tab Database Master — kolom stok saat mode edit kini punya input **satuan** dan **faktor acc.** (pengali qty Accurate per-item): `BBK-101` → satuan GRAM + kategori BAHAN BAKU KOSMETIK; `BBO-056` → faktor `1000` (satuan tetap PCS). Lalu klik **Sync Stok** sekali lagi.

Prosedur API manual di bawah = fallback (bila FE belum ter-deploy) & untuk memahami mekaniknya.

## Urutan (jangan dibalik)

**1. Lihat rencananya dulu — jangan langsung apply.**

```
POST /api/manufacture/master-bahan/align-accurate?dry_run=true
```

Periksa hasilnya sebelum lanjut:

| Field | Arti |
|---|---|
| `akan_dipindah` | jumlah kode Accurate tujuan |
| `merge` | >1 kode lama menunjuk 1 kode Accurate (barang fisik yang terlanjur terpecah) — stok dijumlahkan |
| `tak_cocok_dibiarkan` | namanya tak cocok persis → **tetap kode lama**, tidak ditebak |
| `ambigu_dibiarkan` | 1 nama cocok ke >1 kode Accurate → dibiarkan |
| `rencana[]` | daftar `kode_lama → kode_baru` + nama |

Baca `rencana[]` sekilas: pastikan pasangannya masuk akal. Kalau ada yang janggal, **berhenti** dan tanyakan ke orang gudang — jangan apply.

**2. Apply.**

```
POST /api/manufacture/master-bahan/align-accurate
```

Memindahkan `_id` + cascade rujukan: `manufacture_stok`, `manufacture_saldo_awal_bulanan` (`_id` komposit `kode|YYYY-MM`), `manufacture_transaksi`, `manufacture_formula`, `manufacture_production_log`, `manufacture_material_order`, `manufacture_procurement_po`. Idempoten — aman diulang (`dipindah` jadi 0).

**3. Sync master bahan** (menarik bahan yang memang baru dari Accurate):

```
POST /api/manufacture/master-bahan/sync-accurate
```

`perlu_align` **harus kosong**. Kalau masih terisi, berarti langkah 1–2 belum jalan/gagal — jangan lanjut.

**4. Sync stok:**

```
POST /api/manufacture/stok/sync-accurate
```

**5. Betulkan satuan yang dilaporkan.** Cek `satuan_perlu_dicek` dari langkah 4 (satuan PCS tapi qty Accurate pecahan = satuan master salah, atau satuan Accurate-nya beda). Per 16 Juli 2026 ada dua, dan **keduanya beda penanganan**:

```
PUT /api/manufacture/master-bahan/BBK-101
{ "satuan": "GRAM", "kategori": "BAHAN BAKU KOSMETIK" }

PUT /api/manufacture/master-bahan/BBO-056
{ "faktor_stok_accurate": 1000 }
```

- `BBK-101` OAT EXTRACT: salah entri — semua ekstrak lain GRAM & kategori bahan baku.
- `BBO-056` CANGKANG KAPSUL: satuan PCS **sudah benar**; yang beda satuan Accurate-nya (**ribuan butir**) → pakai faktor per-item, **jangan** diubah jadi GRAM (angka MRP kebetulan benar, tapi kapsul jadi terhitung sebagai bahan curah bergram di dashboard — dan `satuan_perlu_dicek` ikut bisu, jadi salahnya tak akan ketahuan lagi).

Lalu ulangi langkah 4; `satuan_perlu_dicek` harus kosong.

## Verifikasi

```
// 0 = tak ada bahan yang muncul di >1 kode (inti masalah "menumpuk")
const byName = {};
db.manufacture_master_bahan.find({}, {nama:1}).forEach(d => {
  const n = (d.nama||"").toUpperCase().replace(/[^A-Z0-9 ]/g," ").replace(/\s+/g," ").trim();
  (byName[n] = byName[n] || []).push(d._id);
});
print(Object.values(byName).filter(v => v.length > 1).length);

// rujukan formula menggantung — hanya "#N/A" yang wajar (error di file NEW FORMULA sumber)
const mb = new Set(db.manufacture_master_bahan.distinct("_id"));
const dangling = new Set();
db.manufacture_formula.find().forEach(f => (f.ingredients||[]).forEach(i => {
  if (!mb.has(i.kode_bahan)) dangling.add(i.kode_bahan);
}));
print(JSON.stringify([...dangling]));
```

Hasil di localhost sbg pembanding: **484** baris master bahan, **0** duplikat, **8** kode lama tersisa (sengaja), rujukan menggantung hanya `#N/A`.

## Yang sengaja TIDAK diselaraskan

Kode-kode ini namanya tak cocok persis dan **butuh konfirmasi orang gudang** — jangan ditebak, fuzzy match pernah memilih **"PLASTIK SHRINK 19 CM" untuk "PLASTIK SRING 9 CM"** dan **20 CM untuk 10/12 CM**:

| Kode lama | Nama | Kendala | Status |
|---|---|---|---|
| `SLG` | SILICA GEL | Accurate salah ketik: `PP-036 SILLICA GEL` | ✅ **selesai di localhost 16 Juli 2026** — user konfirmasi stok WMS 6.767.876 = data test, angka real di Accurate (46). Caranya: rename nama WMS → `SILLICA GEL` (samakan dgn Accurate) → align memindahkannya (`PP-036`, alias `SLG`, 22 formula ikut). **Di dev harus diulang** (rename = data per-environment): edit nama via UI → klik Sync Master Bahan |
| `PS SRK 7/8/9/10/12 CM` | PLASTIK SRING … | Accurate punya varian ukuran+merek (`PP-021`…`PP-039`), tak terputuskan otomatis | ✅ **selesai via kebijakan user 16 Juli 2026**: "jangan pedulikan data lama, semuanya ngikut stok Accurate" — pemetaan identitas jadi tak perlu. 5 baris lama **dihapus** (0 rujukan formula; 3 transaksi OPENING era sheet ikut dihapus agar `/stok/reconcile` tak menghidupkan angka lama), lalu **11 varian PLASTIK SHRINK Accurate didaftarkan** sbg master baru (`PP-012/021/022/023/024/025/028/030/039/072/073`, satuan ROL, kategori UMUM) → sync mengisi stoknya. `bahan_tanpa_padanan_accurate` kini **kosong**. **Di dev harus diulang** (data per-environment; hapus transaksi OPENING butuh mongosh — tak ada UI-nya) |
| `RF150` | BOTOL VIVIDENT (150 ML) | ternyata BUKAN "tak ada di Accurate" — WMS menamai botol menurut pemakaiannya, Accurate menurut jenisnya | ✅ **selesai di localhost 16 Juli 2026** — user konfirmasi = `BKK-015 BOTOL RF 150 ML TUTUP ULIR PUTIH`; merge via rename nama → align (alias `RF150`, 3 formula + 2 transaksi ikut, stok pakai Accurate 7.884). **Di dev harus diulang** |
| `TEST-01` | Barang TESTING | data testing | ✅ **dihapus** (localhost, konfirmasi user; 0 rujukan). **Di dev hapus juga** via tombol hapus di Database Master |

Setelah dikonfirmasi, cukup tambahkan kode lama ke `aliases` baris kanoniknya (atau betulkan namanya agar cocok persis dgn Accurate — cara SLG), lalu jalankan ulang align/klik Sync Master Bahan.

> **Update 18 Juli 2026:** langkah registrasi manual varian PP- TIDAK diperlukan lagi di environment baru — sync kini punya daftar kurasi `bahanNonPrefix` (15 kode PP- bahan) di `sync_hpp.go`, jadi tombol sync sendiri sudah menggenapkan 532. Bagian pendaftaran manual di atas tinggal relevan sebagai sejarah.

Catatan: duplikat di sisi Accurate (`PP-025` & `PP-028` bernama persis sama "PLASTIK SHRINK NEI - 7 CM") ikut termirror ke WMS — itu data finance untuk dibereskan di Accurate; begitu di-merge di sana, sisi WMS tinggal menghapus baris matinya.

## Dokumen Terkait

- [[Microservices - Manufacture Service]] · [[API - Manufacture Service]] · [[Manufacture - Stock & Material Management]]
- [[External - Accurate]] · [[RUN - Accurate API Access Token (OAuth)]] · [[ADR - 0001 Akuntansi via Accurate]]
