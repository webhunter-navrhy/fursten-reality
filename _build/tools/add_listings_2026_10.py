#!/usr/bin/env python3
"""Doplnenie 6 ponúk z 2. strany profilu M. Fürsten na Vaše reality (2. 10. 2026).
Rovnaký postup ako import_listings.py, ale existujúce (ručne upravené) ponuky v _data/listings.json NEPREPISUJE –
len pridá chýbajúce ID na koniec. Spustenie: python3 _build/tools/add_listings_2026_10.py"""
import json, os, re, sys
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import import_listings as IL   # to_html, FIX, DROP_LINE, cesty

ROOT, RAW = IL.ROOT, IL.RAW

# položky bez odrážok v zdroji -> zoznam
def bullets(*items): return [(f'\n{s}\n', f'\n* {s}\n') for s in items]

CFG = {
 '2969': dict(slug='prenajom-3-izbovy-byt-dubnica-centrum', kind='prenajom', type='Byt', status='aktualne',
   title='3-izbový byt 80 m² na prenájom, Dubnica nad Váhom – Centrum I', short='3-izbový byt na prenájom',
   locality='Dubnica nad Váhom – Centrum I', address='Centrum I, Dubnica nad Váhom',
   lead='Priestranný, zrekonštruovaný a kompletne zariadený byt s dvoma balkónmi v centre Dubnice nad Váhom, pri OC ABC. Na dlhodobý prenájom, voľný od 15. 12. 2026.',
   photos=[0, 1, 4, 5, 2, 3, 6, 7, 8, 9], plans=[], viz=[],
   price='700 € / mesiac', price_note='Vratná kaucia 1 400 €. Pri podpise nájomnej zmluvy sa uhrádza nájomné a kaucia.', price_includes='',
   params=dict(rooms='3', area_usable='80 m²', floor='5. poschodie, výťah', condition='Po rekonštrukcii, kompletne zariadený',
               building='Panelový bytový dom', extras='2 balkóny (východ a západ), pivnica, miestnosť na bicykle', available='Od 15. 12. 2026'),
   cut=['KONTAKT']),
 '2631': dict(slug='dom-pozemok-937-m2-hlohovec-sulekovo', kind='predaj', type='Rodinný dom', status='aktualne',
   title='Starší dom na pozemku 937 m², Hlohovec – Šulekovo', short='Dom na pozemku 937 m²',
   locality='Hlohovec – Šulekovo', address='Šulekovo, Hlohovec',
   lead='Rovinatý pozemok 937 m² v obľúbenej časti Hlohovca so starším 4-izbovým domom a všetkými sieťami – na rekonštrukciu alebo na stavbu nového domu podľa Vašich predstáv.',
   photos=[8, 12, 1, 3, 5, 7, 4, 10, 13, 2, 11], plans=[], viz=[(0, (625, 168, 1522, 500))],
   price='98 500 €', price_note='', price_includes='',
   params=dict(rooms='4', area_usable='120 m²', area_plot='937 m² (cca 16 × 64 m)', condition='Pôvodný stav – na rekonštrukciu alebo zbúranie',
               building='Pálená tehla, škridlová strecha', utilities='Voda, elektrina, plyn, kanalizácia', heating='Ústredné',
               parking='Samostatne stojaca garáž 15 m²', ownership='Osobné', extras='Sklad 25 m²; regulačný blok BV – max. index zastavania 35 %'),
   viz_note='Vizualizácia je ilustračná – ukazuje jednu z možností, ako by mohla vyzerať novostavba na pozemku.',
   cut=['Pri kontaktovaní emailom']),
 '2559': dict(slug='chalupa-cavoj-krpelance', kind='predaj', type='Chata / chalupa', status='aktualne',
   title='Chalupa na lazoch pod lesom, Čavoj – Krpelance', short='Chalupa na lazoch pod lesom',
   locality='Čavoj – Krpelance (okres Prievidza)', address='Čavoj, osada Krpelance',
   lead='Murovaná chalupa s tromi podlažiami v pokojnej osade Krpelance – pod lesom, s panoramatickým výhľadom a kachľami. Na víkendy aj dlhšie pobyty v prírode.',
   photos=[1, 0, 9, 8, 10, 2, 3, 4, 5, 6, 7], plans=[], viz=[],
   price='55 500 €', price_note='', price_includes='',
   params=dict(rooms='5', area_usable='100 m²', area_plot='552 m² + ½ spoločného dvora (480 m²), svahovitý', condition='Čiastočne prerobená',
               building='Murovaná', year='2006', utilities='Elektrina, vodovod, septik', heating='Krbové kachle, tradičné kachle',
               ownership='Osobné', extras='Balkóny, vonkajší balkónový chodník, pivnica'),
   geo=[],   # súradnice na portáli ukazujú mimo obce -> mapa podľa adresy
   cut=['Cena: 55 500']),
 '2562': dict(slug='rekreacny-pozemok-zubak', kind='predaj', type='Pozemok', status='aktualne',
   title='Rekreačný pozemok 3 611 m², Zubák', short='Rekreačný pozemok 3 611 m²',
   locality='Zubák (okres Púchov)', address='Zubák, okres Púchov',
   lead='Veľký pozemok určený na výstavbu rekreačných chát v pokojnej časti obce Zubák – so vstupom priamo z obecnej cesty, prírodou okolo a hradom Lednica na dosah.',
   photos=[0, 1, 2], plans=[(3, (0, 98, 564, 1080))], viz=[],
   price='54 000 €', price_note='O kúpe menšej časti pozemku sa dá dohodnúť.', price_includes='',
   params=dict(area_plot='3 611 m² (cca 97 × 41 m)', utilities='Elektrina cca 20 m od pozemku, voda z vlastnej studne (bez plynu a kanalizácie)',
               parking='Vstup priamo zo spevnenej obecnej cesty', ownership='Osobné', extras='Určený na výstavbu rekreačných chát'),
   cut=['V prípade záujmu poskytujeme']),
 '2689': dict(slug='pozemok-lednicke-rovne-medne', kind='predaj', type='Pozemok', status='aktualne',
   title='Pozemok 2 330 m² na dom alebo chatu, Lednické Rovne – Medné', short='Pozemok 2 330 m²',
   locality='Lednické Rovne – Medné', address='Medné, Lednické Rovne',
   lead='Pozemok na výstavbu rodinného domu alebo rekreačnej chaty v pokojnej časti Medné – v prírode, a predsa 10 km od Púchova a s kompletnou vybavenosťou v Lednických Rovniach. Obrázok je ilustračný.',
   photos=[], plans=[], viz=[(0, (0, 236, 955, 620))],
   price='46 € / m²', price_note='Pri výmere 2 330 m² je celková cena 107 180 €.', price_includes='',
   params=dict(area_plot='2 330 m² (rovina)', utilities='Možnosť pripojenia na elektrinu v blízkosti pozemku', ownership='Osobné',
               extras='Na výstavbu rodinného domu alebo rekreačnej chaty'),
   viz_note='Obrázok je ilustračná vizualizácia.', note='Obrázok v inzeráte je ilustračná vizualizácia, nie fotografia pozemku.',
   cut=['V prípade záujmu cena']),
 '2680': dict(slug='chatka-so-zahradou-trencianske-teplice', kind='predaj', type='Chata / chalupa', status='rezervovane',
   title='Záhradná chatka s pozemkom 758 m², Trenčianske Teplice', short='Chatka so záhradou',
   locality='Trenčianske Teplice', address='Trenčianske Teplice',
   lead='Drevená chatka na murovaných základoch s pozemkom 758 m², ovocnými stromami a výhľadom na okolitú krajinu – len pár minút od centra kúpeľného mesta.',
   photos=[7, 8, 0, 1, 5, 2, 3, 4, 6], plans=[], viz=[],
   price='37 000 €', price_note='', price_includes='',
   params=dict(area_usable='42 m²', area_plot='758 m² (svahovitý)', condition='Pôvodný stav, využitie jar – jeseň',
               building='Drevená stavba na murovaných základoch', utilities='Elektrina (voda – možnosť studne)',
               parking='Príjazd autom až k pozemku (nová asfaltová cesta)', ownership='Osobné', extras='Balkón, pivnica 10 m², ovocné stromy'),
   cut=['CENA : 37 000', 'CENA: 37 000']),
}

