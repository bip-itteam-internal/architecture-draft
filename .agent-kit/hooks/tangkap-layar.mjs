#!/usr/bin/env node
// tangkap-layar.mjs - tangkapan layar + ukuran DOM build erp-frontend untuk judge desain.
//
// Dipanggil tangkap-layar.ps1 sesudah `pnpm start` listen. Menulis <keluaran>/ringkasan.json dan
// PNG <keluaran>/<i>-<keadaan>-<lebar>-<tema>.png. Keputusan "tangkapan gagal vs galat kode" BUKAN
// di sini (itu layar-lib.py); skrip ini hanya merekam fakta selengkap mungkin supaya keputusan itu
// bisa diambil tanpa menebak.
//
// Pemakaian:
//   node tangkap-layar.mjs --url-dasar http://localhost:<p> --manifest <json> --keluaran <dir>
//                          [--chrome <exe>] [--batas-rute-detik 90]
// Env opsional TANGKAP_LAYAR_PROFIL_DASAR: induk folder profil Chrome (dipakai test supaya
// pemeriksaan "tak ada Chrome tersisa" hanya melihat proses miliknya sendiri).
//
// Jebakan yang masing-masing pernah memakan satu jam di mesin ini (catatan
// erp-frontend-verifikasi-layar-tanpa-backend), dan karena itu dikodekan di sini:
// - Stub 401 melempar ke /login lewat interceptor axios: yang tak distub dijawab 500, tak pernah 401.
// - employee/me yang gagal di-retry tanpa henti dan halaman mentok di Skeleton: selalu 200.
// - Cegat "beda origin dengan url dasar ATAU pathname /api/": worktree tanpa .env memanggil API
//   relatif ke server Next sendiri, dan .env worktree lain bisa menunjuk PROD.
// - Tema lewat localStorage.theme sebelum navigate (next-themes), dibuktikan dari kelas <html>;
//   prefers-color-scheme tidak mengubah tema aplikasi ini.
// - Tangkapan viewport saja: captureBeyondViewport merusak tata letak Recharts.
// - Klik lewat Input.dispatchMouseEvent di tengah elemen; event sintetis tak membuka Radix.
// - Network.setCookie memakai `url`, nilai JSON di-encodeURIComponent (koma memecah header).
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";

const MATRIKS_PENUH = [
  { lebar: 1366, tinggi: 768, mobile: false, tema: "light" },
  { lebar: 1366, tinggi: 768, mobile: false, tema: "dark" },
  { lebar: 390, tinggi: 844, mobile: true, tema: "light" },
  { lebar: 390, tinggi: 844, mobile: true, tema: "dark" },
];
const TOMBOL_OVERLAY = ["Nanti saja", "Ingatkan saya nanti", "Mengerti"];
const TEKS_BOUNDARY = ["Terjadi Kesalahan", "Application error: a client-side exception"];
const CHROME_BAWAAN = [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
];
const BATAS_KONSOL = 60;
const SEGMEN_MAKS = 3; // tangkapan pertama + 2 gulir; lebih dari itu jarang dibaca penilai

const tidur = (ms) => new Promise((r) => setTimeout(r, ms));

function bacaArgumen(argv) {
  const a = { batasRuteDetik: 90, chrome: "" };
  for (let i = 0; i < argv.length; i++) {
    const k = argv[i], v = argv[i + 1];
    if (k === "--url-dasar") { a.urlDasar = v; i++; }
    else if (k === "--manifest") { a.manifest = v; i++; }
    else if (k === "--keluaran") { a.keluaran = v; i++; }
    else if (k === "--chrome") { a.chrome = v; i++; }
    else if (k === "--batas-rute-detik") { a.batasRuteDetik = Number(v) || 90; i++; }
  }
  return a;
}

// Ditulis atomik dan diulang tiap entri: bila proses dibunuh di tengah, yang tersisa tetap JSON
// sah berisi entri yang sudah jadi, bukan berkas setengah tertulis.
function tulisRingkasan(keluaran, ringkasan) {
  const tujuan = path.join(keluaran, "ringkasan.json");
  const sementara = tujuan + ".tmp";
  fs.writeFileSync(sementara, JSON.stringify(ringkasan, null, 2), "utf8");
  fs.renameSync(sementara, tujuan);
}

