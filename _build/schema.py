"""Obsahová schéma pre administráciu — každý upraviteľný text a obrázok webu Fürsten Reality.

Stránka -> sekcie -> polia:
  F(key, label, kind, default, hint)          kinds: text | md | textarea | image | url | bool
  L(key, label, item_fields, default, title)  opakovateľný zoznam (item_fields = [(name, label, kind)])
md:        *zvýraznenie zlatou farbou*, **tučné**, nový riadok = zalomenie
textarea:  odseky oddelené prázdnym riadkom
Hodnota „[DOPLNIŤ …]“ = údaj, ktorý treba doplniť pred spustením (admin ho zvýrazní v prehľade).
"""

def F(key, label, kind='text', default='', hint='', todo=False):
    return {'key': key, 'label': label, 'kind': kind, 'default': default, 'hint': hint, 'todo': todo}

def L(key, label, fields, default, title='title', hint=''):
    return {'key': key, 'label': label, 'kind': 'list', 'fields': [{'name': n, 'label': l, 'kind': k} for n, l, k in fields],
            'default': default, 'title': title, 'hint': hint}

MD = 'Slovo v *hviezdičkách* sa zvýrazní zlatou farbou, **dve hviezdičky** = tučne.'
H1 = 'Nový riadok nadpisu = Enter. Slovo v *hviezdičkách* sa zvýrazní.'
TODO = 'Doplniť pred spustením webu.'

GDPR = """Tieto informácie vysvetľujú, ako spracúvam osobné údaje, ktoré mi zveríte cez formuláre na tomto webe, telefonicky alebo e-mailom.

## Prevádzkovateľ
Mária Fürsten – Fürsten Reality
Centrum II 92/54-15, 018 41 Dubnica nad Váhom
IČO: 40380505 · IČ DPH: SK1020072713
Fyzická osoba – podnikateľka zapísaná v živnostenskom registri
E-mail: fursten@vasereality.sk · telefón: +421 904 808 521

## Aké údaje spracúvam a prečo
Meno, telefón, e-mail a obsah Vašej správy (napríklad typ a lokalitu nehnuteľnosti alebo to, čo hľadáte). Údaje používam výlučne na to, aby som Vás mohla kontaktovať, odpovedať na Vašu otázku, dohodnúť obhliadku alebo pripraviť ponuku spolupráce.

## Právny základ
Spracúvanie je nevyhnutné na vykonanie opatrení pred uzavretím zmluvy na Vašu žiadosť (čl. 6 ods. 1 písm. b) GDPR), prípadne ide o môj oprávnený záujem odpovedať na Vašu správu (čl. 6 ods. 1 písm. f) GDPR).

## Ako dlho údaje uchovávam
Kým vybavujeme Vašu požiadavku, najdlhšie však 3 roky od posledného kontaktu. Ak spolu uzavrieme zmluvu, údaje uchovávam po dobu stanovenú právnymi predpismi.

## Komu údaje poskytujem
Údaje nepredávam. Pri spolupráci na konkrétnom obchode ich môžem poskytnúť realitnej kancelárii VAŠE REALITY s.r.o., s ktorou spolupracujem, a to len v nevyhnutnom rozsahu. Technicky ich spracúvajú aj poskytovatelia webu a e-mailu (sprostredkovatelia): WebHunter s.r.o. a služba na doručovanie e-mailov z formulárov.

## Vaše práva
Máte právo na prístup k údajom, ich opravu, vymazanie, obmedzenie spracúvania, prenosnosť a právo namietať. Stačí napísať na fursten@vasereality.sk. Ak si myslíte, že s údajmi nezaobchádzam správne, môžete podať návrh na Úrad na ochranu osobných údajov SR, Hraničná 12, 820 07 Bratislava (dataprotection.gov.sk).

## Cookies
Tento web nepoužíva reklamné ani analytické cookies. Ukladá sa len technicky nevyhnutné nastavenie prehliadača.

Posledná aktualizácia: 30. 9. 2026"""

