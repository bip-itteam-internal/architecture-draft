# Rencana - Kurangi Fetch Global Sidebar (erp-frontend)

> **Untuk pekerja agentic:** SUB-SKILL WAJIB: superpowers:subagent-driven-development atau superpowers:executing-plans. Langkah pakai checkbox (`- [ ]`).

**Goal:** Karyawan yang tidak memegang modul warehouse / sadewa / accurate harus **nol** request ke tiga endpoint itu. Saat ini setiap tab yang terbuka menembak ketiganya tiap 30 detik, yaitu 360 request per jam per tab, terlepas dari role maupun halaman yang sedang dibuka.

**Prasyarat:** Tidak ada. Murni frontend, tanpa perubahan kontrak backend, jadi aturan "deploy BE sebelum FE" tidak berlaku.

## Temuan (kenapa ini terjadi)

Semua halaman berada di bawah `src/app/(main)/layout.tsx` yang merender `Container` lalu `AppSidebar`. Konsekuensinya: **hook apa pun yang dipanggil sidebar akan jalan di setiap halaman**, termasuk modul yang tidak sedang dibuka pemakai.

Di `src/components/layout/sidebar.tsx:73-109` ada 7 query yang ikut nyala tiap halaman dibuka. Empat di antaranya sudah sehat (`staleTime` 5 sampai 10 menit, tanpa polling): `useFetchMyProfile`, `useSubordinates`, `useMenuHidden`, `useMySpaceRoles`. Tiga sisanya adalah biang keroknya, semuanya **polling 30 detik tanpa `enabled` sama sekali**:

| Hook | Endpoint | Lokasi |
|---|---|---|
| `useQueueCounts` | `/api/warehouse/fulfillment/queue/counts` | `src/features/warehouse/hooks/use-warehouse-queue.ts:119-148` |
| `useSadewaCetakResiPendingCount` | `/api/manufacture/sadewa/actions?type=CETAK_RESI&status=PENDING` | `src/features/warehouse-sadewa/use-sadewa-actions.ts:115-126` |
| `useExternalEditDraftsNewCount` | `/api/integration/accurate/external-edit-drafts?status=BARU` | `src/features/integration/accurate/hooks/use-external-edit-drafts.ts:63-80` |

Ketiganya hanya dipakai untuk **angka badge** di menu warehouse dan Kotak Adopsi. Orang HRIS yang sedang membuka halaman cuti tetap menembak endpoint warehouse, sadewa, dan accurate setiap 30 detik selama tab dibiarkan terbuka, dan sebagian besar dijawab 403/404 lalu dibuang.

Pemerkeruh kedua: `src/components/tanstack.tsx:11` membuat `new QueryClient()` polos tanpa `defaultOptions`, sehingga seluruh aplikasi mewarisi `staleTime: 0` + `refetchOnWindowFocus: true`. Setiap query yang tidak mengatur sendiri akan refetch tiap pindah halaman dan tiap pemakai kembali ke tab browser.

**Yang BUKAN penyebab:** prefetch `next/link` di `navigation.tsx`. Memang memunculkan banyak request `?_rsc=` di Network tab, tapi 203 dari 253 halaman adalah client component sehingga prefetch cuma menarik shell halaman, bukan API modulnya. Berisik dilihat, tapi bukan beban backend, dan mematikannya justru memperlambat navigasi. Jangan dikerjakan.

**Architecture:** Gerbang `enabled` diturunkan dari `combinedMenus`, yaitu daftar menu yang **benar-benar tampil** untuk pemakai ini setelah seluruh penyaringan role, izin RBAC ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]), matriks akses WMS, dan setelan tampilan per posisi. Aturannya satu kalimat: "ada badge kalau menunya ada".

Alternatif yang **DITOLAK**: menyusun ulang predikat dari `systemRoles` (mis. `punyaRoleWarehouseTinggar || itSupervisor || pengawasWms`). Itu menyalin matriks akses WMS ke tempat kedua, dan begitu matriksnya berubah, gerbang fetch menyimpang diam-diam sampai ada yang kebetulan membuka Network tab. Prinsipnya sama dengan aturan feed kalender: jangan menulis ulang resolusi milik modul lain.

Pemindahan hook ini murah karena badge **sudah** ditempel di JSX (`sidebar.tsx:596-631`), terpisah dari perhitungan `combinedMenus`. Yang perlu dilakukan hanya memindahkan tiga pemanggilan hook ke bawah perhitungan itu. Legal terhadap Rules of Hooks: tidak ada early return maupun cabang di antaranya, jumlah dan urutan hook tetap sama tiap render.

