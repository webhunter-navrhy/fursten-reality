#!/usr/bin/env python3
"""One-off import of Mária Fürsten's listings from Vaše reality (scraped.json + downloaded originals)
into _data/listings.json and img/nem/<slug>/NN.webp (max 2000 px) + NN-m.webp (900 px).
After the import, listings are edited in /admin/ — do not re-run over edited data."""
import json, os, re, html
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(ROOT, '_build', 'raw')

SALE_INCL = ('Cena je konečná a zahŕňa kompletný realitný a právny servis: rezervačnú a kúpnu zmluvu, právne poradenstvo '
             'počas celého prevodu, hypotekárne poradenstvo cez partnerov a správny poplatok za návrh na vklad do katastra.')

# per-listing curation: slug, titles, lead, photo classification (indexes of downloaded gallery), params, cut markers
CFG = {
 '2919': dict(slug='byt-orion-dubnica-nad-vahom', kind='predaj', type='Byt',
   title='Moderný 2-izbový byt v Orione, centrum Dubnice nad Váhom', short='Moderný 2-izbový byt v Orione',
   locality='Dubnica nad Váhom', address='Námestie Matice slovenskej, Dubnica nad Váhom',
   lead='Svetlý byt vo vyššom štandarde priamo v centre mesta – s kuchynským ostrovčekom, výťahom, bezbariérovým prístupom a podzemným parkovaním na 3 roky zadarmo.',
   photos=list(range(10)), plans=[], viz=[], home=True, order=1,
   price='155 000 €', price_note='Cena je konečná, nenavyšuje sa o províziu.',
   price_includes='V cene je zahrnutý kompletný realitný a právny servis súvisiaci s bezpečným prevodom nehnuteľnosti. Bonus: parkovanie v podzemnej garáži na 3 roky zadarmo.',
   params=dict(rooms='2', area_usable='57 m²', floor='8. poschodie', condition='Novostavba (kolaudácia 2017)', building='Zosilnený betón',
               heating='Centrálne + podlahové, vlastná regulácia', parking='Podzemná garáž – 3 roky zadarmo', ownership='Osobné', extras='Výťah, bezbariérový prístup, videovrátnik'),
   cut=['KONTAKT NA OBHLIADKU', 'CENA A SERVIS REALITNEJ KANCELÁRIE']),
 '2964': dict(slug='dom-so-zahradou-prejta', kind='predaj', type='Rodinný dom',
   title='Dom s potenciálom a veľkou záhradou, Prejta', short='Dom s veľkou záhradou',
   locality='Dubnica nad Váhom – Prejta', address='Družstevná ulica, Dubnica nad Váhom – Prejta',
   lead='Tehlový dom na rovinatom pozemku 1 050 m² v pokojnej časti Prejta. Veľké izby, pivnica, hospodárska budova a podkrovie, kde môžu vzniknúť ďalšie tri izby.',
   photos=[2, 5, 6, 7, 8, 9, 10, 11, 12, 13, 17, 19, 20], plans=[4], viz=[1, 3, 16, 15, 14, 18, 0], home=True, order=2,
   price='175 000 €', price_note='', price_includes='',
   params=dict(rooms='2 (+ potenciál 3 izieb v podkroví)', area_usable='80 m² obytná plocha', area_built='118 m²', area_plot='1 050 m²',
               condition='Pôvodný stav – na rekonštrukciu', building='Tehla', year='Kolaudácia 1980',
               utilities='Voda, elektrina, plyn, kanalizácia', heating='Lokálne', parking='Na vlastnom pozemku', ownership='Osobné',
               extras='Pivnica, komora, terasa, hospodárska budova'),
   viz_note='Vizualizácie sú ilustračné a predstavujú návrh možného vzhľadu domu po rekonštrukcii. Fotografie označené „Virtuálne upratané“ sú skutočné priestory, z ktorých boli digitálne odstránené veci.',
   cut=['Vizualizácie v inzeráte', 'Obhliadku si dohodnite']),
 '2791': dict(slug='rodinny-dom-mikusovce', kind='predaj', type='Rodinný dom',
   title='Rodinný dom so záhradou a jazierkom, Mikušovce', short='Rodinný dom so záhradou a jazierkom',
   locality='Mikušovce (okres Ilava)', address='Mikušovce, okres Ilava',
   lead='Dvojpodlažný tehlový dom z roku 2005 na slnečnom pozemku 1 048 m² – šesť izieb, krb, krytá terasa s vonkajším krbom a záhrada s jazierkom. Pripravený na okamžité nasťahovanie.',
   photos=list(range(13)), plans=[], viz=[], home=True, order=3,
   price='295 000 €', price_note='Zariadenie je možné po dohode ponechať.', price_includes=SALE_INCL,
   params=dict(rooms='6', area_usable='163 m²', area_plot='1 048 m²', condition='Výborný – bez potreby investícií', building='Tehla',
               year='Kolaudácia 2005', utilities='Elektrina, plyn, voda, septik', heating='Plynový kotol, podlahové + radiátory, krb',
               parking='2 autá na pozemku', ownership='Osobné', extras='Krytá terasa 20 m², záhradný domček, jazierko, pochôdzna povala'),
   cut=['ID :1100', 'Neváhajte nás kontaktovať a dohodnite si obhliadku']),
 '2941': dict(slug='dom-po-rekonstrukcii-cervenik', kind='predaj', type='Rodinný dom',
   title='Útulný dom po rekonštrukcii, Červeník', short='Menší dom po rekonštrukcii',
   locality='Červeník', address='Mlynská ulica, Červeník',
   lead='Kompaktné bývanie bez náročnej údržby – dom po rekonštrukcii s bezúdržbovým dvorom, novou strešnou krytinou a všetkými sieťami. Ideálny pre jednu osobu alebo pár.',
   photos=[0, 1, 3, 4, 5, 6, 7, 8, 9, 11, 12, 2], plans=[10], viz=[], home=True, order=4,
   price='135 000 €', price_note='', price_includes='',
   params=dict(rooms='2', area_usable='67 m²', area_plot='126 m²', condition='Po rekonštrukcii', building='Tehla',
               utilities='Voda, kanalizácia, elektrina, plyn, optika', heating='Plynové (gamatky)', parking='Na ulici', ownership='Osobné',
               extras='Dvor so zámkovou dlažbou, terasa, nová strecha'),
   cut=['Viac informácií a termín obhliadky']),
 '2954': dict(slug='dva-domy-horna-breznica', kind='predaj', type='Rodinný dom',
   title='Dva rodinné domy na pozemku 763 m², Horná Breznica', short='Dva domy so záhradou',
   locality='Horná Breznica (okres Púchov)', address='Horná Breznica, okres Púchov',
   lead='Vidiecka usadlosť s dvoma domami, garážou, hospodárskymi priestormi a vlastnou studňou. Pôvodný stav – priestor na rekonštrukciu presne podľa vás.',
   photos=[1, 3, 6, 7, 9, 10], plans=[12, 14, 11, 13], viz=[0, 4, 5, 8, 2], home=False, order=5,
   price='110 000 €', price_note='', price_includes='',
   params=dict(rooms='3 (2 + 1)', area_usable='110 m²', area_plot='763 m²', condition='Pôvodný stav – na rekonštrukciu', building='Tehla',
               year='1959 – 1966', utilities='Nová elektrická prípojka, vlastná studňa, žumpa (bez plynu)', heating='Lokálne',
               parking='Garáž', ownership='Osobné', extras='Pivnica, dielňa, sklady, hospodárska časť'),
   viz_note='Vizualizácie sú ilustračné a ukazujú možnú podobu po úprave. Pôdorysy sú orientačné, 3D pôdorysy s ilustračným zariadením.',
   cut=['CENA: 110 000', 'Pre bližšie informácie']),
 '2905': dict(slug='dom-dva-byty-inovecka-trencin', kind='predaj', type='Rodinný dom',
   title='Dom s dvoma bytmi, Inovecká ulica, Trenčín', short='Dom s dvoma bytmi',
   locality='Trenčín', address='Inovecká ulica, Trenčín',
   lead='Tehlový dom na rohovom pozemku 600 m² s dvoma samostatnými 3-izbovými bytmi – pre dve generácie, bývanie s prenájmom alebo spojenie bývania a podnikania.',
   photos=list(range(2, 23)), plans=[], viz=[0, 1], home=False, order=6,
   price='359 990 €', price_note='', price_includes='',
   params=dict(rooms='6 (2 × 3 izby)', area_usable='180 m²', area_built='114 m²', area_plot='600 m² (rohový)', condition='Udržiavaný, čiastočne prerobený',
               building='Tehla', year='cca 1965 – 1970', utilities='Elektrina, mestský vodovod, kanalizácia, plyn', heating='Plynové',
               parking='Garáž 30 m² so vstupom z ulice', ownership='Osobné', extras='Podpivničenie 60 m², balkón 9 m², záhrada s ovocnými stromami'),
   viz_note='AI vizualizácie sú ilustračné, červená čiara znázorňuje orientačné hranice pozemku.',
   cut=['Cena nehnuteľnosti: 359990', 'Pre viac informácií a dohodnutie']),
 '2893': dict(slug='4-izbovy-byt-trencianske-teplice', kind='predaj', type='Byt',
   title='4-izbový byt 87 m², Trenčianske Teplice', short='4-izbový byt 87 m²',
   locality='Trenčianske Teplice', address='Ulica SNP, Trenčianske Teplice',
   lead='Priestranný byt v pôvodnom stave v zateplenom dome v kúpeľnom meste – ideálny, ak si chcete nový domov vytvoriť od základov podľa seba.',
   photos=[0, 2, 3, 4, 5, 6], plans=[1], viz=[], home=False, order=7,
   price='149 990 €', price_note='Ponúknite cenu – po obhliadke rada prediskutujem vašu cenovú ponuku.', price_includes='',
   params=dict(rooms='4', area_usable='87 m²', floor='1. poschodie (bez výťahu)', condition='Pôvodný stav', building='Panel, zateplený dom',
               heating='Centrálne', ownership='Osobné', extras='Balkón 5 m², pivnica 6 m²'),
   cut=['Pri kontaktovaní emailom']),
 '2943': dict(slug='prenajom-2-izbovy-byt-trencin', kind='prenajom', type='Byt',
   title='2-izbový byt na prenájom, Trenčín – Dolný Šianec', short='2-izbový byt na prenájom',
   locality='Trenčín – Dolný Šianec', address='Dolný Šianec, Trenčín',
   lead='Štýlový, kompletne zariadený byt s lodžiou a vlastným miestom v podzemnej garáži, 10 minút pešo od centra Trenčína. Voľný od 1. 10. 2026.',
   photos=list(range(9)), plans=[], viz=[], home=True, order=8,
   price='595 € / mesiac', price_note='Vratná kaucia 1 190 € (2 nájmy). Províziu 450 € hradí nájomca.',
   price_includes='Nájom zahŕňa parkovacie miesto v podzemnej garáži.',
   params=dict(rooms='2', area_usable='58 m²', floor='1. poschodie z 2, výťah', condition='Po rekonštrukcii, kompletne zariadený',
               building='Polyfunkčný dom (2009)', heating='Vlastný plynový kotol', parking='Miesto v podzemnej garáži (v cene)',
               extras='Lodžia 3 m², špajza, práčka', available='Od 1. 10. 2026', costs=''),
   cut=['Ďalšie informácie Vám poskytneme']),
}

