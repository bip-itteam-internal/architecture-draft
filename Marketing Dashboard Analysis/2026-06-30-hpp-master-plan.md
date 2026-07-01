# HPP Master Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tambah HPP (Cost) per SKU ke master `items`, dengan endpoint list + upload xlsx (preview → commit) + edit manual, dan tab FE "HPP Master".

**Architecture:** Field `Cost` baru di `entity.ItemProduct`. Upload xlsx di-parse di backend (lib `excelize`), nama produk di-fuzzy-match ke `items.Name`, hasil dikembalikan sebagai preview (matched/ambiguous/unmatched) tanpa menulis DB. Commit terpisah meng-upsert `Cost`. FE: tab baru di `marketing-insight` dengan modal upload + preview + tabel.

**Tech Stack:** Go + Fiber + MongoDB (service `integration`); `github.com/xuri/excelize/v2` untuk xlsx; Next.js + shadcn + Tailwind (`erp-frontend`), `axiosInstance`.

**Spec:** `docs/superpowers/specs/2026-06-30-profit-engine-design.md`

**Working dir backend:** `bip-erp/services/integration`
**Run tests:** `go test ./internal/...`

---

## File Structure

Backend (`bip-erp/services/integration`):
- Modify: `internal/domain/entity/item.go` — tambah field `Cost`
- Create: `internal/usecase/hpp_usecase.go` — parse xlsx, fuzzy-match, build preview, commit upsert
- Create: `internal/usecase/hpp_usecase_test.go` — test match + preview
- Create: `internal/interface/http/hpp_handler.go` — handler list/upload/commit/edit
- Modify: `main.go` — wire handler + routes
- Modify: `go.mod` / `go.sum` — tambah excelize

Frontend (`erp-frontend`):
- Create: `src/app/(main)/marketing-insight/hpp-master/page.tsx`
- Create: `src/features/marketing-insight/hpp-master/types/hpp-master.ts`
- Create: `src/features/marketing-insight/hpp-master/hooks/use-hpp.ts`
- Create: `src/features/marketing-insight/hpp-master/components/upload-modal.tsx`

---

## Task 1: Tambah field mapping + Cost ke master items

> **TERVALIDASI DATA NYATA (2026-06-30):** Master `items` (87 produk) jadi mapping hub join.
> Join ads↔order TERBUKTI via `item_group_id`(ads) == `product_id`(order). `seller_sku` order = teks
> ("DR FAY CREAM") ≠ `items.sku` ("PJB-002"). Maka items butuh 3 field tambahan: `product_id`,
> `seller_sku`, `cost`. Lihat MASTER doc section B3.

**Files:**
- Modify: `internal/domain/entity/item.go:25` (setelah `BasePrice`)

- [ ] **Step 1: Tambah field product_id, seller_sku, Cost**

Di struct `ItemProduct`, setelah baris `BasePrice float64 ...`:

```go
	ProductID   string   `json:"product_id" bson:"product_id,omitempty"`   // = TikTok Shop product_id = ads item_group_id (join hub)
	SellerSKU   string   `json:"seller_sku" bson:"seller_sku,omitempty"`   // teks seller_sku di order (mis. "DR FAY CREAM")
	Cost        float64  `json:"cost" bson:"cost,omitempty"`               // HPP per pcs
```

- [ ] **Step 2: Build verify kompilasi**

Run: `go build ./...`
Expected: sukses, tanpa error.

- [ ] **Step 3: Commit**

```bash
git add internal/domain/entity/item.go
git commit -m "feat(items): tambah field Cost (HPP) ke ItemProduct"
```

---

## Task 2: Tambah excelize dependency

**Files:**
- Modify: `go.mod`, `go.sum`

- [ ] **Step 1: Tambah lib**

Run: `go get github.com/xuri/excelize/v2`
Expected: go.mod terupdate dengan `github.com/xuri/excelize/v2`.

- [ ] **Step 2: Commit**

```bash
git add go.mod go.sum
git commit -m "chore: tambah excelize untuk parse xlsx HPP"
```

---

## Task 3: HPP usecase — normalize + fuzzy match

**Files:**
- Create: `internal/usecase/hpp_usecase.go`
- Test: `internal/usecase/hpp_usecase_test.go`

- [ ] **Step 1: Tulis test gagal untuk normalizeName + matchName**

`internal/usecase/hpp_usecase_test.go`:

```go
package usecase

import "testing"

func TestNormalizeName(t *testing.T) {
	cases := map[string]string{
		"  Glossmen Lip Serum ": "glossmen lip serum",
		"Dr Fay Cream":          "dr fay cream",
		"KYURA ACNE-CREAM!":     "kyura acne cream",
	}
	for in, want := range cases {
		if got := normalizeName(in); got != want {
			t.Errorf("normalizeName(%q)=%q want %q", in, got, want)
		}
	}
}

func TestMatchName(t *testing.T) {
	items := []ItemNameSKU{
		{SKU: "GLM-01", Name: "Glossmen Lip Serum"},
		{SKU: "DRF-01", Name: "Dr Fay Cream"},
		{SKU: "DRF-02", Name: "Dr Fay Facial Foam"},
	}
	// exact-contains → 1 match
	got := matchName("Glossmen", items)
	if len(got) != 1 || got[0].SKU != "GLM-01" {
		t.Errorf("matchName(Glossmen)=%v want [GLM-01]", got)
	}
	// ambiguous: "Dr Fay" cocok 2
	got = matchName("Dr Fay", items)
	if len(got) != 2 {
		t.Errorf("matchName(Dr Fay) len=%d want 2", len(got))
	}
	// unmatched
	got = matchName("Produk Tak Ada", items)
	if len(got) != 0 {
		t.Errorf("matchName(unmatched) len=%d want 0", len(got))
	}
}
```

- [ ] **Step 2: Run test → gagal kompilasi**

Run: `go test ./internal/usecase/ -run 'TestNormalizeName|TestMatchName' -v`
Expected: FAIL — `undefined: normalizeName`, `undefined: matchName`, `undefined: ItemNameSKU`.

- [ ] **Step 3: Implement normalize + match**

`internal/usecase/hpp_usecase.go`:

```go
package usecase

import (
	"regexp"
	"strings"
)

// ItemNameSKU adalah pasangan minimal untuk matching nama → SKU.
type ItemNameSKU struct {
	SKU  string
	Name string
}

var nonAlphaNum = regexp.MustCompile(`[^a-z0-9 ]+`)
var multiSpace = regexp.MustCompile(`\s+`)

// normalizeName: lowercase, ganti simbol jadi spasi, rapikan spasi.
func normalizeName(s string) string {
	s = strings.ToLower(strings.TrimSpace(s))
	s = nonAlphaNum.ReplaceAllString(s, " ")
	s = multiSpace.ReplaceAllString(s, " ")
	return strings.TrimSpace(s)
}

// matchName: cocokkan nama xlsx ke daftar item via contains (dua arah) atas nama ter-normalisasi.
// Return semua kandidat (0=unmatched, 1=matched, >1=ambiguous).
func matchName(xlsxName string, items []ItemNameSKU) []ItemNameSKU {
	q := normalizeName(xlsxName)
	if q == "" {
		return nil
	}
	var out []ItemNameSKU
	for _, it := range items {
		n := normalizeName(it.Name)
		if n == q || strings.Contains(n, q) || strings.Contains(q, n) {
			out = append(out, it)
		}
	}
	return out
}
```

- [ ] **Step 4: Run test → pass**

Run: `go test ./internal/usecase/ -run 'TestNormalizeName|TestMatchName' -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add internal/usecase/hpp_usecase.go internal/usecase/hpp_usecase_test.go
git commit -m "feat(hpp): normalize + fuzzy match nama produk ke SKU"
```

---

## Task 4: HPP usecase — parse xlsx + build preview

**Files:**
- Modify: `internal/usecase/hpp_usecase.go`
- Test: `internal/usecase/hpp_usecase_test.go`

- [ ] **Step 1: Tulis test buildPreview**

Tambah di `hpp_usecase_test.go`:

```go
func TestBuildPreview(t *testing.T) {
	items := []ItemNameSKU{
		{SKU: "GLM-01", Name: "Glossmen Lip Serum", Cost: 0},
		{SKU: "DRF-01", Name: "Dr Fay Cream", Cost: 18700},
		{SKU: "DRF-02", Name: "Dr Fay Facial Foam"},
	}
	parsed := []ParsedHPP{
		{Name: "Glossmen", HPP: 17000}, // matched
		{Name: "Dr Fay", HPP: 18700},   // ambiguous (2 kandidat)
		{Name: "Barang Hantu", HPP: 999}, // unmatched
	}
	p := buildPreview(parsed, items)
	if len(p.Matched) != 1 || p.Matched[0].SKU != "GLM-01" || p.Matched[0].NewCost != 17000 {
		t.Errorf("matched salah: %+v", p.Matched)
	}
	if len(p.Ambiguous) != 1 || len(p.Ambiguous[0].Candidates) != 2 {
		t.Errorf("ambiguous salah: %+v", p.Ambiguous)
	}
	if len(p.Unmatched) != 1 || p.Unmatched[0].Name != "Barang Hantu" {
		t.Errorf("unmatched salah: %+v", p.Unmatched)
	}
}
```

- [ ] **Step 2: Run test → gagal**

Run: `go test ./internal/usecase/ -run TestBuildPreview -v`
Expected: FAIL — `undefined: ParsedHPP`, `buildPreview`, `Cost` field di ItemNameSKU.

- [ ] **Step 3: Implement types + buildPreview + parseXLSX**

Tambah di `hpp_usecase.go`. Update `ItemNameSKU` tambah `Cost float64`:

```go
// (update struct ItemNameSKU: tambah field Cost float64)

// ParsedHPP satu baris hasil parse xlsx.
type ParsedHPP struct {
	Name string  `json:"name"`
	HPP  float64 `json:"hpp"`
}

type MatchedRow struct {
	Name        string  `json:"xlsx_name"`
	SKU         string  `json:"sku"`
	ItemName    string  `json:"item_name"`
	CurrentCost float64 `json:"current_cost"`
	NewCost     float64 `json:"new_cost"`
}

type AmbiguousRow struct {
	Name       string        `json:"xlsx_name"`
	NewCost    float64       `json:"new_cost"`
	Candidates []ItemNameSKU `json:"candidates"`
}

type UnmatchedRow struct {
	Name    string  `json:"xlsx_name"`
	NewCost float64 `json:"new_cost"`
}

type HPPPreview struct {
	Matched   []MatchedRow   `json:"matched"`
	Ambiguous []AmbiguousRow `json:"ambiguous"`
	Unmatched []UnmatchedRow `json:"unmatched"`
}

func buildPreview(parsed []ParsedHPP, items []ItemNameSKU) HPPPreview {
	var p HPPPreview
	for _, row := range parsed {
		cands := matchName(row.Name, items)
		switch len(cands) {
		case 0:
			p.Unmatched = append(p.Unmatched, UnmatchedRow{Name: row.Name, NewCost: row.HPP})
		case 1:
			p.Matched = append(p.Matched, MatchedRow{
				Name: row.Name, SKU: cands[0].SKU, ItemName: cands[0].Name,
				CurrentCost: cands[0].Cost, NewCost: row.HPP,
			})
		default:
			p.Ambiguous = append(p.Ambiguous, AmbiguousRow{Name: row.Name, NewCost: row.HPP, Candidates: cands})
		}
	}
	return p
}
```

Tambah parse xlsx (import `github.com/xuri/excelize/v2`, `io`, `strconv`):

```go
// parseHPPXLSX baca sheet pertama+kedua: kol A=Produk, kol B=HPP/Pcs. Skip header & baris kosong.
func parseHPPXLSX(r io.Reader) ([]ParsedHPP, error) {
	f, err := excelize.OpenReader(r)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	var out []ParsedHPP
	for _, sheet := range f.GetSheetList() {
		rows, err := f.GetRows(sheet)
		if err != nil {
			continue
		}
		for _, row := range rows {
			if len(row) < 2 {
				continue
			}
			name := strings.TrimSpace(row[0])
			hppStr := strings.ReplaceAll(strings.TrimSpace(row[1]), ",", "")
			if name == "" || strings.EqualFold(name, "Produk") {
				continue
			}
			hpp, err := strconv.ParseFloat(hppStr, 64)
			if err != nil || hpp <= 0 {
				continue
			}
			out = append(out, ParsedHPP{Name: name, HPP: hpp})
		}
	}
	return out, nil
}
```

- [ ] **Step 4: Run test → pass**

Run: `go test ./internal/usecase/ -run TestBuildPreview -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add internal/usecase/hpp_usecase.go internal/usecase/hpp_usecase_test.go
git commit -m "feat(hpp): parse xlsx + build preview matched/ambiguous/unmatched"
```

---

