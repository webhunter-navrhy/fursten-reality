#!/usr/bin/env python3
"""Balíček finálneho loga Fürsten Reality (variant C – tmavozelená + zlatá) pre Facebook, tlač a bannery.
Výstup: _build/logo-export/{SVG,PDF,PNG}/ + Fursten-Reality-logo.zip
SVG: text prevedený na krivky (Montserrat, OFL) – bez závislosti na fontoch. PDF a PNG cez rsvg-convert (librsvg).
Spustenie (lokálne, potrebuje fontTools + rsvg-convert): python3 _build/tools/logo_export.py"""
import os, re, shutil, subprocess, zipfile
import logo_brand as LB

ROOT = LB.ROOT
EXP = os.path.join(ROOT, '_build', 'logo-export')
GREEN, GOLD, CREAM, GOLD_L, WHITE = LB.GREEN, LB.GOLD, LB.CREAM, LB.GOLD_L, '#FFFFFF'
PAPER = '#F4F0E6'   # svetlé pozadie webu

def print_safe(svg):
    """maska (zárezy vo veži) -> orezová cesta s even-odd: cairo/rsvg ju v PDF nechá vektorovú (maska sa rastruje)"""
    def clip(m):
        gaps = ' '.join(re.findall(r'<path d="([^"]+)" fill="#000"/>', m.group(2)))
        return f'<clipPath id="{m.group(1)}" clipPathUnits="userSpaceOnUse"><path clip-rule="evenodd" d="M0 0H1254V700H0Z {gaps}"/></clipPath>'
    svg = re.sub(r'<mask id="(g\d+)"[^>]*>(.*?)</mask>', clip, svg)
    return re.sub(r'mask="url\(#(g\d+)\)"', r'clip-path="url(#\1)"', svg)

def stacked(A, B, T):
    """domček nad nápisom FÜRSTEN, pod ním linky a REALITY (ako logo z Facebooku, bez podtitulku a vlnovky)"""
    d, _ = LB.text('FURSTEN', 650, 218, 88, 832, fit=1077 - 12)
    ux0, ux1, _ = LB.glyph_bounds('U', 650, 218)
    f = LB.font(650); sc = 218 / f['head'].unitsPerEm; cmap = f.getBestCmap(); hm = f['hmtx']
    advs = [hm[cmap[ord(c)]][0] * sc for c in 'FURSTEN']
    ux = 88 + advs[0] + (1077 - 12 - sum(advs)) / 6
    uml = ''.join(f'<rect x="{ux + ux0 + dx:.1f}" y="652" width="34" height="26" fill="{B}"/>' for dx in (18, (ux1 - ux0) - 52))
    real, _ = LB.text('REALITY', 420, 84, 627, 945, track=.34, anchor='middle')
    lines = f'<path d="M88 912H276" stroke="{A}" stroke-width="7"/><path d="M976 912H1163" stroke="{B}" stroke-width="7"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="60 70 1134 900" width="1134" height="900" role="img" aria-label="Fürsten Reality">'
            f'<title>Fürsten Reality</title>{LB.mark(A, B)}<path d="{d}" fill="{T}"/>{uml}{lines}<path d="{real}" fill="{B}"/></svg>')

def symbol(A, B):
    """samotný domček (strecha + budovy), štvorcové plátno s malým okrajom"""
    m = LB.mark(A, B).replace('M88 607H322', 'M300 607H322').replace('M928 607H1163', 'M928 607H950')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="274 5 702 702" width="702" height="702" role="img" aria-label="Fürsten Reality">'
            f'<title>Fürsten Reality</title>{m}</svg>')

def horizontal(A, B, T):
    LB.OUT = os.path.join(EXP, 'tmp'); os.makedirs(LB.OUT, exist_ok=True)
    LB.horizontal(A, B, T, 'h.svg'); s = open(os.path.join(LB.OUT, 'h.svg')).read(); shutil.rmtree(LB.OUT)
    return s

def rsvg(src, dst, fmt, w=None, h=None, bg=None):
    cmd = ['rsvg-convert', '-f', fmt, '-o', dst] + (['-w', str(w)] if w else []) + (['-h', str(h)] if h else []) + (['-b', bg] if bg else []) + ['-a', src]
    subprocess.run(cmd, check=True)

