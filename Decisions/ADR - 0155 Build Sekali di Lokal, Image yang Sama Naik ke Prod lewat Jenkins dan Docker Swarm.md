# ADR - 0155 Build Sekali di Lokal, Image yang Sama Naik ke Prod lewat Jenkins dan Docker Swarm

> **Status**: 🟡 **Diusulkan**, 2026-10-06, hasil brainstorming sesi Tech Development. Menunggu tiga hal: diterima pemilik keputusan (tulis `🟢 Diterima, <tanggal>, oleh <login/jabatan>` di baris ini), persetujuan manajemen atas satu jendela downtime migrasi (§12), dan kapasitas host Hyper-V yang terukur (§ Belum Diputuskan). Nol implementasi.

%% Vault ini PUBLIK: tak ada kredensial, nama orang, maupun rincian celah yang belum ditambal di dokumen ini. %%

## Untuk Manajemen

**Masalahnya dalam satu kalimat.** Aplikasi produksi saat ini dibangun langsung di server produksi tanpa uji otomatis sebelumnya, tiap deploy mematikan service beberapa detik, dan cadangan datanya masih tersimpan di server yang sama.

**Yang diputuskan.** Semua aplikasi dibangun dan diuji **sekali** di server kantor (VM 121). Image yang sama persis lalu naik ke produksi lewat **satu tombol** yang ditekan tim IT. Produksi dijalankan **Docker Swarm**, sehingga update tidak mematikan layanan dan rollback berjalan otomatis bila versi baru tidak sehat. Cadangan produksi **ditarik setiap hari ke VM backup di kantor**, dan pemantauan dipusatkan di **Grafana**.

**Biaya.** Seluruh software open source. Fase F0–F3 tanpa biaya tambahan, asalkan RAM server kantor bisa ditambah dari host yang ada.

**Yang diminta dari manajemen.** Satu jendela downtime terjadwal di jam sepi untuk migrasi (§12). Ini pengecualian sekali dari arahan "deploy tanpa downtime" 2026-06-29; deploy rutin sesudahnya tetap tanpa downtime.

**Yang tidak dijanjikan.** Kubernetes dan Kafka belum dipasang sekarang. Keduanya ada di peta beserta pemicunya (§1, §6).

## Deskripsi

*Arsitektur CI/CD dan runtime untuk semua aplikasi di VPS produksi: build dan uji di VM lokal 121, registry dan monitoring di lokal, promosi image ke produksi lewat tombol Jenkins, orkestrasi Docker Swarm di produksi, backup ditarik ke VM lokal.*

- **Berlaku untuk**: `bip-erp`, `erp-frontend`, `Sistem-Distribusi-Offline`, `Log-Direktur`, `career-bharata`, `audit-bharata`, `form-survey`, dan hoppscotch (image pihak ketiga, versinya dipatok). MyBharata tetap lewat Codemagic ([[IT - CI-CD]]).
- **Diukur ke**: VPS produksi dan VM 121, 2026-10-06, read-only.
- **Peta visual** (artifact privat, butuh akses): https://claude.ai/artifact/V9oYm7g3aH5BG5ZKxrwtAv. Peta adalah salinan bertanggal; yang mengikat dokumen ini.

## Context

### Keadaan terukur 2026-10-06

| | VPS produksi (Biznet) | VM 121 (kantor) |
|---|---|---|
| CPU / RAM | 8 vCPU · 15 GiB, sisa ±6 GiB, swap 3,7 GiB terpakai | 12 vCPU · **11 GiB**, swap **5,6 GiB** terpakai |
| Disk | root 88 GB, **81%**; `/backup` 98 GB, 40% | 139 GB, **86%** |
| Container | 76, termasuk 6 aplikasi di luar bip-erp | 54 |
| Catatan | 27 instance mongod memakan 6,1 GB RAM; journal + `diagnostic.data` 12,5 GB; build cache 12,4 GB yang tak pernah ter-prune (178 kali prune harian membebaskan 0 B); healthcheck `mongosh` di 26 mongod tiap 5–10 detik, ±0,5 detik CPU per cek, perkiraan ±2,3 core terus-menerus dari ±4,2 core yang sibuk | build cache 33,4 GB; 831 volume anonim yatim ±7,7 GB |

VPS produksi **belum bisa di-upgrade** untuk saat ini.

### Cara kerja sekarang

