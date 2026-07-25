# Rencana 1 - Fondasi Tenant Presensi Multi-Perusahaan (Backend Inti)

> **Untuk pekerja agentic:** SUB-SKILL WAJIB: gunakan superpowers:subagent-driven-development (disarankan) atau superpowers:executing-plans untuk mengeksekusi task-per-task. Langkah pakai checkbox (`- [ ]`).

**Goal:** Membuat backend bip-erp sadar-perusahaan (`company_id`) sebagai fondasi multi-tenant, TANPA mengubah perilaku BIP yang sudah berjalan.

**Architecture:** Row-level tenancy di satu database. Setiap identitas membawa `company_id` lewat JWT -> header `BIP-Company-ID` -> helper penyaring bersama `common.CompanyID(c)` (default fallback `"BIP"`). Data lama BIP di-backfill sekali. Perubahan bersifat ADITIF; token/data tanpa `company_id` otomatis jatuh ke `"BIP"` sehingga BIP identik seperti sekarang.

**Tech Stack:** Go 1.x, Fiber v2, MongoDB (mongo-driver), golang-jwt (HS256). Test: table-driven / `fiber app.Test` (tanpa DB), `package main`/`package common`.

## Global Constraints
- **BIP TIDAK BOLEH berubah perilaku.** `company_id` default = `"BIP"`. Token/data lama tanpa klaim/field company harus jatuh ke `"BIP"`.
- **Aditif saja.** Tambah field/header/claim/collection baru; jangan hapus/ubah makna yang lama.
- **Pola test kode ini:** fungsi PURE atau lewat `fiber app.Test` dengan header `BIP-*`; TANPA MongoDB. Fungsi yang menyentuh DB TIDAK di-unit-test (ikuti kebiasaan repo) - diverifikasi via `go build` + smoke test dev.
- **Git:** commit sering; pesan `feat:`/`test:`/`chore:`; **tanpa** trailer `Co-Authored-By`. Branch per service dari `main` (mis. `feat/tenant-foundation`). Ingat gotcha Windows: jalankan git via PowerShell `-c core.fsmonitor=false`.
- Konstanta pusat: `DefaultCompanyID = "BIP"` (dideklarasikan sekali di Task 1, dipakai semua task).

---

### Task 1: Primitif penyaring perusahaan (`common.CompanyID`) + konstanta & header

Meniru pola `common.SupervisedDepartments(c)` di `shared-library/common/department_scope.go:29-55`.

**Files:**
- Modify: `bip-erp/shared-library/common/header.go` (tambah `Header.CompanyID`, `Local.CompanyID`)
- Create: `bip-erp/shared-library/common/company_scope.go`
- Test: `bip-erp/shared-library/company_scope_test.go` (package `shared_library` seperti `department_scope_test.go` root)

**Interfaces:**
- Produces: `const common.DefaultCompanyID = "BIP"`; `common.Header.CompanyID = "BIP-Company-ID"`; `common.Local.CompanyID = "company_id"`; `func common.CompanyID(c *fiber.Ctx) string` (kembalikan header `BIP-Company-ID`, atau `DefaultCompanyID` bila kosong).

- [ ] **Step 1: Tulis test gagal** (`bip-erp/shared-library/company_scope_test.go`)

Meniru gaya request-level `bip-erp/shared-library/department_scope_test.go` (helper bikin `fiber.New()`, set header, `app.Test`).

```go
package shared_library

import (
	"net/http/httptest"
	"testing"

	common "github.com/bharata/shared-library/common"
	"github.com/gofiber/fiber/v2"
)

// companyOf menjalankan common.CompanyID(c) di dalam request fiber nyata dengan
// header BIP-Company-ID yang diberikan (kosong = tak diset).
func companyOf(t *testing.T, header string) string {
	t.Helper()
	app := fiber.New()
	var got string
	app.Get("/x", func(c *fiber.Ctx) error {
		got = common.CompanyID(c)
		return c.SendStatus(200)
	})
	req := httptest.NewRequest("GET", "/x", nil)
	if header != "" {
		req.Header.Set(common.Header.CompanyID, header)
	}
	if _, err := app.Test(req); err != nil {
		t.Fatalf("app.Test: %v", err)
	}
	return got
}

func TestCompanyIDFallback(t *testing.T) {
	cases := []struct {
		name, header, want string
	}{
		{"header ada", "PGL", "PGL"},
		{"header kosong -> default BIP", "", common.DefaultCompanyID},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if got := companyOf(t, tc.header); got != tc.want {
				t.Fatalf("CompanyID = %q, want %q", got, tc.want)
			}
		})
	}
}
```