FIX = {
 '2559': [('EXKLUZÍVNE | Chalupa na lazoch s nádhernými výhľadmi pod lesom – Čavoj, osada Krpelance.\n', ''),
          ('VAŠE REALITY s.r.o. Vám v exkluzívnom zastúpení ponúka na predaj', 'V exkluzívnom zastúpení ponúkam na predaj'),
          ('1. nadzemné podlažie', 'Prvé nadzemné podlažie'), ('pri chalube', 'pri chalupe'), ('480 m²,spojený', '480 m², spojený'),
          ('Miesto, ktoré si zamilujete', 'MIESTO, KTORÉ SI ZAMILUJETE'), ('odporúčame vozidlo', 'odporúčam vozidlo'),
          ('Pozemok je svahovitý', '\nPozemok je svahovitý')]
         + bullets('vstupná chodba', 'kúpeľňa so sprchovacím kútom', 'samostatné WC so splachovaním', 'hosťovská kuchyňa', 'spálňa',
                   'priestranná obývacia miestnosť', 'krbové kachle vykurujúce aj podkrovie', 'kuchynský kút s tečúcou vodou', 'elektrický varič',
                   'tradičné kachle vhodné na kúrenie, varenie aj pečenie', 'tri miestnosti', 'jedna priechodná izba', 'jedna dokončená izba',
                   'jedna miestnosť využívaná ako sklad, pripravená na dokončenie podľa vlastných predstáv',
                   'pozemok pri chalupe: 552 m²', 'spoluvlastnícky podiel na spoločnom dvore: 1/2 z výmery 480 m², spojený dvojitou stenou so zrkadlovo otočenou susednou chalupou.', 'lyžiarske stredisko Homôlka', 'turistické a cyklistické trasy Strážovských vrchov',
                   'obec Valaská Belá', 'kúpeľné a historické mesto Bojnice'),
 '2562': [('EXKLUZÍVNA PONUKA - VAŠE REALITY - realitná kancelária Vám ponúka na predaj pozemok s výmerou 3611m2, určený', 'Ponúkam na predaj pozemok s výmerou 3 611 m² určený'),
          ('Rozmer pozemku 97 m dlžka a 41 m šírka.', 'Rozmery pozemku: dĺžka 97 m, šírka 41 m.'), ('maximálny kľud', 'maximálny pokoj'),
          ('na dedine .', 'na dedine.'),
          ('IS elektrika v blízkosti pozemku, voda vlastná studňou, plyn nie, kanalizácia nie, cesta obecná spevnená.',
           'Elektrina je v blízkosti pozemku, voda z vlastnej studne, plyn ani kanalizácia nie sú.'),
          (' Vstup na pozemok priamo z obecnej cesty.', ' Na pozemok sa vstupuje priamo zo spevnenej obecnej cesty.'), ('Lednické Rovné', 'Lednické Rovne'),
          ('hrad Lednica krásne prostredie.', 'hrad Lednica a krásne prostredie.'), ('lekár , kostol', 'lekár, kostol'),
          ('V prípade záujmu o bližšie informácie technického charakteru Vám poskytneme priamo v RK.', 'Bližšie technické informácie Vám rada poskytnem.')],
 '2631': [('STAVEBNÝ POZEMOK 937 m² – HLOHOVEC, ŠULEKOVO\n', ''), ('ZBÚRAJTE STARÉ. POSTAVTE SI NOVÉ.', 'ZBÚRAJTE STARÉ, POSTAVTE SI NOVÉ'),
          ('VAŠE REALITY ponúkajú na predaj', 'Ponúkam na predaj'), ('Cena nehnuteľnosti: 98 500 €.\n', '')],
 '2680': [('VAŠE REALITY - realitná kancelária .\nPredáva v exkluzívnom zastúpení majiteľa záhradnú chatku s pozemkom 758m2, v krásnom prostredí mesta Trenčianske Teplice,\nktorá',
           'V exkluzívnom zastúpení majiteľa predávam záhradnú chatku s pozemkom 758 m² v krásnom prostredí mesta Trenčianske Teplice, ktorá'),
          ('Je vhodný na : výstavbu chaty , umiestnenie mobilného domu.', 'Je vhodný na výstavbu chaty alebo umiestnenie mobilného domu.'),
          ('obytnou miestnosťou , podpivničená .', 'obytnou miestnosťou, podpivničená.'),
          ('Stavba sa dá sa využívať jar - jeseň.', 'Stavbu je možné využívať od jari do jesene.'),
          ('V chatke je zavedená elektrina .Voda môže byť riiešená studňou,susedia maju studňu.', 'V chatke je zavedená elektrina. Vodu je možné riešiť studňou – susedia studňu majú.'),
          ('Rozmery pozemku : šírka: 21 m (vstupná časť) – postupne sa rozširuje až na 26m dĺžka : 46 m a 27 m rozloha : 758 m2 Výborná',
           'Rozmery pozemku: šírka 21 m (vstupná časť), postupne sa rozširuje až na 26 m; dĺžka 46 m a 27 m; rozloha 758 m².\n\nVýborná')],
 '2689': [('EXKLUZÍVNA PONUKA - VAŠE REALITY - realitná kancelária Vám v exkluzívnom zastúpení ponúka na predaj pozemok s výmerou 2330 m2, určený na výstavbu rodinného domu alebo rekreačnej chaty.',
           'V exkluzívnom zastúpení ponúkam na predaj pozemok s výmerou 2 330 m² určený na výstavbu rodinného domu alebo rekreačnej chaty.'),
          ('maximálny kľud', 'maximálny pokoj'),
          ('Od obce Lednické Rovné v rozsahu približne 10 km sa nachádza okresné mesto Púchov, v obci Lednické Rovné je', 'Približne 10 km od obce Lednické Rovne sa nachádza okresné mesto Púchov. V obci Lednické Rovne je'),
          ('Pizzeria', 'pizzeria'), ('Lednické Rovne - Medné', 'Lednické Rovne – Medné'), ('autobusová stanica. .', 'autobusová stanica.')],
 '2969': [('Ponúkame na dlhodobý prenájom', 'Ponúkam na dlhodobý prenájom'), ('Voľný od 15.12.2026.', 'Voľný od 15. 12. 2026.'), ('bicyklov.\n', 'bicyklov\n'), ('dvoch balkónov.\n', 'dvoch balkónov\n')],
}

