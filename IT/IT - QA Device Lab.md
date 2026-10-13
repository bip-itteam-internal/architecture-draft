## Deskripsi

*Alat QA internal untuk menguji aplikasi Android secara massal di banyak HP yang tercolok USB ke satu PC: mirroring, kontrol serentak, aksi massal, dan agen AI yang menjalankan uji dari satu perintah. Dibangun sebagai pengganti aman untuk software "group control" Panda.*

- **Status**: 🟡 Direncanakan — spec desain selesai 2026-10-13, belum ada kode.
- **Stack (rencana)**: Node 24 + TypeScript, Fastify, React + Vite, vitest, pnpm. Alat eksternal: `adb`, `scrcpy`, `maestro`.
- **Path di repo**: repo `qa-device-lab` (sibling di workspace `erp/`), spec di `docs/superpowers/specs/2026-10-13-qa-device-lab-design.md`. Repo GitHub di org **belum dibuat** (TBD).

## Latar Belakang

Tim memakai Panda 9.13.219 (`panda_android_setup_9.13.219.exe`, penerbit "xiaowei technoligy Ltd.") untuk mengontrol banyak HP Android dari PC. Analisis statis 2026-10-13 (installer diekstrak, APK di-decompile, string aplikasi PC dibaca; aplikasi tidak dijalankan) menyimpulkan:

- **Bukan malware yang dikenal.** VirusTotal 1/65, satu-satunya deteksi berupa tebakan machine learning berskor rendah.
- **Tetapi berisiko untuk perangkat kantor**:
  - aplikasi PC terhubung terus-menerus ke server pembuat dan punya modul akses jarak jauh (P2P);
  - aplikasi pendamping di HP bisa diperintah aplikasi lain di HP yang sama, termasuk menjalankan skrip otomasi dan membaca clipboard;
  - UI aplikasi PC diberi izin menjalankan perintah shell;
  - lisensi diikat ke sidik jari hardware;
  - installer tanpa tanda tangan digital;
  - paket membawa Magisk (root) dan pemasang driver USB.

Rekomendasi: Panda **tidak dipasang di PC kantor atau HP kerja**. Rincian teknis temuan ada di laporan privat (lihat Sumber Daya); sengaja tidak ditulis di vault karena repo vault publik.

Inti Panda ternyata alat open-source (scrcpy untuk mirroring). Karena itu penggantinya dibangun ulang dari komponen open-source, **tanpa menyalin kode Panda**.

## Ruang Lingkup

**Mode manual** (setara Panda, tanpa AI):
- grid layar semua HP (screenshot berkala) dan mirror mulus per HP lewat scrcpy;
- kontrol serentak: satu HP pemimpin, gerakan ditiru HP pengikut (koordinat dalam persen layar);
- kirim teks sama atau berbeda per HP, pintasan teks, kirim dan tarik berkas;
- aksi massal: install APK, buka/tutup aplikasi, hapus data aplikasi (dengan konfirmasi), screenshot, Home, buka halaman Settings;
- label dan grup HP, rekam video sesi, rekam logcat + deteksi crash/ANR, layar mati saat dikontrol, clipboard dua arah;
- editor skenario YAML (format Maestro) dan menjalankannya paralel di banyak HP, hasil per HP di `runs/`.

**Mode agen** (pola sama dengan [[Microservices - Assistant Service]]):
- satu perintah bahasa alami, lalu agen mengusulkan aplikasi target dan pengecekan hasil, disetujui QA, lalu dikunci;
- loop: baca struktur layar, susun skenario, coba di satu HP, perbaiki (maks. 3 putaran), sebar ke semua HP dengan data bervariasi, lapor;
- agen **tidak boleh melemahkan pengecekan terkunci**; pengecekan yang gagal setelah navigasi benar dilaporkan sebagai kemungkinan bug aplikasi;
- AI lewat router internal yang sama dengan Copilot (`AI_BASE_URL`, `AI_API_KEY`, `AI_MODEL`).