- **Deploy produksi = build di server produksi**: `git reset --hard origin/main` lalu `docker compose up -d --build <service> --no-deps` ([[RUN - Deploy Microservices bip-erp]]). Container lama dimatikan sebelum yang baru hidup.
- **Tak ada gerbang otomatis**: workflow GitHub Actions dimatikan, tak ada registry, tak ada uji sebelum naik ([[IT - CI-CD]]). Kegagalan "merged tapi biner lama yang melayani" sudah terjadi berulang.
- **Versi yang berjalan tak bisa dijawab pasti**; [[ADR - 0140 Versioning Rilis SemVer per Repo dari Tag Git]] sudah memutuskan versi dibakar ke image, belum diimplementasikan.
- **Backup** harian ±2,4 GB ke disk `/backup` di VPS yang sama, retensi 15 hari, tanpa alert ([[IT - Backup & DR]]).
- **Monitoring**: Beszel dan Uptime Kuma ([[IT - Monitoring System]]). Stack Grafana + Prometheus + Loki sudah ditulis di `bip-erp/infra/monitoring` tapi tidak berjalan; Promtail di dalamnya sudah EOL sejak 2 Maret 2026.
- **Kafka** tidak ada. Antrean webhook sudah ada di [[Microservices - Integration Service]] (`webhook_log` + `webhook_task` dengan `attempts`/`next_at`), jadi Kafka tidak dibutuhkan sebagai penampung webhook.

### Arahan manajemen 2026-06-29

Deploy tidak boleh menyebabkan downtime (poin 6), dan data utama server dicadangkan ke lokal (poin 4).

## Decision

1. **Docker Swarm, bukan K3s/K8s.** Produksi satu VPS: kemampuan utama Kubernetes (penjadwalan dan pemulihan lintas node) tak terpakai, sementara K3s membawa containerd kedua di disk yang sudah 81%. Swarm memakai engine yang sama, membaca file compose yang ada, dan memberi rolling update, healthcheck gating, serta rollback. **Pemicu pindah ke K3s: produksi menjadi ≥3 VPS di region yang sama** (F5). Satu cluster yang membentang kantor dan Biznet ditolak, karena kantor di balik NAT dan produksi akan ikut goyah saat internet kantor putus.
2. **Build sekali, image yang sama naik.** Produksi berhenti membangun dari checkout. Image diberi tag versi git + sha sesuai [[ADR - 0140 Versioning Rilis SemVer per Repo dari Tag Git]].
3. **Jenkins di VM 121, tombol approve untuk seluruh tim IT.** Jenkins memakai poll (121 di balik NAT, webhook GitHub tak bisa masuk). Langkah promosi ke produksi berhenti di `input` dengan `submitter` = grup `it-deploy`, yang ditegakkan Jenkins, bukan disiplin. Sesudah tombol ditekan, push, rolling update, verifikasi (versi di `/health`, umur image, healthcheck), dan rollback berjalan otomatis. Agent tidak menekan tombol ini (aturan tim: deploy produksi dijalankan manusia).
4. **Registry dan stack Grafana di VM 121.** Karena VPS belum bisa di-upgrade, produksi hanya memegang agen monitoring (Grafana Alloy menggantikan Promtail, node-exporter, cAdvisor; perkiraan ±0,5 GB RAM) dan 2 versi image terakhir per service. Rollback tetap tidak bergantung internet kantor karena image sebelumnya masih ada di produksi.
5. **Lapisan data tetap compose, di luar pipeline.** Mongo, Postgres, MinIO, dan Redis tidak masuk Swarm; `start-first` pada database berarti dua proses membuka volume yang sama.
6. **Kafka di peta, belum dipasang** (F4). Dipasang saat use case pertamanya diputuskan; kandidatnya notifikasi antar-service yang kini best-effort, atau pengganti `SyncCollection` berbasis polling.
7. **Siap-GitOps, gerbang tetap Jenkins.** File stack dan tag image disimpan di repo deploy sejak F0, dan Jenkins men-commit tiap kenaikan. Agen GitOps (Portainer CE atau SwarmCD) baru dipasang saat branch protection tersedia, karena tanpa itu merge PR tidak bisa dipaksakan menjadi gerbang. Argo CD hanya mendukung Kubernetes, jadi menyusul di F5.
8. **Backup ditarik ke VM backup lokal yang baru.** VM kecil (2 vCPU, 2 GB, ±200 GB) menarik `/backup` lewat WireGuard setiap 03:00 dengan user SSH read-only. Produksi tak memegang kredensial apa pun ke lokal, jadi salinan lokal tak bisa dihapus dari produksi. Retensi 30 harian + 12 bulanan, checksum dicocokkan, uji restore bulanan, alert WA bila gagal. Tidak langsung ke host Hyper-V, karena host itu induk semua VM kantor.
9. **Staging memakai data dev yang ada.** Smoke test memeriksa bentuk respons lewat gateway; data pribadi dan gaji produksi tidak keluar ke 121.
10. **`.env` tetap satu-satunya sumber, di produksi.** `docker stack deploy` tidak membaca `.env` untuk substitusi `${VAR}`, jadi file stack dirender dengan `docker compose config` saat deploy, dan **gerbang menolak variabel yang kosong** (kelas kegagalan "Defaulting to a blank string" yang sudah pernah mematikan fitur). Jenkins tidak memegang isi `.env`, hanya kunci SSH deploy. Swarm secrets atau SOPS menyusul bersama GitOps.
11. **Semua aplikasi di produksi ikut pipeline**, masing-masing dengan Jenkinsfile dan file stack. Lapisan data mereka (termasuk Postgres) tetap mengikuti §5.
12. **Migrasi produksi ke Swarm (F2) big-bang, sekali**, di jam sepi, dengan persetujuan manajemen dan jendela yang diumumkan. Geladi penuh di 121 lebih dulu; bila belum hijau dalam 30 menit, rollback (`docker stack rm` lalu `docker compose up -d`). Deploy rutin sesudahnya tetap tanpa downtime (`start-first`).