function portBebas() {
  return new Promise((res, rej) => {
    const s = net.createServer();
    s.once("error", rej);
    s.listen(0, "127.0.0.1", () => { const p = s.address().port; s.close(() => res(p)); });
  });
}

async function ambilJson(url, opsi = {}, batasMs = 3000) {
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), batasMs);
  try {
    const r = await fetch(url, { ...opsi, signal: ac.signal });
    return await r.json();
  } finally { clearTimeout(t); }
}

// ---- CDP minimal di atas WebSocket bawaan Node 24 (tanpa puppeteer) ----
class Cdp {
  constructor(ws) {
    this.ws = ws; this.id = 0; this.tunggu = new Map(); this.pendengar = new Map();
    ws.onmessage = (ev) => {
      const m = JSON.parse(typeof ev.data === "string" ? ev.data : ev.data.toString());
      if (m.id && this.tunggu.has(m.id)) {
        const { res, rej, t } = this.tunggu.get(m.id);
        this.tunggu.delete(m.id); clearTimeout(t);
        if (m.error) rej(new Error(m.error.message || JSON.stringify(m.error))); else res(m.result || {});
      } else if (m.method) {
        for (const fn of this.pendengar.get(m.method) || []) {
          try { fn(m.params || {}); } catch { /* pendengar tak boleh mematikan sesi */ }
        }
      }
    };
    ws.onclose = () => { for (const { rej, t } of this.tunggu.values()) { clearTimeout(t); rej(new Error("websocket tertutup")); } this.tunggu.clear(); };
  }
  static buka(url) {
    return new Promise((res, rej) => {
      const ws = new WebSocket(url);
      const t = setTimeout(() => rej(new Error("websocket tak tersambung: " + url)), 15000);
      ws.onopen = () => { clearTimeout(t); res(new Cdp(ws)); };
      ws.onerror = () => { clearTimeout(t); rej(new Error("websocket gagal: " + url)); };
    });
  }
  kirim(method, params = {}, batasMs = 30000) {
    const id = ++this.id;
    return new Promise((res, rej) => {
      const t = setTimeout(() => { this.tunggu.delete(id); rej(new Error("CDP " + method + " tak menjawab")); }, batasMs);
      this.tunggu.set(id, { res, rej, t });
      try { this.ws.send(JSON.stringify({ id, method, params })); } catch (e) { clearTimeout(t); this.tunggu.delete(id); rej(e); }
    });
  }
  on(method, fn) { if (!this.pendengar.has(method)) this.pendengar.set(method, []); this.pendengar.get(method).push(fn); }
  tutup() { try { this.ws.close(); } catch { /* sudah tertutup */ } }
}

// ---- Chrome: profil baru, dibunuh hanya miliknya ----
async function nyalakanChrome(exe, profil) {
  const port = await portBebas();
  // Argumen SATU string (windowsVerbatimArguments): di mesin ini Chrome yang menerima argumen
  // sebagai larik dari Start-Process tak pernah membuka port debug. Kutip dipasang sendiri.
  const argumen = [
    "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
    "--disable-extensions", "--disable-background-networking", "--disable-sync",
    "--disable-component-update", "--mute-audio", "--window-size=1366,900",
    `--remote-debugging-port=${port}`, `--user-data-dir="${profil}"`, "about:blank",
  ].join(" ");
  // argv0 dikutip sendiri: dalam mode verbatim libuv tak mengutipnya, dan "C:\Program Files\..."
  // yang terpecah di spasi dibaca Chrome sebagai URL tambahan.
  const proses = spawn(exe, [argumen], { argv0: `"${exe}"`, windowsVerbatimArguments: true, stdio: "ignore", shell: false, windowsHide: true });
  proses.on("error", () => { /* dilaporkan lewat batas waktu /json/version */ });
  // Siap = /json/version menjawab. DevToolsActivePort tidak dipakai: di mesin ini berkas itu bisa
  // tak pernah ditulis walau HTTP-nya sudah hidup. Menyala bisa ~30 dtk, jadi batasnya 60.
  const batas = Date.now() + 60000;
  let versi = null;
  while (Date.now() < batas) {
    if (proses.exitCode !== null) break;
    try { versi = await ambilJson(`http://127.0.0.1:${port}/json/version`, {}, 2000); break; } catch { await tidur(500); }
  }
  return { proses, port, versi };
}