SCHEMA = [
 {'id': 'general', 'title': 'Kontakt a údaje', 'icon': 'contact', 'sections': [
  {'title': 'Kontaktné údaje', 'fields': [
    F('contact.name', 'Meno', default='Mária Fürsten'),
    F('contact.role', 'Pozícia', default='realitná maklérka'),
    F('contact.phone', 'Telefón', default='+421 904 808 521'),
    F('contact.email', 'E-mail', default='fursten@vasereality.sk'),
    F('contact.hours', 'Kedy sa mi môžete ozvať', default='Pondelok – piatok 8:00 – 18:00, po dohode aj cez víkend'),
    F('contact.languages', 'Jazyky', default='slovenčina · čeština · nemčina'),
    F('contact.region', 'Pôsobnosť (krátko)', default='Púchov · Považská Bystrica · Ilava · Dubnica nad Váhom · Trenčín a priľahlé obce'),
    F('contact.vr_url', 'Môj profil na Vaše reality', 'url', 'https://www.vasereality.sk/makler/10--maria-fursten'),
    F('contact.facebook', 'Facebook (nepovinné)', 'url', ''),
    F('contact.instagram', 'Instagram (nepovinné)', 'url', ''),
  ]},
  {'title': 'Fotografia', 'fields': [
    F('about.photo', 'Moja fotografia (portrét)', 'image', 'img/site/maria-fursten.webp', 'Na výšku (pomer 3 : 4), ideálne aspoň 1200 px. Zobrazí sa v sekcii O mne. Keď fotku odoberiete, web ukáže monogram.'),
    F('about.photo_small', 'Malá fotka – tvár (štvorec)', 'image', 'img/site/maria-fursten-tvar.webp', 'Výrez tváre na štvorec. Zobrazuje sa v malom krúžku (úvod, kontakt, detail nehnuteľnosti).'),
  ]},
  {'title': 'Logo', 'fields': [
    F('brand.own_logo', 'Použiť logo z Facebooku (s domčekom) namiesto písma „Fürsten“', 'bool', True, 'Zapnuté = Vaše logo s domčekom prekreslené do farieb webu (variant C, vybraný 2. 10. 2026). Vypnuté = písmové logo webu. Súbory loga sú aj v img/site/brand/.'),
  ]},
  {'title': 'Údaje o podnikaní a spustenie webu', 'fields': [
    F('legal.name', 'Obchodné meno', default='Mária Fürsten – Fürsten Reality'),
    F('legal.ico', 'IČO', default='40380505', todo=True),
    F('legal.vat', 'IČ DPH', default='SK1020072713'),
    F('legal.address', 'Miesto podnikania', default='Centrum II 92/54-15, 018 41 Dubnica nad Váhom', todo=True),
    F('legal.register', 'Zápis v registri', default='Fyzická osoba – podnikateľka zapísaná v živnostenskom registri'),
    F('launch.domain', 'Vlastná doména webu', 'url', '', 'Napr. https://www.fursten-reality.sk – vyplní správca webu po nasmerovaní domény. ' + TODO, todo=True),
    F('legal.coop', 'Spolupráca', 'textarea', 'Pôsobím pod vlastnou značkou Fürsten Reality ako samostatná maklérka (živnostníčka) a spolupracujem s realitnou kanceláriou VAŠE REALITY s.r.o.'),
    F('footer.text', 'Text v pätičke', 'textarea', 'Predaj, kúpa a prenájom nehnuteľností v Púchove, Považskej Bystrici, Ilave, Dubnici nad Váhom, Trenčíne a v priľahlých lokalitách. Osobne, zrozumiteľne a s rešpektom k Vášmu času.'),
  ]},
 ]},

 {'id': 'home', 'title': 'Úvodná stránka', 'icon': 'home', 'sections': [
  {'title': 'Vyhľadávače (SEO)', 'fields': [
    F('home.seo_title', 'Titulok stránky', default='Mária Fürsten – realitná maklérka | Púchov, Považská Bystrica, Ilava, Dubnica nad Váhom, Trenčín'),
    F('home.seo_desc', 'Popis pre Google', 'textarea', 'Predaj, kúpa a prenájom nehnuteľností v Púchove, Považskej Bystrici, Ilave, Dubnici nad Váhom, Trenčíne a v priľahlých obciach. Mária Fürsten – Fürsten Reality, v spolupráci s VAŠE REALITY.'),
  ]},
  {'title': 'Úvod (prvá obrazovka)', 'fields': [
    F('home.hero_label', 'Štítok nad nadpisom', default='Realitná maklérka · Púchov · Považská Bystrica · Ilava · Dubnica nad Váhom · Trenčín'),
    F('home.hero_title', 'Hlavný nadpis', 'md', 'Domov\nv dobrých *rukách*.', H1),
    F('home.hero_sub', 'Text pod nadpisom', 'md', 'Som **Mária Fürsten**. Pomôžem Vám predať nehnuteľnosť za férovú cenu alebo nájsť takú, ktorá bude naozaj Vaša – v Púchove, Považskej Bystrici, Ilave, Dubnici nad Váhom, Trenčíne a v priľahlých obciach.', MD),
    F('home.hero_image', 'Veľká fotka vpravo', 'image', 'img/nem/rodinny-dom-mikusovce/01.webp', 'Keď bude hotová Vaša fotografia, môžete ju dať sem (na výšku).'),
    F('home.hero_caption', 'Popisok fotky', default='Rodinný dom so záhradou · Mikušovce'),
    F('home.cta_sell', 'Tlačidlo 1 – nadpis', default='Chcem predať nehnuteľnosť'),
    F('home.cta_sell_sub', 'Tlačidlo 1 – popis', default='Ocenenie, príprava a predaj od A po Z'),
    F('home.cta_buy', 'Tlačidlo 2 – nadpis', default='Hľadám nehnuteľnosť'),
    F('home.cta_buy_sub', 'Tlačidlo 2 – popis', default='Povedzte mi, čo hľadáte, ozvem sa'),
  ]},
  {'title': 'Vybrané ponuky', 'fields': [
    F('home.offers_label', 'Štítok', default='Z mojej ponuky'),
    F('home.offers_title', 'Nadpis', 'md', 'Byty, domy aj domy *s potenciálom*', MD + ' Ktoré nehnuteľnosti sa tu ukážu, nastavíte pri nehnuteľnosti prepínačom „Na úvodnej stránke“.'),
    F('home.offers_lead', 'Text', 'md', 'Moderné bývanie v centre, rodinné domy so záhradou aj staršie domy, ktorým môžete dať nový život.'),
  ]},
  {'title': 'O mne', 'fields': [
    F('about.label', 'Štítok', default='O mne'),
    F('about.title', 'Nadpis', 'md', 'Dobrý deň,\nsom *Mária*.', H1),
    F('about.text', 'Text', 'textarea',
      'Pochádzam z okolia Púchova a momentálne žijem v Dubnici nad Váhom. Tento kraj nepoznám len z máp a realitných portálov – poznám ho z každodenného života. Viem, kde sa dobre býva, kde sa byty rýchlo predávajú a čo kupujúcich pri dome zaujíma ako prvé. A poznám aj ľudí, ktorí tu žijú.\n\n'
      'Púchov, Považská Bystrica, Ilava, Dubnica nad Váhom i Trenčín sú mi blízke. Na osobné stretnutie či obhliadku preto viem prísť rýchlo – do miest aj priľahlých obcí.\n\n'
      'Pri každej nehnuteľnosti ma zaujíma aj to, čo je za ňou: prečo predávate, kedy sa chcete sťahovať, čo pre Vás znamená dobrá cena. Až potom navrhnem postup realizácie. Na obhliadky chodím osobne a po každej Vám dám vedieť, ako prebehla.\n\n'
      'Pracujem pod vlastnou značkou **Mária Fürsten Reality** ako samostatná maklérka a spolupracujem s realitnou kanceláriou **VAŠE REALITY s.r.o.**\n\n'
      'Pri riešení financovania spolupracujem s finančným maklérom Ing. Máriom Janíkom, ktorý Vám poskytne finančné poradenstvo a pomôže s výberom hypotéky či iného vhodného úveru súvisiaceho s kúpou alebo predajom nehnuteľnosti.',
      'Text doplňte vlastnými slovami – čím osobnejšie, tým lepšie.'),
    F('about.signature', 'Podpis', default='Mária Fürsten'),
    L('about.facts', 'Krátke fakty', [('title', 'Názov', 'text'), ('text', 'Hodnota', 'text')], [
      {'title': 'Komunikujem', 'text': 'po slovensky, česky a nemecky.'}],
      hint='Len údaje, ktoré už nie sú v texte vyššie (mestá a spolupráca s VAŠE REALITY sú v texte).'),
  ]},
  {'title': 'Služby', 'fields': [
    F('services.label', 'Štítok', default='S čím pomôžem'),
    F('services.title', 'Nadpis', 'md', 'Jasne, *konkrétne* a bez drobného písma', MD),
    L('services.items', 'Služby', [('title', 'Názov', 'text'), ('text', 'Krátky popis', 'textarea'), ('points', 'Čo presne urobím (každý riadok = jeden bod)', 'textarea'), ('link', 'Odkaz', 'url')], [
      {'title': 'Predaj nehnuteľnosti', 'text': 'Byt, dom, pozemok aj starší dom na rekonštrukciu.',
       'points': 'Reálnu cenu podľa predajov v okolí, nie podľa prianí\nKontrolu listu vlastníctva a podkladov\nFotografie, popis a pri staršom dome vizualizácie po rekonštrukcii\nInzerciu na realitných portáloch a osobné obhliadky\nRezervačnú a kúpnu zmluvu a návrh na vklad do katastra\nOdovzdanie nehnuteľnosti a prepis energií',
       'link': 'predat.html'},
      {'title': 'Kúpa a hľadanie', 'text': 'Keď neviete, kde začať, alebo nemáte čas sledovať portály.',
       'points': 'Spolu si ujasníme lokalitu, rozpočet a dispozíciu\nPosielam Vám len ponuky, ktoré dávajú zmysel\nIdem s Vami na obhliadku a upozorním na riziká\nPreverím list vlastníctva, ťarchy a vecné bremená\nHypotéku vybavíte cez overených partnerov',
       'link': 'hladam.html'},
      {'title': 'Prenájom', 'text': 'Pre majiteľov, ktorí chcú spoľahlivého nájomcu bez starostí.',
       'points': 'Odporučím výšku nájmu a podmienky\nInzerciu a výber nájomcu\nNájomnú zmluvu a preberací protokol\nKauciu a odovzdanie bytu s kľúčmi',
       'link': 'kontakt.html'}]),
  ]},
  {'title': 'Priebeh spolupráce', 'fields': [
    F('process.label', 'Štítok', default='Ako spolupracujeme'),
    F('process.title', 'Nadpis', 'md', 'Šesť krokov od prvej kávy *po kľúče*', MD),
    F('process.lead', 'Text', 'md', 'Pri predaji viete vždy, v ktorom kroku sa nachádzame a čo nasleduje. Prvé stretnutie je nezáväzné.'),
    L('process.steps', 'Kroky', [('title', 'Názov kroku', 'text'), ('text', 'Popis', 'textarea')], [
      {'title': 'Stretnutie a obhliadka', 'text': 'Prídem sa na nehnuteľnosť pozrieť a vypočujem si Vaše plány, termíny a očakávania.'},
      {'title': 'Cena a plán', 'text': 'Podľa porovnateľných predajov v okolí navrhnem reálnu cenu a postup predaja. Dohodneme sa na podmienkach spolupráce.'},
      {'title': 'Podklady a prezentácia', 'text': 'Skontrolujem potrebné podklady a pripravím fotodokumentáciu, popis a podľa potreby pôdorysy či vizualizácie.'},
      {'title': 'Inzercia a obhliadky', 'text': 'Nehnuteľnosť zverejním na portáloch a obhliadky vediem osobne. Po každej obhliadke Vám dám spätnú väzbu.'},
      {'title': 'Zmluvy a bezpečný prevod', 'text': 'Rezervačná a kúpna zmluva, bezpečná úhrada kúpnej ceny a návrh na vklad do katastra – s právnym servisom.'},
      {'title': 'Odovzdanie', 'text': 'Odovzdanie kľúčov od nehnuteľnosti s preberacím protokolom, stavmi meračov a prepisom energií.'}]),
  ]},
  {'title': 'Referencie', 'fields': [
    F('reviews.label', 'Štítok', default='Referencie'),
    F('reviews.title', 'Nadpis', 'md', 'Čo hovoria *klienti*', MD + ' Sekcia sa na webe ukáže, až keď v časti Referencie pridáte aspoň jednu referenciu.'),
  ]},
  {'title': 'Kontakt (spodná časť)', 'fields': [
    F('contactsec.label', 'Štítok', default='Kontakt'),
    F('contactsec.title', 'Nadpis', 'md', 'Napíšte mi,\n*ozvem sa* Vám.', H1),
    F('contactsec.text', 'Text', 'md', 'Najrýchlejšie ma zastihnete telefonicky. Ak píšete, nechajte mi prosím aj telefónne číslo – zavolám Vám späť.'),
  ]},
 ]},

 {'id': 'listing', 'title': 'Ponuka a detail', 'icon': 'grid', 'sections': [
  {'title': 'Stránka Ponuka', 'fields': [
    F('offer.seo_title', 'Titulok stránky', default='Ponuka nehnuteľností – Púchov, Považská Bystrica, Ilava, Dubnica nad Váhom, Trenčín | Fürsten Reality'),
    F('offer.seo_desc', 'Popis pre Google', 'textarea', 'Aktuálna ponuka bytov a domov na predaj a prenájom v Púchove, Považskej Bystrici, Ilave, Dubnici nad Váhom, Trenčíne a v priľahlých obciach. Mária Fürsten – Fürsten Reality.'),
    F('offer.title', 'Nadpis', 'md', 'Aktuálna *ponuka*', H1),
    F('offer.lead', 'Text', 'md', 'Byty a domy na predaj a prenájom od Púchova cez Považskú Bystricu, Ilavu a Dubnicu nad Váhom až po Trenčín – vrátane priľahlých obcí. Na každú nehnuteľnosť Vás rada prevediem osobne.'),
    F('offer.sold_title', 'Nadpis sekcie predaných', 'md', 'Predané *a prenajaté*', MD),
    F('offer.empty', 'Text, keď filter nič nenájde', 'md', 'V tejto kategórii teraz nič nemám. Povedzte mi, čo hľadáte – ozvem sa, keď sa objaví vhodná ponuka.'),
  ]},
  {'title': 'Výzva „Neverejné ponuky“', 'fields': [
    F('offmarket.title', 'Nadpis', 'md', 'Nenašli ste? *Povedzte mi*, čo hľadáte.', MD),
    F('offmarket.text', 'Text', 'md', 'Niektorí majitelia nechcú predávať cez verejnú inzerciu. Keď mi poviete, čo hľadáte, ozvem sa, len čo sa objaví vhodná nehnuteľnosť – aj taká, ktorá sa na portáloch neukáže.'),
    F('offmarket.btn', 'Tlačidlo', default='Neverejné ponuky – napísať, čo hľadám'),
  ]},
  {'title': 'Detail nehnuteľnosti', 'fields': [
    F('detail.btn', 'Hlavné tlačidlo', default='Dohodnúť obhliadku'),
    F('detail.agent_sub', 'Text pod menom', default='Nehnuteľnosť Vám rada ukážem osobne'),
    F('detail.viz_note', 'Poznámka k vizualizáciám (ak pri nehnuteľnosti nie je vlastná)', default='Vizualizácie sú ilustračné – ukazujú možnú podobu po úprave, nie súčasný stav.'),
    F('detail.plan_missing', 'Text, keď chýba pôdorys', default='Pôdorys Vám rada pošlem na požiadanie.'),
    F('detail.price_default', 'Text o cene, ak nie je vyplnené „Čo cena zahŕňa“', default='Podrobnosti o cene a o tom, čo zahŕňa, Vám rada vysvetlím pri obhliadke.'),
    F('detail.form_title', 'Nadpis formulára', 'md', 'Dohodnime si *obhliadku*', MD),
  ]},
 ]},

 {'id': 'sell', 'title': 'Chcem predať', 'icon': 'key', 'sections': [
  {'title': 'Texty', 'fields': [
    F('sell.seo_title', 'Titulok stránky', default='Chcem predať nehnuteľnosť – Púchov, Považská Bystrica, Ilava, Dubnica nad Váhom, Trenčín | Fürsten Reality'),
    F('sell.seo_desc', 'Popis pre Google', 'textarea', 'Predávate byt, dom alebo pozemok v Púchove, Považskej Bystrici, Ilave, Dubnici nad Váhom, Trenčíne či v okolitých obciach? Napíšte mi pár údajov, ozvem sa a dohodneme nezáväzné stretnutie.'),
    F('sell.title', 'Nadpis', 'md', 'Chcem predať\n*nehnuteľnosť*', H1),
    F('sell.lead', 'Text', 'md', 'Stačí pár údajov. Ozvem sa Vám, prídem sa na nehnuteľnosť pozrieť a navrhnem reálnu cenu aj postup – nezáväzne.'),
    L('sell.points', 'Body vedľa formulára', [('title', 'Text', 'text')], [
      {'title': 'Reálna cena podľa predajov v okolí'}, {'title': 'Fotografie, popis a pri staršom dome vizualizácie'},
      {'title': 'Osobná obhliadka a moja spätná väzba'}, {'title': 'Zmluvy, právny servis a vklad do katastra nehnuteľností'}]),
    F('sell.thanks', 'Poďakovanie po odoslaní', 'md', 'Ďakujem, Vaša správa prišla. *Ozvem sa Vám* najneskôr nasledujúci pracovný deň.'),
  ]},
 ]},

 {'id': 'search', 'title': 'Hľadám nehnuteľnosť', 'icon': 'search', 'sections': [
  {'title': 'Texty', 'fields': [
    F('search.seo_title', 'Titulok stránky', default='Hľadám nehnuteľnosť – Púchov, Považská Bystrica, Ilava, Dubnica nad Váhom, Trenčín | Fürsten Reality'),
    F('search.seo_desc', 'Popis pre Google', 'textarea', 'Hľadáte byt alebo dom v Púchove, Považskej Bystrici, Ilave, Dubnici nad Váhom, Trenčíne alebo v okolitých obciach? Povedzte mi, čo hľadáte, a dám Vám vedieť, keď sa objaví vhodná ponuka.'),
    F('search.title', 'Nadpis', 'md', 'Hľadám\n*nehnuteľnosť*', H1),
    F('search.lead', 'Text', 'md', 'Napíšte mi, čo hľadáte – lokalitu, rozpočet a čo je pre Vás dôležité. Ozvem sa, keď sa objaví nehnuteľnosť, ktorá Vám bude sedieť, aj keď ešte nebude verejne inzerovaná.'),
    F('search.thanks', 'Poďakovanie po odoslaní', 'md', 'Ďakujem! Vaše požiadavky mám zapísané a *ozvem sa*, keď budem mať vhodnú ponuku.'),
  ]},
 ]},

 {'id': 'contactpage', 'title': 'Stránka Kontakt', 'icon': 'mail', 'sections': [
  {'title': 'Texty', 'fields': [
    F('contactpage.seo_title', 'Titulok stránky', default='Kontakt – Mária Fürsten, realitná maklérka | Púchov, Považská Bystrica, Ilava, Dubnica nad Váhom, Trenčín'),
    F('contactpage.title', 'Nadpis', 'md', 'Ozvite sa,\n*rada pomôžem*.', H1),
    F('contactpage.thanks', 'Poďakovanie po odoslaní', 'md', 'Ďakujem za správu. *Ozvem sa Vám* čo najskôr.'),
  ]},
 ]},

 {'id': 'privacy', 'title': 'Ochrana osobných údajov', 'icon': 'lock', 'sections': [
  {'title': 'Text stránky', 'fields': [
    F('privacy.body', 'Text', 'textarea', GDPR, 'Riadok začínajúci „## “ je nadpis. Ak niekam napíšete „[DOPLNIŤ …]“, na webe sa to zvýrazní ako chýbajúci údaj.', todo=True),
  ]},
 ]},
]

def defaults():
    out = {}
    for page in SCHEMA:
        for sec in page['sections']:
            for f in sec['fields']:
                out[f['key']] = f['default']
    return out
