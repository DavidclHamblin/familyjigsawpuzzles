"""Builds the Family Jigsaw Puzzles static site.

python3 src/build.py  ->  dist/  (the real site, for GitHub Pages)
Sizes, materials, treatments, backdrops and prices live in assets/js/data.js; this script reads it with node,
so there is one source of truth.
"""
import hashlib, json, random, shutil, subprocess
from pathlib import Path
from html import escape as e

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
DOMAIN = "www.familyjigsawpuzzles.com"
SITE = f"https://{DOMAIN}"

data = json.loads(subprocess.check_output(["node", "-e", """
global.window = {}; require(process.argv[1]); console.log(JSON.stringify(window.FJP));
""", str(ROOT / "assets/js/data.js")]))
CFG, SIZES, WOOD, MATERIALS = data["config"], data["sizes"], data["woodSizes"], data["materials"]
TREATMENTS, BACKDROPS, REGIONS, GBP = data["treatments"], data["backdrops"], data["regions"], data["gbp"]
DISCOUNT = CFG["foundingDiscount"]


def money(eur):
    """A price shown in pounds by default; region.js switches it to euros for EU visitors."""
    return f'<span class="money" data-eur="{eur}">£{GBP[str(eur)]}</span>'


FONTS = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Figtree:wght@400;500;600;700&family=Oswald:wght@600&display=swap"


# ---------- Jigsaw shapes ----------
# One edge with a tab, in edge coordinates: t runs 0..1 along the edge, n is the bump out of it (fraction of edge length).
_TAB = [((0.30, 0), (0.42, 0.02), (0.40, -0.06)), ((0.37, -0.16), (0.45, -0.22), (0.50, -0.22)),
        ((0.55, -0.22), (0.63, -0.16), (0.60, -0.06)), ((0.58, 0.02), (0.70, 0), (1, 0))]


def edge(x0, y0, x1, y1, d):
    """Cubic curves from (x0,y0) to (x1,y1) with a tab on side d (+1 or -1); d=0 is a straight edge.
    Reversing an edge means swapping the ends and flipping d, which keeps the tab on the same side."""
    if d == 0:
        return f"L{x1:.1f} {y1:.1f}"
    dx, dy = x1 - x0, y1 - y0
    def pt(t, n):
        return f"{x0 + t * dx - n * d * dy:.1f} {y0 + t * dy + n * d * dx:.1f}"
    return "".join("C" + ",".join(pt(*p) for p in seg) for seg in _TAB)


def jigsaw(cols, rows, w, h, seed=7):
    """The cut lines of a cols x rows puzzle as one SVG path, plus the tab directions (for cutting out a piece)."""
    rnd = random.Random(seed)
    vdir = [[rnd.choice((1, -1)) for _ in range(rows)] for _ in range(cols - 1)]   # edge right of column c, row r
    hdir = [[rnd.choice((1, -1)) for _ in range(cols)] for _ in range(rows - 1)]   # edge below row r, column c
    cw, ch = w / cols, h / rows
    d = []
    for c in range(cols - 1):
        x = (c + 1) * cw
        d.append(f"M{x:.1f} 0" + "".join(edge(x, r * ch, x, (r + 1) * ch, vdir[c][r]) for r in range(rows)))
    for r in range(rows - 1):
        y = (r + 1) * ch
        d.append(f"M0 {y:.1f}" + "".join(edge(c * cw, y, (c + 1) * cw, y, hdir[r][c]) for c in range(cols)))
    return "".join(d), vdir, hdir, cw, ch


def piece_outline(c, r, cols, rows, vdir, hdir, cw, ch):
    """Closed outline of piece (c, r), walking clockwise: top, right, bottom, left."""
    x0, y0, x1, y1 = c * cw, r * ch, (c + 1) * cw, (r + 1) * ch
    top = hdir[r - 1][c] if r > 0 else 0
    right = vdir[c][r] if c < cols - 1 else 0
    bottom = hdir[r][c] if r < rows - 1 else 0
    left = vdir[c - 1][r] if c > 0 else 0
    return (f"M{x0:.1f} {y0:.1f}" + edge(x0, y0, x1, y0, top) + edge(x1, y0, x1, y1, right)
            + edge(x1, y1, x0, y1, -bottom) + edge(x0, y1, x0, y0, -left) + "Z")