function bunuhChrome(chrome, profil) {
  if (chrome?.proses?.pid && chrome.proses.exitCode === null) {
    spawnSync("taskkill", ["/T", "/F", "/PID", String(chrome.proses.pid)], { stdio: "ignore" });
  }
  // Sapuan kedua: proses anak yang tercerai dari induknya. Disaring lewat folder profil, jadi
  // browser user dan run tangkapan lain tak tersentuh.
  const pola = profil.replace(/'/g, "''");
  spawnSync("powershell.exe", ["-NoProfile", "-NonInteractive", "-Command",
    `Get-CimInstance Win32_Process -Filter "Name='chrome.exe' OR Name='msedge.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains('${pola}') } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop } catch {} }`],
  { stdio: "ignore", timeout: 30000 });
  for (let i = 0; i < 10; i++) {
    try { fs.rmSync(profil, { recursive: true, force: true }); return; } catch { spawnSync("powershell.exe", ["-NoProfile", "-Command", "Start-Sleep -Milliseconds 500"], { stdio: "ignore" }); }
  }
}

// ---- stub ----
function buatJwt(sub) {
  const b64 = (o) => Buffer.from(JSON.stringify(o)).toString("base64url");
  // exp jauh di depan: tanpa itu getTimeUntilExpiry = 0, refresh proaktif gagal, lalu /login.
  const exp = Math.floor(Date.now() / 1000) + 10 * 365 * 24 * 3600;
  return `${b64({ alg: "HS256", typ: "JWT" })}.${b64({ sub, employee_id: sub, exp, iat: Math.floor(Date.now() / 1000) })}.uji-tangkap-layar`;
}

// Arti `pola` (berlaku untuk penulis manifest):
//   "/api/employee/resign"        pathname SAMA atau BERAKHIRAN pola itu (baseURL relatif maupun
//                                 gateway lengkap sama-sama cocok). `/resign/summary` TIDAK cocok.
//   "/api/employee/resign/*"      awalan: semua path di bawahnya (termasuk `/resign/123`).
//   "/api/employee/list?type=x"   bagian path seperti di atas, DAN tiap parameter query di pola
//                                 ada dengan nilai sama (parameter lain di URL boleh ada).
// Dulu potongan-teks biasa: diukur di uji asap /hris/resign, stub daftar ikut menjawab
// `/resign/summary` dan `/resign/non-aktif-tanpa-catatan` dengan bentuk yang salah, dan layarnya
// menampilkan baris daftar di panel lain tanpa satu pun galat. Bila beberapa cocok, pola terpanjang
// menang.
function polaCocok(pola, u) {
  if (typeof pola !== "string" || !pola) return false;
  const [polaPath, polaQuery] = pola.split("?", 2);
  let pathCocok;
  if (polaPath.endsWith("*")) pathCocok = u.pathname.includes(polaPath.slice(0, -1));
  else pathCocok = u.pathname === polaPath || u.pathname.endsWith(polaPath.startsWith("/") ? polaPath : "/" + polaPath);
  if (!pathCocok) return false;
  if (polaQuery) {
    for (const [k, v] of new URLSearchParams(polaQuery)) if (u.searchParams.get(k) !== v) return false;
  }
  return true;
}

function cariStub(daftar, u) {
  let pilih = null;
  for (const s of daftar || []) {
    if (s && polaCocok(s.pola, u) && (!pilih || s.pola.length > pilih.pola.length)) pilih = s;
  }
  return pilih;
}

function header(req, nama) {
  const h = req.headers || {};
  for (const k of Object.keys(h)) if (k.toLowerCase() === nama.toLowerCase()) return h[k];
  return "";
}

// ---- skrip yang dievaluasi di halaman ----
const JS_UKUR = `(() => {
  const terlihat = (el) => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== "hidden" && cs.display !== "none"; };
  const sel = (el) => { const bagian = []; let e = el;
    for (let i = 0; e && e.nodeType === 1 && i < 4; i++) {
      if (e.id) { bagian.unshift("#" + CSS.escape(e.id)); break; }
      let s = e.tagName.toLowerCase();
      const ds = e.getAttribute("data-slot"); if (ds) s += '[data-slot="' + ds + '"]';
      const role = e.getAttribute("role"); if (role) s += '[role="' + role + '"]';
      s += [...e.classList].slice(0, 3).map((c) => "." + CSS.escape(c)).join("");
      const ind = e.parentElement; if (ind) { const sama = [...ind.children].filter((c) => c.tagName === e.tagName);
        if (sama.length > 1) s += ":nth-of-type(" + (sama.indexOf(e) + 1) + ")"; }
      bagian.unshift(s); e = e.parentElement; if (!e || e === document.body || e === document.documentElement) break;
    }
    return bagian.join(" > "); };
  const de = document.documentElement;
  const luber_halaman = de.scrollWidth > de.clientWidth + 1;
  const luber_wadah = [];
  for (const el of document.body ? document.body.querySelectorAll("*") : []) {
    if (luber_wadah.length >= 40) break;
    if (el instanceof SVGElement || el.closest("svg")) continue;
    // clientWidth <= 2: teks sr-only (1px, clip) yang memang sengaja tak terlihat.
    if (!(el.clientWidth > 2) || el.scrollWidth <= el.clientWidth + 1) continue;
    const cs = getComputedStyle(el);
    if (cs.textOverflow === "ellipsis") continue; // truncate disengaja, bukan luberan
    if (!terlihat(el)) continue;
    luber_wadah.push({ selektor: sel(el), scrollWidth: el.scrollWidth, clientWidth: el.clientWidth, overflowX: cs.overflowX });
  }
  const tumpang = []; const sudah = new Set();
  const interaktif = 'button, a[href], input:not([type="hidden"]), select, textarea, [role="button"], [role="tab"], [role="link"], [role="menuitem"], [role="checkbox"], [role="switch"], [role="combobox"]';
  for (const el of document.querySelectorAll(interaktif)) {
    if (tumpang.length >= 30) break;
    if (!terlihat(el)) continue;
    const r = el.getBoundingClientRect(); const x = r.left + r.width / 2, y = r.top + r.height / 2;
    if (x < 0 || y < 0 || x >= innerWidth || y >= innerHeight) continue;
    const atas = document.elementFromPoint(x, y);
    if (!atas || atas === el || el.contains(atas) || atas.contains(el)) continue;
    const k = sel(el) + "|" + sel(atas); if (sudah.has(k)) continue; sudah.add(k);
    tumpang.push({ a: sel(el), b: sel(atas) });
  }
  const disabled = [];
  for (const el of document.querySelectorAll('button:disabled, input:disabled, [aria-disabled="true"]')) {
    if (disabled.length >= 40) break;
    if (!terlihat(el)) continue;
    const cs = getComputedStyle(el);
    disabled.push({ teks: (el.innerText || el.value || el.getAttribute("aria-label") || "").trim().slice(0, 80), opacity: cs.opacity, pointerEvents: cs.pointerEvents });
  }
  const teks = document.body ? document.body.innerText : "";
  const kls = de.classList;
  return {
    rute_akhir: location.pathname + location.search,
    tema_terbukti: kls.contains("dark") ? "dark" : kls.contains("light") ? "light" : "",
    error_boundary: ${JSON.stringify(TEKS_BOUNDARY)}.some((t) => teks.includes(t)),
    ukuran: { luber_halaman, luber_wadah, tumpang, disabled },
  };
})()`;

function jsCariTeks(teks, peran) {
  // Pilih lewat teks, utamakan yang di luar sidebar: querySelector polos mengambil tautan sidebar
  // yang muncul lebih dulu di DOM dan klik tampak berhasil di elemen yang salah.
  return `(() => {
    const pola = ${peran === "tab" ? JSON.stringify('[role="tab"]') : JSON.stringify('button, a, [role="button"], [role="tab"], [role="menuitem"], [role="option"], label')};
    const cocok = [...document.querySelectorAll(pola)].filter((e) => {
      const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && (e.innerText || "").trim() === ${JSON.stringify(teks)}; });
    const el = cocok.find((e) => !e.closest('[data-sidebar], aside, nav')) || cocok[0];
    if (!el) return null;
    el.scrollIntoView({ block: "center", inline: "center" });
    const r = el.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  })()`;
}

async function nilai(cdp, ekspresi) {
  const h = await cdp.kirim("Runtime.evaluate", { expression: ekspresi, returnByValue: true, awaitPromise: true });
  if (h.exceptionDetails) throw new Error("evaluasi gagal: " + (h.exceptionDetails.exception?.description || h.exceptionDetails.text));
  return h.result?.value;
}

async function klik(cdp, x, y) {
  await cdp.kirim("Input.dispatchMouseEvent", { type: "mouseMoved", x, y });
  await cdp.kirim("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", clickCount: 1 });
  await cdp.kirim("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", clickCount: 1 });
}

