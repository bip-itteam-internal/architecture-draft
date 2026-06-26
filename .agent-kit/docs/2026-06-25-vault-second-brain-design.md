# Design — Vault sebagai Team Second Brain (Pendekatan B)

> Status: Disetujui (brainstorming) · Tanggal: 2026-06-25 · Target: `architecture-draft/` (vault)

## Latar Belakang

`architecture-draft/` sudah matang sebagai **knowledge base arsitektur grounded-in-code**:
folder domain, konvensi penamaan `Prefix - Nama`, status marker (✅/⚠️/🟡/🔴), Templates,
`Decisions/` (ADR), `API Reference/`, `Reference/` (glosarium/RACI), `Logs/`, dan di-publish
ke wiki publik (`architecture.bharatainternasional.com`).

Yang belum ada untuk menjadikannya **"second brain" tim**: tiga stream pengetahuan
non-arsitektur — **operasional non-kode**, **capture harian/notulen**, dan **bisnis & keputusan**.
Stream ke-3 sebenarnya sudah ~80% terbangun (`Decisions/` + bagian "Latar Belakang" dok domain),
jadi fokus nyata = stream 1 & 2.

## Tujuan & Non-Tujuan

**Tujuan**
- Tambah rumah jelas untuk **runbook/how-to/onboarding/troubleshoot** (operasional non-kode).
- Tambah **corong capture** (daily notes, idea inbox, notulen rapat) yang bisa "naik kelas"
  jadi dok permanen.
- Pertahankan satu vault, satu graph, satu search; pisahkan **publik (wiki)** vs **privat (capture mentah)**
  dengan satu garis exclusion.
- Reuse mesin vault yang sudah ada (pola non-domain area + carve-out di `CLAUDE.md`).

**Non-Tujuan**
- Tidak menambah folder untuk stream "bisnis & keputusan" — reuse `Decisions/` (ADR) + dok domain.
- Tidak mengubah navigasi/HOMEPAGE secara besar (user tidak memilih gap navigasi).
- Tidak memindah vault ke Obsidian Publish berbayar / mengganti tooling export.
- Bukan second brain **pribadi** — ini untuk pengetahuan **tim/proyek bip-erp**.

## Keputusan Desain (hasil brainstorming)

| Topik | Keputusan |
|---|---|
| Stream yang ditambah | Operasional non-kode · Capture harian/notulen · (bisnis = reuse) |
| Tempat tinggal | **Vault yang sama**, area non-domain baru |
| Publik vs privat | `Runbooks/` **ikut publish**; `Workspace/` **di-exclude** dari publish |
| Visibilitas git repo | **Privat (hanya tim)** → `Workspace/` aman masuk git, cukup di-exclude dari export |
| Stream bisnis/keputusan | **Tanpa folder baru** — `Decisions/` (ADR) + "Latar Belakang" dok domain |
| Grounding `Workspace/` | **Dikecualikan** dari grounded-in-code, status marker, template, gate 0-broken-link |

## Struktur folder & penamaan

```
architecture-draft/
├── Runbooks/                    ← non-domain area BARU · PUBLISH ke wiki · aturan vault penuh
│   └── RUN - <Topik>.md         ex: RUN - Onboarding Developer Baru,
│                                    RUN - Restart Service Produksi,
│                                    RUN - Troubleshoot Login SSO
└── Workspace/                   ← non-domain area BARU · TIDAK di-publish · corong capture
    ├── Inbox/                   daily notes (YYYY-MM-DD.md) + idea capture (nama bebas)
    └── Meetings/                MTG - YYYY-MM-DD <Topik>.md
```

Prefix baru: **`RUN -`** → `Runbooks/`, **`MTG -`** → `Workspace/Meetings/`.
`Inbox/` bebas-prefix (capture cepat, gesekan minimum). Keduanya **flat** (tanpa sub-pohon domain),
mengikuti pola `Reference`/`Logs`.

## Aturan & exemption

- **`Runbooks/` = warga kelas-satu.** Grounded (prosedur harus benar-benar jalan), status marker
  berlaku, wikilink **wajib resolve** (0 broken). Ikut `CLAUDE.md` §1/§4/§5. Tetap di-publish karena
  berguna untuk onboarding & operasional tim.
