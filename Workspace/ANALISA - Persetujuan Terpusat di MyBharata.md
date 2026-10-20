## Deskripsi

*Pecahan kerja untuk [[ADR - 0188 Persetujuan Terpusat di MyBharata, Detail Seragam dari Agregator, Tanpa Arahan ke Web]]. Bukan rencana per berkas; tiap blok di bawah adalah draf issue yang dibuat di GitHub, cukup jelas untuk dilempar ke `/brief` setelah ADR-nya Diterima. Cara kerja di MyBharata: [[APP - MyBharata]] § Persetujuan Terpusat (usulan).*

> ⛔ **Menunggu [[ADR - 0188 Persetujuan Terpusat di MyBharata, Detail Seragam dari Agregator, Tanpa Arahan ke Web]] Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **Status**: 🟡 Belum dikerjakan
- **Tanggal**: 2026-10-20
- **Pemutus**: irfanarfianto
- **Ukuran**: **Besar**. Tiga repo harus berubah dan masing-masing butuh lebih dari satu PR:
  - `bip-erp`: agregator belum punya `jenis`, `langkah[]`, maupun endpoint detail (`antrean_pengajuan.go:45-236`, `:1888`); lima service sumber belum memberi akses baca penyetuju atau rute detail (`procurement/main.go:873`, `inventory/permintaan_gate.go:46-54`, learning/marketing-analytics/recruitment tanpa GET by id).
  - `my-bharata`: belum memanggil agregator sama sekali (git grep `origin/dev` 2026-10-19), kartu beranda membaca `/hr/requests` (`pending_approval_card.dart:25`), layar peninjau hanya untuk 6 jenis karyawan + booking + tiket.
  - `erp-frontend`: kategori tampil sebagai lencana outline tanpa warna/ikon (`tabel-persetujuan.tsx:393-395`), Sheet hanya untuk 3 kategori (`page.tsx:277-295`), tiga stepper terpisah tanpa komponen bersama.
- **Rujukan visual**: Figma `BUV8afcBrNSbkmm0qI8EYz`, halaman "Persetujuan Terpusat" (salinan bertanggal, bukan sumber kebenaran).

## Urutan

```
#1 [BE] jenis + langkah ringkas ──┬─> #4 [Mobile] kartu + daftar ──┐
                                  ├─> #7 [FE] tabel compact ───────┤
#2 [BE] detail seragam (sesudah #1) ─┬─> #5 [Mobile] detail + aksi <┘ (juga butuh #3)
#3 [BE] akses baca + rute detail ────┤   #6 [Mobile] Rincian Payroll (sesudah #2)
                                     └─> #8 [FE] Sheet 16 jenis + stepper (sesudah #2, #3, #7)
```

Deploy: backend lebih dulu, lalu MyBharata, lalu web. Semua field baru tambahan; konsumen lama tetap jalan.

## Perlu ukur prod (sebelum #5 dan #8 diberi `Siap Agent`)

Per 2026-10-15, ADR 0181 mencatat 0 dokumen menunggu untuk Permintaan ERP, Pelatihan, Payroll, Permintaan Barang GA, dan Requisition. Ukur ulang (baca saja, mongosh di DB masing-masing service; alamat di [[IT - Server, VMs and Databases]] § MongoDB ERP Production):

```js
// jalankan per koleksi, tempel hasilnya di issue #5 dan #8
["pengajuan_barang","permintaan_erp","permintaan_barang_ga","training_request","payroll_run","karya_live_support","requisitions","offers"].forEach(c => {
  const r = db.getCollection(c).aggregate([{ $group: { _id: "$status", n: { $sum: 1 } } }]).toArray();
  print(c, JSON.stringify(r));
});
```

Jenis yang masih 0 dokumen menunggu dikerjakan paling akhir di #5 dan #8.

---

## Induk · bip-erp

**Judul**: Persetujuan Terpusat di MyBharata dan Portal Persetujuan seragam per jenis

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Penyetuju tidak punya satu tempat di HP untuk melihat dan menuntaskan semua yang menunggu dia: kartu Beranda MyBharata hanya menghitung pengajuan karyawan + booking, dan sembilan jenis lain hanya bisa diputus lewat web. Web sendiri menampilkan kategori tanpa pembeda visual dan hanya tiga kategori yang punya panel detail.

## Keputusan
[[ADR - 0188 Persetujuan Terpusat di MyBharata, Detail Seragam dari Agregator, Tanpa Arahan ke Web]] (layak `Siap Agent` sesudah ADR berstatus Diterima). Induk tanpa PR sendiri; ditutup manual saat semua sub-issue merged.

