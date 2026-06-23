---
description: Eksekusi rencana — TDD default-adaptif
---

Eksekusi rencana dari /plan.

Aturan TDD (default-adaptif):
- Jika project punya test infra (mis. *_test.go untuk Go, atau test runner di
  package.json untuk JS): tulis test dulu (gagal) → implement minimal → test hijau → ulang.
- Jika project BELUM punya test infra sama sekali: jangan berhenti; implement sesuai
  rencana, lalu sarankan menambah test untuk unit baru.

Langkah:
1. Untuk JS/TS pakai **pnpm**, BUKAN npm/yarn (lihat .claude/CLAUDE.md).
2. Kerjakan per langkah kecil dari rencana; commit sering (per langkah logis).
3. Jaga perubahan dalam lingkup rencana. Temuan di luar lingkup → catat untuk /review,
   jangan langsung dikerjakan.
