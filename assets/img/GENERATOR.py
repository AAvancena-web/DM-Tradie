"""Generate on-brand placeholder imagery.

No stock photography is reachable from this environment, so rather than leave
empty slots these are drawn: a brand-coloured ground, a motif suggesting the
subject, then grain and a vignette so they read as designed art rather than a
failed image. Every one is meant to be replaced by a real photograph.
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = '/home/user/DM-Tradie/assets/img'
os.makedirs(OUT, exist_ok=True)
SS = 2  # supersample, then downscale for clean edges

WAYS = {
 'amber':  ((251,175,67),  (242,96,74),   (26,10,14)),
 'ember':  ((247,131,59),  (198,41,63),   (24,9,13)),
 'crimson':((242,96,74),   (168,30,78),   (22,8,14)),
 'plum':   ((224,75,98),   (122,30,99),   (20,8,16)),
 'mulberry':((184,54,95),  (74,27,85),    (18,8,16)),
 'ink':    ((126,46,85),   (42,20,51),    (14,7,14)),
 'slate':  ((58,52,70),    (20,18,26),    (10,9,12)),
 'sun':    ((251,175,67),  (247,120,58),  (28,12,10)),
}

def ground(w, h, way, angle=118):
    a, b, _ = WAYS[way]
    y, x = np.mgrid[0:h, 0:w]
    t = math.radians(angle)
    p = (x*math.cos(t) + y*math.sin(t))
    p = (p - p.min()) / (p.max() - p.min())
    img = np.zeros((h, w, 3))
    for i in range(3):
        img[..., i] = a[i] + (b[i]-a[i])*p
    return Image.fromarray(img.astype('uint8'))

def wash(im, cx, cy, r, colour, alpha):
    """A soft radial glow, drawn big and blurred."""
    w, h = im.size
    lay = Image.new('L', (w, h), 0)
    d = ImageDraw.Draw(lay)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=alpha)
    lay = lay.filter(ImageFilter.GaussianBlur(r*0.42))
    im.paste(Image.new('RGB', (w, h), colour), (0, 0), lay)
    return im

def grain(im, amount=7):
    w, h = im.size
    n = np.random.normal(0, amount, (h, w, 1)).repeat(3, 2)
    a = np.clip(np.asarray(im).astype('float32') + n, 0, 255)
    return Image.fromarray(a.astype('uint8'))

def vignette(im, strength=0.42):
    w, h = im.size
    y, x = np.mgrid[0:h, 0:w]
    d = np.sqrt(((x-w/2)/(w/2))**2 + ((y-h/2)/(h/2))**2)
    m = np.clip(1 - strength*np.clip(d-0.55, 0, None)/0.75, 0, 1)[..., None]
    return Image.fromarray((np.asarray(im)*m).astype('uint8'))

def hatch(d, w, h, step=52, alpha=16):
    for i in range(-h, w+h, step):
        d.line([(i, 0), (i+h, h)], fill=(255, 255, 255, alpha), width=2)

# ---------------------------------------------------------------- motifs
def m_browser(d, w, h):
    """Stacked browser windows, receding."""
    for i, (sx, sy, a) in enumerate([(0.30, 0.34, 34), (0.16, 0.22, 54), (0.0, 0.10, 92)]):
        bw, bh = w*0.52, h*0.50
        x, y = w*0.24 + sx*w*0.22, h*0.22 + sy*h*0.22
        d.rounded_rectangle([x, y, x+bw, y+bh], radius=18*SS, outline=(255,255,255,a), width=3*SS)
        d.line([(x, y+34*SS), (x+bw, y+34*SS)], fill=(255,255,255,a), width=3*SS)
        for k in range(3):
            d.ellipse([x+18*SS+k*22*SS, y+12*SS, x+30*SS+k*22*SS, y+24*SS], outline=(255,255,255,a), width=2*SS)
        if i == 2:
            for k, ww in enumerate([0.62, 0.40, 0.52]):
                yy = y+62*SS+k*26*SS
                d.line([(x+20*SS, yy), (x+20*SS+bw*ww, yy)], fill=(255,255,255,a-30), width=5*SS)

def m_pins(d, w, h):
    """Map pins over a street grid."""
    for i in range(1, 7):
        d.line([(0, h*i/7), (w, h*i/7 - h*0.10)], fill=(255,255,255,43), width=2*SS)
    for i in range(1, 9):
        d.line([(w*i/9, 0), (w*i/9 + w*0.05, h)], fill=(255,255,255,43), width=2*SS)
    for (cx, cy, s, a) in [(0.50,0.44,1.0,120),(0.30,0.60,0.62,70),(0.70,0.62,0.7,80),(0.62,0.30,0.5,55)]:
        r = w*0.062*s
        x, y = w*cx, h*cy
        d.ellipse([x-r, y-r, x+r, y+r], outline=(255,255,255,a), width=3*SS)
        d.ellipse([x-r*0.34, y-r*0.34, x+r*0.34, y+r*0.34], fill=(255,255,255,a))
        d.polygon([(x-r*0.52, y+r*0.72), (x+r*0.52, y+r*0.72), (x, y+r*1.9)], outline=(255,255,255,a))

def m_target(d, w, h):
    """Concentric rings with rising bars."""
    cx, cy = w*0.46, h*0.44
    for i, r in enumerate([0.30, 0.21, 0.12, 0.05]):
        rr = w*r
        d.ellipse([cx-rr, cy-rr, cx+rr, cy+rr], outline=(255,255,255,72+i*22), width=3*SS)
    d.line([(cx, cy-w*0.36), (cx, cy+w*0.36)], fill=(255,255,255,63), width=2*SS)
    d.line([(cx-w*0.36, cy), (cx+w*0.36, cy)], fill=(255,255,255,63), width=2*SS)
    for i, bh in enumerate([0.14, 0.24, 0.19, 0.34, 0.44]):
        x = w*0.66 + i*w*0.058
        d.rounded_rectangle([x, h*0.78-h*bh, x+w*0.036, h*0.78], radius=6*SS,
                            fill=(255,255,255,57+i*16))

def m_phones(d, w, h):
    """Phone frames with a play mark."""
    for i, (x, sc, a) in enumerate([(0.24,0.80,46),(0.42,1.0,100),(0.62,0.80,46)]):
        pw, ph = w*0.15*sc, h*0.54*sc
        px, py = w*x, h*0.5 - ph/2
        d.rounded_rectangle([px, py, px+pw, py+ph], radius=22*SS, outline=(255,255,255,a), width=3*SS)
        d.line([(px+pw*0.34, py+14*SS), (px+pw*0.66, py+14*SS)], fill=(255,255,255,a), width=4*SS)
        if i == 1:
            cx, cy, r = px+pw/2, py+ph/2, pw*0.20
            d.polygon([(cx-r*0.6, cy-r), (cx-r*0.6, cy+r), (cx+r, cy)], outline=(255,255,255,188))
    for k, r in enumerate([0.30, 0.38, 0.46]):
        rr = w*r
        d.arc([w*0.5-rr, h*0.5-rr, w*0.5+rr, h*0.5+rr], 200, 340, fill=(255,255,255,51-k*6), width=2*SS)

def m_brand(d, w, h):
    """Overlapping identity shapes."""
    cx, cy = w*0.5, h*0.48
    r = w*0.17
    d.regular_polygon((cx-r*0.55, cy, r), 6, rotation=0, outline=(255,255,255,130), width=3*SS)
    d.ellipse([cx+r*0.05-r, cy-r, cx+r*0.05+r, cy+r], outline=(255,255,255,115), width=3*SS)
    d.rounded_rectangle([cx-r*0.2, cy-r*0.72, cx+r*1.3, cy+r*0.72], radius=16*SS,
                        outline=(255,255,255,93), width=3*SS)
    for i in range(4):
        x = w*0.30 + i*w*0.11
        d.rounded_rectangle([x, h*0.78, x+w*0.082, h*0.855], radius=8*SS,
                            fill=(255,255,255,51+i*14))

def m_lens(d, w, h):
    """Aperture blades inside a lens ring."""
    cx, cy = w*0.5, h*0.47
    R = w*0.20
    d.ellipse([cx-R*1.42, cy-R*1.42, cx+R*1.42, cy+R*1.42], outline=(255,255,255,77), width=3*SS)
    d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=(255,255,255,153), width=3*SS)
    for k in range(6):
        a0 = math.radians(k*60)
        a1 = math.radians(k*60 + 120)
        d.line([(cx+R*math.cos(a0), cy+R*math.sin(a0)),
                (cx+R*math.cos(a1), cy+R*math.sin(a1))], fill=(255,255,255,106), width=3*SS)
    for i in range(3):
        x = w*0.13 + i*w*0.29
        d.rounded_rectangle([x, h*0.80, x+w*0.20, h*0.885], radius=8*SS,
                            outline=(255,255,255,72), width=2*SS)

def m_facade(d, w, h, seed=0):
    """Abstract building facades — the work tiles."""
    rnd = random.Random(seed)
    base = h*0.86
    x = w*0.06
    while x < w*0.94:
        bw = w*rnd.uniform(0.09, 0.17)
        bh = h*rnd.uniform(0.26, 0.62)
        a = rnd.choice([26, 38, 52, 68])
        d.rectangle([x, base-bh, x+bw, base], outline=(255,255,255,a+22), width=3*SS)
        if rnd.random() < 0.55:
            d.polygon([(x, base-bh), (x+bw/2, base-bh-h*0.09), (x+bw, base-bh)],
                      outline=(255,255,255,a+22))
        rows = int(bh/(h*0.085))
        for r in range(rows):
            for c in range(max(2, int(bw/(w*0.045)))):
                wx = x + w*0.018 + c*w*0.045
                wy = base - bh + h*0.035 + r*h*0.085
                if wx+w*0.026 < x+bw and wy+h*0.05 < base and rnd.random() < 0.72:
                    d.rectangle([wx, wy, wx+w*0.026, wy+h*0.05], fill=(255,255,255,a//2+8))
        x += bw + w*rnd.uniform(0.012, 0.03)
    d.line([(0, base), (w, base)], fill=(255,255,255,115), width=4*SS)

def m_site(d, w, h):
    """A site scene: crane, frame, ground line — for the about page."""
    base = h*0.84
    d.line([(0, base), (w, base)], fill=(255,255,255,106), width=4*SS)
    # frame
    fx, fw, fh = w*0.14, w*0.30, h*0.46
    d.rectangle([fx, base-fh, fx+fw, base], outline=(255,255,255,115), width=3*SS)
    for i in range(1, 4):
        d.line([(fx, base-fh*i/4), (fx+fw, base-fh*i/4)], fill=(255,255,255,77), width=2*SS)
    for i in range(1, 4):
        d.line([(fx+fw*i/4, base-fh), (fx+fw*i/4, base)], fill=(255,255,255,77), width=2*SS)
    d.line([(fx, base), (fx+fw, base-fh)], fill=(255,255,255,63), width=2*SS)
    # crane
    mx = w*0.62
    d.line([(mx, base), (mx, h*0.14)], fill=(255,255,255,130), width=4*SS)
    d.line([(w*0.42, h*0.18), (w*0.88, h*0.18)], fill=(255,255,255,130), width=4*SS)
    d.line([(mx, h*0.14), (w*0.42, h*0.18)], fill=(255,255,255,86), width=2*SS)
    d.line([(mx, h*0.14), (w*0.88, h*0.18)], fill=(255,255,255,86), width=2*SS)
    d.line([(w*0.78, h*0.18), (w*0.78, h*0.44)], fill=(255,255,255,106), width=2*SS)
    d.rectangle([w*0.755, h*0.44, w*0.805, h*0.50], outline=(255,255,255,130), width=3*SS)

MOTIF = {'browser':m_browser, 'pins':m_pins, 'target':m_target, 'phones':m_phones,
         'brand':m_brand, 'lens':m_lens, 'site':m_site}

def make(name, w, h, way, motif, seed=0):
    W, H = w*SS, h*SS
    im = ground(W, H, way).convert('RGB')
    a, b, dark = WAYS[way]
    im = wash(im, W*0.16, H*0.04, W*0.52, (255, 244, 228), 74)
    im = wash(im, W*0.94, H*1.04, W*0.72, dark, 205)
    im = wash(im, W*0.50, H*1.18, W*0.78, dark, 150)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    hatch(d, W, H, step=46*SS, alpha=17)
    if motif == 'facade':
        m_facade(d, W, H, seed)
    else:
        MOTIF[motif](d, W, H)
    im = Image.alpha_composite(im.convert('RGBA'), lay).convert('RGB')
    im = im.resize((w, h), Image.LANCZOS)
    im = vignette(grain(im, 5), 0.5)
    p = f'{OUT}/{name}.jpg'
    im.save(p, 'JPEG', quality=82, optimize=True, progressive=True)
    return p, os.path.getsize(p)

JOBS = [
 # service page + card imagery
 ('service-web-design',        1200, 760, 'amber',    'browser', 0),
 ('service-local-seo',         1200, 760, 'ember',    'pins',    0),
 ('service-google-ads',        1200, 760, 'crimson',  'target',  0),
 ('service-meta-ads',          1200, 760, 'plum',     'phones',  0),
 ('service-branding',          1200, 760, 'mulberry', 'brand',   0),
 ('service-content-photography',           1200, 760, 'ink',      'lens',    0),
 # project tiles
 ('work-northbeam',            1280, 800, 'slate',    'facade',  3),
 ('work-kerrick',              1280, 800, 'sun',      'facade',  11),
 ('work-vantage',              1280, 800, 'ink',      'facade',  21),
 ('work-palm',                 1280, 800, 'plum',     'facade',  33),
 ('work-studio-nine',          1280, 800, 'ember',    'facade',  47),
 ('work-ironbark',             1280, 800, 'slate',    'facade',  59),
 # about
 ('about-crew',                1600, 900, 'crimson',  'site',    0),
]
total = 0
for name, w, h, way, motif, seed in JOBS:
    p, sz = make(name, w, h, way, motif, seed)
    total += sz
    print(f'{name:26} {w}x{h}  {sz//1024:>4} KB')
print(f'{"total":26}          {total//1024:>4} KB')