_LOGO = ('<path d="M3 3h11v3.2a2.6 2.6 0 1 0 0 4.6V14H3z" fill="#EE4B2B"/>'
         '<path d="M18 3h11v11h-3.2a2.6 2.6 0 1 0-4.6 0H18z" fill="#FFC21A"/>'
         '<path d="M3 18h3.2a2.6 2.6 0 1 1 4.6 0H14v11H3z" fill="#16A6E3"/>'
         '<path d="M18 18h11v11H18v-3.2a2.6 2.6 0 1 0 0-4.6z" fill="#1FB45A"/>')
LOGO = f'<svg class="logo-jig" viewBox="0 0 32 32" aria-hidden="true">{_LOGO}</svg>'
FAVICON = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">{_LOGO}</svg>'


def v(rel):
    """Asset link with a short content hash, so browsers fetch a changed file straight away."""
    h = hashlib.sha1((ROOT / "assets" / rel).read_bytes()).hexdigest()[:8]
    return f"assets/{rel}?v={h}"


def head(title, desc, path):
    return f"""<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE}/{path}">
<link rel="canonical" href="{SITE}/{path}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{v("css/site.css")}">
"""


def header():
    return f"""<header class="site-head"><div class="wrap">
<a class="logo" href="index.html" aria-label="Family Jigsaw Puzzles home">{LOGO}Family Jigsaw Puzzles</a>
<nav class="nav" aria-label="Main"><a href="#sizes">Sizes</a><a href="#looks">Looks</a><a href="#materials">Cardboard or wood</a><a href="#pricing">Pricing</a><a href="#faq">FAQ</a></nav>
<label class="region"><span class="sr-only">Deliver to</span><select class="region-select" aria-label="Deliver to">{''.join(f'<option value="{k}">{e(r["label"])}</option>' for k, r in REGIONS.items())}</select></label>
<a class="btn btn-sm red" href="#join">Join the list</a>
</div></header>
<p class="region-bar" id="region-bar" role="status" hidden></p>"""


def footer():
    return f"""<footer class="site-foot"><div class="wrap foot-grid">
<div style="display:grid;gap:10px;max-width:380px"><a class="logo" href="index.html">{LOGO}Family Jigsaw Puzzles</a>
<p class="small">Jigsaw puzzles made from your own photos, as they are or drawn in our cartoon styles, in cardboard or wood.</p></div>
<div style="display:grid;gap:12px"><div class="foot-links"><a href="#sizes">Sizes</a><a href="#looks">Looks and backdrops</a><a href="#materials">Cardboard or wood</a><a href="#pricing">Pricing</a><a href="#faq">FAQ</a><a href="#faq-privacy">Photo privacy</a><a href="mailto:{CFG["email"]}">Contact</a></div>
<div class="foot-links"><a href="{CFG["boardBooks"]}">Family Board Books</a><a href="{CFG["storybooks"]}">Family Storybooks</a><a href="{CFG["learnToRead"]}">Family Learn to Read</a></div>
<p class="small">&copy; <span data-year>2026</span> Family Jigsaw Puzzles &middot; familyjigsawpuzzles.com &middot; part of <a href="{CFG["umbrella"]}">Our Family Presents</a></p></div>
</div></footer>"""


