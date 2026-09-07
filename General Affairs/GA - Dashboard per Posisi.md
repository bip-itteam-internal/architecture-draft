## Deskripsi

*Rancangan isi dashboard per posisi untuk divisi **General Affair** (5 lembar) dan **Procurement** (2 posisi). Diturunkan mengikuti [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]]. Dua divisi digabung dalam satu dokumen karena keduanya sudah tinggal di folder yang sama dan Procurement hanya punya dua posisi.*

- **Status**: 🟡 **Rancangan**. Tiga posisi GA punya tab di `/hris` (GA Staff, Office Boy, Security); Admin dan kedua posisi Procurement belum punya layar sama sekali.
- **Angka KPI diukur 2026-08-28** (sumber: [[HRIS - Matriks KPI per Departemen]]). **Ukur ulang sebelum dipakai mengambil keputusan.**
- **Path di repo**: `erp-frontend/src/features/hris/dashboard/kartu/isi/isi-ga.tsx` · `isi-office-boy.tsx` · `isi-security.tsx`

## Temuan utama: satu modul mengunci sepertiga divisi

Dari **24 metrik General Affair, sembilan terkunci pada satu hal yang sama**: tidak ada modul checklist berjadwal (patroli, 5R, GMP, preventive maintenance) di sistem. Konsepnya sudah ditulis di [[GA - Checklist Management]] tetapi belum dibangun.

| Penghambat | Metrik | Posisi yang terdampak |
|---|---:|---|
| Modul checklist berjadwal belum ada | 9 | Office Boy (semua), Security (separuh), kedua GA Staff, Admin |
| Angka dari `inventory_db.inventory` | 6 | GA Staff (aset), Admin |
| Master anggaran GA belum ada | 3 | Admin, GA Staff (building) |
| Belum dipetakan sama sekali | 4 | Security, GA Staff (building), Admin |
| Data procurement (sudah ada) | 2 | Admin |

**Membangun modul checklist adalah satu pekerjaan yang membuka sembilan metrik di lima posisi.** Tidak ada pekerjaan lain di divisi ini yang mendekati daya ungkitnya.

## Admin (General Service)

