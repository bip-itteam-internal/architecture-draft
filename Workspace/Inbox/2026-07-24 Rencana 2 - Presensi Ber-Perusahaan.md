# Rencana 2 - Presensi Ber-Perusahaan (Attendance Service + Notification)

> **Untuk pekerja agentic:** SUB-SKILL WAJIB: superpowers:subagent-driven-development atau superpowers:executing-plans. Langkah pakai checkbox (`- [ ]`).

**Goal:** Menyaring seluruh data & alur presensi per-perusahaan (`company_id`) di attendance-service + notification, sehingga perusahaan pilot terisolasi dari BIP.

**Prasyarat:** **Rencana 1 sudah selesai & ter-deploy** (ada `common.CompanyID(c)`, `common.DefaultCompanyID="BIP"`, header `BIP-Company-ID`, `WorkData.company_id`, login menstempel perusahaan).

**Architecture:** Setiap query presensi ditambah filter `company_id` yang bersumber dari `common.CompanyID(c)`; setiap penulisan di-cap `company_id`; data lama BIP di-backfill. Pembangun filter diekstrak jadi fungsi murni agar bisa TDD (gaya test attendance = pure/table-driven, tanpa DB/Fiber).

**Tech Stack:** Go, Fiber v2, MongoDB. Test: `package main`, table-driven, tanpa DB (lihat `services/attendance/correction_test.go`).

## Global Constraints
- **BIP tak boleh berubah.** Data/token tanpa `company_id` -> `"BIP"` (via `common.CompanyID`).
- **Aditif saja**: tambah filter/field; tak ada filter lama yang dihapus (agent konfirmasi belum ada `company_id` di attendance -> semua penambahan).
- **Test = pure helper** (ekstrak pembangun `bson.M` jadi fungsi murni lalu assert). TIDAK ada preseden test integrasi Fiber di service ini.
- **Git**: commit sering, `feat:`/`test:`, tanpa `Co-Authored-By`; branch `feat/attendance-tenant`. Git via PowerShell `-c core.fsmonitor=false`.
- Semua backfill migrasi idempoten (`$exists:false` guard), dipanggil sekali saat boot; verifikasi di **dev** dulu.

---

### Task 1: Tambah field `company_id` ke struct/koleksi presensi

**Files:** Modify `bip-erp/shared-library/models/attendance/models.go`; Modify `bip-erp/shared-library/models/employee/models.go:209` (`WorkSchedule`).

**Interfaces (Produces):** field `CompanyID string bson:"company_id" json:"company_id"` di: `AttendanceEntries`(:543), `DailyLeaveRequest`(:750, koleksi `leave_request`), `AttendanceCorrectionRequest`(:960), `BusinessTripRequest`(:714), `ScheduleExchangeRequest`(:816), `Guestbook`(:632), `CompanyWorkSchedule`(:595), `CompanyHoliday`(:617), `CompanyWifi`(:625), dan `employee.WorkSchedule`(:209).

- [ ] **Step 1:** Tambah baris `CompanyID string bson:"company_id" json:"company_id"` (untuk Guestbook pakai `bson:"company_id,omitempty"` selaras field lainnya) tepat setelah `EmployeeID`/`_id` pada setiap struct di atas.
- [ ] **Step 2:** Build: `cd bip-erp/shared-library; go build ./...` -> sukses.
- [ ] **Step 3:** Commit: `git commit -am "feat(models): field company_id di koleksi presensi + WorkSchedule"`.

*(Tanpa unit test - hanya penambahan field; diverifikasi via build + task berikutnya.)*

---

### Task 2: `work_schedule` sync membawa perusahaan (hulu)

`work_schedule` men-drive `/report` & cron; sumbernya `WorkData` -> endpoint `/sync/work-schedules`. Karena `SyncCollection` mem-WIPE lalu re-insert (`shared-library/database/mongodb/mongo.go:125-131`), cukup benahi HULU; tak perlu migrasi koleksi tujuan.

**Files:** Modify `bip-erp/services/employee/` (handler `/sync/work-schedules` + factory pembangun `WorkSchedule` dari `WorkData`); Test `bip-erp/services/employee/company_test.go` (tambahan).

**Interfaces:** Produces `WorkSchedule.CompanyID` terisi dari `WorkData.CompanyID` (fallback BIP via `resolveCompanyID` dari Rencana 1).

