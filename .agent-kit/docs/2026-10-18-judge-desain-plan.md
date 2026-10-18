# Judge Desain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Menambah lapis ketiga `/judge` untuk diff layar erp-frontend: skrip yang menangkap layar dari build worktree dengan API distub, dan agen read-only `loop-judge-desain` yang menilainya; temuan kritis memblokir PR.

**Architecture:** Keputusan deterministik (pemicu, validasi manifest, klasifikasi hasil tangkapan, bantahan) tinggal di `hooks/layar-lib.py` dan diuji pytest. Tangkapan dikerjakan `hooks/tangkap-layar.mjs` (Node 24, CDP lewat `WebSocket` bawaan, tanpa puppeteer) yang dibungkus `hooks/tangkap-layar.ps1` (menyalakan `pnpm start` atas build gerbang). Agen dan command hanya merujuk path; isi `ui-checklist.md` tidak disalin.

**Tech Stack:** Python 3 + pytest (pola `tests/test_gerbang.py`), Node 24 ESM, PowerShell 5.1, Chrome headless, Markdown agen/command kit.

**Spec:** `architecture-draft/.agent-kit/docs/2026-10-18-judge-desain-design.md`

## Global Constraints

- Hanya repo `erp-frontend`. MyBharata tidak menyalakan apa pun.
- Temuan **kritis** judge desain memblokir; `lolos = gerbang AND verdict AND verdict_desain` bila judge desain menyala.
- Tangkapan gagal **tidak** memblokir: judge menilai dari kode saja, `layar_dinilai: false`, alasan ditulis di verdict, log, dan badan PR.
- Mendarat di `/login` = tangkapan gagal. Error boundary = galat kode, apa pun isi konsol (diubah 2026-10-18: build produksi tanpa source map, jadi syarat konsol menunjuk berkas diff tak pernah terpenuhi); galat alat dan `/login` menang lebih dulu.
- Manifest tidak ada / tidak sah padahal diff menyentuh layar = temuan kritis untuk eksekutor.
- Hanya baris yang ditambahkan/diubah diff yang bisa kritis; pelanggaran lama = informasional.
- Saat judge desain menyala, `loop-judge` melewati `review-checklist.md` §F dan §J untuk berkas erp-frontend; i18n tetap milik `loop-judge`.
- Stub: `employee/me` selalu 200; tak distub = 500; **tidak pernah 401**; CORS `Access-Control-Allow-Origin: http://localhost:<port>` + `OPTIONS` 204; cegat "bukan localhost ATAU pathname `/api/`".
- Cookie `system_roles` bernilai string per modul; token JWT ber-`exp` jauh di depan; tidak pernah singgah ke `/login`.
- Matriks: desktop 1366 dan ponsel 390 × tema terang dan gelap (via `localStorage.theme` sebelum navigate, dibuktikan kelas `<html>`), bahasa `id`; keadaan data tambahan hanya desktop terang.
- Tangkapan viewport saja, tak pernah `captureBeyondViewport`.
- Jangan membunuh semua `chrome`; hanya proses berprofil uji dan pohon proses pemilik port.
- Batas percobaan loop tetap 3.
- Salah tuduh: bantahan eksekutor yang diterima judge + centang `- [ ] salah tuduh: <temuan>` di PR.
- Tanpa trailer `Co-Authored-By`. PowerShell, bukan Bash. Vault: stage per nama berkas, push `main`.

## Review Focus

- Manifest berisi rute yang tak ada (404 Next) → harus jadi tangkapan gagal ber-alasan, bukan galat kode dan bukan lolos diam. Test di Task 1 (`test_klasifikasi_404_tangkapan_gagal`).
- Port pilihan sudah dipakai sesi lain / `pnpm start` tak pernah listen → skrip berhenti berbatas waktu dengan `galat` di `ringkasan.json`, tak menggantung loop. Test di Task 2 (`batas waktu server`).
- Diff hanya mengubah locale atau test FE → judge desain tidak menyala. Test di Task 1 (`test_locale_dan_test_bukan_layar`).
- Judge desain menerima `ringkasan.json` yang `rute`-nya kosong (semua gagal) → harus dibaca sebagai `layar_dinilai: false`, bukan "layar bersih". Test di Task 1 (`test_ringkasan_tanpa_tangkapan_tidak_dinilai`) dan aturan di Task 3.
- Bantahan merujuk temuan yang tak ada di verdict sebelumnya → diabaikan dan dicatat, tidak dihitung salah tuduh. Test di Task 1 (`test_bantahan_tanpa_temuan_diabaikan`).