FIX = {
 '2964': [('RODINNÝ DOM S VEĽKOU ZÁHRADOU A PRIESTOROM PRE VAŠE PLÁNY – PREJTA, POZEMOK 1 050 m²', ''),
          ('VAŠE REALITY ponúkajú na predaj', 'Ponúkam na predaj'), ('80 tých  rokoch', '80. rokoch'), ('80 tých rokoch', '80. rokoch'),
          ('kolaudovaný  v', 'kolaudovaný v'), ('časť  Prejta', 'časť Prejta'), ('118 m2)', '118 m²).'), ('80 m². (zastavaná', '80 m² (zastavaná')],
 '2791': [('Rodinný dom, ktorý si zamilujete na prvý pohľad – Mikušovce\n', ''),
          ('VAŠE REALITY – realitná kancelária Vám v exkluzívnom zastúpení ponúka na predaj', 'V exkluzívnom zastúpení ponúkam na predaj'),
          ('Prečo práve tento dom?', 'PREČO PRÁVE TENTO DOM')],
 '2941': [('Útulný dom pre pokojné bývanie bez starostí\n', '')],
 '2954': [('Vaše reality ponúka na predaj', 'Ponúkam na predaj')],
 '2905': [('Bývanie, podnikanie aj investícia na jednom mieste\n', ''), ('Realitná kancelária VAŠE REALITY ponúka', 'Ponúkam')],
 '2893': [('Vaše Reality ponúkajú na predaj', 'Ponúkam na predaj'), ('CENA – ALEBO PONÚKNITE NÁM SVOJU PREDSTAVU', 'CENA – ALEBO PONÚKNITE SVOJU PREDSTAVU'),
          ('Pri tejto nehnuteľnosti sme sa rozhodli', 'Pri tejto nehnuteľnosti som sa rozhodla'), ('Radi dáme priestor', 'Rada dám priestor')],
 '2943': [('nájmov(1190 EUR) Províziu za sprostredkovanie vo výške 450 eur', 'nájmov (1 190 €). Províziu za sprostredkovanie vo výške 450 €'), ('VAŠE REALITY v zastúpení majiteľa nehnuteľnosti ponúkajú', 'V zastúpení majiteľa ponúkam')],
}
TECH_2791 = ('Technické informácie\n', 'Domov, kde si každé ráno')

