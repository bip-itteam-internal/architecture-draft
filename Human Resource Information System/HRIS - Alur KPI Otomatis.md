## Deskripsi

*Penjelasan otomasi skor KPI dalam bentuk diagram. Ada **dua versi**: gambaran besar untuk pembaca non-teknis, dan alur rinci untuk dev. Keduanya tersimpan di `Additional documents/Excalidraw/`; halaman ini catatan penunjuknya, sekaligus supaya diagramnya terjangkau pencarian vault (folder `Additional documents/` tidak diindeks).*

- **Bentuk**: dua diagram Excalidraw
- **Status**: ✅ Selaras dengan keadaan produksi per **2 Agustus 2026**

| Versi | Untuk siapa | Menjawab apa |
|---|---|---|
| [[HRIS - Alur KPI Otomatis.excalidraw]] | SPV, Leader, HR, direksi | Kenapa skornya belum terisi sendiri padahal matriknya sudah lengkap |
| [[HRIS - Alur KPI Otomatis Rinci.excalidraw]] | Dev departemen | Sembilan langkah yang benar-benar dijalankan employee-service, beserta katalog rumus, arah target, dan jalur kegagalan |

### Versi gambaran besar

![[HRIS - Alur KPI Otomatis.excalidraw]]

### Versi rinci

![[HRIS - Alur KPI Otomatis Rinci.excalidraw]]

## Rangkaiannya, dalam lima langkah

1. Tim bekerja seperti biasa (Kyura, IT, HR, Gudang).
2. Pekerjaannya tercatat lewat aplikasi (absensi, tiket, monitoring, TikTok).
3. Catatannya tersimpan di database.
4. Sistem menghitung skor tiap orang, dibandingkan dengan **matrik KPI per posisi**.
5. Skor KPI terisi sendiri; atasan tinggal memeriksa, bukan menebak.

Mesin langkah 4 sudah jalan di produksi sejak 1 Agustus 2026. Yang belum: **0 dari 70 matrik** diisi pengaturannya, jadi hari ini belum ada satu posisi pun yang benar-benar otomatis.

## Tiga syarat yang sering terlupa

Rangkaian di atas terlihat mulus, tetapi tiap langkah punya syarat yang selama ini justru jadi penghambat sebenarnya. Ketiganya **bukan pekerjaan kode**.

| Syarat | Buktinya di sistem sekarang |
|---|---|
| Aplikasinya sungguh dipakai dan diisi lengkap | Tenggat tiket tidak pernah diisi, jadi kecepatan penyelesaian tidak bisa dihitung sama sekali (**0 dari 293 tiket**) |
| Sistem tahu data itu milik siapa | **86.845 video** tersimpan, tapi baru **10 dari 41 ICC** tercatat memegang toko. Datanya ada, pemiliknya yang belum |
| Matriknya mungkin diukur | Satu metrik meminta 70% video berjenis VSA, padahal dari **104.269 video hanya ada 73**. Semua orang akan dapat nol, selamanya |

## Prinsip yang mengikat mesinnya

Kalau salah satu syarat belum terpenuhi, sistem **tidak mengarang angka**. Metrik itu ditandai "belum bisa dihitung" beserta alasannya, dan penilaiannya kembali manual seperti sekarang.

Alasannya sederhana: angka karangan lebih berbahaya daripada kolom kosong, karena tidak ada yang curiga padanya. Kolom kosong terlihat dan ditanya; angka yang tampak wajar tetapi salah akan dipakai menilai orang tanpa seorang pun memeriksanya.

## Dokumen Terkait

- [[HRIS - Otomasi Skor KPI]] (analisis kelayakan, peta sumber data, rencana bertahap)
- [[HRIS - Matriks KPI per Departemen]] (isi lengkap 311 metrik produksi per departemen)
- [[RUN - Menambah Metrik KPI Otomatis]] (cara dev menambah metrik otomatis)
- [[HRIS - Key Performance Index]] (mekanisme scoring dan RBAC)
