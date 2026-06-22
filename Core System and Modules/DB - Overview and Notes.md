## Backup Database

Backup dilakukan untuk database-database penting, mingguan setiap hari Senin pukul 4:15 pagi

Saat ini backup hanya berada di direktori project mesin lokal, hal ini perlu ditingkatkan agar dapat mengunggah backup ke layanan cloud, sehingga kita memiliki cadangan untuk fallback jika mesin lokal atau VM crash dan tidak dapat dipulihkan

## Sinkronisasi Collection

Dalam database akan ada banyak collection dan beberapa collection tersebut tidak secara native dimiliki oleh database tersebut, oleh karena itu collection tersebut perlu di-fetch dari database asalnya jika memungkinkan pada setiap server restart, berbasis cron, atau melalui aksi berbasis subscription

Contoh dapat dilihat di bawah ini

![[database-collection-ownership-example.png]]

Hal ini diperlukan untuk menegakkan kepemilikan pada setiap database dengan benar dan hanya memperbarui collection yang dimiliki oleh pemiliknya, sementara yang lain dapat melakukan fetch collection data secara berkala atau segera jika diperlukan sesuai pertimbangan sistem

Selain itu, manfaat dari metode ini adalah lookup atau query lintas database tidak lagi diperlukan karena masing-masing sudah memiliki informasinya sendiri pada collection yang dibutuhkan. Jika salah satu service down, service lain tetap dapat bekerja dengan baik menggunakan data collection yang sudah di-fetch sebelumnya

## Replikasi Database

Replikasi database diperlukan jika kita ingin mengekspos database untuk penggunaan eksternal oleh aplikasi lain, di mana ia hanya akan memiliki akses **READ**

Saat ini ini hanya aktif untuk **Employee-MongoDB** dan cluster slave/secondary yang digunakan oleh **Task Management**

Aturan replikasi secara eksplisit menyatakan bahwa cluster tidak dapat diubah untuk primary karena saat ini kita belum memiliki dynamic cluster picker untuk aksi tersebut

## Daftar Database dan Collection-nya

**Employee-MongoDB**
- PersonalData
- PersonalDocs
- WorkData
- WorkDocs
- WorkSchedule
- SystemAuthentication
- CompanyWorkSchedule (Sync from Attendance-Service)
- CompanyHoliday

**Attendance-MongoDB**
- AttendanceEntries
- CompanyWorkSchedule
- CompanyGroupRotation
- CompanyHoliday
- CompanyWifi
- FingerprintExport
- Guestbook
- WorkSchedule (Sync from Employee-Service)
- LeaveRequest

**Notification-MongoDB**
- Inbox
- Article
- Splash
