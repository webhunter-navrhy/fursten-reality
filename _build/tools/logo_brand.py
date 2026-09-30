#!/usr/bin/env python3
"""Vektorová (SVG) rekonštrukcia loga Fürsten Reality, ktoré Mária používa na Facebooku (pôvodne raster 1254 px).
Výstup: img/site/brand/*.svg — text prevedený na krivky (Montserrat, OFL), žiadne závislosti na fontoch.
  fursten-logo-original.svg   pôvodné farby (modrá/červená) – pre Facebook, tlač
  fursten-logo-web.svg        farby webu (tmavozelená/šampanská zlatá)
  fursten-logo-horizontal.svg / -light.svg   vodorovná verzia do hlavičky / na tmavé pozadie
Spustenie (lokálne, potrebuje fontTools): python _build/tools/logo_brand.py"""
import os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'img', 'site', 'brand'); os.makedirs(OUT, exist_ok=True)
FONT = os.path.join(ROOT, '_build', 'fonts', 'Montserrat[wght].ttf')
_fonts = {}
def font(w):
    if w not in _fonts: _fonts[w] = instantiateVariableFont(TTFont(FONT), {'wght': w})
    return _fonts[w]

def text(s, w, size, x0, base, track=0.0, fit=None, anchor='start'):
    """outlined text; fit=width stretches tracking to span exactly `fit` px"""
    f = font(w); upm = f['head'].unitsPerEm; sc = size / upm
    gs = f.getGlyphSet(); cmap = f.getBestCmap(); hm = f['hmtx']
    names = [cmap[ord(c)] for c in s]
    adv = [hm[g][0] * sc for g in names]
    if fit and len(names) > 1:
        # visible width = sum advances minus last glyph's right bearing
        track = (fit - sum(adv)) / (len(names) - 1) / size
    total = sum(adv) + track * size * (len(names) - 1)
    x = x0 - (total / 2 if anchor == 'middle' else total if anchor == 'end' else 0)
    ds = []
    for g, a in zip(names, adv):
        pen = SVGPathPen(gs); gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, x, base))); ds.append(pen.getCommands())
        x += a + track * size
    return ' '.join(ds), total

def glyph_bounds(ch, w, size):
    f = font(w); gs = f.getGlyphSet(); g = f.getBestCmap()[ord(ch)]
    bp = BoundsPen(gs); gs[g].draw(bp); sc = size / f['head'].unitsPerEm
    xmin, ymin, xmax, ymax = bp.bounds
    return xmin * sc, xmax * sc, ymax * sc

def mark(A, B, W='#fff'):
    """skyline + roof + window, coordinates in the original 1254 px canvas. A = primary, B = accent"""
    clip = 'M0 0H1254V607H925L645 380 325 607H0Z'
    sl = lambda x: 242 + (x - 553) * .58                      # descending top edge of the striped block
    bars = ''.join(f'<path d="M{553 + k * 17} {sl(553 + k * 17):.1f} {564 + k * 17} {sl(564 + k * 17):.1f}V600H{553 + k * 17}Z" fill="{A}"/>' for k in range(5))
    gaps = ''.join(f'<path d="M{564 + k * 17} {sl(564 + k * 17) - 1:.1f} {570 + k * 17} {sl(570 + k * 17) - 1:.1f}V600H{564 + k * 17}Z" fill="#000"/>' for k in range(5))
    uid = abs(hash(A + B)) % 10000
    towers = (f'<defs><mask id="g{uid}" maskUnits="userSpaceOnUse" x="0" y="0" width="1254" height="700"><rect width="1254" height="700" fill="#fff"/>{gaps}</mask></defs>'
              f'<g clip-path="url(#sky{uid})">'
              f'<path d="M463 297 548 242V600H463Z" fill="{B}"/>'
              f'<path d="M570 178 700 92V600H570Z" fill="{A}" mask="url(#g{uid})"/>{bars}'
              f'<path d="M712 165 770 210V600H712Z" fill="{A}"/>'
              f'<path d="M785 313 847 360V600H785Z" fill="{A}"/></g>')
    roof = (f'<path d="M88 607H322" stroke="{A}" stroke-width="7"/>'
            f'<path d="M318 612 645 398 930 610" fill="none" stroke="{A}" stroke-width="20" stroke-linejoin="miter"/>'
            f'<path d="M928 607H1163" stroke="{B}" stroke-width="7"/>'
            f'<path d="M362 614 640 460 772 548" fill="none" stroke="{B}" stroke-width="12"/>'
            + ''.join(f'<rect x="{x}" y="{y}" width="30" height="30" fill="{A}"/>' for x in (606, 643) for y in (548, 585)))
    return f'<defs><clipPath id="sky{uid}"><path d="{clip}"/></clipPath></defs>{towers}{roof}'

