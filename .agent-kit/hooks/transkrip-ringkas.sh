#!/usr/bin/env bash
# transkrip-ringkas.sh — cermin transkrip-ringkas.ps1 (alasan desain ada di sana). Butuh python3.
# Pemakaian: transkrip-ringkas.sh <transkrip.jsonl> <keluaran.md> [maks_teks=1500] [maks_input=200]
set -u
[ $# -ge 2 ] || { echo "pakai: $0 <transkrip.jsonl> <keluaran.md> [maks_teks] [maks_input]" >&2; exit 2; }
command -v python3 >/dev/null 2>&1 || { echo "butuh python3" >&2; exit 2; }
python3 - "$1" "$2" "${3:-1500}" "${4:-200}" <<'PY'
import json, sys, os, re, datetime
src, dst, maks_teks, maks_input = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
if not os.path.exists(src):
    print(f"Transkrip tidak ada: {src}", file=sys.stderr); sys.exit(2)
def potong(s, n):
    s = re.sub(r"\s+", " ", s or "").strip()
    return s[:n] + " […]" if len(s) > n else s
def ringkas(content):
    out = []
    if isinstance(content, str):
        return [potong(content, maks_teks)]
    for b in content or []:
        t = b.get("type")
        if t == "text": out.append(potong(b.get("text", ""), maks_teks))
        elif t == "tool_use":
            arg = []
            for k, v in (b.get("input") or {}).items():
                arg.append(f"{k}: {potong(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False), maks_input)}")
            out.append(f"- tool: **{b.get('name','')}** {{ {'; '.join(arg)} }}")
        elif t == "tool_result":
            c = b.get("content"); n = len(c) if isinstance(c, str) else sum(len(x.get("text","")) for x in (c or []) if isinstance(x, dict))
            out.append(f"- hasil tool ({n} char)")
    return out
total = sah = u = a = 0; body = []
with open(src, encoding="utf-8") as f:
    for line in f:
        if not line.strip(): continue
        total += 1
        try: o = json.loads(line)
        except Exception: continue
        sah += 1
        if o.get("isSidechain") is True: continue
        t = o.get("type")
        if t not in ("user", "assistant"): continue
        msg = o.get("message") or {}
        blok = ringkas(msg.get("content"))
        if not blok: continue
        if t == "user": u += 1; body.append(f"### [{o.get('timestamp','')}] USER")
        else: a += 1; body.append(f"### [{o.get('timestamp','')}] ASSISTANT")
        body.extend(blok); body.append("")
ratio = sah / total if total else 0
if ratio < 0.5 or u == 0 or a == 0:
    print(f"Transkrip tidak terurai: {sah}/{total} baris JSON sah, user={u}, assistant={a}. Skema mungkin berubah. JANGAN memakai ringkasan kosong.", file=sys.stderr); sys.exit(3)
hdr = [f"# Ringkasan transkrip: {os.path.basename(src)}",
       f"- Baris: {total}, JSON sah: {sah}, giliran user: {u}, giliran assistant: {a}",
       f"- Dibuat: {datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')} UTC oleh transkrip-ringkas.sh (teks dipotong {maks_teks} char, argumen tool {maks_input} char)",
       "", "## Alur", ""]
os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
with open(dst, "w", encoding="utf-8") as f: f.write("\n".join(hdr + body) + "\n")
print(f"OK: {u} giliran user, {a} giliran assistant -> {dst}")
PY
