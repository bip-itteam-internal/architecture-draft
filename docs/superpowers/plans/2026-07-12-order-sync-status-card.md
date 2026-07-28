# Order Sync Status Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tampilkan status sinkronisasi order TikTok (cron 4x/hari) dan Shopee (webhook realtime) di halaman `/integration/transactions/list` dalam bentuk 2 card informatif.

**Architecture:**
- TikTok: `sync-tt-shop-orders` task simpan run stats ke `reconciler_run_stats` (collection yang sama dengan income-reconciler). Endpoint baru query stats tersebut.
- Shopee: endpoint query `webhook_logs` collection — count order-status webhook (code=3) hari ini + timestamp terakhir. Tidak perlu simpan stats baru.
- FE: 2 card di bawah `SettlementSyncStatus` yang sudah ada, menggunakan pola yang sama.

**Tech Stack:** Go + Fiber + MongoDB (backend), Next.js + React Query + Tailwind (frontend)

---

### Task 1: Backend — saveRunStats di sync-tt-shop-orders

**Files:**
- Modify: `bip-erp/services/integration/internal/worker/tasks/tt_shop_sync_orders.go`

- [ ] **Step 1: Tambah counter upserted di Run()**

Tambah variabel `totalUpserted int64` yang diakumulasi per shop. `SyncOrders` tidak return count — gunakan snapshot count dari `transaction_orders` sebelum dan sesudah run sebagai proxy. Cara lebih simpel: simpan stats dengan `upserted=0` (unknown) dan hanya timestamp + job name — cukup untuk kebutuhan UI "terakhir sync jam berapa".

Edit `tt_shop_sync_orders.go`, tambah `saveRunStats` call di akhir `Run()`:

```go
func (t *syncTTShopOrdersTask) Run(ctx context.Context, p worker.TaskProvider) error {
    start := time.Now()
    // ... existing code ...

    t.saveRunStats(ctx, p, start)
    return nil
}

const ttOrderSyncStatsCollection = "reconciler_run_stats"

func (t *syncTTShopOrdersTask) saveRunStats(ctx context.Context, p worker.TaskProvider, start time.Time) {
    doc := bson.M{
        "_id":         uuid.NewString(),
        "job":         "sync-tt-shop-orders",
        "run_at":      time.Now(),
        "duration_ms": time.Since(start).Milliseconds(),
    }
    if _, err := mongodb.GetCollection(ttOrderSyncStatsCollection).InsertOne(ctx, doc); err != nil {
        p.Logger.Warn("sync-tt-shop-orders: failed to save run stats", "error", err)
    }
}
```

- [ ] **Step 2: Tambah import yang dibutuhkan**

```go
import (
    // existing imports...
    mongodb "github.com/bharata/shared-library/database/mongodb"
    "github.com/google/uuid"
    "go.mongodb.org/mongo-driver/bson"
)
```

- [ ] **Step 3: Build verify**

```bash
cd bip-erp/services/integration && go build ./...
```
Expected: no error

- [ ] **Step 4: Commit**

```bash
git add services/integration/internal/worker/tasks/tt_shop_sync_orders.go
git commit -m "feat(integration): simpan run stats sync-tt-shop-orders ke reconciler_run_stats"
```

---

### Task 2: Backend — Endpoint GET /tiktok/shop/orders/sync-status

**Files:**
- Modify: `bip-erp/services/integration/internal/interface/http/tiktok_shop_handler.go`
- Modify: `bip-erp/services/integration/main.go`

- [ ] **Step 1: Tambah struct response**

Di `tiktok_shop_handler.go`, tambah di bawah struct `settlementSyncLastRun`:

```go
type orderSyncLastRun struct {
    RunAt      time.Time `bson:"run_at"      json:"run_at"`
    DurationMs int64     `bson:"duration_ms" json:"duration_ms"`
}
```

- [ ] **Step 2: Implement handler GetTTOrderSyncStatus**

```go
// GetTTOrderSyncStatus mengembalikan status sync order TikTok Shop:
// run terakhir + jumlah run hari ini (Asia/Jakarta).
func (h *TiktokShopHandler) GetTTOrderSyncStatus(c *fiber.Ctx) error {
    ctx := c.Context()
    coll := mongodb.GetCollection(reconcilerRunStatsCollection)

    var lastRun *orderSyncLastRun
    var latest orderSyncLastRun
    err := coll.FindOne(ctx, bson.M{"job": "sync-tt-shop-orders"},
        options.FindOne().SetSort(bson.D{{Key: "run_at", Value: -1}})).Decode(&latest)
    switch {
    case err == nil:
        lastRun = &latest
    case errors.Is(err, mongo.ErrNoDocuments):
        // belum ada run
    default:
        return fiber.NewError(fiber.StatusInternalServerError, err.Error())
    }

    loc, _ := time.LoadLocation("Asia/Jakarta")
    now := time.Now().In(loc)
    startOfDay := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, loc)

    runs, _ := coll.CountDocuments(ctx, bson.M{
        "job":    "sync-tt-shop-orders",
        "run_at": bson.M{"$gte": startOfDay},
    })

    data := fiber.Map{
        "schedule": "0,8,16,23",
        "last_run": lastRun,
        "today":    fiber.Map{"runs": runs},
    }
    return NewResponse().WithMessage("tt order sync status obtained").WithData(data).Render(c)
}
```