- [ ] **Step 1 (test gagal):** Uji fungsi pembangun schedule dari workdata mengisi company:
```go
func TestWorkScheduleCompanyFromWorkData(t *testing.T) {
	ws := buildWorkSchedule(employee.WorkData{EmployeeID: "PGL-1", CompanyID: "PGL"}) // sesuaikan nama factory nyata
	if ws.CompanyID != "PGL" {
		t.Fatalf("company_id schedule = %q, want PGL", ws.CompanyID)
	}
}
```
- [ ] **Step 2:** Jalankan -> FAIL (`buildWorkSchedule`/field belum ada). *(Bila pembentukan WorkSchedule saat ini inline, ekstrak jadi fungsi `buildWorkSchedule(WorkData) employee.WorkSchedule` lebih dulu agar bisa diuji.)*
- [ ] **Step 3:** Di pembentukan `WorkSchedule` (dan endpoint `/sync/work-schedules`), set `CompanyID: resolveCompanyID(workData)`.
- [ ] **Step 4:** Jalankan test -> PASS; `go build ./...`.
- [ ] **Step 5:** Commit `feat(employee): work_schedule bawa company_id dari work_data`.

---

### Task 3: Migrasi backfill data presensi lama = BIP

Meniru `migrateWorkDataCompany` (Rencana 1). Untuk koleksi yang TIDAK di-sync-wipe (entries, requests, guestbook, company_*).

**Files:** Create `bip-erp/services/attendance/company_migrate.go`; panggil dari boot (`services/attendance/main.go` dekat `setup`/awal `main`).

**Interfaces:** Produces `func migrateAttendanceCompany()`.

- [ ] **Step 1:** Tulis fungsi:
```go
func migrateAttendanceCompany() {
	cols := []attendance.Collection{
		attendance.Collections.AttendanceEntries, attendance.Collections.LeaveRequest,
		attendance.Collections.CorrectionRequest, attendance.Collections.BusinessTripRequest,
		attendance.Collections.ScheduleExchangeRequest, attendance.Collections.Guestbook,
		attendance.Collections.CompanyWorkSchedule, attendance.Collections.CompanyHoliday,
		attendance.Collections.CompanyWifi,
	}
	for _, name := range cols {
		res, err := mongodb.GetCollection(name).UpdateMany(context.Background(),
			bson.M{"company_id": bson.M{"$exists": false}},
			bson.M{"$set": bson.M{"company_id": common.DefaultCompanyID}})
		if err != nil { log.Printf("[Migrate] %s.company_id: %v", name, err); continue }
		if res.ModifiedCount > 0 { log.Printf("[Migrate] %s.company_id=BIP: %d", name, res.ModifiedCount) }
	}
}
```
- [ ] **Step 2:** Panggil `migrateAttendanceCompany()` saat boot (sekali). `work_schedule` TIDAK di sini (di-refresh via sync Task 2).
- [ ] **Step 3:** Build; verifikasi **dev**: tiap koleksi `countDocuments({company_id:{$exists:false}})` = 0.
- [ ] **Step 4:** Commit `feat(attendance): migrasi backfill company_id=BIP data lama`.

---

### Task 4: Primitif penyaring & stempel di service

**Files:** Create `bip-erp/services/attendance/company.go`; Test `bip-erp/services/attendance/company_test.go`.

**Interfaces:** Produces `func companyFilter(base bson.M, company string) bson.M` (mengembalikan salinan base + `"company_id": company`); `func withCompany(doc bson.M, company string) bson.M` (untuk `$set`/insert map). Keduanya pure -> gampang TDD.

- [ ] **Step 1 (test gagal):**
```go
func TestCompanyFilter(t *testing.T) {
	got := companyFilter(bson.M{"employee_id": "X"}, "PGL")
	if got["company_id"] != "PGL" || got["employee_id"] != "X" {
		t.Fatalf("companyFilter salah: %v", got)
	}
	// base tak termutasi
	base := bson.M{"a": 1}
	_ = companyFilter(base, "PGL")
	if _, ok := base["company_id"]; ok {
		t.Fatal("companyFilter tidak boleh memutasi base")
	}
}
```
- [ ] **Step 2:** Jalankan -> FAIL.
- [ ] **Step 3:** Implementasi (salin map, jangan mutasi argumen):
```go
func companyFilter(base bson.M, company string) bson.M {
	out := bson.M{"company_id": company}
	for k, v := range base { out[k] = v }
	return out
}
func withCompany(doc bson.M, company string) bson.M { return companyFilter(doc, company) }
```
- [ ] **Step 4:** Test PASS; build.
- [ ] **Step 5:** Commit `feat(attendance): helper companyFilter/withCompany (pure)`.

---

### Task 5: Cap `company_id` pada semua penulisan presensi

Setiap insert distempel `common.CompanyID(c)`.

**Files (Modify):** `main.go` (`/tap` insert entry `:898`+ jalur create, guestbook), `self_requests.go` (create leave/exchange), `correction.go` (`handleCreateCorrection` `:294`), `business_trip.go` (`handleCreateBusinessTrip` `:209`).