def page(title, desc, path, body):
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{head(title, desc, path)}</head>
<body>
{header()}
<main>
{body}
</main>
{footer()}
<script src="{v("js/data.js")}"></script>
<script src="{v("js/region.js")}"></script>
<script src="{v("js/site.js")}"></script>
</body>
</html>
"""


# ---------- The example scene (our own drawing, never a customer photo) ----------
W, H = 600, 420


def person(x, y, s, top, skin, hair, style="short"):
    hairs = {
        "short": '<path d="M33 40c2-17 32-17 34 0-7-7-27-7-34 0z" fill="{h}"/>',
        "long": '<path d="M32 44c-2-22 38-22 36 0v22c-4-8-6-14-6-22-8-6-16-6-24 0 0 8-2 14-6 22z" fill="{h}"/>',
        "bun": '<path d="M34 40c2-15 30-15 32 0-6-6-26-6-32 0z" fill="{h}"/><circle cx="50" cy="22" r="8" fill="{h}"/>',
    }
    return (f'<g class="who" transform="translate({x} {y}) scale({s})">'
            f'<path class="body" d="M20 150 30 70q20-10 40 0l10 80z" fill="{top}"/>'
            f'<circle class="face" cx="50" cy="46" r="18" fill="{skin}"/>' + hairs[style].format(h=hair)
            + '<circle cx="43" cy="47" r="2" fill="#1E1A33"/><circle cx="57" cy="47" r="2" fill="#1E1A33"/>'
            '<path d="M44 55q6 5 12 0" stroke="#1E1A33" stroke-width="1.8" fill="none" stroke-linecap="round"/></g>')


FAMILY = ('<g class="family">'
          '<path class="splat" d="M160 250c-40-60 20-120 90-110 40-50 130-40 150 10 70-10 110 60 70 110 30 40-10 90-60 80-20 40-120 40-140 0-60 20-120-30-110-90z" fill="#FFC21A"/>'
          + person(170, 168, 1.45, "#16A6E3", "#F1CFB5", "#5a3a22", "short")
          + person(300, 160, 1.5, "#EE4B2B", "#E8B896", "#2b1d14", "long")
          + person(238, 232, 1.0, "#1FB45A", "#F1CFB5", "#8a5a2b", "bun")
          + '</g>')

BACKDROP_SVG = {
    "keep": '<rect width="600" height="420" fill="#DDF1F8"/><path d="M0 300q150-40 300-10t300-20v150H0z" fill="#9CCB8C"/>'
            '<circle cx="500" cy="80" r="34" fill="#FFE59A"/><path d="M60 300v-60m0 0c-24 0-30-40 0-50 30 10 24 50 0 50z" stroke="#7A5A3A" stroke-width="6" fill="#4FA65A"/>',
    "paris": '<rect width="600" height="420" fill="#FBD9C4"/><circle cx="470" cy="110" r="44" fill="#FFB27A"/>'
             '<path d="M0 330h600v90H0z" fill="#C9B79C"/>'
             '<path d="M0 330v-60h40v-20h30v20h40v-40h35v60h45v-30h40v70z" fill="#B88CB0" opacity=".7"/>'
             '<path d="M420 330l20-90 6-80 4-60 4 60 6 80 20 90h-18q-12-40-24 0z" fill="#5B4A63"/>'
             '<path d="M432 250h36M438 170h24" stroke="#5B4A63" stroke-width="6"/>'
             '<path d="M520 330v-50h40v-15h40v65z" fill="#B88CB0" opacity=".7"/>',
    "beach": '<rect width="600" height="420" fill="#BFE8FA"/><circle cx="480" cy="90" r="40" fill="#FFE07A"/>'
             '<path d="M0 260h600v60H0z" fill="#16A6E3"/><path d="M0 262q30-8 60 0t60 0 60 0 60 0 60 0 60 0 60 0 60 0 60 0 60 0" stroke="#fff" stroke-width="4" fill="none" opacity=".7"/>'
             '<path d="M0 310q300-30 600 0v110H0z" fill="#F4D9A0"/><path d="M60 300l60-90 10 90z" fill="#EE4B2B"/>',
    "snow": '<rect width="600" height="420" fill="#D7E6F5"/><path d="M0 300l120-170 90 110 90-160 120 150 70-80 110 150z" fill="#8FA6C4"/>'
            '<path d="M120 130l26 38-26-8-24 10zM300 80l30 50-30-10-28 12zM490 170l20 30-20-6-18 8z" fill="#fff"/>'
            '<path d="M0 320q300-50 600 0v100H0z" fill="#fff"/>'
            '<g fill="#fff"><circle cx="80" cy="60" r="3"/><circle cx="200" cy="40" r="2.5"/><circle cx="380" cy="70" r="3"/><circle cx="540" cy="50" r="2.5"/></g>',
    "space": '<rect width="600" height="420" fill="#1E1A33"/><g fill="#fff"><circle cx="40" cy="40" r="2"/><circle cx="120" cy="90" r="1.5"/><circle cx="210" cy="30" r="2"/><circle cx="380" cy="50" r="1.5"/><circle cx="560" cy="120" r="2"/><circle cx="520" cy="30" r="1.5"/><circle cx="90" cy="200" r="1.5"/></g>'
             '<circle cx="480" cy="110" r="46" fill="#8A3FD9"/><ellipse cx="480" cy="110" rx="78" ry="14" fill="none" stroke="#F2558C" stroke-width="6"/>'
             '<path d="M0 330q300-60 600 0v90H0z" fill="#9A97B0"/><circle cx="100" cy="370" r="16" fill="#7E7B96"/><circle cx="470" cy="360" r="22" fill="#7E7B96"/>',
    "jungle": '<rect width="600" height="420" fill="#CDEBC0"/><path d="M0 320q300-40 600 0v100H0z" fill="#5BAA4A"/>'
              '<g fill="#1FB45A"><path d="M0 0q90 60 40 180Q10 100 0 0z"/><path d="M600 0q-90 70-30 200Q600 110 600 0z"/><path d="M80 420q-40-120 40-200-10 100-40 200z"/><path d="M540 420q40-120-30-190 0 100 30 190z"/></g>'
              '<circle cx="520" cy="260" r="10" fill="#FF8A1F"/><path d="M60 120q20-10 30 4" stroke="#9A5B34" stroke-width="6" fill="none"/>',
}


def scene(backdrop="keep"):
    return "".join(f'<g class="bd bd-{k}"{"" if k == backdrop else " hidden"}>{svg}</g>' for k, svg in BACKDROP_SVG.items()) + FAMILY


FILTERS = """<defs>
<filter id="f-water" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency=".035" numOctaves="2" seed="3"/><feDisplacementMap in="SourceGraphic" scale="9"/><feGaussianBlur stdDeviation=".8"/></filter>
<filter id="f-paint"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="1" seed="5"/><feDisplacementMap in="SourceGraphic" scale="3"/></filter>
<pattern id="dots" width="8" height="8" patternUnits="userSpaceOnUse"><circle cx="4" cy="4" r="1.6" fill="#1E1A33" opacity=".22"/></pattern>
<linearGradient id="photo-light" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".6" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".18"/></linearGradient>
</defs>"""


def puzzle_svg(uid, cols, rows, lift=None, cls="", label="", backdrop="keep"):
    """The example scene cut into a cols x rows jigsaw. lift=(c, r) lifts one piece out of the picture."""
    cuts, vdir, hdir, cw, ch = jigsaw(cols, rows, W, H)
    extra = ""
    if lift:
        c, r = lift
        outline = piece_outline(c, r, cols, rows, vdir, hdir, cw, ch)
        extra = (f'<clipPath id="{uid}-lift"><path d="{outline}"/></clipPath>'
                 f'<path d="{outline}" fill="#1E1A33" opacity=".78"/>'
                 f'<g class="lifted" style="--tx:{-cw * .35:.0f}px;--ty:{-ch * .55:.0f}px">'
                 f'<g clip-path="url(#{uid}-lift)"><use href="#{uid}-pic"/></g><path d="{outline}" fill="none" stroke="#fff" stroke-width="2"/></g>')
    return (f'<svg class="puzzle {cls}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(label)}">{FILTERS.replace("id=\"", f"id=\"{uid}-")}'
            f'<g id="{uid}-pic" class="pic" style="--water:url(#{uid}-f-water);--paint:url(#{uid}-f-paint)">{scene(backdrop)}<rect class="sheen" width="{W}" height="{H}" fill="url(#{uid}-photo-light)"/>'
            f'<rect class="halftone" width="{W}" height="{H}" fill="url(#{uid}-dots)"/></g>'
            f'<path class="cuts" d="{cuts}" fill="none"/>{extra}</svg>')


# ---------- Sections ----------
def size_card(s):
    cols, rows = s["grid"]
    # A small cut grid to show how fine the pieces are, drawn at the puzzle's real proportions.
    w, h = 120, round(120 * s["h"] / s["w"])
    cuts = jigsaw(min(cols, 12), min(rows, 10), w, h, seed=s["pieces"])[0]
    return f"""<article class="size" style="--sc:{s["color"]}">
