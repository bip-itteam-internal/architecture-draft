> **Status**: 🟡 Draft — disusun dari dokumentasi publik KiriminAja Mitra API (`developer.kiriminaja.com`) per Juli 2026. **Belum pernah dieksekusi dengan akun Bharata asli** — belum ada implementasi client KiriminAja di [[Microservices - Integration Service]] (§KiriminAja, konsep). Jangan anggap langkah di bawah final; verifikasi ulang tiap field/endpoint saat implementasi nyata dimulai, dan naikkan status ke ✅ setelah terverifikasi jalan.

## Tujuan

Mendapatkan API key (Bearer token) KiriminAja Mitra API — untuk kebutuhan integrasi shipping/logistics: create shipment, cek ongkir, tracking, cetak label, webhook status, pickup scheduling, dan payment/COD management.

## Kapan dipakai

Saat memulai implementasi client KiriminAja di `services/integration` (lihat rencana teknis di [[Microservices - Integration Service]] §KiriminAja).

## Prasyarat

- Akses email tim (untuk kontak `tech@kiriminaja.com`) dan kesiapan proses partnership/approval dari pihak KiriminAja (bukan self-service instan seperti Shopee/TikTok/Meta).
- Kejelasan sumber data order yang akan dikirim via KiriminAja (lihat open question di [[Microservices - Integration Service]] §KiriminAja — belum diputuskan saat dokumen ini ditulis).
- Callback/webhook URL publik untuk menerima update status pengiriman (satu API key hanya bisa satu webhook endpoint).

## Langkah

1. **Kontak tim teknis KiriminAja** — kirim email ke `tech@kiriminaja.com`, jelaskan kebutuhan integrasi (create shipment, cek ongkir, tracking, cetak label, webhook, pickup, COD). Tim KiriminAja akan memandu proses registrasi & partnership.
2. **Registrasi akun Sandbox** — setelah disetujui, dapat akses Sandbox Dashboard.
3. **Ambil API key sandbox** — di Sandbox Dashboard → menu *Integrasi* → copy API Key. Simpan sebagai secret (env var), jangan commit ke repo.
4. **Evaluasi Go SDK resmi** — KiriminAja menyediakan SDK resmi untuk Go (`github.com/kiriminaja/go`), selain PHP/Node/Python/Ruby/Rust. Evaluasi pakai SDK ini langsung di `services/integration` alih-alih menulis HTTP client dari nol (beda dari pola Shopee/TikTok/Meta yang semua custom client).
5. **Set up webhook endpoint** — daftarkan URL webhook untuk menerima update status pengiriman (endpoint baru `POST /webhooks/services/kiriminaja` di sisi BIP, lihat [[Microservices - Integration Service]] §KiriminAja).
6. **Integrasi & UAT di sandbox** — hubungkan backend ke endpoint sandbox (`https://tdev.kiriminaja.com`), uji seluruh fitur: cek ongkir, create shipment (AWB), cetak label, tracking, webhook, pickup scheduling, payment/COD.
7. **Transisi ke produksi** — setelah UAT lolos, dapat API key produksi (endpoint `https://client.kiriminaja.com`). **Bearer token staging tidak bisa dipakai untuk produksi** — pastikan tidak tertukar.

## Verifikasi

- Panggil endpoint cek ongkir sandbox dengan API key → dapat response rate lintas beberapa kurir (JNE, J&T, SiCepat, dll), bukan error auth.
- Buat 1 shipment percobaan (create shipment) di sandbox → dapat AWB/nomor resi.
- Webhook test: trigger perubahan status di sandbox → pastikan payload diterima di endpoint `POST /webhooks/services/kiriminaja`.
- API key tersimpan sebagai env var (bukan hardcoded), sejalan pola `SHOPEE_PARTNER_ID`/`TIKTOK_SHOP_APP_ID` yang sudah ada.

## Bila gagal / Rollback

- **Auth ditolak** — pastikan header `Authorization: Bearer {api_key}` benar dan pakai key sesuai environment (sandbox vs produksi tidak bisa dicampur).
- **Webhook tidak diterima** — cek satu API key hanya boleh satu webhook endpoint terdaftar; pastikan tidak ada endpoint lama yang masih terdaftar dari percobaan sebelumnya.
- **Approval partnership lama/tidak jelas** — proses ini butuh persetujuan manual dari KiriminAja (bukan self-service), tidak ada SLA waktu tunggu resmi yang terdokumentasi publik — follow up langsung ke `tech@kiriminaja.com` bila tidak ada respons.
- **Token bocor** — jangan sebarkan bearer token ke pihak mana pun (larangan eksplisit dari KiriminAja); segera minta rotasi ke tim KiriminAja bila diduga bocor.

## Referensi Eksternal

- [Get Started - KiriminAja Developer](https://developer.kiriminaja.com/docs)
- [Overview - Developer KiriminAja](https://developer.kiriminaja.com/docs/introduction)
- [Bagaimana cara mendapatkan API Key?](https://help.kiriminaja.com/article/bagaimana-cara-mendapatkan-api-key)
- [KiriminAja GitHub Organization](https://github.com/kiriminaja) — SDK resmi (Go, PHP, Node, Python, Ruby, Rust)
- [KiriminAja Go SDK](https://github.com/kiriminaja/go)
- [Integrasi API Ekspedisi untuk Bisnis - KiriminAja](https://kiriminaja.com/integration)

## Dokumen Terkait

- [[Microservices - Integration Service]] — rencana teknis §KiriminAja
- [[LOG - Shopee API Rate Limit Request]] — preseden mitigasi rate-limit vendor pengiriman/marketplace
