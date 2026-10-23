## Deskripsi

*Endpoint **notification-service** (inbox, splash, article, FCM, WhatsApp). Gateway: `/api/notification/*`. Open routes pakai service key `?key=NOTIFICATION_SERVICE_KEY`. Grounded ke `services/notification/main.go`.*

- **Implementasi**: [[Microservices - Notification Service]] · **Status**: ✅
- **Indeks**: [[API - Index]]

## Inbox · Splash · Article (JWT via gateway)
| Method | Path | Fungsi |
|---|---|---|
| GET/DELETE | `/inbox` | List inbox (`?count=unread|read|all`, `?id=` mark read) / hapus |
| GET | `/inbox?page=N` | Paginasi **opt-in** (`?limit=` bawaan 15 batas 100, `?status=unread|read`) → `{data, pagination}` |
| POST | `/inbox/read-all` | Tandai semua belum-dibaca milik pemanggil → `{"modified": n}` |
| GET/POST/DELETE | `/splash` | List/buat (multipart)/hapus splash promotion |
| GET/POST/DELETE | `/article` | List (`?recent=`)/buat (multipart)/hapus artikel |
| GET | `/data-type/:dt` | Enum (inbox-category) |

## Open routes (service key `?key=`)
| Method | Path | Fungsi |
|---|---|---|
| POST | `/inbox/send` | Simpan notifikasi ke inbox (category tervalidasi) **lalu push ke browser DAN ponsel**. `400` category tak dikenal · `503` database belum terhubung |
| POST | `/wa/send-personal` | Kirim WhatsApp personal. Body `{employee_id \| phone_number, message}` |
| POST | `/wa/send-group` | Kirim WhatsApp grup. Body `{group, message, title?}`; `group` = alias (tabel di bawah). `400` field wajib kosong atau field tak dikenal · `500` NotifAPI membalas selain 200 |
| POST | `/fcm/send-personal` · `/fcm/send-department` · `/fcm/send-broadcast` | Kirim/broadcast FCM (`?platform=mobile|web_browser`) |

### Alias grup WhatsApp (`group` di `/wa/send-group`)
| Alias (tidak peka huruf besar-kecil) | Env id grup |
|---|---|
| `it` · `tech development` | `WHATSAPP_IT_GROUP_ID` |
| `it-alert` | `WHATSAPP_IT_ALERT_GROUP_ID` |
| `sales` | `WHATSAPP_SALES_GROUP_ID` |

> ⚠️ Alias di luar tabel **tidak ditolak** service ini: `group_id` terkirim kosong ke NotifAPI. Dan rute publik gateway `POST /public/feedback?group=<alias>` (body `{message}`) yang meneruskan ke sini **selalu membalas `{"success": true}`** selama service ini bisa dihubungi, apa pun balasan `/wa/send-group`; `group` diambil dari query, `title` tidak diteruskan. Detail: [[Microservices - Notification Service]] · [[API - API Gateway]].

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/debug/fcm` | Test FCM (debug) |

> Cron harian 03:00 WIB hapus inbox >2 bulan ([[IT - Background Jobs & Schedulers]]).

> ⚠️ **`/inbox/send` mengipas sendiri ke dua kanal sejak 2026-08-22.** Service pengirim yang sudah memanggilnya **tidak boleh** memanggil `/fcm/send-*` lagi — penerimanya akan mendapat notifikasi ponsel dua kali. `/fcm/send-*` tetap dipakai untuk pengiriman yang memang bukan notifikasi inbox (pengingat presensi dari cron). Alasan & urutan deploy: [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]].

> [!warning] `GET /inbox` TANPA `?page` wajib tetap array telanjang
> MyBharata membaca badan respons mentah lalu menguji `data is List`. Begitu balasan
> bawaannya dibungkus jadi objek, uji itu gagal dan cabang `else`-nya mengembalikan **list
> kosong, bukan galat** — inbox jadi kosong tanpa satu pun pesan. APK yang sudah terpasang
> tak bisa dipaksa update, jadi ini kontrak permanen, bukan sampai rilis mobile berikutnya.
> Paginasi karena itu **opt-in**. Detail: [[Microservices - Notification Service]].

## Dokumen Terkait
- [[Microservices - Notification Service]] · [[IT - Background Jobs & Schedulers]] · [[API - Index]]
