## Deskripsi

*Kompensasi & benefit karyawan: komponen gaji, BPJS, pajak (PPh21), tunjangan, serta bonus/lembur/insentif. Melengkapi [[HRIS - Payroll]] (proses penggajian) dengan rincian komponen & benefit, dan sejak 2026-10-01 memuat cara kerja **struktur gaji berversi** yang diputuskan [[ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari]].*

- **Status**: 🟡 Konsep / Draft. Struktur gaji berversi **diusulkan, kode belum ada**; master komponen dan penetapan gaji satu-dokumen yang berlaku hari ini ✅ di [[Microservices - Payroll Service]].

## Ruang Lingkup

- **Komponen gaji**: gaji pokok, tunjangan tetap/tidak tetap, potongan
- **BPJS**: Kesehatan & Ketenagakerjaan (data BPJS dikelola di [[HRIS - Personalia]] / [[Microservices - Employee Service]])
- **Pajak PPh21**: perhitungan & pelaporan (**belum** terdokumentasi)
- **Benefit** lain: THR, tunjangan kesehatan, dll
- **Variabel**: lembur ([[HRIS - Overtime]]), insentif ([[Sales - Incentive]] / [[Finance - Incentive]])

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Personalia | staf HRD, pengisi struktur gaji | `payroll.salary.write` lewat paket ([[ADR - 0129 Persetujuan Payroll Run Bertingkat dan Dibayar per Badan Usaha sebelum Terbit]]) | Web ERP |
| Manajer HRD (SPV HRD) | penyetuju angka gaji baru | paket SPV HRD | Web ERP |
| Cost Control, SPV Finance, Direktur | pembaca seluruh gaji | paket baca payroll (ADR 0129) | Web ERP |
| Karyawan | pembaca gajinya sendiri lewat slip dan Lampiran 1 kontrak | diri sendiri | MyBharata |

- **Tujuan**: setiap rupiah di slip bisa ditelusuri ke keputusan yang mendasarinya, tanpa angka diketik ulang.
- **Pain point** (diukur 2026-10-01): penetapan gaji ditimpa tanpa riwayat; 160 dari 183 ditimpa sekaligus dari sheet September; gaji pokok selalu penuh walau ada perubahan, masuk, atau resign di tengah periode.
- **Aksi utama**: menetapkan struktur gaji dari offer, kontrak, dan promosi/mutasi; menyetujui versi baru; membaca riwayat.

## Golongan komponen

Master komponen ada di `payroll_db.salary_component` (seed `services/payroll/models_component.go`). Dalam urusan perubahan struktur, komponen terbagi tiga, dan **hanya golongan pertama yang dibawa event personalia**:

| Golongan | Komponen | Ikut dasar BPJS | Terisi di prod (2026-10-01, dari 183) |
|---|---|---|---|
| **Struktur tetap** (`manual`, per orang) | Gaji Pokok | ya | 183 |
| | Tunjangan Jabatan | ya | 175 |
| | Tunjangan Makan | tidak | 175 |
| | Tunjangan Kehadiran (nilai dasar) | tidak | 176 (diukur ulang 2026-10-02) |
| | Tunjangan PPh 21 | tidak | 1 |
| | Tunjangan Masa Kerja | tidak | 0 |
| | Tunjangan Shift | tidak | 0 |
| **Variabel per run** (`manual`) | Bonus, Insentif, Kasbon, Lain-lain | tidak | diisi per run |
| **Dihitung engine** (`computed`) | Lembur, BPJS (Kesehatan, JHT, JP, JKK, JKM), PPh 21, Potongan Telat/Izin/Mangkir/Uang Makan | - |: |

⚠️ **Jangan menyalin komponen variabel ke struktur berikutnya.** Kasbon yang terbawa ke versi baru terpotong ulang tiap bulan tanpa galat. Potongan telat, izin, dan mangkir dihitung dari nilai dasar Tunjangan Kehadiran (`baseKehadiran / 26`). ⚠️ Koreksi 2026-10-02: catatan sebelumnya ("terisi untuk 1 orang") berasal dari kueri yang keliru; diukur ulang per `component_id`, Tunjangan Kehadiran terisi untuk 176 dari 183 karyawan dengan id komponen aktif di master.

Selain komponen, struktur tetap memuat **dasar upah BPJS Kesehatan dan Ketenagakerjaan**, **kepesertaan BPJS**, **status PTKP**, dan **badan usaha penggaji**.

## Struktur Gaji Berversi (🟡 Diusulkan)

Keputusan dan alasannya di [[ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari]]; bagian ini cara kerjanya.

### Versi

- Setiap perubahan menerbitkan **versi utuh** (seluruh struktur tetap + field BPJS/PTKP/badan usaha), bukan selisih.
- Versi menyimpan **tanggal mulai berlaku** saja; tanggal berakhir diturunkan dari versi berikutnya.

```
Versi #1  berlaku 2026-08-26 ─┐
Versi #2  berlaku 2026-10-26 ─┤ #1 berakhir 2026-10-25 (diturunkan)
Versi #3  berlaku 2027-03-10 ─┘ #2 berakhir 2027-03-09 (diturunkan)
```

- Status: `menunggu persetujuan` → `terjadwal` → `berlaku` → `lewat`, atau `batal`. Cron harian memindahkan `terjadwal` ke `berlaku` (pola sama dengan mutasi dan resign).
- Versi yang sudah dipakai payroll run di atas draft **tak bisa diubah**; koreksi = versi baru.
- `employee_salary` tetap ada sebagai proyeksi "versi berlaku hari ini" untuk konsumen lama (PKWT, THR, impor, koreksi run), ditulis hanya oleh payroll.

