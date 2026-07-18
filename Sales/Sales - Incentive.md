## Deskripsi

Insentive disini memiliki irisan yang ada di [[Finance - Incentive]]
perbedaannya adalah pada dokumen ini lebih pada kriteria dan data advertisement. Seperti CPA, Konversi dan lain sebagainya yang tidak tercover di accurate online. 
Setiap bulan SPV marketing merekap pencapaian iklan yang nantinya digabungkan dengan Sistem Finance (insentif)

- **Status**: ✅ Implemented — engine insentif (9 role marketing) sudah dihitung di [[Microservices - Insentive Service]].
## Implementasi (backend: [[Microservices - Insentive Service]])

Engine insentif sudah diimplementasikan dan menghitung **9 role marketing** dengan kriteria/scoring spesifik:

| Role | Tipe | Kriteria utama |
|---|---|---|
| ADV Leader TikTok (`adv_leader`) | Individual | **ROI binary** — `realisasi ≥ target` → bobot penuh, jika tidak → 0 |
| ADV Marketplace (`adv_marketplace`) | Individual | **CPA range** — `((target_atas − realisasi)/100) + 1` |
| ADV Meta (`adv_meta`) | Individual | **CPA range** |
| Host Live (`host_live`) | Shared/tim | `score × multiplier × konversi / teamSize` |
| Affiliate (`affiliate`) | Shared/tim | idem |
| CRM (`crm`) | Individual | standard |
| CS (`cs`) | Individual | + syarat **closing rate ≥ 50%** |
| ICC (`icc`) | Pay-per-video | Rp10.000/video; Rp150.000/video (GMV Max); hanya video 7–30 hari |
| Supervisor (`supervisor`) | Profit-based | `achievementRate% × realisasi_profit`; gugur jika rata-rata KPI tim < 70 atau retur > 5% |

**Aturan umum**
- **Score minimum 70** → di bawahnya `DISQUALIFIED` (insentif 0)
- Multiplier bertingkat per role (mis. ADV Marketplace/Meta/Host/CRM: ≥81 → 5×, 70–80.99 → 2×)
- Rumus individual: `total_score × multiplier × konversi`

**Sumber data (otomatis)**
- Data iklan/performa (CPA, ROI, konversi, GMV) ditarik dari [[Microservices - Integration Service]] (TikTok GMV Max) via **mapping** employee → advertiser_id/store_id
- Profit SPV dari [[External - Accurate]]

**Alur**
Cron tarik data → hasil `AUTO_DRAFT` → karyawan/ADV Leader bisa override metrik (wajib alasan, ter-audit) → submit → **Finance approve / minta revisi**. Khusus ICC & Host Live disubmit oleh ADV Leader TikTok (bukan dirinya sendiri).

> Detail endpoint, schema DB, RBAC, dan QA ada di [[Microservices - Insentive Service]] serta `services/insentive/SYSTEM_DESIGN.md` di repo bip-erp.

## Dokumen Terkait

- [[Finance - Incentive]] · [[Microservices - Insentive Service]] (backend) · [[Microservices - Integration Service]] (data iklan) · [[External - Accurate]]