## Yang harus benar
- Semua sub-issue merged dan ter-deploy dengan urutan BE → Mobile → FE.

## Di luar cakupan
- Penanda SLA/"lewat N hari" (ADR 0181 butir 12). Model persetujuan tunggal (ADR 0137).

## Data / bukti pendukung
Lihat § Perlu ukur prod di ANALISA ini.

## Prasyarat
ADR 0188 Diterima.

---

## #1 · bip-erp · [BE] Antrean: field `jenis` + `langkah[]` ringkas di baris (bagian 1/3)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Jenis pengajuan karyawan hanya hidup di teks `perihal` (`antrean_pengajuan.go:837-840`), sehingga MyBharata dan web tak bisa memecah kategori `karyawan` per jenis tanpa mengurai teks. Baris antrean juga tak membawa langkah persetujuan; `langkah_ke/total` hanya terisi untuk Pengajuan Barang dan Permintaan Barang GA (`antrean_kontrak.go:156-160`).

## Keputusan
ADR 0188 butir 4 (layak `Siap Agent` sesudah ADR Diterima). Bentuk: `jenis` = kode stabil (`cuti`, `izin`, `sakit`, `dinas`, `koreksi`, `tukar`, `booking`; non-karyawan = kategori); `langkah[]` ringkas = langkah selesai terakhir + langkah menunggu, field per langkah sesuai ADR; diterjemahkan sekali di agregator.

## Yang harus benar
- Tiap baris `GET /pengajuan/antrean` (kedua sumbu) membawa `jenis` tak kosong; baris karyawan memakai kode jenis, bukan teks.
- `perihal` baris karyawan tidak lagi diawali nama jenis (`"Cuti Tahunan"`, bukan `"Cuti - Cuti Tahunan"`).
- Tiap baris membawa `langkah` berisi paling banyak dua langkah dengan `status` dari enam nilai ADR; langkah yang menunggu pemanggil ber-`anda: true`.
- `langkah_ke`/`langkah_total` diturunkan dari langkah yang sama (test membuktikan keduanya tidak bisa menyimpang).
- Field opsional langkah ter-serialisasi `null`, bukan hilang (test kontrak JSON).
- Sumber yang tak punya riwayat (tiket: hanya timestamp) tetap menghasilkan langkah `pengaju` + langkah menunggu, bukan daftar kosong.
- Konsumen lama (web hari ini) tetap jalan: test kontrak lama hijau.

