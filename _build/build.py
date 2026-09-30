#!/usr/bin/env python3
"""Generátor statického webu Fürsten Reality — spustenie: python3 _build/build.py
Obsah je v _data/*.json (upravuje sa cez /admin/), predvolené texty v _build/schema.py."""
import json, os, re, hashlib, shutil, html as H, urllib.parse
from datetime import date
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
import sys; sys.path.insert(0, os.path.join(ROOT, '_build'))
from schema import SCHEMA, defaults

S = defaults()
S.update(json.load(open('_data/site.json', encoding='utf-8')))
LIST = [x for x in json.load(open('_data/listings.json', encoding='utf-8')) if not x.get('hidden')]
REVS = [r for r in json.load(open('_data/reviews.json', encoding='utf-8')) if not r.get('hidden')]

BASE = 'https://webhunter-navrhy.github.io/fursten-reality/'
SITE_ID = 'fursten'
FORM_API = f'https://webhunter-admin.webhunter.workers.dev/api/{SITE_ID}/form'
esc = H.escape
def T(k): return S.get(k, '') if S.get(k) is not None else ''
def TL(k): return S.get(k) or []

NAME = T('contact.name'); TEL = T('contact.phone'); TEL_H = 'tel:' + re.sub(r'[^\d+]', '', TEL); MAIL = T('contact.email')
PHOTO = T('about.photo')

# ------------------------------------------------------------------ icons
def ico(d, w=18, sw=1.5, fill='none'):
    return f'<svg class="i" width="{w}" height="{w}" viewBox="0 0 24 24" fill="{fill}" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
ARR = ico('<path d="M4 12h16M14 6l6 6-6 6"/>', 16)
ARR_L = ico('<path d="M20 12H4M10 6l-6 6 6 6"/>', 16)
PHONE = ico('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>', 17)
MAILI = ico('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>', 17)
PIN = ico('<path d="M12 21s7-6.1 7-11.5A7 7 0 0 0 5 9.5C5 14.9 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.4"/>', 15)
CHECK = ico('<path d="M5 12.5l4.5 4.5L19 7.5"/>', 18, 1.8)
PLAY = ico('<path d="M8 5.5v13l11-6.5z"/>', 26, 1.4, 'currentColor')
CUBE = ico('<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M4 7.5l8 4.5 8-4.5M12 12v9"/>', 18)
GRID = ico('<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>', 16)
MAPI = ico('<path d="M9 4L3 6.5v13.5l6-2.5 6 2.5 6-2.5V4l-6 2.5z"/><path d="M9 4v13.5M15 6.5V20"/>', 18)
LOCK = ico('<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>', 12)

# ------------------------------------------------------------------ text helpers
def md(s):
    s = esc(str(s or ''), quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.+?)\*', r'<em>\1</em>', s)
    return s.replace('\n', '<br>')
def paras(s, cls=''):
    parts = [p.strip() for p in re.split(r'\n\s*\n', str(s or '')) if p.strip()]
    return ''.join((f'<p class="{cls}">' if cls and i == 0 else '<p>') + md(p) + '</p>' for i, p in enumerate(parts))
def plain(s): return re.sub(r'[*~]', '', str(s or ''))
def todo_html(s):
    """[DOPLNIŤ: …] placeholders stay visible but marked"""
    return re.sub(r'\[DOPLNIŤ:?\s*([^\]]*)\]', lambda m: f'<mark class="todo" title="Doplní sa pred spustením">{m.group(1) or "doplní sa"}</mark>', s)

def heading(text, tag='h1', cls=''):
    """lines of a heading become separately revealed spans"""
    lines = str(text or '').split('\n')
    inner = ''.join(f'<span class="ln"><span style="--l:{i}">{md(l)}</span></span>' for i, l in enumerate(lines))
    return f'<{tag} class="split {cls}">{inner}</{tag}>'

class Clean(HTMLParser):
    OK = {'p', 'h2', 'h3', 'h4', 'strong', 'b', 'em', 'i', 'u', 'a', 'ul', 'ol', 'li', 'blockquote', 'br'}
    def __init__(s): super().__init__(convert_charrefs=True); s.out = []
    def handle_starttag(s, t, a):
        if t not in s.OK: return
        if t == 'a':
            href = dict(a).get('href') or ''
            if href.lower().startswith('javascript'): href = '#'
            s.out.append('<a href="' + esc(href) + '"' + (' target="_blank" rel="noopener"' if href.startswith('http') else '') + '>')
        else: s.out.append(f'<{"h3" if t == "h2" else t}>')
    def handle_endtag(s, t):
        if t in s.OK and t != 'br': s.out.append(f'</{"h3" if t == "h2" else t}>')
    def handle_data(s, d): s.out.append(esc(d, quote=False))
def clean_html(h):
    c = Clean(); c.feed(h or ''); return re.sub(r'<p>(\s|<br>)*</p>', '', ''.join(c.out))

def btn(href, text, cls='', ext=False, icon=ARR):
    t = ' target="_blank" rel="noopener"' if ext else ''
    return f'<a href="{href}" class="btn {cls}"{t}><span>{esc(text)}</span>{icon}</a>'

def link(h):
    h = h or '#'
    return h if re.match(r'^(https?:|mailto:|tel:|#)', h) else '@/' + h.lstrip('/')

def _ver(f): return hashlib.md5(open(f, 'rb').read()).hexdigest()[:8]

def img_attrs(p, sizes='(max-width: 760px) 100vw, 50vw'):
    """src + srcset when a 900px '-m' variant exists next to the file"""
    p = p or ''
    m = re.sub(r'\.(webp|jpe?g|png)$', r'-m.\1', p)
    if m != p and os.path.exists(m):
        return f'src="@/{esc(m)}" srcset="@/{esc(m)} 900w, @/{esc(p)} 2000w" sizes="{sizes}"'
    return f'src="@/{esc(p)}"'

# ------------------------------------------------------------------ listings
STATUS = {'aktualne': ('aktualne', 'Aktuálne', 'live'), 'rezervovane': ('rezervovane', 'Rezervované', 'res'),
          'predane': ('predane', 'Predané', 'done'), 'prenajate': ('prenajate', 'Prenajaté', 'done')}