**Default teknis yang ikut diputuskan:**
- `docker swarm init --default-addr-pool 10.200.0.0/16`, karena pool bawaan `10.0.0.0/8` mencakup LAN kantor `10.10.10.0/24`, dan overlay yang mendapat subnet itu akan menelan lalu lintas ke 121 tanpa galat. WireGuard memakai `10.99.0.0/24`.
- Overlay network `attachable` dengan alias sama dengan nama service sekarang, sehingga container compose (Mongo, nginx-proxy-manager) bisa bergabung dan `*_MODULE_URL` tak berubah.
- Urutan deploy: BE sebelum FE bila kontrak berubah. Notifikasi ke grup WA "BIP Notification Center" yang sudah ada.

## Consequences

**Yang membaik**
- Deploy rutin tanpa downtime, rollback dalam hitungan detik dan otomatis bila healthcheck gagal.
- Build tak lagi memakan CPU dan disk produksi (±11 GB build cache di disk root lepas).
- Tiap perubahan diuji dan dinaikkan ke staging dengan image yang sama sebelum tombol produksi muncul.
- Kegagalan "merged tapi belum naik" tertangkap verifikasi otomatis, bukan oleh pengguna.
- Versi yang berjalan tercatat di repo deploy dan ditandai di grafik Grafana.
- Backup punya salinan di lokasi kedua yang tak bisa dihapus dari produksi.

**Yang dibayar**
- Cakupan besar: tujuh repo masuk pipeline.
- VM 121 harus ditambah RAM (≥24 GiB) dan disk (≥250 GB, atau dibersihkan lebih dulu).
- Internet kantor menjadi jalur deploy dan jalur Grafana. Saat putus, deploy dan Grafana berhenti; produksi tetap berjalan dan Uptime Kuma tetap memantau dari luar.
- Satu kali downtime terjadwal untuk migrasi.
- Tim perlu menguasai Swarm dan Jenkins; runbook deploy ditulis ulang di F2.

**Syarat agar keuntungannya nyata (diaudit sebelum F2)**
- Tiap service punya healthcheck. Tanpanya, versi baru dianggap sehat seketika dan "tanpa downtime" tidak berlaku.
- Job terjadwal in-process (reconciler, sweep, sync marketplace; [[IT - Background Jobs & Schedulers]]) aman bila jalan dua kali sesaat selama `start-first`, atau diberi kunci.

## Fase

| Fase | Isi | Menyentuh produksi |
|---|---|---|
| **F0 Fondasi** | WireGuard 121 ↔ Biznet · registry di 121 · repo deploy · VM backup + rsync pull · versi di image (ADR 0140) | agen WireGuard + user read-only backup |
| **F1 Jenkins di 121** | bersihkan disk + tambah RAM 121 · build + test semua app · Swarm staging dengan data dev | tidak |
| **F2 Produksi ke Swarm** | audit healthcheck + job terjadwal · geladi di 121 · big-bang sekali · jalur deploy lama dimatikan | ya, satu jendela |
| **F3 Observability** | Grafana stack di 121 · agen Alloy di produksi · alert WA + anotasi deploy | agen saja |
| **F4 Kafka** | saat use case pertama diputuskan | TBD |
| **F5 K3s** | pemicu: produksi ≥3 VPS satu region · GitOps penuh dengan Argo CD | TBD |

## Belum Diputuskan (TBD)

- **Kapasitas host Hyper-V** dan dari mana RAM 121 diambil. Kandidat terkuat: VM produksi lama yang masih menyala tapi tidak dipakai ([[IT - Server, VMs and Databases]]).
- VM backup dibuat baru atau memakai ulang VM yang ada.
- Tanggal dan pemilik jendela migrasi F2.
- Use case pertama Kafka.
- Retensi akhir data monitoring di 121 (rancangan awal: metrik 90 hari).

## Dokumen Terkait

- [[IT - CI-CD]] · [[RUN - Deploy Microservices bip-erp]] · [[IT - Catatan Rilis ERP]]
- [[IT - Server, VMs and Databases]] · [[IT - Environment Inventory]]
- [[IT - Monitoring System]] · [[Microservices - Monitoring Service]]
- [[IT - Backup & DR]]
- [[ADR - 0140 Versioning Rilis SemVer per Repo dari Tag Git]] · [[ADR - 0002 Database-per-Service]] · [[ADR - 0042 Sistem Distribusi Memakai Gateway Sendiri]]
- [[Microservices - Integration Service]] · [[IT - Background Jobs & Schedulers]]