---

### Task 1: `layar-lib.py` — keputusan deterministik

**Files:**
- Create: `.agent-kit/hooks/layar-lib.py`
- Create: `.agent-kit/tests/test_layar.py`
- Modify: `.agent-kit/hooks/gerbang-kit.py` (daftar test gerbang kit: tambah `tests/test_layar.py`)

**Interfaces:**
- Produces:
  - `berkas_layar(berkas: list[str]) -> list[str]` — berkas `.tsx` di bawah `src/app/`, `src/features/`, `src/components/`, kecuali `*.test.tsx`, `*.spec.tsx`, `__tests__/`.
  - `perlu_judge_desain(repo: str, berkas: list[str]) -> bool` — `repo == "erp-frontend"` dan `berkas_layar` tak kosong.
  - `validasi_manifest(obj: dict) -> list[str]` — daftar galat; kosong = sah. Skema: `{"rute":[{"path":str,"aksi":[{"klik_teks":str}|{"tab":str}]?,"keadaan":[str]}], "cookie":{"system_roles":{str:str},"position":str,"department":str,"lang":"id"|"en"}, "stub":{"<keadaan>":[{"pola":str,"status":int,"body":any}]}}`. Galat bila: `rute` kosong, `path` tak diawali `/`, nilai `system_roles` bukan string, `status == 401`, keadaan yang dirujuk rute tak ada di `stub`, `stub` tak punya `berisi` dan `kosong`.
  - `klasifikasi_rute(hasil: dict, berkas_diff: list[str]) -> str` — `"ok" | "tangkapan_gagal" | "galat_kode"`. `hasil` = satu entri `rute` dari `ringkasan.json` (`rute_akhir`, `status_http`, `error_boundary: bool`, `konsol: [str]`, `galat: str|None`).
  - `layar_dinilai(ringkasan: dict) -> bool` — True bila minimal satu rute `ok` atau `galat_kode`.
  - `hitung_salah_tuduh(verdict_desain_berikut: dict, bantahan: list[dict], temuan_sebelum: list[dict]) -> dict` — `{"diterima": int, "ditolak": int, "diabaikan": int}`; kunci temuan = `(file, line, alasan)`.
  - CLI: `python layar-lib.py perlu --repo <r> --berkas-dari <txt>` → cetak JSON `{"perlu": bool, "berkas_layar": [...]}`; `python layar-lib.py validasi <manifest.json>` → exit 0/1 + JSON galat; `python layar-lib.py ringkas <ringkasan.json> --berkas-dari <txt>` → JSON rute terklasifikasi + `layar_dinilai`.