- [ ] **Step 2: Jalankan test, pastikan GAGAL kompilasi**

Run (PowerShell): `cd bip-erp/shared-library; go test ./... -run TestCompanyIDFallback`
Expected: FAIL - `undefined: common.CompanyID` / `common.Header.CompanyID` / `common.DefaultCompanyID`.

- [ ] **Step 3: Tambah konstanta header & local** (`bip-erp/shared-library/common/header.go`)

Di dalam `var Header = struct{...}{...}` (`header.go:5-25`) tambah baris (setelah `SupervisedDepartments`):
```go
	CompanyID: "BIP-Company-ID",
```
dan pada definisi struct-nya tambah field `CompanyID string`. Di dalam `var Local = struct{...}{...}` (`header.go:27-43`) tambah field + nilai:
```go
	CompanyID: "company_id",
```

- [ ] **Step 4: Buat helper** (`bip-erp/shared-library/common/company_scope.go`)

```go
package common

import "github.com/gofiber/fiber/v2"

// DefaultCompanyID = tenant default (BIP). Dipakai sebagai fallback agar token/data
// lama tanpa klaim perusahaan tetap berperilaku seperti sistem single-company semula.
const DefaultCompanyID = "BIP"

// CompanyID mengembalikan perusahaan (tenant) pemilik request dari header BIP-Company-ID.
// Kosong (token/data lama) -> DefaultCompanyID. Ini SATU-SATUNYA sumber kebenaran
// penyaringan perusahaan untuk internal service; jangan baca header mentah di tempat lain.
func CompanyID(c *fiber.Ctx) string {
	if v := c.Get(Header.CompanyID); v != "" {
		return v
	}
	return DefaultCompanyID
}
```

- [ ] **Step 5: Jalankan test, pastikan LULUS**

Run: `cd bip-erp/shared-library; go test ./... -run TestCompanyIDFallback -v`
Expected: PASS (2 subtest).

- [ ] **Step 6: Commit**

```
git add shared-library/common/header.go shared-library/common/company_scope.go shared-library/company_scope_test.go
git commit -m "feat(common): CompanyID scope helper + BIP-Company-ID header (fallback BIP)"
```

---

### Task 2: JWT membawa `company_id`

Meniru `bip-erp/shared-library/jwt_roundtrip_test.go` dan pola `supervised_departments` di `auth/jwt.go`.

**Files:**
- Modify: `bip-erp/shared-library/common/struct.go:165-178` (`PayloadJWT`)
- Modify: `bip-erp/shared-library/auth/jwt.go:40-61` (`SignJWT`) & `:63-111` (`ValidateJWT`)
- Test: `bip-erp/shared-library/jwt_company_roundtrip_test.go`

**Interfaces:**
- Consumes: `common.Local.CompanyID`, `common.DefaultCompanyID` (Task 1).
- Produces: `PayloadJWT.CompanyID string`; klaim JWT `company_id`; `c.Locals(common.Local.CompanyID)` terisi setelah `ValidateJWT`.

- [ ] **Step 1: Tulis test gagal** (`bip-erp/shared-library/jwt_company_roundtrip_test.go`)

