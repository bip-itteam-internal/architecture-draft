# Fixture Kantor Agent

`baris-nyata.json` berisi satu baris kejadian **nyata** per jenis dari transkrip sesi Claude Code
(`~/.claude/projects/<proyek>/<sesi>.jsonl` dan `<sesi>/subagents/agent-*.jsonl`), diambil
2026-09-15 dari Claude Code 2.1.269. `meta-subagent.json` berisi satu `.meta.json` subagent nyata.

Kenapa baris nyata dan bukan rakitan tangan: test yang memalsukan bentuk sumbernya sudah terbukti
buta di repo ini (`rules/team-memory.md`, bagian memanggil endpoint daftar service lain). Skenario uji
disusun di `tests/test_kantor_agent.py` dengan menyalin templat ini lalu hanya mengubah field yang
sedang diuji (id, nama tool, `stop_reason`, `timestamp`, `cwd`).

## Pembersihan (repo vault PUBLIC)

- Yang dipertahankan hanya nilai struktural: `type`, `stop_reason`, nama tool di blok `tool_use`,
  `isMeta`, `isSidechain`, `userType`, `entrypoint`, `version`, `operation`, `model`, `agentType`,
  `requestShape`, `spawnDepth`.
- Semua id diganti id palsu yang tetap berpasangan, `timestamp` diseragamkan, `cwd` menjadi
  `{WORKSPACE}` (diisi test), dan string lain menjadi `"x"`.
- Sebelum commit, gerbang ini wajib **0 hasil** (README ini sengaja dikecualikan karena memuat
  polanya sendiri):

```
git grep -n -i -E "data utama|irfan|claudia|gmail|bip-|itteam|c:\\\\|/users/|\\\\wt\\\\|erp|office|aplikasi" -- ".agent-kit/tests/fixtures/kantor-agent/*.json"
```

Bila format transkrip berubah di rilis Claude Code berikutnya, ambil ulang templat dengan cara yang
sama. Jangan menyuntingnya dengan tangan: templat yang disunting tangan berhenti membuktikan bentuk
aslinya.