- [ ] **Step 1: Tulis test yang gagal** di `tests/test_layar.py` (impor modul lewat `importlib.util` seperti `test_gerbang.py`):
  - `test_berkas_layar_memilih_tsx_ui`: `["src/app/hris/page.tsx","src/lib/axios.ts","src/features/kpi/components/x.tsx","src/features/kpi/x.test.tsx","src/i18n/locales/id.ts"]` → `["src/app/hris/page.tsx","src/features/kpi/components/x.tsx"]`.
  - `test_locale_dan_test_bukan_layar`: `perlu_judge_desain("erp-frontend", ["src/i18n/locales/en.ts","src/features/a/__tests__/b.tsx"]) is False`.
  - `test_repo_lain_tidak_menyala`: `perlu_judge_desain("my-bharata", ["src/app/x.tsx"]) is False`.
  - `test_manifest_sah`: manifest minimal (satu rute, keadaan `berisi`+`kosong`) → `[]`.
  - `test_manifest_roles_array_ditolak`: `system_roles: {"hris": ["supervisor"]}` → satu galat menyebut `system_roles`.
  - `test_manifest_stub_401_ditolak`, `test_manifest_tanpa_keadaan_kosong_ditolak`, `test_manifest_keadaan_tak_dikenal_ditolak`.
  - `test_klasifikasi_login_tangkapan_gagal`: `rute_akhir="/login"` → `"tangkapan_gagal"`.
  - `test_klasifikasi_404_tangkapan_gagal`: `status_http=404` → `"tangkapan_gagal"`.
  - `test_error_boundary_menunjuk_diff_galat_kode`: `error_boundary=True`, `konsol=["TypeError ... at src/features/kpi/components/x.tsx:12"]`, diff memuat berkas itu → `"galat_kode"` (sama dengan kasus berikutnya: boundary selalu galat_kode).
  - `test_error_boundary_bukan_diff_galat_kode`: konsol menunjuk `src/components/table/index.tsx`, tak di diff → tetap `"galat_kode"` (diubah 2026-10-18: build produksi tanpa source map, jadi tak ada syarat konsol). Ditambah `test_error_boundary_konsol_chunk_kosong_galat_kode` dan `test_error_boundary_kalah_dari_galat_dan_login` (galat alat dan `/login` menang lebih dulu).
  - `test_ringkasan_tanpa_tangkapan_tidak_dinilai`: `{"rute": []}` → `layar_dinilai` False; semua `tangkapan_gagal` → False.
  - `test_bantahan_diterima_dihitung`, `test_bantahan_ditolak_dihitung`, `test_bantahan_tanpa_temuan_diabaikan`.

- [ ] **Step 2: Jalankan, pastikan gagal**
  Run: `$env:PYTHONDONTWRITEBYTECODE=1; architecture-draft/Tools/.venv/Scripts/python.exe -m pytest -p no:cacheprovider -q architecture-draft/.agent-kit/tests/test_layar.py`
  Expected: FAIL (modul tidak ditemukan).

- [ ] **Step 3: Implementasikan fungsi-fungsi di atas** di `hooks/layar-lib.py`, docstring kepala gaya `gerbang-kit.py` (mengapa, bukan apa). Pencocokan berkas di konsol: normalisasi `\` → `/`, cocokkan sufiks path diff di dalam baris.

- [ ] **Step 4: Jalankan, pastikan lulus** (perintah sama). Expected: semua PASS.

- [ ] **Step 5: Kontrol negatif**: ubah sementara `klasifikasi_rute` agar `/login` → `"ok"`, pastikan `test_klasifikasi_login_tangkapan_gagal` merah pada assertion itu, kembalikan.

- [ ] **Step 6: Daftarkan `tests/test_layar.py` di `gerbang-kit.py`**, lalu commit:
  `git add .agent-kit/hooks/layar-lib.py .agent-kit/tests/test_layar.py .agent-kit/hooks/gerbang-kit.py` → `git commit -F <berkas>` "feat(agent-kit): layar-lib, keputusan deterministik judge desain".

### Task 2: `tangkap-layar` — skrip tangkapan

**Files:**
- Create: `.agent-kit/hooks/tangkap-layar.mjs`
- Create: `.agent-kit/hooks/tangkap-layar.ps1`
- Create: `.agent-kit/tests/fixtures/layar/index.html` (halaman uji: tombol, elemen yang meluber sengaja, penanda tema)
- Create: `.agent-kit/tests/test-tangkap-layar.ps1`
- Modify: `.agent-kit/tests/test-init.ps1` (panggil `test-tangkap-layar.ps1`; lewati dengan pesan tercetak bila Chrome tak ada)

**Interfaces:**
- Consumes: skema manifest dari Task 1.
- Produces:
  - `node tangkap-layar.mjs --url-dasar <http://localhost:p> --manifest <json> --keluaran <dir> [--chrome <exe>] [--batas-rute-detik 90]` → menulis `<dir>/ringkasan.json` dan PNG `<dir>/<i>-<keadaan>-<lebar>-<tema>.png`.
  - `ringkasan.json`: `{"url_dasar":str,"rute":[{"path":str,"keadaan":str,"lebar":1366|390,"tema":"light"|"dark","png":str,"rute_akhir":str,"status_http":int,"error_boundary":bool,"konsol":[str],"galat":str|null,"tema_terbukti":str,"ukuran":{"luber_halaman":bool,"luber_wadah":[{"selektor":str,"scrollWidth":int,"clientWidth":int}],"tumpang":[{"a":str,"b":str}],"disabled":[{"teks":str,"opacity":str,"pointerEvents":str}]}}],"galat":str|null}`.
  - `tangkap-layar.ps1 -Path <wt> -Manifest <json> -Keluaran <dir>` → memilih port bebas (bukan 3000), `pnpm start -p <port>` (build sudah ada dari gerbang; tanpa `.next` → `galat` "build tidak ada"), tunggu listen ≤ 60 dtk, panggil `.mjs`, hentikan pohon proses pemilik port. Exit 0 selalu bila `ringkasan.json` tertulis (galat ada di isinya); exit 1 hanya bila tak bisa menulis apa pun.

