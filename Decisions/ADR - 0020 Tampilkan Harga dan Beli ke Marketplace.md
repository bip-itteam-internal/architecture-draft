> Status: ✅ **Accepted** (2026-06-29)

# ADR - 0020 Tampilkan Harga + Beli ke Marketplace

## Context
[[APP - Website Bharata Internasional]] (rebuild `bharatainternasional.com`) semula mengikuti PRD v1.2 yang menetapkan **Non-Goal**: tanpa checkout/pembayaran, **tanpa menampilkan harga**, pembelian diarahkan ke marketplace resmi. Stakeholder kemudian meminta pengalaman "belanja" seperti herbalife.com.

## Decision
Mengambil pendekatan **belanja ringan**:
- **Menampilkan harga** produk (kolom `harga` baru, integer Rupiah, NULL = "Hubungi untuk harga").
- Tombol **"Beli"** pada halaman produk mengarah ke **marketplace** (Shopee/Tokopedia/TikTok), via link **per-produk** (kolom `link_shopee`/`link_tokopedia`/`link_tiktokshop`) dengan **fallback** ke link global di Pengaturan Situs.
- **Checkout, keranjang, pembayaran, dan akun pelanggan tetap TIDAK ada** di situs (Non-Goal PRD poin 1 tetap berlaku).
- Kepatuhan regulasi (izin edar, distribusi, PSE) **ditangani tim Bharata** di luar lingkup teknis.

Membalik **PRD §4 poin 2** ("Menampilkan harga produk" sebagai Non-Goal). Poin 1 (checkout) tidak berubah.

## Consequences
- **Positif**: pengunjung melihat harga & jalur beli yang jelas tanpa membangun e-commerce penuh; selaras dengan arah marketplace yang sudah ada; perubahan backend minimal (1 migration + kolom).
- **Negatif / risiko**: harga harus dijaga konsisten dengan marketplace (sumber kebenaran harga ada di marketplace); bila kelak diputuskan checkout penuh, perlu ADR baru + backend besar (order/payment); menampilkan harga obat/kosmetik mengikat ke kepatuhan konten.
- **Implementasi**: migration `00004_products_harga_marketplace.sql`; `Product` (DTO + shared types) bertambah `harga` + 3 link; `apps/web` ProductCard/ProductDetail; `apps/admin` ProductForm. Test unit FE + handler BE.
