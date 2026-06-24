> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Modul **Messenger**:
- **Conversations panel** — chat 1:1 antar user dalam sistem (real-time via Pusher).
- Notifikasi pesan, daftar percakapan, riwayat.
- Pelengkap integrasi keluar: **Slack / Telegram / Twilio** (notifikasi), **Zoom** (meeting).

## Yang sudah ada di Bharata ERP

- [[Microservices - Notification Service]] — `inbox`, `splash`, `article` (notifikasi satu arah ke karyawan), bukan chat dua arah.
- Komunikasi tim nyata kemungkinan via WhatsApp/eksternal. 🔴 Tidak ada chat internal di dalam ERP.

## Gap / Peluang

- Tidak ada **chat dua arah** di dalam sistem. Nilainya: diskusi kontekstual di samping task/approval tanpa pindah aplikasi.
- Namun ini area yang **mudah duplikatif** dengan tools chat eksternal yang sudah dipakai — nilai marginal perlu divalidasi.

## Rekomendasi

- **Adopsi — prioritas rendah (minor).** Pertimbangkan hanya bila ada kebutuhan diskusi in-context (mis. komentar di task sudah cukup?).
- **Alternatif lebih murah**: perkuat **komentar/notifikasi kontekstual** pada modul yang ada (task, approval) ketimbang membangun messenger penuh.
- **Penempatan usulan** (bila jadi): perluas [[Microservices - Notification Service]] menjadi 2 arah, atau dok `IT - Internal Messaging`.

## Risiko & catatan jaga sistem berjalan

- Real-time (websocket/Pusher) menambah beban infra; nilai vs biaya harus jelas sebelum mulai.
- Jangan jadikan kanal komunikasi kritis tanpa retensi/audit (lihat [[IT - Security]]).

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[Microservices - Notification Service]] · [[Microservices - Task Management Service]] · [[IT - Security]]