<svg class="size-pic" viewBox="0 0 {w} {h}" aria-hidden="true"><rect width="{w}" height="{h}" rx="4" fill="var(--sc)"/><path d="{cuts}" fill="none" stroke="#fff" stroke-opacity=".75" stroke-width="{1.6 if cols < 12 else 1}"/></svg>
<p class="size-n">{s["pieces"]:,}<small> pieces</small></p>
<p class="size-dim">{s["w"] / 10:g} × {s["h"] / 10:g} cm</p>
<p class="size-who">{e(s["who"])}</p>
<p class="muted small">{e(s["line"])}</p>
<dl class="size-prices"><div><dt>Cardboard</dt><dd>{money(s["card"])}</dd></div></dl>
<a class="stage-cta" href="#join" data-want="{s["id"]}">Notify me &rarr;</a>
</article>"""


def looks():
    tchips = "".join(f'<button type="button" class="chip-btn" data-look="{t["id"]}" aria-pressed="{"true" if i == 0 else "false"}">{e(t["name"])}</button>' for i, t in enumerate(TREATMENTS))
    bchips = "".join(f'<button type="button" class="chip-btn" data-bd="{b["id"]}" aria-pressed="{"true" if i == 0 else "false"}">{e(b["name"])}</button>' for i, b in enumerate(BACKDROPS))
    lines = "".join(f'<p class="look-line" data-line="{t["id"]}"{"" if i == 0 else " hidden"}>{e(t["line"])}</p>' for i, t in enumerate(TREATMENTS))
    return f"""<section id="looks" class="section" style="padding-top:0"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Looks and backdrops</p><h2>Keep your photo, or make it magic</h2><p class="lede">Use your photo just as it is, or have us draw your family in one of our cartoon styles. Then, if you like, swap the background for somewhere new, like Paris or outer space.</p></div>
