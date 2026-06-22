## Notes

*This feature was added as a complement to the Attendance System. Shift Exchange allows employees to request swapping their work/off-duty days within the same month, subject to a multi-level approval workflow. The feature is particularly relevant for shift-based employees (Security, Production, Host Live) who may also request a different shift time on the exchanged day.*

## Background

* Employees sometimes need to work on their scheduled day off (e.g. a holiday) and take a different day off in return, or shift-based employees want to change which shift slot they work on a specific date.
* Previously this was handled informally through HR without a traceable audit trail.
* The shift exchange feature provides a formal digital request → approval → automated attendance adjustment pipeline.
* Available for **all employees**, but shift-based employees (Security, Production, Host Live) get an additional option to specify a different `exchange_work_time` (shift slot) on the target date.

## Use Cases

1. **Static schedule employee** — works on a national holiday (work_date) and gets a working day off in return (exchange_date). The two dates must be in the same month.
2. **Shift-based employee (same-day)** — requests a shift time change on a single day (work_date == exchange_date). For example, swapping from the morning shift to the night shift.
3. **Shift-based employee (different-day)** — same as case 1, but can additionally pick which shift slot to work via `exchange_work_time`.

## Data Model

Collection: `shift_exchange_request` (inside attendance database)

```
ShiftExchangeRequest {
  _id:                ObjectID
  employee_id:        string
  full_name:          string
  position:           string
  department:         string

  work_date:          Date         // The day the employee will work (originally off)
  exchange_date:      Date         // The day the employee takes off (originally working)
  exchange_work_time: WorkTime?    // Optional — only for shift-based employees
                                   // { start: "HH:MM", end: "HH:MM" }

  reason:             string

  status:             ReviewStatus // Derived from review_1 + review_2
  review_1:           ReviewData   // First reviewer (supervisor / department head / HR)
  review_2:           ReviewData   // Second reviewer (HR / Direktur), may be empty

  metadata:           Metadata     // created_at, created_by, updated_at, updated_by
}
```

Reuses existing `ReviewData`, `ReviewStatus`, and `WorkTime` types from the attendance domain.

### Review Status Resolution

Status is computed from the two reviews via `ResolveShiftExchangeStatus()`:
- If **either** reviewer rejects → `Ditolak`
- If **either** reviewer ignores → `Diabaikan`
- If review_2 is **empty** and review_1 is approved → `Disetujui`
- If **both** approved → `Disetujui`
- Otherwise → `Menunggu persetujuan`

## Reviewer Determination

Reviewers are determined dynamically based on the requester's role:

| Requester Role         | Review 1                      | Review 2                 |
|------------------------|-------------------------------|--------------------------|
| Regular employee       | Department head (by dept name)| HR Department            |
| Supervisor             | HR Department                 | Direktur                 |
| HR staff               | HR Department head            | *(none)*                 |
| HR supervisor          | Direktur                      | *(none)*                 |

## Business Rules / Validations

- `exchange_date` must be **at least 2 days** from today
- `work_date` and `exchange_date` must be in the **same month**
- `exchange_work_time` is **only** allowed for shift-based employees (Security, Production, Host Live)
- If provided, `exchange_work_time` must match one of the allowed shift slots for the employee's schedule type:
  - Security: `07:00-19:00`, `19:00-07:00`
  - Production: `08:00-16:00`, `16:00-00:00`, `00:00-08:00`
  - Host Live: `07:00-15:00`, `12:00-20:00`, `16:00-24:00`, `08:00-16:00`
- For non-shift (static) employees on the front-end:
  - `work_date` must be a holiday / red date (OFF-DUTY, NATIONAL_HOLIDAY, COMPANY_HOLIDAY, etc.)
  - `exchange_date` must NOT be a holiday / red date
  - `work_date` and `exchange_date` cannot be the same day

## API Endpoints

All routes are under the **Attendance Service** (`/api/attendance/shift-exchange/`), proxied through the API Gateway.

| Method  | Route                        | Description                                      |
|---------|------------------------------|--------------------------------------------------|
| POST    | `/shift-exchange/create`     | Create a new shift exchange request               |
| GET     | `/shift-exchange/view`       | List requests (supports `?as=reviewer/reviewed`, `?filter=ongoing/past`, `?id=`, `?search=`) |
| PATCH   | `/shift-exchange/review`     | Approve or reject a request (body: `{ id, status, notes? }`) |
| PATCH   | `/shift-exchange/cancel`     | Cancel own pending request (query: `?id=`)        |

