**Status**: ⚠️ **Implemented (ada catatan)** — kode selesai & ber-tes, bip-erp branch `feat/accurate-item-rename-auto-migrasi` (commit `71786d88`+`3674ba98`+`28cc5cfb`), **PR belum dibuka**. Asumsi kunci (id internal Accurate stabil lintas rename) belum diverifikasi empiris — lihat "Belum selesai".

# ADR - 0088 Auto-Migrasi Padanan Perlengkapan Lewat ID Internal Accurate, Bukan Konfirmasi Manusia

Saat Accurate mengganti nomor item perlengkapan, sistem kini memindahkan padanan `accurate_item_no` unit ERP + menghapus baris stok lama **secara otomatis**, tanpa tombol konfirmasi manusia — menyimpang sadar dari pola [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]].

## Context

- Bug ditemukan dari layar: barang fisik yang SAMA (Charger Baterai Kamera Sony) tampil **dobel** di explorer Perlengkapan — nomor lama `100205` berstatus "Cocok 1/1", nomor baru `PK-057` berstatus "Belum Ada Padanan 0/1", nama+qty+Total Biaya identik.
- Root cause: `BulkUpsert` (`accurate_stock_repo.go`) cuma insert/update by `item_no` per batch sync jam-jaman, **tak pernah menghapus** `item_no` yang hilang dari katalog. Saat Accurate rename nomor item, baris lama jadi yatim permanen sementara padanan ERP (`inventory.accurate_item_no`) masih menunjuk nomor lama.
- Preseden yang ada untuk kelas masalah "salinan Accurate bisa drift": [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]] — scanner **read-only** melapor, manusia menekan tombol "Segarkan". Preseden itu **tidak** langsung dipakai di sini karena sinyalnya beda kelas:
  - ADR-0066 (retur): sinyal pembanding cuma **total angka** dari `list.do` — heuristik, ambigu (total sama belum tentu dokumen sama), sehingga wajar menuntut mata manusia sebelum bertindak.
  - Kasus ini (perlengkapan): Accurate `list-stock.do` sudah mengirim **id internal per item** (`ItemStockRow.AccurateID`, mis. Charger = `9302`) — sudah diparsing sejak fitur Total Biaya (untuk `item/detail.do?id=`) tapi dibuang sesudah dipakai, tak pernah dipersist. Id ini **seharusnya** tetap sama walau `item_no` diganti, karena rename di Accurate mengedit satu kolom kode, bukan menghapus lalu membuat ulang barangnya.
- Keputusan eksplisit GA (bukan saran default sistem): staf **tidak boleh kerja dua kali** (unpair manual + pair manual) untuk kasus yang sinyalnya sudah pasti. Pola "Ganti ke saran" yang ada untuk aset tetap (`padananMencurigakan`, non-destruktif, satu klik) sengaja **tidak** dipakai/ditiru di sini — GA memilih otomatisasi penuh untuk kelas kasus ini.
- Ownership: `inventory.accurate_item_no` sebelumnya HANYA ditulis staf lewat `PATCH /item/:id` ([[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]]). Menambah penulis kedua otomatis adalah keputusan yang wajib ADR per [[REF - Kepemilikan Data]] aturan #4 — inilah ADR itu.

## Decision

**1. Persist `AccurateID`.** `entity.AccurateStock` dapat field `accurate_id` (int64, `omitempty` — baris pra-fitur tetap sah bernilai 0/kosong). Diisi `BulkUpsert` dari `ItemStockRow.AccurateID` tiap sync jam-jaman.

