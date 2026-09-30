"""Obsahová schéma pre administráciu — každý upraviteľný text a obrázok webu Fürsten Reality.

Stránka -> sekcie -> polia:
  F(key, label, kind, default, hint)          kinds: text | md | textarea | image | url | bool
  L(key, label, item_fields, default, title)  opakovateľný zoznam (item_fields = [(name, label, kind)])
md:        *kurzíva v zlatej*, **tučné**, nový riadok = zalomenie
textarea:  odseky oddelené prázdnym riadkom
Hodnota „[DOPLNIŤ …]“ = údaj, ktorý treba doplniť pred spustením (admin ho zvýrazní v prehľade).
"""

def F(key, label, kind='text', default='', hint='', todo=False):
    return {'key': key, 'label': label, 'kind': kind, 'default': default, 'hint': hint, 'todo': todo}

def L(key, label, fields, default, title='title', hint=''):
    return {'key': key, 'label': label, 'kind': 'list', 'fields': [{'name': n, 'label': l, 'kind': k} for n, l, k in fields],
            'default': default, 'title': title, 'hint': hint}

MD = 'Slovo v *hviezdičkách* sa zvýrazní zlatou kurzívou, **dve hviezdičky** = tučne.'
H1 = 'Nový riadok nadpisu = Enter. Slovo v *hviezdičkách* sa zvýrazní.'
TODO = 'Doplniť pred spustením webu.'

GDPR = """Tieto informácie vysvetľujú, ako spracúvam osobné údaje, ktoré mi zveríte cez formuláre na tomto webe, telefonicky alebo e-mailom.

## Prevádzkovateľ
Mária Fürsten – Fürsten Reality
[DOPLNIŤ: miesto podnikania]
IČO: [DOPLNIŤ: IČO]
E-mail: fursten@vasereality.sk · telefón: +421 904 808 521

## Aké údaje spracúvam a prečo
Meno, telefón, e-mail a obsah vašej správy (napríklad typ a lokalitu nehnuteľnosti alebo to, čo hľadáte). Údaje používam výlučne na to, aby som vás mohla kontaktovať, odpovedať na vašu otázku, dohodnúť obhliadku alebo pripraviť ponuku spolupráce.

## Právny základ
Spracúvanie je nevyhnutné na vykonanie opatrení pred uzavretím zmluvy na vašu žiadosť (čl. 6 ods. 1 písm. b) GDPR), prípadne ide o môj oprávnený záujem odpovedať na vašu správu (čl. 6 ods. 1 písm. f) GDPR).

## Ako dlho údaje uchovávam
Kým vybavujeme vašu požiadavku, najdlhšie však [DOPLNIŤ: napr. 2 roky] od posledného kontaktu. Ak spolu uzavrieme zmluvu, údaje uchovávam po dobu stanovenú právnymi predpismi.

## Komu údaje poskytujem
Údaje nepredávam. Pri spolupráci na konkrétnom obchode ich môžem poskytnúť realitnej kancelárii VAŠE REALITY s.r.o., s ktorou spolupracujem, a to len v nevyhnutnom rozsahu. Technicky ich spracúvajú aj poskytovatelia webu a e-mailu (sprostredkovatelia): WebHunter s.r.o. a služba na doručovanie e-mailov z formulárov.
[DOPLNIŤ: ďalší príjemcovia, ak nejakí sú]

## Vaše práva
Máte právo na prístup k údajom, ich opravu, vymazanie, obmedzenie spracúvania, prenosnosť a právo namietať. Stačí napísať na fursten@vasereality.sk. Ak si myslíte, že s údajmi nezaobchádzam správne, môžete podať návrh na Úrad na ochranu osobných údajov SR, Hraničná 12, 820 07 Bratislava (dataprotection.gov.sk).

## Cookies
Tento web nepoužíva reklamné ani analytické cookies. Ukladá sa len technicky nevyhnutné nastavenie prehliadača.

Posledná aktualizácia: [DOPLNIŤ: dátum]"""