**Tech Stack:** Next.js 16 App Router, React 19, TanStack Query + axios. Test: vitest (`pnpm test`). Lint: `pnpm lint` atas `./src`.

## Global Constraints

- **Badge tidak boleh hilang untuk yang berhak.** Ini kegagalan paling mungkin dari rencana ini, dan test saja tidak cukup membuktikannya. Wajib verifikasi dua akun di browser (Task 6).
- **`sidebar.tsx` adalah komponen shared** yang dipakai semua modul, jadi finalize wajib `pnpm test` **penuh**, bukan file terpilih.
- **Fungsi murni diekstrak ke berkas sendiri** supaya bisa dites tanpa merender sidebar, mengikuti pola `kpi-menu.ts`, `tools-menu.ts`, `sidebar-menu-shape.ts` yang sudah mapan di folder itu.
- **Tidak ada teks user-facing baru**, jadi ADR 0010 (i18n) tidak tersentuh.
- **Git**: branch `fix/sidebar-fetch-global` dari `origin/main`, commit tanpa trailer `Co-Authored-By`, git via PowerShell. Repo kode **wajib PR**, jangan commit langsung ke `main`.

---

### Task 1: Berkas murni `sidebar-badges.ts` + test

**Files (Create):** `src/components/layout/sidebar-badges.ts`, `src/components/layout/sidebar-badges.test.ts`

**Interfaces:**
```ts
export const URL_BADGE = {
  gudangPicking: "/warehouse/picking",
  gudangPacking: "/warehouse/packing",
  sadewaResi:    "/warehouse/sadewa/labels",
  kotakAdopsi:   "/integration-accurate/kotak-adopsi",
} as const;

export function kumpulkanUrlMenu(modul: { items: MenuItem[] }[]): Set<string>
export function badgeYangDibutuhkan(urls: Set<string>): {
  antrianGudang: boolean;   // picking ATAU packing
  sadewaResi: boolean;
  kotakAdopsi: boolean;
}
```

`kumpulkanUrlMenu` wajib menelusuri item datar **dan** anak grup, karena `ratakanIndukTipis` (`sidebar-menu-shape.ts:65`) bisa menaikkan anak ke tingkat atas sehingga bentuk pohonnya berbeda antar-pemakai.

- [ ] **Step 1 (test gagal, vitest):** `sidebar-badges.test.ts` dengan kasus:
  - menu kosong (karyawan HRIS biasa) -> ketiganya `false`. **Ini keluhan aslinya, kunci di sini.**
  - hanya `/warehouse/sadewa/labels` (admin gudang Sadewa) -> `sadewaResi` true, `antrianGudang` **false**
  - hanya `/warehouse/picking` -> `antrianGudang` true
  - hanya `/warehouse/packing` -> `antrianGudang` true
  - `/integration-accurate/kotak-adopsi` -> `kotakAdopsi` true
  - URL bersarang di dalam grup -> tetap terdeteksi
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Implementasi `kumpulkanUrlMenu` + `badgeYangDibutuhkan`.
- [ ] **Step 4:** PASS.
- [ ] **Step 5:** Commit `feat(sidebar): predikat badge dari menu yang benar-benar tampil`.

---

### Task 2: Parameter `enabled` di tiga hook

Bentuk `(enabled = true)` bukan pola baru: `useMySpaceRoles` (`src/features/task-management/hooks.ts:65`) dan `useSubordinates` (`src/features/hris/employee/hooks/use-subordinates.ts:16`) sudah memakainya.

**Files (Modify):**

| Berkas | Perubahan | Catatan |
|---|---|---|
| `src/features/warehouse/hooks/use-warehouse-queue.ts:119` | tambah argumen ke-6 `opsi?: { enabled?: boolean; refetchInterval?: number }` | Hook ini **juga dipakai** `src/features/warehouse/components/QueueView.tsx:353` dengan 5 filter positional. Argumen opsional di akhir membuat call-site itu tidak berubah sama sekali. |
| `src/features/warehouse-sadewa/use-sadewa-actions.ts:115` | `useSadewaCetakResiPendingCount(enabled = true)` | Eksklusif sidebar (sudah diverifikasi grep). |
| `src/features/integration/accurate/hooks/use-external-edit-drafts.ts:63` | `useExternalEditDraftsNewCount(enabled = true)` | Eksklusif sidebar (sudah diverifikasi grep). |

