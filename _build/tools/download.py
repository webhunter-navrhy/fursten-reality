#!/usr/bin/env python3
"""Download gallery originals listed in _build/raw/scraped.json -> _build/raw/img/<id>/NN.<ext> (polite: UA + delay)."""
import json, os, time, ssl, urllib.request
try:
    import certifi; CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    CTX = ssl.create_default_context()
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw')
UA = 'WebHunterPreviewBot/1.0 (+https://webhunter.cz; info.webhunter@email.cz)'
for o in json.load(open(os.path.join(RAW, 'scraped.json'))):
    d = os.path.join(RAW, 'img', o['id']); os.makedirs(d, exist_ok=True)
    for k, u in enumerate(o['images']):
        dst = os.path.join(d, f'{k:02d}.' + u.rsplit('.', 1)[-1])
        if os.path.exists(dst) and os.path.getsize(dst) > 1000: continue
        req = urllib.request.Request(u, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=60, context=CTX) as r: open(dst, 'wb').write(r.read())
        print(o['id'], k, os.path.getsize(dst), flush=True)
        time.sleep(1.5)
print('done')
