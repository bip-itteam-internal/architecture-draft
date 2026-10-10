# Affiliate Seller Sync — Implementation Plan

- **Status**: 🟡 Konsep / Plan — rencana implementasi affiliate sync.

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development atau superpowers:executing-plans. Steps pakai checkbox `- [ ]`.

**Goal:** Auto-sync data affiliate dari TikTok Shop `Search Seller Affiliate Orders` API ke koleksi `affiliate_orders`, dipanggil dari DALAM service (token via `GetOrRefreshToken`, bukan token DB stale).

**Architecture:** Client method baru di `tiktok_client.go` (reuse `generateSign`/`buildQueryString`) → usecase sync (pola order sync) → repo upsert → cron task + endpoint manual. Token diambil via `GetOrRefreshToken(storeID)` existing (auto-refresh, hindari token stale — lihat memory `affiliate-api-test-findings`).

**Tech Stack:** Go + Fiber + MongoDB, service `bip-erp/services/integration`.

**Spec:** `docs/superpowers/specs/2026-06-30-affiliate-seller-sync-design.md`
**Run tests:** `go test ./internal/...` · **Build:** `go build ./...`
**Working dir:** `bip-erp/services/integration`

## PRASYARAT (di luar kode — cek dulu)
- Scope **733764** (Read Seller Affiliate Collaborations) granted di app `TIKTOK_SHOP_APP_ID`.
- Toko re-authorize dgn scope itu (cred `scopes:[]` kosong = red flag; pastikan token punya akses affiliate).
- Test HARUS dari service (token via GetOrRefreshToken). Token DB langsung = stale → 401 (terbukti).

## Endpoint API
```
POST open-api.tiktokglobalshop.com/affiliate_seller/202405/orders/search
Query: app_key, timestamp, shop_cipher, version=202405, page_size, sign  (+ page_token)
Header: x-tts-access-token
Body: {} (opsional filter create_time_ge/le, order_status)
```

---

## File Structure
- Modify: `internal/infrastructure/clients/tiktok_client.go` — method `SearchSellerAffiliateOrders` + response types
- Create: `internal/domain/entity/affiliate.go` — `AffiliateOrder`
- Create: `internal/infrastructure/repository/affiliate_repo.go` — upsert + list
- Modify: `internal/domain/repository/*` — interface `AffiliateRepository` (ikut pola repo lain)
- Create: `internal/usecase/affiliate_usecase.go` — `SyncOrders`
- Create: `internal/interface/http/affiliate_handler.go` — sync + list handler
- Create: `internal/worker/tasks/affiliate_orders_sync.go` — cron task
- Modify: `main.go` — wire + routes + register task

---

## Task 1: Client method SearchSellerAffiliateOrders

**Files:** Modify `internal/infrastructure/clients/tiktok_client.go`

- [ ] **Step 1: Tambah response types** (setelah types video performance)

```go
type AffiliateOrderQuery struct {
	PageSize     int
	PageToken    string
	CreateTimeGe int64 // unix, opsional
	CreateTimeLe int64
}

type TiktokAffiliateOrdersResponse struct {
	Code    int    `json:"code"`
	Message string `json:"message"`
	Data    struct {
		NextPageToken string                  `json:"next_page_token"`
		TotalCount    int                     `json:"total_count"`
		Orders        []TiktokAffiliateOrder  `json:"orders"`
	} `json:"data"`
}

// Field grounded ke CSV affiliate_orders + dok Affiliate integration.md.
// Verifikasi nama JSON aktual saat call pertama; sesuaikan bila beda.
type TiktokAffiliateOrder struct {
	OrderID         string `json:"order_id"`
	ProductID       string `json:"product_id"`
	SkuID           string `json:"sku_id"`
	ProductName     string `json:"product_name"`
	PaymentAmount   string `json:"payment_amount"`
	Quantity        int    `json:"quantity"`
	OrderStatus     string `json:"order_status"`
	CreatorUsername string `json:"creator_username"`
	ContentType     string `json:"content_type"`
	ContentID       string `json:"content_id"`
	CommissionRate  string `json:"commission_rate"`
	EstCommission   string `json:"est_commission"`
	ActualCommission string `json:"actual_commission"`
	CreateTime      int64  `json:"create_time"`
}
```

- [ ] **Step 2: Tambah method** (pola sama `GetShopVideoPerformance` — POST + cipher + version)