- [ ] **Step 1 (test gagal, vitest `renderHook`):** untuk ketiga hook, dengan `enabled: false` maka `axiosInstance.get` **tidak pernah** dipanggil. Preseden `.test.tsx` renderHook sudah ada di repo (`use-attendance-setting.test.tsx`, `use-contract-history.test.tsx`).
- [ ] **Step 2:** FAIL.
- [ ] **Step 3:** Implementasi parameter di ketiga hook. Default tetap `enabled: true` supaya tak ada call-site lain yang berubah perilaku.
- [ ] **Step 4:** PASS; `pnpm exec tsc --noEmit`.
- [ ] **Step 5:** Commit `feat(warehouse,accurate): gerbang enabled untuk hook badge sidebar`.

> **Kenapa Step 1 wajib ada:** fungsi murni yang hijau di Task 1 tidak membuktikan satu pun request tercegah. Ini persis kelas kesalahan yang sudah menggigit tim di sisi Go (test fungsi murni lolos semua sementara cacat glue handler hidup). Yang diuji di sini adalah gerbangnya, bukan boolean-nya.

---

### Task 3: Sambungkan di `sidebar.tsx`

**Files (Modify):** `src/components/layout/sidebar.tsx`

- [ ] **Step 1:** Pindahkan pemanggilan `useQueueCounts` (baris 73), `useSadewaCetakResiPendingCount` (74), dan `useExternalEditDraftsNewCount` (77) ke **bawah** blok perhitungan `combinedMenus` (berakhir baris 561).
- [ ] **Step 2:** Hitung `const perluBadge = badgeYangDibutuhkan(kumpulkanUrlMenu(combinedMenus ?? []))`, teruskan ke `enabled` masing-masing hook. `combinedMenus` bisa `undefined`; perlakukan itu sebagai "belum tahu, jangan fetch".
- [ ] **Step 3:** Pastikan penempelan badge di `sidebar.tsx:596-631` tidak berubah perilakunya (nilai `undefined` tetap jatuh ke `|| 0`).
- [ ] **Step 4:** `pnpm test` penuh + `pnpm lint` bersih. Perhatikan `react-hooks/rules-of-hooks` tidak protes.
- [ ] **Step 5:** Commit `fix(sidebar): jangan fetch badge modul yang tak dimiliki pemakai`.

---

### Task 4: Longgarkan interval badge

Badge antrian gudang tidak perlu presisi 30 detik untuk orang yang tidak sedang mengerjakan antrian.

**Files (Modify):** `use-sadewa-actions.ts:124`, `use-external-edit-drafts.ts:77`, `sidebar.tsx` (opsi ke `useQueueCounts`)

- [ ] **Step 1:** Sadewa dan Kotak Adopsi: `30_000` -> `120_000` langsung di hook-nya. Aman karena keduanya eksklusif sidebar.
- [ ] **Step 2:** Queue counts: **JANGAN** ubah konstanta di hook. Halaman antrian gudang (`QueueView`) memakai hook yang sama dan 30 detik memang tepat di sana ([[WH - Fulfillment Flow & WMS Tinggarjaya]]). Sidebar mengirim `refetchInterval: 120_000` lewat opsi dari Task 2; default hook tetap 30 detik.
- [ ] **Step 3:** `pnpm test` + `lint`.
- [ ] **Step 4:** Commit `perf(sidebar): longgarkan polling badge dari 30s ke 120s`.

Hasil bersih untuk yang memang punya modulnya: dari 360 turun ke 90 request per jam per tab. Untuk yang tidak punya: nol.

---

### Task 5: `defaultOptions` QueryClient (commit terpisah, bisa di-revert sendiri)

**Files (Modify):** `src/components/tanstack.tsx:11`

```ts
new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, refetchOnWindowFocus: false },
  },
})
```

- [ ] **Step 1:** Terapkan `defaultOptions`. `retry` sengaja **tidak** disentuh: di luar lingkup dan bisa menyembunyikan kegagalan nyata.
- [ ] **Step 2:** `pnpm test` penuh + `lint`.
- [ ] **Step 3:** Commit `perf(query): default staleTime 30s + matikan refetchOnWindowFocus`.

