

## Deskripsi

*OCR Document adalah **shared service lintas-fitur** (bukan khusus General Affairs) — penyedia kapabilitas **OCR + dokumen-intelligence (RAG)** yang dikonsumsi berbagai subsistem ERP.*

- **Status**: 🟡 Konsep / Draft — layanan OCR + dokumen-intelligence (RAG) lintas-fitur; konsumen sebagian besar masih fase lanjut (perlu verifikasi implementasi ke kode).

## Konsumen / Dipakai oleh

- [[GA - Inventory Management]] — membaca dokumen (pembelian/kedatangan)
- [[GA - Waste Management]] — dokumen kepatuhan/manifest
- [[HRIS - Recruitment]] — OCR fallback untuk CV hasil scan (AI CV screening — fase lanjut)
- *Kandidat berikutnya:* [[GA - Procurement System]] (form pengajuan/tanda terima), [[HRIS - Leave Request]] (surat keterangan dokter), [[Manufacture - Stock & Material Management]] (berita acara / dokumen supplier)

---

## Temuan terukur 2026-09-08

> Bagian ini ditambahkan setelah blueprint di bawahnya, dan **mengoreksi sebagian asumsinya**.
> Blueprint (bagian 1 sampai 8) ditulis sebelum ada pengukuran ke infrastruktur nyata; ia
> dipertahankan apa adanya sebagai riwayat pertimbangan. Bila keduanya bertentangan, **bagian
> ini yang berlaku**, karena angkanya diukur.

### Blueprint ini mencampur DUA kapabilitas, dan itu yang membuatnya tampak mahal

Bagian 1 sampai 8 merancang **RAG document Q&A**: embedding, vector store, retrieval, LLM lokal
via Ollama. Itu kapabilitas untuk menjawab pertanyaan bebas atas korpus dokumen.

Yang sebenarnya diminta lima dari enam konsumen di atas adalah **ekstraksi terstruktur**: baca
satu dokumen, keluarkan field yang sudah ditentukan (nomor faktur, supplier, total; atau nama
pelamar, pendidikan, pengalaman). Itu tidak butuh embedding, tidak butuh vector store, dan tidak
butuh Ollama. Menggabungkan keduanya jadi satu proyek membuat kebutuhan yang sederhana ikut
menanggung ongkos yang tidak diperlukannya.

**Pisahkan keduanya.** Ekstraksi terstruktur bisa jalan sekarang; RAG Q&A belum punya konsumen
yang menyebutkan pertanyaan yang ingin dijawabnya, dan sesuai [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]]
itu belum lolos gerbang.

### Ekstraksi terstruktur sudah bisa jalan hari ini, tanpa infrastruktur baru

Endpoint AI internal yang dipakai [[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]]
**menerima gambar** lewat blok `image_url` standar. Diuji 2026-09-08 atas faktur Bahasa Indonesia:
nomor faktur, nama supplier, jumlah baris item, dan total terbaca **persis**. Kontrol negatif
(prompt sama, gambar dibuang) menjawab "tidak melihat gambar", jadi hasilnya benar-benar dari
membaca, bukan menebak.

Ongkos token terukur (`prompt_tokens`):

| | token | gambar saja |
|---|---|---|
| tanpa gambar (overhead tetap) | 2.061 | - |
| gambar 760x420 | 2.484 | 423 |
| pindaian A4 200 dpi | 3.624 | **1.563** |

⛔ **Overhead tetap 2.030 token lebih besar daripada gambar A4 itu sendiri**, dan ia 57% dari
seluruh permintaan (suntikan system prompt Claude Code oleh proxy). Konsekuensinya untuk bagian
2 blueprint: rencana "OCR dulu supaya hemat token" **tidak terbayar**. Menukar gambar A4 (1.563)
dengan teksnya (kira-kira 500) cuma memangkas sekitar 29% dari total, dan untuk itu perlu
instance ber-GPU yang menyala terus. Tuas penghematan yang jauh lebih besar dan **gratis** adalah
meminta alias endpoint tanpa suntikan system prompt itu.

### Asumsi infrastruktur blueprint tidak selamat