### View endpoint query parameters

- `as=reviewer` — show requests where the caller is the current reviewer (pending)
- `as=reviewed` — show requests the caller has already reviewed
- `filter=ongoing` — requests that are still active or recently updated
- `filter=past` — requests with final statuses or stale + exchange_date passed
- `id=<hex>` — fetch a single request by ObjectID
- `search=<term>` — search by employee_id or full_name

## Approval Flow

```
Employee creates request
    ↓
Notify employee (confirmation) + Notify Review 1 (new request)
    ↓
Review 1 approves?
    ├── Yes, has Review 2 → Notify Review 2, wait
    │       ↓
    │   Review 2 approves?
    │       ├── Yes → Status: Approved → Apply to attendance
    │       └── No  → Status: Rejected → Notify employee
    ├── Yes, no Review 2 → Status: Approved → Apply to attendance
    └── No → Status: Rejected → Notify employee
```

## Post-Approval: Attendance Impact (`applyApprovedShiftExchange`)

When a shift exchange is fully approved, the system automatically modifies attendance entries:

### Same-day exchange (work_date == exchange_date)
- Updates the existing attendance entry's `work_time` to the new `exchange_work_time`
- Comment: "Shift time changed (approved shift exchange)"

### Different-day exchange (work_date ≠ exchange_date)

**work_date** (originally off, now working):
- If an attendance entry exists → update status to `Tepat Waktu`, set comment, optionally update `work_time`
- If no entry exists → **insert** a new `AttendanceEntries` document with the employee data, schedule, and work time resolved from the exchange_date's original schedule

**exchange_date** (originally working, now off):
- If an attendance entry exists → update status to `Replacement Day Off`
- If no entry exists → **insert** a new entry with status `Replacement Day Off`

### Impact on Schedule Calendar View

The `getEmployeeScheduleDateRange()` function in `func.go` also incorporates approved shift exchanges when building the employee's calendar view. It fetches approved `ShiftExchangeRequest` documents in the date range and swaps the schedule/work-time display accordingly, including a `REPLACEMENT_DAY_OFF` schedule format for the exchanged day.

## Notifications

All notifications use the push notification system (FCM + inbox) via notification-service:

| Event                   | Recipient          | Channel        |
|-------------------------|--------------------|----------------|
| Request created         | Requester          | Personal       |
| New request for review  | Reviewer (by ID)   | Personal       |
| Awaiting HR review      | HR Department      | Department     |
| Request approved        | Requester          | Personal       |
| Request rejected        | Requester          | Personal       |

## Frontend Implementation

### Pages

| Route                          | Page                  | Description                        |
|--------------------------------|-----------------------|------------------------------------|
| `/hris/shift-exchange`         | My Requests           | Employee views/cancels own requests |
| `/hris/shift-exchange/approvals` | Approvals           | Reviewer approves/rejects requests |

### Feature Module Structure

```
src/features/hris/shift-exchange/
├── components/
│   ├── approval-actions.tsx      — Approve/Reject dialog buttons
│   ├── approval-progress.tsx     — Visual review step indicators
│   ├── request-form.tsx          — New request form with calendar schedule view
│   └── review-notes.tsx          — Dialog to view reviewer notes
├── hooks/
│   ├── use-fetch.ts              — React Query hooks for fetching requests
│   └── use-upsert.ts            — Mutations for create, review, cancel
├── lib/
│   └── schedule.ts              — Schedule label/color/format utilities
├── schemas/
│   └── shift-exchange.ts        — Zod validation schemas
└── types/
    └── shift-exchange.ts        — TypeScript interfaces
```

### Key Frontend Behaviors

- Request form shows an **interactive calendar** with color-coded schedule modifiers (morning/night/off-duty/holiday) pulled from the employee's own schedule
- For shift-based employees, the form shows a **shift time selector** dropdown with available time slots
- Non-shift employees have client-side validation enforcing work_date must be a red date and exchange_date must not be
- Approval progress shows a visual pipeline with colored status indicators per reviewer
- Pending review count is polled every 60 seconds for the sidebar badge
- All list tables use client-side pagination with page size options: 3 (default), 5, 10, 50

## Requirements

- [x] Employees master data (look up reference, supervisor data)
- [x] Attendance database read/write access
- [x] Notification service integration (FCM + inbox)
- [x] Employee schedule data (for calendar view and validation)

## Dependencies

- [x] [[HRIS - Attendance System]]
- [x] [[Microservices - Attendance Service]]
- [x] [[HRIS - Big Pictures]]