```go
package shared_library

import (
	"testing"

	"github.com/bharata/shared-library/auth"
	common "github.com/bharata/shared-library/common"
	"github.com/gofiber/fiber/v2"
	"net/http/httptest"
)

func TestJWTMembawaCompanyID(t *testing.T) {
	t.Setenv("JWT_SECRET", "test-secret-123")
	tok, err := auth.GenerateJWT(common.PayloadJWT{
		EmployeeID: "PGL-0001", Username: "pgluser", CompanyID: "PGL",
	})
	if err != nil {
		t.Fatalf("GenerateJWT: %v", err)
	}
	app := fiber.New()
	var got string
	app.Get("/x", auth.ValidateJWT(), func(c *fiber.Ctx) error {
		if v := c.Locals(common.Local.CompanyID); v != nil {
			got = v.(string)
		}
		return c.SendStatus(200)
	})
	req := httptest.NewRequest("GET", "/x", nil)
	req.Header.Set("Authorization", "Bearer "+tok)
	if _, err := app.Test(req); err != nil {
		t.Fatalf("app.Test: %v", err)
	}
	if got != "PGL" {
		t.Fatalf("Locals company_id = %q, want PGL", got)
	}
}
```

- [ ] **Step 2: Jalankan test, pastikan GAGAL**

Run: `cd bip-erp/shared-library; go test ./... -run TestJWTMembawaCompanyID`
Expected: FAIL - `unknown field CompanyID in struct literal` (PayloadJWT belum punya field).

- [ ] **Step 3: Tambah field ke `PayloadJWT`** (`struct.go`, setelah `Position`)

```go
	CompanyID string `bson:"company_id" json:"company_id,omitempty"`
```

- [ ] **Step 4: Set klaim di `SignJWT`** (`auth/jwt.go:45-54`, di dalam `jwt.MapClaims{...}`)

Tambah baris:
```go
		"company_id": func() string {
			if payload.CompanyID != "" {
				return payload.CompanyID
			}
			return common.DefaultCompanyID
		}(),
```
(Selalu tulis `company_id`; kosong -> `"BIP"`, supaya token BIP lama-gaya tetap konsisten.)

- [ ] **Step 5: Baca klaim di `ValidateJWT`** (`auth/jwt.go`, dekat `:97-105` bersama Locals lain)

```go
	if v, ok := claims["company_id"]; ok && v != nil {
		c.Locals(common.Local.CompanyID, fmt.Sprintf("%v", v))
	} else {
		c.Locals(common.Local.CompanyID, common.DefaultCompanyID)
	}
```

- [ ] **Step 6: Jalankan test, pastikan LULUS**

Run: `cd bip-erp/shared-library; go test ./... -run TestJWTMembawaCompanyID -v`
Expected: PASS. Jalankan juga test JWT lama: `go test ./... -run TestGenerateJWT` -> tetap PASS (regresi).

- [ ] **Step 7: Commit**

```
git add shared-library/common/struct.go shared-library/auth/jwt.go shared-library/jwt_company_roundtrip_test.go
git commit -m "feat(auth): JWT membawa company_id (default BIP)"
```

---

### Task 3: Gateway meneruskan header `BIP-Company-ID`

Meniru penanganan `SupervisedDepartments` di `shared-library/routes/gateway_request.go`.

**Files:**
- Modify: `bip-erp/shared-library/routes/gateway_request.go:56-99` (strip + set)
- Modify: `bip-erp/shared-library/routes/internal_request.go:56-57` (teruskan scope antar-service, bila ada)

**Interfaces:**
- Consumes: `common.Local.CompanyID`, `common.Header.CompanyID`, `common.DefaultCompanyID`.
- Produces: setiap request ter-`Reroute` membawa header `BIP-Company-ID`.

- [ ] **Step 1: Strip header company kiriman klien**

Di daftar penghapusan `BIP-*` (`gateway_request.go:56-67`, tempat `req.Header.Del(...)` untuk 8 header) tambah:
```go
	req.Header.Del(common.Header.CompanyID)
```

- [ ] **Step 2: Set dari Locals**

Dekat blok set header dari Locals (`:70-99`, contoh `req.Header.Set(common.Header.Department, department)`) tambah:
```go
	company := common.DefaultCompanyID
	if v := c.Locals(common.Local.CompanyID); v != nil {
		if s, ok := v.(string); ok && s != "" {
			company = s
		}
	}
	req.Header.Set(common.Header.CompanyID, company)
```

- [ ] **Step 3: Teruskan antar-service** (`internal_request.go`, dekat `:56-57`)