KIND = {'predaj': 'Na predaj', 'prenajom': 'Na prenájom'}
PARAMS = [('rooms', 'Počet izieb'), ('area_usable', 'Úžitková plocha'), ('area_built', 'Zastavaná plocha'), ('area_plot', 'Plocha pozemku'),
          ('floor', 'Poschodie'), ('condition', 'Stav'), ('building', 'Konštrukcia'), ('year', 'Rok výstavby'),
          ('utilities', 'Inžinierske siete'), ('heating', 'Vykurovanie'), ('parking', 'Parkovanie'), ('costs', 'Mesačné náklady'),
          ('energy', 'Energetický certifikát'), ('ownership', 'Vlastníctvo'), ('available', 'Voľné od'), ('extras', 'Ďalej k dispozícii')]
PLABEL = dict(PARAMS)
TYPE_PARAMS = {
    'Byt': ['rooms', 'area_usable', 'floor', 'condition', 'building', 'heating', 'parking', 'costs', 'energy', 'ownership', 'available', 'extras'],
    'Rodinný dom': ['rooms', 'area_usable', 'area_built', 'area_plot', 'condition', 'building', 'year', 'utilities', 'heating', 'parking', 'costs', 'energy', 'ownership', 'available', 'extras'],
    'Pozemok': ['area_plot', 'utilities', 'parking', 'ownership', 'available', 'extras'],
    'Chata / chalupa': ['rooms', 'area_usable', 'area_plot', 'condition', 'building', 'year', 'utilities', 'heating', 'parking', 'ownership', 'extras'],
    'Komerčný priestor': ['area_usable', 'area_plot', 'floor', 'condition', 'building', 'utilities', 'heating', 'parking', 'costs', 'energy', 'ownership', 'available', 'extras'],
}
def pv(x, k): return str((x.get('params') or {}).get(k) or '').strip()
def short_num(v):
    m = re.match(r'^\s*([\d\s ]+(?:,\d+)?\s*m²)', v)
    return m.group(1).strip() if m else v.split(' (')[0].strip()
def key_facts(x):
    """up to 4 headline facts for cards/detail strip"""
    t = x.get('type'); out = []
    r = pv(x, 'rooms')
    if r: out.append(('Izby', r.split(' (')[0]))
    a = pv(x, 'area_usable')
    if a: out.append(('Plocha', short_num(a)))
    if t in ('Rodinný dom', 'Pozemok', 'Chata / chalupa') and pv(x, 'area_plot'): out.append(('Pozemok', short_num(pv(x, 'area_plot'))))
    if t == 'Byt' and pv(x, 'floor'): out.append(('Poschodie', pv(x, 'floor').split(' (')[0].split(',')[0]))
    for f in x.get('facts') or []:
        if f.get('v') and f.get('l') and len(out) < 4: out.append((f['l'], f['v']))
    return out[:4]

for x in LIST:
    x['st'] = STATUS.get(x.get('status'), STATUS['aktualne'])
    x['href'] = f'nehnutelnosti/{x["slug"]}.html'
    x['cover'] = (x.get('photos') or [None])[0] or (x.get('viz') or [''])[0]
    x['card_title'] = x.get('short') or x['title']
def is_done(x): return x['st'][2] == 'done'
ACTIVE = [x for x in LIST if not is_done(x)]
DONE = [x for x in LIST if is_done(x)]

def badges(x):
    key, lab, kind = x['st']
    out = f'<span class="badge badge--kind">{KIND.get(x.get("kind"), "Na predaj")}</span>'
    if kind != 'live': out += f'<span class="badge badge--{kind}">{lab}</span>'
    return out

def card(x, i=0, cls=''):
    key, lab, kind = x['st']
    facts = ''.join(f'<span>{esc(v)}<small>{esc(l)}</small></span>' for l, v in key_facts(x)[:3])
    price = f'<p class="lc-price">{esc(x.get("price") or "Cena na vyžiadanie")}</p>' if kind != 'done' else f'<p class="lc-price lc-price--done">{lab}</p>'
    return (f'<a href="@/{x["href"]}" class="lcard rv {cls}{" is-done" if kind == "done" else ""}" style="--i:{i % 3}" data-kind="{esc(x.get("kind") or "predaj")}" data-type="{esc(x.get("type") or "")}">'
            f'<div class="lc-media"><img {img_attrs(x["cover"], "(max-width: 760px) 100vw, 40vw")} alt="{esc(x["title"])}" loading="lazy" decoding="async">'
            f'<div class="lc-badges">{badges(x)}</div><span class="lc-go">{ARR}</span></div>'
            f'<div class="lc-body"><p class="lc-loc">{PIN}{esc(x.get("locality") or "")}</p><h3>{esc(x["card_title"])}</h3>'
            f'<div class="lc-facts">{facts}</div>{price}</div></a>')

# ------------------------------------------------------------------ layout
NAV = [('ponuka.html', 'Ponuka'), ('index.html#o-mne', 'O mne'), ('index.html#spolupraca', 'Spolupráca'), ('kontakt.html', 'Kontakt')]

def head(title, desc, r, img, path, ld=''):
    return f'''<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#F4F0E6">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{BASE}{img}">
<meta property="og:url" content="{BASE}{path}">
<meta property="og:type" content="website">
<meta property="og:locale" content="sk_SK">
<link rel="canonical" href="{BASE}{path}">{ld}
<link rel="icon" href="{r}img/site/mark.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{r}img/site/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..500;1,6..72,300..500&family=Hanken+Grotesk:wght@400..650&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{r}assets/css/style.css?v={_ver('assets/css/style.css')}">
<script src="{r}assets/js/main.js?v={_ver('assets/js/main.js')}" defer></script>
</head>'''

def header(r, active):
    links = ''.join(f'<a href="{r}{h}" class="nl{" on" if h == active else ""}">{t}</a>' for h, t in NAV)
    return f'''<a class="skip" href="#obsah">Preskočiť na obsah</a>
<header class="nav">
  <div class="nav-in">
    <a href="{r}index.html" class="brand" aria-label="Fürsten Reality – domov"><img src="{r}img/site/logo.svg" alt="Fürsten Reality" width="210" height="61"></a>
    <nav class="menu" aria-label="Hlavná navigácia">
      {links}
      <a class="menu-tel" href="{TEL_H}">{PHONE}<span>{esc(TEL)}</span></a>
      <a href="{r}predat.html" class="btn btn--sm">{esc(T('home.cta_sell').replace(' nehnuteľnosť', ''))}</a>
    </nav>
    <button class="burger" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
  </div>
</header>'''

def monogram(cls=''):
    return (f'<div class="mono {cls}" aria-hidden="true"><svg viewBox="0 0 200 260"><path d="M10 258V100a90 90 0 0 1 180 0v158" fill="none" stroke="currentColor" stroke-width="1"/>'
            f'<path d="M26 258V104a74 74 0 0 1 148 0v154" fill="none" stroke="currentColor" stroke-width=".6" opacity=".55"/></svg><span>MF</span><small>Mária Fürsten</small></div>')