- [ ] **Step 1: Tulis test integrasi yang gagal** `tests/test-tangkap-layar.ps1` (pola `Check` dari `test-init.ps1`): server statis Node sekali-pakai menyajikan `fixtures/layar/`, manifest uji dengan rute `/index.html` dan `/tidak-ada.html`, lalu periksa:
  - `ringkasan.json` ada dan 4 entri untuk `/index.html` keadaan `berisi` (2 lebar × 2 tema) + 1 entri `kosong` (desktop terang).
  - `tema_terbukti` `light`/`dark` sesuai entri (fixture membaca `localStorage.theme` ke kelas `<html>`).
  - `ukuran.luber_wadah` memuat selektor elemen yang sengaja meluber; elemen yang tak meluber tidak.
  - entri `/tidak-ada.html` ber-`status_http` 404.
  - permintaan fixture ke `/api/x` menerima body stub, dan ke `/api/tak-distub` menerima 500 (fixture menuliskan status ke DOM).
  - tidak ada proses `chrome` ber-`--user-data-dir` profil uji tersisa sesudahnya.

- [ ] **Step 2: Jalankan, pastikan gagal**
  Run: `powershell -NoProfile -ExecutionPolicy Bypass -File architecture-draft/.agent-kit/tests/test-tangkap-layar.ps1`
  Expected: FAIL (skrip tidak ada).

- [ ] **Step 3: Implementasikan `tangkap-layar.mjs`**: Chrome `--headless=new --remote-debugging-port=<p> --user-data-dir=<baru>` (argumen satu string), siap = `/json/version` menjawab; satu target per entri; `Fetch.enable` + `Fetch.fulfillRequest` sesuai Global Constraints; `Page.addScriptToEvaluateOnNewDocument` untuk `localStorage.theme` dan cookie lewat `Network.setCookie` ber-`url`; `Emulation.setDeviceMetricsOverride` untuk lebar; tutup overlay (`Escape`, tombol berteks "Nanti saja", "Ingatkan saya nanti", "Mengerti"); jalankan `aksi`; rekam `Runtime.consoleAPICalled`/`exceptionThrown`; ukur DOM; `Page.captureScreenshot` tanpa `captureBeyondViewport`. Error boundary dideteksi dari teks `Terjadi Kesalahan`.

- [ ] **Step 4: Implementasikan `tangkap-layar.ps1`** sesuai Interfaces.

- [ ] **Step 5: Jalankan test, pastikan lulus.** Expected: semua `Check` OK.

- [ ] **Step 6: Uji asap manual sekali atas worktree erp-frontend nyata** (satu halaman daftar yang sudah ada, manifest tangan), lihat PNG-nya dengan `Read`, catat hasil di `## Hasil` rencana ini. Ini bukti, bukan test otomatis.

