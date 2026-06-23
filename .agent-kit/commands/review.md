---
description: Review diff — bug + konsistensi vs arsitektur
---

Review pekerjaan sebelum /sync-docs & /wrap.

Langkah:
1. Lihat diff project aktif (perubahan sesi ini, belum/baru di-commit).
2. Cek dua dimensi:
   a. **Korrektness/bug**: error handling, edge case, regresi.
   b. **Konsistensi arsitektur**: apakah implementasi menyimpang dari dok di
      `architecture-draft/`? Endpoint/kontrak/ownership data sesuai? (rujuk dok dari /start-task)
3. Sajikan temuan: severity + lokasi (file:line) + saran fix.
4. Bila ada temuan kritis, sarankan kembali ke /implement; bila bersih, lanjut /sync-docs.