```go
func (c *TikTokClient) SearchSellerAffiliateOrders(
	ctx context.Context,
	shopCipher, accessToken, appKey, appSecret string,
	q AffiliateOrderQuery,
) (*TiktokAffiliateOrdersResponse, error) {
	path := "/affiliate_seller/202405/orders/search"
	timestamp := time.Now().Unix()

	signParams := map[string]string{
		"app_key":     appKey,
		"timestamp":   fmt.Sprintf("%d", timestamp),
		"shop_cipher": shopCipher,
		"version":     "202405",
	}
	if q.PageSize > 0 {
		signParams["page_size"] = fmt.Sprintf("%d", q.PageSize)
	}
	if q.PageToken != "" {
		signParams["page_token"] = q.PageToken
	}

	body := "{}" // filter opsional bisa ditambah ke body sesuai dok
	sign := generateSign(appSecret, path, signParams, body)
	signParams["sign"] = sign

	rawURL := fmt.Sprintf("%s%s?%s", tiktokAPIBaseURL, path, buildQueryString(signParams))
	req, err := http.NewRequestWithContext(ctx, "POST", rawURL, strings.NewReader(body))
	if err != nil {
		return nil, fmt.Errorf("tiktok: search_affiliate_orders create request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-tts-access-token", accessToken)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("tiktok: search_affiliate_orders request: %w", err)
	}
	defer resp.Body.Close()
	b, _ := io.ReadAll(resp.Body)

	var result TiktokAffiliateOrdersResponse
	if err := json.Unmarshal(b, &result); err != nil {
		return nil, fmt.Errorf("tiktok: search_affiliate_orders decode: %w (body=%s)", err, string(b))
	}
	if result.Code != 0 {
		return nil, fmt.Errorf("tiktok: search_affiliate_orders code=%d msg=%s", result.Code, result.Message)
	}
	return &result, nil
}
```

- [ ] **Step 3: Build** — `go build ./...` → sukses (pastikan `strings`/`io` sudah di-import; keduanya sudah dipakai di file).

- [ ] **Step 4: Commit**
```bash
git add internal/infrastructure/clients/tiktok_client.go
git commit -m "feat(integration): add SearchSellerAffiliateOrders client method"
```

---

## Task 2: Entity AffiliateOrder

**Files:** Create `internal/domain/entity/affiliate.go`

- [ ] **Step 1: Entity**
```go
package entity

import "time"

// AffiliateOrder = 1 baris order affiliate (dari Search Seller Affiliate Orders).
type AffiliateOrder struct {
	ID               string    `json:"id" bson:"_id"` // "<order_id>_<sku_id>"
	OrderID          string    `json:"order_id" bson:"order_id"`
	StoreID          string    `json:"store_id" bson:"store_id"`
	ProductID        string    `json:"product_id" bson:"product_id"` // = ads item_group_id (join hub)
	SkuID            string    `json:"sku_id" bson:"sku_id"`
	ProductName      string    `json:"product_name" bson:"product_name"`
	PaymentAmount    float64   `json:"payment_amount" bson:"payment_amount"`
	Quantity         int       `json:"quantity" bson:"quantity"`
	OrderStatus      string    `json:"order_status" bson:"order_status"`
	CreatorUsername  string    `json:"creator_username" bson:"creator_username"`
	ContentType      string    `json:"content_type" bson:"content_type"`
	ContentID        string    `json:"content_id" bson:"content_id"`
	CommissionRate   float64   `json:"commission_rate" bson:"commission_rate"`
	EstCommission    float64   `json:"est_commission" bson:"est_commission"`
	ActualCommission float64   `json:"actual_commission" bson:"actual_commission"`
	OrderCreateTime  time.Time `json:"order_create_time" bson:"order_create_time"`
	SyncedAt         time.Time `json:"synced_at" bson:"synced_at"`
}
```

- [ ] **Step 2: Build** `go build ./...` → sukses.
- [ ] **Step 3: Commit**
```bash
git add internal/domain/entity/affiliate.go
git commit -m "feat(integration): add AffiliateOrder entity"
```

---

## Task 3: Repository (upsert + list)

**Files:** Create `internal/infrastructure/repository/affiliate_repo.go`; tambah interface `AffiliateRepository` di `internal/domain/repository/` (ikut file pola repo lain — mis. tiktok_shop_repo interface).