PRON = re.compile(r'(?<![\wÀ-ž])(vy|vás|vám|váš|vaš[a-zá-ž]*|vami)(?![\wÀ-ž])')
def vykanie(s): return PRON.sub(lambda m: m.group(0)[0].upper() + m.group(0)[1:], s)

def images(lid, slug, items, prefix=''):
    """items: index alebo (index, (x0, y0, x1, y1)) – orez (napr. vizualizácia z plagátu bez loga a kontaktov)"""
    src = os.path.join(RAW, 'img', lid); files = sorted(os.listdir(src))
    dst = os.path.join(ROOT, 'img', 'nem', slug); os.makedirs(dst, exist_ok=True)
    out = []
    for it in items:
        k, box = (it if isinstance(it, tuple) else (it, None))
        im = ImageOps.exif_transpose(Image.open(os.path.join(src, files[k]))).convert('RGB')
        if box: im = im.crop(box)
        name = f'{prefix}{k:02d}'
        big = im.copy(); big.thumbnail((2000, 2000), Image.LANCZOS); big.save(os.path.join(dst, name + '.webp'), 'WEBP', quality=80, method=6)
        sm = im.copy(); sm.thumbnail((900, 900), Image.LANCZOS); sm.save(os.path.join(dst, name + '-m.webp'), 'WEBP', quality=76, method=6)
        out.append(f'img/nem/{slug}/{name}.webp')
    return out