<div class="looks">
<div class="looks-pic">{puzzle_svg("lk", 6, 4, cls="look-photo", label="Example puzzle: our drawing of a family, in the chosen look and backdrop")}
<p class="small">Our example family. Your puzzle shows your own photo.</p></div>
<div class="looks-ctl">
<div class="field"><span class="ctl-label">1. Choose a look</span><div class="chips" role="group" aria-label="Look">{tchips}</div>{lines}</div>
<div class="field"><span class="ctl-label">2. Choose a backdrop</span><div class="chips" role="group" aria-label="Backdrop">{bchips}</div>
<p class="small">Backdrops work best with photos of people. Scenery photos keep their own background.</p></div>
<div class="field"><span class="ctl-label">3. See it before you pay</span><p class="muted">We show you a free preview of your picture with the look and backdrop you chose. Change it as often as you like until it's right.</p></div>
</div></div>
</div></section>"""


def wood_card(w):
    return f"""<article class="wood-size"><p class="size-n">{e(w["name"])}</p><p class="size-dim">{w["w"] / 10:g} × {w["h"] / 10:g} cm</p>
<p class="muted small">{e(w["line"])}</p><p class="price">{money(w["price"])}</p>
<a class="stage-cta" href="#join" data-want="{w["id"]}" data-mat="wood">Notify me &rarr;</a></article>"""


def materials():
    cards = []
    for m in MATERIALS:
        badge = ""
        pts = "".join(f"<li>{e(p)}</li>" for p in m["points"])
        cards.append(f"""<article class="mat mat-{m["id"]}">{badge}