async function tutupOverlay(cdp, denganEscape) {
  // Overlay ajakan/panduan muncul beberapa detik SESUDAH muat dan menelan klik pertama, jadi
  // diulang beberapa putaran, bukan sekali.
  for (let putaran = 0; putaran < 3; putaran++) {
    if (denganEscape) {
      await cdp.kirim("Input.dispatchKeyEvent", { type: "keyDown", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 });
      await cdp.kirim("Input.dispatchKeyEvent", { type: "keyUp", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 });
    }
    for (const t of TOMBOL_OVERLAY) {
      const titik = await nilai(cdp, jsCariTeks(t));
      if (titik) await klik(cdp, titik.x, titik.y);
    }
    await tidur(600);
  }
}

// Tunggu jaringan tenang: menangkap di tengah retry React Query memotret Skeleton dan terbaca
// seperti layar rusak. Jeda antar-retry 1, 2, lalu 4 dtk, jadi jendela tenang 1 dtk berakhir DI
// DALAM jeda itu (terukur di uji asap /hris/resign). Selama ada 5xx baru-baru ini, jendela
// tenangnya dipanjangkan melewati jeda terpanjang.
async function tungguTenang(ctx, maksMs) {
  const batas = Date.now() + maksMs;
  let tenangSejak = Date.now();
  while (Date.now() < batas) {
    const perlu = Date.now() - ctx.terakhir5xx < 8000 ? 4500 : 1000;
    if (ctx.dalamPerjalanan.size > 0) tenangSejak = Date.now();
    else if (Date.now() - tenangSejak >= perlu) return;
    await tidur(150);
  }
}

