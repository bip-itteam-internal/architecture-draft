## Deskripsi

*Izin membuat tipe form tertentu ditempelkan pada **departemen**, bukan pada posisi atau peran modul, dan disimpan sebagai **daftar-larangan** yang bawaannya membolehkan semua. Ini sumbu izin di luar [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]], dan ADR ini menjelaskan kenapa itu dibenarkan.*

- **Status**: ⚠️ **Diimplementasikan penuh 2026-08-08 (BE + FE), BELUM merge dan belum deploy** — branch `feat/form-builder-izin-tipe-per-departemen` di `bip-erp` dan `erp-frontend`. Desain kerja: `erp/docs/superpowers/specs/2026-08-08-tipe-form-per-departemen-design.md`
- **Berlaku untuk**: [[Microservices - Form Builder Service]] · [[APP - Web ERP]]

## Context

Form Builder punya empat tipe form (`survey`, `evaluation`, `checklist`, `kaizen`) dan setiap departemen yang boleh memakainya bisa membuat **semua**-nya. Kebutuhan tiap departemen berbeda, dan pemilik produk meminta dua hal: aturan yang benar-benar ditegakkan (departemen X tak boleh membuat tipe Y), sekaligus dropdown yang tak menawarkan tipe yang tak pernah dipakai.

Keduanya ternyata satu pekerjaan. Kerapian adalah konsekuensi gratis dari aturannya, **asalkan server yang memberi tahu klien apa yang boleh**. Bila FE menyaring dengan aturannya sendiri, lahir salinan kedua yang pasti menyimpang.

Yang menjadikan ini keputusan arsitektur, bukan sekadar fitur: [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] menetapkan hak menempel di **posisi**, sedangkan ini menempel di **departemen**. Menambah sumbu izin diam-diam adalah cara sistem izin berubah jadi beberapa sistem yang saling bertentangan.

## Decision

**1. Izinnya menempel di departemen, bukan di posisi.**

Kepemilikan form di Form Builder sudah berupa `owner_department` sejak PR #869, dan itu diputuskan sadar: `system_roles` adalah hak akses modul, bukan hierarki organisasi, sehingga orang yang kebetulan punya peran di dua modul sempat melihat form dua tim sekaligus.

Pertanyaan yang dijawab aturan ini adalah *"departemen ini menjalankan proses apa"*, bukan *"orang ini boleh apa"*. Semua orang di General Affair menjawabnya sama. Menempelkannya di posisi berarti menyalin jawaban yang identik ke setiap posisi lalu menunggu salah satunya menyimpang. Karena itu **ini konfigurasi departemen, bukan perluasan RBAC** — dan `system_roles` tetap menentukan siapa yang boleh membuka Form Builder sama sekali.

**2. Yang disimpan adalah tipe yang DILARANG, bukan yang diizinkan.**

Bawaannya semua boleh; tak ada baris berarti tak ada larangan.

Dengan daftar-izin, tipe form yang ditambahkan nanti tak terlihat oleh satu pun departemen sampai seseorang menyunting tiap baris — fiturnya merge, deploy, dan **diam**. Itu kelas kegagalan yang sudah berulang di repo ini: `recurrence` mustahil dinyalakan selama tiga hari "live" karena satu baris pengikatan hilang, dan kategori inbox Kaizen hilang tanpa jejak karena tak terdaftar di daftar-izin `shared-library`.

Dengan daftar-larangan kegagalannya berbalik arah: sebuah departemen mendapat tipe yang tak diniatkan IT. Terlihat, tak merusak data, diperbaiki dalam semenit.

> [!note] Ini TIDAK membatalkan pilihan daftar-izin di papan ide Kaizen
> Papan Kaizen memilih daftar-izin untuk tipe field, dan itu tetap benar **di sana**: yang dijaga kebocoran ke layar seluruh karyawan, jadi tipe baru memang harus tersembunyi sampai sengaja diizinkan. Di sini tak ada yang bocor. **Arah bawaan ditentukan oleh apa yang rusak bila salah**, bukan oleh keseragaman gaya.

