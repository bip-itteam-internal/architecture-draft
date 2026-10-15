> Detail ingatan tim, dibaca **ON-DEMAND** dari indeks `../team-memory.md`. Jangan di-import ke `CLAUDE.md`; update cukup `git pull architecture-draft`.

## Gotchas repo & RBAC
- **Repo mybharata di-rename** `hris_bharata` → **`my-bharata`** (`github.com/bip-itteam-internal/my-bharata`). Remote `origin` lokal lama masih menunjuk nama lama tapi push/`gh` jalan via redirect; rapikan: `git remote set-url origin https://github.com/bip-itteam-internal/my-bharata.git`.
- **RBAC `system_roles`**: key = **kode MODUL** (`it`,`hris`,`finance`,`ga`,…), **BUKAN** nama departemen (pemetaan modul→nama dept di `shared-library/common/roles.go` `deptKeyToNames`; `space.division` simpan nama dept). `system_roles` = hak akses **modul/menu**, **bukan hierarki org** — **atasan/supervisor departemen ada di `work_data`** (`is_supervisor:true` + `department`), bukan di `system_roles`.

### ⛔ "HRGA" adalah LABEL SUPERVISI, bukan nama departemen siapa pun

Tak seorang pun ber-`work_data.department` = `HRGA`. Isinya selalu **`Human Resource`** atau **`General Affair`**; `HRGA` adalah `master_department.supervision_label` yang lahir dari `supervised_by`. Master data yang menentukan, bukan kode, jadi pengelompokannya bisa **batal** kapan saja dan saat itu terjadi kedua nama asli muncul kembali terpisah.

Backend sudah menangani ini dan konsisten. Diukur di prod 2026-08-25: `GET /kpi` dengan filter `Human Resource`, `General Affair`, maupun `HRGA` membalas **blok yang sama persis** berlabel `HRGA` berisi 20 orang. Begitu juga `KPIAutoConfig.Scope: "department"` yang mekar ke seluruh grup lewat master data (`kpi_auto.go`, `idAnggotaCakupan`).

Yang berulang kali salah adalah **frontend**, dan kegagalannya SENYAP di kedua arah. Keduanya terjadi pada hari yang sama:

1. **Pemilih tak digrupkan** → `Human Resource` dan `General Affair` tampil sebagai dua pilihan untuk satu kelompok, dan **kedua pilihan menampilkan 20 orang yang identik**. Tak ada galat, tak ada angka salah, cuma jumlah pilihannya yang keliru sehingga pembacanya mengira ada dua tim (erp-frontend [#1210](https://github.com/bip-itteam-internal/erp-frontend/pull/1210)).
2. **Pemilih digrupkan tapi konsumennya mencocokkan `work_data.department` PERSIS** → nol anggota, dan layar berbunyi **"Tidak ada anggota"** untuk grup yang berisi 20 orang (erp-frontend [#1212](https://github.com/bip-itteam-internal/erp-frontend/pull/1212)).

Aturan yang berlaku:

- **Label grup sah dipakai sebagai FILTER** ke backend, dan backend menerjemahkannya. Daftar bergrupnya dari `GET /data-type/department?grouped=true`. ⚠️ Nilainya dibandingkan dengan string **`"true"` persis**, jadi `grouped=1` diabaikan diam-diam dan mengembalikan daftar mentah.
- **Label grup TIDAK PERNAH cocok** dengan `work_data.department` seorang pun. Kode yang menyaring per orang wajib membandingkan dengan **label BLOK yang dikembalikan backend**, bukan menyimpulkan "hasilnya kosong berarti tak ada anggota". Menjatuhkannya ke "kalau kosong tampilkan semua" juga salah: departemen yang memang kosong lalu terisi orang lain, dan itu jauh lebih sulit disadari daripada daftar kosong.
- ⛔ **Layar yang MENULIS nama departemen tak boleh memakai daftar bergrup.** `kpi_template.department` menyimpan nama ASLI (`Human Resource` / `General Affair`); template yang tersimpan sebagai `HRGA` tak akan cocok dengan `work_data` siapa pun, dan gagalnya senyap: templatenya jadi, lalu tak pernah terpakai menilai siapa-siapa. Karena itu `template-editor.tsx` sengaja TIDAK digrupkan sementara `kpi-page-content.tsx` digrupkan.
- Dari 24 pemanggil `useDataTypes({ endpoint: "department" })` di erp-frontend, per 2026-08-25 baru **5** yang memakai `grouped`. Sisanya belum diperiksa satu per satu, dan untuk sebagian halaman departemen mentah memang yang benar. **Putuskan per halaman**, jangan sapu massal.

⛔ **Di BACKEND, kelas ini punya bentuk yang lebih senyap lagi: 200 berisi NOL baris.** Dua fungsi bernama mirip TIDAK boleh dipakai bergantian, dan yang keliru tak pernah melempar galat:

| Fungsi | Menerima | Untuk |
|---|---|---|
| `ResolveDepartmentFilter` | **label grup** ATAU nama departemen | menerjemahkan nilai yang datang **dari layar** |
| `SupervisedDepartments` / `ExpandToDepartmentGroup` | **nama departemen** saja | memekarkan satu nama ke grupnya |

`SupervisedDepartments(master, "HRGA")` mencari master department yang **NAMANYA** "HRGA" — label itu tinggal di `supervision_label`, bukan di `name` — lalu mengembalikan `"HRGA"` **apa adanya** (`department_scope.go`). Filter yang memakainya tak cocok dengan `work_data` siapa pun, jadi endpoint membalas **200 tanpa satu pun baris**, dan layar berbunyi "belum ada datanya" alih-alih "filternya tak menemukan siapa-siapa".

Terjadi **dua kali dalam satu hari** (2026-08-26): `/kpi/auto-scores` membuat kolom "Terhitung otomatis" berbunyi **0/20** untuk grup berisi 20 orang (bip-erp [#1444](https://github.com/bip-itteam-internal/bip-erp/pull/1444)), lalu `/kpi/template-assignment` membuat penetapan template satu grup tampil kosong ([#1454](https://github.com/bip-itteam-internal/bip-erp/pull/1454)). **Perbaikan pertama tak ikut menyentuh yang kedua** — bukti langsung bahwa aturannya tak boleh punya dua salinan.

⛔ **Bentuk ketiga: label grup DI DALAM CSV.** `ResolveDepartmentFilter` sendiri pun sempat hanya mengenali label yang **berdiri sendiri**, karena perbandingannya dilakukan terhadap SELURUH nilai. Label yang sama sebagai satu potongan di antara nama lain diteruskan mentah, dan akibatnya sama: 200 berisi baris KURANG.

Yang membuatnya bergejala: `DepartmentFilterOptions` sengaja MENGGANTI anggota grup dengan satu entri berlabel, jadi layar mana pun yang menggabungkan seluruh opsi dropdown jadi satu CSV mengirim satu label untuk **SETIAP** grup. Tab "Per Karyawan" halaman KPI melakukan persis itu (`departmentOptions.join(",")`), sehingga yang hilang **bukan satu departemen melainkan seluruh departemen yang punya grup** — dua puluh orang HRGA lenyap dari pencarian, dan mengklik salah satunya dari kartu Per Departemen melompat ke orang lain. ⚠️ **Round-trip per-opsi tak menangkapnya**: test lama memeriksa tiap opsi satu per satu, dan satu per satu memang sudah benar sejak dulu; yang patah cuma gabungannya. Kunci bentuk yang benar-benar dikirim FE (`Join(DepartmentFilterOptions(...), ",")`), bukan elemennya.

**Yang benar untuk nilai dari layar** adalah komposisi keduanya, persis seperti `GET /kpi`: `ExpandToDepartmentGroup(ResolveDepartmentFilter(master, q))`. Di employee-service ia kini tinggal di satu tempat, `cakupanDepartemenKPI`, dengan penjaga pemindai sumber berdaftar-izin per berkas — pemanggil baru `employee.SupervisedDepartments` atas nilai query membuat testnya merah. **Pemanggilan yang memakai `work_data.department` milik seseorang tetap AMAN** dan sengaja diizinkan: label grup tak pernah tersimpan di sana.

⚠️ **Unit test biasa tak menangkap kelas ini**, dan itu sebabnya penjaganya memindai sumber: jalur yang salah tetap mengembalikan slice yang **sah**, cuma berisi nama yang tak dimiliki siapa pun.