def main():
    data = {o['id']: o for o in json.load(open(os.path.join(RAW, 'scraped.json'), encoding='utf-8'))}
    path = os.path.join(ROOT, '_data', 'listings.json')
    listings = json.load(open(path, encoding='utf-8'))
    have = {str(x.get('ref')) for x in listings}
    IL.FIX.update(FIX)
    added = 0
    for lid, c in CFG.items():
        if lid in have: print('preskakujem (už je na webe)', lid); continue
        o = data[lid]
        body = IL.to_html(o['description'], c['cut'], lid)
        if c.get('note'): body += f'<p><em>{c["note"]}</em></p>'
        body = body.replace('<h3>Byt pozostáva z</h3>', '<p>Byt pozostáva z:</p>')
        x = {
            'id': c['slug'], 'slug': c['slug'], 'ref': lid, 'title': c['title'], 'short': c['short'],
            'kind': c['kind'], 'type': c['type'], 'status': c['status'],
            'locality': c['locality'], 'address': c['address'],
            'price': c['price'], 'price_note': c['price_note'], 'price_includes': c['price_includes'],
            'params': c['params'], 'facts': [],
            'lead': c['lead'], 'body': vykanie(body),
            'photos': images(lid, c['slug'], c['photos']),
            'plans': images(lid, c['slug'], c['plans'], 'p'),
            'viz': images(lid, c['slug'], c['viz'], 'v'),
            'viz_note': c.get('viz_note', ''),
            'video': '', 'tour': '',
            'geo': c['geo'] if 'geo' in c else ([o['geo'].get('latitude'), o['geo'].get('longitude')] if o.get('geo') else []),
            'source': o['url'], 'home': False, 'hidden': False, 'seo_desc': '',
            'updated': '2026-10-02T12:00:00Z',
        }
        listings.append(x); added += 1
        print(lid, x['slug'], len(x['photos']), len(x['plans']), len(x['viz']))
    open(path, 'w', encoding='utf-8').write(json.dumps(listings, ensure_ascii=False, indent=1) + '\n')
    print('pridané:', added, '· spolu:', len(listings))

if __name__ == '__main__':
    main()