def full_logo(A, B, name):
    # FÜRSTEN: Montserrat 650, spanning x 88–1165, baseline 832; umlaut drawn as two accent squares
    d, _ = text('FURSTEN', 650, 218, 88, 832, fit=1077 - 12)
    ux0, ux1, uh = glyph_bounds('U', 650, 218)
    # position of U: advance of F + tracking
    f = font(650); sc = 218 / f['head'].unitsPerEm; cmap = f.getBestCmap(); hm = f['hmtx']
    advs = [hm[cmap[ord(c)]][0] * sc for c in 'FURSTEN']
    tr = (1077 - 12 - sum(advs)) / 6
    ux = 88 + advs[0] + tr
    uml = ''.join(f'<rect x="{ux + ux0 + dx:.1f}" y="652" width="34" height="26" fill="{B}"/>' for dx in (18, (ux1 - ux0) - 52))
    real, rw = text('REALITY', 420, 84, 627, 945, track=.34, anchor='middle')
    parts = ['MÁRIA FÜRSTEN', 'VÁŠ MAKLÉR', 'SINCE 2020']
    widths = [text(t, 500, 42, 0, 0, track=.035)[1] for t in parts]
    gap = (1036 - sum(widths)) / 2
    x = 104; tags = []; dots = ''
    for k, (t, w) in enumerate(zip(parts, widths)):
        tags.append(text(t, 500, 42, x, 1021, track=.035)[0]); x += w
        if k < 2: dots += f'<circle cx="{x + gap / 2:.1f}" cy="1006" r="7" fill="{B}"/>'; x += gap
    tag1, tag2, tag3 = tags
    swoosh = (f'<path d="M250 1055Q560 1232 900 1072Q560 1196 250 1055Z" fill="{A}"/>'
              f'<path d="M600 1199Q880 1182 1006 1054Q860 1164 600 1199Z" fill="{B}"/>')
    lines = f'<path d="M88 912H276" stroke="{A}" stroke-width="7"/><path d="M976 912H1163" stroke="{B}" stroke-width="7"/>'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="60 70 1134 1150" role="img" aria-label="Fürsten Reality – Mária Fürsten, váš maklér">'
           f'<title>Fürsten Reality</title>{mark(A, B)}<path d="{d}" fill="{A}"/>{uml}{lines}<path d="{real}" fill="{B}"/>'
           f'<path d="{tag1} {tag2} {tag3}" fill="{A}"/>{dots}{swoosh}</svg>')
    open(os.path.join(OUT, name), 'w').write(svg)

def horizontal(A, B, T, name):
    """mark (cropped roof + skyline) + FÜRSTEN / REALITY — for the site header (height 61)"""
    # mark region in original coords: x 300..950, y 85..620 -> scale to height 58
    s = 58 / 535; mx = -300 * s; my = -85 * s + 1.5
    d, w = text('FURSTEN', 650, 38, 84, 39, track=.06)
    f = font(650); sc = 38 / f['head'].unitsPerEm; cmap = f.getBestCmap(); hm = f['hmtx']
    ux = 84 + hm[cmap[ord('F')]][0] * sc + .06 * 38
    ux0, ux1, _ = glyph_bounds('U', 650, 38)
    uml = ''.join(f'<rect x="{ux + ux0 + dx:.2f}" y="6.2" width="5.6" height="4.4" fill="{B}"/>' for dx in (3, (ux1 - ux0) - 8.6))
    r, rw = text('REALITY', 430, 13.5, 84 + w / 2, 58, track=.42, anchor='middle')
    W = 84 + w + 4
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} 61" width="{W:.0f}" height="61" role="img" aria-label="Fürsten Reality">'
           f'<title>Fürsten Reality</title><g transform="translate({mx:.2f} {my:.2f}) scale({s:.5f})">{mark(A, B).replace("M88 607H322", "M300 607H322").replace("M928 607H1163", "M928 607H950")}</g>'
           f'<path d="{d}" fill="{T}"/>{uml}<path d="{r}" fill="{B}"/></svg>')
    open(os.path.join(OUT, name), 'w').write(svg)

BLUE, RED = '#0B3F94', '#D2141C'
GREEN, GOLD, CREAM, GOLD_L = '#1F3B34', '#B08D55', '#F3EEE2', '#CDB07E'
full_logo(BLUE, RED, 'fursten-logo-original.svg')
full_logo(GREEN, GOLD, 'fursten-logo-web.svg')
horizontal(GREEN, GOLD, GREEN, 'fursten-logo-horizontal.svg')
horizontal(CREAM, GOLD_L, CREAM, 'fursten-logo-horizontal-light.svg')
print(sorted(os.listdir(OUT)))