- [ ] **Step 1: Interface** (di `internal/domain/repository/`, file baru `affiliate_repo.go` atau sesuai konvensi existing)
```go
package repository

import (
	"context"
	"integration/internal/domain/entity"
)

type AffiliateRepository interface {
	UpsertOrders(ctx context.Context, orders []entity.AffiliateOrder) (int, error)
	ListOrders(ctx context.Context, storeID string, limit, skip int64) ([]entity.AffiliateOrder, int64, error)
}
```

- [ ] **Step 2: Impl** `internal/infrastructure/repository/affiliate_repo.go` (pola `item_repo.go`: `mongodb.GetCollection`, bulk `UpdateOne` upsert)
```go
package repository

import (
	"context"
	"time"

	"github.com/bharata/shared-library/database/mongodb"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"integration/internal/domain/entity"
	domainRepo "integration/internal/domain/repository"
)

const affiliateOrdersCollection = "affiliate_orders"

type affiliateRepo struct{}

func NewAffiliateRepository() domainRepo.AffiliateRepository { return &affiliateRepo{} }

func (r *affiliateRepo) UpsertOrders(ctx context.Context, orders []entity.AffiliateOrder) (int, error) {
	if len(orders) == 0 {
		return 0, nil
	}
	coll := mongodb.GetCollection(affiliateOrdersCollection)
	models := make([]mongo.WriteModel, 0, len(orders))
	now := time.Now()
	for _, o := range orders {
		o.SyncedAt = now
		models = append(models, mongo.NewUpdateOneModel().
			SetFilter(bson.M{"_id": o.ID}).
			SetUpdate(bson.M{"$set": o}).
			SetUpsert(true))
	}
	res, err := coll.BulkWrite(ctx, models)
	if err != nil {
		return 0, err
	}
	return int(res.UpsertedCount + res.ModifiedCount), nil
}

func (r *affiliateRepo) ListOrders(ctx context.Context, storeID string, limit, skip int64) ([]entity.AffiliateOrder, int64, error) {
	coll := mongodb.GetCollection(affiliateOrdersCollection)
	filter := bson.M{}
	if storeID != "" {
		filter["store_id"] = storeID
	}
	total, _ := coll.CountDocuments(ctx, filter)
	cur, err := coll.Find(ctx, filter)
	if err != nil {
		return nil, 0, err
	}
	var out []entity.AffiliateOrder
	if err := cur.All(ctx, &out); err != nil {
		return nil, 0, err
	}
	return out, total, nil
}
```
> Verifikasi signature `mongodb.GetCollection` + import path `shared-library` ke file repo existing. Sesuaikan bila beda.

- [ ] **Step 3: Build** `go build ./...` → sukses.
- [ ] **Step 4: Commit**
```bash
git add internal/domain/repository/affiliate_repo.go internal/infrastructure/repository/affiliate_repo.go
git commit -m "feat(integration): add AffiliateRepository upsert+list"
```

---

## Task 4: Usecase SyncOrders (token via GetOrRefreshToken)

**Files:** Create `internal/usecase/affiliate_usecase.go`