- [ ] **Step 3: Daftarkan route di main.go**

Cari blok route TikTok Shop, tambahkan:
```go
tpRoute.Get("/orders/sync-status", tiktokShopHandler.GetTTOrderSyncStatus)
```

- [ ] **Step 4: Build + commit**

```bash
cd bip-erp/services/integration && go build ./...
git add services/integration/internal/interface/http/tiktok_shop_handler.go \
        services/integration/main.go
git commit -m "feat(integration): endpoint GET /tiktok/shop/orders/sync-status"
```

---

### Task 3: Backend — Endpoint GET /shopee/orders/sync-status

**Files:**
- Modify: `bip-erp/services/integration/internal/interface/http/shopee_handler.go`
- Modify: `bip-erp/services/integration/main.go`

- [ ] **Step 1: Implement handler GetShopeeOrderSyncStatus**

Di `shopee_handler.go`:

```go
// GetShopeeOrderSyncStatus mengembalikan status sync order Shopee via webhook:
// jumlah webhook order-status (code=3) hari ini + timestamp terakhir.
func (h *ShopeeHandler) GetShopeeOrderSyncStatus(c *fiber.Ctx) error {
    ctx := c.Context()
    coll := mongodb.GetCollection("webhook_logs")

    loc, _ := time.LoadLocation("Asia/Jakarta")
    now := time.Now().In(loc)
    startOfDay := time.Date(now.Year(), now.Month(), now.Day(), 0, 0, 0, 0, loc)

    filter := bson.M{
        "source":          "SHOPEE",
        "payload.code":    3,
        "created_at":      bson.M{"$gte": startOfDay},
    }

    todayCount, _ := coll.CountDocuments(ctx, filter)

    var lastDoc struct {
        CreatedAt time.Time `bson:"created_at"`
    }
    var lastWebhookAt *time.Time
    err := coll.FindOne(ctx,
        bson.M{"source": "SHOPEE", "payload.code": 3},
        options.FindOne().SetSort(bson.D{{Key: "created_at", Value: -1}}).
            SetProjection(bson.M{"created_at": 1}),
    ).Decode(&lastDoc)
    if err == nil {
        lastWebhookAt = &lastDoc.CreatedAt
    }

    data := fiber.Map{
        "mode":            "realtime",
        "today_count":     todayCount,
        "last_webhook_at": lastWebhookAt,
    }
    return NewResponse().WithMessage("shopee order sync status obtained").WithData(data).Render(c)
}
```

- [ ] **Step 2: Daftarkan route di main.go**

```go
shopeeRoute.Get("/orders/sync-status", shopeeHandler.GetShopeeOrderSyncStatus)
```

- [ ] **Step 3: Build + commit**

```bash
cd bip-erp/services/integration && go build ./...
git add services/integration/internal/interface/http/shopee_handler.go \
        services/integration/main.go
git commit -m "feat(integration): endpoint GET /shopee/orders/sync-status"
```

---

### Task 4: Frontend — Hook + komponen OrderSyncStatus

**Files:**
- Create: `erp-frontend/src/features/integration/transactions/hooks/use-fetch-order-sync-status.ts`
- Create: `erp-frontend/src/features/integration/transactions/components/order-sync-status.tsx`
- Modify: `erp-frontend/src/app/(main)/integration/transactions/list/page.tsx`

- [ ] **Step 1: Buat hook TikTok**

```typescript
// use-fetch-order-sync-status.ts
import { useQuery } from "@tanstack/react-query";
import { axiosInstance } from "@/lib/axios";

export type TTOrderSyncLastRun = {
  run_at: string;
  duration_ms: number;
};

export type TTOrderSyncStatus = {
  schedule: string;
  last_run: TTOrderSyncLastRun | null;
  today: { runs: number };
};

export type ShopeeOrderSyncStatus = {
  mode: string;
  today_count: number;
  last_webhook_at: string | null;
};

export const useFetchTTOrderSyncStatus = () =>
  useQuery<TTOrderSyncStatus>({
    queryKey: ["tt-order-sync-status"],
    queryFn: async () => {
      const { data } = await axiosInstance.get<{ data: TTOrderSyncStatus }>(
        "/api/integration/tiktok/shop/orders/sync-status"
      );
      return data.data;
    },
    staleTime: 5 * 60 * 1000,
  });

export const useFetchShopeeOrderSyncStatus = () =>
  useQuery<ShopeeOrderSyncStatus>({
    queryKey: ["shopee-order-sync-status"],
    queryFn: async () => {
      const { data } = await axiosInstance.get<{ data: ShopeeOrderSyncStatus }>(
        "/api/integration/shopee/orders/sync-status"
      );
      return data.data;
    },
    staleTime: 5 * 60 * 1000,
  });
```

