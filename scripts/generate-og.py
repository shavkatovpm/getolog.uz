#!/usr/bin/env python3
"""Har bir sahifa uchun alohida OG rasm (1200x630) yasaydi.

Sarlavhalarni `dist/` dagi tayyor HTML'dan o'qiydi, ya'ni rasmlar sahifa
kontenti bilan doim mos bo'ladi. Ishlatish:

    npx astro build          # avval sayt yig'ilsin
    python3 scripts/generate-og.py
    npx astro build          # rasmlar public/ dan dist/ ga ko'chsin

Yangi sahifa qo'shilganda shu ketma-ketlikni qayta bajaring.
"""

import html
import os
import re
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
OUT = os.path.join(ROOT, "public", "og")
LOGO = os.path.join(ROOT, "public", "logo.png")

W, H = 1200, 630
BG = (240, 241, 243)
INK = (26, 29, 34)
MUTED = (102, 110, 122)
ACCENT = (91, 107, 122)
CARD = (231, 233, 236)

BOLD_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
REGULAR_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def pick_font(candidates, size):
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    raise SystemExit("Mos shrift topilmadi: " + ", ".join(candidates))


def slug_for(pathname: str) -> str:
    """/ru/blog/x/ -> ru-blog-x, / -> home. Layout.astro dagi mantiq bilan bir xil."""
    parts = [p for p in pathname.strip("/").split("/") if p]
    return "-".join(parts) if parts else "home"


def wrap(draw, text, font, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def build(pathname, title, category, logo_img):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # chap tomonda urg'u chizig'i
    draw.rectangle([0, 0, 10, H], fill=ACCENT)

    pad = 80
    # brend qatori
    if logo_img is not None:
        img.paste(logo_img, (pad, 62), logo_img)
        brand_x = pad + logo_img.width + 18
    else:
        brand_x = pad
    f_brand = pick_font(BOLD_CANDIDATES, 38)
    draw.text((brand_x, 70), "Getolog", font=f_brand, fill=INK)

    # kategoriya chipi
    top = 190
    if category:
        f_cat = pick_font(BOLD_CANDIDATES, 22)
        tw = draw.textlength(category.upper(), font=f_cat)
        draw.rounded_rectangle([pad, top, pad + tw + 40, top + 44], radius=22, fill=CARD)
        draw.text((pad + 20, top + 10), category.upper(), font=f_cat, fill=ACCENT)
        top += 74

    # sarlavha
    size = 62
    while size >= 38:
        f_title = pick_font(BOLD_CANDIDATES, size)
        lines = wrap(draw, title, f_title, W - pad * 2 - 20)
        line_h = int(size * 1.26)
        if len(lines) * line_h <= H - top - 130:
            break
        size -= 4
    y = top
    for line in lines[:5]:
        draw.text((pad, y), line, font=f_title, fill=INK)
        y += line_h

    # pastki qator
    f_foot = pick_font(REGULAR_CANDIDATES, 28)
    draw.line([pad, H - 108, W - pad, H - 108], fill=(210, 213, 218), width=2)
    draw.text((pad, H - 78), "getolog.uz" + pathname.rstrip("/"), font=f_foot, fill=MUTED)

    return img


def main():
    if not os.path.isdir(DIST):
        raise SystemExit("dist/ topilmadi — avval `npx astro build` bajaring.")

    os.makedirs(OUT, exist_ok=True)

    logo_img = None
    if os.path.exists(LOGO):
        logo_img = Image.open(LOGO).convert("RGBA").resize((56, 56), Image.LANCZOS)
        mask = Image.new("L", (56, 56), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, 55, 55], radius=16, fill=255)
        logo_img.putalpha(mask)

    made = 0
    for dirpath, _, filenames in os.walk(DIST):
        if "index.html" not in filenames:
            continue
        rel = os.path.relpath(dirpath, DIST)
        pathname = "/" if rel == "." else "/" + rel.replace(os.sep, "/") + "/"

        raw = open(os.path.join(dirpath, "index.html"), encoding="utf-8").read()
        m = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S)
        if m:
            title = re.sub(r"<[^>]+>", "", m.group(1))
        else:
            t = re.search(r"<title>(.*?)</title>", raw, re.S)
            title = t.group(1) if t else "Getolog"
        title = html.unescape(re.sub(r"\s+", " ", title)).strip()
        title = re.sub(r"\s*[—|]\s*Getolog\s*$", "", title)

        c = re.search(r'class="(?:lp__category|article-category|blog-card__category)"[^>]*>(.*?)<', raw, re.S)
        category = html.unescape(c.group(1)).strip() if c else ""

        out_path = os.path.join(OUT, slug_for(pathname) + ".png")
        build(pathname, title, category, logo_img).save(out_path, "PNG", optimize=True)
        made += 1
        print("  ", slug_for(pathname) + ".png", "<-", pathname)

    print(f"\n{made} ta OG rasm yasaldi: public/og/")


if __name__ == "__main__":
    sys.exit(main())
