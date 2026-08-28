# Prosedur Pencarian Vault (dipakai bersama)

> Dirujuk oleh `/ask`, `/start-task`, dan `/analisa-kebutuhan`. **Satu tempat**: sebelum berkas
> ini ada, prosedur yang sama tersalin di dua command dan sempat menyimpang. Jangan menyalinnya
> lagi ke command baru, rujuk saja.

## 1. Pilih dokumen dari dua arah

a. `architecture-draft/CLAUDE.md` §7 memetakan **repo kode → dokumen**. Dipakai bila titik
   berangkatnya kode, dan untuk `/start-task` selalu.
b. `architecture-draft/VAULT-INDEX.json` memetakan **pertanyaan → dokumen**. Cocokkan teks ke
   `ringkasan` dan `kata_kunci`, ambil **3 sampai 5** kandidat.

Sumbunya berbeda dan keduanya berguna; gabungkan hasilnya.

Bila indeks tidak ada, rusak, atau `versi_skema` tak dikenal, pakai (a) saja + grep vault/kode,
**beri tahu user** bahwa indeks tidak tersedia, dan sarankan `/index-vault`.

## 2. Baca dokumen terpilih SECARA UTUH

Jangan menyimpulkan dari ringkasan indeks.

## 3. Perhatikan status

Perhatikan `status_emoji` + `status_teks` di entri indeks dan marker di dokumennya:

| Marker | Arti |
|---|---|
| ✅ Implemented | ada di kode |
| ⚠️ Implemented (ada catatan) | ada di kode, tapi ada gap/bug/parsial |
| 🟡 Konsep | rencana, belum ada kodenya |
| 🔴 Stub | kerangka saja |
| 🔜 Direncanakan | belum dikerjakan |
| ⛔ Superseded | sudah digantikan, jangan dipakai |

Sekitar sepertiga dokumen **tidak punya status**: seluruh dok meta root dan seluruh `API - *`.
Itu normal, bukan gap.

## 4. Cocok topik bukan berarti menjawab

Indeks selalu mengembalikan dokumen terdekat, bahkan ketika jawabannya belum pernah ditulis.
Setelah membaca, tanya diri sendiri apakah pertanyaannya benar-benar terjawab atau dokumen itu
cuma sebidang topik. Bila cuma sebidang, katakan begitu dan sebut apa yang belum ada — jangan
menyajikan yang terdekat seolah itu jawabannya. Diuji 2026-07-20: "berapa lama masa percobaan
karyawan" dan "kenapa gaji telat cair" mengembalikan dokumen recruitment dan payroll yang
relevan topiknya tapi tidak memuat jawabannya.