<svg class="mat-pic" viewBox="0 0 120 80" aria-hidden="true">{MAT_SVG[m["id"]]}</svg>
<h3>{e(m["name"])}</h3><p class="muted">{e(m["line"])}</p><ul class="ticks">{pts}</ul></article>""")
    return f"""<section id="materials" class="section" style="padding-top:0"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Cardboard or wood</p><h2>Two ways to make it</h2><p class="lede">Every puzzle is printed to order, one at a time, and posted to you or straight to the person you're giving it to.</p></div>
<div class="mats">{"".join(cards)}</div>
<h3 class="sub-h" id="wood">Wooden puzzle sizes</h3>
<div class="woods">{"".join(wood_card(w) for w in WOOD)}</div>
<p class="note">Wooden puzzles are made to order and take a little longer to reach you: allow 2 to 4 weeks.</p>
</div></section>"""


_P = "M10 10h40v12a8 8 0 1 0 0 16v12H10z"
MAT_SVG = {
    "card": f'<rect x="4" y="6" width="112" height="68" rx="8" fill="#16A6E3"/><path d="{_P}" transform="translate(30 4)" fill="#fff" opacity=".9"/><path d="{_P}" transform="translate(64 14) rotate(8 30 30)" fill="#FFC21A"/>',
    "wood": '<rect x="4" y="6" width="112" height="68" rx="8" fill="#C99A6B"/><g stroke="#A97C50" stroke-width="2" fill="none" opacity=".7"><path d="M4 22q60-8 112 0"/><path d="M4 40q60 8 112 0"/><path d="M4 58q60-6 112 0"/></g>'
            f'<path d="{_P}" transform="translate(34 6)" fill="#E2BC8E" stroke="#8A6238" stroke-width="2"/><path d="M84 30c6-10 18-2 10 8l-10 10-10-10c-8-10 4-18 10-8z" fill="#EE4B2B"/>',
}


FAQ = [
    ("How many pieces should I choose?", "For children aged 3 to 5, 30 big pieces is plenty. Most children from 6 enjoy 110 pieces, and 252 pieces makes a lovely evening for older children and families. 500 and 1,000 pieces are for keen puzzlers. Each size shows the finished size in centimetres, so you can check it fits your table."),
    ("What makes a good photo for a puzzle?", "A sharp, well-lit photo taken on a modern phone works well. Faces should be clear and not too small. For the cartoon looks and backdrops, a photo of people standing or sitting together is best. Busy, detailed pictures make the most fun puzzles, and big areas of plain sky make the hardest."),
    ("What are the looks?", "You can keep your photo as it is, or we draw it in one of our cartoon styles: Cartoon Splash, Painted Splash, Watercolour, Comic Pop or Storybook. They're the same styles families choose for our Family Board Books."),
    ("How do backdrops work?", "We draw your family into a new scene, such as the streets of Paris, a sunny beach, snowy mountains, a jungle or outer space. You see a free preview first and can try another backdrop before you order."),
    ("Cardboard or wood?", "Cardboard puzzles have a glossy photo finish, come in a gift tin with your picture on the lid, and are made in the UK in a few days. Wooden puzzles are laser cut from 3 mm wood, come in a keepsake box and last for years. They cost a little more and take 2 to 4 weeks to arrive."),
    ("Can you send it straight to the person it's for?", "Yes. Just enter their address at checkout. We never put prices in the parcel."),
    ("Where are my photos stored?", "In private, encrypted storage in the European Union, in Cloudflare's EU data centres. Before a photo leaves your phone or computer, we shrink it and remove hidden details such as where it was taken. Your photos are never published.", "faq-privacy"),
    ("How long do you keep my photos?", "Free previews are deleted after 14 days if you don't order. Original photos are deleted once your puzzle is printed. You can delete everything yourself at any time. We never use your photos for advertising or to train AI."),
    ("Where do you deliver?", "The UK and Europe. We'll confirm delivery times and costs when ordering opens."),
]


def faq_html():
    return "".join(f'<details{" id=" + chr(34) + q[2] + chr(34) if len(q) > 2 else ""}><summary>{e(q[0])}</summary><p>{e(q[1])}</p></details>' for q in FAQ)


def pricing():
    rows = "".join(f'<tr><td>Cardboard</td><td><b>{s["pieces"]:,} pieces</b></td><td>{s["w"] / 10:g} × {s["h"] / 10:g} cm</td><td>{e(s["who"])}</td>'
                   f'<td class="price">{money(s["card"])}</td></tr>' for s in SIZES)
    rows += "".join(f'<tr><td>Wood</td><td><b>{e(w["name"])}</b></td><td>{w["w"] / 10:g} × {w["h"] / 10:g} cm</td><td>All ages</td>'
                    f'<td class="price">{money(w["price"])}</td></tr>' for w in WOOD)
    return f"""<section id="pricing" class="section" style="padding-top:0"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Pricing</p><h2>One price, every look included</h2><p class="lede">Your photo as it is, any cartoon look and any backdrop all cost the same. Founding families on our list get {DISCOUNT}% off their first puzzle.</p></div>