- [ ] **Step 7: Commit** keempat berkas + `test-init.ps1`: "feat(agent-kit): tangkap-layar, tangkapan layar build worktree dengan stub".

### Task 3: agen `loop-judge-desain`

**Files:**
- Create: `.agent-kit/agents/loop-judge-desain.md`
- Modify: `.agent-kit/tests/test-init.ps1`

**Interfaces:**
- Consumes: path brief, diff, `ui-checklist.md`, manifest, keluaran `layar-lib.py ringkas` (atau `"tidak tersedia: <alasan>"`), worktree, bantahan eksekutor (boleh kosong).
- Produces: blok
  ```
  <<VERDICT_DESAIN>>
  {"lolos":bool,"layar_dinilai":bool,"temuan":[{"file":str,"line":int,"kelas":"kritis|informasional","sumbu":"konsistensi|kemudahan","bukti":"file:line|ukuran:<png>#<field>","alasan":str,"saran":str}],"bantahan":[{"temuan":{"file":str,"line":int,"alasan":str},"putusan":"diterima|ditolak","alasan":str}],"catatan":[str],"ringkasan":str}
  <<END>>
  ```

- [ ] **Step 1: Tulis pemeriksaan yang gagal** di `test-init.ps1`: berkas agen tersalin ke `.claude/agents/`; frontmatter `tools: Read, Grep, Glob`; isi memuat `<<VERDICT_DESAIN>>`, `layar_dinilai`, `bantahan`, dan path `ui-checklist.md`; isi **tidak** memuat judul bagian `## 2a. Sheet` (bukti checklist dirujuk, bukan disalin).
- [ ] **Step 2: Jalankan `test-init.ps1`**, pastikan pemeriksaan baru merah.
- [ ] **Step 3: Tulis agen** dengan `model: opus`, `maxTurns: 40`. Isi: peran; dua sumbu (konsistensi = `ui-checklist.md` §1–§2d + Konvensi FE team-memory **tanpa** i18n; kemudahan = §2 + alur di brief); aturan kritis dan anti-salah-tuduh persis Global Constraints; temuan dari gambar tanpa ukuran = informasional/pertanyaan; selera = informasional; `layar_dinilai` disalin dari input, bukan dinilai sendiri; wajib memutus tiap bantahan; manifest tak cukup keadaan = temuan. Daftar "jangan dilaporkan" diambil dari memori `erp-frontend-verifikasi-layar-tanpa-backend` (tombol disabled primary tampak menyala, label sumbu Recharts dilewati di 390px, batang nol tak dirender, indikator dev Next, `PopoverContent`/`Card` tanpa `data-slot`).
- [ ] **Step 4: Jalankan `test-init.ps1`**, pastikan hijau.
- [ ] **Step 5: Commit**: "feat(agent-kit): agen loop-judge-desain".

### Task 4: sambungkan ke `/judge`, `/kerjakan`, dan eksekutor

**Files:**
- Modify: `.agent-kit/commands/judge.md` (langkah 3: syarat kirim `ui-checklist.md` ke `loop-judge` dibalik; langkah 3b baru; langkah 4 triangulasi + baris laporan `Desain:`)
- Modify: `.agent-kit/commands/kerjakan.md` (§3 field log `verdict_desain`, `layar`, `salah_tuduh`; §4 temuan desain + bantahan; §5 badan PR)
- Modify: `.agent-kit/agents/loop-judge.md` (lewati §F/§J untuk erp-frontend bila prompt menyebut judge desain menyala)
- Modify: `.agent-kit/agents/loop-fe.md`, `loop-test.md`, `loop-fix.md`, `loop-refactor.md` (wajib manifest bila menyentuh layar erp-frontend; bagian laporan `Bantahan`)
- Modify: `.agent-kit/commands/supervise.md` + `.agent-kit/agents/loop-supervisor.md` (hitung judge desain dari log `salah_tuduh` + centang PR lewat `gh pr view --json body`; tampilkan setelah ≥ 10 run)
- Modify: `.agent-kit/tests/test-init.ps1`

