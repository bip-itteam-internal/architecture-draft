![[scrum-cycle.jpeg]]

Product owner: Lead Departments (Spv)
Scrum Master: Fani Triastowo

### Product backlog
Product backlog hanya berupa daftar fitur yang dibutuhkan. Tidak berbentuk task atau issue.
Ditahap ini, product owner dan scrum master berdiskusi terkait fitur yang dibutuhkan. Tidak menutup kemungkinan, product owner dan scrum master berupa tim dan lebih dari 1 orang.

| No. | Name                                | Description                                                                           |
| --- | ----------------------------------- | ------------------------------------------------------------------------------------- |
| 1.  | Management Tasks                    | Task di atur di sini dan target sesuai KPI dan insentif                               |
| 2.  | Management Space                    | Space adalah pemisah antar project. setiap departement harus memiliki minimal 1 space |
| 3.  | Login SSO menggunakan akun karyawan | User tidak perlu membuat akun baru untuk setiap aplikasi internal perusahaan          |

### Sprint planning
Sprint planning adalah proses breakdown task-task yang akan dilakukan
Sprint planning dilakukan setiap kali akan melakukan sprint (misal 1 atau 2 minggu sekali) apabila sprint backlog di sprint sebelumnya telah selesai

### Sprint backlog
Saat sprint terjadi, perlu koordinasi langsung dengan User terkait fitur sehingga iterasi menjadi cepat ter-deliver

| ID     | Name                                                       | Priority | Type | Story points | Sprints | Deps   | Assignee     |
| ------ | ---------------------------------------------------------- | -------- | ---- | ------------ | ------- | ------ | ------------ |
| SB-001 | Menampilkan list task yang sedang dikerjakan               | Core     | BE   | 8            | 1       | -      | Fahrurozi    |
| SB-002 | Menampilkan list task yang sudah selesai                   | Core     | BE   | 8            | 1       | -      | Pero Roberto |
| SB-003 | Konversi task yang sudah selesai menjadi KPI sesuai target | Core     | BE   | 8            | 1       | SB-002 | Pero Roberto |

### Daily meeting
Daily meeting tidak harus setiap hari, dilakukan apabila ada kendala atau milestone penting.
Catatan daily meeting bisa di sisipkan di comment di masing-masing sprint backlog

### Product increment
Story yang sudah selesai langsung di merge ke dev branch untuk langsung dilakukan testing. Dibutuhkan CI/CD dan QA Dev (untuk sementara QA dilakukan oleh Scrum Master atau Product Owner).  