def portrait(cls='', eager=False):
    if PHOTO:
        return f'<img class="{cls}" {img_attrs(PHOTO, "(max-width: 760px) 90vw, 40vw")} alt="{esc(NAME)}, realitná maklérka" {"" if eager else "loading=\"lazy\""}>'
    return monogram(cls)

def footer(r):
    lg = lambda v, ph='doplní sa pred spustením': esc(v) if v else f'<mark class="todo">{ph}</mark>'
    soc = ''.join(f'<li><a class="u" href="{esc(T(k))}" target="_blank" rel="noopener">{n}</a></li>' for k, n in (('contact.facebook', 'Facebook'), ('contact.instagram', 'Instagram')) if T(k))
    return f'''<footer class="foot">
  <div class="wrap">
    <div class="foot-top">
      <div class="foot-brand">
        <img src="{r}img/site/logo-light.svg" alt="Fürsten Reality" width="210" height="61">
        <p>{esc(T('footer.text'))}</p>
      </div>
      <div><h4>Web</h4><ul>
        <li><a class="u" href="{r}ponuka.html">Ponuka nehnuteľností</a></li>
        <li><a class="u" href="{r}predat.html">Chcem predať</a></li>
        <li><a class="u" href="{r}hladam.html">Hľadám nehnuteľnosť</a></li>
        <li><a class="u" href="{r}index.html#o-mne">O mne</a></li>
        <li><a class="u" href="{r}kontakt.html">Kontakt</a></li>
      </ul></div>
      <div><h4>Kontakt</h4><ul>
        <li><a class="u" href="{TEL_H}">{esc(TEL)}</a></li>
        <li><a class="u" href="mailto:{esc(MAIL)}">{esc(MAIL)}</a></li>
        <li>{esc(T('contact.region'))}</li>
        <li><a class="u" href="{esc(T('contact.vr_url'))}" target="_blank" rel="noopener">Môj profil na Vaše reality</a></li>{soc}
      </ul></div>
      <div><h4>Podnikateľ</h4><ul class="legal">
        <li>{esc(T('legal.name'))}</li>
        <li>IČO: {lg(T('legal.ico'))}</li>
        <li>Miesto podnikania: {lg(T('legal.address'))}</li>
        <li>{lg(T('legal.register'), 'zápis v registri – doplní sa')}</li>
      </ul></div>
    </div>
    <p class="foot-coop">{esc(T('legal.coop'))}</p>
    <div class="foot-bot">
      <span>© {date.today().year} Fürsten Reality · Mária Fürsten</span>
      <span class="foot-links"><a class="u" href="{r}ochrana-osobnych-udajov.html">Ochrana osobných údajov</a><a class="u foot-admin" href="{r}admin/">{LOCK} Administrácia</a></span>
    </div>
  </div>
</footer>'''

def mbar(r, second=None):
    s = second or (f'{r}kontakt.html#formular', 'Napísať')
    return f'<div class="mbar" aria-label="Rýchly kontakt"><a href="{TEL_H}" class="mbar-call">{PHONE}<span>Zavolať</span></a><a href="{s[0]}" class="mbar-go"><span>{esc(s[1])}</span>{ARR}</a></div>'

def nbsp_text(doc):
    """non-breaking spaces in numbers (1 050 m², 155 000 €) — only in text nodes, never in tags/scripts"""
    parts = re.split(r'(<script.*?</script>|<style.*?</style>|<[^>]+>)', doc, flags=re.S)
    for i in range(0, len(parts), 2):
        t = re.sub(r'(?<=\d) (?=\d{3}\b)', '\u00a0', parts[i])
        parts[i] = re.sub(r'(?<=\d) (?=(m²|€|izb|m\b|%))', '\u00a0', t)
    return ''.join(parts)

PAGES = []
def write(path, title, desc, body, active='', img='img/site/og.jpg', ld='', second=None):
    r = '../' * path.count('/')
    doc = head(title, desc, r, img, '' if path == 'index.html' else path, ld) + '\n<body>\n' + header(r, active) + \
        f'\n<main id="obsah">\n{body}\n</main>\n' + footer(r) + '\n' + mbar(r, second) + '\n</body>\n</html>\n'
    doc = doc.replace('@/', r)
    doc = nbsp_text(doc)
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    open(path, 'w', encoding='utf-8').write(doc); PAGES.append(path)

LD_AGENT = '\n<script type="application/ld+json">' + json.dumps({
    '@context': 'https://schema.org', '@type': 'RealEstateAgent', 'name': 'Fürsten Reality – Mária Fürsten', 'url': BASE,
    'logo': BASE + 'img/site/logo.svg', 'image': BASE + 'img/site/og.jpg', 'telephone': re.sub(r'[^\d+]', '', TEL), 'email': MAIL,
    'areaServed': ['Dubnica nad Váhom', 'Ilava', 'Trenčín', 'Nová Dubnica', 'Trenčianske Teplice', 'Púchov'],
    'knowsLanguage': ['sk', 'cs', 'de'], 'founder': {'@type': 'Person', 'name': NAME, 'jobTitle': 'realitná maklérka'},
    'address': {'@type': 'PostalAddress', 'addressLocality': 'Dubnica nad Váhom', 'addressCountry': 'SK'},
}, ensure_ascii=False) + '</script>'

# ------------------------------------------------------------------ forms
FID = [0]
def nid():
    FID[0] += 1; return f'f{FID[0]}'
def f_in(name, label, typ='text', req=False, ph='', auto='', full=False, mode=''):
    fid = nid()
    a = (' required' if req else '') + (f' placeholder="{esc(ph)}"' if ph else '') + (f' autocomplete="{auto}"' if auto else '') + (f' inputmode="{mode}"' if mode else '')
    star = '<i>*</i>' if req else ''
    return f'<div class="fld{" full" if full else ""}"><label for="{fid}">{esc(label)}{star}</label><input id="{fid}" type="{typ}" name="{esc(name)}"{a}></div>'
def f_area(name, label, ph='', val='', req=False):
    fid = nid()
    return f'<div class="fld full"><label for="{fid}">{esc(label)}{"<i>*</i>" if req else ""}</label><textarea id="{fid}" name="{esc(name)}" rows="4" placeholder="{esc(ph)}"{" required" if req else ""}>{esc(val)}</textarea></div>'