DROP_LINE = re.compile(r'^(ID\s*:|Kontakt:?$|Mária F[uü]rsten|tel\.:|e-mail:|Tím VAŠE REALITY|Člen Realitnej|Na skoré stretnutie|Pri kontaktovaní|Cena:\s*359990)', re.I)

def clean_text(s):
    s = html.unescape(s).replace('\xa0', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    return s

def to_html(desc, cut, lid=''):
    t = clean_text(desc)
    for a, b in FIX.get(lid, []): t = t.replace(a, b)
    if lid == '2791':   # unbulleted technical list -> bullets
        i, j = t.find(TECH_2791[0]), t.find(TECH_2791[1])
        if 0 < i < j:
            seg = t[i + len(TECH_2791[0]):j]
            seg = '\n'.join('* ' + l.strip() for l in seg.split('\n') if l.strip())
            t = t[:i] + 'TECHNICKÉ INFORMÁCIE\n' + seg + '\n\n' + t[j:]
    for c in cut:
        i = t.find(c)
        if i > 0: t = t[:i]
    blocks = [b.strip() for b in re.split(r'\n\s*\n', t) if b.strip()]
    out = []
    def is_head(l):
        if l.startswith(('*', '-', '•')): return False
        letters = re.sub(r'[^A-Za-zÀ-ž]', '', l)
        up = sum(1 for ch in letters if ch.isupper())
        if len(l) < 95 and len(letters) > 3 and up / len(letters) > 0.9: return True
        if len(l) < 40 and l.endswith(':') and len(l.split()) <= 3: return True
        return len(l) < 34 and l[0].isupper() and not re.search(r'[.,!?;:–]$', l) and len(l.split()) <= 3 and not re.search(r'\d', l)
    def fmt_head(l):
        l = l.rstrip(':').strip()
        letters = re.sub(r'[^A-Za-zÀ-ž]', '', l)
        if letters and sum(ch.isupper() for ch in letters) / len(letters) > 0.9:
            l = l[0] + l[1:].lower()
            for w in ('Orion', 'Prejta', 'Trenčianskych Teplíc', 'Dubnice', 'Trenčín', 'Wc'):
                l = re.sub(w, w if w != 'Wc' else 'WC', l, flags=re.I)
        return l
    for b in blocks:
        lines = [l.strip() for l in b.split('\n') if l.strip() and not DROP_LINE.match(l.strip())]
        i = 0
        while i < len(lines):
            l = lines[i]
            if re.match(r'^[*\-•]\s*', l):
                items = []
                while i < len(lines) and re.match(r'^[*\-•]\s*', lines[i]):
                    items.append(re.sub(r'^[*\-•]\s*', '', lines[i]).rstrip(',;')); i += 1
                out.append('<ul>' + ''.join(f'<li>{html.escape(x)}</li>' for x in items) + '</ul>'); continue
            # "X:" followed by short comma lines -> list
            if l.endswith(':') and i + 2 < len(lines) + 1:
                j = i + 1; items = []
                while j < len(lines) and len(lines[j]) < 160 and (lines[j].endswith((',', '.')) or j == len(lines) - 1) and not lines[j].endswith(':') and len(items) < 20:
                    if lines[j].endswith('.') and items: items.append(re.sub(r'^[*\-•]\s*', '', lines[j]).rstrip('.')); j += 1; break
                    if lines[j].endswith('.') and not items: break
                    items.append(re.sub(r'^[*\-•]\s*', '', lines[j]).rstrip(',')); j += 1
                if len(items) >= 2:
                    out.append(f'<p>{html.escape(l)}</p><ul>' + ''.join(f'<li>{html.escape(x)}</li>' for x in items) + '</ul>'); i = j; continue
            if is_head(l):
                out.append(f'<h3>{html.escape(fmt_head(l))}</h3>'); i += 1; continue
            out.append(f'<p>{html.escape(l)}</p>'); i += 1
    body = ''.join(out)
    body = body.replace('Realitná kancelária Vaše reality ponúka', 'Ponúkam').replace('Vaše Reality ponúkajú', 'Ponúkam')
    return body

def process_images(lid, slug, idxs):
    src = os.path.join(RAW, 'img', lid)
    files = sorted(os.listdir(src))
    dst = os.path.join(ROOT, 'img', 'nem', slug); os.makedirs(dst, exist_ok=True)
    out = []
    for k in idxs:
        f = files[k]
        im = ImageOps.exif_transpose(Image.open(os.path.join(src, f))).convert('RGB')
        name = f'{k:02d}'
        big = im.copy(); big.thumbnail((2000, 2000), Image.LANCZOS); big.save(os.path.join(dst, name + '.webp'), 'WEBP', quality=80, method=6)
        sm = im.copy(); sm.thumbnail((900, 900), Image.LANCZOS); sm.save(os.path.join(dst, name + '-m.webp'), 'WEBP', quality=76, method=6)
        out.append(f'img/nem/{slug}/{name}.webp')
    return out

def main():
    data = {o['id']: o for o in json.load(open(os.path.join(RAW, 'scraped.json')))}
    listings = []
    for lid, c in sorted(CFG.items(), key=lambda kv: kv[1]['order']):
        o = data[lid]
        x = {
            'id': c['slug'], 'slug': c['slug'], 'ref': lid, 'title': c['title'], 'short': c['short'],
            'kind': c['kind'], 'type': c['type'], 'status': 'aktualne',
            'locality': c['locality'], 'address': c['address'],
            'price': c['price'], 'price_note': c['price_note'], 'price_includes': c['price_includes'],
            'params': c['params'], 'facts': [],
            'lead': c['lead'], 'body': to_html(o['description'], c['cut'], lid),
            'photos': process_images(lid, c['slug'], c['photos']),
            'plans': process_images(lid, c['slug'], c['plans']),
            'viz': process_images(lid, c['slug'], c['viz']),
            'viz_note': c.get('viz_note', ''),
            'video': '', 'tour': '',
            'geo': [o['geo'].get('latitude'), o['geo'].get('longitude')] if o.get('geo') else [],
            'source': o['url'], 'home': c['home'], 'hidden': False, 'seo_desc': '',
            'updated': '2026-09-30T12:00:00Z',
        }
        listings.append(x)
        print(lid, x['slug'], len(x['photos']), len(x['plans']), len(x['viz']))
    os.makedirs(os.path.join(ROOT, '_data'), exist_ok=True)
    json.dump(listings, open(os.path.join(ROOT, '_data', 'listings.json'), 'w'), ensure_ascii=False, indent=1)

if __name__ == '__main__':
    main()