**Interfaces:**
- Consumes: CLI `layar-lib.py` (Task 1), `tangkap-layar.ps1` (Task 2), agen (Task 3).
- Produces: path tetap `.task-plans/judge/<slug>-layar.json` (manifest), `.task-plans/judge/<slug>-<n>-layar/` (tangkapan), log ber-field `verdict_desain`, `layar`, `salah_tuduh`.

- [ ] **Step 1: Tulis pemeriksaan yang gagal** di `test-init.ps1`, tiap pemeriksaan dibatasi ke potongan bagiannya (pola 1.39.0):
  - `judge.md` langkah 3b menyebut `layar-lib.py perlu`, `tangkap-layar.ps1`, `loop-judge-desain`, dan `layar_dinilai`; langkah 4 memuat `verdict_desain`.
  - `judge.md` langkah 3 tidak lagi mengirim `ui-checklist.md` ke `loop-judge` bila judge desain menyala.
  - `kerjakan.md` §3 memuat `verdict_desain`, `layar`, `salah_tuduh`; §5 memuat `- [ ] salah tuduh:`.
  - `loop-judge.md` memuat `§F` dan `§J` dalam kalimat pengecualian.
  - keempat eksekutor memuat `<slug>-layar.json` dan `Bantahan`.
  - `supervise.md` memuat `salah_tuduh` dan `salah tuduh:` (centang PR).
- [ ] **Step 2: Jalankan `test-init.ps1`**, pastikan merah.
- [ ] **Step 3: Sunting `judge.md`**: 3b = (a) `layar-lib.py perlu` atas berkas diff; tidak perlu → lewati, tulis "Desain: tidak menyala"; (b) manifest: `layar-lib.py validasi`; tidak ada/tidak sah → temuan kritis untuk eksekutor, judge desain tetap dijalankan dari kode; (c) `tangkap-layar.ps1` dengan `run_in_background: true`, lalu `layar-lib.py ringkas`; (d) dispatch `loop-judge-desain`; (e) urai `<<VERDICT_DESAIN>>`, tak terurai → `lolos: false`. Langkah 4: `lolos = gerbang AND verdict AND verdict_desain`; baris laporan `Desain: <lolos|gagal|tidak menyala> · layar dinilai <ya|tidak: alasan> · kritis <n>`.
- [ ] **Step 4: Sunting `kerjakan.md`**: §3 field log; `salah_tuduh` dari `layar-lib.py` `hitung_salah_tuduh` pada percobaan ≥ 2; §4 temuan kritis desain masuk "Yang harus diperbaiki", ditambah "boleh membantah dengan bukti di bagian Bantahan"; §5 badan PR: ringkasan desain, daftar PNG, alasan bila layar tak tertangkap, dan satu `- [ ] salah tuduh: <file:line — alasan>` per temuan desain.
- [ ] **Step 5: Sunting `loop-judge.md`, keempat eksekutor, `supervise.md`, dan `loop-supervisor.md`** sesuai Files. Supervisor melaporkan per periode: run menyala, temuan kritis desain, salah tuduh (bantahan diterima + centang), run dengan `layar_dinilai: false` beserta alasannya.
- [ ] **Step 6: Jalankan `test-init.ps1`**, pastikan hijau.
- [ ] **Step 7: Commit**: "feat(agent-kit): judge desain di /judge dan /kerjakan".

### Task 5: versi, changelog, ingatan tim

**Files:**
- Modify: `.agent-kit/VERSION` (`1.41.0`; cek dulu `git show origin/main:.agent-kit/VERSION`, nomor diklaim saat push)
- Modify: `.agent-kit/README.md` (§ Isi kit: agen + skrip baru; § Changelog: entri 1.41.0, **Butuh re-init**)
- Modify: `.agent-kit/rules/team-memory.md` (§ Skill & tooling AI: satu butir judge desain yang merujuk spec, tidak menyalin aturannya)