## Task 5: HPP usecase struct + interface (list, preview, commit, edit)

**Files:**
- Modify: `internal/usecase/hpp_usecase.go`

- [ ] **Step 1: Tambah usecase struct yang pakai ItemRepository**

Tambah di `hpp_usecase.go` (import `context`, `entity`, `repository`):

```go
type HPPUseCase interface {
	List(ctx context.Context) ([]ItemNameSKU, error)
	Preview(ctx context.Context, r io.Reader) (HPPPreview, error)
	Commit(ctx context.Context, rows []CommitRow) (int, error)
	SetCost(ctx context.Context, sku string, cost float64) error
}

type CommitRow struct {
	SKU  string  `json:"sku"`
	Cost float64 `json:"cost"`
}

type hppUseCase struct {
	itemRepo repository.ItemRepository
}

func NewHPPUseCase(itemRepo repository.ItemRepository) HPPUseCase {
	return &hppUseCase{itemRepo: itemRepo}
}

func (u *hppUseCase) loadItems(ctx context.Context) ([]ItemNameSKU, error) {
	items, _, err := u.itemRepo.GetItems(ctx, repository.ItemListFilter{})
	if err != nil {
		return nil, err
	}
	out := make([]ItemNameSKU, 0, len(items))
	for _, it := range items {
		if it.SKU == "" {
			continue
		}
		out = append(out, ItemNameSKU{SKU: it.SKU, Name: it.Name, Cost: it.Cost})
	}
	return out, nil
}

func (u *hppUseCase) List(ctx context.Context) ([]ItemNameSKU, error) {
	return u.loadItems(ctx)
}

func (u *hppUseCase) Preview(ctx context.Context, r io.Reader) (HPPPreview, error) {
	parsed, err := parseHPPXLSX(r)
	if err != nil {
		return HPPPreview{}, err
	}
	items, err := u.loadItems(ctx)
	if err != nil {
		return HPPPreview{}, err
	}
	return buildPreview(parsed, items), nil
}

func (u *hppUseCase) Commit(ctx context.Context, rows []CommitRow) (int, error) {
	updated := 0
	for _, row := range rows {
		if row.SKU == "" || row.Cost <= 0 {
			continue
		}
		if err := u.SetCost(ctx, row.SKU, row.Cost); err != nil {
			return updated, err
		}
		updated++
	}
	return updated, nil
}

func (u *hppUseCase) SetCost(ctx context.Context, sku string, cost float64) error {
	item, err := u.itemRepo.GetItemBySKU(ctx, sku)
	if err != nil {
		return err
	}
	item.Cost = cost
	return u.itemRepo.UpdateItem(ctx, &item, nil)
}
```

> Catatan: verifikasi signature `GetItems`, `GetItemBySKU`, `UpdateItem`, dan tipe `repository.ItemListFilter` di `internal/usecase/item_usesace.go` & repo. Sesuaikan argumen `actionBy` bila `UpdateItem` mewajibkan non-nil — bila wajib, buat actor system default.

- [ ] **Step 2: Build verify**

Run: `go build ./...`
Expected: sukses. Bila error signature, sesuaikan ke API repo aktual.

- [ ] **Step 3: Commit**

```bash
git add internal/usecase/hpp_usecase.go
git commit -m "feat(hpp): usecase list/preview/commit/setCost via ItemRepository"
```

---

## Task 6: HPP HTTP handler

**Files:**
- Create: `internal/interface/http/hpp_handler.go`

- [ ] **Step 1: Implement handler**

`internal/interface/http/hpp_handler.go` (ikut pola handler existing: `NewResponse().WithData().Render(c)`):

