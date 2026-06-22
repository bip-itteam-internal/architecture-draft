## Notes

*This feature was added as a complement to the Attendance System. Attendance Correction allows employees to request clock-in/out corrections for days where they forgot to clock in, clock out, or both. Clock times are automatically filled from the employee's work schedule upon approval — no manual time input is required.*

## Background

* Employees occasionally forget to clock in or clock out, resulting in incomplete attendance records ("Tanpa Keterangan" / Alpha status).
* Previously, corrections were handled informally through HR without a traceable audit trail.
* The attendance correction feature provides a formal digital request, multi-level approval, and automated attendance fix pipeline.
* Clock times are derived from the employee's scheduled work time (`WorkTime.Start` / `WorkTime.End`), ensuring corrections are always consistent with the assigned shift.

## Use Cases

1. **Forgot clock-in** — Employee was present but forgot to clock in. Correction fills `clock_in` from schedule start time.
2. **Forgot clock-out** — Employee was present but forgot to clock out. Correction fills `clock_out` from schedule end time.
3. **Forgot both** — Employee was present the entire day but neither clocked in nor out. Correction fills both from schedule.

## Data Model

Collection: `correction_request` (inside attendance database)

```
AttendanceCorrectionRequest {
  _id:              ObjectID
  employee_id:      string
  full_name:        string
  position:         string
  department:       string

  attendance_id:    ObjectID       // Reference to the attendance entry being corrected
  attendance_date:  Date           // The date of the attendance entry
  work_time:        WorkTime       // { start: "HH:MM", end: "HH:MM" } — snapshot of schedule

  correction_type:  CorrectionType // "checkin" | "checkout" | "both"
  reason:           string

  status:           ReviewStatus   // Derived from review_1 + review_2
  review_1:         ReviewData     // First reviewer (department supervisor or HR supervisor)
  review_2:         ReviewData     // Second reviewer (HR department), may be empty

  metadata:         Metadata       // created_at, created_by, updated_at, updated_by
}
```

Reuses existing `ReviewData`, `ReviewStatus`, `WorkTime`, and `CorrectionType` types from the attendance domain.

### Correction Type Labels

| Value      | Label               |
|------------|---------------------|
| `checkin`  | Clock-in            |
| `checkout` | Clock-out           |
| `both`     | Clock-in & Clock-out|

### Review Status Resolution

Status is computed from the two reviews via `ResolveLeaveRequestStatus(review_1, review_2)`:
- If **either** reviewer rejects -> `Ditolak`
- If review_2 is **empty/not applicable** and review_1 is approved -> `Disetujui`
- If **both** approved -> `Disetujui`
- Otherwise -> `Menunggu persetujuan`

Additionally, employees can cancel their own pending requests, which sets `status` to `Dibatalkan`.

## Reviewer Determination (4 Cases)

Reviewers are determined dynamically based on the requester's role and department. Supervisor detection uses `getSupervisorData(department)` to resolve actual supervisors.

| Case | Requester Role     | Review 1                          | Review 2        | Notes                                   |
|------|--------------------|-----------------------------------|-----------------|-----------------------------------------|
| 1    | Regular employee   | Department supervisor (dept-level)| HR Department   | Standard 2-tier flow                    |
| 2    | Supervisor (non-HR)| *(skipped)*                       | HR Department   | Skip review_1, go directly to HR       |
| 3    | HR staff           | HR supervisor (dept-level)        | *(none, FINAL)* | SPV HR approval is final               |
| 4    | HR supervisor      | *(auto-approved)*                 | *(none)*        | Immediately applied, no approval needed |

### Key Rules

- **Self-approval prevention**: HR staff cannot approve their own correction request. The filter excludes requests where `employee_id == reviewer's employee_id`.
- **Department-level routing**: For cases 1 and 3, `review_1` is assigned at the department level (`review_1.full_name = department`, `review_1.employee_id = ""`). Any supervisor in that department can pick up the review.
- **Case 3 is FINAL**: When SPV HR approves an HR staff request, the correction is applied immediately without going through review_2.
- **Case 4 auto-apply**: SPV HR's own requests are auto-approved and applied at creation time.

## API Endpoints

All routes are under the **Attendance Service** (`/api/attendance/correction/`), proxied through the API Gateway.

| Method | Route                    | Description                                           |
|--------|--------------------------|-------------------------------------------------------|
| POST   | `/correction`            | Create a new correction request                       |
| GET    | `/correction/mine`       | List the employee's own correction requests            |
| GET    | `/correction`            | List requests for review (`?as=reviewer` or `?as=reviewed`) |
| PATCH  | `/correction/:id/cancel` | Cancel own pending request                            |
| PATCH  | `/correction/:id/review` | Approve or reject a request (body: `{ status, notes? }`) |