SCHEMA = [
 {'id': 'general', 'title': 'Kontakt a údaje', 'icon': 'contact', 'sections': [
  {'title': 'Kontaktné údaje', 'fields': [
    F('contact.name', 'Meno', default='Mária Fürsten'),
    F('contact.role', 'Pozícia', default='realitná maklérka'),
    F('contact.phone', 'Telefón', default='+421 904 808 521'),
    F('contact.email', 'E-mail', default='fursten@vasereality.sk'),
    F('contact.hours', 'Kedy sa mi môžete ozvať', default='Pondelok – piatok 8:00 – 18:00, po dohode aj cez víkend'),
    F('contact.languages', 'Jazyky', default='slovenčina · čeština · nemčina'),
    F('contact.region', 'Pôsobnosť (krátko)', default='Dubnica nad Váhom · Ilava · Trenčín a okolie'),
    F('contact.vr_url', 'Môj profil na Vaše reality', 'url', 'https://www.vasereality.sk/makler/10--maria-fursten'),
    F('contact.facebook', 'Facebook (nepovinné)', 'url', ''),
    F('contact.instagram', 'Instagram (nepovinné)', 'url', ''),
  ]},
  {'title': 'Fotografia', 'fields': [
    F('about.photo', 'Moja fotografia (portrét)', 'image', '', 'Najlepšie výška aspoň 1600 px, na výšku. Kým tu nie je fotka, web ukazuje elegantný monogram.', todo=True),
  ]},
  {'title': 'Pred spustením – údaje o podnikaní', 'fields': [
    F('legal.name', 'Obchodné meno', default='Mária Fürsten – Fürsten Reality'),
    F('legal.ico', 'IČO', default='', hint=TODO, todo=True),
    F('legal.address', 'Miesto podnikania', default='', hint=TODO, todo=True),
    F('legal.register', 'Zápis v registri', default='', hint='Napr. „Zapísaná v živnostenskom registri Okresného úradu Ilava, č. …“. ' + TODO, todo=True),
    F('legal.coop', 'Spolupráca', 'textarea', 'Pôsobím pod vlastnou značkou Fürsten Reality ako samostatná maklérka (živnostníčka) a spolupracujem s realitnou kanceláriou VAŠE REALITY s.r.o.'),
    F('footer.text', 'Text v pätičke', 'textarea', 'Predaj, kúpa a prenájom nehnuteľností v Dubnici nad Váhom, Ilave, Trenčíne a okolí. Osobne, zrozumiteľne a s rešpektom k vášmu času.'),
  ]},
 ]},

 {'id': 'home', 'title': 'Úvodná stránka', 'icon': 'home', 'sections': [
  {'title': 'Vyhľadávače (SEO)', 'fields': [
    F('home.seo_title', 'Titulok stránky', default='Mária Fürsten – realitná maklérka | Dubnica nad Váhom, Ilava, Trenčín'),
    F('home.seo_desc', 'Popis pre Google', 'textarea', 'Predaj, kúpa a prenájom nehnuteľností v Dubnici nad Váhom, Ilave, Trenčíne a okolí. Mária Fürsten – Fürsten Reality, v spolupráci s VAŠE REALITY.'),
  ]},
  {'title': 'Úvod (prvá obrazovka)', 'fields': [
    F('home.hero_label', 'Štítok nad nadpisom', default='Realitná maklérka · Dubnica nad Váhom · Ilava · Trenčín'),
    F('home.hero_title', 'Hlavný nadpis', 'md', 'Domov\nv dobrých *rukách*.', H1),
    F('home.hero_sub', 'Text pod nadpisom', 'md', 'Som **Mária Fürsten**. Pomôžem vám predať nehnuteľnosť za férovú cenu alebo nájsť takú, ktorá bude naozaj vaša – v Dubnici nad Váhom, Ilave, Trenčíne a okolí.', MD),
    F('home.hero_image', 'Veľká fotka vpravo', 'image', 'img/nem/rodinny-dom-mikusovce/01.webp', 'Keď bude hotová vaša fotografia, môžete ju dať sem (na výšku).'),
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
      'Realitám sa venujem v kraji, ktorý dobre poznám – od Dubnice nad Váhom cez Ilavu až po Trenčín. Viem, ktoré ulice sú tiché, kde sa rýchlo predávajú byty a čo kupujúcich pri dome zaujíma ako prvé.\n\n'
      'Pri každej nehnuteľnosti ma zaujíma aj to, čo je za ňou: prečo predávate, kedy sa chcete sťahovať, čo pre vás znamená dobrá cena. Až potom navrhnem postup. Na obhliadky chodím osobne a po každej vám dám vedieť, ako prebehla.\n\n'
      'Pracujem pod vlastnou značkou **Fürsten Reality** ako samostatná maklérka a spolupracujem s realitnou kanceláriou **VAŠE REALITY s.r.o.** Máte tak jedného človeka, ktorý sa o vás stará, a za ním zázemie kancelárie – zmluvy, právny servis a inzerciu na portáloch.',
      'Text doplňte vlastnými slovami – čím dlhšie a osobnejšie, tým lepšie.'),
    F('about.signature', 'Podpis', default='Mária Fürsten'),
    L('about.facts', 'Krátke fakty', [('title', 'Názov', 'text'), ('text', 'Hodnota', 'text')], [
      {'title': 'Pôsobím', 'text': 'Dubnica nad Váhom, Ilava, Trenčín a okolie'},
      {'title': 'Dohovoríme sa', 'text': 'po slovensky, česky aj po nemecky'},
      {'title': 'Spolupracujem s', 'text': 'VAŠE REALITY s.r.o.'}]),
  ]},
  {'title': 'Služby', 'fields': [
    F('services.label', 'Štítok', default='S čím pomôžem'),
    F('services.title', 'Nadpis', 'md', 'Jasne, *konkrétne* a bez drobného písma', MD),
    L('services.items', 'Služby', [('title', 'Názov', 'text'), ('text', 'Krátky popis', 'textarea'), ('points', 'Čo presne urobím (každý riadok = jeden bod)', 'textarea'), ('link', 'Odkaz', 'url')], [
      {'title': 'Predaj nehnuteľnosti', 'text': 'Byt, dom, pozemok aj starší dom na rekonštrukciu.',
       'points': 'Reálnu cenu podľa predajov v okolí, nie podľa prianí\nKontrolu listu vlastníctva a podkladov\nFotografie, popis a pri staršom dome vizualizácie po rekonštrukcii\nInzerciu na realitných portáloch a osobné obhliadky\nRezervačnú a kúpnu zmluvu a návrh na vklad do katastra\nOdovzdanie nehnuteľnosti a prepis energií',
       'link': 'predat.html'},
      {'title': 'Kúpa a hľadanie', 'text': 'Keď neviete, kde začať, alebo nemáte čas sledovať portály.',
       'points': 'Spolu si ujasníme lokalitu, rozpočet a dispozíciu\nPosielam vám len ponuky, ktoré dávajú zmysel\nIdem s vami na obhliadku a upozorním na riziká\nPreverím list vlastníctva, ťarchy a vecné bremená\nHypotéku vybavíte cez overených partnerov',
       'link': 'hladam.html'},
      {'title': 'Prenájom', 'text': 'Pre majiteľov, ktorí chcú spoľahlivého nájomcu bez starostí.',
       'points': 'Odporučím výšku nájmu a podmienky\nInzerciu a výber nájomcu\nNájomnú zmluvu a preberací protokol\nKauciu a odovzdanie bytu s kľúčmi',
       'link': 'kontakt.html'}]),
  ]},
  {'title': 'Priebeh spolupráce', 'fields': [
    F('process.label', 'Štítok', default='Ako spolupracujeme'),
    F('process.title', 'Nadpis', 'md', 'Šesť krokov od prvej kávy *po kľúče*', MD),
    F('process.lead', 'Text', 'md', 'Pri predaji viete vždy, v ktorom kroku sme a čo nasleduje. Prvé stretnutie je nezáväzné.'),
    L('process.steps', 'Kroky', [('title', 'Názov kroku', 'text'), ('text', 'Popis', 'textarea')], [
      {'title': 'Stretnutie a obhliadka', 'text': 'Prídem sa na nehnuteľnosť pozrieť a vypočujem si vaše plány, termíny a očakávania.'},
      {'title': 'Cena a plán', 'text': 'Podľa porovnateľných predajov v okolí navrhnem reálnu cenu a postup predaja. Dohodneme sa na podmienkach.'},
      {'title': 'Podklady a prezentácia', 'text': 'Skontrolujem list vlastníctva a podklady, pripravím fotografie, popis a podľa potreby pôdorys či vizualizácie.'},
      {'title': 'Inzercia a obhliadky', 'text': 'Nehnuteľnosť zverejním na portáloch, záujemcov preverím a obhliadky vediem osobne. Po každej vám dám spätnú väzbu.'},
      {'title': 'Zmluvy a bezpečný prevod', 'text': 'Rezervačná a kúpna zmluva, bezpečná úhrada kúpnej ceny a návrh na vklad do katastra – s právnym servisom.'},
      {'title': 'Odovzdanie', 'text': 'Odovzdanie kľúčov s preberacím protokolom, stavmi meračov a prepisom energií.'}]),
  ]},
  {'title': 'Referencie', 'fields': [
    F('reviews.label', 'Štítok', default='Referencie'),
    F('reviews.title', 'Nadpis', 'md', 'Čo hovoria *klienti*', MD + ' Sekcia sa na webe ukáže, až keď v časti Referencie pridáte aspoň jednu referenciu.'),
  ]},
  {'title': 'Kontakt (spodná časť)', 'fields': [
    F('contactsec.label', 'Štítok', default='Kontakt'),
    F('contactsec.title', 'Nadpis', 'md', 'Napíšte mi,\n*ozvem sa* vám.', H1),
    F('contactsec.text', 'Text', 'md', 'Najrýchlejšie ma zastihnete telefonicky. Ak píšete, nechajte mi prosím aj telefónne číslo – zavolám vám späť.'),
  ]},
 ]},

 {'id': 'listing', 'title': 'Ponuka a detail', 'icon': 'grid', 'sections': [
  {'title': 'Stránka Ponuka', 'fields': [
    F('offer.seo_title', 'Titulok stránky', default='Ponuka nehnuteľností – Dubnica nad Váhom, Ilava, Trenčín | Fürsten Reality'),
    F('offer.seo_desc', 'Popis pre Google', 'textarea', 'Aktuálna ponuka bytov a domov na predaj a prenájom v Dubnici nad Váhom, Ilave, Trenčíne a okolí. Mária Fürsten – Fürsten Reality.'),
    F('offer.title', 'Nadpis', 'md', 'Aktuálna *ponuka*', H1),
    F('offer.lead', 'Text', 'md', 'Byty a domy na predaj a prenájom v Dubnici nad Váhom, Ilave, Trenčíne a okolí. Na každú nehnuteľnosť vás rada prevediem osobne.'),
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
    F('detail.agent_sub', 'Text pod menom', default='Nehnuteľnosť vám rada ukážem osobne'),
    F('detail.viz_note', 'Poznámka k vizualizáciám (ak pri nehnuteľnosti nie je vlastná)', default='Vizualizácie sú ilustračné – ukazujú možnú podobu po úprave, nie súčasný stav.'),
    F('detail.plan_missing', 'Text, keď chýba pôdorys', default='Pôdorys vám rada pošlem na požiadanie.'),
    F('detail.price_default', 'Text o cene, ak nie je vyplnené „Čo cena zahŕňa“', default='Podrobnosti o cene a o tom, čo zahŕňa, vám rada vysvetlím pri obhliadke.'),
    F('detail.form_title', 'Nadpis formulára', 'md', 'Dohodnime si *obhliadku*', MD),
  ]},
 ]},

 {'id': 'sell', 'title': 'Chcem predať', 'icon': 'key', 'sections': [
  {'title': 'Texty', 'fields': [
    F('sell.seo_title', 'Titulok stránky', default='Chcem predať nehnuteľnosť – Dubnica nad Váhom, Ilava, Trenčín | Fürsten Reality'),
    F('sell.seo_desc', 'Popis pre Google', 'textarea', 'Predávate byt, dom alebo pozemok v Dubnici nad Váhom, Ilave či Trenčíne? Napíšte mi pár údajov, ozvem sa a dohodneme nezáväzné stretnutie.'),
    F('sell.title', 'Nadpis', 'md', 'Chcem predať\n*nehnuteľnosť*', H1),
    F('sell.lead', 'Text', 'md', 'Stačí pár údajov. Ozvem sa vám, prídem sa na nehnuteľnosť pozrieť a navrhnem reálnu cenu aj postup – nezáväzne.'),
    L('sell.points', 'Body vedľa formulára', [('title', 'Text', 'text')], [
      {'title': 'Reálna cena podľa predajov v okolí'}, {'title': 'Fotografie, popis a pri staršom dome vizualizácie'},
      {'title': 'Osobné obhliadky a spätná väzba po každej'}, {'title': 'Zmluvy, právny servis a vklad do katastra'}]),
    F('sell.thanks', 'Poďakovanie po odoslaní', 'md', 'Ďakujem, vaša správa prišla. *Ozvem sa vám* najneskôr nasledujúci pracovný deň.'),
  ]},
 ]},

 {'id': 'search', 'title': 'Hľadám nehnuteľnosť', 'icon': 'search', 'sections': [
  {'title': 'Texty', 'fields': [
    F('search.seo_title', 'Titulok stránky', default='Hľadám nehnuteľnosť – Dubnica nad Váhom, Ilava, Trenčín | Fürsten Reality'),
    F('search.seo_desc', 'Popis pre Google', 'textarea', 'Hľadáte byt alebo dom v Dubnici nad Váhom, Ilave, Trenčíne a okolí? Povedzte mi, čo hľadáte, a dám vám vedieť, keď sa objaví vhodná ponuka.'),
    F('search.title', 'Nadpis', 'md', 'Hľadám\n*nehnuteľnosť*', H1),
    F('search.lead', 'Text', 'md', 'Napíšte mi, čo hľadáte – lokalitu, rozpočet a čo je pre vás dôležité. Ozvem sa, keď sa objaví nehnuteľnosť, ktorá vám bude sedieť, aj keď ešte nebude verejne inzerovaná.'),
    F('search.thanks', 'Poďakovanie po odoslaní', 'md', 'Ďakujem! Vaše požiadavky mám zapísané a *ozvem sa*, keď budem mať vhodnú ponuku.'),
  ]},
 ]},

 {'id': 'contactpage', 'title': 'Stránka Kontakt', 'icon': 'mail', 'sections': [
  {'title': 'Texty', 'fields': [
    F('contactpage.seo_title', 'Titulok stránky', default='Kontakt – Mária Fürsten, realitná maklérka | Dubnica nad Váhom, Ilava, Trenčín'),
    F('contactpage.title', 'Nadpis', 'md', 'Ozvite sa,\n*rada pomôžem*.', H1),
    F('contactpage.thanks', 'Poďakovanie po odoslaní', 'md', 'Ďakujem za správu. *Ozvem sa vám* čo najskôr.'),
  ]},
 ]},

 {'id': 'privacy', 'title': 'Ochrana osobných údajov', 'icon': 'lock', 'sections': [
  {'title': 'Text stránky', 'fields': [
    F('privacy.body', 'Text', 'textarea', GDPR, 'Riadok začínajúci „## “ je nadpis. Všetky miesta „[DOPLNIŤ …]“ treba pred spustením nahradiť skutočnými údajmi – na webe sú zatiaľ zvýraznené.', todo=True),
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