```go
package http

import (
	"github.com/gofiber/fiber/v2"
	"integration/internal/usecase"
)

type HPPHandler struct {
	useCase usecase.HPPUseCase
}

func NewHPPHandler(uc usecase.HPPUseCase) *HPPHandler {
	return &HPPHandler{useCase: uc}
}

func (h *HPPHandler) List(c *fiber.Ctx) error {
	rows, err := h.useCase.List(c.Context())
	if err != nil {
		return NewResponse().WithError(err).WithStatusCode(fiber.StatusInternalServerError).Render(c)
	}
	return NewResponse().WithData(rows).Render(c)
}

func (h *HPPHandler) Upload(c *fiber.Ctx) error {
	fh, err := c.FormFile("file")
	if err != nil {
		return NewResponse().WithError(err).WithStatusCode(fiber.StatusBadRequest).WithMessage("file wajib").Render(c)
	}
	f, err := fh.Open()
	if err != nil {
		return NewResponse().WithError(err).WithStatusCode(fiber.StatusBadRequest).Render(c)
	}
	defer f.Close()
	preview, err := h.useCase.Preview(c.Context(), f)
	if err != nil {
		return NewResponse().WithError(err).WithStatusCode(fiber.StatusBadRequest).WithMessage("gagal parse xlsx").Render(c)
	}
	return NewResponse().WithData(preview).Render(c)
}

func (h *HPPHandler) Commit(c *fiber.Ctx) error {
	var body struct {
		Rows []usecase.CommitRow `json:"rows"`
	}
	if err := c.BodyParser(&body); err != nil {
		return NewResponse().WithError(err).WithStatusCode(fiber.StatusBadRequest).Render(c)
	}
	n, err := h.useCase.Commit(c.Context(), body.Rows)
	if err != nil {
		return NewResponse().WithError(err).WithStatusCode(fiber.StatusInternalServerError).Render(c)
	}
	return NewResponse().WithData(fiber.Map{"updated": n}).Render(c)
}

func (h *HPPHandler) Edit(c *fiber.Ctx) error {
	sku := c.Params("sku")
	var body struct {
		Cost float64 `json:"cost"`
	}
	if err := c.BodyParser(&body); err != nil {
		return NewResponse().WithError(err).WithStatusCode(fiber.StatusBadRequest).Render(c)
	}
	if err := h.useCase.SetCost(c.Context(), sku, body.Cost); err != nil {
		return NewResponse().WithError(err).WithStatusCode(fiber.StatusInternalServerError).Render(c)
	}
	return NewResponse().WithData(fiber.Map{"sku": sku, "cost": body.Cost}).Render(c)
}
```

> Verifikasi nama method response helper aktual di `response.go` (Step di Task ini pakai `WithData/WithError/WithStatusCode/WithMessage/Render`). Sesuaikan bila beda.

- [ ] **Step 2: Build verify**

Run: `go build ./...`
Expected: sukses.

- [ ] **Step 3: Commit**

```bash
git add internal/interface/http/hpp_handler.go
git commit -m "feat(hpp): handler list/upload/commit/edit"
```

---

## Task 7: Wire routes di main.go

**Files:**
- Modify: `main.go` (dekat blok DI + routes existing)

- [ ] **Step 1: Tambah DI + routes**

Di bagian Dependency Injection (dekat `itemUseCase`/`tiktokBusinessUseCase`):

```go
	hppUseCase := usecase.NewHPPUseCase(itemRepo)
	hppHandler := httpDelivery.NewHPPHandler(hppUseCase)
```

> Jika variabel repo item bernama lain (mis. `itemRepo` belum ada di main.go), buat: `itemRepo := infraRepo.NewItemRepository()` mengikuti pola repo lain.

Di blok routes:

```go
	hppRoute := app.Group("/items/hpp")
	hppRoute.Get("", hppHandler.List)
	hppRoute.Post("/upload", hppHandler.Upload)
	hppRoute.Post("/commit", hppHandler.Commit)
	hppRoute.Post("/:sku", hppHandler.Edit)
```

- [ ] **Step 2: Build verify**

Run: `go build ./...`
Expected: sukses.

- [ ] **Step 3: Run semua test**

Run: `go test ./internal/...`
Expected: PASS (HPP test hijau, test lain tak rusak).

- [ ] **Step 4: Commit**

```bash
git add main.go
git commit -m "feat(hpp): wire route /items/hpp (list/upload/commit/edit)"
```

---

## Task 8: FE — types + hook

**Files:**
- Create: `erp-frontend/src/features/marketing-insight/hpp-master/types/hpp-master.ts`
- Create: `erp-frontend/src/features/marketing-insight/hpp-master/hooks/use-hpp.ts`

> Working dir FE: `erp-frontend`. Verifikasi lokasi `axiosInstance` (lihat import di feature existing, mis. `src/features/marketing-insight/gmv-max/hooks/use-fetch-gmv-max.ts`).

- [ ] **Step 1: Types**

`types/hpp-master.ts`:

```ts
export type HppItem = { sku: string; name: string; cost: number };

export type MatchedRow = {
  xlsx_name: string;
  sku: string;
  item_name: string;
  current_cost: number;
  new_cost: number;
};
export type AmbiguousRow = {
  xlsx_name: string;
  new_cost: number;
  candidates: { sku: string; name: string }[];
};
export type UnmatchedRow = { xlsx_name: string; new_cost: number };

export type HppPreview = {
  matched: MatchedRow[];
  ambiguous: AmbiguousRow[];
  unmatched: UnmatchedRow[];
};

export type CommitRow = { sku: string; cost: number };
```

- [ ] **Step 2: Hook**

`hooks/use-hpp.ts` (sesuaikan import `axiosInstance` ke path aktual):

```ts
"use client";
import * as React from "react";
import { axiosInstance } from "@/lib/axios"; // VERIFIKASI path
import type { HppItem, HppPreview, CommitRow } from "../types/hpp-master";

export function useHpp() {
  const [items, setItems] = React.useState<HppItem[]>([]);
  const [loading, setLoading] = React.useState(false);

  const fetchList = React.useCallback(async () => {
    setLoading(true);
    try {
      const res = await axiosInstance.get("/items/hpp");
      setItems(res.data?.data ?? []);
    } finally {
      setLoading(false);
    }
  }, []);

  const upload = React.useCallback(async (file: File): Promise<HppPreview> => {
    const fd = new FormData();
    fd.append("file", file);
    const res = await axiosInstance.post("/items/hpp/upload", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data?.data as HppPreview;
  }, []);

  const commit = React.useCallback(async (rows: CommitRow[]): Promise<number> => {
    const res = await axiosInstance.post("/items/hpp/commit", { rows });
    return res.data?.data?.updated ?? 0;
  }, []);

  const editCost = React.useCallback(async (sku: string, cost: number) => {
    await axiosInstance.post(`/items/hpp/${encodeURIComponent(sku)}`, { cost });
  }, []);

  React.useEffect(() => { fetchList(); }, [fetchList]);

  return { items, loading, fetchList, upload, commit, editCost };
}
```

- [ ] **Step 3: Typecheck**

Run (di `erp-frontend`): `pnpm tsc --noEmit`
Expected: tanpa error pada file baru (perbaiki path import bila merah).

- [ ] **Step 4: Commit**

```bash
git add src/features/marketing-insight/hpp-master/types src/features/marketing-insight/hpp-master/hooks
git commit -m "feat(fe/hpp): types + hook list/upload/commit/edit"
```

---

## Task 9: FE — upload modal + page

**Files:**
- Create: `erp-frontend/src/features/marketing-insight/hpp-master/components/upload-modal.tsx`
- Create: `erp-frontend/src/app/(main)/marketing-insight/hpp-master/page.tsx`

- [ ] **Step 1: Upload modal**

`components/upload-modal.tsx` — pakai komponen Dialog shadcn existing (verifikasi import dari `@/components/ui/dialog`):

```tsx
"use client";
import * as React from "react";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import type { HppPreview, CommitRow } from "../types/hpp-master";

type Props = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onUpload: (file: File) => Promise<HppPreview>;
  onCommit: (rows: CommitRow[]) => Promise<number>;
  onDone: () => void;
};

export function UploadModal({ open, onOpenChange, onUpload, onCommit, onDone }: Props) {
  const [preview, setPreview] = React.useState<HppPreview | null>(null);
  const [busy, setBusy] = React.useState(false);

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try { setPreview(await onUpload(file)); } finally { setBusy(false); }
  };

  const handleCommit = async () => {
    if (!preview) return;
    setBusy(true);
    try {
      const rows: CommitRow[] = preview.matched.map((m) => ({ sku: m.sku, cost: m.new_cost }));
      const n = await onCommit(rows);
      alert(`HPP terupdate: ${n} produk`);
      onOpenChange(false);
      setPreview(null);
      onDone();
    } finally { setBusy(false); }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader><DialogTitle>Upload HPP (xlsx)</DialogTitle></DialogHeader>
        <input type="file" accept=".xlsx" onChange={handleFile} disabled={busy} />
        {preview && (
          <div className="max-h-80 space-y-3 overflow-auto text-sm">
            <div>✅ Cocok: {preview.matched.length}</div>
            <div>⚠️ Ambigu: {preview.ambiguous.length}</div>
            <div>❌ Tak ketemu: {preview.unmatched.length}</div>
            <table className="w-full">
              <thead><tr><th className="text-left">Produk (xlsx)</th><th>SKU</th><th>HPP baru</th></tr></thead>
              <tbody>
                {preview.matched.map((m) => (
                  <tr key={m.sku}><td>{m.item_name}</td><td>{m.sku}</td><td>{m.new_cost}</td></tr>
                ))}
              </tbody>
            </table>
            {preview.unmatched.length > 0 && (
              <div className="text-muted-foreground">
                Tak ketemu: {preview.unmatched.map((u) => u.xlsx_name).join(", ")}
              </div>
            )}
          </div>
        )}
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={busy}>Batal</Button>
          <Button onClick={handleCommit} disabled={busy || !preview || preview.matched.length === 0}>
            Terapkan {preview ? `(${preview.matched.length})` : ""}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
```

