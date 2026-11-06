"""Build the Fab listing images (1920x1080 PNG) from the screenshots in Shots/ into Images/.

    python render.py

Needs Chrome or Edge, and network access for Google Fonts. A screenshot that isn't in Shots/ yet is drawn as a grey
stand-in and the image is written as .draft.png, which git ignores. Upload only the images without .draft.

Layout rules: 72 px margins; headlines in Montserrat Black, three words or fewer a line; one accent per image, taken
from the dots of the plugin icon; flat shapes, no gradients; screenshots enlarged at most 1.3x.
"""

import html
import pathlib
import struct
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
SHOTS = HERE / "Shots"
OUT = HERE / "Images"
LOGO = (HERE / "Brand" / "KhaosSystems.svg").as_uri()
ICON = (HERE / "Brand" / "Icon.svg").as_uri()
BROWSER = next(p for p in [
    pathlib.Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    pathlib.Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
] if p.exists())

RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE = "#E5484D", "#F5A623", "#F2D94E", "#46B95F", "#3E8BFF", "#A05BEF"
INK = "#141318"
FLAT = "#17161B"
BLEED = "border-radius:6px 0 0 6px"
MAX_SCALE = 1.3

# Points on the screenshots, in screenshot pixels. Measure them again whenever a shot is retaken.
COVER_ASSETS_CROP = (235, 40, 540, 590)  # cb-props.png: the document among the assets
COVER_DOC_CROP = (393, 36, 1104, 708)    # docs-props.png: the page and its outline
README_TILE = (455, 134, 98, 162)        # cb-props.png: the document's tile
BESIDE_CROP = (235, 40, 1065, 590)       # cb-props.png: the folder's contents
EDIT_CROP = (393, 36, 905, 700)          # docs-edit.png: the source and the live preview
# docs-overview.png: what each callout outlines, as x, y, w, h.
OVERVIEW = {"search": (8, 47, 280, 26), "favorites": (3, 88, 320, 66), "project": (3, 154, 320, 330), "plugins": (3, 484, 320, 154),
            "toolbar": (936, 44, 296, 32), "outline": (1086, 88, 150, 170)}
CREATE_ROW = 307                         # create-row.png: the middle of the Create Document row
TILE_CROP = (235, 120, 440, 200)         # create-done.png: the new document's tile
NEW_DOC_CROP = (393, 36, 718, 280)       # docs-new.png: the new document

SLIDES = [
    {"id": "00-cover", "layout": "cover", "claim": ("Real .md files", "No uassets"), "accent": YELLOW},
    {"id": "01-beside-assets", "layout": "beside", "title": ("Docs", "beside", "assets"), "note": "Double-click to read", "accent": BLUE},
    {"id": "02-plain-text", "layout": "plain", "title": ("Plain text", "in your repo"), "accent": GREEN},
    {"id": "03-live-preview", "layout": "live", "title": ("Edit it", "see it live"), "accent": PURPLE},
    {"id": "04-one-window", "layout": "window", "accent": YELLOW},
    {"id": "05-new-document", "layout": "create", "title": ("Right-click", "Create Document", "Start writing"), "accent": ORANGE},
    {"id": "06-nothing-to-register", "layout": "plugins", "title": ("Nothing", "to", "register"),
     "note": "Your project and its plugins", "accent": RED},
]

# The sample project's Environment/Props folder, as it sits on disk.
LISTING_FOLDER = "Content/Environment/Props"
LISTING = ["Materials/", "MaterialSphere.uasset", "README.md", "SM_Bush.uasset", "SM_Chair.uasset", "SM_CornerFrame.uasset", "SM_Couch.uasset",
           "SM_Door.uasset", "SM_DoorFrame.uasset", "SM_GlassWindow.uasset", "SM_Lamp_Ceiling.uasset", "SM_Lamp_Wall.uasset"]
