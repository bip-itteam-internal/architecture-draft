## Deskripsi

Database ini akan menyimpan segala hal tentang file sesuai dengan access key yang diberikan untuk direktori tersebut, ini akan menjadi file server utama untuk seluruh aplikasi

## Fitur

Kebutuhan dasar file server seperti upload, preview, download, delete, move, dan copy file, dengan dukungan penuh untuk semua tipe dokumen.

Semua aksi tersebut membutuhkan access key yang sesuai dengan direktori mana yang dapat diakses, saat ini kami memiliki direktori MinIO seperti berikut:
- **employee/** - Tempat seluruh dokumen database karyawan berada
- **attendance/** - Tempat dokumen kehadiran, seperti dokumen cuti, sakit, dan liburan yang perlu dicatat
- **task/** - Dukungan eksternal untuk menyimpan file task management

## Access Key

Access key dibagi menjadi 2 tipe, sesuai dengan penggunaannya, gunakan sesuai kebutuhan. Pada sistem backend Anda akan memiliki access key penuh berupa read dan write untuk aksi Anda, dan pada frontend Anda akan diberikan read-only key untuk preview dan download

Daftar access key beserta spesifikasinya:
1. Read dan write key (ukuran hex 12byte)
2. Read-only key (separuh truncation dari read dan write key)

Key ini juga dibatasi pada bagian mana yang dapat diaksesnya di direktori MinIO, contohnya saat ini kami memiliki 3 full access key untuk direktori yang tercantum pada fitur di atas, dan 3 read-only key untuk direktori tersebut juga