<div class="table-wrap"><table><thead><tr><th>Material</th><th>Puzzle</th><th>Finished size</th><th>Good for</th><th>Price</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="note">Launch prices, to be confirmed before ordering opens. Delivery costs are shown at checkout.</p>
</div></section>"""


def want_options():
    opts = ['<option value="">Not sure yet</option>']
    opts += [f'<option value="{s["id"]}">Cardboard, {s["pieces"]:,} pieces ({s["w"] / 10:g} × {s["h"] / 10:g} cm)</option>' for s in SIZES]
    opts += [f'<option value="{w["id"]}">Wood, {e(w["name"])} ({w["w"] / 10:g} × {w["h"] / 10:g} cm)</option>' for w in WOOD]
    return "".join(opts)


def join_band():
    looks = "".join(f'<option value="{t["id"]}">{e(t["name"])}</option>' for t in TREATMENTS)
    return f"""<section class="section" style="padding-top:0"><div class="wrap">
<div class="band" id="join">
<div style="display:grid;gap:14px"><p class="eyebrow" style="color:#CFCADE">Founding families</p><h2>Be first to puzzle, and get {DISCOUNT}% off</h2><p>Our first puzzles open for orders soon. Join the list and we'll email you a {DISCOUNT}% founding-family discount for your first puzzle.</p></div>
<form class="form" data-signup="waitlist" novalidate>
<div class="field"><label for="w-email" style="color:#fff">Email</label><div class="form-row"><input id="w-email" name="email" type="email" autocomplete="email" placeholder="name@example.com" required><button class="btn red" type="submit">Join the list</button></div></div>
<div class="field"><label for="w-want" style="color:#fff">Which puzzle?</label><select id="w-want" name="size">{want_options()}</select></div>
<div class="field"><label for="w-look" style="color:#fff">Which look?</label><select id="w-look" name="look">{looks}<option value="unsure">Not sure yet</option></select></div>
<p class="form-msg" role="status" style="color:#fff"></p>
</form></div></div></section>"""


# ---------- Home ----------
def home():
    sizes = "".join(size_card(s) for s in SIZES)
    body = f"""