SOURCE_FILE = "Content/Environment/Props/README.md"
SOURCE_LINES = (SHOTS / "sample" / "Content" / "Environment" / "Props" / "README.md").read_text(encoding="utf-8").splitlines()[:15]


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;700&display=block');
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 1920px; height: 1080px; overflow: hidden; }
body { position: relative; background: #111; color: #fff; font-family: 'Inter', sans-serif; -webkit-font-smoothing: antialiased; }
.display { font-family: 'Montserrat', sans-serif; font-weight: 900; text-transform: uppercase; letter-spacing: -0.01em; line-height: 0.92; }
.missing { background: #2B2F35; display: flex; align-items: center; justify-content: center; color: #6E747C;
  font-size: 28px; font-weight: 600; }
.shot { position: absolute; border-radius: 6px; box-shadow: 0 40px 100px rgba(0,0,0,0.6), 0 0 0 1px #000; background-repeat: no-repeat; }
.ks { position: absolute; height: 60px; filter: drop-shadow(0 2px 10px rgba(0,0,0,.6)); }
.head { position: absolute; font-size: 112px; text-shadow: 0 6px 30px rgba(0,0,0,.45); }
em { font-style: normal; display: block; }
.step { position: absolute; width: 64px; height: 64px; border-radius: 50%; color: #fff; font: 900 38px Montserrat;
  display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 18px rgba(0,0,0,.45); }
.code { position: absolute; background: #16161A; border-radius: 6px; box-shadow: 0 40px 100px rgba(0,0,0,0.45), 0 0 0 1px #000;
  overflow: hidden; font: 500 24px 'JetBrains Mono', monospace; color: #C9C9CF; }
.code .bar { height: 54px; background: #0E0E11; display: flex; align-items: center; padding: 0 22px; font-weight: 700; color: #fff; font-size: 20px; }
.code .line { height: 45px; display: flex; align-items: center; padding: 0 22px; white-space: pre; }
.code .add { background: #1B2E22; color: #D8F2DF; }
.note { position: absolute; font: 700 30px Montserrat; letter-spacing: .02em; text-transform: uppercase; line-height: 1.25; }
.flat .shot, .flat .code { box-shadow: 0 12px 28px rgba(0,0,0,.28), 0 0 0 1px #000; }
"""


class Page:
    """One image: collects its HTML and remembers whether a stand-in was used."""

    def __init__(self):
        self.parts, self.draft = [], False
        self.body = ""

    def add(self, *parts):
        self.parts.extend(parts)

    def solid(self, colour):
        self.add(f'<div style="position:absolute;inset:0;background:{colour}"></div>')

    def panel(self, name, left=None, top=0, scale=1.0, right=None, crop=None, extra=""):
        """A screenshot, or the crop (x, y, w, h) of one, at `scale`, its left edge at `left` or its right edge at
        `right`. Returns its box and scale as (left, top, width, height, scale, crop x, crop y)."""
        scale = min(scale, MAX_SCALE)
        path = SHOTS / name
        if not path.exists():
            self.draft = True
            w, h = (crop[2], crop[3]) if crop else (800, 600)
            width, height = w * scale, h * scale
            left = right - width if right is not None else left
            self.add(f'<div class="shot missing" style="left:{left}px;top:{top}px;width:{width}px;height:{height}px">{name}</div>')
            return left, top, width, height, scale, *(crop[:2] if crop else (0, 0))
        full_w, full_h = png_size(path)
        x, y, w, h = crop or (0, 0, full_w, full_h)
        width, height = w * scale, h * scale
        left = right - width if right is not None else left
        self.add(f'<div class="shot" style="left:{left}px;top:{top}px;width:{width}px;height:{height}px;'
                 f'background-image:url(\'{path.as_uri()}\');background-size:{full_w * scale}px {full_h * scale}px;'
                 f'background-position:{-x * scale}px {-y * scale}px;{extra}"></div>')
        return left, top, width, height, scale, x, y

    def logo(self, style):
        self.add(f'<img class="ks" style="{style}" src="{LOGO}">')

    def headline(self, title, left, top, size, first, second):
        lines = "".join(f'<em style="color:{first if i == 0 else second}">{html.escape(line)}</em>' for i, line in enumerate(title))
        self.add(f'<h1 class="display head" style="left:{left}px;top:{top}px;font-size:{size}px;text-shadow:none">{lines}</h1>')

    def step(self, number, left, top, colour=INK):
        self.add(f'<div class="step" style="left:{left}px;top:{top}px;background:{colour}">{number}</div>')

    def rows(self, lines, colour, left, top, size):
        rows = "".join(
            f'<div style="display:flex;align-items:center;gap:26px;margin-bottom:22px">'
            f'<div class="step" style="position:relative;flex:none;background:{colour}">{n}</div>'
            f'<span>{html.escape(line)}</span></div>'
            for n, line in enumerate(lines, 1))
        self.add(f'<h1 class="display head" style="left:{left}px;top:{top}px;font-size:{size}px;line-height:1;text-shadow:none">{rows}</h1>')

    def html(self):
        return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head>"
                f"<body class='{self.body}'>{''.join(self.parts)}</body></html>")


def to_page(box, x, y):
    """A point on a screenshot, in screenshot pixels, as page coordinates."""
    left, top, _, _, scale, cx, cy = box
    return left + (x - cx) * scale, top + (y - cy) * scale


def outline(page, box, rect, colour, width=5):
    x, y = to_page(box, rect[0], rect[1])
    scale = box[4]
    page.add(f'<div style="position:absolute;left:{x - 4}px;top:{y - 4}px;width:{rect[2] * scale + 8}px;height:{rect[3] * scale + 8}px;'
             f'border:{width}px solid {colour};border-radius:8px"></div>')
    return x, y, rect[2] * scale, rect[3] * scale


def cover(page, slide):
    """The document in the Content Browser, and the page it opens."""
    accent = slide["accent"]
    page.solid(FLAT)
    top = 300
    box = page.panel("cb-props.png", left=72, top=top, scale=1.2, crop=COVER_ASSETS_CROP)
    outline(page, box, README_TILE, accent)
    page.panel("docs-props.png", right=1920, top=top, scale=1.0, crop=COVER_DOC_CROP, extra=BLEED)
    claim = " &nbsp;".join(html.escape(line) + "." for line in slide["claim"])
    page.add(f'<div style="position:absolute;left:72px;top:48px;display:flex;align-items:center;gap:36px">'
             f'<img src="{ICON}" style="width:150px">'
             f'<div><h1 class="display" style="font-size:132px;white-space:nowrap">Khaos Docs</h1>'
             f'<div class="display" style="font-size:46px;margin-top:14px;color:{accent}">{claim}</div></div></div>')
    page.logo("right:72px;top:60px")


def beside(page, slide):
    accent = slide["accent"]
    page.solid(accent)
    box = page.panel("cb-props.png", right=1920 - 72, top=(1080 - BESIDE_CROP[3] * 1.2) / 2, scale=1.2, crop=BESIDE_CROP)
    outline(page, box, README_TILE, "#fff")
    page.headline(slide["title"], 72, 330, 96, INK, "#fff")
    page.add(f'<div class="note" style="left:72px;top:620px;color:{INK};width:420px">{html.escape(slide["note"])}</div>')
    page.logo("left:72px;bottom:72px;filter:brightness(0)")


def code(page, left, top, width, height, title, lines, highlight=()):
    rows = "".join(f'<div class="line{" add" if text in highlight else ""}">{html.escape(text) or "&nbsp;"}</div>' for text in lines)
    page.add(f'<div class="code" style="left:{left}px;top:{top}px;width:{width}px;height:{height}px">'
             f'<div class="bar">{html.escape(title)}</div>{rows}</div>')


def plain(page, slide):
    page.body = "flat"
    page.solid(slide["accent"])
    page.headline(slide["title"], 72, 60, 96, INK, "#fff")
    top, height = 279, 729
    code(page, 72, top, 620, height, LISTING_FOLDER, LISTING, highlight=("README.md",))
    code(page, 716, top, 1132, height, SOURCE_FILE, SOURCE_LINES)
    page.logo("right:72px;top:60px;filter:brightness(0)")


def live(page, slide):
    page.solid(slide["accent"])
    scale = 1.1
    page.panel("docs-edit.png", right=1920 - 72, top=(1080 - EDIT_CROP[3] * scale) / 2, scale=scale, crop=EDIT_CROP)
    page.headline(slide["title"], 72, 400, 96, INK, "#fff")
    page.logo("left:72px;bottom:72px;filter:brightness(0)")


def window(page, slide):
    """The Documentation window with what's in it called out, like the sister plugin's overview."""
    accent = slide["accent"]
    page.solid(FLAT)
    box = page.panel("docs-overview.png", left=300, top=90, scale=1.0)
    callouts = [("Search", "search", "left"), ("Favorites", "favorites", "left"), ("Project", "project", "left"), ("Plugins", "plugins", "left"),
                ("Read or edit", "toolbar", "right"), ("Outline", "outline", "right")]
    svg = ['<svg style="position:absolute;left:0;top:0" width="1920" height="1080">']
    for text, key, side in callouts:
        rx, ry, rw, rh = OVERVIEW[key]
        x, y = to_page(box, rx, ry)
        middle = y + rh / 2
        edge = box[0] if side == "left" else box[0] + box[2]
        end = edge - 40 if side == "left" else edge + 40
        tx, anchor = (end - 16, "end") if side == "left" else (end + 16, "start")
        svg.append(f'<rect x="{x}" y="{y}" width="{rw}" height="{rh}" rx="5" fill="none" stroke="{accent}" stroke-width="3"/>'
                   f'<line x1="{edge}" y1="{middle}" x2="{end}" y2="{middle}" stroke="#fff" stroke-width="3"/>'
                   f'<circle cx="{edge}" cy="{middle}" r="9" fill="{accent}" stroke="#fff" stroke-width="3"/>'
                   f'<text x="{tx}" y="{middle + 12}" text-anchor="{anchor}" fill="#fff" '
                   f'style="font:900 34px Montserrat;text-transform:uppercase">{html.escape(text)}</text>')
    page.add("".join(svg) + "</svg>")
    page.logo("right:72px;bottom:72px")


def create(page, slide):
    """A new document as numbered steps: the menu, the tile, the page."""
    page.body = "flat"
    page.solid(slide["accent"])
    page.rows(slide["title"], INK, 72, 340, 52)
    menu = page.panel("create-row.png", left=800, top=190, scale=1.3)
    _, y = to_page(menu, 0, CREATE_ROW)
    page.step(2, 800 - 76, y - 32)
    page.panel("create-done.png", left=1130, top=190, scale=1.3, crop=TILE_CROP)
    page.panel("docs-new.png", left=1130, top=510, scale=1.0, crop=NEW_DOC_CROP)
    page.step(3, 1130 - 32, 510 - 28)
    page.logo("left:72px;bottom:72px;filter:brightness(0)")


def plugins(page, slide):
    page.solid(slide["accent"])
    page.panel("docs-plugin.png", right=1920 - 72, top=90, scale=1.0)
    page.headline(slide["title"], 72, 340, 96, INK, "#fff")
    page.add(f'<div class="note" style="left:72px;top:630px;color:{INK};width:440px">{html.escape(slide["note"])}</div>')
    page.logo("left:72px;bottom:72px;filter:brightness(0)")


LAYOUTS = {"cover": cover, "beside": beside, "plain": plain, "live": live, "window": window, "create": create, "plugins": plugins}


def render(slide):
    page = Page()
    LAYOUTS[slide["layout"]](page, slide)
    name = f"KhaosDocs-{slide['id']}{'.draft' if page.draft else ''}.png"
    target = OUT / name
    target.unlink(missing_ok=True)
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as work:
        source = pathlib.Path(work) / "page.html"
        source.write_text(page.html(), encoding="utf-8")
        # A fresh profile each time: a browser already running on the profile takes the command over.
        subprocess.run([
            str(BROWSER), "--headless=new", f"--user-data-dir={pathlib.Path(work) / 'profile'}", "--no-first-run",
            "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1", "--allow-file-access-from-files",
            "--window-size=1920,1080", "--virtual-time-budget=8000", f"--screenshot={target}", source.as_uri(),
        ], check=True, capture_output=True)
    if not target.exists():
        raise RuntimeError(f"{BROWSER.stem} wrote no {name}")
    print(name)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("KhaosDocs-*.png"):
        old.unlink()
    for slide in SLIDES:
        render(slide)