- **`Workspace/` = dikecualikan**, bahasa carve-out sama seperti `Logs`:
  - Dikecualikan dari **grounded-in-code (§1)** — boleh berisi draf/ide/hipotesis.
  - Dikecualikan dari **status marker (§5)** dan **template (§6)**.
  - Dikecualikan dari **gate "0 broken wikilink" (§4)** — capture boleh nge-link ke catatan yang
    belum ada (itu TODO masa depan / pola Zettelkasten).
  - **Wajib**: dok yang dipublish (di luar `Workspace/`) tetap 0-broken — link **dari** dok publik
    **ke** `Workspace/` tidak diperbolehkan (akan jadi broken di wiki).

## Alur "naik kelas" (promotion) — inti second brain

```
Inbox / Meetings  ──matang──▶  rumah permanen                 ──▶ catatan mentah
(tangkap cepat)                (dok domain / RUN - / ADR -)        di-arsip / hapus
```

- Saat catatan Inbox/Meeting "matang", **isinya dipindah** ke rumah yang benar (dok domain,
  `RUN -`, atau `ADR -`), lalu catatan mentahnya ditandai selesai/diarsip/dihapus.
- `Workspace/` harus tetap **ramping**. Kalau menggembung → sinyal ada yang belum naik kelas.
- Stream bisnis/keputusan mendarat lewat alur ini ke `ADR -` (keputusan) atau "Latar Belakang"
  dok domain (konteks bisnis), **bukan** mengendap permanen di Inbox.

## Mekanisme exclusion publish

- **Satu garis**: seluruh `Workspace/` dikecualikan dari export wiki. Pendekatan dua-sabuk
  (mana pun yang didukung tool export saat publish):
  1. **Ignore-glob** path `Workspace/**` di konfigurasi tool export, dan/atau
  2. Default frontmatter `publish: false` pada dok `Workspace/` (banyak plugin export menghormatinya).
- **Git ≠ publish.** Repo privat → `Workspace/` **tetap di-commit** (kolaboratif), hanya tidak
  ikut ke HTML export/wiki publik.
- Mekanisme persis tergantung tool export yang dipakai saat publish (plugin export tidak aktif di
  `community-plugins.json` saat ini → publish dijalankan ad-hoc). **Lihat TBD-1.**

## Daftar perubahan (implementasi)

1. **`CLAUDE.md` (rulebook vault)** — daftarkan `Runbooks/` + `Workspace/` di §2 (area non-domain);
   tambah prefix `RUN -`/`MTG -` di §3; tambah bahasa exemption `Workspace/` di §1/§4/§5/§6;
   catat aturan exclusion publish.
2. **`Templates/`** — tambah `Template - Runbook.md`, `Template - Meeting Note.md`,
   `Template - Daily Note.md` (skeleton + placeholder `%% %%`, tanpa wikilink hidup, seperti template lain).
3. **`IT/IT - SOP Dokumentasi Vault.md`** — perluas decision-tree penamaan:
   kapan Runbook vs dok domain vs Inbox vs Meeting; dokumentasikan alur naik kelas.
4. **`HOMEPAGE.md`** — tambah baris index **Runbooks**; `Workspace/` sengaja **tidak** ditaut
   dari homepage publik.
5. **Buat folder + seed**: `Runbooks/RUN - Onboarding Developer Baru.md` (boleh awali dari materi
   `DEVELOPER GUIDE`), `Workspace/Inbox/.gitkeep` + 1 contoh daily note,
   `Workspace/Meetings/MTG - 2026-06-25 Contoh.md`.
6. **Wiring exclusion publish** — set ignore-glob/`publish: false` di tool export. **TBD-1.**
7. **(Opsional, dogfooding)** `Decisions/ADR - 0005 Vault sebagai Team Knowledge Base.md` —
   catat keputusan ini (Context → Decision → Consequences).

## Risiko & Mitigasi

- **Capture mentah bocor ke wiki** → satu garis exclusion `Workspace/**` + default `publish: false`;
  larangan link publik→Workspace agar tak ada jejak di wiki.
- **`Workspace/` menggembung jadi "tempat sampah"** → alur naik kelas eksplisit di SOP;
  Workspace ditegaskan ramping/sementara.
- **Runbook jadi usang (drift dari kenyataan)** → `Runbooks/` ikut grounded + status marker;
  masuk cakupan `/sync-docs`.
- **Bingung "ini taruh di mana"** → decision-tree di SOP (§3 perubahan) jadi rujukan tunggal.

## Pertanyaan Terbuka (TBD)

- **TBD-1**: Mekanisme exclusion publish yang persis bergantung pada tool export yang dijalankan
  saat publish wiki (plugin export tidak aktif di vault saat ini). Konfirmasi dengan yang menjalankan
  export; sementara itu pakai konvensi `Workspace/` + `publish: false` agar robust ke tool apa pun.