- [ ] **Step 1:** Sunting ketiga berkas. Changelog menyebut alasan (M-04, Portal KPI, Sheet 16/24), hasil kontrol negatif Task 1, dan hasil uji asap Task 2.
- [ ] **Step 2:** Jalankan `python architecture-draft/.agent-kit/hooks/gerbang-kit.py` (atau push yang memicunya) dan `test-init.ps1`; keduanya hijau.
- [ ] **Step 3:** Commit, `git merge origin/main`, push `main` dengan `run_in_background: true`.

## Cara Verifikasi

- `tests/test_layar.py` dan `tests/test-tangkap-layar.ps1` hijau, kontrol negatif Task 1 terbukti merah.
- Uji asap Task 2: PNG halaman erp-frontend nyata terbaca, tema terbukti, tanpa `/login`.
- Satu `/kerjakan` sungguhan atas brief FE kecil sesudah re-init: log memuat `verdict_desain` dan `layar`, badan PR memuat centang salah tuduh. Ini butuh manusia memilih brief-nya; dicatat sebagai butir terbuka di `/wrap`.

## Hasil

### Uji asap Task 2 (2026-10-18)

- **Sasaran**: worktree `C:\Users\irfan\wt\fe-cek-main` (build sudah ada, commit `cbba5af04`, tanpa `.env`
  sehingga API relatif `/api/` ke server Next dan seluruhnya tercegat), rute `/hris/resign`, manifest
  tangan berkeadaan `berisi` (2 baris stub) dan `kosong`, lolos `layar-lib.py validasi`.
- **Hasil**: `tangkap-layar.ps1` exit 0. Lima entri (berisi 1366/390 x terang/gelap + kosong desktop
  terang), semuanya `status_http` 200, `rute_akhir` `/hris/resign` (tak satu pun ke `/login`),
  `error_boundary` false, `tema_terbukti` sama dengan tema yang diminta di kelima entri, `luber_halaman`
  false. Port dilepas, nol proses Chrome berprofil uji tersisa. PNG dilihat dengan `Read`: desktop
  terang (sidebar HRGA, kartu statistik), ponsel gelap (tata letak 390 sungguhan), segmen gulir kedua
  (tabel berisi dua baris stub dan paginasi), dan keadaan kosong (ilustrasi tabel kosong plus panel
  backlog "Gagal memuat ..." karena endpointnya sengaja tak distub).
- **Dua cacat alat ditemukan uji asap, diperbaiki, dan kini dijaga `test-tangkap-layar.ps1`**:
  1. `pola` stub semula potongan teks, sehingga stub daftar `/api/employee/resign` ikut menjawab
     `/resign/summary` dan `/resign/non-aktif-tanpa-catatan` dengan bentuk yang salah (baris daftar
     tampil di panel lain, tanpa galat). Kini **akhiran path**: pathname sama atau berakhiran pola;
     `/x/*` = awalan; `?k=v` di pola = parameter query wajib sama; pola terpanjang menang.
  2. Jendela tenang 1 dtk berakhir di dalam jeda retry React Query (1, 2, 4 dtk), sehingga panel yang
     tak distub terpotret sebagai Skeleton. Kini **4,5 dtk selama ada 5xx dalam 8 dtk terakhir**
     (maks 20 dtk), 1 dtk selain itu.
- **Waktu**: sekitar 15 dtk per entri di halaman nyata (5 entri = 76 dtk), ditambah Chrome menyala
  (bisa sampai 30 dtk di mesin ini). `/judge` sebaiknya menjalankan tangkapan di background.
- **Temuan source map**: build produksi Next tidak menerbitkan source map browser, jadi stack di
  `konsol` menunjuk chunk `/_next/static/chunks/<hash>.js`, bukan berkas sumber. Aturan lama "error
  boundary galat kode hanya bila konsol menunjuk berkas diff" karena itu tak pernah bisa terpenuhi.
  Diputuskan controller 2026-10-18: error boundary **selalu** galat kode (galat alat dan `/login`
  menang lebih dulu); `layar-lib.py`, `test_layar.py`, dan spec "Aturan tambahan" butir 1 sudah
  disesuaikan.