- [ ] **Step 1: Usecase** — reuse `GetOrRefreshToken` + shop cipher lookup (pola order sync di tiktok_usecase.go)
```go
package usecase

import (
	"context"
	"fmt"
	"strconv"
	"time"

	"integration/internal/domain/entity"
	"integration/internal/domain/repository"
	"integration/internal/infrastructure/clients"
)

type AffiliateUseCase interface {
	SyncOrders(ctx context.Context, storeID string) (int, error)
}

type affiliateUseCase struct {
	client       *clients.TikTokClient
	affRepo      repository.AffiliateRepository
	ttShopUC     TikTokShopUseCase // untuk GetOrRefreshToken + cipher/appkey
	appKey       string
	appSecret    string
}

func NewAffiliateUseCase(client *clients.TikTokClient, affRepo repository.AffiliateRepository, ttShopUC TikTokShopUseCase, appKey, appSecret string) AffiliateUseCase {
	return &affiliateUseCase{client: client, affRepo: affRepo, ttShopUC: ttShopUC, appKey: appKey, appSecret: appSecret}
}

func (u *affiliateUseCase) SyncOrders(ctx context.Context, storeID string) (int, error) {
	// token AKTIF via GetOrRefreshToken (hindari token DB stale — lihat memory affiliate-api-test-findings)
	token, err := u.ttShopUC.GetOrRefreshToken(ctx, storeID)
	if err != nil {
		return 0, fmt.Errorf("affiliate: get token store=%s: %w", storeID, err)
	}
	cipher, err := u.ttShopUC.GetShopCipher(ctx, storeID) // tambah helper bila belum ada
	if err != nil {
		return 0, fmt.Errorf("affiliate: get cipher store=%s: %w", storeID, err)
	}

	total := 0
	pageToken := ""
	for {
		resp, err := u.client.SearchSellerAffiliateOrders(ctx, cipher, token, u.appKey, u.appSecret, clients.AffiliateOrderQuery{PageSize: 50, PageToken: pageToken})
		if err != nil {
			return total, err
		}
		batch := make([]entity.AffiliateOrder, 0, len(resp.Data.Orders))
		for _, o := range resp.Data.Orders {
			pay, _ := strconv.ParseFloat(o.PaymentAmount, 64)
			est, _ := strconv.ParseFloat(o.EstCommission, 64)
			act, _ := strconv.ParseFloat(o.ActualCommission, 64)
			rate, _ := strconv.ParseFloat(o.CommissionRate, 64)
			batch = append(batch, entity.AffiliateOrder{
				ID: o.OrderID + "_" + o.SkuID, OrderID: o.OrderID, StoreID: storeID,
				ProductID: o.ProductID, SkuID: o.SkuID, ProductName: o.ProductName,
				PaymentAmount: pay, Quantity: o.Quantity, OrderStatus: o.OrderStatus,
				CreatorUsername: o.CreatorUsername, ContentType: o.ContentType, ContentID: o.ContentID,
				CommissionRate: rate, EstCommission: est, ActualCommission: act,
				OrderCreateTime: time.Unix(o.CreateTime, 0),
			})
		}
		n, err := u.affRepo.UpsertOrders(ctx, batch)
		if err != nil {
			return total, err
		}
		total += n
		if resp.Data.NextPageToken == "" {
			break
		}
		pageToken = resp.Data.NextPageToken
	}
	return total, nil
}
```
> **PENTING:** `TikTokShopUseCase` harus expose `GetOrRefreshToken(ctx, storeID) (string, error)` (sudah ada, cek interface — mungkin unexported; export bila perlu) + helper `GetShopCipher(ctx, storeID) (string, error)` (tambah bila belum ada: lookup `tt_shop_authorized_shops` by store). Verifikasi & sesuaikan.

- [ ] **Step 2: Build** `go build ./...` → sukses (sesuaikan interface TikTokShopUseCase).
- [ ] **Step 3: Commit**
```bash
git add internal/usecase/affiliate_usecase.go
git commit -m "feat(integration): affiliate SyncOrders via GetOrRefreshToken (active token)"
```

---

## Task 5: HTTP handler + routes

**Files:** Create `internal/interface/http/affiliate_handler.go`; Modify `main.go`

- [ ] **Step 1: Handler**
```go
package http

import (
	"github.com/gofiber/fiber/v2"
	"integration/internal/usecase"
)

type AffiliateHandler struct{ uc usecase.AffiliateUseCase }

func NewAffiliateHandler(uc usecase.AffiliateUseCase) *AffiliateHandler { return &AffiliateHandler{uc: uc} }

// GET /tiktok/affiliate/orders/sync?store_id=...
func (h *AffiliateHandler) Sync(c *fiber.Ctx) error {
	storeID := c.Query("store_id")
	if storeID == "" {
		return NewResponse().WithStatusCode(fiber.StatusBadRequest).WithMessage("store_id wajib").Render(c)
	}
	n, err := h.uc.SyncOrders(c.Context(), storeID)
	if err != nil {
		return NewResponse().WithError(err).WithStatusCode(fiber.StatusInternalServerError).Render(c)
	}
	return NewResponse().WithData(fiber.Map{"upserted": n}).Render(c)
}
```

- [ ] **Step 2: Wire di main.go** (dekat DI tiktokShop + routes `tpRoute`)
```go
	affiliateUseCase := usecase.NewAffiliateUseCase(tiktokClient, infraRepo.NewAffiliateRepository(), tiktokShopUseCase, os.Getenv("TIKTOK_SHOP_APP_KEY"), os.Getenv("TIKTOK_SHOP_APP_SECRET"))
	affiliateHandler := httpDelivery.NewAffiliateHandler(affiliateUseCase)
	// ...
	affRoute := app.Group("/tiktok/affiliate")
	affRoute.Get("/orders/sync", affiliateHandler.Sync)
```
> Verifikasi nama var `tiktokClient`/`tiktokShopUseCase` aktual di main.go; sesuaikan.

