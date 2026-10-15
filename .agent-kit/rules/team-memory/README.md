# Ingatan Tim — berkas topik (detail)

> Indeksnya `../team-memory.md`: hanya berkas itu yang di-import `CLAUDE.md` dan ikut tiap sesi.
> Yang di folder ini dibaca **ON-DEMAND**, lewat pemicu di § Peta indeks — pola yang sama dengan
> `plan-checklist.md` / `review-checklist.md`. Isinya dipecah dari satu berkas 123 KB (2026-10-15);
> **judul `##`/`###` aslinya dipertahankan persis**, jadi rujukan lama `team-memory § <judul>`
> tetap bisa dicari. Update cukup `git pull architecture-draft`, tanpa re-run `init`.
> Yang mencari satu kata di seluruh ingatan tim: `git grep -n "<kata>" -- .agent-kit/rules/team-memory*`
> (`git grep`, bukan ripgrep — berkas ber-byte NUL dilewati ripgrep, lihat `gotchas-lingkungan-windows.md`).

| Berkas | Isinya |
|---|---|
| `gotchas-lingkungan-windows.md` | Jebakan mesin dev Windows: NUL menghilangkan berkas dari pencarian, `git stash` lintas worktree, bukti "sudah merged", tool `Bash` yang timeout, `.claude/` hasil generate, aturan PR semua repo kode vs vault yang push langsung `main`, nomor ADR ganda. |
| `konvensi-git-rilis.md` | Branch, pesan commit, urutan deploy BE→FE, merge per-hunk yang menelan fitur, versioning rilis mobile, dan batas kewenangan deploy PROD. |
| `fe-konvensi-ui.md` | Aturan umum layar `erp-frontend`/MyBharata: kerangka bukan spinner, urutan reuse komponen, tiga angka `Sheet`, tombol kembali, padding, i18n, panduan per menu, input tanggal, struktur tabel HRIS. |
| `fe-tabel-filter.md` | Jebakan tabel daftar dan filter: kemampuan `MainTable`, batas `FilterTable`, draft filter, format tanggal, `ScrollArea` yang tak menggulir, lebar scrollbar, batas test jsdom. |
| `fe-bagan-chart.md` | Bagan: komponen bersama, `ChartContainer`, pilihan warna dan palet, id gradien, offset, `type="monotone"`, domain sumbu, deret kosong, batas uji recharts. |
| `fe-kpi-metrik.md` | KPI di layar: tiga jenis baris rincian, sumber mana yang mengisinya, gerbang `/kpi/sumber-katalog`, arti `auto_formula`. |
| `fe-push-notifikasi.md` | Push notification web (Firebase FCM): VAPID, probe yang menyesatkan, `catch` kosong, izin tanpa token, `NEXT_PUBLIC_*` saat build. |
| `fe-verifikasi-lokal.md` | Cara memverifikasi perubahan `erp-frontend`: lokal, bukan lewat CI, dan cara membandingkan dengan baseline. |
| `kalender-terpusat.md` | Kewajiban mendaftarkan feed ke `calendar-service` untuk fitur bertanggal, prinsip tiga lapis visibilitas, bentuk item, `PATCH` sebagian, lingkup yang sudah diputuskan. |
| `portal-persetujuan.md` | Kewajiban menyetor tahap persetujuan/tindakan ke Portal Persetujuan, cara mendaftar, dan siapa menyaring haknya. |
| `backend-go.md` | Gotcha service Go: tempat gerbang dicari, kunci YAML ganda, `c.JSON()` sebagai nilai galat, lapisan binding request, ID yang bukan `_id`, kategori inbox. |
| `backend-endpoint-daftar-service.md` | Memanggil endpoint daftar milik service lain: bentuk amplop, nama field, paginasi, `null` vs kunci hilang. |
| `repo-rbac-departemen.md` | RBAC `system_roles` vs hierarki org, dan kelas kegagalan label grup departemen ("HRGA") di FE maupun BE. |
| `mutasi-antar-tenant.md` | Memindahkan karyawan antar perusahaan: yang patah, yang tidak, dan urutan yang aman. |
| `atribusi-iklan-marketplace.md` | Atribusi order iklan vs organik di marketplace: arti "iklan", kunci join, tanggal yang sah, golongan yang disimpan. |
| `memori-sumber-kebenaran.md` | Cara membuktikan klaim, memakai graf kode, memperlakukan status yang bergerak, dan di mana aturan bisnis perusahaan sesungguhnya tinggal. |
| `skill-tooling-ai.md` | Command, skill, dan hook agent-kit: mana yang dipakai kapan, gerbang dan antreannya, jebakan yang sudah terukur. |
| `backlog-github-project.md` | Backlog GitHub Project #15: arti tiap Status, cara menautkan PR ke issue, sub-issue per repo, dan Definition of Ready sebelum agent boleh mengerjakan issue. |