def f_chips(name, label, opts, multi=False, first=True):
    typ = 'checkbox' if multi else 'radio'
    items = ''.join(f'<label class="chip"><input type="{typ}" name="{esc(name)}" value="{esc(o)}"{" checked" if (k == 0 and first and not multi) else ""}><span>{esc(o)}</span></label>' for k, o in enumerate(opts))
    return f'<fieldset class="fld full"><legend>{esc(label)}</legend><div class="chips">{items}</div></fieldset>'
def f_contact(msg_label='Správa', msg_ph='', msg_val='', msg_req=False):
    return (f_in('Meno', 'Meno a priezvisko', req=True, auto='name') + f_in('Telefón', 'Telefón', 'tel', auto='tel', ph='+421 …', mode='tel')
            + f_in('E-mail', 'E-mail', 'email', auto='email', full=True) + f_area('Správa', msg_label, msg_ph, msg_val, msg_req))
def form(kind, fields, submit, thanks, listing=None, cls=''):
    data = f' data-listing-id="{esc(listing["ref"] or listing["slug"])}" data-listing-title="{esc(listing["title"])}" data-listing-url="{BASE}{listing["href"]}"' if listing else ''
    return f'''<form class="form {cls}" data-form="{kind}" data-api="{FORM_API}" novalidate{data}>
  <div class="form-grid">{fields}</div>
  <div class="hp" aria-hidden="true"><label>Web<input type="text" name="website" tabindex="-1" autocomplete="off"></label></div>
  <label class="consent"><input type="checkbox" name="Súhlas" value="áno" required><span>Súhlasím so spracovaním osobných údajov na účel vybavenia mojej požiadavky. <a class="u" href="@/ochrana-osobnych-udajov.html" target="_blank">Viac informácií</a></span></label>
  <div class="form-foot"><p class="form-note">Telefón alebo e-mail stačí jedno. Odpovedám zvyčajne v ten istý deň.</p><button type="submit" class="btn"><span>{esc(submit)}</span>{ARR}</button></div>
  <p class="form-err" role="alert"></p>
  <div class="form-done" role="status" tabindex="-1"><span class="done-ic">{CHECK}</span><p>{md(thanks)}</p><small>Ak je to naliehavé, zavolajte mi na <a class="u" href="{TEL_H}">{esc(TEL)}</a>.</small></div>
</form>'''

# ------------------------------------------------------------------ sections
def contact_section(title=None, text=None, anchor='kontakt', show_head=True):
    fields = f_chips('Téma', 'S čím vám môžem pomôcť?', ['Predaj', 'Kúpa', 'Prenájom', 'Iné']) + f_contact('Správa', 'Napíšte pár viet – o akú nehnuteľnosť ide, kde sa nachádza, čo potrebujete…')
    return f'''<section class="sec contact" id="{anchor}">
  <div class="wrap contact-grid">
    <div class="contact-side">
      {f'<p class="eyebrow rv">{esc(T("contactsec.label"))}</p>' + heading(title or T('contactsec.title'), 'h2', 'rv') if show_head else ''}
      <p class="lead rv">{md(text or T('contactsec.text'))}</p>
      <div class="cbig rv">
        <a href="{TEL_H}" class="cb-line"><small>Telefón</small><span>{esc(TEL)}</span></a>
        <a href="mailto:{esc(MAIL)}" class="cb-line"><small>E-mail</small><span>{esc(MAIL)}</span></a>
        <div class="cb-line"><small>Kedy</small><span class="cb-s">{esc(T('contact.hours'))}</span></div>
      </div>
      <div class="agent-mini rv">{portrait('am-photo')}<div><b>{esc(NAME)}</b><small>{esc(T('contact.role'))} · Fürsten Reality<br>v spolupráci s VAŠE REALITY s.r.o.</small></div></div>
    </div>
    <div class="contact-form rv" id="formular">{form('kontakt', fields, 'Odoslať správu', T('contactpage.thanks'))}</div>
  </div>
</section>'''

def offmarket_band():
    return f'''<section class="offm">
  <div class="wrap offm-in rv">
    <div><h2>{md(T('offmarket.title'))}</h2><p>{md(T('offmarket.text'))}</p></div>
    {btn('@/hladam.html', T('offmarket.btn'), 'btn--gold')}
  </div>
</section>'''

def reviews_section():
    if not REVS: return ''
    items = ''.join(f'<figure class="rev rv" style="--i:{k % 3}"><blockquote>{esc(v.get("text", ""))}</blockquote><figcaption><b>{esc(v.get("name", ""))}</b><span>{esc(v.get("meta", "") or v.get("date", ""))}</span></figcaption></figure>' for k, v in enumerate(REVS))
    return f'''<section class="sec reviews" id="referencie">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow rv">{esc(T('reviews.label'))}</p><h2 class="rv">{md(T('reviews.title'))}</h2></div></div>
    <div class="rev-grid">{items}</div>
  </div>
</section>'''

def process_steps():
    return ''.join(f'<li class="step rv" style="--i:{k % 3}"><span class="step-n">{k + 1:02d}</span><h3>{esc(s.get("title", ""))}</h3><p>{esc(s.get("text", ""))}</p></li>' for k, s in enumerate(TL('process.steps')))

