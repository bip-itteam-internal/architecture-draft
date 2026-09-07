---
description: Dashboard AI Engineering Loop — HTML statis bergaya World Monitor dari data lokal + gh (SHIPPED, MIX, HOTSPOTS, LOOP, CYCLE, BASELINE, SESI), filter rentang/repo di halaman
---

Bangkitkan **dashboard** loop ke `.task-plans/dashboard.html` lalu buka di browser. Berkas, bukan
layanan (ADR 0077 §5): halaman me-refresh diri tiap 60 detik, dan `--loop <detik>` menulis
ulang datanya berkala tanpa server.

Panel dan sumbernya:

| Panel | Sumber | Catatan |
|---|---|---|
| SHIPPED, CYCLE, MIX, HOTSPOTS | `gh pr list` per irisan mingguan (bip-erp, erp-frontend) | MIX dari prefiks conventional judul PR (87 sampai 90% judul di sini berpola) |
| LOOP | `.task-plans/briefs`, `.task-plans/judge` | data lokal, sejak kit 1.15.0 |
| SESI | `.task-plans/sesi` | ditulis hook; sesi yang lahir sebelum kit 1.15.0 tidak muncul |
| BASELINE | `.agent-kit/baseline/*.json` | bertanggal; ukur ulang saat `main` bergerak jauh |
| SPEND, RISK | **tidak ada** | ditulis di kaki halaman, bukan diisi nol |

Argumen: `[--hari N]` (bawaan 30, data yang ditanam; filter 7/14/30 di halaman), `[--repo a,b]`,
`[--tanpa-gh]` (pakai cache `.task-plans/dashboard-data.json`, cepat/offline), `[--loop detik]`.

## Langkah

1. Jalankan (Windows):
   ```
   powershell -NoProfile -ExecutionPolicy Bypass -File .claude/hooks/dashboard.ps1 -Workspace "<ws>" [-Hari N] [-Repos a,b] [-TanpaGh]
   ```
   (mac/linux: `dashboard.sh`.) Tanpa `-TanpaGh` ia menarik PR lewat `gh` per irisan mingguan;
   untuk 30 hari dua repo sekitar satu sampai dua menit. Tampilkan baris ringkasnya
   (`PR n, brief n, judge n, sesi n`) dan **peringatan irisan penuh** bila ada: irisan yang
   mencapai batas 500 berarti angkanya KURANG dari kenyataan, katakan itu, jangan disembunyikan.
2. Bila `--loop N`: jalankan sebagai proses terlepas (`Start-Process powershell ... -Loop N`),
   cetak PID-nya dan cara menghentikannya.
3. Buka `.task-plans/dashboard.html` (`Start-Process` path-nya) dan cetak path-nya.
4. Bacakan yang menuntut tindakan, bukan seluruh angka: brief GAGAL (path worktree + log),
   sesi BASI (id + worktree), PR terbuka dari loop yang menunggu merge.

## Jangan

- Jangan menambah panel yang tidak punya sumber data. Nol palsu lebih buruk daripada kosong
  yang diberi keterangan.
- Jangan menyalin angka PR se-organisasi dari Papan Aktivitas Developer ke sini; cukup tautkan.
- Jangan mengubah tampilan di `dashboard.html` hasil; sunting `hooks/dashboard.template.html`
  di kit (satu-satunya penulis UI), lalu re-init.
