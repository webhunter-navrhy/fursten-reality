#!/usr/bin/env python3
"""Fürsten Reality wordmark -> img/site/*.svg (text as outlines). Needs fontTools (run locally, output is committed)."""
import os
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
F = os.path.join(ROOT, '_build', 'fonts')

def load(name, axes):
    f = TTFont(os.path.join(F, name)); return instantiateVariableFont(f, axes)

def text_path(font, s, size, x0, y0, track=0.0):
    """return (svg path d, advance width) — baseline at y0"""
    upm = font['head'].unitsPerEm; sc = size / upm
    gs = font.getGlyphSet(); cmap = font.getBestCmap(); hm = font['hmtx']
    kern = {}
    ds = []; x = x0
    names = [cmap[ord(c)] for c in s]
    for i, g in enumerate(names):
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, x, y0)))
        ds.append(pen.getCommands())
        x += hm[g][0] * sc + (track * size if i < len(names) - 1 else 0)
    return ' '.join(ds), x - x0

serif = load('Newsreader[opsz,wght].ttf', {'wght': 400, 'opsz': 72})
ital = load('Newsreader-Italic[opsz,wght].ttf', {'wght': 380, 'opsz': 72})
sans = load('HankenGrotesk[wght].ttf', {'wght': 560})

def build(text_col, gold, sub_col, fname, with_mark=True):
    # mark: arch doorway with italic F
    mx = 0
    arch = f'M{mx+1} 58 V22 A19 19 0 0 1 {mx+39} 22 V58'
    fpath, fw = text_path(ital, 'F', 40, 0, 0)
    f_d, _ = text_path(ital, 'F', 40, mx + 20 - fw / 2 - 1.5, 48)
    tx = 56 if with_mark else 0
    word, ww = text_path(serif, 'Fürsten', 44, tx, 40)
    sub, sw = text_path(sans, 'REALITY', 11.2, tx + 1.5, 58, track=0.5)
    W = tx + max(ww, sw) + 2
    mark = (f'<path d="{arch}" fill="none" stroke="{gold}" stroke-width="1.6"/>'
            f'<path d="M{mx+8} 58 H{mx+32}" stroke="{gold}" stroke-width="1.6"/>'
            f'<path d="{f_d}" fill="{gold}"/>') if with_mark else ''
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.1f} 60" width="{W:.0f}" height="60" role="img" aria-label="Fürsten Reality">'
           f'<title>Fürsten Reality</title>{mark}<path d="{word}" fill="{text_col}"/><path d="{sub}" fill="{sub_col}"/></svg>')
    open(os.path.join(ROOT, 'img', 'site', fname), 'w').write(svg)
    return W

GREEN, GOLD, GOLD_D, CREAM = '#1F3B34', '#B8955E', '#9C7A45', '#F3EEE2'
print(build(GREEN, GOLD_D, GOLD_D, 'logo.svg'))
print(build(CREAM, '#CDB07E', '#CDB07E', 'logo-light.svg'))
# favicon / app mark: arch + F on deep green
f_d, _ = text_path(ital, 'F', 40, 0, 0); fw = _
f_d, _ = text_path(ital, 'F', 40, 32 - fw / 2 - 1.5, 45)
open(os.path.join(ROOT, 'img', 'site', 'mark.svg'), 'w').write(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{GREEN}"/>'
    f'<path d="M13 55 V26 A19 19 0 0 1 51 26 V55" fill="none" stroke="#CDB07E" stroke-width="2.2"/>'
    f'<path d="{f_d}" fill="#E9D9B8"/></svg>')