- [ ] **Step 3: Build + test** `go build ./... && go test ./internal/...` → hijau.
- [ ] **Step 4: Commit**
```bash
git add internal/interface/http/affiliate_handler.go main.go
git commit -m "feat(integration): wire affiliate sync handler + route"
```

---

## Task 6: Cron task (harian)

**Files:** Create `internal/worker/tasks/affiliate_orders_sync.go`; Modify `main.go` (register)

- [ ] **Step 1: Task** (pola `tt_business_gmv_max_report.go`: `Run` + `Schedule`; loop authorized shops)
```go
package tasks

import (
	"context"
	"integration/internal/usecase"
	"integration/internal/worker"
)

type affiliateOrdersSyncTask struct {
	affUC    usecase.AffiliateUseCase
	shopLister interface{ ListStoreIDs(ctx context.Context) ([]string, error) } // sesuaikan ke sumber daftar shop
}

func NewAffiliateOrdersSyncTask(affUC usecase.AffiliateUseCase, shopLister interface{ ListStoreIDs(ctx context.Context) ([]string, error) }) worker.Task {
	return &affiliateOrdersSyncTask{affUC: affUC, shopLister: shopLister}
}

func (t *affiliateOrdersSyncTask) Name() string     { return "sync-affiliate-orders" }
func (t *affiliateOrdersSyncTask) Schedule() string  { return "0 3 * * *" } // 03:00 harian

func (t *affiliateOrdersSyncTask) Run(ctx context.Context, p worker.TaskProvider) error {
	ids, err := t.shopLister.ListStoreIDs(ctx)
	if err != nil {
		return err
	}
	for _, id := range ids {
		_, _ = t.affUC.SyncOrders(ctx, id) // log error per-store, jangan gagalkan semua
	}
	return nil
}
```
> Verifikasi interface `worker.Task` aktual (Name/Schedule/Run signature) di `tt_business_gmv_max_report.go`. Sesuaikan persis. `ListStoreIDs` = pakai sumber daftar shop existing (mis. tiktokShopRepo.ListAuthorizedShops).

- [ ] **Step 2: Register di main.go** (dekat `tasks.Register(...)` lain)
```go
	if err := tasks.Register(app.Manager, tasks.NewAffiliateOrdersSyncTask(affiliateUseCase, <shopLister>)); err != nil {
		logger.Error("register task failed", "error", err)
	}
```

- [ ] **Step 3: Build + test** → hijau.
- [ ] **Step 4: Commit**
```bash
git add internal/worker/tasks/affiliate_orders_sync.go main.go
git commit -m "feat(integration): register daily affiliate orders sync cron"
```

---

## Task 7: Verifikasi end-to-end (di service, bukan lokal)

- [ ] **Step 1:** Deploy/jalankan service dgn scope 733764 granted + toko re-authorized.
- [ ] **Step 2:** Panggil `GET /tiktok/affiliate/orders/sync?store_id=<Glowbooster storeID>`. Token via GetOrRefreshToken (aktif). Cek response `{upserted: N}` bukan 401.
- [ ] **Step 3:** Kalau **401/scope error** → prasyarat belum beres (scope 733764 belum granted / toko belum re-auth dgn scope). Bereskan di TikTok Partner, bukan kode.
- [ ] **Step 4:** Kalau **field decode error** → nama JSON response ≠ asumsi. Log body, sesuaikan `TiktokAffiliateOrder` tags ke response nyata.
- [ ] **Step 5:** Bandingkan hasil vs CSV `affiliate_orders_*.csv` (802 order) — jumlah + field cocok?
- [ ] **Step 6:** Verifikasi join: `affiliate_orders.product_id` ada di `tt_business_gmv_max_performance_reports.dimensions.item_group_id` (sudah terbukti 18/18 di CSV).

---

## Catatan penting (dari test 2026-07-01)
- **JANGAN** ambil token dari `tt_shop_credentials` langsung — stale (di-supersede refresh cron) → 401. Selalu via `GetOrRefreshToken`.
- `buildQueryString` raw (no url-encode). `version=202405` wajib di query. Signing = `generateSign` existing.
- app_key/secret = env `TIKTOK_SHOP_APP_KEY/SECRET` (bukan coll credentials yang kosong).
- Lihat memory `affiliate-api-test-findings` + spec `2026-06-30-affiliate-seller-sync-design.md`.

## Di luar scope plan ini
- FE tab Affiliate (setelah data masuk).
- Join ke profit-engine (Scope 2).
- Creator API / Get Live Room Info (scope lain).
- Webhook real-time (cron harian dulu).