> Ambiguous resolution (pilih SKU manual) = enhancement; Fase 1 commit hanya `matched`. Ambiguous/unmatched ditampilkan untuk koreksi via edit manual setelahnya. Catat ini sebagai batasan sadar (bukan silent).

- [ ] **Step 2: Page**

`app/(main)/marketing-insight/hpp-master/page.tsx`:

```tsx
"use client";
import * as React from "react";
import { Button } from "@/components/ui/button";
import { useHpp } from "@/features/marketing-insight/hpp-master/hooks/use-hpp";
import { UploadModal } from "@/features/marketing-insight/hpp-master/components/upload-modal";

export default function Page() {
  const { items, loading, fetchList, upload, commit } = useHpp();
  const [open, setOpen] = React.useState(false);

  return (
    <main className="flex w-full flex-col gap-6">
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-semibold leading-8">HPP Master</h1>
          <p className="text-sm text-muted-foreground">
            Kelola HPP (harga pokok) per SKU. Upload file xlsx untuk update massal.
          </p>
        </div>
        <Button onClick={() => setOpen(true)}>Upload xlsx</Button>
      </div>

      <div className="rounded-lg border bg-white p-4">
        {loading ? <div>Memuat…</div> : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-muted-foreground">
                <th className="py-2">SKU</th><th>Nama</th><th className="text-right">HPP</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              {items.map((it) => (
                <tr key={it.sku} className="border-t">
                  <td className="py-2">{it.sku}</td>
                  <td>{it.name}</td>
                  <td className="text-right">{it.cost > 0 ? it.cost.toLocaleString("id-ID") : "—"}</td>
                  <td>{it.cost > 0 ? "Terisi" : "Kosong"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <UploadModal
        open={open}
        onOpenChange={setOpen}
        onUpload={upload}
        onCommit={commit}
        onDone={fetchList}
      />
    </main>
  );
}
```

- [ ] **Step 3: Typecheck + build**

Run (di `erp-frontend`): `pnpm tsc --noEmit` lalu `pnpm build`
Expected: sukses (perbaiki import komponen ui bila path beda).

- [ ] **Step 4: Commit**

```bash
git add src/features/marketing-insight/hpp-master/components src/app/\(main\)/marketing-insight/hpp-master
git commit -m "feat(fe/hpp): tab HPP Master + modal upload preview/commit"
```

---

## Task 10: Verifikasi end-to-end (manual)

- [ ] **Step 1: Jalankan service + FE**, buka tab HPP Master.
- [ ] **Step 2: Upload** `COGS-per-products (jan-mei2026).xlsx`.
- [ ] **Step 3: Cek preview** — pastikan ada matched (mis. "Glossmen", "Dr Fay Cream", "Flo Hair Tonic"), catat unmatched.
- [ ] **Step 4: Terapkan**, refresh, pastikan kolom HPP terisi untuk SKU yang cocok.
- [ ] **Step 5: Edit manual** 1 SKU unmatched, pastikan tersimpan.
- [ ] **Step 6:** Catat daftar produk unmatched untuk koreksi mapping nama (input ke fase berikutnya).

---

## Catatan batasan sadar (bukan silent)

- Commit hanya menerapkan baris **matched**. Ambiguous & unmatched ditampilkan, diselesaikan via **edit manual** (Fase 1). Resolusi ambiguous in-modal = enhancement.
- HPP dianggap berlaku lintas bulan (nilai per pcs stabil). Versioning HPP per bulan = di luar scope plan ini.
- Periode HPP xlsx Jan–Mei; dipakai untuk laba Juni (sesuai spec).
