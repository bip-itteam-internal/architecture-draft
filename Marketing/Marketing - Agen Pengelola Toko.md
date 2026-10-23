# Marketing - Agen Pengelola Toko

## Deskripsi

*Konsep agen AI yang secara bertahap mengambil alih pekerjaan pemegang toko marketplace (posisi Account Specialist) di divisi Beautyhacks dan Kyura. Agen ini bukan service baru: ia adalah mesin keputusan berbasis aturan (bekas Asisten Analisa Marketing, fiturnya sendiri dihapus 2026-10-11) yang diperluas dengan toko pilot, penyetuju Leader/SPV, dan penilaian dampak tiap keputusan terhadap laba matang. Lapisan pengiriman dan persetujuannya **harus dirancang ulang**, karena yang lama sudah dihapus. Keputusan arsitekturnya di [[ADR - 0145 Agen Pengelola Toko Tumbuh dari Mesin Keputusan yang Ada, Dampak Diukur Sebelum Eksekusi]]; dok ini menyimpan cara kerjanya.*

- **Status**: 🟡 **Konsep**, 2026-10-01; landasan berubah 2026-10-11. Kode tahap 1 belum ada. ⚠️ Yang tersisa dari dasarnya hanya **mesin keputusan** (katalog, kelayakan, jendela matang, orkestrator) di `services/marketing-analytics/`, dipertahankan **tanpa pemanggil produksi** oleh [[ADR - 0169 Asisten Analisa Marketing Dihapus, Copilot Jadi Pintu Tunggal, Mesin Keputusan Dipertahankan]]. Laporan terjadwal, kiriman keputusan, jawaban jalankan/tolak, dan lapisan model yang dibangun di atasnya ([[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]]) sudah dihapus dari kode dan prod (2026-10-11).
- **Implementasi**: [[Microservices - Marketing Analytics Service]] (mesin keputusan saja; koleksi `keputusan_kiriman` diarsip tanpa kode pembaca)

## Latar Belakang

- Permintaan: agen AI yang menggantikan pemegang toko (konten, iklan, promo, CS, strategi), bertujuan laba maksimal dan belajar dari pengalaman.
- "Pengelola toko" bukan satu jabatan. Pekerjaan satu toko dibagi ke banyak posisi (Account Specialist, Marketplace Advertiser, Host Live, Affiliate, Customer Support, Video Editor, Meta Advertiser, Buzzer), lihat [[Marketing - Dashboard per Posisi (Beauty Hacks & Kyura)]]. Sasaran pertama: **Account Specialist**.
- Pekerjaan Account Specialist menurut [[ADR - 0107 Alat Kerja Pemegang Akun Toko lewat Izin Posisi akuntoko]]: memantau performa toko, membaca ulasan, melaporkan masalah packing ke gudang, mengajukan boosting. Menurut wawancara 2026-09-30, juga membuat video AI dengan alat yang berbeda-beda per orang (tidak tercatat di satu tempat).
- KPI Account Specialist (template prod, diukur 2026-09-12): profit dari `insentif_profit` bobot 0,6, ROAS dari `kinerja_toko` bobot 0,2, retur % bobot 0,2.
- Masalah inti: tidak ada cara mengetahui apakah keputusan mesin untuk sebuah toko sama baiknya dengan keputusan manusia. Mesin keputusan yang ada mencatat jawaban orang, tetapi tidak menilai hasilnya.

## Ruang Lingkup / Cakupan (business view)

Tujuh lapis fondasi agen dan posisinya hari ini:

| Lapis | Isi | Keadaan (2026-09-30) | Tahap |
|---|---|---|---|
| Mata | Data laba, iklan, retur, video per toko | ✅ Mart marketing-analytics (48 jam), order 4 jam, retur 2 jam | ada |
| Otak | Katalog tindakan tertutup dan kelayakan backend (aturan, tanpa model) | ⚠️ ada di kode tanpa pemanggil produksi sejak 2026-10-11; lapisan model yang memilih dan menjelaskan DIHAPUS | sebagian |
| Tujuan dan pagar | `laba_matang` 30 hari, katalog tertutup, larangan proyeksi rupiah | ⚠️ sebagian di kode mesin (`keputusan_katalog.go`, `keputusan_jendela_matang.go`) | 1 |
| Pengawasan | Penyetuju Leader/SPV per toko pilot, jawaban tercatat | ❌ jalur jawaban (`/keputusan-kiriman`) DIHAPUS 2026-10-11; harus dirancang ulang | 1 |
| Evaluasi | Dampak tiap keputusan vs toko pembanding; verifikasi "dijalankan" dari data | ❌ belum ada | 1 |
| Memori | Hasil penilaian dampak (append-only) sebagai bahan belajar; pengetahuan kurasi manusia di vault privat terpisah | ❌ belum ada | 1 (dampak), nanti (pengetahuan) |
| Tangan | Aksi tulis ke marketplace, dijalankan saat disetujui dengan identitas penyetuju | ❌ nol aksi tulis pemasaran | 2, per tindakan ber-ADR |

### Siklus tahap 1

1. Keputusan untuk toko pilot dihasilkan mesin yang dipertahankan. **Pengantarannya TBD**: jadwal laporan yang dulu mengirimnya sudah dihapus (kandidat pengganti: di atas Copilot, bukan menghidupkan arsip).
2. Penyetuju (Leader/SPV yang ditulis eksplisit per toko) menjawab `jalankan` atau `tolak`. **Jalur jawabannya TBD**, sama alasannya.
3. Orang menjalankan tindakannya di Seller Center.
4. Sistem memeriksa jejaknya di data bila bisa (`terverifikasi` / `tidak_terverifikasi` / `tak_bisa_diverifikasi`).
5. Sesudah matang (±30 sampai 50 hari), sistem menilai selisih `laba_matang` 30 hari sesudah vs sebelum, dikurangi perubahan toko pembanding.
6. Hasil penilaian per jenis tindakan menjadi masukan keyakinan keputusan berikutnya.

### Aturan pemakaian angka (wajib dibaca sebelum merancang penilaian)

- **Pakai `laba_matang`, bukan `gross_profit`.** Laba jendela pendek nyaris selalu belum cair: kiriman laporan (kini dihapus) prod 2026-09-25 mencetak laba kotor −Rp212 jt untuk jendela 2 hari dengan settlement cair 0% (`keputusan_jendela_matang.go`).
- `gross_profit` = net settlement − HPP − biaya iklan; **retur sudah terpotong di settlement**, jangan dikurangi lagi.
- `roas` = revenue ÷ biaya iklan, **berbasis revenue sebelum diskon** sehingga optimistis; `nil` bila iklan nol, bukan 0.
- `iklan_sia_sia` **tidak boleh dijumlahkan** ke laba atau ke biaya lain; hanya untuk mengurutkan.
- `ads_cost_tanpa_mata_uang` sudah termasuk di `ads_cost`.
- Profit insentif **berbeda** dari `kinerja_toko` (rumus, periode, dan cutoff berbeda); jangan dipakai bergantian.
- ROAS per video tidak andal (biaya bocor ke campaign `-1`, `icc_video_metric.go`).
- Dampak yang tidak bisa dinilai berstatus `tak_bisa_dinilai`, bukan nol; yang belum matang `belum_matang`, bukan nol.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Penyetuju toko pilot | Leader / SPV Beautyhacks atau Kyura | ditulis eksplisit per toko pilot (bukan `RequireMarketingLeader`) | Web ERP |
| Pemegang toko pilot | Account Specialist | tetap tercatat di `icc_account_mappings` selama tahap 1 | Web ERP |
| Pembaca hasil | Direktur, pemilik produk | daftar penerima eksplisit; pola lama (ADR 0120) dicabut, jalur barunya TBD | Web ERP |