### View endpoint query parameters

- `as=reviewer` — show requests where the caller is the current reviewer (pending review)
- `as=reviewed` — show requests the caller has already reviewed, **including canceled requests** that were assigned to this reviewer

## Approval Flow

```
Employee creates request
    |
    |-- Case 4 (HR SPV): Auto-approve + apply correction immediately
    |
    |-- Case 3 (HR Staff): Notify HR SPV -> SPV approves? -> Apply (FINAL)
    |
    |-- Case 2 (Non-HR SPV): Notify HR dept -> HR approves? -> Apply
    |
    |-- Case 1 (Regular): Notify dept SPV -> SPV approves?
            |-- Yes -> Notify HR dept -> HR approves? -> Apply
            |-- No  -> Rejected -> Notify employee
```

## Post-Approval: Attendance Impact (`applyCorrectionToEntry`)

When a correction is fully approved, the system automatically modifies the referenced attendance entry:

- **Clock-in correction**: Sets `clock_in` to `WorkTime.Start`, `clock_in_method` to "Website", `status` to "Tepat Waktu", `late_hour` to 0
- **Clock-out correction**: Sets `clock_out` to `WorkTime.End`, `clock_out_method` to "Website"
- **Both**: Applies both of the above
- Adds comment: `"Koreksi disetujui #<correction_id>"`
- Updates metadata with the approver's ID

## Review Filter Logic (`buildCorrectionReviewFilter`)

The filter determines which requests a reviewer can see:

**Pending tab** (`reviewed=false`):
- Requests where `review_1.employee_id` matches the reviewer AND `review_1.status` is waiting
- Requests where `review_1` is department-level and matches the reviewer's department (excluding own requests)
- For HR department: requests where `review_2.status` is waiting (excluding own requests)
- Excludes requests with `status = "Dibatalkan"`

**Reviewed tab** (`reviewed=true`):
- Requests where reviewer has already acted on review_1 or review_2
- Department-level matches with non-waiting review statuses
- For HR department: review_2 matches with completed statuses
- **Canceled requests**: requests that were assigned to this reviewer but canceled by the employee before review

## Notifications

All notifications use the push notification system (FCM + inbox) via notification-service:

| Event                          | Recipient       | Channel    |
|--------------------------------|-----------------|------------|
| SPV approves regular employee  | HR Department   | Department |
| SPV approves HR staff (FINAL)  | Employee        | Personal   |
| HR approves                    | Employee        | Personal   |
| Any reviewer rejects           | Employee        | Personal   |

## Frontend Implementation

### Pages

| Route                                   | Page       | Description                             |
|-----------------------------------------|------------|-----------------------------------------|
| `/hris/attendance-correction`           | My Requests| Employee views attendance + corrections  |
| `/hris/attendance-correction/approvals` | Approvals  | Reviewer approves/rejects requests       |

### Feature Module Structure

```
src/features/hris/attendance-correction/
├── components/
│   ├── correction-actions.tsx    — Approve/Reject dialog buttons
│   └── modal-create.tsx          — New correction request modal
├── hooks/
│   └── use-correction.ts        — React Query hooks for fetch/create/cancel/review
├── schemas/
│   └── correction.ts            — Zod validation schema
└── types/
    └── correction.ts            — TypeScript interfaces and constants
```

### Key Frontend Behaviors

- My Requests page has two views: **table** and **calendar** (interactive calendar with color-coded attendance status)
- Calendar view shows detail cards (clock-in, clock-out, schedule) when a date is selected
- Correction request modal auto-detects missing clock-in/out and pre-selects the correction type
- Employees can only request corrections for days where clock-in or clock-out is missing
- No manual time input — the modal explains that times will be auto-filled from the shift schedule upon approval
- Approvals page has tabs: **Menunggu Review** (pending) and **Sudah Direview** (reviewed, includes canceled)
- Reviewer sees the requester's work schedule ("Jam Kerja" column) for context
- All list tables use client-side pagination with page size options: 3 (default), 5, 10, 50

## Requirements

- [x] Employees master data (look up reference, supervisor data)
- [x] Attendance database read/write access
- [x] Notification service integration (FCM + inbox)
- [x] Employee schedule data (for auto-filling clock times)

## Dependencies

- [x] [[HRIS - Attendance System]]
- [x] [[HRIS - Shift Exchange]] *(shared review patterns and notification infrastructure)*
- [x] [[Microservices - Attendance Service]]
- [x] [[HRIS - Big Pictures]]