**Kenapa ini lebih aman dari kelihatannya:** 11 hook yang benar-benar butuh refresh saat pemakai kembali ke tab (kas-toko balances, sync-status, daily invoices, daily adjustments, daily returns, listing stocks, sample shipping journals, receipts, warehouse stocks, summary report, return stats, semuanya di modul Accurate) **sudah menulis `refetchOnWindowFocus: true` secara eksplisit**. Mengubah default ke `false` tidak mematikan satu pun dari mereka. Yang berubah hanyalah query yang selama ini tak menyatakan sikap apa pun.

**Kenapa commit terpisah:** ini satu-satunya bagian yang menyentuh seluruh aplikasi sekaligus dan tidak bisa dibuktikan aman lewat test. Bila muncul keluhan "data saya tidak ter-refresh", revert satu berkas ini tanpa kehilangan Task 1 sampai 4.

Efek samping yang **diterima sadar**: avatar di header (`src/components/layout/user.tsx:47`, `useDocumentPreview` tanpa `staleTime`) berhenti diunduh ulang tiap navigasi. Itu perbaikan, bukan kerugian.

---

### Task 6: Verifikasi & regresi

- [ ] **Step 1:** `pnpm test` **penuh** -> hijau. `pnpm lint` atas `./src` -> tanpa error (warning boleh).
- [ ] **Step 2 (bukti dari browser, bukan dari test hijau):** login akun HRIS biasa, buka halaman cuti, biarkan 2 menit, pastikan Network tab **kosong** dari `/api/warehouse/fulfillment/queue/counts`, `/api/manufacture/sadewa/actions`, dan `/api/integration/accurate/external-edit-drafts`.
- [ ] **Step 3 (regresi, yang paling penting):** login akun gudang Tinggarjaya -> badge Picking/Packing **masih muncul dengan angka benar**. Login admin gudang Sadewa ([[WH - Warehouse Sadewa]]) -> badge Pengemasan Sadewa muncul, tapi queue counts Tinggarjaya **tidak** ditembak. Login akun finance -> badge Kotak Adopsi muncul.
- [ ] **Step 4:** Buat PR ke `main`.

---

## Catatan

- **Yang sengaja tidak dikerjakan:** empat query `/api/employee/me*` di sidebar sudah ber-`staleTime` 5 sampai 10 menit dan tidak polling, jadi sudah sehat. Prefetch `next/link` juga dibiarkan (lihat bagian Temuan).
- **Efek samping kecil yang diterima:** saat `useMenuHidden` masih loading, `menuTersembunyi` kosong sehingga menu tampil apa adanya dan badge bisa sempat ter-`enabled` satu kali sebelum menjadi `false`. Satu request, dan hanya untuk pemakai yang memang punya menunya.
- **Risiko `staleTime` global:** data bisa terasa basi maksimal 30 detik. Alur "ubah lalu lihat hasilnya" tidak terpengaruh karena `invalidateQueries` setelah mutasi tetap menandai query stale terlepas dari `staleTime`.
- **Gap dokumentasi yang ditemukan:** [[APP - Web ERP]] mendeskripsikan stack (TanStack Query + axios) dan sidebar berbasis role, tapi **belum mencatat konvensi data-fetching sama sekali**. Tidak ada aturan soal polling, `staleTime`, maupun kewajiban menggerbangi hook yang hidup di sidebar. Ketiadaan aturan itulah yang membuat bug ini bisa tumbuh tanpa ada yang menyadari. Tutup di `/sync-docs`: tambahkan satu bagian konvensi di [[APP - Web ERP]], dan promosikan satu kalimat ke ingatan tim, yaitu **hook di sidebar berarti hook di setiap halaman, jadi wajib ber-`enabled`**.

## Self-review

- Rencana ini **tidak menyimpang** dari dokumen arsitektur mana pun: tak ada aturan vault soal cache policy frontend. Yang ada adalah gap dok, dicatat di Catatan.
- Placeholder: tidak ada. Semua path + baris konkret dan sudah diverifikasi ke kode pada 2026-08-07, bukan diingat.
- Pemakaian lain ketiga hook sudah dicek lewat grep sebelum memutuskan mana yang boleh diubah konstantanya (`useQueueCounts` punya call-site kedua, dua lainnya tidak).
- Klaim "11 hook sudah eksplisit `refetchOnWindowFocus: true`" berasal dari grep, bukan perkiraan. Ini yang menurunkan risiko Task 5 dari tebakan menjadi terukur.
- Urutan task disusun supaya tiap commit berdiri sendiri dan bisa di-revert terpisah; Task 5 sengaja paling belakang karena paling luas dampaknya dan paling sulit dibuktikan lewat test.