- **Tujuan**: tahu jenis keputusan mana yang benar-benar menambah laba, sebelum memberi mesin kewenangan lebih.
- **Pain point**: keputusan AI sudah terbit, tetapi tak ada yang tahu apakah menjalankannya berhasil; "dijalankan" hanya pengakuan.
- **Aksi utama**: menjawab keputusan toko pilot; membaca hasil penilaian dampak.

## Konsumen Data

- [[Microservices - Marketing Analytics Service]]: mesin keputusan yang dipertahankan. Loop belajar ADR 0127 ikut hilang bersama jawabannya; langkah 2 yang memakai hasil penilaian dampak harus dirancang ulang.
- [[Finance - Incentive]]: **tidak** mengonsumsi apa pun di tahap 1; menjadi terdampak begitu toko pilot dilepas dari pemegang manusia (lihat Kendala).

## Kendala

- **Nol aksi tulis pemasaran ke marketplace** di `bip-erp` (diukur `git grep` 2026-09-30); satu-satunya aksi tulis adalah pengiriman barang Shopee. Izin scope API tulis dari TikTok dan Shopee belum dicek.
- **Loop belajar tidak punya data**: prod `keputusan_kiriman` 5 kiriman berisi 417 keputusan, 0 jawaban (diukur 2026-10-11, tercatat di ADR 0169); koleksinya kini diarsip tanpa kode pembaca, jadi bukan bahan siap pakai.
- **Insentif**: toko tanpa pemegang manusia dibuang dari hitungan insentif (`services/insentive/func.go:2168-2170`), dan toko Leader/SPV adalah gabungan toko anggotanya, jadi melepas toko pilot mengeluarkan profitnya dari pencapaian penyetuju. Penugasan toko bertanggal ([[ADR - 0138 Penugasan Toko Marketplace Bertanggal Berlaku untuk KPI dan Insentif]]) belum diputuskan.
- **Identitas**: eksekusi tanpa kehadiran pemakai ditolak [[ADR - 0135 Jadwal Tugas Copilot Mengirim Pengingat, Bukan Menjalankan Tanpa Kehadiran Pemakai]]; karena itu tahap 2 dirancang sebagai eksekusi saat disetujui.
- **Video**: Ideamills ([[APP - Ideamills]]) terpisah dari ERP dan tidak menyimpan id video marketplace; 97% video 30 hari di toko berpemegang dibuat kreator yang tak terpetakan ke Account Specialist (diukur 2026-09-12). Pembelajaran konten belum mungkin.
- **Kesegaran**: mart diperbarui tiap 48 jam; agen tidak bisa bereaksi real-time.
- **Pemegang toko** (prod 2026-09-30): 61 pemetaan aktif, 36 orang.

## Belum Diputuskan (TBD)

- Toko mana yang jadi pilot dan siapa penyetuju per toko (pemilik: manajemen marketing).
- Definisi persis toko pembanding (tim dan channel sama; kriteria kemiripan lain), diputuskan saat `/plan` tugas penilaian dampak (T5).
- Aturan insentif dan KPI untuk toko tanpa pemegang manusia (pemilik: manajemen marketing + Finance), prasyarat melepas toko pilot.
- Jenis tindakan pertama yang dieksekusi di tahap 2 dan ketersediaan scope API-nya.
- Jalur baca pengetahuan kurasi manusia (vault privat) dari server, dan pencatatan id video di Ideamills.
- Kompensasi beban kerja baru Leader/SPV sebagai penyetuju.

## Dokumen Terkait

- [[ADR - 0145 Agen Pengelola Toko Tumbuh dari Mesin Keputusan yang Ada, Dampak Diukur Sebelum Eksekusi]]
- [[ADR - 0169 Asisten Analisa Marketing Dihapus, Copilot Jadi Pintu Tunggal, Mesin Keputusan Dipertahankan]]
- [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]]
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
- [[CORE - Kapabilitas AI dan Machine Learning]]
- [[Marketing - Dashboard per Posisi (Beauty Hacks & Kyura)]]
- [[Microservices - Marketing Analytics Service]]