# ================================================================== HOME
def build_home():
    feat = [x for x in ACTIVE if x.get('home')] or ACTIVE[:5]
    cards = ''.join(card(x, k, 'big' if k == 0 else '') for k, x in enumerate(feat[:5]))
    n = len(ACTIVE)
    cards += f'''<a href="@/ponuka.html" class="lcard lcard--all rv" style="--i:2"><span class="eyebrow">Celá ponuka</span><b>{n} {"nehnuteľnosť" if n == 1 else "nehnuteľnosti" if 1 < n < 5 else "nehnuteľností"}</b><span class="lc-all-go">Pozrieť všetky {ARR}</span></a>'''
    facts = ''.join(f'<div class="fact rv" style="--i:{k}"><small>{esc(f.get("title", ""))}</small><span>{esc(f.get("text", ""))}</span></div>' for k, f in enumerate(TL('about.facts')))
    svc = ''
    for k, s in enumerate(TL('services.items')):
        pts = ''.join(f'<li>{CHECK}<span>{esc(p.strip())}</span></li>' for p in str(s.get('points', '')).split('\n') if p.strip())
        svc += (f'<article class="svc rv" style="--i:{k}"><span class="svc-n">0{k + 1}</span><h3>{esc(s.get("title", ""))}</h3><p class="svc-lead">{esc(s.get("text", ""))}</p>'
                f'<ul>{pts}</ul>{("<a class=" + chr(34) + "lnk" + chr(34) + " href=" + chr(34) + link(s.get("link")) + chr(34) + ">Viac " + ARR + "</a>") if s.get("link") else ""}</article>')
    hero_img = T('home.hero_image')
    body = f'''
<section class="hero">
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow fade" style="--d:.05s">{esc(T('home.hero_label'))}</p>
      {heading(T('home.hero_title'), 'h1', 'hero-h')}
      <p class="hero-sub fade" style="--d:.45s">{md(T('home.hero_sub'))}</p>
      <div class="hero-ctas fade" style="--d:.6s">
        <a href="@/predat.html" class="cta-card cta-card--dark"><span class="cta-k">01</span><b>{esc(T('home.cta_sell'))}</b><small>{esc(T('home.cta_sell_sub'))}</small><span class="cta-arr">{ARR}</span></a>
        <a href="@/hladam.html" class="cta-card"><span class="cta-k">02</span><b>{esc(T('home.cta_buy'))}</b><small>{esc(T('home.cta_buy_sub'))}</small><span class="cta-arr">{ARR}</span></a>
      </div>
      <p class="hero-coop fade" style="--d:.75s"><span class="dot"></span>Fürsten Reality · v spolupráci s VAŠE REALITY s.r.o.</p>
    </div>
    <figure class="hero-fig fade" style="--d:.2s">
      <div class="arch"><img {img_attrs(hero_img, "(max-width: 760px) 92vw, 42vw")} alt="{esc(T('home.hero_caption'))}" fetchpriority="high"></div>
      <figcaption>{esc(T('home.hero_caption'))}</figcaption>
      <div class="hero-card">
        {portrait('hc-photo', True)}
        <div><b>{esc(NAME)}</b><small>{esc(T('contact.role'))}</small><a href="{TEL_H}">{PHONE}{esc(TEL)}</a></div>
      </div>
    </figure>
  </div>
  <div class="wrap hero-areas fade" style="--d:.9s" aria-label="Kde pôsobím">
    {''.join(f'<span>{esc(a)}</span>' for a in ['Dubnica nad Váhom', 'Ilava', 'Trenčín', 'Nová Dubnica', 'Trenčianske Teplice', 'Púchov a okolie'])}
  </div>
</section>

<section class="sec offers">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow rv">{esc(T('home.offers_label'))}</p><h2 class="rv">{md(T('home.offers_title'))}</h2></div>
      <p class="lead rv">{md(T('home.offers_lead'))}</p>
    </div>
    <div class="lgrid lgrid--home">{cards}</div>
  </div>
</section>

<section class="sec about" id="o-mne">
  <div class="wrap about-grid">
    <figure class="about-fig rv">
      <div class="arch arch--tall">{portrait('about-photo')}</div>
    </figure>
    <div class="about-copy">
      <p class="eyebrow rv">{esc(T('about.label'))}</p>
      {heading(T('about.title'), 'h2', 'rv')}
      <div class="prose rv">{paras(T('about.text'))}</div>
      <p class="sig rv">{esc(T('about.signature'))}</p>
      <div class="facts">{facts}</div>
    </div>
  </div>
</section>

<section class="sec services" id="spolupraca">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow rv">{esc(T('services.label'))}</p><h2 class="rv">{md(T('services.title'))}</h2></div>
    </div>
    <div class="svc-grid">{svc}</div>
  </div>
</section>

<section class="sec process">
  <div class="wrap">
    <div class="sec-head">
      <div><p class="eyebrow rv">{esc(T('process.label'))}</p><h2 class="rv">{md(T('process.title'))}</h2></div>
      <p class="lead rv">{md(T('process.lead'))}</p>
    </div>
    <ol class="steps">{process_steps()}</ol>
    <div class="process-cta rv">{btn('@/predat.html', T('home.cta_sell'))}{btn('@/hladam.html', T('home.cta_buy'), 'btn--ghost')}</div>
  </div>
</section>

{reviews_section()}

{contact_section()}
'''
    write('index.html', T('home.seo_title'), T('home.seo_desc'), body, 'index.html', ld=LD_AGENT)

# ================================================================== PONUKA
def build_offer():
    from collections import Counter
    c = Counter();
    for x in ACTIVE:
        c[x.get('kind')] += 1; c[x.get('type')] += 1
    chips = [('all', 'Všetko', len(ACTIVE)), ('kind:predaj', 'Na predaj', c['predaj']), ('kind:prenajom', 'Na prenájom', c['prenajom']),
             ('type:Rodinný dom', 'Domy', c['Rodinný dom']), ('type:Byt', 'Byty', c['Byt']), ('type:Pozemok', 'Pozemky', c['Pozemok'])]
    chip_html = ''.join(f'<button class="fchip{" on" if k == "all" else ""}" data-f="{esc(k)}">{t}<sup>{n}</sup></button>' for k, t, n in chips if n or k == 'all')
    grid = ''.join(card(x, k) for k, x in enumerate(ACTIVE))
    sold = ''
    if DONE:
        sold = f'''<section class="sec sold" id="predane">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow rv">Referencie z praxe</p><h2 class="rv">{md(T('offer.sold_title'))}</h2></div></div>
    <div class="lgrid">{''.join(card(x, k) for k, x in enumerate(DONE))}</div>
  </div>
</section>'''
    body = f'''
<section class="phero">
  <div class="wrap phero-grid">
    <div><nav class="crumbs"><a href="@/index.html">Domov</a><span>Ponuka</span></nav>
      {heading(T('offer.title'), 'h1')}</div>
    <p class="lead fade" style="--d:.3s">{md(T('offer.lead'))}</p>
  </div>
</section>
<section class="sec sec--tight">
  <div class="wrap">
    <div class="filters" role="group" aria-label="Filter ponuky">{chip_html}</div>
    <div class="lgrid" data-grid>{grid}</div>
    <p class="empty-note" hidden>{md(T('offer.empty'))}</p>
  </div>
</section>
{offmarket_band()}
{sold}
'''
    write('ponuka.html', T('offer.seo_title'), T('offer.seo_desc'), body, 'ponuka.html')

# ================================================================== DETAIL
def gal_links(imgs, group, label=''):
    return ''.join(f'<a href="@/{esc(p)}" data-lb="{group}"{f" data-cap={chr(34)}{esc(label)}{chr(34)}" if label else ""}><img {img_attrs(p, "(max-width: 760px) 50vw, 25vw")} alt="" loading="lazy" decoding="async">{f"<span class={chr(34)}vtag{chr(34)}>{esc(label)}</span>" if label else ""}</a>' for p in imgs)

