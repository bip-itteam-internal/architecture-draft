## Catatan

*Panduan proses **Scrum & pengembangan** tim ERP Bharata — cara tim bekerja dari ide fitur sampai rilis. Ini dokumen **proses/PM**, bukan arsitektur sistem.*

![[scrum-cycle.jpeg]]

## Peran

| Peran | Pengisi | Tugas |
|---|---|---|
| **Product Owner** | Lead Departments (SPV) | Menentukan & memprioritaskan fitur yang dibutuhkan |
| **Scrum Master** | Fani Triastowo | Memfasilitasi proses, breakdown, dan (sementara) QA |
| **Development Team** | BE/FE/DevOps | Mengerjakan sprint backlog |
| **QA** | sementara oleh Scrum Master / Product Owner | Verifikasi sebelum rilis (target: QA Dev terpisah) |

## Alur Scrum

### 1. Product Backlog
Daftar **fitur** yang dibutuhkan (bukan task/issue). PO & Scrum Master berdiskusi soal kebutuhan; bisa berupa tim (>1 orang).

### 2. Sprint Planning
Breakdown fitur jadi task-task. Dilakukan tiap akan mulai sprint (mis. 1–2 minggu) bila sprint backlog sebelumnya selesai.

### 3. Sprint Backlog
Task untuk sprint berjalan. Perlu **koordinasi langsung dengan User** terkait fitur agar iterasi cepat ter-deliver.

### 4. Daily Meeting
Tidak harus tiap hari — dilakukan saat ada kendala atau milestone penting. Catatan bisa disisipkan sebagai komentar di masing-masing sprint backlog item.

### 5. Product Increment
Story yang selesai langsung **merge ke `dev` branch** untuk testing.

## Definition of Done

- Kode selesai sesuai acceptance criteria
- Lolos test (unit/integration) + **QA** (sementara oleh SM/PO)
- Ter-merge & ter-deploy tanpa error

## Branching & Deployment

- Alur branch: **feature branch → `dev` (testing) → `main` (production)**
- **CI/CD sudah tersedia** — deploy otomatis saat push ke `main` (GitHub Actions self-hosted runner; Codemagic untuk mobile). Detail: [[IT - CI-CD]]
- QA Dev terpisah masih menjadi target (saat ini QA oleh Scrum Master/Product Owner)

## Tools

- **Task & sprint tracking**: [[APP - Dynamic Task Tracker]] (kini diposisikan sebagai IT Helpdesk/ticketing; backend [[Microservices - Task Management Service]])
- **Deployment**: [[IT - CI-CD]]

## Contoh Backlog (snapshot historis)

> Tabel berikut adalah **contoh/snapshot awal** (sprint task-management). Item-item ini sebagian besar **sudah diimplementasikan** — disimpan sebagai ilustrasi format, bukan backlog terkini.

### Product Backlog (contoh)
| No. | Name | Description |
| --- | --- | --- |
| 1. | Management Tasks | Task diatur di sini, target sesuai KPI & insentif |
| 2. | Management Space | Space = pemisah antar project; tiap departemen minimal 1 space |
| 3. | Login SSO menggunakan akun karyawan | Tidak perlu akun baru tiap aplikasi internal (lihat [[CORE - SSO Flow]]) |

### Sprint Backlog (contoh)
| ID | Name | Priority | Type | Story points | Sprints | Deps | Assignee |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SB-001 | Menampilkan list task yang sedang dikerjakan | Core | BE | 8 | 1 | - | Fahrurozi |
| SB-002 | Menampilkan list task yang sudah selesai | Core | BE | 8 | 1 | - | Pero Roberto |
| SB-003 | Konversi task selesai menjadi KPI sesuai target | Core | BE | 8 | 1 | SB-002 | Pero Roberto |
