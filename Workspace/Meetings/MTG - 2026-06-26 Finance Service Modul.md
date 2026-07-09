---
publish: false
---

> **Rapat:** Finance Service — Review Modul · **Tanggal:** 2026-06-26 · **Hadir:** Tim Finance, Utvi (mapping logistik)

## Agenda

- Review modul Finance service: produk, summary, piutang, transaksi non-order

---

## Catatan

### 1. Produk & SKU

- Data SKU sudah ada — mencakup **single product** dan **bundling**
- SKU mulai digunakan: **17 Juni 2026**
- Perlu **product mapping** (SKU marketplace → item Accurate)
- Kategori produk:
  - **Kyuragb** → Skincare
  - **Beautyhack** → Perawatan dan Kecantikan
- Di Accurate saat ini hanya single product yang masuk; **bundling belum dimasukkan** → perlu implementasi

### 2. Departemen & Project

- Departemen yang terlibat:
  - Marketing Beautyhack
  - Marketing KY+GB
- Perlu setup **Project** di Accurate untuk pembagian ini

### 3. List Account Accurate

- Akun yang akan digunakan: **Rahardian**, **Afiani**, **Utvi**

### 4. Summary (Income / Sales / Return)

- Fitur **centang multi toko** diperlukan untuk income, sales, dan return
- **Shop mapping** → dikerjakan tim mapping
- **Bank mapping** untuk income sudah ada endpoint-nya; butuh **list data bank** dari Accurate

#### Constraint data order saat buat summary:

| Tipe Summary | Field wajib ada di order |
|---|---|
| `summaryInvoice` (status TO_SHIP & SHIPPED) | `shipped_at` |
| `summaryIncome` | `shipped_at`, `completed_at` |
| `summaryReturn` (status CANCELLED) | `completed_at`, `returned_at` |
| `summaryReturn` (status RETURNED) | `completed_at`, `returned_at` |

> Status invoice yang sudah ter-cover: TO_SHIP & SHIPPED → `shipped_at` ada; COMPLETED → `completed_at` ada
> Status return yang sudah ter-cover: CANCELLED → `cancelled_at` ada; RETURNED → `returned_at` ada

### 5. Piutang

- Butuh **kolom tanggal** di invoice (untuk tracking jatuh tempo)
- Notifikasi pada **14 hari** dan **60 hari** setelah jatuh tempo
- Piutang tidak hanya dari marketplace — ada piutang yang diinput **langsung di Accurate** (non-MP) → perlu bisa dibaca/disinkronkan

### 6. Transaksi Selain Order (Non-Marketplace)

#### Transaksi Logistik

- Ada transaksi dari logistik yang perlu dibaca sistem
- Uang masuk/keluar dari sumber yang belum teridentifikasi
- Mekanisme: `order_id` → `related_order_id` (dari logistik)
- Mencakup: **uang keluar** dan **uang masuk**
- **Blueprint** akan dibuatkan oleh **Utvi** — TBD

#### Mutasi Toko

- Toko memiliki mutasi seperti rekening bank
- Ada indikasi uang masuk dan keluar **selain dari sales**
- Perlu fitur baca mutasi toko sebagai sumber data keuangan tambahan

---

## Keputusan

1. Bundling produk harus dimasukkan ke Accurate — perlu validasi logic baru (saat ini hanya leaf SKU)
2. Constraint `shipped_at` / `completed_at` / `returned_at` wajib dipenuhi sebelum summary dibuat
3. Piutang = modul baru, belum ada implementasi sama sekali
4. Transaksi logistik menunggu blueprint dari Utvi sebelum bisa diimplementasikan
5. Mutasi toko = modul baru, konsep awal perlu disusun

---

## Action Items

- [ ] **Utvi** — buat blueprint transaksi logistik (order_id → related_order_id, uang masuk/keluar)
- [ ] **Tim Mapping** — shop mapping untuk summary multi-toko
- [ ] **Dev** — implementasi bundling produk di product mapping Accurate
- [ ] **Dev** — fetch list data bank dari Accurate untuk bank mapping income
- [ ] **Dev** — tambah kolom tanggal invoice untuk fitur piutang
- [ ] **Dev** — notifikasi piutang 14 hari & 60 hari
- [ ] **Dev** — baca piutang non-MP dari Accurate langsung
- [ ] **Dev** — implementasi constraint status order pada create summary
- [ ] **Dev** — desain modul mutasi toko

---

## Naik Kelas?

| Topik | Target Dok |
|---|---|
| Bundling produk & constraint summary | Update [[Finance - Bridging App New Golang]] |
| Piutang (modul baru) | Buat `Finance - Piutang.md` (🔴 Stub) |
| Transaksi logistik | Buat `Finance - Transaksi Logistik.md` setelah blueprint Utvi ada |
| Mutasi toko | Buat `Finance - Mutasi Toko.md` (🟡 Konsep) |
| Departemen & Project Accurate | Tambah ke [[Finance - Bridging App New Golang]] |