## Di luar cakupan
Endpoint detail (#2); perubahan penyimpanan riwayat di service sumber.

## Data / bukti pendukung
Bentuk simpan per modul (dari grounding 2026-10-19): `ReviewStep` attendance (`attendance/hr_admin.go:98-104`), `ReviewSlot` learning (`learning/models_request.go:86-88`), `RiwayatBarang` (`procurement/pengajuan_barang.go:261-277`), `RiwayatRun` (`payroll/models_payroll_run.go:159-173`), `RiwayatPermintaan` (`inventory/permintaan_barang.go:139-147`), `RiwayatKarya` (`marketing-analytics/karya_live_support.go:94-99`), Permintaan ERP hanya `DisetujuiOleh/Pada` (`procurement/permintaan_erp.go:92-93`), tiket hanya timestamp (`task-management/models_task.go:65-66`).

## Prasyarat
ADR 0188 Diterima.

---

## #2 · bip-erp · [BE] Detail seragam `GET /pengajuan/antrean/:kategori/:id` + `langkah[]` lengkap (bagian 2/3, sesudah #1)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
MyBharata wajib menampilkan detail semua jenis tanpa membuka web, tetapi agregator tak punya endpoint detail (hanya `/pengajuan/antrean` dan `/pengajuan/ringkasan`); merakit detail per sumber di Dart dan TypeScript berarti logika langkah ditulis dua kali.

## Keputusan
ADR 0188 butir 3-4 (layak `Siap Agent` sesudah ADR Diterima). Bentuk: satu endpoint detail di employee-service yang memanggil rute detail sumber dengan identitas pemanggil, mengembalikan baris + `langkah[]` lengkap + rincian label-nilai per jenis.

## Yang harus benar
- `GET /pengajuan/antrean/:kategori/:id` membalas bentuk sama untuk 10 kategori: field baris, `langkah` lengkap (urut waktu, termasuk putaran dikembalikan), dan `rincian` berupa daftar `{label, nilai}` yang sudah berbahasa layar.
- 403 dari sumber diteruskan sebagai 403 (bukan 500, bukan 200 kosong); sumber tak terjangkau = 502 berpesan.
- Kategori atau id tak dikenal = 404.
- Gateway: rute bekerja lewat `/api/employee/pengajuan/antrean/...` (test mereproduksi pemotongan prefix).
- Rute literal didaftarkan sebelum saudara ber-`:param` di prefiks yang sama (test bentuk respons, bukan status).
- Test kontrak mengurai rekaman respons sungguhan tiap sumber, bukan struct tiruan.

## Di luar cakupan
Membuka akses baca baru di sumber (#3); aksi/tombol (tetap memanggil endpoint modul asal).

## Data / bukti pendukung
Rute detail sumber hari ini: attendance `GET /hr/requests/detail` (`hr_admin.go:39`), pengajuan barang `GET /pengajuan-barang/:id`, tiket `GET /tasks/:id`, payroll `GET /payroll-runs/:id`, requisition `GET /requisitions/:id`; Live Support, Pelatihan, Offer belum punya (#3).

## Prasyarat
#1 merged.

---

## #3 · bip-erp · [BE] Akses baca penyetuju + rute detail Live Support, Pelatihan, Offer, Permintaan Pembelian, Permintaan Barang GA (bagian 3/3)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Penyetuju yang tak memegang izin modul ditolak membaca dokumen yang sedang ia putuskan: `GET /permintaan-erp/:id` digerbang `procurement.view` (`procurement/main.go:873`), `GET /permintaan/:nomor` 403 sesudah status `DIAJUKAN` kecuali staf GA (`inventory/permintaan_gate.go:46-54`), daftar Offer digerbang `recruitment.view`. Live Support, Pelatihan, dan Offer tak punya rute detail per id sama sekali.

## Keputusan
ADR 0188 butir 5 (layak `Siap Agent` sesudah ADR Diterima). Bentuk: penyetuju/pelaksana boleh membaca dokumen yang ada di antrean atau riwayatnya, pola `BolehMelihatPengajuan` (`procurement/pengajuan_barang_cakupan_baca.go:76-100`); gerbang di service sumber; tanpa memberi izin modul.

## Yang harus benar
- Penyetuju tahap yang sedang aktif bisa `GET` detail Permintaan Pembelian, Permintaan Barang GA (semua status), dan Offer tanpa izin modul; orang lain tanpa izin tetap 403.
- Rute detail per id baru untuk Live Support (`karya`), Pelatihan (`training_request`), dan Offer, dengan aturan baca yang sama; pemohon tetap bisa membaca miliknya.
- Tiap gerbang punya test positif (penyetuju lolos) dan negatif (karyawan acak 403), lewat `app.Test(httptest...)`.
- Gerbang dicari di pendaftaran rute, middleware grup, dan filter `FindOne`, bukan hanya badan handler.

## Di luar cakupan
Mengubah siapa berwenang memutus; endpoint riwayat baru untuk sumber yang belum punya (ADR 0181:135).

## Data / bukti pendukung
Grounding 2026-10-19: `git grep -E 'Get\(./live-support/karya/:id'`, `'Get\(./requests/:id.,'` (learning), `'Get\(./offers/:id'` atas `origin/main` semuanya nihil.

## Prasyarat
ADR 0188 Diterima.

---

## #4 · my-bharata · [Mobile] Kartu "Perlu Tindakan" + halaman Persetujuan Menunggu/Riwayat 16 jenis (bagian 1/3)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Kartu Beranda "Perlu Review" menghitung hanya pengajuan karyawan + booking (`pending_approval_card.dart:25-26`) dan menyembunyikan kartu saat galat (`:26`, `:53-54`), sehingga gagal muat tak bisa dibedakan dari "tak ada yang menunggu". MyBharata belum punya daftar lintas modul.

## Keputusan
ADR 0188 butir 1-2 (layak `Siap Agent` sesudah ADR Diterima). Bentuk: judul "Perlu Tindakan", subjudul "{n} menunggu Anda", ikon inbox, angka = baris agregator non-`pantau`, tanpa penanda lewat-N-hari; kartu daftar berbentuk `ReviewerLeaveCard` asli.

## Yang harus benar
- Kartu Beranda: judul "Perlu Tindakan" / "Needs Action", subjudul "{n} menunggu Anda" / "{n} waiting for you" (key di `app_id.arb` dan `app_en.arb`), ikon `LucideIcons.inbox`; angka = jumlah baris `?as=reviewer` dengan `aksi != pantau`.
- Galat pemuatan menampilkan keadaan galat dengan coba lagi, bukan menyembunyikan kartu; kartu tersembunyi hanya saat angka 0 yang sah.
- Ketuk kartu membuka halaman Persetujuan (pil "Perlu tindakan" aktif).
- Halaman Persetujuan: tab Menunggu (urut terlama) dan Riwayat (urut terbaru), pencarian nomor/perihal/pemohon, pil per `aksi`, penyaring jenis; `degraded` tak kosong tampil sebagai pemberitahuan, bukan daftar kosong.
- Kartu = `ReviewerLeaveCard` asli + trailing lama menunggu + nominal bila `nilai` tak null + `ReviewStepper` dua langkah dari `langkah`, pil `aksi` pada langkah `anda`.
- Warna/ikon 16 jenis di `RequestTypeUIHelper` (delapan baru ditambahkan di tempat yang sama).
- Ketuk kartu jenis karyawan membuka halaman detail peninjau yang sudah ada; jenis lain menunggu #5 (sementara read-only dari baris).
- Pil "Submitted" di `submission_card_stepper.dart:133` lewat l10n.
- Widget test: kartu galat ≠ kosong; pemetaan `jenis` → warna/ikon untuk 16 jenis.

## Di luar cakupan
Detail dan aksi jenis non-karyawan (#5); Rincian Payroll (#6).

## Data / bukti pendukung
Rancangan: Figma "MyBharata: Persetujuan Terpusat versi compact" (kartu 16 jenis, M1, M2, kartu Beranda).

## Prasyarat
#1 merged **dan ter-deploy** (deploy sesudah `bip-erp` #1).

---

## #5 · my-bharata · [Mobile] Detail + aksi jenis non-karyawan, stepper ringkas/semua (bagian 2/3)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Pelatihan, Pengajuan Barang, Permintaan Pembelian, Permintaan Barang GA, Live Support, Payroll, Requisition, dan Offer tak punya layar peninjau di MyBharata; penyetujunya terpaksa membuka web.

## Keputusan
ADR 0188 butir 3 (layak `Siap Agent` sesudah ADR Diterima). Bentuk: detail berbentuk `ReviewerSubmissionDetailPage` asli dari `GET /pengajuan/antrean/:kategori/:id`; tanpa tombol ke web; `pantau`/`boleh_putus` false = pesan status tanpa tombol.

## Yang harus benar
- Tiap jenis non-karyawan membuka detail di aplikasi: kartu jenis + perihal utuh + nominal + stepper; "Detail Pengajuan" dari `rincian` server; bilah bawah aksi.
- Stepper detail ringkas dua langkah + "Lihat semua langkah (N)" bila langkah > 2; terbuka menampilkan seluruh `langkah`.
- Tombol aksi memanggil endpoint modul asal yang sama dengan web; tampil hanya bila `boleh_putus == true`.
- Tidak ada `launchUrl` ke domain ERP web (test/grep di PR).
- 403 detail tampil "Anda tidak lagi berhak melihat dokumen ini", bukan galat umum.
- Urutan per jenis mengikuti hasil § Perlu ukur prod: jenis berdata lebih dulu.

## Di luar cakupan
Rincian Payroll per karyawan (#6).

## Data / bukti pendukung
Perlu ukur prod: jumlah dokumen menunggu per koleksi (kueri di § Perlu ukur prod ANALISA ini).

## Prasyarat
#2, #3, dan #4 merged; deploy sesudah `bip-erp` #2 dan #3.

---

## #6 · my-bharata · [Mobile] Rincian Payroll: tabel compact + rincian gaji per karyawan (bagian 3/3)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Penyetuju payroll run harus bisa memeriksa gaji seluruh karyawan sebelum memutus, dan aturan ADR 0188 melarang mengarahkannya ke web.

## Keputusan
ADR 0188 butir 3 (layak `Siap Agent` sesudah ADR Diterima). Bentuk: halaman Rincian Payroll (tabel Karyawan · Pokok · Potongan · Bersih) + Rincian Gaji per karyawan berbentuk `PayslipDetailBody`; **tanpa PIN tambahan**, akses `payroll.view`.

## Yang harus benar
- Tombol "Lihat rincian {n} karyawan" di detail Payroll membuka Rincian Payroll di aplikasi.
- Tabel: kepala menempel, baris total menempel, angka penuh berpemisah ribuan tanpa "Rp" (satuan di kepala kolom), pencarian nama/NIK, penyaring departemen, muat bertahap.
- Ketuk baris membuka Rincian Gaji: Pendapatan, Potongan, Bruto, Total Potongan, Gaji Bersih; navigasi sebelumnya/berikutnya; tombol Unduh PDF tak tampil selama run belum terbit.
- Penyetuju tanpa `payroll.view` melihat pesan terkunci yang menyebut izinnya, bukan galat umum.
- Format rupiah memakai `formatRupiahSlip` yang ada (satu tempat).

## Di luar cakupan
PIN tambahan (ditolak ADR 0188); perubahan perhitungan payroll.

## Data / bukti pendukung
`GET /payroll-runs/:id` mengembalikan seluruh baris per karyawan (`payroll/run_handlers.go:366-387`); paket Tanda Tangan membawa `payroll.view` (`shared-library/common/catalog_payroll.go:190-214`).

## Prasyarat
#2 merged; deploy sesudah `bip-erp` #2.

---

## #7 · erp-frontend · [FE] Tabel & Riwayat compact, ubin warna/ikon jenis, label "Permintaan Pembelian" (bagian 1/2)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Tabel Persetujuan memakai lencana kategori outline tanpa warna/ikon (`tabel-persetujuan.tsx:393-395`), lima kolom dengan Nilai terpisah yang kebanyakan kosong, dan label "Permintaan ERP" (`id.ts:23790`, `en.ts:23265`) yang tak bermakna bagi pemakai.

## Keputusan
ADR 0188 butir 6-7 (layak `Siap Agent` sesudah ADR Diterima). Bentuk: kolom Menunggu · Tindakan (+x/y) · Dokumen (ubin jenis + perihal + jenis · nomor, nominal di kanan) · Pemohon; Riwayat Diproses · Tindakan Anda · Dokumen · Pemohon · Posisi sekarang; warna/ikon sama dengan MyBharata.

## Yang harus benar
- Kolom Nilai dihapus; nominal tampil di ujung kanan sel Dokumen hanya bila `nilai` tak null (ekspor tetap punya kolom Nilai).
- Ubin jenis 16 warna/ikon dari satu peta di `features/persetujuan/lib/`, memakai `jenis` dari baris; jenis tak dikenal jatuh ke abu netral.
- Kategori `karyawan` dipecah per `jenis` di penyaring.
- Label `permintaanErp` → "Permintaan Pembelian" / "Purchase Request" di `id.ts` dan `en.ts`.
- Tanpa penanda lewat-N-hari.
- `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` hijau; kegagalan `pnpm test` tidak bertambah dari baseline.

## Di luar cakupan
Sheet kategori baru dan stepper bersama (#8).

## Data / bukti pendukung
Rancangan: Figma "Tabel web compact" dan "Tabel web compact · Riwayat".

## Prasyarat
`bip-erp` #1 merged; deploy sesudah `bip-erp` #1.

---

## #8 · erp-frontend · [FE] Sheet 16 jenis + komponen stepper bersama (bagian 2/2, sesudah #7)

**Pemutus:** irfanarfianto
**PIC:** (diisi saat In Progress)

## Masalah
Hanya karyawan, Pengajuan Barang, dan Tiket yang membuka Sheet (`page.tsx:277-295`); jenis lain bernavigasi ke modul. Stepper dirakit tiga kali terpisah (`linimasa-pengajuan.tsx`, `stepper-tahap-payroll.tsx`, inline `request-detail.tsx:177-220`) dengan label hardcode.

## Keputusan
ADR 0188 butir 7 (layak `Siap Agent` sesudah ADR Diterima). Bentuk: Sheet tiga bagian untuk 16 jenis; header = nama pemohon, badan dimulai perihal utuh; satu komponen stepper yang merender `langkah[]` (ringkas dua langkah + "Lihat semua langkah").

## Yang harus benar
- Klik baris jenis mana pun membuka Sheet `?detail=<kategori>:<id>` berisi data `GET /pengajuan/antrean/:kategori/:id`.
- Kerangka Sheet sesuai `ui-checklist.md` §2a: header tetap, badan `flex-1 min-h-0 overflow-y-auto px-4`, `SheetFooter` untuk aksi.
- Header berisi nama pemohon + jenis · posisi · departemen + status; perihal tidak dipotong (tampil utuh di badan).
- Komponen stepper bersama dipakai Sheet; status enam nilai dari `langkah[].status`; label lewat i18n.
- Tombol ke halaman lengkap modul tetap ada di web.
- Uji kelas `min-h-0` dengan kontrol negatif; `pnpm tsc/lint/build` hijau.

## Di luar cakupan
Mengganti stepper di halaman modul di luar portal.

## Data / bukti pendukung
Perlu ukur prod: sama dengan #5; jenis berdata lebih dulu.

## Prasyarat
`bip-erp` #2 dan #3 serta #7 merged; deploy sesudah `bip-erp` #2 dan #3.
