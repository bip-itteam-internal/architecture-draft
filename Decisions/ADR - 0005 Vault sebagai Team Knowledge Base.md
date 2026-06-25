## ADR 0005 — Vault sebagai Team Second Brain (Runbooks + Workspace)

- **Status**: ✅ Accepted
- **Tanggal**: 2026-06-25
- **Konteks dok**: [[CLAUDE]] · [[IT - SOP Dokumentasi Vault]] · [[HOMEPAGE]]

## Context

Vault `architecture-draft/` sudah matang sebagai KB arsitektur grounded-in-code, tapi belum punya rumah untuk pengetahuan operasional non-kode (runbook/onboarding/troubleshoot) maupun corong capture (daily note/notulen). Detail: design `.agent-kit/docs/2026-06-25-vault-second-brain-design.md`.

## Decision

Tambah dua area non-domain:
- **`Runbooks/`** (`RUN -`) — operasional non-kode, **tetap grounded + di-publish** ke wiki.
- **`Workspace/`** (`Inbox/` + `Meetings/` `MTG -`) — corong capture **privat, di-exclude dari publish**, dikecualikan dari grounded/status/template/gate-wikilink. Capture "naik kelas" → dok domain / `RUN -` / `ADR -`.

Stream bisnis/keputusan **tanpa folder baru** — reuse `Decisions/` (ADR) + "Latar Belakang" dok domain. Repo privat → `Workspace/` tetap di git, hanya di-exclude dari export wiki.

## Consequences

- ➕ Pengetahuan operasional & capture punya rumah; alur "naik kelas" jelas.
- ➕ Satu graph/search; pemisahan publik/privat lewat satu garis (`Workspace/**`).
- ➖ Butuh disiplin agar `Workspace/` tetap ramping (bukan tempat sampah).
- ⚠️ Mekanisme exclusion publish persis tergantung tool export (TBD — lihat design doc).
- 🔗 Aturan dikodifikasi di [[CLAUDE]] §2/§3 + [[IT - SOP Dokumentasi Vault]].

## Dokumen Terkait

- [[CLAUDE]] · [[IT - SOP Dokumentasi Vault]] · [[HOMEPAGE]] · [[RUN - Onboarding Developer Baru]]
