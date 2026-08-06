## Deskripsi

*Endpoint **form-builder-service** (form dinamis + analisa jawaban + kepatuhan presensi). Gateway: `/api/form-builder/*`. Kelola form butuh **tingkat peran** `staff`/`supervisor`/`admin` di modul mana pun DAN departemen pemanggil ada di daftar departemen aktif; mengisi cukup terautentikasi. Grounded ke `services/form-builder/routes.go` + handler terkait (`main`, PR #849; kepemilikan per departemen PR #869).*

- **Status**: ⚠️ Implemented (live di dev **dan prod** sejak 2026-08-01; **penilaian karyawan, tipe form, dan rekap per orang dinilai** merged 2026-08-02 lewat PR #907 + #908 — **live di dev DAN prod** sejak 2026-08-02). **Form berulang** (`recurrence`, `period_key`, `?period=`) merged ke `main` 2026-08-03 lewat PR #938, #940, #942 — **setelah** deploy prod 08-01/08-02, jadi **status prod belum diverifikasi**. Baru didokumentasikan 2026-08-06 dan belum punya catatan uji end-to-end.
- **Kaizen** (`form_type: "kaizen"`, rute `/kaizen/*`, `/me/kaizen*`, `/internal/kaizen/metrics`) ✅ **live dev + prod** sejak 2026-08-06 lewat PR #1016, #1028, #1029, #1034, #1039, #1044, #1046 — seluruhnya teruji end-to-end di dev. Belum ada satu pun form kaizen di prod, jadi masih inert.
- **Implementasi**: [[Microservices - Form Builder Service]]
- **Indeks**: [[API - Index]]
- **Konsumen**: seluruh rute `/forms*` — termasuk `analytics`, `responses`, `export` — dipakai [[APP - Web ERP]]. Rute **`/me/*`** dipakai [[APP - MyBharata]] (section Survei di beranda + halaman pengisian), dan **`/me/kaizen*`** dipakai menu Kaizen tersendiri di aplikasi itu.

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Health check (di belakang gateway key) |

## Kelola Form (RBAC per departemen)
| Method | Path | Fungsi |
|---|---|---|
| POST | `/forms` | Buat form (lahir `draft`; `owner_department` wajib dan harus dalam cakupan pemanggil. Ejaannya **dikanonikkan** ke daftar departemen aktif) |
| GET | `/forms` | Daftar form departemen yang boleh dikelola pemanggil (`?status=`, `?form_type=`, `?search=`, `?page=`, `?limit=` maks 100). Tiap item membawa `form_type`, `response_count` (jumlah jawaban) dan `respondent_count` (jumlah ORANG) |
| GET | `/forms/:id` | Detail + `response_count` |
| PATCH | `/forms/:id` | Sunting. `409` bila susunan field diubah padahal sudah ada jawaban (**berlaku juga untuk form berulang**, lihat catatan di bawah). `409` juga bila `recurrence` **dinyalakan** pada form yang sudah punya jawaban; mematikannya tetap boleh. `owner_department` tak bisa dipindah |
| PATCH | `/forms/:id/status` | `draft`→`published`→`closed`. `409` bila mencoba mundur dari `published` ke `draft`. Saat terbit: **memotret sasaran penilaian** (`422` bila gagal, kosong, atau >300 orang) lalu mengirim notifikasi inbox ke seluruh sasaran |
| DELETE | `/forms/:id` | Hapus lunak (`deleted_at` + status `closed`) |

> **Cakupannya departemen, bukan modul.** Diambil dari `common.SupervisedDepartments` (departemen sendiri + yang dibawahi lewat `master_department.supervised_by`) lalu diiris daftar departemen aktif. SPV HRGA karena itu melihat form Human Resource **dan** General Affair, tapi tidak Tech Development. Daftar aktifnya konfigurasi `FORM_BUILDER_DEPARTMENTS`; bila kosong dipakai bawaan `Human Resource, General Affair, Tech Development`.

## Analisa & Export (RBAC per departemen)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/forms/:id/analytics` | Rekap per pertanyaan + tren harian + tingkat pengisian (lihat bentuk respons di bawah). `?period=` menyaring satu putaran form berulang |
| GET | `/forms/:id/responses` | Daftar jawaban berhalaman (`?page=`, `?limit=` maks 200), terbaru dulu. `?period=` |
| GET | `/forms/:id/export` | CSV (`text/csv`). Header `X-Export-Truncated` muncul bila menyentuh batas 20.000 baris. `?period=` |

> **`?period=` kosong berarti SELURUH periode di sini**, dan itu KEBALIKAN dari arti periode kosong pada penjaga duplikat saat mengisi (di sana kosong berarti "hanya jawaban yang memang tak punya periode"). Pemilik form yang membuka halaman analisa tanpa memilih periode mengharapkan rekap penuh, bukan rekap yang diam-diam menyusut.

> **Kolom dan kartu analisa mengikuti pertanyaan PERIODE yang diminta**, bukan susunan terbaru milik form. Keduanya bisa berbeda karena pertanyaan form berulang boleh disunting untuk periode berikutnya. Tanpa `?period=`, yang dipakai adalah susunan terbaru — pada rentang banyak periode memang tak ada satu susunan yang benar.

## Pengisian (karyawan terautentikasi)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/me/capability` | `{can_manage, departments[]}` — apa yang boleh dilakukan pemanggil di Form Builder |
| GET | `/me/forms` | Form terbit yang ditujukan ke pemanggil (+`owner_department`, `form_type`, `submitted`, `blocks_attendance`, `gate_end_date`). Form penilaian ikut membawa `subject_enabled`, `subject_total`, `subject_done`, `subject_anonymous`. Pada form berulang, `submitted` dihitung terhadap **periode berjalan**, bukan seumur hidup form |
| GET | `/me/forms/:id/subjects` | Daftar orang yang harus DINILAI pemanggil + `progress{done,total,anonymous}`. `409` bila form tak menilai siapa pun |
| POST | `/me/forms/:id/responses` | Kirim jawaban (+`subject_employee_id` untuk form penilaian). `403` bila bukan sasaran atau menilai orang di luar daftar, `409` bila form tak `published` atau orang itu sudah dinilai. Balas `subject_done`, `subject_total`, `all_completed` |
| GET | `/me/responses` | Riwayat jawaban sendiri |

> **Idempoten**: pengiriman identik dalam 2 menit dibalas `200 {"duplicate": true}` tanpa insert baru (sidik jawaban di-hash setelah kunci diurutkan, jadi payload yang disusun ulang saat retry tetap terdeteksi).

> **Kenapa `/me/capability` ada di grup pengisian, bukan di balik `requireFormManager`.** Daftar departemen aktif tinggal di konfigurasi server; tanpa endpoint ini setiap klien harus menyalinnya dan pasti melenceng saat daftarnya berubah. Ditaruh di `/me` supaya yang tak berhak menerima `can_manage:false` yang bisa dibaca klien, bukan `403` yang harus ditebak artinya. `departments` sengaja dikosongkan bila `can_manage:false`.

## Kaizen untuk karyawan (`/me/kaizen*`)

> Merged ke `main` 2026-08-06: papan ide lewat PR [#1028](https://github.com/bip-itteam-internal/bip-erp/pull/1028), permukaan karyawan lewat PR [#1034](https://github.com/bip-itteam-internal/bip-erp/pull/1034). **Belum diverifikasi lewat gateway hidup.**

**Terpisah dari `/me/forms` dengan sengaja.** Program Kaizen bukan "satu form lagi" bagi pengisinya: ia berulang tiap periode, berkuota, punya riwayat keputusan, dan idenya dibaca orang lain. [[APP - MyBharata]] menampilkannya di **menu tersendiri**, bukan bercampur di daftar survei.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/me/kaizen` | Program berjalan untuk pemanggil: `{has_program, form_id, title, description, fields, progress, board_visible}`. `progress` = `{quota, submitted, fulfilled, period_key, opens_at, closes_at}` |
| GET | `/me/kaizen/ideas` | Riwayat ide sendiri **lintas periode**, terbaru dulu. `?period=`, `?page=`, `?limit=` maks **50**. Balas `{data[{id,period_key,submitted_at,answers,decision}], total, page, limit, fields}` |
| GET | `/me/kaizen/board` | Papan ide publik: `{data[{id,employee_name,department,status,submitted_at,answers}], period_key}`. `?period=` (default periode berjalan), maks **100** kartu |
| GET | `/me/kaizen/committee` | Program mana yang boleh ditinjau pemanggil: `{is_committee, form_id, title, period_key, can_manage_form}`. Bukan komite dibalas `{is_committee:false}`, **bukan `403`** |

> **Kenapa penemuan komite ada di `/me/*`, bukan `/kaizen/*`.** Seluruh rute komite menuntut id form, dan satu-satunya cara lain menemukannya adalah `GET /forms` — yang digerbang peran pengelola DAN departemen aktif, sedangkan komite ditunjuk HR dan bisa saja staf biasa dari departemen mana pun. Rute ini justru harus bisa dipanggil orang yang haknya **belum diketahui**, karena itu memang pertanyaannya. Dipakai menu **Komite Kaizen** di [[APP - Web ERP]]. `can_manage_form` membedakan anggota terdaftar dari pengelola departemen pemilik: keduanya boleh meninjau, hanya yang kedua boleh menyunting programnya.

> **Bukan sasaran program dibalas `has_program:false`, BUKAN `404`.** Menu Kaizen tetap bisa dibuka dan menjelaskan keadaannya, alih-alih menampilkan layar galat untuk keadaan yang sebenarnya normal. `has_program:false` juga menjawab "perusahaan ini belum punya program" — backend tak membedakan keduanya karena bagi pemakai keduanya memang sama.

> **Definisi pertanyaan dikirim SEKALI di tingkat atas** pada `/me/kaizen/ideas`, tidak diulang tiap ide. Riwayat 50 ide yang masing-masing membawa salinan definisi form akan berlipat ukurannya tanpa menambah satu pun informasi.

> **Papan menyaring dengan DAFTAR IZIN tipe field**, bukan daftar larangan. Papan dibaca seluruh karyawan, jadi tipe pertanyaan yang ditambahkan nanti (lampiran berkas, yang nilainya cuma id unggahan) tersembunyi secara bawaan sampai seseorang sengaja mengizinkannya. Daftar larangan bekerja sebaliknya: tipe baru bocor lebih dulu, ketahuan setelah tampil di depan sekantor. Ide yang masih ditinjau maupun yang ditolak **tak pernah** muncul; papan juga kosong bila `board_visible:false`.

> ✅ **`/me/kaizen` ikut membawa `blocks_attendance` dan `gate_end_date`** sejak PR [#1039](https://github.com/bip-itteam-internal/bip-erp/pull/1039), memakai perhitungan yang sama persis dengan `/me/forms`. Perlu karena form Kaizen dikeluarkan dari daftar survei di mobile: tanpanya, karyawan yang tertahan saat clock-in tak punya satu pun petunjuk di layar.

## Kaizen (komite program ide bulanan)

> Merged ke `main` 2026-08-06 lewat PR #1016. Dev naik otomatis lewat Harness, **belum diverifikasi**; prod tidak auto-deploy. Konsepnya di [[HRIS - Kaizen (Ide Perbaikan)]].

**Prefix `/kaizen/*`, SENGAJA di luar grup `/forms`.** Grup itu digerbang `requireFormManager` (tingkat peran pengelola + departemen aktif), sedangkan anggota komite ditunjuk HR dan bisa saja staf biasa dari departemen mana pun. Gerbangnya per-form: terdaftar di `settings.kaizen.committee_employee_ids` **atau** boleh mengelola departemen pemilik form.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/kaizen/forms/:id/responses` | Antrean komite. `?period=` (default periode berjalan), `?status=pending\|accepted\|rejected\|implemented`, `?department=`, `?page=`, `?limit=` maks 200. Membawa `fields` periode itu supaya label jawaban benar |
| PATCH | `/kaizen/forms/:id/responses/:responseId/decision` | Keputusan atas satu ide |
| POST | `/kaizen/forms/:id/responses/decisions` | Keputusan massal, maks **200** id sekali kirim. Membalas `{decided[], failed[{id,error}]}` — satu ide yang keburu diputuskan orang lain gagal sendirian, sisanya tetap tersimpan |
| GET | `/kaizen/forms/:id/compliance` | Papan kepatuhan periode itu: `{period_key, summary, data[]}` |
| GET | `/kaizen/forms/:id/compliance/export` | CSV kepatuhan. Header `X-Kaizen-Participants-Partial` muncul bila potret pesertanya belum lengkap |

> **Seluruh permukaan ini terkunci ke perusahaan pemanggil** (`common.CompanyID`), termasuk jalur bacanya. Override `?company=` milik admin pusat TIDAK berlaku di sini: memutuskan nasib ide adalah menulis, dan antrean sengaja ikut dikunci supaya yang dilihat selalu sama dengan yang bisa ditindak.

**Keputusan** (`decision` pada FormResponse): `{status, note, reviewed_by, reviewed_by_name, reviewed_at, implemented_at, pic_employee_id, pic_name, implementation_note}`. Absen = **belum ditinjau**; tak ada nilai `pending` yang tersimpan, jadi saringannya memakai `?status=pending` yang di server diterjemahkan jadi `$in: [null]`.

Transisi sah: belum ditinjau → `accepted`/`rejected`; `accepted` → `implemented`/`rejected`. `rejected` dan `implemented` **terminal** (`409`). Menolak **wajib** `note` (`400`), menandai diterapkan **wajib** `implemented_at` (`400`, sengaja tidak diisi otomatis karena skor KPI menghitung per periode).

⚠️ Menandai "diterapkan" pada ide yang belum pernah diterima saat ini dibalas `400`; seharusnya `409`. Diketahui, belum diperbaiki.

## Internal (dipanggil service lain)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/internal/compliance` | Form wajib yang belum diisi: `{blocking:[{id,title}], warning:[...]}`. Dipakai [[Microservices - Attendance Service]] saat clock-in |
| GET | `/internal/kaizen/metrics` | Hitungan ide per orang pada satu periode: `{data{<employee_id>:{submitted,accepted,implemented}}, period_key, has_program}`. `?period=YYYY-MM` (default periode berjalan). Ditarik [[Microservices - Employee Service]] untuk skor KPI |

> **Tiga angka, bukan satu.** Kepatuhan dihitung dari ide yang **diajukan** (karyawan memegang kendali penuh atas kepatuhannya sendiri), skor KPI dari ide yang **diterapkan** — begitulah redaksi metriknya di [[HRIS - Matriks KPI per Departemen]]. `has_program:false` membedakan "perusahaan ini belum menjalankan programnya" dari "gagal mengambil data"; hanya yang kedua layak dilaporkan sebagai metrik gagal hitung.

> **Identitas terkunci ke header.** Query `?employee_id=&department=&company_id=` HANYA dihormati bila request tak membawa `BIP-Employee-ID` sama sekali (ciri panggilan service-to-service). Request pemakai lewat gateway selalu terkunci ke dirinya sendiri — tanpa aturan ini rute ini jadi jalan mengintip form tertunda orang lain lintas perusahaan. Lihat [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].

## Bentuk data penting

**Tipe field** (`fields[].type`): `short_text` · `long_text` · `number` · `date` (`YYYY-MM-DD`) · `time` (`HH:MM`) · `dropdown` · `radio` · `checkbox` (jawaban berupa array) · `scale` (rentang maks 10 langkah) · **`section`**.

**`section` bukan pertanyaan** melainkan penanda awal bagian, hidup di dalam `fields` yang tetap datar. `label` jadi judul bagian, `description` jadi keterangannya. Aturannya: tak boleh `required`, tak boleh membawa `options`/`min`/`max`/`max_length`/`scale_*`, dan **jawaban yang menunjuk key bagian ditolak** (`400`). Bagian tak muncul di `analytics.fields` maupun kolom CSV.

**Keterangan ujung skala** (`scale_min_label`, `scale_max_label`) — mis. `"Sangat tidak puas"` .. `"Sangat puas"`. Keduanya opsional dan satu ujung saja pun sah; maksimal **40 karakter**; hanya berlaku untuk tipe `scale` (menempel di tipe lain ditolak `400`). Murni keterangan tampilan: nilai jawaban tetap angka, dan mengirim teks labelnya sebagai jawaban tetap ditolak.

**Pemilik** (`owner_department`): nama departemen `master_department` (mis. `"General Affair"`), BUKAN key `system_roles`. Form lama yang masih menyimpan `owner_module` dipindah otomatis saat service boot (`it`→`Tech Development`, `ga`→`General Affair`).

**Sasaran** (`audience.type`): `all` · `departments` (+`departments[]`) · `employees` (+`employee_ids[]`). `estimated_size` diisi manual sebagai penyebut tingkat pengisian; bila 0, `response_rate` tidak dikirim. Perhatikan `audience.departments` menjawab **siapa yang mengisi**, sedangkan `owner_department` menjawab **siapa yang memiliki** — keduanya tak harus sama.

**Tipe form** (`form_type`): `survey` · `evaluation` · `request` · `checklist` · `kaizen`. Kiriman kosong jadi `survey`; nilai tak dikenal ditolak `400` (bukan diam-diam diubah). **Terikat dua arah dengan `subject`**: `evaluation` wajib punya sasaran, dan yang punya sasaran wajib `evaluation`.

**Pengaturan Kaizen** (`settings.kaizen`): `{quota_default, quota_by_department[{department,quota}], committee_employee_ids[], board_visible, board_hidden_fields[]}`. **Terikat dua arah dengan `form_type: "kaizen"`**: tipe itu wajib punya blok ini, dan blok ini hanya sah di tipe itu. Tipe `kaizen` juga wajib `recurrence.unit: "monthly"`, serta menolak `single_response: true` dan menolak `subject`.

`quota_default` dan tiap `quota` antara 0 dan 31; departemen ganda ditolak `400`; `board_hidden_fields` wajib menunjuk key yang benar-benar ada. Kuota adalah **lantai**, bukan langit-langit: ide melebihi kuota tetap diterima, dan entri berkuota `0` berarti dikecualikan tapi tetap boleh mengirim. Menerbitkan form kaizen kedua saat masih ada yang `published` di perusahaan yang sama ditolak `409`.

> ⚠️ **`settings.kaizen` yang ABSEN pada `PATCH` berarti "jangan diubah"**, bukan "hapus". Tanpa aturan ini satu kiriman tanpa blok itu akan mengubah program Kaizen yang masih draft jadi survei biasa dan membuang kuota berikut daftar komite, tanpa galat. Konsekuensinya **tipe kaizen tidak bisa diubah ke tipe lain lewat `PATCH`** — hentikan programnya dengan menutup form.

**Potret peserta** (`participants`, `participants_at`, `participants_partial` pada dokumen periode): daftar orang yang wajib mengisi periode itu berikut kuota masing-masing, diambil cron **tiap periode**. Dipakai sebagai penyebut papan kepatuhan, menggantikan `audience.estimated_size` yang diisi manual. Gagal memotret tidak menggagalkan periode; yang ditahan hanya persentase di papan.

**Sasaran PENILAIAN** (`subject`): `{rules[], departments[], positions[], employee_ids[], allow_self, anonymous, resolved[]}`. `rules` digabung **OR**, isinya `departments`/`positions`/`employees`, dan tiap aturan wajib membawa daftarnya sendiri. `resolved` adalah **potret** yang diisi backend saat terbit — kiriman klien diabaikan. `anonymous` mengosongkan identitas penilai di export dan daftar jawaban, tapi TIDAK di database.

> **`subject` menjawab siapa yang DINILAI**, `audience` menjawab siapa yang MENGISI. Skenario "semua karyawan menilai tiap Office Boy" = `audience.type: all` + `subject.rules: ["positions"]`, `positions: ["Office Boy"]`. **Gerbang presensi ditolak `400`** pada form bersasaran penilaian.

**Form berulang** (`recurrence`): `{enabled, unit: "monthly"|"weekly", open_day}`. ⚠️ **Baru benar-benar bisa dikirim sejak PR #1019 (2026-08-06)**; sebelum itu `formRequest` tak punya fieldnya sehingga form berulang mustahil dibuat lewat API. Pada `PATCH`, **absen berarti jangan diubah** — kirim `{"enabled": false, ...}` eksplisit untuk mematikannya. Nil atau `enabled:false` berarti form sekali jalan, dan perilakunya persis seperti sebelum fitur ini ada. `open_day` 1..28 untuk bulanan (dibatasi 28 karena Februari), 1..7 untuk mingguan mengikuti hari ISO Senin sampai Minggu. Nilai di luar rentang atau `unit` tak dikenal ditolak `400`.

Jendela periode **selalu berakhir di ujung bulan atau minggu**, bukan sekian hari setelah buka, supaya dua periode tak pernah hidup bersamaan. Penandanya (`period_key`) `2026-08` untuk bulanan dan `2026-W32` untuk mingguan (penomoran **ISO**, supaya minggu yang melintasi pergantian tahun tak melahirkan dua penanda). Periode dibuka otomatis oleh cron **tiap jam** (`Asia/Jakarta`), hanya untuk form `published`.

**`period_key` pada jawaban** (`FormResponse.period_key`): kosong untuk form biasa **dan** untuk seluruh jawaban yang tersimpan sebelum fitur ini. Klien tidak mengirimnya; backend menurunkannya dari aturan pengulangan dan waktu kirim. Kunci keunikan pengisian ikut bergeser jadi (form, pengisi, yang dinilai, periode), sehingga form bulanan bisa diisi ulang tiap putaran.

**Gerbang presensi** (`attendance_gate`): `{enabled, mode: "warn"|"block", start_date, end_date}`. Tanggal wajib **RFC3339** (`2026-08-01T00:00:00Z`); `"2026-08-01"` akan ditolak. **Pada form berulang, `start_date`/`end_date` diabaikan** dan yang dipakai adalah jendela periode berjalan: tanggal statis akan lewat setelah bulan pertama dan gerbangnya tak pernah menyala lagi, padahal formnya terbit ulang tiap bulan.

**Respons analytics**: `total_responses`, `unique_respondents`, `audience_size`, `sample_size`, `truncated`, `response_rate` (opsional), `daily[{date,count}]`, `fields[{key,label,type,answered,skipped,options[{option,count}],average,min,max,sample_text[]}]`. Saat `truncated=true`, `response_rate` sengaja tidak dikirim karena tak bisa dihitung jujur dari sebagian data.

**Respons analytics form penilaian** (absen pada form biasa): `evaluation{subject_count, evaluators_started, evaluators_completed, pairs_done}`, `subjects[{employee_id,name,department,position,responses,scores[{key,label,answered,average}]}]`, `subjects_truncated`. `scores` hanya untuk pertanyaan `number`/`scale`, dan `average` **absen** (bukan 0) bila belum ada yang menilai. `response_rate` di sini = `evaluators_completed / audience_size` — yang dihitung penilai yang menyelesaikan SELURUH daftarnya, bukan yang sekadar mengirim satu penilaian.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] · [[IT - Form Builder]]
- [[API - Index]] · [[API - Attendance Service]] · [[CORE - API Master Gateway]]