- [ ] **Step 1:** Di tiap titik create, ambil `company := common.CompanyID(c)` lalu set field `CompanyID: company` pada struct (atau `withCompany(doc, company)` bila map) sebelum `InsertOne`.
- [ ] **Step 2:** Build.
- [ ] **Step 3:** Verifikasi dev: buat 1 pengajuan sebagai user perusahaan pilot -> dokumen tersimpan dengan `company_id` benar.
- [ ] **Step 4:** Commit `feat(attendance): stempel company_id pada create presensi/pengajuan`.

---

### Task 6: Saring `/entries`, `/today`, `/mood`

**Files (Modify):** `main.go:976` (`filter := bson.M{}` -> mulai dgn company), `:1008-1039` (teruskan company ke employee `/list`), `:1285`/`:1438` (pola sama).

- [ ] **Step 1:** Awali filter: `filter := bson.M{"company_id": common.CompanyID(c)}` (ganti `bson.M{}`).
- [ ] **Step 2:** Saat memanggil employee `/list?type=employee&department=...`, tambahkan `&company_id=` + `common.CompanyID(c)` agar employee-service hanya balas karyawan perusahaan itu (butuh dukungan param di employee `/list` - lihat Task 6b). Ini mencegah `employee_id $in` bocor lintas perusahaan.
- [ ] **Step 3:** Samakan untuk `/today` (`:1313 $match`) & `/mood`.
- [ ] **Step 4:** Build; dev: `/entries` sebagai HR perusahaan pilot hanya menampilkan karyawan perusahaan itu.
- [ ] **Step 5:** Commit `feat(attendance): scope /entries,/today,/mood per company`.

**Task 6b (employee-service `/list` terima `company_id`):** Modify employee-service handler `/list` -> bila query `company_id` ada, tambahkan ke filter Mongo `work_data`. Uji pembangun filter list secara pure bila memungkinkan. Commit terpisah `feat(employee): /list saring company_id`.

---

### Task 7: Saring `/report`

**Files (Modify):** `main.go:640-641` (`Find(ctx, bson.M{})` -> per company), `:620-622` (entries date filter + company), `:345` (`/sync/company-work-schedules` bila kembalikan semua).

- [ ] **Step 1:** `curSchedule, err := collSchedule.Find(ctx, bson.M{"company_id": common.CompanyID(c)})`.
- [ ] **Step 2:** Entries: `companyFilter(bson.M{"date": bson.M{"$gte":start,"$lt":end}}, common.CompanyID(c))`.
- [ ] **Step 3:** Build; dev: laporan perusahaan pilot hanya karyawannya; laporan BIP tetap sama.
- [ ] **Step 4:** Commit `feat(attendance): scope /report per company`.

---

### Task 8: Saring HR admin (titik isolasi utama)

`hrQueryOverlay`/`hrBaseFilter` (`hr_admin.go:309,343`) merembes ke semua daftar HR (leave/correction/trip/exchange). `department` di sini dari **query string**, jadi company WAJIB dari token.

**Files (Modify):** `hr_admin.go:309-345`; Test `hr_admin_test.go` (baru, pure).

**Interfaces:** `hrBaseFilter` mengembalikan `bson.M` yang selalu berisi `company_id = common.CompanyID(c)`.

- [ ] **Step 1 (test gagal):** ekstrak inti jadi pure `hrCompanyBase(company string) bson.M` lalu:
```go
func TestHRCompanyBase(t *testing.T) {
	f := hrCompanyBase("PGL")
	if f["company_id"] != "PGL" { t.Fatalf("hrBase tak scope company: %v", f) }
}
```
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Tambah `company_id` di `hrBaseFilter`/`hrQueryOverlay` via `common.CompanyID(c)` (admin pusat: lihat Task 10 Rencana 3 utk override).
- [ ] **Step 4:** PASS; build; dev: HR perusahaan pilot TIDAK melihat pengajuan BIP dan sebaliknya.
- [ ] **Step 5:** Commit `feat(attendance): HR list scope company (isolasi)`.

---

### Task 9: Saring filter review (correction & business trip)

**Files (Modify):** `correction.go:480` (`buildCorrectionReviewFilter`), `business_trip.go` (`buildReviewFilter`), `self_requests.go:135` (exchange `$or`). Test: tambah kasus di `correction_test.go` (pola pure sudah ada).

- [ ] **Step 1 (test gagal):** tambah parameter `company string` ke `buildCorrectionReviewFilter` dan assert hasil `bson.M` mengandung `company_id`:
```go
func TestCorrectionReviewFilterCompany(t *testing.T) {
	f := buildCorrectionReviewFilter("E1", "IT", "Staff", false, "PGL")
	if f["company_id"] != "PGL" { t.Fatalf("review filter tak scope company: %v", f) }
}
```
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Tambah `company_id` di pembangun filter; pemanggil kirim `common.CompanyID(c)`.
- [ ] **Step 4:** PASS; build.
- [ ] **Step 5:** Commit `feat(attendance): review filter (koreksi/dinas/tukar) scope company`.