def main():
    shutil.rmtree(EXP, ignore_errors=True)
    for d in ('SVG', 'PDF', 'PNG'): os.makedirs(os.path.join(EXP, d))
    svgs = {
        'Fursten-Reality-logo-vodorovne-farebne': horizontal(GREEN, GOLD, GREEN),
        'Fursten-Reality-logo-vodorovne-svetle': horizontal(CREAM, GOLD_L, CREAM),
        'Fursten-Reality-logo-vodorovne-biele': horizontal(WHITE, WHITE, WHITE),
        'Fursten-Reality-logo-nad-sebou-farebne': stacked(GREEN, GOLD, GREEN),
        'Fursten-Reality-logo-nad-sebou-svetle': stacked(CREAM, GOLD_L, CREAM),
        'Fursten-Reality-logo-nad-sebou-biele': stacked(WHITE, WHITE, WHITE),
        'Fursten-Reality-symbol-farebny': symbol(GREEN, GOLD),
        'Fursten-Reality-symbol-svetly': symbol(CREAM, GOLD_L),
        'Fursten-Reality-symbol-biely': symbol(WHITE, WHITE),
    }
    for n, s in svgs.items():
        s = print_safe(s); p = os.path.join(EXP, 'SVG', n + '.svg'); open(p, 'w', encoding='utf-8').write(s)
        rsvg(p, os.path.join(EXP, 'PDF', n + '.pdf'), 'pdf')
    S = lambda n: os.path.join(EXP, 'SVG', n + '.svg')
    P = lambda n: os.path.join(EXP, 'PNG', n)
    rsvg(S('Fursten-Reality-logo-vodorovne-farebne'), P('Fursten-Reality-logo-vodorovne-farebne-1000px.png'), 'png', w=1000)
    rsvg(S('Fursten-Reality-logo-vodorovne-farebne'), P('Fursten-Reality-logo-vodorovne-farebne-3000px.png'), 'png', w=3000)
    rsvg(S('Fursten-Reality-logo-vodorovne-biele'), P('Fursten-Reality-logo-vodorovne-biele-3000px.png'), 'png', w=3000)
    rsvg(S('Fursten-Reality-logo-nad-sebou-farebne'), P('Fursten-Reality-logo-nad-sebou-farebne-3000px.png'), 'png', w=3000)
    rsvg(S('Fursten-Reality-logo-nad-sebou-biele'), P('Fursten-Reality-logo-nad-sebou-biele-3000px.png'), 'png', w=3000)
    rsvg(S('Fursten-Reality-symbol-farebny'), P('Fursten-Reality-symbol-farebny-1024px.png'), 'png', w=1024, h=1024)
    rsvg(S('Fursten-Reality-symbol-biely'), P('Fursten-Reality-symbol-biely-1024px.png'), 'png', w=1024, h=1024)
    # profilovka Facebook 1080 × 1080: logo nad sebou na svetlom pozadí webu, okraj tak, aby sa zmestilo aj do kruhového výrezu
    inner = print_safe(stacked(GREEN, GOLD, GREEN))
    w = 780; h = round(w * 900 / 1134)
    fb = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1080" width="1080" height="1080"><rect width="1080" height="1080" fill="{PAPER}"/>'
          f'<svg x="{(1080 - w) / 2}" y="{(1080 - h) / 2 + 6}" width="{w}" height="{h}" viewBox="60 70 1134 900">{inner[inner.index(">") + 1:inner.rindex("</svg>")]}</svg></svg>')
    fbp = S('Fursten-Reality-Facebook-profilovka'); open(fbp, 'w', encoding='utf-8').write(fb)
    rsvg(fbp, P('Fursten-Reality-Facebook-profilovka-1080px.png'), 'png', w=1080, h=1080); os.remove(fbp)
    open(os.path.join(EXP, 'CITAJ-MA.txt'), 'w', encoding='utf-8').write(
        'Fürsten Reality – logo (variant C: tmavozelená #1F3B34 + zlatá #B08D55)\n\n'
        'SVG – vektor, text prevedený na krivky (na web, do grafických programov, pre tlačiareň)\n'
        'PDF – vektor pre tlačiareň (vizitky, bannery, polep auta)\n'
        'PNG – priehľadné pozadie (Facebook, Word, e-maily)\n\n'
        'farebne = na svetlé pozadie · svetle = krémová + zlatá na tmavé pozadie (ako v pätičke webu) · biele = jednofarebné biele na tmavé pozadie alebo fotku\n'
        'vodorovne = do hlavičiek a bannerov · nad sebou = na štvorcové a vysoké formáty · symbol = samotný domček (ikona, razítko, avatar)\n'
        'Facebook-profilovka-1080px.png = profilová fotka stránky (logo sa zmestí aj do kruhového výrezu)\n\n'
        'Svetlé pozadie webu: #F4F0E6 · krémová: #F3EEE2 · svetlá zlatá: #CDB07E\n')
    z = os.path.join(EXP, 'Fursten-Reality-logo.zip')
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zf:
        for d in ('SVG', 'PDF', 'PNG'):
            for f in sorted(os.listdir(os.path.join(EXP, d))): zf.write(os.path.join(EXP, d, f), f'Fursten-Reality-logo/{d}/{f}')
        zf.write(os.path.join(EXP, 'CITAJ-MA.txt'), 'Fursten-Reality-logo/CITAJ-MA.txt')
    for d in ('SVG', 'PDF', 'PNG'): print(d, sorted(os.listdir(os.path.join(EXP, d))))
    print(z, os.path.getsize(z) // 1024, 'kB')

if __name__ == '__main__':
    main()
