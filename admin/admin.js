/* =====================================================================
   Administrácia – Fürsten Reality (Mária Fürsten)
   Dáta sú v GitHub repozitári (_data/*.json). Uloženie = jeden commit cez
   spoločný backend WebHunter (webhunter-admin); GitHub Action web pregeneruje.
   ===================================================================== */
'use strict';
(() => {
const CFG = {
  id: 'fursten', repo: 'webhunter-navrhy/fursten-reality', site: '../',
  api: /^(localhost|127\.0\.0\.1)$/.test(location.hostname) ? 'http://localhost:8787' : 'https://webhunter-admin.webhunter.workers.dev',
};
const FILES = { site: '_data/site.json', listings: '_data/listings.json', reviews: '_data/reviews.json' };
const LABEL = { site: 'Texty a nastavenia webu', listings: 'Nehnuteľnosti', reviews: 'Referencie' };
const STATUSES = [['aktualne', 'Aktuálne'], ['rezervovane', 'Rezervované'], ['predane', 'Predané'], ['prenajate', 'Prenajaté']];
const STATUS_L = Object.fromEntries(STATUSES);
const KINDS = [['predaj', 'Predaj'], ['prenajom', 'Prenájom']];
const TYPES = ['Byt', 'Rodinný dom', 'Pozemok', 'Chata / chalupa', 'Komerčný priestor'];
const PARAMS = [['rooms', 'Počet izieb', 'napr. 3'], ['area_usable', 'Úžitková / obytná plocha', 'napr. 72 m²'], ['area_built', 'Zastavaná plocha', 'napr. 118 m²'],
  ['area_plot', 'Plocha pozemku', 'napr. 1 050 m²'], ['floor', 'Poschodie', 'napr. 3. poschodie z 8, výťah'], ['condition', 'Stav', 'napr. po rekonštrukcii'],
  ['building', 'Konštrukcia', 'napr. tehla'], ['year', 'Rok výstavby / kolaudácie', 'napr. kolaudácia 2005'], ['utilities', 'Inžinierske siete', 'napr. voda, elektrina, plyn, kanalizácia'],
  ['heating', 'Vykurovanie', 'napr. plynový kotol, podlahové'], ['parking', 'Parkovanie', 'napr. garáž, 2 miesta na pozemku'], ['costs', 'Mesačné náklady', 'napr. 180 € / mesiac vrátane energií'],
  ['energy', 'Energetický certifikát', 'napr. B'], ['ownership', 'Vlastníctvo', 'napr. osobné'], ['available', 'Voľné od', 'napr. ihneď'], ['extras', 'Ďalej k dispozícii', 'napr. balkón, pivnica, terasa']];
const TYPE_PARAMS = {
  'Byt': ['rooms', 'area_usable', 'floor', 'condition', 'building', 'heating', 'parking', 'costs', 'energy', 'ownership', 'available', 'extras'],
  'Rodinný dom': ['rooms', 'area_usable', 'area_built', 'area_plot', 'condition', 'building', 'year', 'utilities', 'heating', 'parking', 'costs', 'energy', 'ownership', 'available', 'extras'],
  'Pozemok': ['area_plot', 'utilities', 'parking', 'ownership', 'available', 'extras'],
  'Chata / chalupa': ['rooms', 'area_usable', 'area_plot', 'condition', 'building', 'year', 'utilities', 'heating', 'parking', 'ownership', 'extras'],
  'Komerčný priestor': ['area_usable', 'area_plot', 'floor', 'condition', 'building', 'utilities', 'heating', 'parking', 'costs', 'energy', 'ownership', 'available', 'extras'],
};
const LS = 'fr_';

const S = { sess: null, schema: [], D: {}, snap: {}, pending: {}, preview: {}, def: false, saving: false,
            lf: { status: 'all', q: '' }, pub: { state: 'off', text: '' } };

/* ------------------------------------------------------------ icons */
const I = (d, extra = '') => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" ${extra}>${d}</svg>`;
const IC = {
  home: I('<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>'),
  dash: I('<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>'),
  building: I('<path d="M3 21h18"/><path d="M5 21V8l7-5 7 5v13"/><path d="M9 21v-5h6v5"/><path d="M10 11h4"/>'),
  pen: I('<path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/>'),
  star: I('<path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z"/>'),
  starF: I('<path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z" fill="currentColor"/>'),
  text: I('<path d="M4 6h16M4 12h10M4 18h14"/>'),
  phone: I('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>'),
  gear: I('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'),
  ext: I('<path d="M14 4h6v6"/><path d="M20 4L10 14"/><path d="M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>'),
  plus: I('<path d="M12 5v14M5 12h14"/>'),
  drag: I('<circle cx="9" cy="6" r="1"/><circle cx="15" cy="6" r="1"/><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/><circle cx="9" cy="18" r="1"/><circle cx="15" cy="18" r="1"/>'),
  eye: I('<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/>'),
  eyeOff: I('<path d="M17.9 17.9A10.5 10.5 0 0 1 12 19c-7 0-11-7-11-7a18.7 18.7 0 0 1 5.1-5.9M9.9 5.2A9.9 9.9 0 0 1 12 5c7 0 11 7 11 7a18.5 18.5 0 0 1-2.2 3.2M14.1 14.1a3 3 0 1 1-4.2-4.2"/><path d="M1 1l22 22"/>'),
  trash: I('<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M6 6l1 14h10l1-14"/>'),
  copy: I('<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/>'),
  up: I('<path d="M12 19V5M5 12l7-7 7 7"/>'),
  down: I('<path d="M12 5v14M19 12l-7 7-7-7"/>'),
  x: I('<path d="M18 6L6 18M6 6l12 12"/>', 'stroke-width="2.4"'),
  upload: I('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M17 8l-5-5-5 5"/><path d="M12 3v12"/>'),
  image: I('<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>'),
  check: I('<path d="M20 6L9 17l-5-5"/>'),
  alert: I('<path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h0"/>'),
  info: I('<circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h0"/>'),
  logout: I('<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="M16 17l5-5-5-5"/><path d="M21 12H9"/>'),
  menu: I('<path d="M3 6h18M3 12h18M3 18h18"/>'),
  search: I('<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>'),
  chev: I('<path d="M6 9l6 6 6-6"/>'),
  lock: I('<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>'),
  link: I('<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>'),
  download: I('<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/>'),
  quote: I('<path d="M3 21c3 0 7-1 7-8V5H3v7h4c0 3-2 5-4 5z"/><path d="M14 21c3 0 7-1 7-8V5h-7v7h4c0 3-2 5-4 5z"/>'),
};
IC.key = I('<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M17 6l3 3M15 8l2 2"/>');
IC.shield = I('<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>');

/* ------------------------------------------------------------ utils */
const $ = (s, c = document) => c.querySelector(s);
const $$ = (s, c = document) => [...c.querySelectorAll(s)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const slugify = (s) => String(s || '').normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70);
const today = () => new Date().toISOString().slice(0, 10);
const skDate = (d) => { const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(d || ''); return m ? `${+m[3]}. ${+m[2]}. ${m[1]}` : (d || ''); };
const ago = (iso) => { if (!iso) return ''; const s = (Date.now() - new Date(iso)) / 1000; if (s < 60) return 'práve teraz'; if (s < 3600) return `pred ${Math.round(s / 60)} min`; if (s < 86400) return `pred ${Math.round(s / 3600)} h`; return skDate(iso); };
const debounce = (fn, ms) => { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; };
const move = (arr, from, to) => { if (to < 0 || to >= arr.length || from === to) return; arr.splice(to, 0, arr.splice(from, 1)[0]); };
const src = (p) => !p ? '' : (S.preview[p] || (/^(https?:|data:|blob:)/.test(p) ? p : CFG.site + p));
const clone = (o) => JSON.parse(JSON.stringify(o));
const uid = () => Math.random().toString(36).slice(2, 8);
const plural = (n, a, b, c) => `${n} ${n === 1 ? a : n > 1 && n < 5 ? b : c}`;
const isTodo = (v) => !String(v ?? '').trim() || /\[DOPLNI/.test(String(v));

function toast(title, sub = '', type = '') {
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.innerHTML = `<span><b>${esc(title)}</b>${sub ? `<small>${esc(sub)}</small>` : ''}</span>`;
  $('#toasts').appendChild(el);
  setTimeout(() => { el.style.transition = 'opacity .4s'; el.style.opacity = '0'; setTimeout(() => el.remove(), 450); }, type === 'err' ? 7000 : 4200);
}

function modal({ title, body, actions = [], wide = false, onMount }) {
  return new Promise((resolve) => {
    const root = $('#modal-root');
    const bg = document.createElement('div');
    bg.className = 'modal-bg';
    bg.innerHTML = `<div class="modal${wide ? ' wide' : ''}" role="dialog" aria-modal="true"><div class="modal-h"><h3>${title}</h3><button class="icon-btn" data-close aria-label="Zavrieť">${IC.x}</button></div>
      <div class="modal-b">${body}</div>${actions.length ? `<div class="modal-f">${actions.map((a, i) => `<button class="btn ${a.cls || 'btn-ghost'}" data-a="${i}">${a.label}</button>`).join('')}</div>` : ''}</div>`;
    const close = (v) => { bg.remove(); document.removeEventListener('keydown', onKey); resolve(v); };
    const onKey = (e) => { if (e.key === 'Escape') close(null); };
    bg.addEventListener('click', (e) => {
      if (e.target === bg || e.target.closest('[data-close]')) return close(null);
      const b = e.target.closest('[data-a]');
      if (b) { const a = actions[+b.dataset.a]; const v = a.value !== undefined ? a.value : (a.get ? a.get(bg) : true); if (v === false) return; close(v); }
    });
    document.addEventListener('keydown', onKey);
    root.appendChild(bg);
    if (onMount) onMount(bg, close);
    const f = bg.querySelector('input,textarea,select'); if (f) setTimeout(() => f.focus(), 50);
  });
}
const confirmDlg = (title, text, ok = 'Zmazať', cls = 'btn-danger') => modal({ title, body: `<p>${text}</p>`, actions: [{ label: 'Zrušiť', value: false }, { label: ok, cls, value: true }] }).then((v) => v === true);

/* ------------------------------------------------------------ server (WebHunter admin API) */
const b64e = (bytes) => { let s = ''; bytes = new Uint8Array(bytes); for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000)); return btoa(s); };
const utf8b64 = (str) => b64e(new TextEncoder().encode(str));
function saveSess() { localStorage.setItem(LS + 'sess_' + CFG.id, JSON.stringify({ t: S.sess, def: S.def, exp: Date.now() + 11.5 * 3600e3 })); }
async function api(path, opt = {}, retried = false) {
  const headers = { ...(opt.body && typeof opt.body === 'string' ? { 'Content-Type': 'application/json' } : {}), ...(opt.headers || {}) };
  if (S.sess) headers.Authorization = 'Bearer ' + S.sess;
  let r;
  try { r = await fetch(`${CFG.api}/api/${CFG.id}${path}`, { ...opt, headers, cache: 'no-store' }); }
  catch { throw new Error('Nedá sa spojiť so serverom administrácie. Skontrolujte pripojenie na internet.'); }
  if (r.status === 401 && path !== '/login' && !retried && S.D.site) {
    if (await reauth()) return api(path, opt, true);
  }
  if (!r.ok) { let m = r.statusText; try { m = (await r.json()).error || m; } catch {} const e = new Error(m); e.status = r.status; throw e; }
  return opt.raw ? r.text() : r.json();
}
const readFile = (path) => api('/file?path=' + encodeURIComponent(path) + '&t=' + Date.now(), { raw: true });
async function commit(files, message) {
  const out = []; const queue = [...files];
  const worker = async () => {
    while (queue.length) {
      const f = queue.shift();
      const { sha } = await api('/blob', { method: 'POST', body: JSON.stringify({ content: f.b64 ?? utf8b64(f.content), encoding: 'base64' }) });
      out.push({ path: f.path, sha });
    }
  };
  await Promise.all([worker(), worker(), worker()]);
  return (await api('/commit', { method: 'POST', body: JSON.stringify({ files: out, message }) })).sha;
}

/* ------------------------------------------------------------ data + dirty state */
async function loadAll() {
  const [schema, ...files] = await Promise.all([
    fetch('schema.json?t=' + Date.now(), { cache: 'no-store' }).then((r) => r.json()),
    ...Object.values(FILES).map((p) => readFile(p).then(JSON.parse)),
  ]);
  S.schema = schema.schema;
  Object.keys(FILES).forEach((k, i) => { S.D[k] = files[i]; });
  if (Array.isArray(S.D.site) || !S.D.site) S.D.site = {};
  for (const p of S.schema) for (const sec of p.sections) for (const f of sec.fields) if (!(f.key in S.D.site)) S.D.site[f.key] = clone(f.default);
  snapshot();
}
function snapshot(keys = Object.keys(FILES)) { keys.forEach((k) => { S.snap[k] = JSON.stringify(S.D[k]); }); }
const dirtyKeys = () => Object.keys(FILES).filter((k) => JSON.stringify(S.D[k]) !== S.snap[k]);
const changed = debounce(() => updateSavebar(), 120);
function discard() { dirtyKeys().forEach((k) => { S.D[k] = JSON.parse(S.snap[k]); }); updateSavebar(); route(); toast('Zmeny zahodené'); }
window.addEventListener('beforeunload', (e) => { if (dirtyKeys().length) { e.preventDefault(); e.returnValue = ''; } });

function validate() {
  const slugs = new Set();
  for (const x of S.D.listings) {
    if (!x.title?.trim()) return 'Nehnuteľnosť bez názvu – doplňte názov.';
    if (!/^[a-z0-9][a-z0-9_-]*$/.test(x.slug || '')) return `Nehnuteľnosť „${x.title}“ má neplatnú adresu (URL). Použite malé písmená, čísla a pomlčky.`;
    if (slugs.has(x.slug)) return `Dve nehnuteľnosti majú rovnakú adresu „${x.slug}“.`;
    slugs.add(x.slug);
  }
  return null;
}

async function saveAll() {
  const keys = dirtyKeys();
  if (!keys.length || S.saving) return;
  const err = validate(); if (err) return toast('Nedá sa uložiť', err, 'err');
  S.saving = true; updateSavebar();
  const bar = document.createElement('div'); bar.className = 'progress-line'; document.body.appendChild(bar);
  try {
    const files = keys.map((k) => ({ path: FILES[k], content: JSON.stringify(S.D[k], null, 1) + '\n' }));
    const used = JSON.stringify(S.D);
    // image + its 900px "-m" variant go together
    const imgs = Object.keys(S.pending).filter((p) => used.includes(p) || used.includes(p.replace(/-m\.(webp|jpg)$/, '.$1')));
    imgs.forEach((p) => files.push({ path: p, b64: S.pending[p] }));
    const main = imgs.filter((p) => !/-m\.(webp|jpg)$/.test(p)).length;
    const sha = await commit(files, keys.map((k) => LABEL[k]).join(', ') + (main ? ` (+${plural(main, 'obrázok', 'obrázky', 'obrázkov')})` : ''));
    imgs.forEach((p) => delete S.pending[p]);
    snapshot(keys);
    toast('Uložené', 'Zmeny sa na webe objavia približne o minútu.', 'ok');
    watchPublish(sha);
  } catch (e) {
    toast('Uloženie sa nepodarilo', e.message, 'err');
  } finally { S.saving = false; bar.remove(); updateSavebar(); }
}

/* ------------------------------------------------------------ publish watcher */
let pubTimer = null;
function setPub(state, text) { S.pub = { state, text }; const el = $('.pub'); if (el) { el.className = 'pub ' + state; el.innerHTML = `<i></i><span>${esc(text)}</span>`; } }
function watchPublish(sha) {
  localStorage.setItem(LS + 'pub', JSON.stringify({ sha, t: Date.now() }));
  clearInterval(pubTimer);
  setPub('busy', 'Zverejňujem zmeny…');
  const started = Date.now();
  pubTimer = setInterval(async () => {
    try {
      const v = await fetch(CFG.site + 'version.json?t=' + Date.now(), { cache: 'no-store' }).then((r) => r.json());
      if (v.sha === sha) { clearInterval(pubTimer); localStorage.removeItem(LS + 'pub'); setPub('', 'Web je aktuálny'); toast('Zmeny sú na webe', 'Web bol práve aktualizovaný.', 'ok'); return; }
    } catch {}
    if (Date.now() - started > 8 * 60000) { clearInterval(pubTimer); setPub('warn', 'Zverejnenie trvá dlhšie'); }
  }, 6000);
}
function initPub() {
  const p = JSON.parse(localStorage.getItem(LS + 'pub') || 'null');
  if (p && Date.now() - p.t < 10 * 60000) watchPublish(p.sha); else setPub('', 'Web je aktuálny');
}

/* ------------------------------------------------------------ images */
async function toBlob(bmp, max) {
  const sc = Math.min(1, max / Math.max(bmp.width, bmp.height));
  const w = Math.round(bmp.width * sc), h = Math.round(bmp.height * sc);
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  c.getContext('2d').drawImage(bmp, 0, 0, w, h);
  let blob = await new Promise((r) => c.toBlob(r, 'image/webp', 0.82)), ext = 'webp';
  if (!blob || blob.type !== 'image/webp') { blob = await new Promise((r) => c.toBlob(r, 'image/jpeg', 0.86)); ext = 'jpg'; }
  return { blob, ext };
}
async function upload(file, hint = '') {
  let bmp;
  try { bmp = await createImageBitmap(file); } catch { throw new Error(`Súbor „${file.name}“ sa nedá načítať. Použite JPG, PNG alebo WebP.`); }
  const big = await toBlob(bmp, 2000), small = await toBlob(bmp, 900);
  const d = new Date();
  const name = (slugify(hint) || slugify(file.name.replace(/\.[^.]+$/, '')) || 'foto').slice(0, 40);
  const base = `img/uploads/${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}/${name}-${uid()}`;
  const path = `${base}.${big.ext}`, pathM = `${base}-m.${small.ext}`;
  S.pending[path] = b64e(await big.blob.arrayBuffer());
  if (small.ext === big.ext) S.pending[pathM] = b64e(await small.blob.arrayBuffer());
  S.preview[path] = URL.createObjectURL(big.blob);
  return path;
}
async function uploadMany(files, hint) {
  const out = [];
  for (const f of files) {
    if (!f.type.startsWith('image/') && !/\.(heic|jpe?g|png|webp)$/i.test(f.name)) continue;
    try { out.push(await upload(f, hint)); } catch (e) { toast('Obrázok sa nepodarilo načítať', e.message, 'err'); }
  }
  return out;
}
function allImages() {
  const set = new Set(Object.keys(S.pending).filter((p) => !/-m\.(webp|jpg)$/.test(p)));
  const re = /img\/[A-Za-z0-9_\-/.]+\.(?:webp|png|jpe?g|svg)/g;
  (JSON.stringify(S.D).match(re) || []).forEach((p) => set.add(p));
  return [...set];
}
function pickFromLibrary() {
  const imgs = allImages();
  return modal({
    title: 'Knižnica obrázkov', wide: true,
    body: `<div class="toolbar"><div class="search">${IC.search}<input type="search" placeholder="Hľadať podľa názvu súboru…" data-q></div><span class="muted">${plural(imgs.length, 'obrázok', 'obrázky', 'obrázkov')} na webe</span></div><div class="lib">${imgs.map((p) => `<button data-p="${esc(p)}" title="${esc(p)}"><img src="${esc(src(p))}" loading="lazy" alt=""></button>`).join('')}</div>`,
    onMount: (bg, close) => {
      bg.querySelector('.lib').addEventListener('click', (e) => { const b = e.target.closest('[data-p]'); if (b) close(b.dataset.p); });
      bg.querySelector('[data-q]').addEventListener('input', (e) => { const q = e.target.value.toLowerCase(); $$('.lib button', bg).forEach((b) => { b.style.display = b.dataset.p.toLowerCase().includes(q) ? '' : 'none'; }); });
    },
  });
}

let IP = [];
function imgPick(get, set, opts = {}) {
  const id = IP.push({ get, set, opts }) - 1;
  const v = get();
  return `<div class="img-pick" data-ip="${id}"><div class="pv">${v ? `<img src="${esc(src(v))}" alt="">` : 'Bez obrázka'}</div>
    <div><div class="bts"><button type="button" class="btn btn-ghost btn-sm" data-ipa="up">${IC.upload} Nahrať</button><button type="button" class="btn btn-ghost btn-sm" data-ipa="lib">${IC.image} Z knižnice</button>${v && !opts.required ? `<button type="button" class="btn btn-ghost btn-sm" data-ipa="rm">Odobrať</button>` : ''}</div>
    ${v ? `<div class="path">${esc(v)}</div>` : ''}</div><input type="file" accept="image/*" hidden></div>`;
}
function bindIP(root) {
  $$('.img-pick', root).forEach((el) => {
    const r = IP[+el.dataset.ip]; if (!r) return;
    const refresh = () => { IP[+el.dataset.ip] = r; const tmp = document.createElement('div'); tmp.innerHTML = imgPick(r.get, r.set, r.opts); const n = tmp.firstElementChild; el.replaceWith(n); bindIP(n.parentElement); r.opts.onChange?.(); };
    const file = el.querySelector('input[type=file]');
    el.addEventListener('click', async (e) => {
      const a = e.target.closest('[data-ipa]')?.dataset.ipa; if (!a) return;
      if (a === 'up') file.click();
      if (a === 'lib') { const p = await pickFromLibrary(); if (p) { r.set(p); changed(); refresh(); } }
      if (a === 'rm') { r.set(''); changed(); refresh(); }
    });
    file.addEventListener('change', async () => { const [p] = await uploadMany([...file.files], r.opts.hint); if (p) { r.set(p); changed(); refresh(); } });
  });
}

function galleryHTML(arr, key, contain = false) {
  return `<div class="gal" data-gal="${key}">${arr.map((p, i) => `<div class="gi${contain ? ' contain' : ''}" draggable="true" data-idx="${i}"><img src="${esc(src(p))}" alt="" loading="lazy">${S.pending[p] ? '<span class="new">Nová</span>' : ''}${i === 0 && key === 'photos' ? '<span class="cover">Titulná</span>' : ''}<button type="button" class="x" data-rm="${i}" aria-label="Odobrať">${IC.x}</button></div>`).join('')}</div>
  <label class="drop" data-drop="${key}">${IC.upload}<b>Pretiahnite fotky sem</b> alebo kliknite a vyberte<br><small>Môžete vybrať viac fotiek naraz. Automaticky sa zmenšia a optimalizujú.</small><input type="file" accept="image/*" multiple hidden></label>
  <div class="row-btns" style="margin-top:.6rem"><button type="button" class="btn btn-ghost btn-sm" data-glib="${key}">${IC.image} Pridať z knižnice</button></div>`;
}
function bindGallery(root, obj, key, hint, rerender) {
  const wrap = $(`[data-gal="${key}"]`, root); if (!wrap) return;
  let from = null;
  wrap.addEventListener('dragstart', (e) => { const it = e.target.closest('.gi'); if (!it) return; from = +it.dataset.idx; it.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', String(from)); });
  wrap.addEventListener('dragover', (e) => { const it = e.target.closest('.gi'); if (!it || from === null) return; e.preventDefault(); $$('.gi.over', wrap).forEach((x) => x.classList.remove('over')); it.classList.add('over'); });
  wrap.addEventListener('drop', (e) => { const it = e.target.closest('.gi'); if (!it || from === null) return; e.preventDefault(); move(obj[key], from, +it.dataset.idx); from = null; changed(); rerender(); });
  wrap.addEventListener('dragend', () => { from = null; $$('.gi', wrap).forEach((x) => x.classList.remove('dragging', 'over')); });
  wrap.addEventListener('click', (e) => { const b = e.target.closest('[data-rm]'); if (!b) return; obj[key].splice(+b.dataset.rm, 1); changed(); rerender(); });
  const drop = $(`[data-drop="${key}"]`, root), input = drop.querySelector('input');
  const add = async (files) => { drop.classList.add('over'); drop.querySelector('b').textContent = 'Nahrávam a optimalizujem…'; const ps = await uploadMany(files, hint); obj[key].push(...ps); if (ps.length) { changed(); toast(`Pridané: ${plural(ps.length, 'obrázok', 'obrázky', 'obrázkov')}`, 'Nezabudnite zmeny uložiť.'); } rerender(); };
  input.addEventListener('change', () => add([...input.files]));
  drop.addEventListener('dragover', (e) => { if (from !== null) return; e.preventDefault(); drop.classList.add('over'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('over'));
  drop.addEventListener('drop', (e) => { if (from !== null) return; e.preventDefault(); add([...e.dataTransfer.files]); });
  $(`[data-glib="${key}"]`, root).addEventListener('click', async () => { const p = await pickFromLibrary(); if (p) { obj[key].push(p); changed(); rerender(); } });
}

function sortable(container, sel, onMove) {
  let from = null;
  container.addEventListener('dragstart', (e) => { const it = e.target.closest(sel); if (!it) return; from = +it.dataset.idx; it.classList.add('dragging'); e.dataTransfer.effectAllowed = 'move'; e.dataTransfer.setData('text/plain', String(from)); });
  container.addEventListener('dragover', (e) => { const it = e.target.closest(sel); if (!it || from === null) return; e.preventDefault(); $$(sel + '.over', container).forEach((x) => x.classList.remove('over')); it.classList.add('over'); });
  container.addEventListener('drop', (e) => { const it = e.target.closest(sel); if (!it || from === null) return; e.preventDefault(); const to = +it.dataset.idx; const f = from; from = null; onMove(f, to); });
  container.addEventListener('dragend', () => { from = null; $$(sel, container).forEach((x) => x.classList.remove('dragging', 'over')); });
}

/* rich text (Quill) */
let quillP = null;
function loadQuill() {
  if (quillP) return quillP;
  quillP = new Promise((res, rej) => {
    const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = 'https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.snow.css'; document.head.appendChild(l);
    const s = document.createElement('script'); s.src = 'https://cdn.jsdelivr.net/npm/quill@2.0.3/dist/quill.js'; s.onload = () => res(window.Quill); s.onerror = () => { quillP = null; rej(new Error('Editor textu sa nepodarilo načítať. Skontrolujte pripojenie na internet.')); };
    document.head.appendChild(s);
  });
  return quillP;
}
async function mountRTE(el, html, onChange, placeholder = 'Začnite písať…') {
  el.innerHTML = '<div class="rte-loading"><span class="spin"></span> Načítavam editor textu…</div>';
  try {
    const Quill = await loadQuill();
    if (!el.isConnected) return;
    el.innerHTML = '<div class="rte"><div class="q"></div></div>';
    const q = new Quill(el.querySelector('.q'), { theme: 'snow', placeholder, modules: { toolbar: [[{ header: [3, false] }], ['bold', 'italic'], [{ list: 'ordered' }, { list: 'bullet' }], ['link'], ['clean']] } });
    q.clipboard.dangerouslyPasteHTML(html || '', 'silent'); q.history.clear();
    const tips = { 'ql-bold': 'Tučné', 'ql-italic': 'Kurzíva', 'ql-link': 'Odkaz', 'ql-clean': 'Odstrániť formátovanie' };
    Object.entries(tips).forEach(([c, t]) => $$('.' + c, el).forEach((b) => b.setAttribute('title', t)));
    q.on('text-change', debounce(() => { let h = q.getSemanticHTML().replace(/&nbsp;/g, ' '); if (/^<p>(<br>)?<\/p>$/.test(h) || !q.getText().trim()) h = ''; onChange(h); }, 250));
  } catch (e) { el.innerHTML = `<div class="banner err">${IC.alert}<span><b>Editor sa nenačítal</b>${esc(e.message)}</span></div>`; }
}
const autosize = (ta) => { ta.style.height = 'auto'; ta.style.height = Math.max(ta.scrollHeight + 2, 46) + 'px'; };

/* ------------------------------------------------------------ re-login */
let reauthP = null;
function reauth() {
  if (reauthP) return reauthP;
  reauthP = modal({
    title: 'Prihláste sa prosím znova',
    body: `<p>Z bezpečnostných dôvodov vypršalo prihlásenie. Rozpracované zmeny zostávajú – po prihlásení sa uložia.</p><div class="f" style="margin-top:1rem"><label>Heslo</label><input type="password" data-rpw autocomplete="current-password"></div>`,
    actions: [{ label: 'Zrušiť', value: false }, { label: 'Prihlásiť', cls: 'btn-primary', get: (bg) => ({ pw: bg.querySelector('[data-rpw]').value }) }],
    onMount: (bg) => bg.querySelector('[data-rpw]').addEventListener('keydown', (e) => { if (e.key === 'Enter') bg.querySelector('[data-a="1"]').click(); }),
  }).then(async (v) => {
    if (!v) return false;
    try { const r = await api('/login', { method: 'POST', body: JSON.stringify({ password: v.pw }) }); S.sess = r.token; S.def = r.def; saveSess(); return true; }
    catch (e) { toast('Prihlásenie sa nepodarilo', e.message, 'err'); return false; }
  }).finally(() => { reauthP = null; });
  return reauthP;
}

/* ------------------------------------------------------------ LOGIN */
function renderLogin(msg = '') {
  document.title = 'Prihlásenie – Administrácia Fürsten Reality';
  $('#app').innerHTML = `<div class="login">
    <div class="login-art"><div class="rings"><span></span><span></span><span></span><span></span></div>
      <img class="logo" src="../img/site/logo-light.svg" alt="Fürsten Reality">
      <div><h1>Vitajte v <em>administrácii</em></h1><p>Tu spravujete nehnuteľnosti, referencie aj všetky texty webu. Zmeny sa na webe objavia do minúty.</p></div>
      <div class="foot"><span>Mária Fürsten · realitná maklérka</span></div></div>
    <div class="login-form"><form novalidate>
      <h2>Prihlásenie</h2><p class="sub">Zadajte heslo do administrácie.</p>
      <div class="f"><label for="pw">Heslo</label><div class="pw-wrap"><input type="password" id="pw" autocomplete="current-password" required><button type="button" data-show>Zobraziť</button></div></div>
      <button class="btn btn-primary btn-lg" style="width:100%;margin-top:1.2rem" type="submit">Prihlásiť sa</button>
      <p class="err">${esc(msg)}</p>
      <a class="back" href="../">← Späť na web</a>
    </form></div></div>`;
  const form = $('form'), pw = $('#pw');
  $('[data-show]').addEventListener('click', (e) => { pw.type = pw.type === 'password' ? 'text' : 'password'; e.target.textContent = pw.type === 'password' ? 'Zobraziť' : 'Skryť'; });
  pw.focus();
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const b = form.querySelector('[type=submit]'); b.disabled = true; b.innerHTML = '<span class="spin" style="border-color:rgba(255,255,255,.3);border-top-color:#fff"></span> Overujem…';
    try {
      const r = await api('/login', { method: 'POST', body: JSON.stringify({ password: pw.value }) });
      S.sess = r.token; S.def = r.def; saveSess();
      await boot();
    } catch (err) {
      $('.err').textContent = err.status === 401 ? 'Nesprávne heslo. Skúste to znova.' : err.message;
      form.classList.remove('shake'); void form.offsetWidth; form.classList.add('shake'); pw.select();
    } finally { b.disabled = false; b.textContent = 'Prihlásiť sa'; }
  });
}
function logout() {
  if (dirtyKeys().length && !confirm('Máte neuložené zmeny. Naozaj sa odhlásiť a zahodiť ich?')) return;
  localStorage.removeItem(LS + 'sess_' + CFG.id); S.sess = null; S.snap = {}; S.D = {}; location.hash = ''; renderLogin();
}

/* ------------------------------------------------------------ SHELL */
function avatar(cls = '') { const p = S.D.site?.['about.photo_small'] || S.D.site?.['about.photo']; return p ? `<img src="${esc(src(p))}" alt="" class="${cls}">` : `<span class="mono-av ${cls}">MF</span>`; }
function pagesNav() { return S.schema.filter((p) => p.id !== 'general'); }
function renderShell() {
  $('#app').innerHTML = `<div class="shell">
    <aside class="side">
      <a class="logo" href="#/"><img src="../img/site/logo-light.svg" alt="Fürsten Reality"><small>Administrácia webu</small></a>
      <nav>
        <a class="item" href="#/" data-nav="dash">${IC.dash}Prehľad</a>
        <div class="grp">Obsah</div>
        <a class="item" href="#/nehnutelnosti" data-nav="nehnutelnosti">${IC.building}Nehnuteľnosti<span class="count" data-count="listings"></span></a>
        <a class="item" href="#/referencie" data-nav="referencie">${IC.quote}Referencie<span class="count" data-count="reviews"></span></a>
        <div class="grp">Web</div>
        <a class="item" href="#/obsah/home" data-nav="obsah">${IC.text}Texty a obrázky</a>
        <div class="sub">${pagesNav().map((p) => `<a href="#/obsah/${p.id}" data-sub="${p.id}">${esc(p.title)}</a>`).join('')}</div>
        <a class="item" href="#/obsah/general" data-nav="general">${IC.phone}Kontakt a údaje</a>
        <a class="item" href="#/nastavenia" data-nav="nastavenia">${IC.gear}Nastavenia</a>
      </nav>
      <div class="foot">
        <div class="pub"><i></i><span></span></div>
        <a class="item" href="../" target="_blank" rel="noopener" style="display:flex;gap:.75rem;align-items:center;padding:.55rem .75rem;border-radius:9px;color:#C9D3CE;font-size:.88rem">${IC.ext.replace('<svg', '<svg width="17" height="17"')}Otvoriť web</a>
        <div class="me">${avatar()}<span><b>Mária Fürsten</b><small>Správkyňa webu</small></span><button data-logout title="Odhlásiť">${IC.logout.replace('<svg', '<svg width="17" height="17"')}</button></div>
      </div>
    </aside>
    <div class="main">
      <header class="top"><button class="burger" aria-label="Menu">${IC.menu.replace('<svg', '<svg width="20" height="20"')}</button><div class="crumb"></div><div class="actions"></div></header>
      <div class="page" id="page"></div>
    </div>
  </div>
  <div class="savebar"><span class="txt"></span><button class="btn btn-ghost btn-sm" data-discard>Zahodiť</button><button class="btn btn-teal" data-save>${IC.check} Uložiť a zverejniť</button></div>`;
  $('[data-logout]').addEventListener('click', logout);
  $('[data-save]').addEventListener('click', saveAll);
  $('[data-discard]').addEventListener('click', async () => { if (await confirmDlg('Zahodiť zmeny?', 'Všetky neuložené zmeny sa stratia.', 'Zahodiť')) discard(); });
  const side = $('.side');
  $('.burger').addEventListener('click', () => { side.classList.add('open'); const s = document.createElement('div'); s.className = 'scrim'; s.onclick = () => { side.classList.remove('open'); s.remove(); }; document.body.appendChild(s); });
  side.addEventListener('click', (e) => { if (e.target.closest('a') && side.classList.contains('open')) { side.classList.remove('open'); $('.scrim')?.remove(); } });
  window.addEventListener('scroll', () => $('.top')?.classList.toggle('scrolled', scrollY > 8), { passive: true });
  document.addEventListener('keydown', (e) => { if ((e.metaKey || e.ctrlKey) && e.key === 's') { e.preventDefault(); saveAll(); } });
  initPub();
}
function updateNav(key, sub) {
  $$('.side [data-nav]').forEach((a) => a.classList.toggle('on', a.dataset.nav === key));
  $$('.side [data-sub]').forEach((a) => a.classList.toggle('on', a.dataset.sub === sub));
  const c = { listings: S.D.listings.length, reviews: S.D.reviews.length };
  $$('.side [data-count]').forEach((el) => { el.textContent = c[el.dataset.count]; });
}
function updateSavebar() {
  const bar = $('.savebar'); if (!bar) return;
  const keys = dirtyKeys();
  const imgs = Object.keys(S.pending).filter((p) => !/-m\.(webp|jpg)$/.test(p)).length;
  bar.classList.toggle('show', keys.length > 0 || S.saving);
  bar.querySelector('.txt').innerHTML = S.saving ? '<b>Ukladám…</b><small>Nahrávam zmeny na web</small>' : `<b>Neuložené zmeny</b><small>${keys.map((k) => LABEL[k]).join(', ')}${imgs ? ` · ${plural(imgs, 'nový obrázok', 'nové obrázky', 'nových obrázkov')}` : ''}</small>`;
  bar.querySelector('[data-save]').disabled = S.saving;
  bar.querySelector('[data-discard]').disabled = S.saving;
  updateNav($('.side [data-nav].on')?.dataset.nav, $('.side [data-sub].on')?.dataset.sub);
}
function setTop(crumbs, actions = '') {
  $('.crumb').innerHTML = crumbs.map((c, i) => i < crumbs.length - 1 && c[1] ? `<a href="${c[1]}">${esc(c[0])}</a><span>/</span>` : `<span>${esc(c[0])}</span>`).join('');
  $('.top .actions').innerHTML = actions;
  document.title = crumbs[crumbs.length - 1][0] + ' – Administrácia';
}
const page = () => $('#page');

/* ------------------------------------------------------------ router */
const ROUTES = [
  [/^\/?$/, viewDash], [/^\/nehnutelnosti$/, viewListings], [/^\/nehnutelnost\/(.+)$/, viewListing],
  [/^\/referencie$/, viewReviews], [/^\/obsah\/(.+)$/, viewTexts], [/^\/nastavenia$/, viewSettings],
];
const FRESH = new Set();
function route() {
  if (!S.D.site) return;
  const h = decodeURIComponent(location.hash.replace(/^#/, '')) || '/';
  IP = [];
  const old = $('#page'); if (old) { const n = document.createElement('div'); n.className = 'page'; n.id = 'page'; old.replaceWith(n); }
  for (const it of FRESH) {
    const cur = h.endsWith('/' + it.id);
    if (!cur && !it.title && !(it.photos || []).length && !it.body) {
      const i = S.D.listings.indexOf(it); if (i > -1) S.D.listings.splice(i, 1);
      FRESH.delete(it);
    } else if (!cur) FRESH.delete(it);
  }
  for (const [re, fn] of ROUTES) { const m = h.match(re); if (m) { window.scrollTo(0, 0); fn(...m.slice(1)); updateSavebar(); return; } }
  location.hash = '#/';
}
window.addEventListener('hashchange', route);

/* ------------------------------------------------------------ pre-launch checklist */
function todos() {
  const out = [];
  for (const p of S.schema) for (const sec of p.sections) for (const f of sec.fields) {
    if (!f.todo) continue;
    const v = S.D.site[f.key];
    const missing = f.kind === 'textarea' ? /\[DOPLNI/.test(String(v || '')) : isTodo(v);
    out.push({ label: f.label, where: p.title, ok: !missing, href: `#/obsah/${p.id}` });
  }
  const mail = String(S.D.site['contact.email'] || '');
  out.push({ label: 'Vlastná e-mailová adresa', where: 'Kontakt a údaje – e-mail na vlastnej doméne (zatiaľ ' + (mail || '—') + ')', ok: !!mail && !/@vasereality\.sk$/i.test(mail), href: '#/obsah/general' });
  out.push({ label: 'Referencie klientov', where: 'Sekcia Referencie sa na webe ukáže po pridaní prvej', ok: S.D.reviews.some((r) => !r.hidden), href: '#/referencie' });
  return out.sort((x, y) => x.ok - y.ok);
}

/* ------------------------------------------------------------ DASHBOARD */
function viewDash() {
  updateNav('dash');
  setTop([['Prehľad']], `<a class="btn btn-ghost" href="../" target="_blank" rel="noopener">${IC.ext} Otvoriť web</a>`);
  const L = S.D.listings;
  const cnt = (s) => L.filter((x) => x.status === s).length;
  const active = cnt('aktualne'), done = cnt('predane') + cnt('prenajate');
  const recent = [...L].sort((a, b) => (b.updated || '').localeCompare(a.updated || '')).slice(0, 6);
  const h = new Date().getHours();
  const hi = h < 10 ? 'Dobré ráno' : h < 18 ? 'Dobrý deň' : 'Dobrý večer';
  const cover = (x) => (x.photos || [])[0] || (x.viz || [])[0] || '';
  const td = todos(); const open = td.filter((t) => !t.ok).length;
  page().innerHTML = `
    ${S.def ? `<div class="banner warn">${IC.lock}<span><b>Používate predvolené heslo „admin“</b>Po odovzdaní webu si ho prosím zmeňte.</span><a class="btn btn-primary btn-sm" href="#/nastavenia">Zmeniť heslo</a></div>` : ''}
    <section class="welcome"><div class="rings"><span></span><span></span><span></span></div>
      <div><h2>${hi}, <em>Mária</em>.</h2><p>Na webe máte ${plural(active, 'aktuálnu ponuku', 'aktuálne ponuky', 'aktuálnych ponúk')}${cnt('rezervovane') ? `, ${cnt('rezervovane')} rezervované` : ''} a ${plural(S.D.reviews.length, 'referenciu', 'referencie', 'referencií')}. Čo dnes upravíme?</p>
        <div class="acts"><a class="btn btn-teal" href="#/nehnutelnost/new">${IC.plus} Pridať nehnuteľnosť</a><a class="btn btn-ghost" href="#/referencie" data-newrev>${IC.quote} Pridať referenciu</a><a class="btn btn-ghost" href="../" target="_blank" rel="noopener">${IC.ext} Zobraziť web</a></div></div>
      <div class="avatar">${avatar()}</div></section>
    <div class="stats">
      <a class="card stat" href="#/nehnutelnosti" data-f="aktualne"><small>Aktuálne</small><b>${active}</b><div class="bar"><i style="width:${Math.min(100, active / Math.max(1, L.length) * 100)}%"></i></div></a>
      <a class="card stat" href="#/nehnutelnosti" data-f="rezervovane"><small>Rezervované</small><b>${cnt('rezervovane')}</b><div class="bar"><i style="width:${cnt('rezervovane') / Math.max(1, L.length) * 100}%;background:var(--res)"></i></div></a>
      <a class="card stat" href="#/nehnutelnosti" data-f="done"><small>Predané a prenajaté</small><b>${done}</b><div class="bar"><i style="width:${done / Math.max(1, L.length) * 100}%;background:#98A2B3"></i></div></a>
      <a class="card stat" href="#/referencie"><small>Referencie</small><b>${S.D.reviews.length}</b><div class="bar"><i style="width:${S.D.reviews.length ? 100 : 0}%"></i></div></a>
    </div>
    <div class="dash-grid">
      <div style="display:grid;gap:1.4rem;align-content:start">
        <div class="card"><div class="card-head"><h3>Pred spustením webu <small>${open ? `zostáva ${open}` : 'všetko hotové'}</small></h3></div>
          <div class="card-pad"><ul class="checklist">${td.map((t) => `<li class="${t.ok ? 'ok' : ''}"><span class="ck">${t.ok ? '✓' : '!'}</span><span><b>${esc(t.label)}</b><br><small class="muted">${esc(t.where)}</small></span>${t.ok ? '' : `<a href="${t.href}">Doplniť</a>`}</li>`).join('')}
</ul>
          <p class="hint" style="margin-top:.8rem">Doménu a e-mail na vlastnej doméne nastaví správca webu (WebHunter). Referencie sa na webe ukážu, keď pridáte prvú.</p></div></div>
        <div class="card"><div class="card-head"><h3>Rýchle akcie</h3></div>
          <div class="qa">
            <a href="#/nehnutelnost/new"><span class="ic">${IC.building}</span><span><b>Pridať nehnuteľnosť</b><small>Fotky, popis, cena, parametre</small></span></a>
            <a href="#/nehnutelnosti"><span class="ic">${IC.check}</span><span><b>Zmeniť stav</b><small>Rezervované, predané, prenajaté</small></span></a>
            <a href="#/obsah/home"><span class="ic">${IC.home}</span><span><b>Úvodná stránka</b><small>Texty, O mne, služby</small></span></a>
            <a href="#/obsah/general"><span class="ic">${IC.phone}</span><span><b>Kontakt a údaje</b><small>Telefón, IČO, fotografia</small></span></a>
          </div></div>
      </div>
      <div class="card"><div class="card-head"><h3>Nehnuteľnosti <small>naposledy upravené</small></h3><a class="btn btn-ghost btn-sm" href="#/nehnutelnosti">Všetky</a></div>
        <ul class="recent">${recent.map((x) => `<li><img src="${esc(src(cover(x)))}" alt="" loading="lazy"><span class="t"><b><a href="#/nehnutelnost/${esc(x.id)}">${esc(x.short || x.title)}</a></b><small>${x.updated ? 'Upravené ' + ago(x.updated) : esc(x.locality)}</small></span><span class="st st-${x.status}">${STATUS_L[x.status] || ''}</span></li>`).join('')}</ul>
      </div>
    </div>`;
  $$('.stats [data-f]').forEach((a) => a.addEventListener('click', () => { S.lf.status = a.dataset.f; }));
  $('[data-newrev]')?.addEventListener('click', () => { sessionStorage.setItem(LS + 'newrev', '1'); });
}

/* ------------------------------------------------------------ LISTINGS */
function viewListings() {
  updateNav('nehnutelnosti');
  setTop([['Nehnuteľnosti']], `<a class="btn btn-primary" href="#/nehnutelnost/new">${IC.plus} Pridať nehnuteľnosť</a>`);
  const L = S.D.listings;
  const count = (f) => L.filter(f).length;
  const tabs = [['all', 'Všetko', () => true], ['aktualne', 'Aktuálne', (x) => x.status === 'aktualne'], ['rezervovane', 'Rezervované', (x) => x.status === 'rezervovane'],
    ['done', 'Predané a prenajaté', (x) => x.status === 'predane' || x.status === 'prenajate'], ['home', 'Na úvodnej stránke', (x) => x.home], ['hidden', 'Skryté', (x) => x.hidden]];
  page().innerHTML = `
    <div class="page-head"><div><h1>Nehnuteľnosti</h1><p>Stav zmeníte priamo v zozname. Predané a prenajaté sa na webe presunú do sekcie „Predané a prenajaté“. Poradie zmeníte potiahnutím riadku. Hviezdička = na úvodnej stránke, oko = viditeľnosť.</p></div></div>
    <div class="toolbar"><div class="seg" data-tabs>${tabs.map(([k, l, f]) => `<button data-t="${k}" class="${S.lf.status === k ? 'on' : ''}">${STATUS_L[k] ? `<span class="dot dot-${k}"></span>` : ''}${l}<sup>${count(f)}</sup></button>`).join('')}</div>
      <div class="search">${IC.search}<input type="search" placeholder="Hľadať názov alebo lokalitu…" value="${esc(S.lf.q)}" data-q></div></div>
    <div class="card"><ul class="rows" data-rows></ul></div>`;
  const rows = $('[data-rows]');
  const cover = (x) => (x.photos || [])[0] || (x.viz || [])[0] || '';
  const draw = () => {
    const f = tabs.find((t) => t[0] === S.lf.status)?.[2] || (() => true);
    const q = S.lf.q.trim().toLowerCase();
    const canDrag = S.lf.status === 'all' && !q;
    const items = L.map((x, i) => [x, i]).filter(([x]) => f(x) && (!q || (x.title + ' ' + x.short + ' ' + x.locality + ' ' + x.address).toLowerCase().includes(q)));
    rows.innerHTML = items.length ? items.map(([x, i]) => `<li class="row${x.hidden ? ' is-hidden' : ''}" data-idx="${i}" ${canDrag ? 'draggable="true"' : ''}>
      <span class="handle" title="${canDrag ? 'Potiahnite pre zmenu poradia' : 'Poradie sa dá meniť v záložke Všetko bez hľadania'}">${canDrag ? IC.drag : ''}</span>
      <a href="#/nehnutelnost/${esc(x.id)}"><img class="thumb" src="${esc(src(cover(x)))}" alt="" loading="lazy"></a>
      <div class="ttl"><a href="#/nehnutelnost/${esc(x.id)}">${esc(x.short || x.title)}</a><small>${x.kind === 'prenajom' ? 'Prenájom' : 'Predaj'} · ${esc(x.type || '')}${x.locality ? ' · ' + esc(x.locality) : ''}</small></div>
      <div class="price">${esc(x.price || '—')}<small>ID ${esc(x.ref || '–')}</small></div>
      <div class="stcell"><select class="st-sel st st-${x.status}" data-st="${i}" aria-label="Stav">${STATUSES.map(([k, l]) => `<option value="${k}" ${x.status === k ? 'selected' : ''}>${l}</option>`).join('')}</select></div>
      <div class="acts">
        <button class="icon-btn${x.home ? ' on' : ''}" data-home="${i}" title="${x.home ? 'Zobrazuje sa na úvodnej stránke' : 'Zobraziť na úvodnej stránke'}">${x.home ? IC.starF : IC.star}</button>
        <button class="icon-btn" data-hide="${i}" title="${x.hidden ? 'Skryté – kliknutím zobrazíte' : 'Viditeľné – kliknutím skryjete'}">${x.hidden ? IC.eyeOff : IC.eye}</button>
        <button class="icon-btn" data-dup="${i}" title="Duplikovať">${IC.copy}</button>
        <button class="icon-btn danger" data-del="${i}" title="Zmazať">${IC.trash}</button>
      </div></li>`).join('') : `<li class="empty"><b>Nič tu nie je</b>V tomto filtri nie sú žiadne nehnuteľnosti.</li>`;
  };
  draw();
  $('[data-tabs]').addEventListener('click', (e) => { const b = e.target.closest('[data-t]'); if (!b) return; S.lf.status = b.dataset.t; $$('[data-t]').forEach((x) => x.classList.toggle('on', x === b)); draw(); });
  $('[data-q]').addEventListener('input', (e) => { S.lf.q = e.target.value; draw(); });
  sortable(rows, '.row', (a, b) => { move(L, a, b); changed(); draw(); });
  rows.addEventListener('change', (e) => { const s = e.target.closest('[data-st]'); if (s) { const x = L[+s.dataset.st]; x.status = s.value; x.updated = new Date().toISOString(); changed(); draw(); toast(`Stav: ${STATUS_L[x.status]}`, 'Nezabudnite uložiť.'); } });
  rows.addEventListener('click', async (e) => {
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.home) { const x = L[+b.dataset.home]; x.home = !x.home; changed(); draw(); }
    if (b.dataset.hide) { const x = L[+b.dataset.hide]; x.hidden = !x.hidden; changed(); draw(); toast(x.hidden ? 'Nehnuteľnosť bude skrytá' : 'Nehnuteľnosť bude viditeľná', 'Prejaví sa po uložení.'); }
    if (b.dataset.dup) { const x = clone(L[+b.dataset.dup]); x.title += ' (kópia)'; x.slug = uniqueSlug(slugify(x.slug + '-kopia')); x.id = x.slug; x.ref = ''; x.updated = new Date().toISOString(); L.splice(+b.dataset.dup + 1, 0, x); changed(); draw(); toast('Nehnuteľnosť zduplikovaná'); }
    if (b.dataset.del) { const x = L[+b.dataset.del]; if (await confirmDlg('Zmazať nehnuteľnosť?', `„${esc(x.short || x.title)}“ zmizne z webu aj s vlastnou stránkou. Ak ju len nechcete ukazovať, použite radšej skrytie (ikona oka) alebo stav Predané.`)) { L.splice(+b.dataset.del, 1); changed(); draw(); toast('Nehnuteľnosť zmazaná', 'Prejaví sa po uložení.'); } }
  });
}
function uniqueSlug(base, self = null) {
  base = base || 'nehnutelnost'; let s = base, k = 2;
  while (S.D.listings.some((x) => x.slug === s && x !== self)) s = `${base}-${k++}`;
  return s;
}

function viewListing(id) {
  updateNav('nehnutelnosti');
  const L = S.D.listings;
  if (id === 'new') {
    const x = { id: '', slug: '', ref: '', title: '', short: '', kind: 'predaj', type: 'Byt', status: 'aktualne', locality: '', address: '',
      price: '', price_note: '', price_includes: '', params: {}, facts: [], lead: '', body: '', photos: [], plans: [], viz: [], viz_note: '',
      video: '', tour: '', geo: [], source: '', home: true, hidden: false, seo_desc: '', updated: new Date().toISOString() };
    x.slug = x.id = uniqueSlug('nova-nehnutelnost'); x._new = true;
    L.unshift(x); FRESH.add(x); changed();
    history.replaceState(null, '', '#/nehnutelnost/' + x.id);
    return viewListing(x.id);
  }
  const x = L.find((i) => i.id === id);
  if (!x) { page().innerHTML = `<div class="empty"><b>Nehnuteľnosť sa nenašla</b><a class="btn btn-ghost" href="#/nehnutelnosti">Späť na zoznam</a></div>`; return; }
  x.params ||= {}; x.facts ||= [];
  const isNew = !!x._new; delete x._new;
  const live = () => CFG.site + 'nehnutelnosti/' + x.slug + '.html';
  setTop([['Nehnuteľnosti', '#/nehnutelnosti'], [x.short || x.title || 'Nová nehnuteľnosť']], `${!isNew ? `<a class="btn btn-ghost" href="${esc(live())}" target="_blank" rel="noopener">${IC.ext} Na webe</a>` : ''}<button class="btn btn-teal" data-save2>${IC.check} Uložiť</button>`);
  const touch = () => { x.updated = new Date().toISOString(); changed(); preview(); };
  const seg = (name, opts, val) => `<div class="seg" data-seg="${name}">${opts.map(([k, l]) => `<button type="button" data-v="${k}" class="${val === k ? 'on' : ''}">${STATUS_L[k] ? `<span class="dot dot-${k}"></span>` : ''}${l}</button>`).join('')}</div>`;
  page().innerHTML = `
    <div class="page-head"><div><h1>${isNew ? 'Nová <em>nehnuteľnosť</em>' : esc(x.short || x.title)}</h1><p>${isNew ? 'Vyplňte základné údaje, pridajte fotky a popis. Nakoniec uložte – nehnuteľnosť sa objaví na webe.' : 'Upravte údaje, fotky alebo popis. Zmeny sa prejavia po uložení.'}</p></div></div>
    <div class="ed">
      <div>
        <section class="card sec"><div class="card-head"><h3><span class="n">1</span>Základné údaje</h3></div><div class="card-pad fgrid">
          <div class="f big full"><label for="l-title">Názov nehnuteľnosti</label><input type="text" id="l-title" data-f="title" value="${esc(x.title)}" placeholder="napr. Rodinný dom so záhradou, Ilava"></div>
          <div class="f full"><label for="l-short">Krátky názov <span class="opt">na kartičky, max. ~40 znakov</span></label><input type="text" id="l-short" data-f="short" value="${esc(x.short)}" placeholder="napr. Rodinný dom so záhradou"></div>
          <div class="f"><div class="lab">Ponuka</div>${seg('kind', KINDS, x.kind || 'predaj')}</div>
          <div class="f"><label for="l-type">Typ</label><select id="l-type" data-f="type">${TYPES.map((t) => `<option ${x.type === t ? 'selected' : ''}>${t}</option>`).join('')}</select></div>
          <div class="f full"><div class="lab">Stav <span class="opt">zobrazí sa ako štítok na webe</span></div>${seg('status', STATUSES, x.status)}</div>
          <div class="f"><label for="l-loc">Lokalita <span class="opt">krátko, na kartičky</span></label><input type="text" id="l-loc" data-f="locality" value="${esc(x.locality)}" placeholder="napr. Dubnica nad Váhom"></div>
          <div class="f"><label for="l-addr">Adresa</label><input type="text" id="l-addr" data-f="address" value="${esc(x.address)}" placeholder="Ulica, obec"></div>
        </div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">2</span>Cena</h3></div><div class="card-pad fgrid">
          <div class="f"><label for="l-price">Cena</label><input type="text" id="l-price" data-f="price" value="${esc(x.price)}" placeholder="napr. 155 000 € alebo 595 € / mesiac"><div class="hint">Prázdne = „Cena na vyžiadanie“.</div></div>
          <div class="f"><label for="l-pn">Poznámka k cene <span class="opt">nepovinné</span></label><input type="text" id="l-pn" data-f="price_note" value="${esc(x.price_note)}" placeholder="napr. Cena je konečná, bez provízie."></div>
          <div class="f full"><label for="l-pi">Čo cena zahŕňa</label><textarea id="l-pi" data-f="price_includes" rows="3" placeholder="napr. právny servis, zmluvy, poplatok za vklad do katastra, parkovacie miesto…">${esc(x.price_includes)}</textarea></div>
        </div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">3</span>Parametre <small data-ptype></small></h3></div><div class="card-pad"><p class="param-note">Zobrazia sa len vyplnené polia. Ponúkame polia vhodné pre zvolený typ nehnuteľnosti.</p><div class="fgrid" data-params></div>
          <div style="margin-top:1.2rem"><div class="lab">Vlastné parametre <span class="opt">napr. Balkón – 6 m²</span></div><div class="facts" data-facts></div><button class="btn btn-ghost btn-sm" data-addfact style="margin-top:.6rem">${IC.plus} Pridať parameter</button></div></div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">4</span>Popis</h3></div><div class="card-pad" style="display:grid;gap:1.1rem">
          <div class="f"><label for="l-lead">Úvodná veta (perex)</label><textarea id="l-lead" data-f="lead" rows="3" placeholder="Jedna až dve vety, ktoré nehnuteľnosť vystihnú. Zobrazí sa veľkým písmom.">${esc(x.lead)}</textarea></div>
          <div class="f"><div class="lab">Podrobný popis</div><div data-rte></div><div class="hint">Nadpisy, tučné písmo, odrážky aj odkazy nastavíte v lište nad textom.</div></div>
        </div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">5</span>Fotografie <small>prvá je titulná</small></h3><span class="muted" data-cnt="photos"></span></div><div class="card-pad" data-galwrap="photos"></div></section>
        <section class="card sec"><div class="card-head"><h3><span class="n">6</span>Pôdorys <small>nepovinné</small></h3><span class="muted" data-cnt="plans"></span></div><div class="card-pad" data-galwrap="plans"></div></section>
        <section class="card sec"><div class="card-head"><h3><span class="n">7</span>Vizualizácie <small>na webe budú označené „Vizualizácia – ilustračné“</small></h3><span class="muted" data-cnt="viz"></span></div><div class="card-pad"><div data-galwrap="viz"></div>
          <div class="f" style="margin-top:1rem"><label for="l-vn">Poznámka k vizualizáciám <span class="opt">nepovinné</span></label><input type="text" id="l-vn" data-f="viz_note" value="${esc(x.viz_note)}" placeholder="napr. Vizualizácie ukazujú možnú podobu po rekonštrukcii."></div></div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">8</span>Video a 3D prehliadka</h3></div><div class="card-pad fgrid">
          <div class="f full"><label for="l-vid">Video (odkaz na YouTube)</label><input type="url" id="l-vid" data-f="video" value="${esc(x.video)}" placeholder="https://www.youtube.com/watch?v=…"></div>
          <div class="f full"><label for="l-tour">3D prehliadka (odkaz)</label><input type="url" id="l-tour" data-f="tour" value="${esc(x.tour)}" placeholder="napr. Matterport"></div>
        </div></section>

        <section class="card sec"><div class="card-head"><h3><span class="n">9</span>Adresa stránky a vyhľadávače</h3></div><div class="card-pad fgrid">
          <div class="f"><label for="l-ref">ID ponuky</label><input type="text" id="l-ref" data-f="ref" value="${esc(x.ref)}" placeholder="napr. 2919"><div class="hint">Príde v e-maile pri dopyte na obhliadku.</div></div>
          <div class="f"><label for="l-slug">Adresa stránky (URL)</label><div class="affix"><span>…/nehnutelnosti/</span><input type="text" id="l-slug" data-f="slug" value="${esc(x.slug)}"></div></div>
          <div class="f full"><label for="l-seo">Popis pre Google <span class="opt">nepovinné</span></label><textarea id="l-seo" data-f="seo_desc" rows="2" placeholder="Keď necháte prázdne, použije sa úvodná veta.">${esc(x.seo_desc)}</textarea></div>
        </div></section>
      </div>
      <aside class="ed-side">
        <div class="card pv-card"><div class="pv-label">Náhľad kartičky</div><div style="padding:.8rem 1.1rem 0"><div class="img" style="border-radius:10px;overflow:hidden" data-pv-img></div></div><div class="body" data-pv-body></div></div>
        <div class="card"><div class="side-list">
          <label class="tog"><span>Na úvodnej stránke<small>V sekcii „Z mojej ponuky“</small></span><input type="checkbox" data-t="home" ${x.home ? 'checked' : ''}><span class="sw"></span></label>
          <label class="tog"><span>Skryť z webu<small>Zostane len v administrácii</small></span><input type="checkbox" data-t="hidden" ${x.hidden ? 'checked' : ''}><span class="sw"></span></label>
        </div></div>
        <div class="card card-pad" style="display:grid;gap:.6rem">
          <button class="btn btn-primary btn-lg" data-save3>${IC.check} Uložiť a zverejniť</button>
          <button class="btn btn-ghost" data-dup>${IC.copy} Duplikovať</button>
          <button class="btn btn-danger" data-del>${IC.trash} Zmazať nehnuteľnosť</button>
          <p class="hint" style="text-align:center">${x.updated ? 'Naposledy upravené ' + ago(x.updated) : ''}</p>
        </div>
      </aside>
    </div>`;
  const root = page();
  let slugTouched = !isNew;
  const preview = () => {
    const c = (x.photos || [])[0] || (x.viz || [])[0];
    $('[data-pv-img]', root).innerHTML = `<div class="img">${c ? `<img src="${esc(src(c))}" alt="">` : ''}<span class="st st-${x.status}">${STATUS_L[x.status]}</span></div>`;
    $('[data-pv-body]', root).innerHTML = `<small><span>${x.kind === 'prenajom' ? 'Prenájom' : 'Predaj'} · ${esc(x.type)}</span><span>${esc(x.price || 'Na vyžiadanie')}</span></small><b>${esc(x.short || x.title || 'Názov nehnuteľnosti')}</b><small>${esc(x.locality || 'Lokalita')}</small>`;
    ['photos', 'plans', 'viz'].forEach((k) => { const el = $(`[data-cnt="${k}"]`, root); if (el) el.textContent = (x[k] || []).length ? `${x[k].length} ks` : ''; });
  };
  const drawParams = () => {
    const keys = TYPE_PARAMS[x.type] || PARAMS.map((p) => p[0]);
    const extra = Object.keys(x.params).filter((k) => x.params[k] && !keys.includes(k));   // keep filled fields visible after a type change
    $('[data-ptype]', root).textContent = 'pre typ ' + x.type;
    $('[data-params]', root).innerHTML = PARAMS.filter(([k]) => keys.includes(k) || extra.includes(k)).map(([k, l, ph]) => `<div class="f${k === 'extras' || k === 'utilities' ? ' full' : ''}"><label for="p-${k}">${esc(l)}</label><input type="text" id="p-${k}" data-p="${k}" value="${esc(x.params[k] || '')}" placeholder="${esc(ph)}"></div>`).join('');
  };
  drawParams();
  $('[data-params]', root).addEventListener('input', (e) => { const k = e.target.dataset.p; if (!k) return; x.params[k] = e.target.value; touch(); e.stopPropagation(); });
  root.addEventListener('input', (e) => {
    const f = e.target.dataset.f; if (!f) return;
    let v = e.target.value;
    if (f === 'slug') { v = slugify(v) || ''; slugTouched = true; }
    x[f] = v;
    if (f === 'title' && !slugTouched) { x.slug = uniqueSlug(slugify(v) || 'nova-nehnutelnost', x); $('#l-slug').value = x.slug; }
    touch();
  });
  $('#l-type').addEventListener('change', () => drawParams());
  $('#l-slug').addEventListener('blur', (e) => { x.slug = uniqueSlug(slugify(e.target.value) || 'nehnutelnost', x); e.target.value = x.slug; touch(); });
  $$('[data-seg]', root).forEach((sg) => sg.addEventListener('click', (e) => { const b = e.target.closest('[data-v]'); if (!b) return; x[sg.dataset.seg] = b.dataset.v; $$('[data-v]', sg).forEach((i) => i.classList.toggle('on', i === b)); touch(); }));
  root.addEventListener('change', (e) => { if (e.target.dataset.t) { x[e.target.dataset.t] = e.target.checked; touch(); } });
  const drawFacts = () => {
    $('[data-facts]', root).innerHTML = (x.facts || []).map((f, i) => `<div class="fact"><input class="in" type="text" data-fl="${i}" value="${esc(f.l)}" placeholder="Názov (napr. Balkón)"><input class="in" type="text" data-fv="${i}" value="${esc(f.v)}" placeholder="Hodnota (napr. 6 m²)"><button class="icon-btn danger" data-frm="${i}" title="Odobrať">${IC.trash}</button></div>`).join('');
  };
  drawFacts();
  $('[data-facts]', root).addEventListener('input', (e) => { const t = e.target; if (t.dataset.fv) x.facts[+t.dataset.fv].v = t.value; if (t.dataset.fl) x.facts[+t.dataset.fl].l = t.value; touch(); e.stopPropagation(); });
  $('[data-facts]', root).addEventListener('click', (e) => { const b = e.target.closest('[data-frm]'); if (b) { x.facts.splice(+b.dataset.frm, 1); drawFacts(); touch(); } });
  $('[data-addfact]', root).addEventListener('click', () => { x.facts.push({ l: '', v: '' }); drawFacts(); touch(); $$('[data-fl]', root).pop()?.focus(); });
  ['photos', 'plans', 'viz'].forEach((k) => {
    x[k] ||= [];
    const wrap = $(`[data-galwrap="${k}"]`, root);
    const draw = () => { wrap.innerHTML = galleryHTML(x[k], k, k === 'plans'); bindGallery(wrap, x, k, x.short || x.title, () => { draw(); touch(); }); };
    draw();
  });
  mountRTE($('[data-rte]', root), x.body, (h) => { x.body = h; touch(); }, 'Opíšte nehnuteľnosť – dispozíciu, stav, okolie, pre koho je ideálna…');
  bindIP(root);
  preview();
  $('[data-save2]').addEventListener('click', saveAll); $('[data-save3]', root).addEventListener('click', saveAll);
  $('[data-dup]', root).addEventListener('click', () => { const c = clone(x); c.title = (c.title || '') + ' (kópia)'; c.slug = c.id = uniqueSlug(slugify(x.slug + '-kopia')); c.ref = ''; c.updated = new Date().toISOString(); L.splice(L.indexOf(x) + 1, 0, c); changed(); toast('Vytvorená kópia', 'Upravujete teraz kópiu.'); location.hash = '#/nehnutelnost/' + c.id; });
  $('[data-del]', root).addEventListener('click', async () => { if (await confirmDlg('Zmazať nehnuteľnosť?', `„${esc(x.short || x.title || 'Nová nehnuteľnosť')}“ zmizne z webu. Ak ju len nechcete ukazovať, použite radšej „Skryť z webu“ alebo stav Predané.`)) { L.splice(L.indexOf(x), 1); changed(); location.hash = '#/nehnutelnosti'; toast('Nehnuteľnosť zmazaná', 'Prejaví sa po uložení.'); } });
  if (isNew) setTimeout(() => $('#l-title')?.focus(), 60);
}

/* ------------------------------------------------------------ REVIEWS */
function viewReviews() {
  updateNav('referencie');
  setTop([['Referencie']], `<button class="btn btn-primary" data-add>${IC.plus} Pridať referenciu</button>`);
  const V = S.D.reviews;
  const draw = () => {
    page().innerHTML = `<div class="page-head"><div><h1>Referencie</h1><p>Hodnotenia klientov. Sekcia Referencie sa na úvodnej stránke ukáže, až keď tu bude aspoň jedna viditeľná referencia. Poradie = poradie na webe.</p></div></div>
      ${V.length ? '' : `<div class="card card-pad" style="text-align:center;padding:2.4rem"><p class="muted" style="margin-bottom:1rem">Zatiaľ tu nie sú žiadne referencie. Stačí skopírovať text od spokojného klienta (so súhlasom).</p><button class="btn btn-primary" data-add2>${IC.plus} Pridať prvú referenciu</button></div>`}
      <div class="rev-grid">${V.map((r, i) => `<article class="card rv${r.hidden ? ' is-hidden' : ''}"><p>${esc(r.text)}</p>
        <footer><span><b>${esc(r.name)}</b><br><small class="muted">${esc(r.meta || '')}${r.hidden ? ' · skryté' : ''}</small></span><span class="acts">
          <button class="icon-btn" data-up="${i}" title="Posunúť vyššie">${IC.up}</button><button class="icon-btn" data-down="${i}" title="Posunúť nižšie">${IC.down}</button>
          <button class="icon-btn" data-hide="${i}" title="${r.hidden ? 'Zobraziť' : 'Skryť'}">${r.hidden ? IC.eyeOff : IC.eye}</button>
          <button class="icon-btn" data-edit="${i}" title="Upraviť">${IC.pen}</button><button class="icon-btn danger" data-del="${i}" title="Zmazať">${IC.trash}</button></span></footer></article>`).join('')}</div>`;
    $('[data-add2]')?.addEventListener('click', add);
  };
  const edit = async (r, isNew) => {
    const v = await modal({
      title: isNew ? 'Nová referencia' : 'Upraviť referenciu',
      body: `<div class="fgrid"><div class="f"><label>Meno klienta</label><input type="text" data-n value="${esc(r.name)}" placeholder="napr. Jana K."></div><div class="f"><label>Doplnok <span class="opt">nepovinné</span></label><input type="text" data-m value="${esc(r.meta)}" placeholder="napr. predaj domu, Ilava · 2026"></div>
        <div class="f full"><label>Text referencie</label><textarea data-t rows="6">${esc(r.text)}</textarea></div></div>`,
      actions: [{ label: 'Zrušiť', value: false }, { label: isNew ? 'Pridať' : 'Hotovo', cls: 'btn-primary', get: (bg) => {
        const n = $('[data-n]', bg).value.trim(), t = $('[data-t]', bg).value.trim();
        if (!n || !t) { toast('Doplňte meno a text', '', 'err'); return false; }
        return { name: n, meta: $('[data-m]', bg).value.trim(), text: t };
      } }],
    });
    if (!v) return false;
    Object.assign(r, v); return true;
  };
  const add = async () => { const r = { name: '', meta: '', text: '', hidden: false }; if (await edit(r, true)) { V.unshift(r); changed(); draw(); toast('Referencia pridaná', 'Nezabudnite uložiť.'); } };
  draw();
  $('[data-add]').addEventListener('click', add);
  page().addEventListener('click', async (e) => {
    const b = e.target.closest('button'); if (!b) return; const d = b.dataset;
    if (d.up) { move(V, +d.up, +d.up - 1); changed(); draw(); }
    if (d.down) { move(V, +d.down, +d.down + 1); changed(); draw(); }
    if (d.hide) { V[+d.hide].hidden = !V[+d.hide].hidden; changed(); draw(); }
    if (d.edit) { if (await edit(V[+d.edit], false)) { changed(); draw(); } }
    if (d.del) { if (await confirmDlg('Zmazať referenciu?', `Referencia od „${esc(V[+d.del].name)}“ bude odstránená.`)) { V.splice(+d.del, 1); changed(); draw(); } }
  });
  if (sessionStorage.getItem(LS + 'newrev')) { sessionStorage.removeItem(LS + 'newrev'); add(); }
}

/* ------------------------------------------------------------ TEXTS (schema driven) */
const MDHELP = `<div class="md-help"><span><code>*slovo*</code> → <em>zvýraznenie</em></span><span><code>**slovo**</code> → <b>tučne</b></span><span>Enter → nový riadok</span></div>`;
function fieldHTML(f, get, set, ctx) {
  const v = get() ?? '';
  const id = 'f' + uid();
  const need = f.todo && (f.kind === 'textarea' ? /\[DOPLNI/.test(String(v)) : isTodo(v));
  const tb = need ? '<span class="todo-b">Doplniť pred spustením</span>' : '';
  const lab = `<label for="${id}">${esc(f.label)}${tb}</label>`;
  const hint = f.hint ? `<div class="hint">${esc(f.hint)}</div>` : '';
  const cls = 'f' + (need ? ' todo' : '');
  ctx.bind.push([id, set]);
  switch (f.kind) {
    case 'md': return `<div class="${cls}">${lab}<textarea class="short" id="${id}" data-auto rows="1">${esc(v)}</textarea>${MDHELP}${hint}</div>`;
    case 'textarea': return `<div class="${cls}">${lab}<textarea id="${id}" data-auto rows="4">${esc(v)}</textarea>${hint}</div>`;
    case 'image': ctx.bind.pop(); return `<div class="${cls}"><div class="lab">${esc(f.label)}${tb}</div>${imgPick(get, (x) => { set(x); }, { hint: f.label })}${hint}</div>`;
    case 'bool': return `<div class="f"><label class="tog"><input type="checkbox" id="${id}" ${v ? 'checked' : ''}><span class="sw"></span>${esc(f.label)}</label>${hint}</div>`;
    default: return `<div class="${cls}">${lab}<input type="text" id="${id}" value="${esc(v)}">${hint}</div>`;
  }
}
function bindFields(root, ctx) {
  ctx.bind.forEach(([id, set]) => {
    const el = root.querySelector('#' + id); if (!el) return;
    const ev = el.type === 'checkbox' || el.tagName === 'SELECT' ? 'change' : 'input';
    el.addEventListener(ev, () => { set(el.type === 'checkbox' ? el.checked : el.value); changed(); if (el.dataset.auto !== undefined) autosize(el); });
    if (el.dataset.auto !== undefined) requestAnimationFrame(() => autosize(el));
  });
  ctx.bind = [];
}
function listEditor(f) {
  const arr = S.D.site[f.key] ||= [];
  const wrap = document.createElement('div');
  wrap.className = 'f full';
  let open = -1;
  const titleOf = (it, i) => { const t = it[f.title] ?? it[f.fields[0]?.name]; return String(t ?? '').replace(/[*~]/g, '').trim() || `Položka ${i + 1}`; };
  const draw = () => {
    const ctx = { bind: [] };
    wrap.innerHTML = `<div class="lab">${esc(f.label)}<span class="opt">${plural(arr.length, 'položka', 'položky', 'položiek')}</span></div>${f.hint ? `<div class="hint" style="margin:-.1rem 0 .5rem">${esc(f.hint)}</div>` : ''}
      <div class="li-ed">${arr.map((it, i) => `<div class="li${i === open ? ' open' : ''}" data-i="${i}"><div class="li-h" data-tg="${i}"><span class="num">${i + 1}</span><span class="t">${esc(titleOf(it, i))}</span>
        <button type="button" class="icon-btn" data-mu="${i}" title="Vyššie">${IC.up}</button><button type="button" class="icon-btn" data-md="${i}" title="Nižšie">${IC.down}</button><button type="button" class="icon-btn danger" data-rm="${i}" title="Odobrať">${IC.trash}</button><span class="icon-btn" aria-hidden="true" style="transform:rotate(${i === open ? 180 : 0}deg)">${IC.chev}</span></div>
        <div class="li-b">${i === open ? f.fields.map((ff) => fieldHTML(ff, () => it[ff.name], (v) => { it[ff.name] = v; const t = wrap.querySelector(`.li[data-i="${i}"] .li-h .t`); if (t && (ff.name === f.title || ff.name === f.fields[0].name)) t.textContent = titleOf(it, i); }, ctx)).join('') : ''}</div></div>`).join('')}
      <button type="button" class="btn btn-ghost btn-sm li-add" data-add>${IC.plus} Pridať položku</button></div>`;
    bindFields(wrap, ctx); bindIP(wrap);
  };
  wrap.addEventListener('click', async (e) => {
    const b = e.target.closest('[data-mu],[data-md],[data-rm],[data-add],[data-tg]'); if (!b) return;
    const d = b.dataset;
    if (d.mu !== undefined) { e.stopPropagation(); move(arr, +d.mu, +d.mu - 1); if (open === +d.mu) open--; changed(); draw(); return; }
    if (d.md !== undefined) { e.stopPropagation(); move(arr, +d.md, +d.md + 1); if (open === +d.md) open++; changed(); draw(); return; }
    if (d.rm !== undefined) { e.stopPropagation(); if (await confirmDlg('Odobrať položku?', `„${esc(titleOf(arr[+d.rm], +d.rm))}“ bude odobraná.`, 'Odobrať')) { arr.splice(+d.rm, 1); open = -1; changed(); draw(); } return; }
    if (d.add !== undefined) { const it = Object.fromEntries(f.fields.map((x) => [x.name, x.kind === 'bool' ? false : ''])); arr.push(it); open = arr.length - 1; changed(); draw(); wrap.querySelector('.li.open input, .li.open textarea')?.focus(); return; }
    if (d.tg !== undefined) { open = open === +d.tg ? -1 : +d.tg; draw(); }
  });
  draw();
  return wrap;
}
function viewTexts(pid) {
  const p = S.schema.find((x) => x.id === pid) || S.schema[0];
  updateNav(p.id === 'general' ? 'general' : 'obsah', p.id);
  const pageUrl = { home: '', listing: 'ponuka.html', sell: 'predat.html', search: 'hladam.html', contactpage: 'kontakt.html', privacy: 'ochrana-osobnych-udajov.html' }[p.id];
  setTop([['Texty a obrázky', '#/obsah/home'], [p.title]], `${pageUrl !== undefined ? `<a class="btn btn-ghost" href="${CFG.site}${pageUrl}" target="_blank" rel="noopener">${IC.ext} Stránka na webe</a>` : ''}<button class="btn btn-teal" data-save2>${IC.check} Uložiť</button>`);
  page().innerHTML = `<div class="page-head"><div><h1>${p.id === 'general' ? 'Kontakt a <em>údaje</em>' : esc(p.title)}</h1><p>${p.id === 'general' ? 'Údaje, ktoré sa opakujú na celom webe – v hlavičke, pätičke, kontaktoch aj pri nehnuteľnostiach. Oranžovo označené polia treba doplniť pred spustením.' : 'Upravte texty a obrázky tejto stránky. Sekcie otvoríte kliknutím.'}</p></div></div>
    ${p.id !== 'general' ? `<nav class="tabs">${pagesNav().map((x) => `<a href="#/obsah/${x.id}" class="${x.id === p.id ? 'on' : ''}">${esc(x.title)}</a>`).join('')}</nav>` : ''}
    <div data-secs></div>`;
  const secs = $('[data-secs]');
  p.sections.forEach((sec, si) => {
    const d = document.createElement('details');
    d.className = 'card acc'; if (si === 0 || p.id === 'general' || sec.fields.some((f) => f.todo)) d.open = true;
    d.innerHTML = `<summary>${esc(sec.title)} <small>${plural(sec.fields.length, 'pole', 'polia', 'polí')}</small><span class="chev">${IC.chev.replace('<svg', '<svg width="18" height="18"')}</span></summary><div class="acc-body"></div>`;
    const body = d.querySelector('.acc-body');
    const ctx = { bind: [] };
    let html = '';
    const lists = [];
    sec.fields.forEach((f) => {
      if (f.kind === 'list') { html += `<div data-list-slot="${lists.length}"></div>`; lists.push(f); }
      else html += fieldHTML(f, () => S.D.site[f.key], (v) => { S.D.site[f.key] = v; }, ctx);
    });
    body.innerHTML = html;
    bindFields(body, ctx); bindIP(body);
    lists.forEach((f, i) => body.querySelector(`[data-list-slot="${i}"]`).replaceWith(listEditor(f)));
    d.addEventListener('toggle', () => { if (d.open) $$('textarea[data-auto]', d).forEach(autosize); });
    secs.appendChild(d);
  });
  $('[data-save2]').addEventListener('click', saveAll);
}

/* ------------------------------------------------------------ SETTINGS */
function viewSettings() {
  updateNav('nastavenia');
  setTop([['Nastavenia']]);
  page().innerHTML = `<div class="page-head"><div><h1>Nastavenia</h1><p>Heslo do administrácie, stav webu a zálohy.</p></div></div>
    <div class="dash-grid">
      <div style="display:grid;gap:1.4rem;align-content:start">
        <section class="card"><div class="card-head"><h3>Heslo do administrácie</h3>${S.def ? '<span class="st st-rezervovane">Predvolené heslo</span>' : '<span class="st st-aktualne">Nastavené</span>'}</div>
          <form class="card-pad fgrid" data-pw>
            <div class="f full"><label>Súčasné heslo</label><input type="password" name="old" autocomplete="current-password"></div>
            <div class="f"><label>Nové heslo</label><input type="password" name="n1" autocomplete="new-password" minlength="8"></div>
            <div class="f"><label>Nové heslo znova</label><input type="password" name="n2" autocomplete="new-password"></div>
            <div class="full" style="display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap"><span class="hint" style="margin:0">Aspoň 8 znakov. Po zmene sa odhlásia všetky ostatné zariadenia.</span><button class="btn btn-primary" type="submit">Zmeniť heslo</button></div>
          </form></section>
        <section class="card"><div class="card-head"><h3>Zabezpečenie</h3><span class="st st-aktualne">Chránené</span></div>
          <div class="card-pad" style="display:grid;gap:.7rem;font-size:.9rem;color:#344054">
            <p>Heslo sa overuje na zabezpečenom serveri a nikde na webe nie je uložené. Po 8 chybných pokusoch sa prihlasovanie na 15 minút zablokuje.</p>
            <p>Prihlásenie platí 12 hodín, potom vás administrácia požiada o heslo znova – rozpracované zmeny sa pritom nestratia.</p>
            <p>Správy z formulárov na webe chodia priamo e-mailom. Adresu príjemcu nastavuje správca webu (WebHunter).</p>
          </div></section>
      </div>
      <div style="display:grid;gap:1.4rem;align-content:start">
        <section class="card"><div class="card-head"><h3>Stav webu</h3></div><div class="card-pad" style="display:grid;gap:.8rem">
          <div class="pub ${S.pub.state}" style="background:var(--line-2);color:var(--text)"><i></i><span>${esc(S.pub.text)}</span></div>
          <p class="muted" style="font-size:.86rem">Po uložení sa web automaticky pregeneruje a zverejní. Zvyčajne to trvá 30 – 90 sekúnd.</p>
          <a class="btn btn-ghost" href="../" target="_blank" rel="noopener">${IC.ext} Otvoriť web</a>
        </div></section>
        <section class="card"><div class="card-head"><h3>Záloha dát</h3></div><div class="card-pad" style="display:grid;gap:.8rem">
          <p class="muted" style="font-size:.86rem">Stiahnite si kompletný obsah webu (nehnuteľnosti, referencie a texty) do jedného súboru. Každé uloženie sa navyše automaticky archivuje, takže sa dá vrátiť aj staršia verzia.</p>
          <button class="btn btn-ghost" data-backup>${IC.download} Stiahnuť zálohu</button>
        </div></section>
        <section class="card"><div class="card-pad" style="display:grid;gap:.6rem"><button class="btn btn-ghost" data-lo>${IC.logout} Odhlásiť sa</button></div></section>
      </div>
    </div>`;
  $('[data-lo]').addEventListener('click', logout);
  $('[data-backup]').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify({ exported: new Date().toISOString(), ...S.D }, null, 1)], { type: 'application/json' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `${CFG.id}-zaloha-${today()}.json`; a.click();
  });
  $('[data-pw]').addEventListener('submit', async (e) => {
    e.preventDefault(); const f = e.target; const b = f.querySelector('[type=submit]');
    const old = f.old.value, n1 = f.n1.value, n2 = f.n2.value;
    if (n1.length < 8) return toast('Nové heslo je príliš krátke', 'Použite aspoň 8 znakov.', 'err');
    if (n1 !== n2) return toast('Heslá sa nezhodujú', '', 'err');
    b.disabled = true; b.textContent = 'Mením…';
    try {
      const r = await api('/password', { method: 'POST', body: JSON.stringify({ old, password: n1 }) });
      S.sess = r.token; S.def = false; saveSess();
      toast('Heslo zmenené', 'Nabudúce sa prihláste novým heslom.', 'ok'); viewSettings();
    } catch (err) { toast('Heslo sa nepodarilo zmeniť', err.message, 'err'); }
    finally { b.disabled = false; b.textContent = 'Zmeniť heslo'; }
  });
}

/* ------------------------------------------------------------ boot */
async function boot() {
  $('#app').innerHTML = `<div class="boot"><img src="../img/site/logo.svg" alt=""><span class="muted" style="display:flex;gap:.7rem;align-items:center"><span class="spin"></span> Načítavam obsah webu…</span></div>`;
  try { await loadAll(); }
  catch (e) {
    if (e.status === 401) { localStorage.removeItem(LS + 'sess_' + CFG.id); S.sess = null; return renderLogin('Prihlásenie vypršalo. Prihláste sa prosím znova.'); }
    $('#app').innerHTML = `<div class="boot"><div class="banner err" style="max-width:520px">${IC.alert}<span><b>Obsah sa nepodarilo načítať</b>${esc(e.message)}</span><button class="btn btn-ghost btn-sm" onclick="location.reload()">Skúsiť znova</button></div></div>`;
    return;
  }
  renderShell(); route();
}
const sess = JSON.parse(localStorage.getItem(LS + 'sess_' + CFG.id) || 'null');
if (sess && sess.exp > Date.now()) { S.sess = sess.t; S.def = !!sess.def; boot(); } else renderLogin();
})();