---

### Task 10: Saring cron sweeper (per perusahaan)

`preAllocEntries` iterasi seluruh `work_schedule` (`cron.go:212`) & `cronAutoIgnoreStaleRequest` (`cron.go:513`) jalan lintas-perusahaan.

**Files (Modify):** `cron.go` (`preAllocEntries`, `cronAutoIgnoreStaleRequest`, `cronSyncCollectionWorkSchedule`).

- [ ] **Step 1:** Cron ambil daftar perusahaan aktif (dari `master_company` via employee-service internal, atau `distinct company_id` di `work_schedule`), lalu **loop per company**: `work_schedule` Find `{company_id: comp}`; `leaveFilter`/`spvFilter` tambah `"company_id": comp`. `company_work_schedule`/holiday juga per company.
- [ ] **Step 2:** Build; dev: pre-alloc & auto-ignore berjalan benar untuk >1 perusahaan tanpa saling menyentuh.
- [ ] **Step 3:** Commit `feat(attendance): cron pre-alloc & sweeper per company`.

---

### Task 11: Fingerprint & WiFi per-perusahaan (defensif)

Perusahaan baru MyBharata (mobile) -> tak pakai mesin; ini pengamanan agar `fingerprint_id`/wifi tak tabrakan lintas perusahaan.

**Files (Modify):** `main.go:898` (lookup fingerprint), `:939-941` (validasi wifi), `:3679/:3707/:3745` (CRUD `company_wifi`), `setup.go:701-757` (seed wifi per company).

- [ ] **Step 1:** Lookup fingerprint tambah `company_id` (mesin dipetakan ke company; BIP = mesin sekarang). Validasi wifi + CRUD `company_wifi` di-scope `common.CompanyID(c)`; seed wifi per company (BIP set sekarang).
- [ ] **Step 2:** Build; dev BIP tetap bisa tap fingerprint seperti biasa.
- [ ] **Step 3:** Commit `feat(attendance): namespace fingerprint & wifi per company`.

---

### Task 12: Notification tidak bocor lintas-perusahaan

Bocor terparah: `sendBroadcastFCM` (tanpa filter), `sendDepartmentFCM` (nama dept bisa sama antar company).

**Files (Modify):** employee-service `/list?type=fcm-token` (terima `company_id`, saring); `services/notification/main.go:955` (`sendPersonalFCM`), `:1021` (`sendDepartmentFCM`), `:1073` (`sendBroadcastFCM`) -> tambah `&company_id=` + `common.CompanyID(c)`.

- [ ] **Step 1:** employee-service: `/list?type=fcm-token` saring `company_id` bila diberikan (uji pure pembangun filter bila memungkinkan).
- [ ] **Step 2:** Ketiga fungsi notif teruskan `common.CompanyID(c)` ke URL.
- [ ] **Step 3:** Build; dev: broadcast/departemen hanya sampai ke perusahaan pengirim.
- [ ] **Step 4:** Commit `feat(notification): saring penerima FCM per company`.

---

### Task 13: Gerbang isolasi & regresi

- [ ] **Step 1:** Build + `go test ./...` di `shared-library`, `services/attendance`, `services/employee`, `services/notification` -> semua PASS.
- [ ] **Step 2 (dev, isolasi):** buat perusahaan pilot + 1 karyawan; karyawan itu absen/izin. Verifikasi: HR pilot melihat datanya; HR BIP TIDAK melihatnya; sebaliknya. Notifikasi tidak lintas.
- [ ] **Step 3 (dev, regresi BIP):** akun BIP absen/izin/laporan seperti biasa -> perilaku identik; migrasi log bersih.
- [ ] **Step 4:** Commit `test(attendance): dokumentasikan gerbang isolasi & regresi` (bila ada test tambahan).

---

## Self-review
- **Cakupan spec Bagian 2 (penyaringan):** entries/today/mood (T6), report (T7), HR admin (T8), review filter (T9), cron (T10), notifikasi (T12), fingerprint/wifi (T11), backfill (T3), field+sync (T1/T2). Semua situs dari penelusuran tercakup.
- **Placeholder:** tak ada; tiap task punya file:line + kode representatif + cara uji.
- **Konsistensi:** `common.CompanyID(c)` (Rencana 1) sumber tunggal; `companyFilter`/`withCompany` konsisten; `company_id` string konsisten. Gaya test = pure/table-driven sesuai `correction_test.go`.
- **Catatan penting:** struct koleksi `leave_request` bernama `DailyLeaveRequest` (bukan `LeaveRequest`) - jangan keliru saat menambah field (Task 1).