def build_details():
    shutil.rmtree('nehnutelnosti', ignore_errors=True)
    for x in LIST:
        key, lab, kind = x['st']
        photos, plans, viz = x.get('photos') or [], x.get('plans') or [], x.get('viz') or []
        allp = photos or viz
        # mosaic: first 5 photos; mobile: swipe strip of all photos
        mosaic = ''.join(f'<a href="@/{esc(p)}" data-lb="photos" class="m{k}"><img {img_attrs(p, "(max-width: 760px) 100vw, 60vw" if k == 0 else "25vw")} alt="{esc(x["title"])} – fotografia {k + 1}" {"fetchpriority=" + chr(34) + "high" + chr(34) if k == 0 else "loading=" + chr(34) + "lazy" + chr(34)} decoding="async"></a>' for k, p in enumerate(allp[:5]))
        more = f'<button class="gal-all" data-open="photos">{GRID}<span>Všetky fotografie ({len(allp)})</span></button>' if len(allp) > 1 else ''
        hidden = ''.join(f'<a href="@/{esc(p)}" data-lb="photos" hidden></a>' for p in allp[5:])
        strip = ''.join(f'<a href="@/{esc(p)}" data-lb="strip"><img {img_attrs(p, "100vw")} alt="" loading="{"eager" if k == 0 else "lazy"}" decoding="async"></a>' for k, p in enumerate(allp))
        ptype = x.get('type') or 'Byt'
        keys = TYPE_PARAMS.get(ptype, [k for k, _ in PARAMS])
        rows = [(PLABEL[k], pv(x, k)) for k in keys if pv(x, k)] + [(f.get('l', ''), f.get('v', '')) for f in (x.get('facts') or []) if f.get('v')]
        if ptype == 'Rodinný dom' and pv(x, 'area_usable') and 'obytn' in pv(x, 'area_usable'):
            rows = [(('Obytná plocha' if l == 'Úžitková plocha' else l), v.replace(' obytná plocha', '')) for l, v in rows]
        ptable = ''.join(f'<div class="pr"><dt>{esc(l)}</dt><dd>{esc(v)}</dd></div>' for l, v in rows)
        kf = ''.join(f'<div><small>{esc(l)}</small><b>{esc(v)}</b></div>' for l, v in key_facts(x))
        price_incl = x.get('price_includes') or T('detail.price_default')
        sec_plans = (f'<section class="dsec rv" id="podorys"><h2>Pôdorys</h2><div class="gal gal--plans">{gal_links(plans, "plans")}</div></section>' if plans
                     else f'<section class="dsec dsec--soft rv" id="podorys"><h2>Pôdorys</h2><p class="muted">{esc(T("detail.plan_missing"))} <a class="u" href="#obhliadka" data-ask="Prosím o zaslanie pôdorysu.">Požiadať o pôdorys</a></p></section>')
        vnote = x.get('viz_note') or T('detail.viz_note')
        sec_viz = f'<section class="dsec rv" id="vizualizacie"><h2>Vizualizácie <span class="vpill">ilustračné</span></h2><p class="vnote">{esc(vnote)}</p><div class="gal">{gal_links(viz, "viz", "Vizualizácia")}</div></section>' if viz and photos else ''
        yt = re.search(r'(?:youtu\.be/|v=|embed/|shorts/)([\w-]{11})', x.get('video') or '')
        sec_video = (f'<section class="dsec rv" id="video"><h2>Video</h2><button class="yt" data-yt="{yt.group(1)}" aria-label="Prehrať video"><img src="https://i.ytimg.com/vi/{yt.group(1)}/hqdefault.jpg" alt="" loading="lazy"><span>{PLAY}</span></button></section>'
                     if yt else (f'<section class="dsec rv" id="video"><h2>Video</h2><p><a class="lnk" href="{esc(x["video"])}" target="_blank" rel="noopener">Pozrieť video {ARR}</a></p></section>' if x.get('video') else ''))
        sec_tour = f'<a class="tour rv" href="{esc(x["tour"])}" target="_blank" rel="noopener">{CUBE}<span><b>3D prehliadka</b><small>Prejdite sa nehnuteľnosťou online</small></span>{ARR}</a>' if x.get('tour') else ''
        geo = x.get('geo') or []
        mapq = f'{geo[0]},{geo[1]}' if len(geo) == 2 and geo[0] else (x.get('address') or x.get('locality') or '')
        sec_map = (f'<section class="dsec rv" id="lokalita"><h2>Lokalita</h2><p class="muted">{PIN} {esc(x.get("address") or x.get("locality") or "")} · poloha je orientačná</p>'
                   f'<div class="map" data-map="https://maps.google.com/maps?q={urllib.parse.quote(mapq)}&z=14&output=embed"><button class="btn btn--ghost btn--sm" type="button">{MAPI}<span>Zobraziť mapu</span></button></div></section>') if mapq else ''
        msg = f'Dobrý deň, mám záujem o obhliadku nehnuteľnosti „{x["title"]}“ (ID {x.get("ref") or x["slug"]}). '
        fields = f_contact('Správa', '', msg) + f_in('Termín', 'Kedy by vám obhliadka vyhovovala?', ph='napr. v týždni poobede, v sobotu dopoludnia', full=True)
        others = [o for o in ACTIVE if o is not x]
        others = sorted(others, key=lambda o: (o.get('type') != x.get('type'), o.get('kind') != x.get('kind')))[:3]
        done_note = f'<p class="done-note">{lab} – nehnuteľnosť už má nového {"majiteľa" if key == "predane" else "nájomcu"}. Hľadáte podobnú? <a class="u" href="@/hladam.html">Napíšte mi</a>.</p>' if kind == 'done' else ''
        pcard = f'''      <div class="pcard">
        <small>{'Mesačný nájom' if x.get('kind') == 'prenajom' else 'Cena'}</small>
        <b class="pc-price">{esc(x.get('price') or 'Na vyžiadanie') if kind != 'done' else lab}</b>
        {f'<p class="pc-note">{esc(x["price_note"])}</p>' if x.get('price_note') else ''}
        <div class="pc-incl"><small>Čo cena zahŕňa</small><p>{esc(price_incl)}</p></div>
        <div class="pc-agent">{portrait('pa-photo')}<div><b>{esc(NAME)}</b><small>{esc(T('detail.agent_sub'))}</small></div></div>
        <a class="pc-tel" href="{TEL_H}">{PHONE}<span>{esc(TEL)}</span></a>
        <a class="pc-mail u" href="mailto:{esc(MAIL)}?subject={urllib.parse.quote(x['title'] + ' (ID ' + str(x.get('ref') or x['slug']) + ')')}">{esc(MAIL)}</a>
        {btn('#obhliadka', T('detail.btn'), 'btn--block')}
      </div>'''
        body = f'''
<article class="detail" data-listing="{esc(x['slug'])}">
<section class="dhead">
  <div class="wrap">
    <nav class="crumbs"><a href="@/index.html">Domov</a><a href="@/ponuka.html">Ponuka</a><span>{esc(x['card_title'])}</span></nav>
    <div class="dhead-row">
      <div>
        <div class="dbadges fade">{badges(x)}<span class="badge badge--line">{esc(ptype)}</span></div>
        <h1 class="dtitle fade" style="--d:.1s">{esc(x['title'])}</h1>
        <p class="dloc fade" style="--d:.2s">{PIN}{esc(x.get('address') or x.get('locality') or '')}</p>
      </div>
      <div class="dprice fade" style="--d:.25s"><small>{'Nájom' if x.get('kind') == 'prenajom' else 'Cena'}</small><b>{esc(x.get('price') or 'Na vyžiadanie') if kind != 'done' else lab}</b></div>
    </div>
  </div>
</section>
<section class="dgal">
  <div class="wrap">
    <div class="mosaic n{min(5, len(allp))}">{mosaic}{hidden}{more}</div>
    <div class="strip-wrap"><div class="strip" data-strip>{strip}</div><span class="strip-count"><b data-strip-i>1</b> / {len(allp)}</span></div>
  </div>
</section>
<section class="sec sec--tight">
  <div class="wrap dgrid">
    <div class="dmain">
      {done_note}
      <p class="dlead rv">{esc(x.get('lead') or '')}</p>
      <div class="kfacts rv">{kf}</div>
      <div class="pc-inline rv">{pcard}</div>
      <section class="dsec rv" id="parametre"><h2>Parametre</h2><dl class="ptable">{ptable}</dl></section>
      <section class="dsec" id="popis"><h2 class="rv">Popis</h2><div class="prose prose--listing rv">{clean_html(x.get('body'))}</div></section>
      {sec_tour}
      {sec_plans}
      {sec_video}
      {sec_viz}
      {sec_map}
      <section class="dsec dform" id="obhliadka">
        <h2 class="rv">{md(T('detail.form_title'))}</h2>
        <p class="muted rv">Nehnuteľnosť: <b>{esc(x['title'])}</b> · ID {esc(x.get('ref') or x['slug'])}</p>
        <div class="rv">{form('obhliadka', fields, T('detail.btn'), 'Ďakujem, *ozvem sa vám* a dohodneme termín obhliadky.', x)}</div>
      </section>
    </div>
    <aside class="dside">
      {pcard}
    </aside>
  </div>
</section>
</article>
<section class="sec more">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow rv">Mohlo by vás zaujímať</p><h2 class="rv">Ďalšie <em>nehnuteľnosti</em></h2></div><a class="lnk rv" href="@/ponuka.html">Celá ponuka {ARR}</a></div>
    <div class="lgrid">{''.join(card(o, k) for k, o in enumerate(others))}</div>
  </div>
</section>
<div class="lb" role="dialog" aria-modal="true" aria-label="Galéria" hidden>
  <div class="lb-stage"><img alt=""></div>
  <span class="lb-cap"></span><span class="lb-count"></span>
  <button class="lb-x" aria-label="Zavrieť">{ico('<path d="M6 6l12 12M18 6L6 18"/>', 22)}</button>
  <button class="lb-p" aria-label="Predchádzajúca">{ARR_L}</button><button class="lb-n" aria-label="Ďalšia">{ARR}</button>
</div>
'''
        desc = x.get('seo_desc') or (x.get('lead') or x['title'])[:158]
        ld = '\n<script type="application/ld+json">' + json.dumps({
            '@context': 'https://schema.org', '@type': 'Product', 'additionalType': 'https://schema.org/RealEstateListing',
            'name': x['title'], 'description': desc, 'image': [BASE + p for p in allp[:6]], 'url': BASE + x['href'],
            'offers': {'@type': 'Offer', 'priceCurrency': 'EUR', 'price': re.sub(r'[^\d]', '', (x.get('price') or '').split('/')[0]) or None,
                       'availability': 'https://schema.org/SoldOut' if kind == 'done' else 'https://schema.org/InStock'},
        }, ensure_ascii=False) + '</script>'
        title = f"{x['title']} – {x.get('price') or 'cena na vyžiadanie'} | Fürsten Reality"
        write(x['href'], title, desc, body, 'ponuka.html', x['cover'], ld, second=('#obhliadka', T('detail.btn')))