Bila `InternalRequest` meneruskan `BIP-Supervised-Departments`, tambahkan penerusan `common.Header.CompanyID` dengan pola yang sama (baca dari header sumber, set ke request tujuan). Jika sumbernya `c.Get`, gunakan `common.CompanyID(c)` agar default terjaga.

- [ ] **Step 4: Verifikasi build**

Run: `cd bip-erp/shared-library; go build ./...`
Expected: sukses tanpa error. (Reroute melakukan HTTP nyata -> tidak di-unit-test; ikuti kebiasaan repo, verifikasi via smoke dev di Task 8.)

- [ ] **Step 5: Commit**

```
git add shared-library/routes/gateway_request.go shared-library/routes/internal_request.go
git commit -m "feat(gateway): teruskan header BIP-Company-ID dari klaim JWT"
```

---

### Task 4: `WorkData.CompanyID` + login menstempel perusahaan

**Files:**
- Modify: `bip-erp/shared-library/models/employee/models.go:186-207` (`WorkData`)
- Create: `bip-erp/services/employee/company.go` (helper `resolveCompanyID`)
- Modify: `bip-erp/services/employee/main.go` login handlers (`:2623`, `:2681`, `:2723`, `:2755`)
- Test: `bip-erp/services/employee/company_test.go`

**Interfaces:**
- Consumes: `common.DefaultCompanyID`.
- Produces: `WorkData.CompanyID string`; `func resolveCompanyID(work employee.WorkData) string`; login mengembalikan `PayloadJWT.CompanyID` terisi.

- [ ] **Step 1: Tulis test gagal** (`bip-erp/services/employee/company_test.go`, `package main`)

Meniru gaya pure `services/employee/department_scope_test.go`.
```go
package main

import (
	"testing"

	common "github.com/bharata/shared-library/common"
	"github.com/bharata/shared-library/models/employee"
)

func TestResolveCompanyID(t *testing.T) {
	cases := []struct {
		name string
		work employee.WorkData
		want string
	}{
		{"punya company", employee.WorkData{CompanyID: "PGL"}, "PGL"},
		{"kosong -> default BIP", employee.WorkData{}, common.DefaultCompanyID},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			if got := resolveCompanyID(tc.work); got != tc.want {
				t.Fatalf("resolveCompanyID = %q, want %q", got, tc.want)
			}
		})
	}
}
```

- [ ] **Step 2: Jalankan test, pastikan GAGAL**

Run: `cd bip-erp/services/employee; go test ./... -run TestResolveCompanyID`
Expected: FAIL - `undefined: resolveCompanyID` dan `unknown field CompanyID`.

- [ ] **Step 3: Tambah field `CompanyID` ke `WorkData`** (`models.go`, setelah `Position`)

```go
	CompanyID string `bson:"company_id" json:"company_id"`
```

- [ ] **Step 4: Buat helper** (`bip-erp/services/employee/company.go`)

```go
package main

import (
	common "github.com/bharata/shared-library/common"
	"github.com/bharata/shared-library/models/employee"
)

// resolveCompanyID mengembalikan perusahaan pemilik akun; kosong (data lama BIP) -> BIP.
func resolveCompanyID(work employee.WorkData) string {
	if work.CompanyID != "" {
		return work.CompanyID
	}
	return common.DefaultCompanyID
}
```

- [ ] **Step 5: Isi `CompanyID` di payload login** (`main.go`)

Pada tiap `return c.JSON(common.PayloadJWT{...})` login (`:2623`, dan pengulangannya di `:2681`, `:2723`, `:2755`) tambah field:
```go
		CompanyID: resolveCompanyID(workData),
```

- [ ] **Step 6: Jalankan test + build**

Run: `cd bip-erp/services/employee; go test ./... -run TestResolveCompanyID -v && go build ./...`
Expected: PASS + build sukses.

- [ ] **Step 7: Commit**

```
git add shared-library/models/employee/models.go services/employee/company.go services/employee/company_test.go services/employee/main.go
git commit -m "feat(employee): WorkData.company_id + login menstempel perusahaan (fallback BIP)"
```

---

