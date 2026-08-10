---
name: audit-keamanan
description: Gunakan saat diminta audit keamanan, threat model, review OWASP, atau "cek celah keamanan" pada repo bip-erp / erp-frontend / mybharata. Memuat gerbang keyakinan anti-noise, pengecualian yang wajib dipatuhi (creds vault IT disengaja), fase audit yang relevan untuk Go/Fiber/MongoDB, OWASP Top 10, dan STRIDE.
---

# Audit keamanan — bip-erp

> Diadaptasi dari skill `/cso` [gstack](https://github.com/garrytan/gstack) (MIT). Fase
> yang tak relevan (skill supply chain, notebook, PCI) dibuang; gerbang keyakinan,
> verifikasi aktif, dan pengecualian keras dipertahankan karena itu yang membedakan audit
> yang dipakai orang dari audit yang diabaikan.

**Aturan pertama: audit yang berisik akan diabaikan.** Lebih baik tiga temuan yang
benar-benar bisa dieksploitasi daripada tiga puluh dugaan. Semua yang di bawah ini
tunduk pada itu.

## Mode

- **Harian (default)** — gerbang keyakinan **8/10**. Hanya laporkan yang kamu yakin.
- **Menyeluruh** — gerbang **2/10**, saring noise sungguhan saja (fixture test, dok,
  placeholder). Temuan di bawah 8 ditandai `TENTATIF`.
- **Diff saja** — batasi ke berkas yang berubah di branch ini. Cocok dijalankan sebelum PR.

Tanyakan mode ke user bila tidak disebut. Default harian.

## Skala keyakinan

- **9-10** — jalur eksploitasi jelas, bisa ditulis PoC-nya.
- **8** — pola kerentanan jelas dengan cara eksploitasi yang dikenal. Batas minimum mode
  harian.
- **Di bawah 8** — jangan dilaporkan di mode harian.

---

## PENGECUALIAN KERAS — buang otomatis, jangan dilaporkan

Langgar ini dan auditnya jadi lebih buruk daripada tidak ada.

1. **Plaintext credentials di dok IT vault** (`IT - Server, VMs and Databases`,
   `IT - Monitoring System`) **DISENGAJA** sebagai referensi akses internal tim IT.
   Jangan diflag, jangan usulkan rotasi, jangan usulkan scrub. Ini keputusan tim, bukan
   kelalaian.
2. **DoS, resource exhaustion, rate limiting.** Kecuali biaya: panggilan LLM tanpa batas
   di `scraping`/Veo adalah risiko finansial, itu tetap dilaporkan.
3. **Secret di disk yang sudah terlindungi** (terenkripsi atau ber-permission benar).
4. **React/Next.js aman XSS secara bawaan.** Hanya flag escape hatch
   (`dangerouslySetInnerHTML`).
5. **Kode klien tidak perlu auth.** Itu tugas server.
6. **Log data non-PII bukan kerentanan.**
7. **Temuan di berkas fixture, seed test, atau dok** kecuali fixture itu benar-benar
   dipakai di jalur produksi.
8. Kerentanan web yang halus hanya bila keyakinannya sangat tinggi **dan** ada jalur
   eksploit konkret.

---

## Fase audit

Jalankan berurutan. Lewati fase yang tak menyentuh lingkup, dan **katakan** fase mana yang
dilewati.

### Fase 0 — Petakan permukaan

Sebelum mencari apa pun: service apa saja yang ada, mana yang terekspos lewat gateway,
mana yang punya rute `/internal/`, koleksi Mongo apa yang dipegang, dan siapa saja
pemanggilnya (web, MyBharata, career portal, webhook marketplace).

### Fase 1 — Batas kepercayaan gateway

Ini permukaan paling sering disalahpahami di sini.

- **`/internal/` BUKAN privat.** Gateway tetap meneruskannya dari internet. Tiap rute
  internal wajib memeriksa identitas pemanggil **sendiri**. Rute internal tanpa gerbang
  sendiri adalah temuan, dan keyakinannya tinggi.
- Rute mana yang lolos tanpa JWT? Apakah itu disengaja (login, career portal publik) atau
  kelalaian?
- Apakah ada endpoint yang mengembalikan data milik orang lain hanya dengan menukar id di
  path (IDOR)? Uji dengan menelusuri kode, bukan dengan memanggil API.

### Fase 2 — Otorisasi dan visibilitas

- **`system_roles` = hak akses modul/menu, BUKAN hierarki org.** Kode yang menyimpulkan
  atasan dari `system_roles` salah; atasan ada di `work_data` (`is_supervisor:true` +
  `department`).
- **Fallback yang meloloskan semua orang.** Bila resolver hak akses gagal atau kembali
  kosong lalu jatuh ke "izinkan", itu temuan kritis, bukan ketahanan.
- **"Boleh diakses" bukan "layak ditampilkan".** RBAC yang mengizinkan bukan alasan
  memunculkan data pribadi orang lain di layar bersama seperti kalender. Cek tiap feed
  agregat terhadap prinsip tiga lapis: data diri sendiri, pekerjaan sendiri, agenda
  perusahaan.
- Aksi admin: ada jejak audit? Perubahan hak akses tercatat?

### Fase 3 — Rahasia dan konfigurasi

- Secret hardcoded di kode, compose, atau workflow CI. **Cek juga riwayat git**, bukan
  cuma HEAD: secret yang sudah dihapus tetap ada di commit lama.
- Secret di `.env` yang ikut ter-commit.
- Kredensial dev dipakai ulang di prod.
- Kunci layanan internal yang kosong sehingga pemeriksaannya lolos begitu saja.
- **Ingat pengecualian keras nomor 1** sebelum melaporkan apa pun soal kredensial di vault.

### Fase 4 — Injeksi dan penanganan input

- Query Mongo yang dibangun dari input user tanpa validasi bentuk (operator injection:
  user mengirim `{"$ne": null}` di tempat yang mengharap string).
- Perintah shell yang dirangkai dari input.
- Deserialisasi input tanpa validasi tipe.
- **SSRF**: URL dari input user atau dari keluaran LLM di-fetch tanpa allowlist. Layanan
  internal terjangkau dari URL yang dikendalikan user?
- Upload: batas ukuran ditegakkan, tipe divalidasi, path tidak dirangkai dari nama berkas.

### Fase 5 — Keluaran LLM dan pihak ketiga

Berlaku untuk `scraping`, Veo/Ideamills, dan webhook marketplace.

- Nilai dari LLM ditulis ke DB atau diteruskan ke mailer tanpa validasi bentuk.
- Keluaran LLM disimpan lalu ditampilkan ke user lain tanpa sanitasi (prompt injection
  tersimpan).
- **Webhook tanpa verifikasi tanda tangan.** Telusuri seluruh rantai middleware sebelum
  menyimpulkan tidak ada.
- Panggilan LLM tanpa batas biaya.

### Fase 6 — Sesi dan token

- Masa berlaku JWT, rotasi refresh token, dan apakah token bisa dibatalkan.
- Apakah token menyimpan klaim yang dipercaya tanpa diverifikasi ulang di service tujuan.
- Karyawan non-aktif: apakah tokennya masih berlaku? Perubahan `is_active` mencabut akses
  atau cuma menyembunyikan dari daftar?

### Fase 7 — OWASP Top 10

Untuk tiap kategori, cari terarah dengan Grep, jangan membaca seluruh repo:

| Kategori | Yang dicari di sini |
|---|---|
| A01 Broken Access Control | Rute tanpa middleware auth, IDOR, eskalasi horizontal/vertikal, `/internal/` telanjang |
| A02 Cryptographic Failures | MD5/SHA1, secret hardcoded, data sensitif tanpa enkripsi |
| A03 Injection | Operator injection Mongo, command injection, escape hatch XSS |
| A04 Insecure Design | Tanpa rate limit di login, tanpa lockout, validasi bisnis cuma di frontend |
| A05 Security Misconfiguration | CORS wildcard di prod, debug mode, pesan galat verbose |
| A06 Komponen Usang | Dependensi dengan CVE diketahui; cek `go.mod` dan `package.json` |
| A07 Auth Failures | Kebijakan password, MFA untuk admin, manajemen sesi |
| A08 Integrity Failures | Deserialisasi tanpa validasi, data eksternal tanpa pemeriksaan keutuhan |
| A09 Logging Failures | Kegagalan otorisasi tidak tercatat, aksi admin tanpa jejak |
| A10 SSRF | Lihat Fase 4 |

### Fase 8 — STRIDE per komponen

Untuk tiap service utama:

```
KOMPONEN: <nama>
  Spoofing        : bisakah penyerang menyamar jadi user/service lain?
  Tampering       : bisakah data diubah saat transit atau saat tersimpan?
  Repudiation     : bisakah aksi disangkal? Ada jejak audit?
  Info Disclosure : data sensitif apa yang bisa bocor, ke siapa?
  DoS             : (lihat pengecualian keras 2, laporkan hanya bila soal biaya)
  Elevation       : bisakah user biasa naik jadi admin/supervisor?
```

### Fase 9 — Klasifikasi data

```
TERBATAS (bocor = tanggung jawab hukum)
  - Kredensial, data pribadi karyawan (NIK, gaji, kontrak), data pelamar

RAHASIA (bocor = kerugian bisnis)
  - Kunci API marketplace, data penjualan, struktur biaya

INTERNAL
  - Struktur organisasi, jadwal
```

Untuk tiap kelas: di mana disimpan, siapa yang bisa membacanya, berapa lama disimpan.

---

## Verifikasi aktif

Tiap temuan yang lolos gerbang keyakinan harus **dibuktikan dengan menelusuri kode**,
bukan dengan menyerang sistem hidup.

- **Rahasia** — periksa apakah polanya memang format kunci sungguhan (panjang, prefiks).
  **Jangan** mengujinya ke API hidup.
- **Webhook** — telusuri handler dan seluruh rantai middleware untuk memastikan verifikasi
  tanda tangan benar-benar tidak ada. **Jangan** mengirim permintaan.
- **SSRF** — telusuri jalur konstruksi URL sampai titik fetch-nya. **Jangan** mengirim
  permintaan.
- **Otorisasi** — baca middleware dan handler-nya, jangan menyimpulkan dari nama rute.

Tandai tiap temuan: `TERVERIFIKASI` (dikonfirmasi lewat penelusuran kode),
`BELUM TERVERIFIKASI` (cuma cocok pola), atau `TENTATIF` (mode menyeluruh, di bawah 8).

**Dilarang menyerang sistem hidup.** Tidak ada percobaan login, tidak ada pengiriman
payload ke dev apalagi prod. Audit ini membaca kode.

**Analisis varian.** Untuk tiap temuan yang terbukti, cari pola yang sama di tempat lain.
Satu rute internal tanpa gerbang biasanya berarti ada beberapa.

---

## Keluaran

```
AUDIT KEAMANAN — <repo> — <mode>
════════════════════════════════
Lingkup   : <fase yang dijalankan; sebutkan yang dilewati>
Dipindai  : <N berkas / N rute / N service>

[KRITIS]  #1  <judul>                       keyakinan 9/10  TERVERIFIKASI
  Lokasi  : file:line
  Masalah : <satu kalimat>
  Eksploit: <skenario konkret, siapa melakukan apa dan dapat apa>
  Fix     : <saran konkret>

[TINGGI]  #2  ...

─────────────────────────────────
RINGKAS: N kritis, N tinggi, N sedang
Kandidat dipindai N, dibuang pengecualian keras N, tak lolos gerbang keyakinan N
```

Baris terakhir wajib ada. Menunjukkan berapa yang dibuang membuat audit ini bisa dipercaya,
dan membuat orang tahu mode menyeluruh akan memunculkan apa.

Bila tidak ada temuan yang lolos: katakan begitu dengan jelas, sebutkan berapa kandidat
yang dibuang dan kenapa. **Jangan mengarang temuan supaya laporannya terlihat berisi.**

## Jangan

- Jangan memperbaiki sendiri temuan keamanan tanpa persetujuan. Laporkan dulu.
- Jangan menaruh detail eksploit yang bisa langsung dipakai ke dalam issue atau PR publik.
- Jangan menyimpulkan apa pun dari status CI erp-frontend (gerbangnya mati sejak
  2026-07-29).
- Jangan melaporkan hal yang sudah masuk pengecualian keras, sekalipun terlihat meyakinkan.
