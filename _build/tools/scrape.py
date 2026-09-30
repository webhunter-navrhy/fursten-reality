#!/usr/bin/env python3
"""Parse downloaded Vaše reality listing pages (_build/raw/l<ID>.html) into _build/raw/scraped.json.
Download is done separately (polite UA, 3 s delay) — see README/commit history."""
import re, json, html, glob, os
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
out = []
for f in sorted(glob.glob(os.path.join(RAW, 'l*.html'))):
    s = open(f, encoding='utf-8').read()
    lid = re.search(r'l(\d+)\.html$', f).group(1)
    prod = None
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try: d = json.loads(m.group(1))
        except Exception: continue
        if d.get('@type') == 'Product': prod = d
    feats = []
    for a, b in re.findall(r'property_features_a">(.*?)</div>\s*<div class="col-auto property_features_b">(.*?)</div>', s, re.S):
        clean = lambda x: html.unescape(re.sub(r'<sup>2</sup>', '²', re.sub(r'\s+', ' ', x))).strip()
        feats.append([re.sub(r'<[^>]+>', '', clean(a)).rstrip(':'), re.sub(r'<[^>]+>', '', clean(b))])
    iframes = re.findall(r'<iframe[^>]+src="([^"]+)"', s)
    canon = prod['url']
    body = s[:s.find('Podobné nehnuteľnosti')]
    imgs = []
    for h in re.findall(r'href="([^"]+)"\s*data-fancybox="gallery', body):
        m = re.search(r'-([0-9a-f]{24})\.(jpe?g|png|webp)', h)
        u = f'https://www.vasereality.sk/imgcache/-{m.group(1)}.{m.group(2)}' if m else h
        if u not in imgs: imgs.append(u)
    addr = prod.get('location', {}).get('address', {})
    geo = prod.get('location', {}).get('geo', {})
    off = prod.get('offers', {})
    out.append({'id': lid, 'url': canon, 'name': prod['name'], 'category': prod.get('category'), 'description': prod.get('description', ''),
                'images': imgs, 'address': addr, 'geo': geo, 'price': off.get('price'), 'currency': off.get('priceCurrency'),
                'availability': off.get('availability'), 'features': feats, 'iframes': iframes})
json.dump(out, open(os.path.join(RAW, 'scraped.json'), 'w'), ensure_ascii=False, indent=1)
for o in out:
    print(o['id'], o['category'], o['price'], len(o['images']), 'img', o['address'].get('addressLocality'), o['iframes'][:3])
    print('   ', '; '.join(f'{a}={b}' for a, b in o['features']))
