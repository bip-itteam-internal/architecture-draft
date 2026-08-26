# Order Production Workflow (Flow Source)

- **Status**: 🟡 Konsep / Source — sumber flowchart (Mermaid) alur order produksi **di sisi [[External - Accurate]]** (target qty → Work Order → baca BOM → simulasi → rilis).
- ⚠️ **Bukan** dokumentasi menu **Material Order (MO)** di WMS — itu entitas lain dengan koleksi & endpoint sendiri, lihat [[Manufacture - Material Order (SPK)]]. Dok ini sempat dijadikan sasaran wikilink beralias "Material Order" dari [[Manufacture - Dokumen Produksi Batch]]; sudah dialihkan 2026-08-26.

File Mermaid
```
flowchart TD

    START([Mulai\nInput Target Qty Barang Jadi])

  

    N1[1. Input Target Qty Barang Jadi\nTetapkan target produksi di Accurate]

    N2[2. Buat Work Order di Accurate\nWO menghubungkan target ke BOM]

    N3[/3. ⚙ Sistem Baca Database BOM\nAccurate baca BOM aktif otomatis/]

    N4[4. Kalkulasi Kebutuhan Bahan Baku\nOutput qty material via rumus BOM]

    D1{Perlu Ubah \n Formula?}

    N4b[Buat Versi BOM Baru\ncth: P-001-Rev1]

    N5[5. Simulasi via Work Order\nBandingkan: Sistem vs. Hitung PPIC]

    EDIT[Edit Revisi BOM]

    N6[6. Cek Laporan Analisa Prod. Order\nVerifikasi output sistem vs. fisik]

    D2{Data Cocok &\n Terverifikasi?}

    N7([✓ 7. Rilis Produksi Final])

  

    START --> N1 --> N2 --> N3 --> N4 --> D1

    D1 -- Ya --> N4b --> N5

    D1 -- Tidak --> N5

    N5 --> EDIT -. revisi .-> N5

    N5 --> N6 --> D2

    D2 -- Tidak --> EDIT

    D2 -- Ya --> N7

  

    style N3 stroke-dasharray: 5 5

    style EDIT fill:#c0392b,color:#fff

    style N7 fill:#27ae60,color:#fff
```

## Dokumen Terkait

- [[Manufacture - Material Order (SPK)]] (padanan alur ini di dalam WMS: SPK formula + No. Batch)
- [[Manufacture - Stock & Material Management]] (dok induk: BOM/formula & perencanaan kebutuhan)
- [[External - Accurate]] (Work Order & BOM aktif dibaca dari sini)
- [[Microservices - Manufacture Service]] (implementasi `manufacture_formula`)