### Task 5: Migrasi backfill `company_id = BIP` untuk data lama

Meniru `migrateDepartmentSupervision` (`services/employee/master_data.go:30-72`) - idempoten, guard `$exists:false`, dipanggil sekali saat boot.

**Files:**
- Modify: `bip-erp/services/employee/company.go` (tambah `migrateWorkDataCompany`)
- Modify: `bip-erp/services/employee/master_data.go:16-21` (`seedMasterData` memanggil migrasi baru) ATAU `main.go:88` boot.

**Interfaces:**
- Consumes: `employee.Collections.WorkData`, `common.DefaultCompanyID`.
- Produces: `func migrateWorkDataCompany()`.

- [ ] **Step 1: Tulis fungsi migrasi** (`company.go`)

```go
import (
	"context"
	"log"

	"github.com/bharata/shared-library/database/mongodb"
	"go.mongodb.org/mongo-driver/bson"
)

// migrateWorkDataCompany men-cap company_id = BIP pada semua work_data yang BELUM
// punya field itu. Idempoten (guard $exists:false), aman dijalankan berulang saat boot.
func migrateWorkDataCompany() {
	coll := mongodb.GetCollection(employee.Collections.WorkData)
	res, err := coll.UpdateMany(context.Background(),
		bson.M{"company_id": bson.M{"$exists": false}},
		bson.M{"$set": bson.M{"company_id": common.DefaultCompanyID}},
	)
	if err != nil {
		log.Printf("[Migrate] work_data.company_id: %v", err)
		return
	}
	if res.ModifiedCount > 0 {
		log.Printf("[Migrate] work_data.company_id = %s untuk %d dok", common.DefaultCompanyID, res.ModifiedCount)
	}
}
```
(Sesuaikan import mongodb dengan yang dipakai `master_data.go`.)

- [ ] **Step 2: Panggil saat boot** (`master_data.go` `seedMasterData()` `:17-21`, atau `main.go:88` setelah `seedMasterData()`)

```go
	migrateWorkDataCompany()
```

- [ ] **Step 3: Verifikasi build**

Run: `cd bip-erp/services/employee; go build ./...`
Expected: sukses. (Migrasi menyentuh DB -> tak di-unit-test; verifikasi di dev, Step 4.)

- [ ] **Step 4: Verifikasi di DEV (bukan prod)**

Jalankan employee-service dev, cek log `[Migrate] work_data.company_id = BIP untuk N dok`. Via mongosh dev (lihat catatan akses Mongo dev): `db.work_data.countDocuments({company_id: {$exists:false}})` harus `0`; `db.work_data.countDocuments({company_id: "BIP"})` = jumlah karyawan BIP.

- [ ] **Step 5: Commit**

```
git add services/employee/company.go services/employee/master_data.go
git commit -m "feat(employee): migrasi backfill work_data.company_id = BIP (idempoten)"
```

---

### Task 6: Master `Company` (model, collection, seed, CRUD)

Meniru `MasterDepartment` (`shared-library/models/employee/master_data.go:25-39`) & CRUD `master.Get/Post /departments` (`services/employee/master_data.go:125,144`).

**Files:**
- Create: `bip-erp/shared-library/models/employee/master_company.go`
- Modify: `bip-erp/shared-library/models/employee/models.go:16-50` (tambah `Collections.MasterCompany = "master_company"`)
- Modify: `bip-erp/services/employee/master_data.go` (route `master.Get/Post /companies`, `seedMasterCompany`)
- Test: `bip-erp/shared-library/models/employee/master_company_test.go`

**Interfaces:**
- Produces: struct `employee.Company{CompanyID/Key, Name, Code, Active, Metadata}`; `employee.Collections.MasterCompany`; endpoint `GET/POST /master/companies`; `func validateCompany(Company) error`.

- [ ] **Step 1: Tulis test gagal** (`master_company_test.go`, `package employee`)