function formatBingkai(st) {
  return (st?.callFrames || []).slice(0, 15).map((f) => `    at ${f.functionName || "<anonim>"} (${f.url}:${f.lineNumber + 1}:${f.columnNumber + 1})`);
}

async function tangkapEntri(chrome, cfg, entri) {
  const hasil = {
    path: entri.path, keadaan: entri.keadaan, lebar: entri.lebar, tema: entri.tema,
    png: null, rute_akhir: "", status_http: 0, error_boundary: false, konsol: [], galat: null,
    tema_terbukti: "", ukuran: { luber_halaman: false, luber_wadah: [], tumpang: [], disabled: [] }, api: [], png_segmen: [],
  };
  const target = await ambilJson(`http://127.0.0.1:${chrome.port}/json/new?about:blank`, { method: "PUT" }, 10000);
  const cdp = await Cdp.buka(target.webSocketDebuggerUrl);
  const ctx = { dalamPerjalanan: new Set(), terakhir5xx: 0 };
  const asal = new URL(cfg.urlDasar).origin;
  const dicegat = (u) => { try { const x = new URL(u); return x.origin !== asal || x.pathname.startsWith("/api/"); } catch { return false; } };
  const tambahKonsol = (s) => { if (hasil.konsol.length < BATAS_KONSOL) hasil.konsol.push(String(s).slice(0, 4000)); };
  try {
    let frameUtama = null;
    cdp.on("Runtime.consoleAPICalled", (p) => {
      if (p.type !== "error" && p.type !== "assert") return;
      const teks = (p.args || []).map((a) => a.value !== undefined ? (typeof a.value === "string" ? a.value : JSON.stringify(a.value)) : (a.description || a.unserializableValue || "")).join(" ");
      tambahKonsol([teks, ...formatBingkai(p.stackTrace)].join("\n"));
    });
    cdp.on("Runtime.exceptionThrown", (p) => {
      const d = p.exceptionDetails || {};
      const baris = [d.exception?.description || d.text || "pengecualian"];
      if (d.url) baris.push(`    di ${d.url}:${(d.lineNumber ?? 0) + 1}:${(d.columnNumber ?? 0) + 1}`);
      tambahKonsol([...baris, ...formatBingkai(d.stackTrace)].join("\n"));
    });
    cdp.on("Log.entryAdded", (p) => {
      const e = p.entry || {};
      // 500 dari stub yang disengaja bukan berita; galat jaringan ke aset lokal (chunk hilang) iya.
      if (e.level === "error" && !(e.url && dicegat(e.url))) tambahKonsol(`${e.text}${e.url ? " (" + e.url + ")" : ""}`);
    });
    cdp.on("Network.requestWillBeSent", (p) => ctx.dalamPerjalanan.add(p.requestId));
    cdp.on("Network.loadingFinished", (p) => ctx.dalamPerjalanan.delete(p.requestId));
    cdp.on("Network.loadingFailed", (p) => ctx.dalamPerjalanan.delete(p.requestId));
    // status_http = respons DOKUMEN bingkai utama yang terakhir, bukan sub-permintaan.
    cdp.on("Network.responseReceived", (p) => {
      if (p.type === "Document" && (!frameUtama || p.frameId === frameUtama)) hasil.status_http = p.response?.status ?? 0;
    });
    cdp.on("Fetch.requestPaused", async (p) => {
      const req = p.request || {};
      try {
        if (!dicegat(req.url)) { await cdp.kirim("Fetch.continueRequest", { requestId: p.requestId }); return; }
        const cors = [
          { name: "Access-Control-Allow-Origin", value: asal },
          { name: "Access-Control-Allow-Credentials", value: "true" },
          { name: "Access-Control-Allow-Methods", value: "GET, POST, PUT, PATCH, DELETE, OPTIONS" },
          { name: "Access-Control-Allow-Headers", value: header(req, "Access-Control-Request-Headers") || "authorization, content-type, x-requested-with" },
          { name: "Vary", value: "Origin" },
        ];
        if (req.method === "OPTIONS") {
          await cdp.kirim("Fetch.fulfillRequest", { requestId: p.requestId, responseCode: 204, responseHeaders: cors, body: "" });
          return;
        }
        const u = new URL(req.url);
        const stub = cariStub(cfg.stubKeadaan, u);
        let status, body, sumber;
        if (/\/employee\/me\/?$/.test(u.pathname)) {
          // Selalu 200: profil yang gagal membuat halaman mentok di Skeleton selamanya.
          status = 200; sumber = stub ? "stub" : "bawaan";
          body = stub ? stub.body : cfg.profil;
        } else if (stub) {
          // 401 tak pernah dikirim walau manifest menulisnya (validasi menolaknya; ini penjaga kedua).
          status = stub.status === 401 ? 500 : (Number.isInteger(stub.status) ? stub.status : 200);
          body = stub.body; sumber = "stub";
        } else {
          status = 500; body = { message: "tidak distub (tangkap-layar)" }; sumber = "tak-distub";
        }
        if (status >= 500) ctx.terakhir5xx = Date.now();
        if (hasil.api.length < 100) hasil.api.push({ metode: req.method, url: req.url.slice(0, 300), status, sumber });
        const teks = typeof body === "string" ? body : JSON.stringify(body ?? null);
        await cdp.kirim("Fetch.fulfillRequest", {
          requestId: p.requestId, responseCode: status,
          responseHeaders: [...cors, { name: "Content-Type", value: "application/json; charset=utf-8" }],
          body: Buffer.from(teks, "utf8").toString("base64"),
        });
      } catch { /* target ditutup di tengah permintaan */ }
    });

    await cdp.kirim("Page.enable");
    await cdp.kirim("Runtime.enable");
    await cdp.kirim("Network.enable");
    await cdp.kirim("Log.enable");
    await cdp.kirim("Fetch.enable", { patterns: [{ urlPattern: "*", requestStage: "Request" }] });
    frameUtama = (await cdp.kirim("Page.getFrameTree")).frameTree?.frame?.id || null;
    await cdp.kirim("Emulation.setDeviceMetricsOverride", { width: entri.lebar, height: entri.tinggi, deviceScaleFactor: 1, mobile: entri.mobile });
    await cdp.kirim("Page.addScriptToEvaluateOnNewDocument", {
      source: `try { localStorage.setItem("theme", ${JSON.stringify(entri.tema)}); } catch (e) {}`,
    });
    for (const [nama, nilaiCookie] of Object.entries(cfg.cookie)) {
      await cdp.kirim("Network.setCookie", { name: nama, value: nilaiCookie, url: cfg.urlDasar, path: "/" });
    }

    const muat = new Promise((res) => cdp.on("Page.loadEventFired", res));
    // Navigasi LANGSUNG ke rute tujuan: singgah ke /login menghapus cookie sesi (useEffect logout).
    const nav = await cdp.kirim("Page.navigate", { url: cfg.urlDasar + entri.path });
    if (nav.errorText) { hasil.galat = "navigasi gagal: " + nav.errorText; return hasil; }
    await Promise.race([muat, tidur(30000)]);
    await tungguTenang(ctx, 20000);
    await tidur(1200);
    await tutupOverlay(cdp, true);

    for (const aksi of entri.aksi || []) {
      const teks = aksi.klik_teks ?? aksi.tab;
      const titik = typeof teks === "string" ? await nilai(cdp, jsCariTeks(teks, aksi.tab !== undefined ? "tab" : "")) : null;
      if (!titik) { hasil.galat = "aksi tidak menemukan elemen: " + JSON.stringify(aksi); break; }
      await tidur(300);
      await klik(cdp, titik.x, titik.y);
      // Animasi buka Radix (zoom/slide) sekitar 1 dtk; mengukur di tengahnya salah ukur.
      await tidur(1200);
      await tungguTenang(ctx, 8000);
    }
    if (entri.aksi?.length) await tutupOverlay(cdp, false); // tanpa Escape: menutup sheet hasil aksi
    await cdp.kirim("Runtime.evaluate", { expression: "window.scrollTo(0, 0)" });

    const ukur = await nilai(cdp, JS_UKUR);
    Object.assign(hasil, { rute_akhir: ukur.rute_akhir, tema_terbukti: ukur.tema_terbukti, error_boundary: ukur.error_boundary, ukuran: ukur.ukuran });
    const foto = await cdp.kirim("Page.captureScreenshot", { format: "png" });
    const nama = `${entri.nomor}-${entri.keadaan}-${entri.lebar}-${entri.tema}.png`;
    const tujuan = path.join(cfg.keluaran, nama);
    fs.writeFileSync(tujuan, Buffer.from(foto.data, "base64"));
    hasil.png = path.resolve(tujuan);
    // Halaman panjang: segmen tambahan lewat gulir jendela, tetap tangkapan viewport (bukan
    // captureBeyondViewport, yang merusak Recharts). Wadah gulir dalam tidak ikut digulir.
    for (let seg = 2; seg <= SEGMEN_MAKS; seg++) {
      const geser = await nilai(cdp, `(() => { const s = document.scrollingElement; const sebelum = s.scrollTop;
        s.scrollTop = sebelum + Math.floor(innerHeight * 0.9); return s.scrollTop - sebelum; })()`);
      if (!(geser > 40)) break;
      await tidur(500);
      const f = await cdp.kirim("Page.captureScreenshot", { format: "png" });
      const t = path.join(cfg.keluaran, nama.replace(/\.png$/, `-s${seg}.png`));
      fs.writeFileSync(t, Buffer.from(f.data, "base64"));
      hasil.png_segmen.push(path.resolve(t));
    }
    return hasil;
  } finally {
    cdp.tutup();
    try { await ambilJson(`http://127.0.0.1:${chrome.port}/json/close/${target.id}`, {}, 5000); } catch { /* jawaban /json/close bukan JSON */ }
  }
}

