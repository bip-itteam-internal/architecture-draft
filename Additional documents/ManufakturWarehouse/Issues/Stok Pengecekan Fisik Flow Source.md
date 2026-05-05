
Mermaid file
```
flowchart TD

    START([Mulai\nTim Gudang])

  

    N1[① Pengecekan Stok Fisik\nHitung semua item di gudang]

    D1{Stok Rusak /\nKadaluarsa?}

    KARANTINA[Pindah ke\nGudang Karantina]

    N2[② Hitung Selisih Stok\nStok Sistem vs. Hitung Fisik]

    N3[③ Input Selisih & Foto\nKe Laporan Stock Opname]

    N4[④ Cetak Berita Acara Resmi\nSemua pihak tandatangan]

    D2{Persetujuan TTD\nDisetujui?}

    N5[⑤ Jalankan Penyesuaian Inventaris\nDi software Accurate]

    FINISH([Selesai])

  

    START --> N1 --> D1

    D1 -- Ya --> KARANTINA --> N2

    D1 -- Tidak --> N2

    N2 --> N3 --> N4 --> D2

    D2 -- Ya --> N5 --> FINISH

    D2 -- Tidak --o N3

  

    style KARANTINA fill:#1a7a4a,color:#fff

    style N3 fill:#c0392b,color:#fff

    style N4 fill:#c0392b,color:#fff

    style N5 fill:#1a7a4a,color:#fff

```