Bagian 5 menulis *"MVP minimal 8GB RAM untuk embedding sederhana; GPU opsional untuk
DeepSeek-OCR"*. Diukur di prod Biznet 2026-09-08: **tidak ada GPU** (VGA-nya QEMU virtual
`1234:1111`), 8 core, **15 GB RAM total dengan 8 GB bebas**, dan **52 container** sudah jalan di
atasnya. VM dev lebih mustahil lagi: 48 container di 7,9 GB dan rutin kena OOM kernel.

Jadi "8 GB RAM" bukan sisa yang tersedia melainkan hampir seluruh sisa mesin, dan "GPU opsional"
sebenarnya berarti "belum ada sama sekali". Model OCR kelas `Unlimited-OCR` (3B parameter bf16,
kira-kira 6 GB bobot, CUDA, inferensi CPU-only tidak didukung) tidak muat di mana pun tanpa
menambah instance ber-GPU sebagai baris biaya baru.

### Kepatuhan data: endpoint internal BUKAN model lokal

`GET /v1/models` per 2026-09-08 mengembalikan `cc/*`, `Claude`, dan `token-router/MiniMax-M3`,
**seluruhnya proksi pihak ketiga**. Nol model lokal. Artinya apa pun yang dikirim ke sana keluar
dari perusahaan, **teks maupun gambar**.

⛔ Karena itu OCR lokal **tidak** menyelesaikan syarat "dokumen tidak boleh keluar", selama tahap
ekstraksinya tetap memanggil endpoint itu. Jalur benar-benar lokal menuntut **dua** model lokal
(OCR dan LLM ekstraksi), bukan satu. Apakah data ERP boleh diproses penyedia AI pihak ketiga
adalah **pertanyaan legal dan manajemen yang belum dijawab**, dan jawabannya membatalkan atau
membuka seluruh kebutuhan GPU di atas. Selama belum dijawab, jangan menjanjikan salah satunya.

### Yang sebenarnya dibutuhkan tiap konsumen, dan hanya satu yang butuh OCR sungguhan

| Konsumen | Bentuk masuk | Butuh OCR? |
|---|---|---|
| [[HRIS - Recruitment]] CV screening | PDF dari portal karir, **maks 1 MB** | **Tidak.** PDF digital sudah punya lapisan teks; cukup ekstraktor PDF. OCR hanya cadangan untuk CV hasil pindai |
| Faktur supplier | pindaian / foto | ya, atau vision |
| [[GA - Inventory Management]] dokumen kedatangan | pindaian / foto | ya, atau vision |
| [[GA - Waste Management]] manifest | pindaian / foto | ya, atau vision |

⚠️ Untuk CV ada **DUA jalur unggah dengan penjaga yang sangat berbeda**, dan menyamakannya
menyesatkan:

| jalur | batas ukuran | pemeriksaan tipe |
|---|---|---|
| portal karir publik (`public_handlers.go`) | **1 MB** | ekstensi wajib `.pdf` |
| unggah oleh HR (`uploadCandidateFile`) | **tidak ada** | **tidak ada** |

Jadi CV hasil pindai memang sulit lewat portal publik, tetapi **bisa masuk tanpa hambatan lewat
HR**, begitu pula DOCX atau JPG. Artinya kebutuhan "OCR fallback untuk CV scan" **nyata**, bukan
kasus teoretis seperti yang sempat ditulis di sini berdasarkan batas 1 MB saja. Yang masih perlu
diukur adalah frekuensinya di prod, bukan apakah mungkin.

Sampai OCR ada, jalur penilaian CV menolak berkas semacam itu dengan alasan yang bisa dibaca
(lapisan teks terlalu tipis, atau bukan PDF), bukan memberinya skor.

⚠️ Tahap `CV Screening` **sudah ada** di pipeline recruitment (`pipeline.go`) sebagai keadaan
menunggu, jadi konsumennya sudah punya tempat mendarat. Yang belum ada cuma pengisinya.

### Urutan yang disarankan, menggantikan MVP 1 di bagian 6

**MVP 0 (baru, dan ini yang pertama):** satu konsumen, ekstraksi terstruktur lewat
[[ADR - 0082 Integrasi AI lewat Klien Tipis di Shared-Library]] yang sudah ada. Tanpa container
baru, tanpa GPU, tanpa vector store. Tujuannya bukan fitur melainkan **angka akurasi atas dokumen
asli** untuk dibawa ke keputusan berikutnya.

