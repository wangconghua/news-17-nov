#!/usr/bin/env python3
"""Render entry.png — one image summing up the world news of
Tuesday 17 November 2026. Pure PIL vector drawing + Noto Sans text,
so every glyph stays crisp and legible (no AI image generation)."""

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
BG = (247, 243, 234)        # off-white newsprint
NAVY = (22, 35, 63)         # header band
GOLD = (201, 162, 75)       # header rule / kicker
PANEL = (255, 255, 255)
INK = (24, 28, 38)          # headline ink
GREY = (88, 94, 108)        # summary ink
FOOT = (120, 124, 134)

FONT_DIR = "/usr/share/fonts/truetype/noto"
F_BLACK = f"{FONT_DIR}/NotoSans-Black.ttf"
F_BOLD = f"{FONT_DIR}/NotoSans-Bold.ttf"
F_REG = f"{FONT_DIR}/NotoSans-Regular.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
def icon_bridge(d, cx, cy, s, col):
    # deck + arch + pillars, drawn in white inside the badge
    d.line([(cx - s, cy + s * 0.45), (cx + s, cy + s * 0.45)], fill=col, width=5)
    d.arc([cx - s, cy - s * 0.9, cx + s, cy + s * 0.9], 180, 360, fill=col, width=5)
    for px in (-s * 0.55, 0, s * 0.55):
        d.line([(cx + px, cy - s * 0.15), (cx + px, cy + s * 0.45)],
               fill=col, width=4)


def icon_drone(d, cx, cy, s, col):
    # quadcopter: body + 4 rotor arms
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        d.line([(cx, cy), (cx + dx * s, cy + dy * s * 0.7)], fill=col, width=4)
        d.ellipse([cx + dx * s - 9, cy + dy * s * 0.7 - 4,
                   cx + dx * s + 9, cy + dy * s * 0.7 + 4], fill=col)
    d.ellipse([cx - 11, cy - 8, cx + 11, cy + 8], fill=col)


def icon_summit(d, cx, cy, s, col):
    # three flags on poles
    for i, px in enumerate((-s * 0.7, 0, s * 0.7)):
        d.line([(cx + px, cy - s * 0.8), (cx + px, cy + s * 0.8)],
               fill=col, width=4)
        d.polygon([(cx + px, cy - s * 0.8), (cx + px + s * 0.55, cy - s * 0.55),
                   (cx + px, cy - s * 0.3)], fill=col)


def icon_quad(d, cx, cy, s, col):
    # four people: head + shoulders
    for px in (-s * 0.75, -s * 0.25, s * 0.25, s * 0.75):
        d.ellipse([cx + px - 8, cy - s * 0.75, cx + px + 8, cy - s * 0.75 + 16],
                  fill=col)
        d.pieslice([cx + px - 13, cy - s * 0.1, cx + px + 13, cy + s * 0.7],
                   180, 360, fill=col)


def icon_cyber(d, cx, cy, s, col):
    # shield with exclamation mark
    d.polygon([(cx, cy - s * 0.85), (cx + s * 0.75, cy - s * 0.5),
               (cx + s * 0.75, cy + s * 0.1), (cx, cy + s * 0.85),
               (cx - s * 0.75, cy + s * 0.1), (cx - s * 0.75, cy - s * 0.5)],
              outline=col, width=5)
    d.line([(cx, cy - s * 0.4), (cx, cy + s * 0.15)], fill=col, width=6)
    d.ellipse([cx - 4, cy + s * 0.35, cx + 4, cy + s * 0.43], fill=col)


def icon_rocket(d, cx, cy, s, col):
    # rocket body + fins + flame
    d.polygon([(cx, cy - s * 0.95), (cx + s * 0.4, cy - s * 0.35),
               (cx + s * 0.4, cy + s * 0.35), (cx, cy + s * 0.6),
               (cx - s * 0.4, cy + s * 0.35), (cx - s * 0.4, cy - s * 0.35)],
              fill=col)
    d.polygon([(cx - s * 0.4, cy + s * 0.1), (cx - s * 0.85, cy + s * 0.6),
               (cx - s * 0.4, cy + s * 0.55)], fill=col)
    d.polygon([(cx + s * 0.4, cy + s * 0.1), (cx + s * 0.85, cy + s * 0.6),
               (cx + s * 0.4, cy + s * 0.55)], fill=col)
    d.polygon([(cx - s * 0.22, cy + s * 0.6), (cx, cy + s * 1.05),
               (cx + s * 0.22, cy + s * 0.6)], fill=(214, 90, 49))