```go
package employee

import "testing"

func TestValidateCompany(t *testing.T) {
	if err := ValidateCompany(Company{Key: "PGL", Name: "CV Pure Glow Lux"}); err != nil {
		t.Fatalf("valid company ditolak: %v", err)
	}
	if err := ValidateCompany(Company{Key: "", Name: "X"}); err == nil {
		t.Fatal("key kosong harus ditolak")
	}
	if err := ValidateCompany(Company{Key: "PGL", Name: ""}); err == nil {
		t.Fatal("name kosong harus ditolak")
	}
}
```

- [ ] **Step 2: Jalankan test, pastikan GAGAL**

Run: `cd bip-erp/shared-library; go test ./models/employee/... -run TestValidateCompany`
Expected: FAIL - `undefined: Company` / `ValidateCompany`.

- [ ] **Step 3: Buat model + validasi** (`master_company.go`)

```go
package employee

import (
	"errors"
	"strings"

	common "github.com/bharata/shared-library/common"
)

// Company = tenant (perusahaan) pemilik data presensi. BERBEDA dari Company di payroll
// (yang untuk kop slip). Key dipakai sebagai company_id yang tersimpan di work_data & JWT.
type Company struct {
	Key     string          `bson:"key" json:"key"`   // = company_id, mis. "BIP", "PGL"
	Name    string          `bson:"name" json:"name"` // nama lengkap, mis. "PT Bharata Internasional"
	Code    string          `bson:"code" json:"code"` // prefix employee_id, mis. "BIP-"
	Active  bool            `bson:"active" json:"active"`
	Metadata common.Metadata `bson:"metadata" json:"metadata"`
}

// ValidateCompany diekspor agar bisa dipanggil dari employee-service (package main).
func ValidateCompany(c Company) error {
	if strings.TrimSpace(c.Key) == "" {
		return errors.New("key perusahaan wajib")
	}
	if strings.TrimSpace(c.Name) == "" {
		return errors.New("nama perusahaan wajib")
	}
	return nil
}
```

- [ ] **Step 4: Tambah collection** (`models.go` `Collections`)

```go
	MasterCompany Collection = "master_company"
```

- [ ] **Step 5: Jalankan test, pastikan LULUS**

Run: `cd bip-erp/shared-library; go test ./models/employee/... -run TestValidateCompany -v`
Expected: PASS.

- [ ] **Step 6: Route CRUD + seed** (`services/employee/master_data.go`, dalam `RegisterMasterDataRoutes`)

Interim RBAC pakai `common.RequireITSupervisor` (peran "admin pusat" resmi didefinisikan di rencana berikutnya). LIST + CREATE meniru `/departments`:
```go
master.Get("/companies", func(c *fiber.Ctx) error {
	var companies []employee.Company
	if err := mongodb.FindMany(employee.Collections.MasterCompany, bson.M{}, &companies); err != nil {
		return c.Status(500).JSON(fiber.Map{"error": err.Error()})
	}
	return c.JSON(fiber.Map{"data": companies, "count": len(companies)})
})

master.Post("/companies", common.RequireITSupervisor, func(c *fiber.Ctx) error {
	var comp employee.Company
	if err := c.BodyParser(&comp); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": "invalid body"})
	}
	if err := employee.ValidateCompany(comp); err != nil {
		return c.Status(400).JSON(fiber.Map{"error": err.Error()})
	}
	var existing employee.Company
	if err := mongodb.FindOne(employee.Collections.MasterCompany, bson.M{"key": comp.Key}, &existing); err == nil {
		return c.Status(409).JSON(fiber.Map{"error": "company key already exists"})
	}
	comp.Active = true
	comp.Metadata = common.UpsertMetadata(common.Metadata{}, c.Get(common.Header.EmployeeID))
	id, err := mongodb.InsertOne(employee.Collections.MasterCompany, comp)
	if err != nil {
		return c.Status(500).JSON(fiber.Map{"error": err.Error()})
	}
	return c.Status(201).JSON(fiber.Map{"message": "company created", "_id": id})
})
```
`seedMasterCompany()` (pola `seedMasterDepartments` `:74-95`, skip bila sudah ada):
```go
func seedMasterCompany() {
	n, _ := mongodb.Count(employee.Collections.MasterCompany, bson.M{"key": common.DefaultCompanyID})
	if n > 0 { return }
	_, _ = mongodb.InsertOne(employee.Collections.MasterCompany, employee.Company{
		Key: common.DefaultCompanyID, Name: "PT Bharata Internasional", Code: "BIP-", Active: true,
		Metadata: common.UpsertMetadata(common.Metadata{}, "system"),
	})
}
```
Panggil `seedMasterCompany()` di `seedMasterData()`.