Baru setelah MVP 0 punya angka, MVP 1 sampai 5 di bagian 6 layak ditimbang ulang, dan sebagian
besar kemungkinan tidak diperlukan.

**Service terpisah baru wajib bila salah satu terjadi**, bukan sebelumnya:
- model lokal benar-benar dipakai (Python plus CUDA tidak bisa masuk biner Go); atau
- prosesnya melewati **batas 30 detik** [[CORE - API Master Gateway]], yang pasti terjadi untuk
  batch arsip, dan menuntut kontrak asinkron (202 + job id), bukan request-response.

**Jangan bikin penyimpanan berkas sendiri.** [[Microservices - File Service]] dan MinIO sudah
hidup di prod, dan CV recruitment sudah tersimpan di sana; OCR membaca object yang sudah ada,
tidak menerima unggahan sendiri. Lihat [[REF - Kepemilikan Data]].

### Catatan bila `Unlimited-OCR` (Baidu) dipilih

MIT, Python, 3B parameter, keluarannya parsing dokumen berstruktur (bukan teks rata, jadi tata
letak tabel faktur terjaga). ⛔ Pemakaiannya menuntut `trust_remote_code=True`, artinya kode
Python dari repo HuggingFace **dieksekusi** saat model dimuat. Bila dipakai: kunci
`revision=<commit hash>`, jangan `main`, dan isolasi containernya dari DB ERP. Dukungan Bahasa
Indonesianya hanya ditandai "multilingual" tanpa daftar, jadi **belum terbukti** dan wajib diuji
dengan dokumen asli sebelum jadi dasar keputusan.

⚠️ Seluruh uji vision di atas memakai gambar **sintetis bersih** hasil render, bukan foto miring
atau pindaian buram. Ia membuktikan jalurnya jalan dan Bahasa Indonesia terbaca; ia **tidak**
membuktikan ketahanan terhadap dokumen nyata yang jelek. Itu isi MVP 0.

---

1. Ringkasan solusi
    

- Tujuan: Aplikasi OCR berbasis RAG yang memungkinkan unggah dokumen, ekstraksi teks, embedding semantik lokal maupun cloud, indexing vektor, retrieval berbasis konteks, dan jawaban berbasis konten dokumen dengan LLM lokal (Gemma, Qwen, LLMA) melalui instalasi offline Ollama.
    
- Keunggulan inti: mengurangi hallusination dengan basis konteks dokumen, fleksibel untuk kombinasi solusi on-premise dan cloud, serta dukungan multibahasa (termasuk bahasa Indonesia).
    

2. Arsitektur komponen
    

- Ingestor dokumen
    
    - Format dukungan: PDF, JPG, PNG
        
    - OCR pipeline opsional: local atau cloud (kombinasi DeepSeek/OCR dan Google Document AI)
        
    - Output: teks mentah per halaman, dengan metadata (dokumen_id, bahasa, halaman, skor OCR)
        
- Pra-pemrosesan teks
    
    - Normalisasi karakter, deteksi bahasa, cleaning noisy teks
        
    - Segmentasi ke chunk (ukuran 500–1000 kata atau 400–800 token per chunk)
        
- Embedding layer
    
    - Opsi embedding lokal: EmbeddingGemma, nomic-embed-text, BGE-M3 via kontainer/diakses via API internal
        
    - Opsi embedding cloud: GPT-based embedding untuk kualitas Representasi (menimbang biaya per permintaan)
        
    - Output: vektor embedding per chunk beserta metadata
        
- Vector store
    
    - Lokal: FAISS untuk indeks berbasis memori
        
    - Opsional eksternal: Milvus/Weaviate untuk skalabilitas dan distribusi
        
- Retrieval & LLM
    
    - Retrieval: pencocokan cosine similarity untuk memilih chunk relevan
        
    - LLM lokal via Ollama: model Gemma, Qwen, LLMA untuk jawaban berbasis konteks; dapat beroperasi offline
        
    - Prompt: konstruksi konteks dengan chunk relevan, ditambah pertanyaan pengguna
        
- API gateway & Orkestrasi
    
    - Endpoint: /upload-doc, /process-status, /query, /health
        
    - Orkestrasi: OCR → pra-pemrosesan → chunking → embedding → indexing → retrieval → LLM
        