- [ ] **Step 2: Buat komponen OrderSyncStatus**

```tsx
// order-sync-status.tsx
"use client";

import { RefreshCw } from "lucide-react";
import { useFetchTTOrderSyncStatus, useFetchShopeeOrderSyncStatus } from "../hooks/use-fetch-order-sync-status";

const timeFormatter = new Intl.DateTimeFormat("id-ID", {
  hour: "2-digit",
  minute: "2-digit",
  timeZone: "Asia/Jakarta",
});

function CardShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 rounded-lg border border-border bg-card px-4 py-3 text-sm text-muted-foreground">
      {children}
    </div>
  );
}

function TTOrderSyncCard() {
  const { data, isLoading } = useFetchTTOrderSyncStatus();

  if (isLoading) return (
    <CardShell>
      <RefreshCw className="size-4 shrink-0 animate-spin" />
      <span>Memuat status sinkronisasi TikTok…</span>
    </CardShell>
  );

  if (!data) return null;

  return (
    <CardShell>
      <span className="flex items-center gap-2">
        <RefreshCw className="size-4 shrink-0" />
        <span className="font-medium text-foreground">Sinkronisasi Order TikTok</span>
      </span>
      <span>Jadwal: 4x sehari</span>
      {data.last_run ? (
        <span>
          Terakhir{" "}
          <span className="font-medium text-foreground">
            {timeFormatter.format(new Date(data.last_run.run_at))} WIB
          </span>
        </span>
      ) : (
        <span>Belum pernah jalan</span>
      )}
      <span>
        Hari ini{" "}
        <span className="font-medium text-foreground">{data.today.runs}</span>x sync
      </span>
    </CardShell>
  );
}

function ShopeeOrderSyncCard() {
  const { data, isLoading } = useFetchShopeeOrderSyncStatus();

  if (isLoading) return (
    <CardShell>
      <RefreshCw className="size-4 shrink-0 animate-spin" />
      <span>Memuat status sinkronisasi Shopee…</span>
    </CardShell>
  );

  if (!data) return null;

  return (
    <CardShell>
      <span className="flex items-center gap-2">
        <RefreshCw className="size-4 shrink-0" />
        <span className="font-medium text-foreground">Sinkronisasi Order Shopee</span>
      </span>
      <span>Realtime</span>
      <span>
        Hari ini{" "}
        <span className="font-medium text-foreground">{data.today_count}</span>{" "}
        order masuk
      </span>
      {data.last_webhook_at && (
        <span>
          Terakhir{" "}
          <span className="font-medium text-foreground">
            {timeFormatter.format(new Date(data.last_webhook_at))} WIB
          </span>
        </span>
      )}
    </CardShell>
  );
}

export function OrderSyncStatus() {
  return (
    <div className="flex flex-col gap-2">
      <TTOrderSyncCard />
      <ShopeeOrderSyncCard />
    </div>
  );
}
```

- [ ] **Step 3: Tambah OrderSyncStatus di page.tsx**

Di `list/page.tsx`, tambahkan import dan render di bawah `<SettlementSyncStatus />`:

```tsx
import { OrderSyncStatus } from "@/features/integration/transactions/components/order-sync-status";

// Di JSX, setelah <SettlementSyncStatus />:
<SettlementSyncStatus />
<OrderSyncStatus />
```

- [ ] **Step 4: Commit**

```bash
git add erp-frontend/src/features/integration/transactions/hooks/use-fetch-order-sync-status.ts \
        erp-frontend/src/features/integration/transactions/components/order-sync-status.tsx \
        erp-frontend/src/app/(main)/integration/transactions/list/page.tsx
git commit -m "feat(frontend): card status sinkronisasi order TikTok & Shopee"
```

---

## Self-Review

- ✅ Semua file path eksak sesuai struktur repo
- ✅ Pola konsisten dengan `SettlementSyncStatus` yang sudah ada
- ✅ Shopee pakai webhook_logs (tidak perlu schema baru)
- ✅ TikTok pakai `reconciler_run_stats` yang sudah ada (field `job` sebagai discriminator)
- ✅ Tidak ada TBD/TODO
- ✅ Build verify di setiap task
