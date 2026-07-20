"""Ringkasan dokumen via Claude Batches API.

Ini satu-satunya bagian non-deterministik dari generator. Kualitasnya
diukur lewat eval set, bukan lewat assertion.
"""

import json
import time

from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

from .parsing import potong_untuk_llm

MODEL = "claude-opus-4-8"
MAX_TOKENS = 1024

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
    """Parse JSON balasan model. Rusak -> None, bukan exception."""
    try:
        data = json.loads(isi)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(data, dict):
        return None
    if "ringkasan" not in data or "kata_kunci" not in data:
        return None
    if not isinstance(data["kata_kunci"], list):
        return None
    return {"ringkasan": data["ringkasan"], "kata_kunci": data["kata_kunci"]}


def submit_batch(client, tugas: list[dict]) -> str:
    """Submit batch ringkasan. Batches API memberi diskon 50 persen."""
    requests = [
        Request(
            custom_id=t["custom_id"],
            params=MessageCreateParamsNonStreaming(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                output_config={
                    "format": {"type": "json_schema", "schema": SKEMA_RINGKASAN}
                },
                messages=[{
                    "role": "user",
                    "content": bangun_prompt(t["judul"], t["jenis"], t["isi"]),
                }],
            ),
        )
        for t in tugas
    ]
    batch = client.messages.batches.create(requests=requests)
    return batch.id


def ambil_hasil(client, batch_id: str, interval: int = 30) -> dict[str, dict | None]:
    """Tunggu batch selesai, kembalikan custom_id -> hasil (None bila gagal)."""
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            break
        print(f"  batch {batch_id}: {batch.processing_status} ...")
        time.sleep(interval)

    hasil: dict[str, dict | None] = {}
    for baris in client.messages.batches.results(batch_id):
        if baris.result.type != "succeeded":
            hasil[baris.custom_id] = None
            continue
        teks = next(
            (b.text for b in baris.result.message.content if b.type == "text"), ""
        )
        hasil[baris.custom_id] = _parse_isi_pesan(teks)
    return hasil