- [ ] **Step 7: Build + verifikasi dev**

Run: `cd bip-erp/services/employee; go build ./...`
Verifikasi dev: `GET /master/companies` mengembalikan minimal 1 (BIP). `POST /master/companies {key:"PGL",name:"CV Pure Glow Lux",code:"PGL-"}` -> 201; ulang -> 409.

- [ ] **Step 8: Commit**

```
git add shared-library/models/employee/master_company.go shared-library/models/employee/models.go shared-library/models/employee/master_company_test.go services/employee/master_data.go
git commit -m "feat(employee): master Company (tenant) + seed BIP + CRUD /master/companies"
```

---

### Task 7: Create-employee menyetel `company_id`

**Files:**
- Modify: `bip-erp/services/employee/func.go:37-45` (insert work_data)
- Modify: `bip-erp/services/employee/company.go` (helper `defaultWorkCompany`)
- Modify: `bip-erp/services/employee/main.go:774-909` (CRUD `map[string]interface{}` untuk `/create|update/:id/work`)
- Modify (opsional): `bip-erp/orchestrator/hris/transactions.go:559-596` (teruskan `company_id` dari payload)
- Test: tambah ke `bip-erp/services/employee/company_test.go`

**Interfaces:**
- Consumes: `resolveCompanyID` (Task 4).
- Produces: `func defaultWorkCompany(work employee.WorkData) employee.WorkData` (mengisi `CompanyID` = BIP bila kosong).

- [ ] **Step 1: Tulis test gagal** (tambahan di `company_test.go`)

```go
func TestDefaultWorkCompany(t *testing.T) {
	got := defaultWorkCompany(employee.WorkData{Department: "X"})
	if got.CompanyID != common.DefaultCompanyID {
		t.Fatalf("company kosong harus jadi BIP, got %q", got.CompanyID)
	}
	got2 := defaultWorkCompany(employee.WorkData{CompanyID: "PGL"})
	if got2.CompanyID != "PGL" {
		t.Fatalf("company terisi harus dipertahankan, got %q", got2.CompanyID)
	}
}
```

- [ ] **Step 2: Jalankan test, pastikan GAGAL**

Run: `cd bip-erp/services/employee; go test ./... -run TestDefaultWorkCompany`
Expected: FAIL - `undefined: defaultWorkCompany`.

- [ ] **Step 3: Tulis helper** (`company.go`)

```go
func defaultWorkCompany(work employee.WorkData) employee.WorkData {
	if work.CompanyID == "" {
		work.CompanyID = common.DefaultCompanyID
	}
	return work
}
```

- [ ] **Step 4: Terapkan di jalur transaksi** (`func.go`, dekat `:40` sebelum `InsertOne`)

```go
	create.WorkData = defaultWorkCompany(create.WorkData)
```
(admin pusat mengirim `company_id` untuk perusahaan baru; bila kosong -> BIP, jadi alur BIP lama tak berubah.)

- [ ] **Step 5: Terapkan di jalur CRUD map** (`main.go:774-909`)

Pada handler `/create/:employee_id/work` (yang memakai `map[string]interface{}`), pastikan bila `company_id` tak ada di body, isi `"BIP"` sebelum `InsertOne`/`Update`. Contoh setelah parse map `body`:
```go
	if _, ok := body["company_id"]; !ok {
		body["company_id"] = common.DefaultCompanyID
	}
```

- [ ] **Step 6: Jalankan test + build**

Run: `cd bip-erp/services/employee; go test ./... -run TestDefaultWorkCompany -v && go build ./...`
Expected: PASS + build sukses.

- [ ] **Step 7: Commit**

```
git add services/employee/company.go services/employee/company_test.go services/employee/func.go services/employee/main.go
git commit -m "feat(employee): create/update work_data mengisi company_id (default BIP)"
```