**3. Aturan berlaku saat tipe DITETAPKAN, bukan saat form disunting.**

Hanya di pembuatan form dan penggantian tipe selagi draft. Mencabut sebuah tipe **tidak menyentuh** form yang sudah ada — tetap hidup, tetap bisa disunting, tetap terbaca.

Ini pelajaran yang baru dibayar hari yang sama saat tipe `request` dihapus: menegakkan tipe pada setiap validasi membuat form yang tipenya tak lagi sah **gagal disunting `403`/`400` tanpa jalan keluar**, karena tipe hanya bisa diubah selagi draft dan form terbit tak bisa mundur ke draft.

**4. Yang menetapkan aturan adalah IT** (`system_roles["it"]`, tingkat `supervisor` atau `admin`).

Form Builder ditempatkan sebagai tooling platform milik Tech Development yang dipakai bersama HRGA, jadi konfigurasinya mengikuti kepemilikan tooling. Departemen **tidak** mengatur dirinya sendiri — itu akan membatalkan tujuan tata kelolanya.

`staff` dikecualikan. `admin`-saja ditolak: bila ternyata tak seorang pun memegang `it:admin`, layarnya tak bisa dibuka siapa pun dan gejalanya senyap.

## Consequences

- **Tak ada form lama yang perlu dimigrasi.** Tanpa baris aturan, perilakunya persis seperti sebelum fitur ini ada.
- **Tipe form baru otomatis tersedia di semua departemen.** Yang menambahkannya wajib sadar itu, dan melarangnya di tempat yang perlu adalah langkah terpisah yang disengaja.
- **Ada dua tempat yang bisa mematikan Form Builder untuk sebuah departemen**: mengeluarkannya dari `FORM_BUILDER_DEPARTMENTS`, atau melarang seluruh tipenya. Keduanya sah dan hasilnya mirip, jadi layar pengaturan wajib menyebut konsekuensinya dengan kata-kata biasa agar keadaan itu tak pernah cuma ketahuan saat orangnya mengeluh.
- **Sumbu izin bertambah satu.** Bila [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] kelak diperluas ke permission-set untuk Form Builder, keputusan ini **wajib ditinjau ulang bersamaan**, bukan dibiarkan hidup berdampingan diam-diam.
- **Frontend tak memegang satu baris pun logika aturan.** `GET /me/capability` menjawab daftar POSITIF per departemen, jadi bila aturannya berubah, tak ada yang perlu diubah di FE.
- **Jangkauan form tetap tak digerbang.** `audience` dan `subject` masih hanya diperiksa bentuknya, bukan apakah orang yang disasar berada dalam cakupan pembuatnya. ADR ini **tidak** menyelesaikannya, dan tidak boleh dianggap sudah menyelesaikannya: departemen yang dibatasi tipenya tetap bisa menyasar karyawan departemen lain dengan tipe yang masih boleh dibuatnya.

## Alternatif yang ditolak

| Alternatif | Alasan ditolak |
|---|---|
| Daftar-izin (allowlist) | Tipe form baru mati diam-diam di semua departemen sampai tiap baris disunting |
| Matriks penuh, tiap departemen wajib punya baris | Departemen yang baru ditambahkan langsung lumpuh tanpa pesan yang menjelaskan sebabnya |
| Env seperti `FORM_BUILDER_DEPARTMENTS` | Tiap perubahan aturan menuntut recreate container; pemilik produk meminta bisa diubah tanpa deploy |
| Peta konstanta di kode | Tiap perubahan menuntut PR + deploy |
| Tiap SPV mengatur departemennya sendiri | Membatalkan tujuan tata kelola: yang dilarang tinggal mengizinkan dirinya sendiri |
| Menempelkannya di posisi sesuai ADR 0030 | Jawabannya identik untuk semua posisi dalam satu departemen; menyalinnya hanya menunggu salah satunya menyimpang |

## Dokumen Terkait

- [[Microservices - Form Builder Service]] · [[API - Form Builder Service]] · [[IT - Form Builder]]
- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]
- [[APP - Web ERP]] · [[HRIS - Kaizen (Ide Perbaikan)]]