**2. Deteksi hilang dengan masa tenggang, bukan seketika.** Field `missing_since *time.Time` disetel (`MarkMissingExcept`) untuk `item_no` yang absen dari batch sync TERKINI, **hanya bila run itu menarik SELURUH katalog dengan sukses** (bukan batch parsial akibat galat di tengah paginasi, dan bukan batch kosong akibat anomali — keduanya dijaga eksplisit di kode). Baris yang kembali terlihat (lewat `BulkUpsert` sync jam-jaman **atau** `UpsertQty` webhook push — keduanya sinyal "masih hidup di Accurate") langsung di-`$unset`. Ambang tenggang **3 jam** (~3 siklus sync jam-jaman) sebelum "hilang" dianggap "berganti nomor" bukan "sesaat tak sinkron".

**3. Cocokkan lewat `AccurateID`, TEPAT SATU kandidat atau diam.** `pilihPadananRename` (fungsi murni): baris stale (lolos tenggang) dicocokkan ke item_no baru di batch TERKINI yang berbagi `accurate_id` sama. **0 kandidat, >1 kandidat (ambigu), atau `accurate_id`=0** (tak ada sinyal) — SENGAJA tidak ditindak. Prinsipnya: diam-diam tak pernah menyala jauh lebih aman daripada sekali salah memindahkan padanan staf yang sudah benar.

