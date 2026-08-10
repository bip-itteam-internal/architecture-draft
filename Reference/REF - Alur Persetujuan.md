## Deskripsi

*Daftar SELURUH alur persetujuan di ERP Bharata beserta siapa yang berwenang memutuskannya. Disusun dari pembacaan rute di seluruh service (2026-08-10), bukan dari dokumen — beberapa gerbang tak terlihat dari daftar rute karena tinggal di dalam handler.*

- **Status**: ✅ Implemented — seluruh baris terverifikasi di kode.
- **Path di repo**: `bip-erp/services/{attendance,payroll,recruitment,procurement,manufacture,insentive,inventory,task-management,hrd-document,employee,integration}` · `bip-erp/shared-library/common/jabatan_direktur.go`
- **Kenapa referensi ini ada**: pertanyaan "persetujuan apa saja yang ada, dan siapa yang boleh" sebelumnya hanya bisa dijawab dengan membaca 11 service satu per satu. Sekali disusun, ia juga memperlihatkan pola yang tak terlihat dari satu alur saja.

## Tiga cara gerbang persetujuan ditulis

Yang membuat inventaris ini sulit disusun, dan mudah salah:

1. **Middleware di daftar rute** — `gate(perm, fallback)` atau `common.Require*`. Terlihat langsung saat membaca `routes.go`.
2. **Di dalam handler** — mis. `BolehSetujuiPesanan(position)` di procurement. **Tak terlihat** saat menyapu daftar rute; sapuan pertama dokumen ini salah melaporkannya "tanpa gerbang".
3. **Slot pada dokumennya** — cuti & dinas menyimpan siapa reviewernya di `spv_status`; gerbangnya mencocokkan pemanggil dengan slot itu.

> ⚠️ **Menyapu `routes.go` saja menghasilkan kesimpulan yang salah.** Dua dari tiga cara di atas tak muncul di sana.

## Inventaris

### Berbasis SLOT pada dokumen

| Alur | Service | Penyetuju |
|---|---|---|
| Cuti / izin / sakit | attendance | atasan langsung; **dialihkan ke Direktur** bila pemohonnya supervisor sendiri |
| Perjalanan dinas | attendance | idem |
| Koreksi presensi | attendance | atasan langsung (tanpa pengalihan) |
| Tukar jadwal | attendance | atasan langsung |
| Verifikasi security (cuti per jam) | attendance | posisi Security |

### Berbasis JABATAN

| Alur | Service | Penyetuju |
|---|---|---|
| Pesanan Pembelian ERP | procurement | `common.SetaraDirektur` — Direktur & Corporate Secretary |
| Permintaan Barang ERP | procurement | atasan departemen peminta (dari cakupan supervisi) |

### Berbasis IZIN / PERAN

| Alur | Service | Penyetuju |
|---|---|---|
| Payroll run — approve & publish | payroll | `payroll.approve`; fallback tier `hris: admin` |
| Rekrutmen — setujui penawaran | recruitment | `recruitment.approve` / HR supervisor |
| Rekrutmen — review & tolak job requisition | recruitment | idem |
| Rekrutmen — putuskan hire | recruitment | HR admin **atau** `secretary` supervisor |
| Rekrutmen — keputusan onboarding | recruitment | HR |
| Dokumen HRD — publish | hrd-document | HR |
| Quality — CAPA | employee | approver produksi / gudang |
| WMS — batch record, rekon MO, proposal, Sadewa | manufacture | peran WMS per tab |
| Task Management — approve/reject tugas | task-management | `ticket.triage` / admin space |
| Kotak Adopsi — adopt & reject draft | integration | peran integration |

### ⚠️ Tanpa gerbang

| Alur | Service | Catatan |
|---|---|---|
| Insentif — approve / unapprove hasil, termasuk bulk | insentive | menyentuh perhitungan insentif |
| Inventory — approve handover | inventory | serah-terima aset |

Keduanya bisa dipanggil siapa pun bertoken sah. Sejalan dengan [[ADR - 0031 Prefix internal Bukan Batas Keamanan]], letak rute tak menjadikannya terlindungi.

## Wewenang setingkat Direktur

Satu-satunya wewenang di ERP ini yang diperiksa lewat **nama jabatan**, bukan peran maupun izin. Ia dipakai tiga tempat, dan sampai 2026-08-10 masing-masing menuliskan daftarnya sendiri:

| Tempat | Untuk |
|---|---|
| `services/attendance` | slot cuti & dinas yang dialihkan ke "Direktur" |
| `services/procurement` | `PosisiApproverPO` — persetujuan Pesanan Pembelian |
| `erp-frontend` | cerminan yang kedua, untuk menyaring menunya |

Ketiganya kini menunjuk **`common.SetaraDirektur`** (`shared-library/common/jabatan_direktur.go`), berisi **Direktur** dan **Corporate Secretary** — keduanya berwenang sama (keputusan organisasi 2026-08-10).

⚠️ **Kenapa satu sumber penting di sini melebihi kerapian.** Daftar yang terlewat di salah satu tempat tak bergejala: orangnya **melihat** antrean — sebab daftarnya juga mencocokkan nama DEPARTEMEN — lalu **ditolak saat memutus**. Antrean berisi, tombolnya balas 403, dan tak ada satu pun pesan yang menjelaskan sebabnya.

⚠️ **Melihat ≠ memutuskan, dan itu disengaja.** Seluruh staf Kesekretariatan (Personal Assistant, Graphic Design, Video Editor) ikut melihat antrean persetujuan Direktur karena pencocokan departemen. Yang boleh memutus hanya dua jabatan di atas; ketiganya dikunci uji sebagai kasus yang harus tetap tertutup. Mempersempit daftarnya adalah keputusan yang belum diambil.

## Belum Diimplementasikan / Catatan

- **Dua alur tanpa gerbang** di tabel di atas belum ditutup.
- **Payroll: niat vs kenyataan.** Komentar di `services/payroll/rbac.go` menulis `isApprover` = "persetujuan final payroll run (Direktur)", tapi isinya `isHRAdmin`. Selama Direktur tak punya paket payroll, HR admin-lah yang menyetujui atas namanya. Ditutup 2026-08-10 dengan memasang paket `payroll_penyetuju` ke jabatannya — **tanpa mengubah gerbang**, sebab `gate()` mendahulukan izin dari klaim.
- **Persetujuan Pesanan & Permintaan tak punya pintu masuk dari navigasi.** Menunya dicabut dari Portal Saya; halamannya (`/persetujuan/pesanan-pembelian`, `/persetujuan/permintaan-barang`) dibiarkan dormant dan hanya bisa dibuka lewat URL langsung. Sejak 2026-08-10 antrean PO punya pintu lewat [[APP - Web ERP]] (Ruang Direktur); **Permintaan Barang masih tanpa pintu**.
- **Persetujuan PO di Accurate tak bisa ditindaklanjuti dari ERP.** ERP menyimpan salinan pesanan Accurate (`status_name: "Diajukan"`), tapi Accurate hanya menyediakan `save.do` — tak ada endpoint approval. Alur yang bisa diputus dari ERP adalah `pesanan_erp`, yang terpisah dari cermin itu.

## Dokumen Terkait

- [[CORE - RBAC dan Permission Set]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]
- [[APP - Web ERP]] (Ruang Direktur) · [[Microservices - Payroll Service]] · [[Microservices - Recruitment Service]] · [[Microservices - Procurement Service]] · [[Microservices - Manufacture Service]]
