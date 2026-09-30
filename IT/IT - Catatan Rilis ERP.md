> **Status**: 🟡 **Konsep** — templat siap, **belum ada entri**. Entri pertama ditulis pada deploy produksi pertama sesudah [[ADR - 0140 Versioning Rilis SemVer per Repo dari Tag Git]] diterapkan.

## Deskripsi

*Catatan rilis payung ERP Bharata: satu baris per deploy produksi, merangkum versi `bip-erp`, `erp-frontend`, dan MyBharata yang berjalan sesudahnya. Dipakai untuk menjawab "ERP versi berapa sekarang" dengan satu nama. Ini **catatan, bukan sumber**: versi sebenarnya ada di tag git dan dilaporkan `/health` tiap service ([[ADR - 0140 Versioning Rilis SemVer per Repo dari Tag Git]] §2, §7).*

## Cara mengisi

Ditulis oleh **orang yang menjalankan deploy produksi**, sesudah gerbang versi lolos ([[RUN - Deploy Microservices bip-erp]] §1c, [[RUN - Deploy Frontend ERP ke Produksi]] §Versi rilis). Entri terbaru di **atas**.

- **Rilis**: `Rilis YYYY.MM.DD`, akhiran `.2`, `.3` bila lebih dari satu deploy produksi sehari.
- **bip-erp**: tag repo, lalu service yang **benar-benar dinaikkan** di deploy ini. Service yang tidak disebut tetap menjalankan versi lamanya; `/health` masing-masing yang menjawab versinya.
- **erp-frontend**: tag, atau `-` bila FE tidak dinaikkan.
- **MyBharata**: version name yang sedang di toko (Play / App Store), bukan yang sedang dibangun.
- **Catatan**: kebutuhan kecocokan antar-repo bila ada ("FE butuh BE ≥ v0.4.0"), dan tautan GitHub Release.

## Riwayat rilis

| Rilis | bip-erp (service dinaikkan) | erp-frontend | MyBharata | Catatan |
|---|---|---|---|---|
| _belum ada entri_ | | | | |

Tag `v0.1.0` sampai `v0.1.2` di kedua repo dibuat **sebelum** aturan ini ada dan tidak terikat pada satu deploy produksi tertentu, jadi tidak dicatat surut di sini. Rilis berikutnya dimulai dari `v0.2.0` di kedua repo (ADR 0140 §Consequences).

## Dokumen Terkait

- [[ADR - 0140 Versioning Rilis SemVer per Repo dari Tag Git]]
- [[RUN - Deploy Microservices bip-erp]] · [[RUN - Deploy Frontend ERP ke Produksi]]
- [[IT - CI-CD]]