- Observability & keamanan
    
    - Logging terstruktur, metrics latency, error rate
        
    - Enkripsi data in transit dan at rest; akses berbasis peran; audit trail
        
- Deployment
    
    - MVP: Docker Compose dengan layanan OCR lokal, embedding lokal, FAISS, FastAPI, dan Ollama untuk LLM
        
    - Skalabilitas: Docker/Kubernetes untuk produksi; auto-scaling ringan pada bagian OCR/embedding jika diperlukan
        

3. Teknologi inti (konfigurasi opsional)
    

- OCR cloud
    
    - DeepSeek-OCR: efisiensi token dan kemampuan untuk dokumen panjang; cocok untuk pipeline batch
        
    - Google Document AI: akurasi tinggi untuk layout kompleks, tabel, dan handwriting; cocok untuk dokumen formal
        
    - Pertimbangan biaya dan privasi: opsi cloud memberikan kemudahan tanpa manajemen infrastruktur, tetapi biaya berulang dan potensi isu privasi
        
- Embedding cloud
    
    - GPT-based embedding untuk kualitas representasi semantik tinggi pada dokumen panjang
        
    - Biaya per permintaan perlu dipertimbangkan saat skala besar
        
- Embedding lokal (pilihan utama untuk MVP tanpa biaya API berkelanjutan)
    
    - EmbeddingGemma: model 300M, on-device, multilingual; footprint relatif kecil; mudah disiagakan melalui Ollama
        
    - nomic-embed-text: konteks window besar, performa kuat pada korpus panjang
        
    - BGE-M3: kualitas embedding multilingual lebih tinggi pada korpus multibahasa, dengan footprint lebih besar
        
- LLM lokal via Ollama
    
    - Model Gemma, Qwen, LLMA siap dijalankan offline melalui Ollama
        
    - Cocok untuk jawaban berbasis konteks tanpa mengandalkan jaringan eksternal
        
- Vector store
    
    - FAISS untuk solusi lokal sederhana dan cepat
        
    - Milvus/Weaviate untuk skala besar dan cluster/clustered retrieval
        

4. Alur data detail (end-to-end)
    

- Step 1: Upload dokumen melalui endpoint /upload-doc
    
- Step 2: OCR layer memilih mode (local/cloud bergantung konfigurasi)
    
    - Parsing teks per halaman dengan struktur layout
        
- Step 3: Pra-pemrosesan teks dan chunking
    
    - Normalisasi, segmentasi, penandaan bahasa
        
- Step 4: Embedding per chunk
    
    - Pilih model embedding (local atau cloud)
        
    - Simpan embedding ke vektor store dengan metadata
        
- Step 5: Retrieval untuk query
    
    - Endpoint /query menerima pertanyaan
        
    - Embedding query → retrieve chunk relevan dari vektor store
        
    - Gabungkan chunk relevan ke prompt LLM
        
- Step 6: Jawaban LLM
    
    - LLM lokal via Ollama mengeluarkan jawaban berbasis konteks dokumen
        
    - Tampilkan jawaban beserta sumber chunk untuk audit trail
        
- Step 7: Monitoring dan logging
    
    - Status processing, waktu respons, sumber bahasa, dan kualitas OCR
        

5. Konfigurasi teknis utama (contoh)
    

- Infrastruktur
    
    - CPU/RAM: MVP minimal 8GB RAM untuk embedding sederhana; GPU opsional untuk DeepSeek-OCR
        
    - Storage: cukup ruang untuk dokumen + embeddings (pertimbangkan 2–3x ukuran dokumen untuk metadata)
        
- Layanan
    
    - OCR: opsi lokal (Tesseract) atau cloud (DeepSeek/OCR, Google Document AI)
        
    - Embedding: embedding Gemma/nomic/BGE via Ollama
        
    - LLM: gemma, qwen, llma via Ollama
        
    - Vector store: FAISS di memory + on-disk index
        
- API & Orkestrasi
    
    - FastAPI sebagai gateway AI
        
    - Celery/RQ untuk antrian tugas OCR/embedding jika perlu
        
    - Docker Compose:
        
        - api: FastAPI server
            
        - ocr-service: container OCR lokal/cloud chooser
            
        - embedding-service: container Ollama atau wrapper
            
        - vector-store: FAISS service atau direktori indeks
            
        - llm-service: Ollama LLM runner
            