---

### Task 8: Gerbang regresi - pastikan BIP tidak berubah

Bukan fitur baru; jaring pengaman sebelum menandai fondasi selesai.

**Files:**
- Test: `bip-erp/shared-library/jwt_company_roundtrip_test.go` (tambah kasus default)

**Interfaces:** tidak ada yang baru.

- [ ] **Step 1: Tambah test "token gaya lama tanpa company -> BIP"**

```go
func TestJWTTanpaCompanyDefaultBIP(t *testing.T) {
	t.Setenv("JWT_SECRET", "test-secret-123")
	tok, _ := auth.GenerateJWT(common.PayloadJWT{EmployeeID: "BIP-0001", Username: "bipuser"}) // tanpa CompanyID
	app := fiber.New()
	var got string
	app.Get("/x", auth.ValidateJWT(), func(c *fiber.Ctx) error {
		got, _ = c.Locals(common.Local.CompanyID).(string)
		return c.SendStatus(200)
	})
	req := httptest.NewRequest("GET", "/x", nil)
	req.Header.Set("Authorization", "Bearer "+tok)
	app.Test(req)
	if got != common.DefaultCompanyID {
		t.Fatalf("tanpa company harus BIP, got %q", got)
	}
}
```

- [ ] **Step 2: Jalankan test, pastikan LULUS**

Run: `cd bip-erp/shared-library; go test ./... -run TestJWTTanpaCompanyDefaultBIP -v`
Expected: PASS.

- [ ] **Step 3: Regresi menyeluruh (build + test semua modul yang disentuh)**

Run:
```
cd bip-erp/shared-library; go build ./...; go test ./...
cd bip-erp/services/employee; go build ./...; go test ./...
```
Expected: semua PASS/sukses.

- [ ] **Step 4: Smoke test dev (BIP tak berubah)**

Login akun BIP dev (mis. `panpan`) -> respons berisi token; decode -> klaim `company_id = "BIP"`. Panggil beberapa endpoint HRIS/presensi yang biasa dipakai BIP -> perilaku identik. Cek log migrasi (Task 5). Verifikasi tidak ada endpoint BIP yang berubah hasilnya.

- [ ] **Step 5: Commit**

```
git add shared-library/jwt_company_roundtrip_test.go
git commit -m "test(auth): regresi token tanpa company_id jatuh ke BIP"
```

---

## Catatan lanjutan (di luar Rencana 1)
- **Attendance service** (Rencana 2): tambah `company_id` di collection presensi + saring semua query pakai `common.CompanyID(c)`; migrasi backfill entri lama BIP; namespace `fingerprint_id` per perusahaan.
- **Master departemen/posisi/jadwal per-perusahaan** (Rencana 2/3): `MasterDepartment` dkk ber-`company_id`; `resolveSupervisedDepartments` & CRUD master disaring per perusahaan.
- **Peran "admin pusat" resmi** (Rencana 3): saat ini CRUD company dijaga `RequireITSupervisor` sementara.
- **Web erp-frontend & MyBharata** (Rencana 3/4): pemilih perusahaan admin pusat, onboarding, dan konsumsi konteks perusahaan.

## Self-review (penulis rencana)
- **Cakupan spec Bagian 1 (identitas & company_id):** Task 1-2-4 (helper+JWT+WorkData+login), Task 6 (entitas Perusahaan), Task 5 (backfill BIP). OK.
- **Cakupan Bagian 2 (penyaringan):** primitif `common.CompanyID` (Task 1) + propagasi gateway (Task 3) = fondasi; penerapan ke query presensi = Rencana 2 (dinyatakan eksplisit). OK untuk lingkup Rencana 1.
- **Placeholder:** tak ada "TBD/implement later"; tiap step berisi kode nyata.
- **Konsistensi tipe:** `common.DefaultCompanyID` (Task 1) dipakai konsisten di Task 2/4/5/7/8; `Header.CompanyID`/`Local.CompanyID` konsisten; `resolveCompanyID`/`defaultWorkCompany`/`ValidateCompany` (ekspor) nama sama di test & impl di seluruh Task 6.