### Satu bentuk isian untuk semua event

Isian versi sama di semua layar (memakai ulang `EmployeeSalaryForm` mode embedded). Yang berbeda per event: asal nilai awal, kolom yang wajib disentuh, dan rujukan hulu.

| Event | Hulu (disimpan sebagai jenis + id) | Tanggal mulai berlaku | Wajib disentuh | Nilai awal |
|---|---|---|---|---|
| Offer, set evaluasi | offer | `join_date` sebenarnya | seluruh struktur | kosong |
| Offer, set kontrak | offer | sehari sesudah tanggal akhir evaluasi | seluruh struktur | kosong |
| Perpanjangan kontrak | kontrak | `start_date` kontrak baru | konfirmasi | versi berlaku |
| PKWT ke PKWTT | kontrak | `start_date` kontrak | konfirmasi | versi berlaku |
| Promosi / demosi | movement | `effective_date` | Tunjangan Jabatan | versi berlaku |
| Mutasi lateral | movement | `effective_date` | - | versi berlaku |
| Mutasi antar-perusahaan | movement | `effective_date` | badan usaha penggaji | versi berlaku |
| Kenaikan berkala / UMK | keputusan massal | tanggal keputusan | Gaji Pokok | versi berlaku |
| Impor sheet HRD | berkas impor | dinyatakan pengimpor | - | dari berkas |
| Koreksi, komponen sementara (Plt) | - | diketik HR | - | versi berlaku |

- Kolom "wajib" = tanda di layar, bukan kunci. Komponen mana yang boleh berubah per event adalah kebijakan HRD.
- Hulu yang tanggalnya berubah **menggeser** versinya; hulu batal **membatalkan** versinya.
- Komponen sementara (Plt) tidak punya tanggal berakhir: HR menjadwalkan versi pengembaliannya sekaligus.

### Offer

- Offer menyimpan **dua set** struktur (evaluasi dan kontrak) dan **tanggal akhir evaluasi** (menggantikan `masa_evaluasi` teks bebas).
- HR melihat rincian; **calon karyawan melihat total** yang dihitung dari komponen dan tidak disimpan. Rincian sampai ke karyawan di Lampiran 1 kontrak ([[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]]).
- Saat kandidat ditautkan ke karyawan, kedua set dikirim ke payroll sebagai versi berlaku + versi terjadwal. Offer yang sudah Accepted dibekukan.

### Prorata per hari

Dalam satu periode, tiap komponen struktur tetap = Σ (nilai versi × hari berlakunya / hari periode). Batas versi: perpindahan versi, `join_date` (karyawan masuk), dan tanggal efektif resign.

Contoh, periode 26 Agustus s.d. 25 September (31 hari), Gaji Pokok Rp 5.000.000:

| Kasus | Sebelum ADR 0148 | Sesudah |
|---|---|---|
| Promosi 10 Sep, GP jadi Rp 6.000.000 | angka yang kebetulan tersimpan saat run dihitung | 15/31 × 5 jt + 16/31 × 6 jt ≈ Rp 5,52 jt |
| Masuk 10 Sep | Rp 5 jt penuh | 16/31 × 5 jt ≈ Rp 2,58 jt |
| Resign efektif 10 Sep | Rp 5 jt penuh ([[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]]) | 15/31 × 5 jt ≈ Rp 2,42 jt |

- **Pembagi = hari kalender periode**: asumsi, **menunggu konfirmasi HRD**.
- Tarif potongan kehadiran per hari memakai nilai dasar Tunjangan Kehadiran dari versi yang berlaku pada hari itu.
- Slip menampilkan **satu baris per komponen** dengan keterangan hari, bukan baris per versi.

### Gerbang saat menyimpan

- GP atau TJ berubah → dasar upah BPJS wajib dikonfirmasi (diubah atau sengaja dibiarkan).
- Kenaikan untuk karyawan ber-SP II aktif → peringatan (Pasal 55 jo. 53, [[HRIS - Disciplinary (Surat Peringatan)]]).
- Versi baru disetujui Manajer HRD; pengisi ≠ penyetuju.

## Keterkaitan

- Diproses oleh [[HRIS - Payroll]] (yang menarik jam kerja/telat/lembur/cuti dari attendance `payroll-supplement`)
- Komponen dasar (kontrak/BPJS) dari [[HRIS - Personalia]]
- Event pemicu perubahan struktur: offer ([[HRIS - Recruitment]]), kontrak ([[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]]), promosi & mutasi ([[HRIS - Career & Promotion]])

## Belum Diputuskan (TBD)

- **Pembagi prorata**: hari kalender (asumsi ADR 0148) vs 30 tetap vs hari kerja: menunggu HRD
- **Komponen yang berubah per event** (mis. apakah TH/TM masa evaluasi berbeda dari masa kontrak): kebijakan HRD
- Rentang gaji per jenjang (kaitan [[HRIS - Career & Promotion]]): sengaja di luar ADR 0148
- Metode perhitungan **PPh21** (TER/PTKP) & pelaporan pajak
- Daftar tunjangan/benefit resmi + aturannya

## Dependensi / Dokumen Terkait

- [[ADR - 0148 Struktur Gaji Berversi per Event Personalia dan Diprorata per Hari]]
- [[HRIS - Payroll]] · [[HRIS - Personalia]] · [[HRIS - Overtime]] · [[Microservices - Payroll Service]]
- [[Sales - Incentive]] · [[Finance - Incentive]]
- [[Microservices - Employee Service]] · [[Microservices - Recruitment Service]]