# ================================================================== CHCEM PREDAŤ
def build_sell():
    pts = ''.join(f'<li class="rv" style="--i:{k}">{CHECK}<span>{esc(p.get("title", ""))}</span></li>' for k, p in enumerate(TL('sell.points')))
    fields = (f_chips('Typ nehnuteľnosti', 'Čo predávate?', ['Byt', 'Rodinný dom', 'Pozemok', 'Chata / chalupa', 'Iné'])
              + f_in('Lokalita', 'Lokalita (obec, ulica)', req=True, ph='napr. Dubnica nad Váhom, Pod hájom', full=True)
              + f_in('Rozloha', 'Približná rozloha', ph='napr. 3 izby, 72 m²', full=True)
              + f_contact('Krátka správa', 'Kedy by ste chceli predávať, v akom je nehnuteľnosť stave…'))
    body = f'''
<section class="phero phero--form">
  <div class="wrap form-page">
    <div class="fp-side">
      <nav class="crumbs"><a href="@/index.html">Domov</a><span>Chcem predať</span></nav>
      {heading(T('sell.title'), 'h1')}
      <p class="lead fade" style="--d:.3s">{md(T('sell.lead'))}</p>
      <ul class="ticks">{pts}</ul>
      <div class="agent-mini fade" style="--d:.5s">{portrait('am-photo')}<div><b>{esc(NAME)}</b><small>Radšej telefonicky? <a class="u" href="{TEL_H}">{esc(TEL)}</a></small></div></div>
    </div>
    <div class="fp-form fade" style="--d:.2s" id="formular-predaj">{form('predaj', fields, 'Odoslať', T('sell.thanks'))}</div>
  </div>
</section>
<section class="sec process process--page">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow rv">{esc(T('process.label'))}</p><h2 class="rv">{md(T('process.title'))}</h2></div><p class="lead rv">{md(T('process.lead'))}</p></div>
    <ol class="steps">{process_steps()}</ol>
  </div>
</section>
'''
    write('predat.html', T('sell.seo_title'), T('sell.seo_desc'), body, 'predat.html', second=('#formular-predaj', 'Formulár'))