**4. Pindahkan padanan lewat endpoint pemilik, bukan tulis silang database.** Integration-service **tidak** menulis langsung ke koleksi `inventory` milik inventory-service (melanggar [[REF - Kepemilikan Data]] aturan #2). Sebagai gantinya: `POST /internal/perlengkapan/ganti-padanan` (inventory-service, gate `gateRobotInternal()` — pola sama dengan `/internal/stok-dari-pengajuan`/`/internal/ga-stok/kurangi`), dipanggil lewat `shared-library/routes.InternalRequest` + `BIP-Gateway-ID`, **tanpa** `fiber.Ctx` (jalur cron/background murni, bukan permintaan manusia lewat gateway — pola sama dengan insentive→inventory). `UpdateMany` pada `accurate_item_no`, idempoten alami (panggilan ulang sesudah migrasi pertama membalas `dipindahkan=0`).

**5. Audit trail wajib.** Koleksi baru `accurate_item_renames` (integration-service) mencatat tiap migrasi sukses: item_no lama+baru, `accurate_id`, nama, jumlah unit ERP yang ikut dipindah, waktu. Aksi yang tadinya cuma staf yang lakukan manual kini butuh jejak yang bisa ditelusuri.

**6. Hapus baris lama HANYA sesudah repoint terbukti berhasil.** `DeleteByItemNo` dipanggil di akhir rantai (repoint → audit → hapus); gagal di langkah mana pun berhenti TANPA melanjutkan, dan `missing_since` yang belum "dituntaskan" otomatis membuat run berikutnya mencoba lagi (retry alami, tanpa mekanisme retry terpisah).

**7. Kriteria kapan boleh menyimpang dari pola ADR-0066.** Bukan aturan sekali-pakai — kriteria yang dipakai di sini, untuk dipakai ulang bila kasus serupa muncul: (a) ada sinyal identitas **stabil** dari sumbernya sendiri (bukan diturunkan/ditebak dari atribut yang bisa kebetulan sama), (b) pencocokan mensyaratkan **tepat satu** kandidat — nol atau banyak kandidat berarti diam, (c) aksinya **idempoten** dan **fail-safe ke arah tidak-bertindak** (salah asumsi = fitur tak pernah menyala, bukan fitur salah bertindak), (d) ada audit trail. Tanpa keempatnya, kembali ke pola scanner+manusia ADR-0066.

**8. Penulis kedua `accurate_item_no` — dicatat, bukan disembunyikan.** [[REF - Kepemilikan Data]] diperbarui: baris "Aset dan perlengkapan GA" kini menyebut integration-service sebagai penulis kedua khusus field ini, menunjuk ADR ini.

## Consequences

- **Staf GA tidak perlu memasangkan ulang** setelah Accurate rename nomor item perlengkapan — baris dobel yang tadinya harus disadari manual (lihat "Alur Pengguna" di rencana `.task-plans/2026-09-12-accurate-item-rename-auto-migrasi.md`) kini hilang sendiri dalam ≤3 jam, tanpa aksi apa pun.
- **Gagal-aman by design**: kalaupun asumsi "AccurateID stabil lintas rename" ternyata SALAH (belum diverifikasi empiris — lihat "Belum selesai"), akibatnya `pilihPadananRename` selalu `ok=false` — fitur ini cuma **tidak pernah menyala**, bukan salah memindahkan padanan siapa pun.
- **Item yang genuinely terhapus di Accurate** (bukan rename — nol `accurate_id` match sama sekali) TETAP jadi baris stale selamanya, seperti hari ini. Tak ada sinyal untuk membedakan "sengaja dihapus, riwayatnya masih dibutuhkan" dari "beneran usang". Kandidat scanner ala ADR-0066 di masa depan bila ini jadi masalah nyata — bukan bagian ADR ini.
- **Kandidat ambigu** (>1 item baru berbagi `accurate_id` — nyaris mustahil karena id Accurate unik per item) juga tak ditindak otomatis, cuma ter-log. Tak ada UI penanda untuk kasus ini; diterima sebagai limitasi sadar mengingat kelangkaannya.
- `reconciled_at` unit ERP yang padanannya dipindah TIDAK ikut disentuh (beda dari `PATCH /item/:id` staf yang selalu men-stempelnya) — pasangan (unit ERP ↔ barang fisik) tak berubah, cuma nomor bukuan Accurate-nya; menyentuh `reconciled_at` akan salah menyiratkan staf memverifikasi ulang hari ini.

## Belum selesai

- **Asumsi kunci belum diverifikasi empiris**: belum ada percobaan nyata mengganti nomor satu item di Accurate lalu memeriksa apakah id internalnya (`AccurateID`) benar-benar tetap sama. Seluruh desain ini bergantung padanya, dan sengaja dibuat gagal-aman (lihat Consequences) justru karena belum bisa dibuktikan langsung — tak ada sandbox Accurate untuk memicu rename on-demand. Begitu ada kesempatan nyata (item perlengkapan yang memang akan di-rename Accurate), verifikasi lewat `cmd/stockprobe`: catat `accurate_id` sebelum, bandingkan sesudah.
- **Skenario rename sungguhan belum tersimulasi end-to-end** di test — hanya diverifikasi lewat fake/mock yang mengasumsikan perilaku Accurate sesuai desain di atas.

Grounded: `entity.AccurateStock` (`AccurateID`/`MissingSince`), `accurate_stock_repo.go` (`BulkUpsert`/`UpsertQty`/`MarkMissingExcept`/`ListStaleBeyond`/`DeleteByItemNo`), `worker/tasks/accurate_stock_refresh.go` (`resolveRenames`), `worker/tasks/accurate_item_rename.go` (`pilihPadananRename`/`resolveRename`/`NewInventoryRepointer`), `entity.AccurateItemRename` + `accurate_item_rename_repo.go` (koleksi `accurate_item_renames`); inventory-service `perlengkapan_ganti_padanan.go` (`GantiPadananPerlengkapan`, `gateRobotInternal()`).

## Dokumen Terkait
- [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]] — pola scanner+manusia yang disimpangi sadar, dan kriteria kapan boleh menyimpang (Decision §7)
- [[ADR - 0069 Perlengkapan Per-Unit Opsional di inventory dengan Guard Anti-Kontaminasi]] — asal-usul `accurate_item_no` dan penulis pertamanya (staf)
- [[REF - Kepemilikan Data]] — aturan #2 (konsumsi lewat pemilik) dan #4 (dua penulis = keputusan ber-ADR) yang menggerakkan desain ini
- [[Microservices - Integration Service]] — mekanisme deteksi + resolusi rename
- [[Microservices - Inventory Service]] — endpoint `/internal/perlengkapan/ganti-padanan`
- [[GA - Inventory Management]] — dampak yang dilihat staf GA
