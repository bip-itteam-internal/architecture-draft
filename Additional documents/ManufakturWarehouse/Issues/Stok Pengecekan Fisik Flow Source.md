
Mermaid file
```
---

config:

  layout: elk

---

flowchart TB

    START(["Mulai\nTim Gudang"]) --> N1["① Pengecekan Stok Fisik\nHitung semua item di gudang"]

    N1 --> D1{"Stok Rusak /\nKadaluarsa?"}

    D1 -- Ya --> APP["Gunakan MyBharata untuk\nInput data &amp; foto item rusak\n dengan berat/kg"]

    APP --> KARANTINA["Pindah ke\nGudang Karantina"]

    KARANTINA --> N2["② Hitung Selisih Stok\nSistem vs. Fisik"]

    D1 -- Tidak --> N2

    N2 --> N3["③ Input Selisih & Foto ke Aplikasi\n Stock Opname Report"]

    N3 --> N4["④ Cetak Berita Acara Resmi\nSemua pihak tandatangan"]

    N4 --> D2{"Persetujuan TTD\nDisetujui?"}

    D2 -- Ya --> N5["⑤ Jalankan Penyesuaian Inventaris\nDi software Accurate"]

    N5 --> FINISH(["Selesai"])

    D2 -- Tidak --> N3

  

     N1:::teal

     APP:::red

     KARANTINA:::green

     N2:::teal

     N3:::red

     N4:::orange

     N5:::green

    classDef teal stroke:#2dd4bf,fill:#f0fdfa

    classDef green stroke:#4ade80,fill:#f0fdf4

    classDef red stroke:#f87171,fill:#fef2f2

    classDef orange stroke:#fb923c,fill:#fff7ed

```