function daftarEntri(manifest) {
  const keluaran = [];
  (manifest.rute || []).forEach((r, i) => {
    const semua = Array.isArray(r.keadaan) && r.keadaan.length ? r.keadaan : Object.keys(manifest.stub || {});
    // Keadaan utama (berisi bila ada) mendapat matriks penuh; keadaan lain desktop terang saja
    // supaya jumlah tangkapan tidak meledak.
    const utama = semua.includes("berisi") ? "berisi" : semua[0];
    for (const k of [utama, ...semua.filter((x) => x !== utama)]) {
      const matriks = k === utama ? MATRIKS_PENUH : [MATRIKS_PENUH[0]];
      for (const m of matriks) keluaran.push({ nomor: i + 1, path: r.path, keadaan: k, aksi: r.aksi || [], ...m });
    }
  });
  return keluaran;
}

function siapkanCookie(manifest) {
  const c = manifest.cookie || {};
  const enc = (v) => encodeURIComponent(typeof v === "string" ? v : JSON.stringify(v));
  const idUji = "UJI-0001";
  const hasil = {
    token: buatJwt(idUji), refreshToken: buatJwt(idUji), employee_id: idUji, username: "pengguna.uji",
    system_roles: enc(c.system_roles || {}), lang: enc(c.lang || "id"),
  };
  if (c.position !== undefined) hasil.position = enc(c.position);
  if (c.department !== undefined) hasil.department = enc(c.department);
  return hasil;
}

