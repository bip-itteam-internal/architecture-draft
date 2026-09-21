## Deskripsi

*Sistem checklist inspeksi berkala untuk tiap fungsi/peralatan General Affairs. Item #11 pada [[GA - Big Pictures]].*

- **Status**: 🟡 Draft / Direncanakan **untuk inspeksi berjadwal per peralatan**. ⚠️ Dua bagian dari lingkup yang dulu dianggap tercakup dokumen ini **sudah berdiri sendiri**, lihat bab di bawah. Diukur 2026-09-21 ke `origin/main` `bip-erp` `6ef719e3`.

## Keadaan terukur: sebagian lingkupnya sudah ada, jangan dibangun ulang

Dokumen ini sering dikutip sebagai penghambat tunggal yang mengunci sembilan metrik KPI di lima posisi GA ([[GA - Dashboard per Posisi]]). **Kutipan itu kini terlalu luas.** Dua mekanisme sudah berdiri dan menjawab sebagian lingkupnya:

| Sudah ada | Bentuknya | Menjawab |
|---|---|---|
| `nilai_inspeksi_satgas` | inspeksi Satgas 5R dan K3 di form-builder, bernilai dari cek ulang terakhir | metrik 5R dan kebersihan, termasuk "Kerapihan dan kebersihan Pos" milik Security |
| `ceklis_kpi` | butir ceklis form-builder ditautkan ke satu metrik KPI lewat **UID butir** | metrik apa pun yang dinilai "sudah atau belum" oleh seorang penilai, tanpa modul baru |

Keputusannya di [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]]. Sumbernya `services/employee/kpi_sumber_inspeksi_satgas.go` dan `kpi_sumber_ceklis.go`.

⛔ **Yang benar-benar belum ada, dan itulah sisa lingkup dokumen ini: inspeksi berjadwal yang lebih rapat dari mingguan.** Recurrence form-builder hanya mengenal `monthly` dan `weekly` (`services/form-builder/models_period.go:13-14`). Ronda security tiap 3 jam, patroli harian, dan preventive maintenance berkala karena itu tidak bisa menumpang form-builder.

⚠️ **Jangan menyelesaikannya dengan menambah satuan sub-harian ke form-builder.** Model periodenya dipakai bersama Kaizen, Satgas, dan `ceklis_kpi`; mengubahnya berarti menggeser satu fakta yang dipegang banyak konsumen demi satu pemakai baru. Irisan pertama yang sudah dirancang mengambil jalan lain: [[GA - Ronda Security]].

## Catatan: apakah ini sama dengan task tracker?

*Pertanyaan awal: "Bukankah ini sama dengan [[APP - Dynamic Task Tracker]]?"* — **Tidak sama, walau polanya bisa dipakai ulang.** Checklist = **inspeksi berkala terstruktur per peralatan** (template item tetap + jadwal periodik + hasil pass/fail/temuan + nilai ukur), bukan tugas ad-hoc. Task tracker cocok untuk pekerjaan satuan; checklist butuh template per aset, penjadwalan rutin, dan riwayat hasil per item.

## Ruang Lingkup

Checklist per fungsi/peralatan GA (template & sumber spreadsheet tertaut di [[GA - Big Pictures]]):
- **Ladder**, **Excavator**, **Diesel Generator**, **Panel Board**, **Fire Extinguisher (APAR)**, dan seterusnya

## Fitur / Proses yang Direncanakan

- **Template checklist** per aset (daftar item + kriteria)
- **Penjadwalan periodik** (harian/mingguan/bulanan) per peralatan
- Pengisian hasil (pass/fail/temuan + foto) + riwayat
- **Eskalasi temuan** → [[GA - Machine & Utility Maintenance]] / [[GA - Building Maintenance]] / [[GA - Accident Prevention]]
- Sumber data untuk [[GA - Audit Internal System]]

## Dependensi / Dokumen Terkait

- [[GA - Big Pictures]]
- [[GA - Machine & Utility Maintenance]] · [[GA - Building Maintenance]] · [[GA - Audit Internal System]] · [[GA - Accident Prevention]] · [[GA - Risk Management]]
- [[APP - Dynamic Task Tracker]] (pola yang dapat dipakai ulang)