**Sengaja tidak dibuat** (tidak dibutuhkan QA, hanya berguna untuk menyamarkan otomasi sebagai banyak manusia):
- pemalsuan identitas perangkat, rotasi IP/proxy per HP, *Random Delay* / *random offset* pada kontrol serentak;
- impor massal akun dan password, integrasi aplikasi chat multi-akun;
- konsol ADB atau shell bebas, akses lewat internet, HP cloud, root.

**Pengaman utama**: server hanya `127.0.0.1`; semua program eksternal lewat satu pintu (daftar-izin, argumen array, tanpa shell); serial HP divalidasi; berkas hanya dari folder proyek; tidak ada aplikasi pendamping di HP.

Target uji: aplikasi milik perusahaan (mis. [[APP - MyBharata]]) atau aplikasi pihak ketiga atas izin pemiliknya.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| QA tester | TBD (belum ada posisi QA aplikasi di struktur organisasi) | Lokal di PC QA, tanpa login | PC Windows + rak HP Android via USB |

- **Tujuan**: menjalankan uji yang sama di banyak HP sekaligus dan mendapat hasil per HP.
- **Pain point**: Panda berisiko untuk perangkat kantor; uji manual per HP lambat.
- **Aksi utama**: kontrol serentak, jalankan skenario, beri perintah ke agen, baca hasil.

## Belum Diputuskan (TBD)

- Jumlah HP per PC. Asumsi spec: maks. 20, diukur saat spike laju screenshot.
- Spike yang menentukan desain:
  - Maestro paralel ke HP berbeda dengan data berbeda;
  - pembacaan hierarki layar lewat `maestro hierarchy`;
  - teks non-ASCII lewat Maestro;
  - laju screenshot grid.
- Pembuatan repo GitHub di org + branch protection.
- Siapa pemilik dan pengguna tetap alat ini (persona QA).

## Sumber Daya

**Komponen dan alat:**
- [scrcpy](https://github.com/Genymobile/scrcpy) — mirroring dan kontrol HP, inti teknis yang juga dipakai Panda.
- [Maestro](https://maestro.mobile.dev) — framework uji UI mobile berbasis YAML, black-box lewat accessibility tree.
- [Android SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools) — `adb`.
- [Google USB Driver](https://developer.android.com/studio/run/win-usb) — driver USB resmi untuk Windows, pengganti pemasang driver Panda.

**Analisis Panda:**
- [Manual resmi Panda](https://doc.some3c.com/panda-manual/quickstart) — daftar fitur yang dijadikan rujukan (dan yang sengaja tidak ditiru).
- [Hasil VirusTotal installer Panda](https://www.virustotal.com/gui/file/3d857a283f97dee627082e57789832700def545be1cda3e767be9c3b4ae1d037) — SHA256 `3D857A28…4AE1D037`, 1/65.
- [innoextract](https://constexpr.org/innoextract/) — mengekstrak installer Inno Setup tanpa menjalankannya.
- [JADX](https://github.com/skylot/jadx) — decompiler APK.
- [REA: Reverse Engineer Anything](https://github.com/morluto/rea) — MCP server reverse engineering. Tidak dipakai di analisis ini (butuh Node ≥ 24.11 dan Ghidra), dicatat sebagai opsi untuk analisis berikutnya.
- Laporan Analisis Keamanan Aplikasi Panda (Claude Docs, privat): minta akses ke tim IT.

## Dokumen Terkait

- [[IT - Development Apps and Tools]] — tools internal tim
- [[IT - Security]] — kebijakan keamanan IT
- [[Microservices - Assistant Service]] — Copilot ERP, pola loop agen dan router AI yang ditiru
- [[CORE - Kapabilitas AI dan Machine Learning]] — kapabilitas AI di ERP
- [[IT - Big Pictures]] — peta domain IT