STORIES = [
    dict(accent=(178, 44, 38), tag="UKRAINE",
         head="UKRAINE HITS CRIMEA BRIDGE AGAIN",
         summ="Second strike in under 24 hours. Russia hit Kyiv's bridges, disrupting power and water.",
         icon=icon_bridge),
    dict(accent=(176, 96, 26), tag="GULF TENSIONS",
         head="IRAN DRONES TARGET US RADAR IN BAHRAIN",
         summ="IRGC hit radar at Sheikh Isa base; Bahrain says drones intercepted, no casualties.",
         icon=icon_drone),
    dict(accent=(31, 94, 140), tag="DIPLOMACY",
         head="XI, TRUMP & PUTIN TO MEET IN SHENZHEN",
         summ="First three-way meeting confirmed for Thursday 19 November in Shenzhen.",
         icon=icon_summit),
    dict(accent=(32, 120, 84), tag="ASIA-PACIFIC",
         head="QUAD LEADERS MEET IN MANILA",
         summ="Trump, Modi, Takaichi and Albanese meet on the ASEAN summit sidelines.",
         icon=icon_quad),
    dict(accent=(96, 58, 138), tag="CYBERSECURITY",
         head="CYBERATTACK HITS 178 TOP WEBSITES",
         summ="Malicious code via Optimizely hit CNN, BBC, Zoom, HSBC and others.",
         icon=icon_cyber),
    dict(accent=(38, 84, 130), tag="SPACE",
         head="VULCAN ROCKET FAILS AFTER LAUNCH",
         summ="ULA rocket failed ~10 minutes after launch; all 40 Amazon Leo satellites lost.",
         icon=icon_rocket),
]


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # ---- header band -------------------------------------------------
    d.rectangle([0, 0, W, 168], fill=NAVY)
    f_kick = font(F_BOLD, 26)
    f_date = font(F_BLACK, 66)
    kick = "TUESDAY  —  THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(kick, font=f_kick)) / 2, 26), kick,
           font=f_kick, fill=GOLD)
    date = "17 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=f_date)) / 2, 58), date,
           font=f_date, fill=(255, 255, 255))
    d.rectangle([312, 146, 712, 150], fill=GOLD)

    # ---- story grid: 2 cols x 3 rows --------------------------------
    margin, gap = 28, 20
    top, bottom = 190, 962
    pw = (W - 2 * margin - gap) // 2
    ph = (bottom - top - 2 * gap) // 3
    f_tag = font(F_BOLD, 20)
    f_head = font(F_BLACK, 29)
    f_sum = font(F_REG, 21)

    for i, st in enumerate(STORIES):
        x = margin + (i % 2) * (pw + gap)
        y = top + (i // 2) * (ph + gap)
        d.rectangle([x, y, x + pw, y + ph], fill=PANEL)
        d.rectangle([x, y, x + 9, y + ph], fill=st["accent"])
        # icon badge
        cx, cy = x + 52, y + 46
        d.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=st["accent"])
        st["icon"](d, cx, cy, 20, (255, 255, 255))
        # tag label right of the badge
        d.text((x + 100, y + 34), st["tag"], font=f_tag, fill=st["accent"])
        # headline, max 2 lines
        head_lines = wrap(d, st["head"], f_head, pw - 48)
        assert len(head_lines) <= 2, f"headline overflow: {st['head']}"
        hy = y + 96
        for ln in head_lines:
            d.text((x + 24, hy), ln, font=f_head, fill=INK)
            hy += 36
        # summary, max 2 lines
        sum_lines = wrap(d, st["summ"], f_sum, pw - 48)
        assert len(sum_lines) <= 2, f"summary overflow: {st['summ']}"
        sy = hy + 8
        for ln in sum_lines:
            d.text((x + 24, sy), ln, font=f_sum, fill=GREY)
            sy += 28

    # ---- footer -------------------------------------------------------
    f_foot = font(F_REG, 20)
    foot = "Events as reported on 17 November 2026"
    d.text(((W - d.textlength(foot, font=f_foot)) / 2, 978), foot,
           font=f_foot, fill=FOOT)

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    main()