- Keamanan
    
    - TLS untuk endpoints
        
    - Secrets management (vault/secrets manager)
        
    - Akses berbasis OAuth2/OpenID Connect jika diperlukan
        

6. Rencana implementasi MVP (jalan)
    

- MVP 1: OCR lokal + chunking + embedding lokal (Gemma) + FAISS + LLM eksternal
    
- MVP 2: tambahkan opsi OCR cloud (DeepSeek-OCR atau Google Document AI) dan sampling benchmark
    
- MVP 3: tambahkan opsi embedding cloud (GPT-based) sebagai fallback/benchmarks
    
- MVP 4: implementasi Ollama LLM offline untuk Gemma, Qwen, LLMA dengan fallback switcher
    
- MVP 5: evaluasi performa, tambahkan caching, optimasi prompt dan chunking
    

7. Kriteria evaluasi
    

- Akurasi OCR (untuk bahasa Indonesia) termasuk teks yang hilang atau salah pengenalan karakter
    
- Kualitas embedding: uji BEIR-like dataset atau kriteria retrieval relevansi chunk
    
- Waktu respon end-to-end dari unggah dokumen hingga jawaban
    
- Biaya operasional per bulan jika menggunakan layanan cloud
    
- Privasi dan compliance sesuai kebijakan perusahaan
    

8. Pertanyaan konfirmasi untuk penyempurnaan blueprint
    

- Apakah ingin MVP langsung menggunakan satu kombinasi (OCR lokal + Embedding Gemma + LLM Gemma via Ollama) atau ingin menyediakan pilihan multi-model (Gemma, nomic, BGE-M3) untuk A/B testing?
    
- Berapa target volume dokumen bulanan dan bahasa dominan dokumen?
    
- Apakah perlu dukungan multi-bahasa selain bahasa Indonesia (mis. Inggris, campuran)?
    
- Infrastruktur mana yang akan dipakai (on-premise, private cloud, hybrid)?
    
- Apakah perlu pustaka monitoring & logging tertentu (OpenTelemetry, Prometheus, Grafana) untuk observability?
    

Catatan teknis tambahan

- Karena Anda meminta opsi OCR cloud dan embedding cloud, pastikan Anda merencanakan biaya operasional serta kebijakan privasi data. Dokumentasikan skema fallback jika layanan cloud sedang down.
    
- Untuk LLM offline via Ollama, pastikan versi Ollama Anda mendukung model Gemma/Qwen/LLMA yang kompatibel, serta cukup memori untuk menjalankan model-model tersebut pada ukuran konteks yang diinginkan.
    
- Sediakan mekanisme caching hasil OCR, chunking, dan embedding untuk mempercepat permintaan berulang terhadap dokumen yang sama.
    


1. [https://unstract.com/blog/best-pdf-ocr-software/](https://unstract.com/blog/best-pdf-ocr-software/)
2. [https://pragmile.com/ocr-ranking-2025-comparison-of-the-best-text-recognition-and-document-structure-software/](https://pragmile.com/ocr-ranking-2025-comparison-of-the-best-text-recognition-and-document-structure-software/)
3. [https://www.techradar.com/best/best-ocr-software](https://www.techradar.com/best/best-ocr-software)
4. [https://www.reddit.com/r/datacurator/comments/1nonzfm/best_ocr_in_2025/](https://www.reddit.com/r/datacurator/comments/1nonzfm/best_ocr_in_2025/)
5. [https://skywork.ai/blog/ai-agent/deepseek-ocr-vs-google-azure-aws-abbyy-paddleocr-tesseract-comparison/](https://skywork.ai/blog/ai-agent/deepseek-ocr-vs-google-azure-aws-abbyy-paddleocr-tesseract-comparison/)
6. [https://klearstack.com/ocr-software-comparison](https://klearstack.com/ocr-software-comparison)
7. [https://learn.g2.com/best-ocr-software](https://learn.g2.com/best-ocr-software)
8. [https://www.f22labs.com/blogs/ocr-models-comparison/](https://www.f22labs.com/blogs/ocr-models-comparison/)
9. [https://thedigitalprojectmanager.com/tools/best-document-scanning-software/](https://thedigitalprojectmanager.com/tools/best-document-scanning-software/)