async function utama() {
  const a = bacaArgumen(process.argv.slice(2));
  if (!a.keluaran) { console.error("tangkap-layar: --keluaran wajib"); return 1; }
  fs.mkdirSync(a.keluaran, { recursive: true });
  const ringkasan = { url_dasar: a.urlDasar || "", rute: [], galat: null };
  const gagal = (pesan) => { ringkasan.galat = pesan; tulisRingkasan(a.keluaran, ringkasan); return 0; };
  if (!a.urlDasar || !a.manifest) return gagal("argumen --url-dasar dan --manifest wajib");

  let manifest;
  try { manifest = JSON.parse(fs.readFileSync(a.manifest, "utf8").replace(/^\uFEFF/, "")); }
  catch (e) { return gagal("manifest tidak terbaca: " + e.message); }
  if (!Array.isArray(manifest.rute) || !manifest.rute.length) return gagal("manifest tanpa rute");

  const exe = a.chrome || CHROME_BAWAAN.find((p) => fs.existsSync(p));
  if (!exe || !fs.existsSync(exe)) return gagal("chrome tidak ditemukan");
  const induk = process.env.TANGKAP_LAYAR_PROFIL_DASAR || os.tmpdir();
  fs.mkdirSync(induk, { recursive: true });
  const profil = path.join(induk, `tangkap-layar-profil-${process.pid}-${Math.random().toString(36).slice(2, 8)}`);

  let chrome = null;
  const bersihkan = () => { bunuhChrome(chrome, profil); };
  for (const sinyal of ["SIGINT", "SIGTERM", "SIGBREAK"]) process.on(sinyal, () => { bersihkan(); process.exit(1); });
  try {
    chrome = await nyalakanChrome(exe, profil);
    if (!chrome.versi) return gagal("chrome tidak menjawab /json/version dalam 60 dtk");
    const profilUji = {
      employee_id: "UJI-0001", full_name: "Pengguna Uji", account_type: "internal",
      work_data: { position: manifest.cookie?.position || "", department: manifest.cookie?.department || "" },
    };
    for (const e of daftarEntri(manifest)) {
      const cfg = {
        urlDasar: a.urlDasar.replace(/\/$/, ""), keluaran: a.keluaran, profil: profilUji,
        cookie: siapkanCookie(manifest), stubKeadaan: (manifest.stub || {})[e.keadaan] || [],
      };
      let hasil;
      const batasMs = a.batasRuteDetik * 1000;
      try {
        hasil = await Promise.race([
          tangkapEntri(chrome, cfg, e),
          tidur(batasMs).then(() => { throw new Error(`batas waktu rute habis (${a.batasRuteDetik} dtk)`); }),
        ]);
      } catch (err) {
        hasil = { path: e.path, keadaan: e.keadaan, lebar: e.lebar, tema: e.tema, png: null, rute_akhir: "", status_http: 0,
          error_boundary: false, konsol: [], galat: String(err.message || err), tema_terbukti: "",
          ukuran: { luber_halaman: false, luber_wadah: [], tumpang: [], disabled: [] }, api: [], png_segmen: [] };
      }
      ringkasan.rute.push(hasil);
      tulisRingkasan(a.keluaran, ringkasan);
      console.error(`tangkap-layar: ${e.path} ${e.keadaan} ${e.lebar} ${e.tema} -> ${hasil.galat || "ok"} (status ${hasil.status_http})`);
    }
    tulisRingkasan(a.keluaran, ringkasan);
    return 0;
  } catch (err) {
    return gagal("tangkap-layar gagal: " + (err.message || err));
  } finally {
    bersihkan();
  }
}

utama().then((rc) => process.exit(rc), (err) => { console.error(err); process.exit(1); });
