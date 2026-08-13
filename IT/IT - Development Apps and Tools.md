## Deskripsi

*Development tools dan aplikasi yang digunakan secara internal untuk melakukan iterasi*

- **Status**: ✅ Aktif — referensi tools internal yang dipakai (Hoppscotch, OneBharata, dll).

[Hoppscotch](https://hoppscotch.io/) - Ekosistem API development open-source
- Di-host secara internal pada VM ERP-Development: http://10.10.10.121:3000/
- Credentials untuk aplikasi ini berasal dari akun GitHub pribadi yang perlu di-invite oleh akun admin Hoppscotch
- Development workspace ada di "BIP ERP"

[OneBharata](https://hoppscotch.io/) - Production
- Produksi kini di **VPS Biznet**, diakses lewat URL publik: https://erp.bharatainternasional.com (alamat lama `http://10.10.10.120:9696/` sudah pensiun). Port `9696` tetap dipakai container-nya di host, tapi tidak diekspos langsung ke pengguna.
- Credentials mengikuti akun yang Anda buat untuk perusahaan saat on-boarding di myBharata, jika Anda lupa Anda bisa menghubungi IT Support

[OneBharata](https://hoppscotch.io/) - Development
- Di-host secara internal pada VM ERP-Development: http://10.10.10.121:9696/
- Credentials dapat diubah untuk keperluan development, namun dokumen terkadang di-resync dengan database production

**Papan Aktivitas Developer** — papan peringkat aktivitas developer se-organisasi GitHub, diperbarui seketika lewat webhook
- Di-host di Cloudflare (akun bersama tim), **bukan** di VM internal: `https://dev-activity-board.bharataitteam.workers.dev/<DASHBOARD_SLUG>`
- Dibuka lewat tautan tanpa login; potongan URL rahasianya ada di rahasia Worker
- Rincian dan batasan pemakaian angkanya: [[IT - Papan Aktivitas Developer]]

## Dokumen Terkait

- [[IT - Big Pictures]] — peta domain IT
- [[IT - Server, VMs and Databases]] — VM tempat tool ini di-host
- [[IT - Papan Aktivitas Developer]] — papan aktivitas developer (di-host di luar VM internal)