<section class="hero"><div class="wrap hero-grid split">
<div class="hero-copy">
<h1 class="wordmark">Family Jigsaw Puzzles</h1>
<p class="lede">Your favourite family photo as a jigsaw puzzle. Keep it as it is, or have us draw it as a cartoon and pop the family into Paris, the seaside or outer space.</p>
<div class="hero-cta"><a class="btn red" href="#join">Join the list for {DISCOUNT}% off</a><a class="btn ghost" href="#looks">See the looks</a></div>
<p class="small">From 30 to 1,000 pieces, in cardboard or wood. Made to order, delivered across the UK and Europe.</p>
</div>
<figure class="hero-pic">{puzzle_svg("hero", 6, 4, lift=(2, 2), cls="look-splash", label="Example puzzle: our drawing of a family in Cartoon Splash style, with one piece lifted out")}</figure>
</div></section>

<section id="sizes" class="section" style="padding-top:28px"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Sizes</p><h2>From 30 chunky pieces to 1,000</h2><p class="lede">Pick a size to suit who's doing it. These are our cardboard puzzles; <a href="#wood">wooden puzzles</a> come in three sizes of their own.</p></div>
<div class="sizes">{sizes}</div>
</div></section>

{looks()}

{materials()}

<section id="how" class="section" style="padding-top:0"><div class="wrap">
<div class="sec-head"><p class="eyebrow">How it works</p><h2>From photo to puzzle</h2></div>
<div class="steps four">
<div class="step"><h3>Add your photo</h3><p>Any photo of your family, a pet or a favourite place, straight from your phone.</p></div>
<div class="step"><h3>Pick a look</h3><p>Keep the photo, or choose a cartoon style and a backdrop such as Paris.</p></div>
<div class="step"><h3>Check the preview</h3><p>See your picture free before you order, and change it until it's right.</p></div>
<div class="step"><h3>We make it</h3><p>Choose your size and cardboard or wood. We print, cut and post it to you.</p></div>
</div></div></section>

<section class="section" style="padding-top:0"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Why families choose us</p><h2>A present they'll do together</h2></div>
<div class="why">
<div class="why-item" style="--wc:var(--red)"><h3>Made for families</h3><p>Sizes for every age, from toddlers' 30 big pieces to grandparents' 1,000.</p></div>
<div class="why-item" style="--wc:var(--sky)"><h3>More than a photo</h3><p>The same cartoon styles as our board books, and backdrops that take you anywhere.</p></div>
<div class="why-item" style="--wc:var(--leaf)"><h3>See it first</h3><p>A free preview of your picture before you pay a penny.</p></div>
<div class="why-item" style="--wc:var(--grape)"><h3>Your photos stay private</h3><p>Stored encrypted in the EU, never published, deleted once your puzzle is made.</p></div>
</div></div></section>

{pricing()}

<section id="faq" class="section" style="padding-top:0"><div class="wrap">
<div class="sec-head"><p class="eyebrow">Questions</p><h2>Good to know</h2></div>
<div class="faq">{faq_html()}</div></div></section>

{join_band()}

<section class="section" style="padding-top:0"><div class="wrap"><div class="sister">
<div style="display:grid;gap:6px"><h3>Books starring your family too</h3><p>Our sister site Family Board Books turns your photos into sturdy board books for little ones, in the same cartoon styles.</p></div>
<a class="btn ghost" href="{CFG["boardBooks"]}">Visit Family Board Books</a></div></div></section>
"""
    return page("Family Jigsaw Puzzles: personalised photo jigsaws, cardboard or wood",
                "Jigsaw puzzles made from your family photos, as they are or as cartoons with backdrops such as Paris. 30 to 1,000 pieces, cardboard or wood, delivered across the UK and Europe.",
                "", body)


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT / "assets", DIST / "assets")
    (DIST / "assets/favicon.svg").write_text(FAVICON)
    pages = {"index.html": home()}
    for name, html in pages.items():
        (DIST / name).write_text(html)
    (DIST / "CNAME").write_text(DOMAIN + "\n")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    urls = "".join(f"<url><loc>{SITE}/{'' if n == 'index.html' else n}</loc></url>" for n in pages)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    print("built", len(pages), "pages")


if __name__ == "__main__":
    main()
