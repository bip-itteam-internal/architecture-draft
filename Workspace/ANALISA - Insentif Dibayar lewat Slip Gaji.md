# ANALISA - Insentif Dibayar lewat Slip Gaji

Papan kerja untuk [[ADR - 0125 Insentif Profit Dibayar lewat Slip Gaji dari Snapshot yang Disetujui Finance]]. Dibuat 2026-09-25 lewat `/analisa-kebutuhan`. Bukan dok terbit; keputusan dan alasannya di ADR, cara kerjanya di [[Finance - Proses Insentif]].

**Kebutuhan:** setiap rupiah insentif yang dibayar berasal dari angka yang dikunci dan disetujui Finance, dibayar tepat satu kali, tidak diketik ulang, dan bisa ditelusuri dari slip ke hitungannya.

## Konfirmasi yang ditunggu (bukan kode)

- [ ] **K1 Finance + HR**: perlakuan PPh 21 (ikut TER bruto bulan diterima) dan dasar BPJS (tidak masuk) untuk komponen Insentif. ADR 0125 §7.
- [ ] **K2 Finance**: apakah Supervisor memberi persetujuan pertama sebelum Finance, atau Finance satu tahap saja. ADR 0125 §3. T1 dirancang bekerja dengan satu tahap.
- [ ] **K3 HR**: tanggal tutup payroll dan kapan sheet gaji dikunci. ADR 0125 §8.
- [ ] **K4 Finance**: Bonus Kyura Supervisor Rp9.379.908 di run Juli (BIP-0056-02-24) insentif atau bonus lain; dan bagaimana insentif penerima lain dibayar selama ini (prod: 1 dari 78 pemegang peran punya Bonus di slip Juli).
- [ ] **K5 Pemilik produk**: rencana engine payroll ERP menggantikan sheet HRD (menentukan kapan T7 dikerjakan).

## Task (berurutan)

- [~] **T1 BE insentive: snapshot periode + persetujuan Finance.** 🟡 Kode + test di branch `feat/insentif-snapshot` (2026-09-25; commit d4ed1e19, 5bb5a82d, de06120c); belum PR/merged; verifikasi lewat gateway dev menunggu deploy. Rencana: `.task-plans/2026-09-25-insentif-snapshot-persetujuan.md`. Aksi bekukan periode final menjadi snapshot per (karyawan, periode, level) berisi baris dashboard apa adanya; batalkan-dan-bekukan-ulang beralasan sebelum terbayar; setujui oleh Finance lewat izin di paket RBAC Finance (bukan peran `insentive`); tolak penyetuju yang penerima snapshot itu; tulis `disetujui` pada target periode yang disetujui. Snapshot terbayar tak bisa dibatalkan. Dependensi: tidak ada. Uji: persetujuan diri sendiri ditolak (termasuk staf Finance), periode belum final ditolak, target terkunci sesudah disetujui.
- [ ] **T2 FE Dashboard Insentif: bekukan, setujui, status.** Tombol bekukan dan setujui untuk Finance, status per baris (belum dibekukan, dibekukan, disetujui, terbayar), ekspor snapshot yang disetujui dalam kolom yang dipakai sheet HRD (dengan rujukan snapshot). Dependensi: T1.
- [ ] **T3 BE payroll: komponen Insentif + penjaga.** Komponen pendapatan `Insentif` (seed); tolak `Insentif` di `component_values` master; test bahwa `/employer-cost` tidak memuat insentif. Dependensi: tidak ada (bisa paralel dengan T1).
- [ ] **T4 BE payroll: impor diperiksa terhadap snapshot + tanda terbayar.** Baris `Insentif` di impor run diterima hanya bila sama dengan snapshot disetujui dan belum terbayar; baris run menyimpan rujukan snapshot; publish run menandai snapshot terbayar di run itu (idempoten, sekali). Gagal-tertutup bila insentive-service tak terjangkau. Dependensi: T1, T3. Deploy: insentive naik sebelum payroll; `INSENTIVE_MODULE_URL` baru di blok payroll compose butuh `--force-recreate`.
- [ ] **T5 FE payroll: kolom Insentif + pemetaan impor.** Kolom `Insentif` di tabel run (hari ini daftar nama kolom tetap, baris baru hanya terlihat di total) dan alias pemetaan di modal impor. Dependensi: T3.
- [ ] **T6 Pencocokan Finance.** Per periode: disetujui, terbayar, belum terbayar, dan tanda bahaya Bonus di slip penerima insentif pada periode yang sama. Dependensi: T4.
- [ ] **T7 (TBD, menunggu K5) Tarikan langsung di run bulanan.** Run bulanan engine menarik snapshot disetujui sebagai baris `Insentif` dengan aturan T4.
- [ ] **T8 Mobile: label kartu Insentif** sesuai ADR 0081 §4 yang diamandemen, bila M2 ADR 0081 dikerjakan sesudah T4. Dependensi: T4, ADR 0081 M2.

## Terpisah, jangan disisipkan ke task di atas

- **Pencabutan peran `system_roles.insentive`**: butuh ADR sendiri. Pembaca yang ditemukan grounding 2026-09-25 (lebih banyak dari perkiraan awal): `bolehSetujuiInsentif`; `marketingLeaderChecks`/`RequireMarketingLeader`/`RequireLiveShiftUser`/`RequireDepartmentShopsView`/`marketingStaffChecks`/`RequireQualityOrMarketing` di `shared-library/common/roles.go` (integration mapping, marketing-analytics ambang/pagu/live shift, komplain gudang dan QC, review scope); `task-management/engagement_handlers.go` (tutup/buka tiket engagement); FE `proxy.ts`, sidebar, `insentif-menu.ts`, `menu-permission.ts`, marketing-analytics `izin.ts`/`kepemilikan.ts`, komplain QC/gudang, lookup karyawan `role_system: "insentive"`; MyBharata `dev` `isHostLive` (menu Live Shift). Alasan di `peran_dari_jabatan.go:34-38` ("tak menyentuh perhitungan uang") sudah tidak benar. ADR 0030 dan ADR 0043 bertentangan soal nasib modul `insentive`. Arah pengganti yang disepakati: akses modul → RBAC `beauty_hacks`/`kyura` (jabatan marketing diberi `:staff` dulu, aditif), tingkat skema/Account Specialist/Leader → jabatan, SPV divisi → hierarki `work_data`, persetujuan → RBAC Finance, Insentif Saya → tanpa peran.
- **Rute legacy insentive tanpa gerbang peran**: `/calculate`, `/master-kpi`, `/mappings`, `/configs/ppn`, `DELETE /results/:id`, daftar `/results*`, `/audit-logs` hanya dijaga `ValidateGateway`, dan gateway tidak punya RBAC per modul (`api-gateway/main.go:1024-1049`). Terbuka bagi pemegang JWT mana pun. Brief perbaikan tersendiri.
- **FE vs BE tak sinkron di Dashboard**: FE meloloskan IT staff dan peran finance apa pun, BE hanya IT supervisor/admin dan finance staff/supervisor/admin.
- **IT bisa menulis target level supervisor** lewat akses admin; putuskan apakah hanya Finance/Direktur.