**Dinilai dari** (template `Admin General Service`, 7 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,2 | Realisasi anggaran belanja tanpa over budget | master anggaran belum ada | ❌ |
| 0,2 | Akurasi pencatatan kas kecil | belum dipetakan | ❌ |
| 0,15 | Ketepatan pengadaan barang ATK & GA | `GET /procurement/po/lead-time` | ✅ |
| 0,15 | Administrasi dokumen GA real time | modul checklist belum ada | ❌ |
| 0,1 | Ketepatan rekap pengajuan dana GA | data procurement (1.835 penerimaan, 2.055 faktur) | ✅ |
| 0,1 | Skor pelayanan & harga vendor | master anggaran belum ada | ❌ |
| 0,1 | Akurasi pengelolaan ATK & inventory | `inventory_db.inventory` 134 item | ⚠️ repair history kosong |

**Bisa ditampilkan sekarang.** Dua metrik pengadaan, total bobot 0,25, dan datanya tebal (139 pemasok, 2.055 faktur pembelian).

- **Visual utama**: lead time PO terhadap ambang, per bulan. Ia satu-satunya metrik posisi ini yang punya deret waktu nyata.
- Antrean pengajuan dana GA yang menunggu, dari modul procurement yang sudah berjalan.

⚠️ **Posisi ini satu-satunya tempat template `Admin General Service` pernah terlihat.** Ia tak punya tab di `TAB_DASHBOARD`, dan satu-satunya layar yang menampilkannya hari ini adalah Peta Otomasi Divisi di tab Ringkasan. Merancang lembarnya berarti menambah tab baru, bukan mengisi yang sudah ada.

## GA Staff

⚠️ **Nama posisi ini dipakai DUA peran berbeda dengan tulisan yang sama persis**: `Building & Maintenance` (4 metrik) dan `General Asset Staff` (5 metrik). Keduanya karena itu berbagi satu tab `ga` yang menggabungkan aset dan pemeliharaan. **Memisahkan lembarnya menuntut HR memecah nama posisi di master data lebih dulu**, dan itu bukan pekerjaan frontend.

**Dinilai dari, peran Building & Maintenance:**

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,3 | Realisasi preventive maintenance | modul checklist belum ada | ❌ |
| 0,3 | Kecepatan menyelesaikan kerusakan | `inventory_db` | ❌ repair history KOSONG |
| 0,25 | Efisiensi biaya maintenance | master anggaran belum ada | ❌ |
| 0,15 | Daily report checklist | belum dipetakan | ❌ |

**Dinilai dari, peran General Asset Staff:**

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,3 | Realisasi rencana kerja | `inventory_db.inventory` | ⚠️ |
| 0,25 | SLA preventive maintenance alat | modul checklist belum ada | ❌ |
| 0,2 | Pemeliharaan aset | `inventory_db.inventory` | ⚠️ |
| 0,15 | Akurasi stok opname aset | stock opname aset belum ada | ❌ |
| 0,1 | Labeling & tagging aset | `inventory_db.inventory` | ⚠️ |

**Bisa ditampilkan sekarang.** Sangat sedikit. Koleksi `inventory_db.inventory` berisi 134 item dan handover per karyawan, cukup untuk kartu cacah aset dan daftar serah-terima, tetapi **riwayat perbaikan kosong dan stok opname aset belum ada** sehingga tiga metrik yang bertumpu padanya tak bisa diangkakan.

- Kartu cacah aset terdata dan daftar handover yang belum kembali. Keduanya nyata, keduanya kecil.
- Tidak ada kandidat visual utama. Jangan memaksakan satu.

**Yang menunggu backend.** Riwayat perbaikan aset dan stok opname, keduanya di `inventory_db`, lalu modul checklist.

## Office Boy

**Dinilai dari** (template `Office Boy Team`, 4 metrik):

| Bobot | Metrik | Sumber |
|---:|---|---|
| 0,3 | Rating pelayanan dan kebersihan | modul checklist belum ada |
| 0,3 | Kondisi kebersihan area yang ditugaskan | modul checklist belum ada |
| 0,25 | Perawatan barang, perabotan, tanaman | modul checklist belum ada |
| 0,15 | Pelaksanaan 5R area pantry | modul checklist belum ada |

⛔ **Tidak direkomendasikan dibuatkan dashboard**, sesuai [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] §4.

Keempat metriknya, bobot penuh 1,0, terkunci pada satu modul yang sama dan belum ada. Posisi ini juga tidak punya antrean, tenggat, atau persetujuan di sistem mana pun, jadi sumbu kedua ADR itu pun kosong. Layar yang dibangun sekarang akan seluruhnya panel menunggu.

**Yang membalikkan keputusan ini**: modul checklist berjadwal berdiri dan dipakai. Satu hal, dan seluruh posisi ini langsung terukur penuh.

## Security

**Dinilai dari** (template `Security Team`, 4 metrik):

| Bobot | Metrik | Sumber |
|---:|---|---|
| 0,3 | Rating pelayanan dan keamanan | belum dipetakan |
| 0,3 | Kepatuhan patroli tiap 3 jam | modul checklist belum ada |
| 0,2 | Kepatuhan SOP security | belum dipetakan |
| 0,2 | Kerapihan dan kebersihan pos jaga | modul checklist belum ada |

⛔ **Tidak direkomendasikan dibuatkan dashboard.** Nol dari empat metrik punya sumber, dan separuhnya menunggu modul yang sama dengan Office Boy.

⚠️ Satu pengecualian yang layak diperiksa terpisah: Security adalah satu-satunya posisi GA yang punya modul operasional berjalan, yaitu [[GA - Guestbook System (Complete)]]. Buku tamu **tidak muncul di satu pun metrik KPI-nya**, jadi ia bukan bahan dashboard menurut sumbu pertama. Tetapi ia pekerjaan nyata yang tercatat, sehingga bila posisi ini akhirnya dibuatkan layar, sumbu keduanya sudah ada. **Keputusan itu di luar dokumen ini**; yang jelas, ketidakhadiran buku tamu di KPI adalah pertanyaan untuk HR, bukan celah yang boleh ditambal frontend.

## Procurement Leader

**Dinilai dari** (template `KPI Leader Procurement`, 5 metrik):

| Bobot | Metrik | Sumber | Keadaan |
|---:|---|---|---|
| 0,4 | Zero production stop + SLA pembelian 100% | `GET /task-management/report/sla` | ✅ 214 sampel |
| 0,2 | Credit term vendor rata-rata N+60 | `GET /procurement/po/lead-time`, 139 pemasok | ✅ |
| 0,2 | Akurasi MRP ≥ 95% | tidak ada modul MRP | ❌ |
| 0,1 | Rebate kontrak jangka panjang 3-5% | `work_data.contract_ending` | ⚠️ salah petak, lihat bawah |
| 0,1 | Performance tim min. 70 | belum dipetakan | ❌ |

**Bisa ditampilkan sekarang.** Dua metrik berbobot total 0,6, dan keduanya bertumpu pada data yang tebal.

- **Visual utama**: SLA pembelian per bulan terhadap ambang. Ia berbobot 0,4 dan punya 214 sampel terukur.
- Kartu sebaran credit term vendor, plus daftar PO yang lewat ETA.
- Antrean persetujuan pembelian yang menunggu Leader, dari [[Microservices - Procurement Service]].

⛔ **Metrik rebate salah petak.** Sumbernya tertulis `work_data.contract_ending` dan `join_date`, yaitu **kontrak KARYAWAN**, sementara metriknya soal kontrak VENDOR. Menyambungkannya apa adanya akan menilai Leader Procurement atas tanggal berakhir kontrak kerja pegawai. Ini kelas kesalahan yang sama dengan metrik aset HRD Supervisor: angka yang tampak wajar dan menjawab pertanyaan lain.

## Procurement Staff Inventory

**Dinilai dari** (template `KPI Staff Inventory`, 5 metrik):

| Bobot | Metrik | Sumber tertulis | Keadaan |
|---:|---|---|---|
| 0,4 | Ketersediaan stok bahan baku 100% sesuai PPIC | `tt_business_gmv_max_performance_reports` | ⛔ salah petak |
| 0,2 | On time delivery supplier ≥ 95% | `tt_business_gmv_max_performance_reports` | ⛔ salah petak |
| 0,2 | Efisiensi harga pembelian, saving ≥ 5% | Accurate proxy | ⚠️ |
| 0,1 | Evaluasi vendor maks 70% | Accurate proxy | ⚠️ |
| 0,1 | Compliance GMP & QA material 100% | modul checklist belum ada | ❌ |

⛔ **Dua metrik terbesar posisi ini, bobot total 0,6, dipetakan ke data IKLAN TIKTOK.** `tt_business_gmv_max_performance_reports` (712.855 baris) dan `mart_profit_attribution` adalah data performa iklan dan atribusi profit marketplace. Keduanya tidak punya hubungan apa pun dengan ketersediaan bahan baku produksi maupun ketepatan pengiriman pemasok.

Ini **bukan metrik yang belum tersambung, melainkan metrik yang tersambung ke tempat yang salah**, dan itu jauh lebih berbahaya: sumbernya berisi jutaan baris sehingga akan menghasilkan angka yang mulus, stabil, dan sepenuhnya keliru. Kelas kesalahan yang sama sudah tercatat dua kali di divisi lain dalam dokumen ini.

**Rekomendasi rancangan.** Jangan merancang layar posisi ini sampai kedua pemetaan itu diperbaiki. Yang benar hampir pasti data penerimaan dan PO di [[Microservices - Procurement Service]], yang sudah ada dan tebal, tetapi **menetapkannya adalah keputusan pemilik KPI, bukan tebakan yang boleh diambil dari dokumen ini.**

## Kebutuhan backend, terurut

1. **Modul checklist berjadwal** ([[GA - Checklist Management]]). Membuka 9 metrik di 5 posisi, dan satu-satunya yang membuat Office Boy serta Security layak punya layar sama sekali. Daya ungkit tertinggi di dokumen ini.
2. **Perbaiki pemetaan Staff Inventory.** Dua metrik berbobot 0,6 menunjuk data iklan TikTok. Keputusan pemilik KPI, bukan pekerjaan kode.
3. **Perbaiki pemetaan rebate Procurement Leader** dari kontrak karyawan ke kontrak vendor.
4. **Riwayat perbaikan aset dan stok opname** di `inventory_db`, mengunci 3 metrik GA Staff.
5. **Master anggaran departemen GA**, mengunci 3 metrik di Admin dan GA Staff.
6. **Pemetaan metrik Security** yang belum dipetakan sama sekali (rating pelayanan, kepatuhan SOP).
7. **Modul MRP** untuk Procurement Leader. Paling besar pekerjaannya, paling kecil cakupannya di dokumen ini.

## Dokumen Terkait

- [[ADR - 0076 Isi Dashboard Posisi Diturunkan dari KPI, Antrean, dan Ambang]] — prinsip penurunannya
- [[REF - Layout Dashboard erp-frontend]] — cara menyusunnya di layar
- [[HRIS - Matriks KPI per Departemen]] — sumber angka di dokumen ini
- [[HRIS - Dashboard per Posisi]] — divisi saudara yang berbagi rute `/hris`
- [[GA - Checklist Management]] — modul yang mengunci daya ungkit terbesar divisi ini
- [[GA - Inventory Management]] — sumber angka aset
- [[GA - Procurement System]] · [[Microservices - Procurement Service]] — sumber angka pengadaan
- [[GA - Building Maintenance]] — konteks peran Building & Maintenance
