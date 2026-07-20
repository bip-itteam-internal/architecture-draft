"""Prompt + validasi untuk ringkasan dokumen.

Ringkasan dan kata_kunci dibuat oleh Claude Code sendiri (tim memakai Claude
Code Max, bukan API key) -- bukan oleh panggilan jaringan dari modul ini.
Modul ini TIDAK memanggil API apa pun: cuma menyusun instruksi (`bangun_prompt`,
dipakai untuk membangun `panduan` di berkas `--daftar-tugas`), stub lokal untuk
dokumen 🔴 Stub, dan validasi tipe atas ringkasan yang diserap kembali lewat
`--serap`.

Ini satu-satunya bagian non-deterministik dari generator. Kualitasnya diukur
lewat eval set, bukan lewat assertion.
"""

import json

from .parsing import potong_untuk_llm

MODEL = "claude-opus-4-8"  # dokumentasi: model yang dipakai Claude Code untuk meringkas

SKEMA_RINGKASAN: dict = {
    "type": "object",
    "properties": {
        "ringkasan": {
            "type": "string",
            "description": "2-3 kalimat, Bahasa Indonesia, berorientasi pertanyaan",
        },
        "kata_kunci": {
            "type": "array",
            "items": {"type": "string"},
            "description": "5-10 kata kunci, campur Indonesia dan English",
        },
    },
    "required": ["ringkasan", "kata_kunci"],
    "additionalProperties": False,
}

_TEMPLATE = """Kamu meringkas satu dokumen dari vault arsitektur ERP Bharata \
untuk dipakai sebagai index pencarian.

Judul dokumen: {judul}
Jenis dokumen: {jenis}

Tulis dalam Bahasa Indonesia. Istilah teknis yang lazim English biarkan English \
(endpoint, request, service, payroll, approval, dst).

`ringkasan`: 2 sampai 3 kalimat yang menjawab "dokumen ini bisa menjawab \
pertanyaan apa saja", BUKAN sekadar memadatkan isinya.
Buruk : "Berisi endpoint dan alur lembur."
Baik  : "Menjawab: bagaimana cara mengajukan lembur, siapa yang menyetujui, \
dan bagaimana upah lembur dihitung."

`kata_kunci`: 5 sampai 10 istilah yang mungkin dipakai orang saat mencari \
dokumen ini. Sertakan padanan dua bahasa bila ada (mis. "lembur" dan \
"overtime"), termasuk singkatan yang dipakai internal.

JANGAN menyimpulkan status implementasi. Itu diambil terpisah dari marker \
dokumen.

--- ISI DOKUMEN ---
{isi}
"""


def bangun_prompt(judul: str, jenis: str | None, isi: str) -> str:
    return _TEMPLATE.format(
        judul=judul,
        jenis=jenis or "tidak diketahui",
        isi=potong_untuk_llm(isi),
    )


def ringkas_stub(judul: str) -> dict:
    """Dokumen 🔴 Stub: satu baris, tanpa panggil LLM. Hemat dan jujur."""
    return {
        "ringkasan": f"Stub kosong untuk {judul}. Belum ada isi.",
        "kata_kunci": [],
    }


def _parse_isi_pesan(isi: str) -> dict | None:
    """Parse JSON balasan model. Rusak -> None, bukan exception.

    Validasi TIPE, bukan cuma keberadaan key: manifest hilir berasumsi
    `ringkasan` adalah `str` (tak kosong) dan `kata_kunci` adalah
    `list[str]`. Data yang lolos di sini dengan tipe salah akan gagal
    jauh dari sumbernya dan sulit didiagnosis -- lebih baik ditolak
    di titik ini, konsisten dengan filosofi fungsi ini: rusak -> None.

    Dulu inputnya datang dari structured output API yang dibatasi skema;
    sekarang datang dari berkas JSON (`--serap`) yang ditulis agent secara
    bebas, yang jauh lebih mungkin menyimpang -- validasi ini justru makin
    penting, bukan berkurang relevansinya.
    """
    try:
        data = json.loads(isi)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    if "ringkasan" not in data or "kata_kunci" not in data:
        return None

    ringkasan = data["ringkasan"]
    kata_kunci = data["kata_kunci"]

    if not isinstance(ringkasan, str) or not ringkasan.strip():
        return None
    if not isinstance(kata_kunci, list):
        return None
    if not all(isinstance(k, str) for k in kata_kunci):
        return None

    return {"ringkasan": ringkasan, "kata_kunci": kata_kunci}