# ================================================================== HĽADÁM
def build_search():
    fields = (f_chips('Chcem', 'Chcem', ['Kúpiť', 'Prenajať si'])
              + f_chips('Typ', 'Čo hľadáte?', ['Byt', 'Rodinný dom', 'Pozemok', 'Chata / chalupa'], multi=True)
              + f_in('Lokalita', 'Lokalita', ph='napr. Dubnica, Ilava, Trenčín a okolie', full=True)
              + f_in('Rozpočet', 'Rozpočet do', ph='napr. 180 000 €', mode='text') + f_in('Izby', 'Počet izieb / plocha', ph='napr. 3 izby, od 70 m²')
              + f_contact('Čo je pre vás dôležité', 'Záhrada, parkovanie, škola nablízku, termín sťahovania…'))
    latest = ''.join(card(x, k) for k, x in enumerate(ACTIVE[:3]))
    body = f'''
<section class="phero phero--form">
  <div class="wrap form-page">
    <div class="fp-side">
      <nav class="crumbs"><a href="@/index.html">Domov</a><span>Hľadám nehnuteľnosť</span></nav>
      {heading(T('search.title'), 'h1')}
      <p class="lead fade" style="--d:.3s">{md(T('search.lead'))}</p>
      <div class="note-card fade" style="--d:.45s"><b>Neverejné ponuky</b><p>{md(T('offmarket.text'))}</p></div>
      <p class="fade" style="--d:.55s"><a class="lnk" href="@/ponuka.html">Pozrieť aktuálnu ponuku ({len(ACTIVE)}) {ARR}</a></p>
    </div>
    <div class="fp-form fade" style="--d:.2s" id="formular-hladam">{form('hladam', fields, 'Odoslať požiadavku', T('search.thanks'))}</div>
  </div>
</section>
<section class="sec more">
  <div class="wrap">
    <div class="sec-head"><div><p class="eyebrow rv">Práve v ponuke</p><h2 class="rv">Možno už <em>tu</em></h2></div><a class="lnk rv" href="@/ponuka.html">Celá ponuka {ARR}</a></div>
    <div class="lgrid">{latest}</div>
  </div>
</section>
'''
    write('hladam.html', T('search.seo_title'), T('search.seo_desc'), body, 'hladam.html', second=('#formular-hladam', 'Formulár'))

# ================================================================== KONTAKT
def build_contact():
    body = f'''
<section class="phero">
  <div class="wrap"><nav class="crumbs"><a href="@/index.html">Domov</a><span>Kontakt</span></nav>
    {heading(T('contactpage.title'), 'h1')}</div>
</section>
{contact_section(None, T('contactsec.text'), 'kontakt-form', show_head=False)}
{offmarket_band()}
'''
    write('kontakt.html', T('contactpage.seo_title'), f'Zavolajte na {TEL} alebo napíšte na {MAIL}. Mária Fürsten – realitná maklérka pre Dubnicu nad Váhom, Ilavu, Trenčín a okolie.', body, 'kontakt.html')

# ================================================================== GDPR
def build_privacy():
    out = []
    for block in re.split(r'\n\s*\n', T('privacy.body')):
        lines = [l for l in block.split('\n') if l.strip()]
        for l in lines:
            if l.startswith('## '): out.append(f'<h2>{esc(l[3:])}</h2>')
            else: out.append(f'<p>{todo_html(esc(l, quote=False))}</p>')
    body = f'''
<section class="phero">
  <div class="wrap"><nav class="crumbs"><a href="@/index.html">Domov</a><span>Ochrana osobných údajov</span></nav>
    <h1 class="split"><span class="ln"><span>Ochrana osobných <em>údajov</em></span></span></h1></div>
</section>
<section class="sec sec--tight"><div class="wrap narrow prose prose--legal">{''.join(out)}</div></section>
'''
    write('ochrana-osobnych-udajov.html', 'Ochrana osobných údajov | Fürsten Reality', 'Informácie o spracúvaní osobných údajov – Mária Fürsten, Fürsten Reality.', body)

def build_404():
    body = f'<section class="phero" style="min-height:70svh"><div class="wrap"><p class="eyebrow">404</p><h1 class="split"><span class="ln"><span>Táto stránka <em>neexistuje</em>.</span></span></h1><p class="lead">Možno bola nehnuteľnosť medzitým predaná. Pozrite si aktuálnu ponuku.</p><div class="row">{btn(BASE + "ponuka.html", "Aktuálna ponuka")}{btn(BASE, "Domov", "btn--ghost")}</div></div></section>'
    write('404.html', 'Stránka sa nenašla | Fürsten Reality', 'Stránka sa nenašla.', body)
    # 404 is served from any depth -> absolute asset paths
    s = open('404.html', encoding='utf-8').read().replace('href="assets/', f'href="{BASE}assets/').replace('src="assets/', f'src="{BASE}assets/') \
        .replace('src="img/', f'src="{BASE}img/').replace('href="img/', f'href="{BASE}img/')
    s = re.sub(r'href="(?!https?:|#|tel:|mailto:)([a-z][^"]*\.html[^"]*)"', lambda m: f'href="{BASE}{m.group(1)}"', s)
    open('404.html', 'w', encoding='utf-8').write(s)

def build_admin_assets():
    json.dump({'schema': SCHEMA}, open('admin/schema.json', 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump({'sha': os.environ.get('GITHUB_SHA', 'local'), 'built': date.today().isoformat()}, open('version.json', 'w'))
    ai = open('admin/index.html', encoding='utf-8').read()
    ai = re.sub(r'admin\.css\?v=\w+', 'admin.css?v=' + _ver('admin/admin.css'), ai)
    ai = re.sub(r'admin\.js\?v=\w+', 'admin.js?v=' + _ver('admin/admin.js'), ai)
    open('admin/index.html', 'w', encoding='utf-8').write(ai)

if __name__ == '__main__':
    build_home(); build_offer(); build_details(); build_sell(); build_search(); build_contact(); build_privacy(); build_404()
    build_admin_assets()
    print(f'{len(PAGES)} stránok vygenerovaných')
