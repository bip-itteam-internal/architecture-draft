# Finance System – Penghapusan Data Duplikat di Finance Lama (Java)

> **Status**: ⚠️ **Implemented (ada catatan)** — prosedur manual/ad hoc, dipakai selama sistem [[Finance - Bridging App]] (Java/PostgreSQL) masih berjalan berdampingan dengan [[Finance - Bridging App New Golang]]. Belum ada tooling otomatis; eksekusinya tetap manusia.

## Deskripsi

*Prosedur untuk menghapus data transaksi income yang salah/duplikat di database Finance lama, biasanya terjadi karena file report marketplace (mis. TikTok) ter-upload lebih dari sekali. Query DELETE di-generate dari kolom Order ID pada file Excel report menggunakan Python di Google Colab, lalu dijalankan manual ke database.*

- Stack: Python (pandas) di Google Colab untuk generate query → dieksekusi manual via database management tool (mis. DBeaver/pgAdmin) ke PostgreSQL Finance lama.
- Terkait: [[Finance - Bridging App]] (sistem Java yang datanya dibersihkan)

## Kapan Dipakai

- File report marketplace ter-upload dobel sehingga income tercatat duplikat.
- Perlu hapus baris transaksi tertentu berdasarkan Order ID sebelum re-upload/re-sync yang benar.

## Tabel & Kolom Acuan

| Tabel            | Kolom key            | Sumber nilai di Excel (sheet "Order details") |
| ----------------- | --------------------- | ---------------------------------------------- |
| `income`          | `reference_order_id`  | Related order ID                               |
| `income_tiktok`   | `related_order_id`    | Related order ID                               |

## Langkah-langkah

### 1. Prompt (generate script Python di Google Colab)

Prompt yang dipakai untuk minta AI (Claude/ChatGPT) generate script Python-nya:

```
Buatkan generate SQL di Python Google Colab.

File: "/content/4. Tiktok Beautyhacks.co.id 1-9 Juli  CV Pure Skin Lux (15.7).xlsx"
Sheet: "Order details"
Kolom: "Related order ID"

Ambil semua nilai unik di kolom tersebut, lalu buatkan query DELETE untuk tiap order ID ke:

SELECT * FROM income WHERE reference_order_id = '<order_id>';
SELECT * FROM income_tiktok WHERE related_order_id = '<order_id>';

(pakai DELETE, bukan SELECT). Tulis semua query ke file delete_income.sql di /content,
lalu tampilkan jumlah order ID yang ditemukan.
```

**Contoh hasil generate** (untuk order ID `584850717389129638`, isi `delete_income.sql`):

```sql
-- income
DELETE FROM income WHERE reference_order_id = '584850717389129638';

-- income_tiktok
DELETE FROM income_tiktok WHERE related_order_id = '584850717389129638';
```

### 2. Script Python (copy ke cell Google Colab)

```python
import pandas as pd

# ==== KONFIGURASI — sesuaikan tiap kali dipakai ====
FILE_PATH = "/content/4. Tiktok Beautyhacks.co.id 1-9 Juli  CV Pure Skin Lux (15.7).xlsx"
SHEET_NAME = "Order details"
COLUMN_NAME = "Related order ID"
OUTPUT_SQL = "/content/delete_income.sql"

TABLES = [
    ("income", "reference_order_id"),
    ("income_tiktok", "related_order_id"),
]

df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
order_ids = df[COLUMN_NAME].dropna().astype(str).str.strip().unique()
order_ids = [oid for oid in order_ids if oid]

with open(OUTPUT_SQL, "w") as f:
    for table, column in TABLES:
        f.write(f"-- {table}\n")
        for oid in order_ids:
            f.write(f"DELETE FROM {table} WHERE {column} = '{oid}';\n")
        f.write("\n")

print(f"{len(order_ids)} order ID ditemukan. Query tersimpan di {OUTPUT_SQL}")
```

Sanity check sebelum download — jumlah `order_ids` harus masuk akal dibanding jumlah baris di Excel (bandingkan dengan `len(df)`); kalau jauh lebih kecil, cek apakah kolom/sheet-nya salah pilih.

### 3. Download hasil SQL

Tambahkan di cell berikutnya, lalu jalankan:

```python
from google.colab import files
files.download(OUTPUT_SQL)
```

### 4. Eksekusi ke database

1. Buka database management tool (DBeaver/pgAdmin/dll), connect ke database Finance lama.
2. **Sebelum DELETE**, jalankan dulu versi SELECT dari query yang sama untuk verifikasi jumlah baris yang akan terhapus sesuai ekspektasi, contoh:
   ```sql
   SELECT * FROM income WHERE reference_order_id = '584850717389129638';
   SELECT * FROM income_tiktok WHERE related_order_id = '584850717389129638';
   ```
3. Paste isi `delete_income.sql`, jalankan dalam satu transaksi (`BEGIN` ... cek row count ... `COMMIT`/`ROLLBACK`) agar bisa dibatalkan kalau row count tidak sesuai.

## Catatan / Peringatan

- Operasi ini **destruktif** — pastikan sudah verifikasi dengan SELECT dan idealnya ada backup/snapshot database sebelum menjalankan DELETE massal.
- Tidak ada validasi otomatis bahwa Order ID di Excel benar-benar duplikat di database — tanggung jawab verifikasi ada di operator yang menjalankan query.
- Prosedur ini spesifik untuk data di Finance lama (Java/PostgreSQL); tidak berlaku untuk sistem baru [[Finance - Bridging App New Golang]].

## Dependensi & Integrasi

- [[Finance - Bridging App]] — sistem & database yang dibersihkan
- [[Finance - Bridging App New Golang]] — pengganti sistem ini, target migrasi

## Dokumen Terkait

- [[Finance - Bridging App]]
- [[Finance - Big Pictures]]
