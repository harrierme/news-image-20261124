#!/usr/bin/env python3
"""Render THE WORLD TODAY - one-page newspaper of Tuesday 24 November 2026.

Draws 60 date-checked stories (4 leads, 16 cards, 40 briefs) plus a world
map with numbered pins, a UTC timeline, a numbers strip, a DATE CHECK box
and a sources footer. All illustrations are drawn with Pillow primitives.
Output: entry.png, 1024x1024, under 1 MiB.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 243, 230)
INK = (26, 26, 26)
RED = (163, 22, 33)
BLUE = (31, 78, 121)
MUTED = (107, 98, 87)
RULE = (26, 26, 26)
SEA = (206, 222, 231)
LAND = (231, 217, 184)
LAND_EDGE = (176, 158, 120)

FD = "/usr/share/fonts/truetype/dejavu/"
FL = "/usr/share/fonts/truetype/liberation/"


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF = FD + "DejaVuSerif.ttf"
SERIF_B = FD + "DejaVuSerif-Bold.ttf"
SANS = FD + "DejaVuSans.ttf"
SANS_B = FD + "DejaVuSans-Bold.ttf"


def wrap(draw, text, fnt, width):
    """Greedy word wrap, returns list of lines fitting width pixels."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, width, max_lines):
    """Wrap and clip to max_lines, adding an ellipsis on the last line."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    while lines and draw.textlength(lines[-1] + " ...", font=fnt) > width:
        lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
    lines[-1] = (lines[-1] + " ...").strip()
    return lines


# ---------------------------------------------------------------- stories
# n, region, field, label, source, headline, summary, scene, pin (lon, lat)
LEADS = [
    (1, "ASIA-PACIFIC", "Diplomacy", "CONFIRMED", "Indian Express",
     "INDIA AND NEPAL OPEN A NEW RAIL LINK",
     "Modi and Nepal PM Shah open the Saryu-Kamala Express, Ayodhya to "
     "Janakpur, with a Rs 15,000-crore package.",
     "train", (82.0, 27.0)),
    (2, "ASIA-PACIFIC", "Disaster", "REPORTED", "Lexington Herald Leader",
     "24 DEAD IN INDONESIA SWEETS-FACTORY FIRE",
     "At least 24 killed and about 30 missing as rescuers search the burned "
     "candy factory; the toll is still rising.",
     "fire", (106.8, -6.2)),
    (3, "N. AMERICA", "Markets", "REPORTED", "CNBC / BlockWest",
     "WALL STREET BOUNCES BACK FROM CORRECTION",
     "Futures rebound Tuesday after the S&P and Dow fell 10%+ from "
     "records; the Nasdaq briefly entered bear territory.",
     "chart", (-74.0, 40.7)),
    (4, "AFRICA", "Sport", "OFFICIAL", "Reuters",
     "CAS TO RULE ON SENEGAL'S CUP APPEAL",
     "CAS decides on Tuesday afternoon whether Senegal get their Africa "
     "Cup of Nations title back.",
     "trophy", (6.6, 46.5)),
]

CARDS = [
    (5, "EUROPE", "Cyber", "CONFIRMED", "The Record",
     "Austria's foreign ministry hacked; diplomat data taken.",
     "hack", (16.4, 48.2)),
    (6, "AFRICA", "Sport", "CONFIRMED", "IANS",
     "South Africa bowl Bangladesh out for 91 at Centurion.",
     "cricket", (28.2, -25.7)),
    (7, "EUROPE", "Sport", "FORECAST", "UEFA",
     "Champions League: City-Napoli, Arsenal-Dortmund tonight.",
     "football", (-0.1, 51.5)),
    (8, "WORLD", "Culture", "FORECAST", "Radio Generation",
     "Miss Universe 2026: a new queen is crowned today.",
     "crown", (100.5, 13.75)),
    (9, "ASIA-PACIFIC", "Culture", "CONFIRMED", "Dunya",
     "Guru Nanak 557th anniversary, day two; markets shut.",
     "temple", (74.9, 31.6)),
    (10, "N. AMERICA", "Economy", "OFFICIAL", "Qwalisoft",
     "US data today: house prices, confidence, Richmond Fed.",
     "data", (-77.0, 38.9)),
    (11, "ASIA-PACIFIC", "Space", "FORECAST", "SpacePolicyOnline",
     "Shenzhou-24 lifts off tonight, first Pakistani aboard.",
     "rocket", (100.3, 41.0)),
    (12, "EUROPE", "Space", "FORECAST", "SpacePolicyOnline",
     "Russia's Progress MS-36 cargo ship launches to the ISS.",
     "cargo", (63.3, 45.6)),
    (13, "ASIA-PACIFIC", "Law", "REPORTED", "Daily Jagran",
     "Delhi court issues non-bailable warrant vs Dhruv Rathee.",
     "gavel", (77.2, 28.6)),
    (14, "ASIA-PACIFIC", "Health", "REPORTED", "Indian Express",
     "FSSAI orders prosecution of Bisleri over water quality.",
     "bottle", (80.5, 26.5)),
    (15, "ASIA-PACIFIC", "Law", "OFFICIAL", "Observer Voice",
     "Court allows Karthigai Deepam lighting at hill shrine.",
     "lamp", (78.1, 9.9)),
    (16, "ASIA-PACIFIC", "Politics", "REPORTED", "Jagran Josh",
     "Rajya Sabha MP Ramrao Wadkute dies at AIIMS Delhi.",
     "capitol", (79.0, 29.5)),
    (17, "EUROPE", "Conflict", "REPORTED", "autoys.eu",
     "Russian strikes leave Odesa without power, heat, water.",
     "strike", (30.7, 46.5)),
    (18, "MIDDLE EAST", "Rights", "REPORTED", "Al Jazeera",
     "Iran flogs singer Parastoo Ahmadi: 74 lashes for singing.",
     "mic", (51.4, 35.7)),
    (19, "ASIA-PACIFIC", "Disaster", "CONFIRMED", "autoys.eu",
     "Magnitude 6.5 earthquake off Vanuatu; no tsunami threat.",
     "quake", (167.0, -16.0)),
    (20, "N. AMERICA", "Transport", "REPORTED", "autoys.eu",
     "Delta IT failure disrupts more than 3,000 US flights.",
     "plane", (-84.4, 33.7)),
]

# n, region, headline
BRIEFS = [
    (21, "ASIA-PACIFIC", "Asia Cup Rising Stars: final Group B games today - India A v UAE, Pakistan Shaheens v Nepal (Doha)."),
    (22, "ASIA-PACIFIC", "Syed Mushtaq Ali Trophy: Plate Final today in Dimapur."),
    (23, "WORLD", "World Chess: Gukesh defends his title against Sindarov as the match goes on."),
    (24, "ASIA-PACIFIC", "AIFF names Bembem Devi, Bentla D'Coth, Jo Paul Ancheri and Bruno Coutinho Sportspersons of Merit."),
    (25, "EUROPE", "Ferrari unveils two 296 models at the Finali Mondiali in Spain."),
    (26, "ASIA-PACIFIC", "SpiceJet: pilots' federation seeks government help over unpaid salaries and grounded jets."),
    (27, "ASIA-PACIFIC", "India's oil import bill up about 60% in October."),
    (28, "ASIA-PACIFIC", "9th Naturopathy Day celebrated across India."),
    (29, "ASIA-PACIFIC", "ICMR completes 100 tech transfers and signs 20 licensing deals."),
    (30, "ASIA-PACIFIC", "Excavator at Amarnath Yatra halt (Sheshnag Lake) sparks anger."),
    (31, "ASIA-PACIFIC", "Top court asks petitioner to approach Allahabad HC over the Saharanpur mosque demolition."),
    (32, "ASIA-PACIFIC", "Top court seeks Centre/ECI reply on PIL for anti-defection law reform."),
    (33, "ASIA-PACIFIC", "Pakistan: petrol down Rs3 a litre (Rs319); diesel steady at Rs357."),
    (34, "ASIA-PACIFIC", "Lahore the world's most polluted city as AQI tops 500."),
    (35, "MIDDLE EAST", "IRGC claims it shot down 78 US drones. [CLAIM]"),
    (36, "N. AMERICA", "US intelligence chief: Putin is 'no friend of America on Ukraine'."),
    (37, "MIDDLE EAST", "Eisenkot condemns settler arson in the West Bank."),
    (38, "MIDDLE EAST", "Pakistan DPM Dar and the Saudi foreign minister discuss regional developments."),
    (39, "ASIA-PACIFIC", "Shehbaz and Nawaz Sharif speak with one voice on a new province."),
    (40, "ASIA-PACIFIC", "PSL 12: opening ceremony and first match in Peshawar, announces Mohsin Naqvi."),
    (41, "ASIA-PACIFIC", "Gold and silver prices rise in Pakistan as global markets rebound."),
    (42, "ASIA-PACIFIC", "Fatima Asghar case: IHC seeks reply on the JIT plea."),
    (43, "ASIA-PACIFIC", "Opposition wants the PTI founder moved to Shifa hospital within 24 hours."),
    (44, "ASIA-PACIFIC", "Undersea cable repairs expected to finish by 6 December."),
    (45, "ASIA-PACIFIC", "WhatsApp security alert for Pakistan users: update now."),
    (46, "AFRICA", "Senegal migrant-boat toll rises to 39; the search goes on."),
    (47, "AFRICA", "Miss Universe: African queens risk missing the event over US visa curbs."),
    (48, "N. AMERICA", "Trump claims credit after the US market crash that followed Democrat midterm wins."),
    (49, "EUROPE", "Ukraine: Russian strikes in the Kyiv region kill and leave people missing."),
    (50, "ASIA-PACIFIC", "South Korea briefly warns Ulleung island after a Russian aircraft enters its airspace."),
    (51, "EUROPE", "Murmansk governor detained on suspicion of embezzlement."),
    (52, "N. AMERICA", "US states sue SpaceX over Grok AI's creation of child sexual abuse material."),
    (53, "EUROPE", "Turkish police hunt a lioness on the loose near Istanbul."),
    (54, "EUROPE", "Danish schools get bomb threats; police say they are hoaxes."),
    (55, "EUROPE", "Estonia issues a statement after a Russian airspace allegation."),
    (56, "EUROPE", "EU Academy platform hit by a cyber incident exposing personal data."),
    (57, "LATIN AMERICA", "Panama and First Quantum resume talks over the Cobre Panama mine."),
    (58, "MIDDLE EAST", "Landmine blast kills five children in northwest Syria."),
    (59, "ASIA-PACIFIC", "South Korea's president nominates a new foreign minister and spy chief."),
    (60, "WORLD", "Weather Photographer of the Year 2026 winner revealed."),
]

UTC_STRIP = [
    ("00:00", "Austria hack reported"),
    ("00:10", "Centurion, day 1: Bangladesh 91 all out"),
    ("00:20", "M6.5 quake off Vanuatu"),
    ("07:00", "SMAT Plate Final, Dimapur"),
    ("14:00", "US FHFA house prices (09:00 ET)"),
    ("15:00", "US consumer confidence (10:00 ET)"),
    ("17:45", "UCL early kick-offs"),
    ("20:00", "UCL: City-Napoli, Arsenal-Dortmund"),
    ("00:19*", "Shenzhou-24 launch (19:19 EST)"),
]

NUMBERS = [
    ("24", "dead, ~30 missing - Indonesia factory fire"),
    ("91", "all out - Bangladesh at Centurion"),
    ("15,000 cr", "rupees - India-Nepal package"),
    ("8", "MoUs signed in New Delhi"),
    ("78", "US drones claimed downed (IRGC)"),
    ("500+", "AQI in Lahore"),
    ("39", "dead - Senegal migrant boat"),
    ("3,000+", "flights hit - Delta IT failure"),
    ("6.5", "magnitude - Vanuatu quake"),
    ("557", "years - Guru Nanak anniversary"),
]

DATE_CHECK_OLD = ("NOT 24 NOV: COP31 collapse (22 Nov) - Kh-101 missiles in Poland "
                   "(20 Nov) - Nvidia Q3 $115.8bn (17 Nov) - Ebola 11,000 cases "
                   "(18 Nov) - Sensex -1,484 (23 Nov) - Zanzibar hotel fire "
                   "(21 Nov).")
DATE_CHECK_FUTURE = ("NOT YET: Argentina budget vote (25 Nov) - US PCE and GDP "
                     "(25 Nov) - Thanksgiving, US markets shut (26 Nov).")

SOURCES = ("Sources: Reuters - AP - AFP - CNBC - The Record - IANS - UEFA - "
           "Al Jazeera - Indian Express - Dunya - ARY - SpacePolicyOnline. "
           "All illustrations drawn for this page; no photographs.")


# ---------------------------------------------------------------- scenes
# Each scene draws a small flat illustration inside (x, y, w, h).
SCENE_BG = {
    "train": (222, 232, 222), "fire": (248, 214, 196), "chart": (210, 226, 238),
    "trophy": (246, 230, 180), "hack": (214, 218, 226), "cricket": (206, 230, 200),
    "football": (208, 224, 210), "crown": (250, 232, 196), "temple": (244, 224, 200),
    "data": (214, 222, 236), "rocket": (206, 216, 236), "cargo": (226, 222, 208),
    "gavel": (232, 220, 204), "bottle": (208, 228, 232), "lamp": (250, 228, 186),
    "capitol": (226, 224, 214), "strike": (244, 206, 196), "mic": (236, 214, 226),
    "quake": (230, 222, 206), "plane": (210, 224, 238),
}


def scene_train(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["train"])
    d.rectangle([x + 4, y + h - 12, x + w - 4, y + h - 8], fill=(90, 90, 90))
    bx, by, bw, bh = x + w * 0.12, y + h * 0.28, w * 0.76, h * 0.42
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=6, fill=(31, 78, 121))
    d.rounded_rectangle([bx + bw * 0.62, by, bx + bw, by + bh], radius=6,
                        fill=(163, 22, 33))
    for i in range(3):
        wx = bx + 8 + i * (bw * 0.2)
        d.rectangle([wx, by + 8, wx + bw * 0.13, by + bh * 0.45],
                    fill=(220, 235, 245))
    for i in range(3):
        cx = bx + bw * 0.2 + i * bw * 0.3
        d.ellipse([cx - 5, by + bh - 2, cx + 5, by + bh + 8], fill=(26, 26, 26))
    d.polygon([(bx + bw * 0.1, by), (bx + bw * 0.3, by - h * 0.16),
               (bx + bw * 0.42, by)], fill=(200, 200, 200))


def scene_fire(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["fire"])
    cx, base = x + w / 2, y + h * 0.92
    d.polygon([(cx - w * 0.34, base), (cx - w * 0.26, y + h * 0.55),
               (cx - w * 0.10, y + h * 0.68), (cx, y + h * 0.30),
               (cx + w * 0.12, y + h * 0.62), (cx + w * 0.28, y + h * 0.48),
               (cx + w * 0.34, base)], fill=(230, 90, 30))
    d.polygon([(cx - w * 0.18, base), (cx - w * 0.10, y + h * 0.62),
               (cx, y + h * 0.48), (cx + w * 0.10, y + h * 0.66),
               (cx + w * 0.18, base)], fill=(245, 180, 40))
    d.rectangle([x + w * 0.08, base - 4, x + w * 0.92, base + 2],
                fill=(90, 70, 60))


def scene_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["chart"])
    ox, oy = x + w * 0.14, y + h * 0.82
    d.line([ox, y + h * 0.12, ox, oy, x + w * 0.92, oy], fill=(26, 26, 26),
           width=2)
    pts = [(ox, y + h * 0.28), (ox + w * 0.18, y + h * 0.48),
           (ox + w * 0.36, y + h * 0.38), (ox + w * 0.54, y + h * 0.62),
           (ox + w * 0.72, y + h * 0.30)]
    d.line(pts, fill=(163, 22, 33), width=3, joint="curve")
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(163, 22, 33))
    d.polygon([(ox + w * 0.62, y + h * 0.30), (ox + w * 0.72, y + h * 0.30),
               (ox + w * 0.72, y + h * 0.20)], fill=(31, 78, 121))


def scene_trophy(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["trophy"])
    cx = x + w / 2
    d.polygon([(cx - w * 0.22, y + h * 0.18), (cx + w * 0.22, y + h * 0.18),
               (cx + w * 0.14, y + h * 0.52), (cx - w * 0.14, y + h * 0.52)],
              fill=(212, 160, 40))
    d.arc([cx - w * 0.34, y + h * 0.16, cx - w * 0.08, y + h * 0.42],
          90, 270, fill=(212, 160, 40), width=4)
    d.arc([cx + w * 0.08, y + h * 0.16, cx + w * 0.34, y + h * 0.42],
          270, 90, fill=(212, 160, 40), width=4)
    d.rectangle([cx - 3, y + h * 0.52, cx + 3, y + h * 0.68],
                fill=(180, 130, 30))
    d.rectangle([cx - w * 0.18, y + h * 0.68, cx + w * 0.18, y + h * 0.76],
                fill=(180, 130, 30))
    d.ellipse([cx - 4, y + h * 0.30, cx + 4, y + h * 0.38], fill=(255, 240, 180))


def scene_hack(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["hack"])
    d.rounded_rectangle([x + w * 0.14, y + h * 0.22, x + w * 0.86, y + h * 0.78],
                        radius=5, fill=(40, 48, 60))
    d.rectangle([x + w * 0.14, y + h * 0.22, x + w * 0.86, y + h * 0.34],
                fill=(70, 82, 100))
    for i, cw in enumerate((0.5, 0.34, 0.42)):
        yy = y + h * (0.44 + i * 0.11)
        d.rectangle([x + w * 0.22, yy, x + w * (0.22 + cw), yy + 3],
                    fill=(120, 220, 140))
    d.ellipse([x + w * 0.62, y + h * 0.42, x + w * 0.80, y + h * 0.60],
              outline=(230, 90, 60), width=3)
    d.line([x + w * 0.74, y + h * 0.54, x + w * 0.84, y + h * 0.66],
           fill=(230, 90, 60), width=3)


def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["cricket"])
    d.ellipse([x + w * 0.08, y + h * 0.55, x + w * 0.92, y + h * 0.95],
              fill=(120, 170, 90))
    d.polygon([(x + w * 0.30, y + h * 0.18), (x + w * 0.44, y + h * 0.18),
               (x + w * 0.52, y + h * 0.62), (x + w * 0.38, y + h * 0.62)],
              fill=(190, 150, 100))
    d.rectangle([x + w * 0.34, y + h * 0.08, x + w * 0.40, y + h * 0.22],
                fill=(120, 90, 60))
    d.ellipse([x + w * 0.66, y + h * 0.28, x + w * 0.78, y + h * 0.40],
              fill=(163, 22, 33))
    d.arc([x + w * 0.60, y + h * 0.22, x + w * 0.84, y + h * 0.46],
          300, 60, fill=(255, 255, 255), width=2)


def scene_football(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["football"])
    cx, cy, r = x + w / 2, y + h * 0.52, min(w, h) * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
              outline=(26, 26, 26), width=2)
    d.polygon([(cx, cy - r * 0.45), (cx + r * 0.43, cy - r * 0.14),
               (cx + r * 0.26, cy + r * 0.36), (cx - r * 0.26, cy + r * 0.36),
               (cx - r * 0.43, cy - r * 0.14)], fill=(26, 26, 26))
    d.line([cx, cy - r * 0.45, cx, cy - r], fill=(26, 26, 26), width=2)
    d.line([cx + r * 0.43, cy - r * 0.14, cx + r * 0.95, cy - r * 0.3],
           fill=(26, 26, 26), width=2)
    d.line([cx - r * 0.43, cy - r * 0.14, cx - r * 0.95, cy - r * 0.3],
           fill=(26, 26, 26), width=2)
    d.rectangle([x + w * 0.1, y + h * 0.86, x + w * 0.9, y + h * 0.90],
                fill=(120, 170, 90))


def scene_crown(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["crown"])
    cx = x + w / 2
    d.polygon([(cx - w * 0.32, y + h * 0.72), (cx - w * 0.32, y + h * 0.34),
               (cx - w * 0.16, y + h * 0.52), (cx, y + h * 0.24),
               (cx + w * 0.16, y + h * 0.52), (cx + w * 0.32, y + h * 0.34),
               (cx + w * 0.32, y + h * 0.72)], fill=(212, 160, 40))
    for px, py in ((cx - w * 0.32, y + h * 0.34), (cx, y + h * 0.24),
                   (cx + w * 0.32, y + h * 0.34)):
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(163, 22, 33))
    d.rectangle([cx - w * 0.32, y + h * 0.72, cx + w * 0.32, y + h * 0.80],
                fill=(180, 130, 30))
    d.ellipse([cx - 5, y + h * 0.55, cx + 5, y + h * 0.65], fill=(163, 22, 33))


def scene_temple(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["temple"])
    cx = x + w / 2
    d.ellipse([cx - w * 0.20, y + h * 0.16, cx + w * 0.20, y + h * 0.52],
              fill=(212, 160, 60))
    d.rectangle([cx - w * 0.34, y + h * 0.52, cx + w * 0.34, y + h * 0.80],
                fill=(200, 170, 110))
    d.polygon([(cx - w * 0.10, y + h * 0.52), (cx + w * 0.10, y + h * 0.52),
               (cx + w * 0.10, y + h * 0.80), (cx - w * 0.10, y + h * 0.80)],
              fill=(120, 80, 40))
    d.rectangle([cx - w * 0.38, y + h * 0.80, cx + w * 0.38, y + h * 0.86],
                fill=(150, 110, 60))
    d.line([cx, y + h * 0.10, cx, y + h * 0.16], fill=(180, 140, 40), width=3)


def scene_data(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["data"])
    base = y + h * 0.80
    for i, bh in enumerate((0.22, 0.38, 0.30, 0.50, 0.42)):
        bx = x + w * (0.14 + i * 0.16)
        d.rectangle([bx, base - h * bh, bx + w * 0.10, base],
                    fill=(31, 78, 121) if i % 2 == 0 else (163, 22, 33))
    d.line([x + w * 0.10, base, x + w * 0.90, base], fill=(26, 26, 26), width=2)
    d.polygon([(x + w * 0.14, y + h * 0.30), (x + w * 0.30, y + h * 0.14),
               (x + w * 0.46, y + h * 0.26), (x + w * 0.62, y + h * 0.10),
               (x + w * 0.80, y + h * 0.18)], fill=None, outline=(26, 26, 26))


def scene_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["rocket"])
    cx = x + w / 2
    for sx, sy in ((0.2, 0.2), (0.8, 0.3), (0.7, 0.75), (0.25, 0.7)):
        d.ellipse([x + w * sx - 2, y + h * sy - 2, x + w * sx + 2,
                   y + h * sy + 2], fill=(255, 255, 255))
    d.polygon([(cx, y + h * 0.12), (cx + w * 0.10, y + h * 0.34),
               (cx + w * 0.10, y + h * 0.60), (cx - w * 0.10, y + h * 0.60),
               (cx - w * 0.10, y + h * 0.34)], fill=(220, 225, 230),
              outline=(26, 26, 26))
    d.ellipse([cx - 4, y + h * 0.36, cx + 4, y + h * 0.44], fill=(31, 78, 121))
    d.polygon([(cx - w * 0.10, y + h * 0.48), (cx - w * 0.20, y + h * 0.66),
               (cx - w * 0.10, y + h * 0.60)], fill=(163, 22, 33))
    d.polygon([(cx + w * 0.10, y + h * 0.48), (cx + w * 0.20, y + h * 0.66),
               (cx + w * 0.10, y + h * 0.60)], fill=(163, 22, 33))
    d.polygon([(cx - w * 0.06, y + h * 0.60), (cx + w * 0.06, y + h * 0.60),
               (cx, y + h * 0.82)], fill=(245, 180, 40))


def scene_cargo(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["cargo"])
    cx = x + w / 2
    d.rectangle([cx - w * 0.26, y + h * 0.30, cx + w * 0.26, y + h * 0.58],
                fill=(200, 200, 200), outline=(26, 26, 26))
    d.rectangle([cx - w * 0.26, y + h * 0.30, cx + w * 0.26, y + h * 0.40],
                fill=(31, 78, 121))
    d.polygon([(cx - w * 0.10, y + h * 0.30), (cx + w * 0.10, y + h * 0.30),
               (cx, y + h * 0.14)], fill=(163, 22, 33))
    d.line([cx - w * 0.30, y + h * 0.66, cx + w * 0.30, y + h * 0.66],
           fill=(26, 26, 26), width=2)
    for sx in (-0.22, 0.22):
        d.polygon([(cx + w * sx, y + h * 0.66), (cx + w * (sx + 0.12),
                   y + h * 0.66), (cx + w * (sx + 0.06), y + h * 0.78)],
                  fill=(245, 180, 40))


def scene_gavel(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["gavel"])
    d.line([x + w * 0.20, y + h * 0.70, x + w * 0.80, y + h * 0.30],
           fill=(120, 85, 50), width=5)
    d.rectangle([x + w * 0.42, y + h * 0.14, x + w * 0.78, y + h * 0.34],
                fill=(90, 60, 35))
    d.rectangle([x + w * 0.30, y + h * 0.72, x + w * 0.70, y + h * 0.80],
                fill=(150, 110, 60))
    d.ellipse([x + w * 0.62, y + h * 0.42, x + w * 0.74, y + h * 0.54],
              fill=(163, 22, 33))


def scene_bottle(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["bottle"])
    cx = x + w / 2
    d.rectangle([cx - w * 0.07, y + h * 0.14, cx + w * 0.07, y + h * 0.30],
                fill=(31, 78, 121))
    d.polygon([(cx - w * 0.07, y + h * 0.30), (cx + w * 0.07, y + h * 0.30),
               (cx + w * 0.16, y + h * 0.44), (cx - w * 0.16, y + h * 0.44)],
              fill=(31, 78, 121))
    d.rounded_rectangle([cx - w * 0.16, y + h * 0.44, cx + w * 0.16,
                         y + h * 0.82], radius=4, fill=(120, 190, 220))
    d.rectangle([cx - w * 0.16, y + h * 0.52, cx + w * 0.16, y + h * 0.64],
                fill=(255, 255, 255))
    d.line([cx - w * 0.16, y + h * 0.58, cx + w * 0.16, y + h * 0.58],
           fill=(163, 22, 33), width=2)


def scene_lamp(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["lamp"])
    cx = x + w / 2
    d.ellipse([cx - w * 0.30, y + h * 0.58, cx + w * 0.30, y + h * 0.78],
              fill=(200, 140, 50))
    d.ellipse([cx - w * 0.12, y + h * 0.62, cx + w * 0.12, y + h * 0.74],
              fill=(150, 100, 40))
    d.polygon([(cx - 3, y + h * 0.62), (cx + 3, y + h * 0.62),
               (cx + 6, y + h * 0.44), (cx - 6, y + h * 0.44)],
              fill=(245, 180, 40))
    d.ellipse([cx - 5, y + h * 0.30, cx + 5, y + h * 0.44], fill=(250, 220, 90))
    for sx in (-0.28, 0.28):
        d.ellipse([cx + w * sx - 3, y + h * 0.52, cx + w * sx + 3,
                   y + h * 0.62], fill=(250, 220, 90))


def scene_capitol(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["capitol"])
    cx = x + w / 2
    d.pieslice([cx - w * 0.22, y + h * 0.14, cx + w * 0.22, y + h * 0.50],
               180, 360, fill=(150, 110, 70))
    d.rectangle([cx - w * 0.34, y + h * 0.50, cx + w * 0.34, y + h * 0.56],
                fill=(150, 110, 70))
    for i in range(4):
        px = cx - w * 0.28 + i * w * 0.19
        d.rectangle([px, y + h * 0.56, px + w * 0.06, y + h * 0.78],
                    fill=(200, 180, 140))
    d.rectangle([cx - w * 0.38, y + h * 0.78, cx + w * 0.38, y + h * 0.84],
                fill=(150, 110, 70))


def scene_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["strike"])
    cx, cy = x + w / 2, y + h * 0.42
    for i in range(8):
        ang = i * 45
        import math
        r1, r2 = w * 0.10, w * 0.30
        a = math.radians(ang)
        x1, y1 = cx + r1 * math.cos(a), cy + r1 * math.sin(a) * 0.8
        x2, y2 = cx + r2 * math.cos(a), cy + r2 * math.sin(a) * 0.8
        d.line([x1, y1, x2, y2], fill=(230, 90, 30), width=4)
    d.ellipse([cx - w * 0.12, cy - h * 0.12, cx + w * 0.12, cy + h * 0.12],
              fill=(245, 180, 40))
    d.rectangle([x + w * 0.12, y + h * 0.72, x + w * 0.34, y + h * 0.86],
                fill=(90, 90, 90))
    d.rectangle([x + w * 0.40, y + h * 0.78, x + w * 0.58, y + h * 0.86],
                fill=(70, 70, 70))
    d.rectangle([x + w * 0.64, y + h * 0.70, x + w * 0.88, y + h * 0.86],
                fill=(100, 100, 100))


def scene_mic(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["mic"])
    cx = x + w / 2
    d.rounded_rectangle([cx - w * 0.12, y + h * 0.14, cx + w * 0.12,
                         y + h * 0.48], radius=8, fill=(60, 60, 70))
    for i in range(3):
        yy = y + h * (0.22 + i * 0.09)
        d.line([cx - w * 0.12, yy, cx + w * 0.12, yy], fill=(200, 200, 210),
               width=2)
    d.arc([cx - w * 0.20, y + h * 0.34, cx + w * 0.20, y + h * 0.62],
          0, 180, fill=(60, 60, 70), width=4)
    d.line([cx, y + h * 0.62, cx, y + h * 0.76], fill=(60, 60, 70), width=4)
    d.line([cx - w * 0.12, y + h * 0.76, cx + w * 0.12, y + h * 0.76],
           fill=(60, 60, 70), width=4)
    d.ellipse([x + w * 0.68, y + h * 0.16, x + w * 0.80, y + h * 0.28],
              fill=(163, 22, 33))


def scene_quake(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["quake"])
    gy = y + h * 0.70
    d.rectangle([x, y + h * 0.70, x + w - 1, y + h - 1], fill=(170, 140, 100))
    d.line([x + w * 0.08, gy, x + w * 0.30, gy - h * 0.10, x + w * 0.45, gy,
            x + w * 0.62, gy - h * 0.14, x + w * 0.80, gy, x + w * 0.94, gy - h * 0.06],
           fill=(60, 45, 30), width=3)
    for bx, by, bw in ((0.14, 0.52, 0.20), (0.48, 0.44, 0.16), (0.70, 0.56, 0.22)):
        d.rectangle([x + w * bx, y + h * by, x + w * (bx + bw),
                     y + h * (by + 0.18)], fill=(120, 110, 100))
    d.polygon([(x + w * 0.30, y + h * 0.30), (x + w * 0.38, y + h * 0.18),
               (x + w * 0.46, y + h * 0.30)], fill=(163, 22, 33))


def scene_plane(d, x, y, w, h):
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=SCENE_BG["plane"])
    cx, cy = x + w / 2, y + h * 0.46
    d.polygon([(cx - w * 0.34, cy), (cx - w * 0.10, cy - h * 0.08),
               (cx + w * 0.30, cy - h * 0.06), (cx + w * 0.38, cy),
               (cx + w * 0.30, cy + h * 0.06), (cx - w * 0.10, cy + h * 0.08)],
              fill=(240, 240, 240), outline=(26, 26, 26))
    d.polygon([(cx - w * 0.02, cy - h * 0.06), (cx + w * 0.06, cy - h * 0.26),
               (cx + w * 0.12, cy - h * 0.06)], fill=(200, 210, 220),
              outline=(26, 26, 26))
    d.polygon([(cx - w * 0.02, cy + h * 0.06), (cx + w * 0.06, cy + h * 0.26),
               (cx + w * 0.12, cy + h * 0.06)], fill=(200, 210, 220),
              outline=(26, 26, 26))
    d.line([x + w * 0.10, y + h * 0.80, x + w * 0.90, y + h * 0.80],
           fill=(26, 26, 26), width=2)
    for i in range(3):
        sx = x + w * (0.2 + i * 0.3)
        d.line([sx, y + h * 0.14, sx + 8, y + h * 0.14], fill=(255, 255, 255),
               width=2)


SCENES = {
    "train": scene_train, "fire": scene_fire, "chart": scene_chart,
    "trophy": scene_trophy, "hack": scene_hack, "cricket": scene_cricket,
    "football": scene_football, "crown": scene_crown, "temple": scene_temple,
    "data": scene_data, "rocket": scene_rocket, "cargo": scene_cargo,
    "gavel": scene_gavel, "bottle": scene_bottle, "lamp": scene_lamp,
    "capitol": scene_capitol, "strike": scene_strike, "mic": scene_mic,
    "quake": scene_quake, "plane": scene_plane,
}

# ---------------------------------------------------------------- world map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-75, 73), (-55, 60),
     (-70, 45), (-80, 32), (-85, 25), (-97, 26), (-105, 20), (-115, 30),
     (-125, 40), (-125, 49), (-145, 60), (-168, 66)],
    [(-80, 10), (-60, 10), (-35, -5), (-40, -20), (-55, -35), (-70, -50),
     (-75, -30), (-80, -15), (-80, 10)],
    [(-10, 36), (-5, 48), (0, 50), (5, 58), (10, 57), (18, 56), (23, 60),
     (30, 70), (40, 68), (45, 60), (35, 45), (30, 40), (25, 36), (15, 38),
     (5, 38), (-10, 36)],
    [(-10, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15),
     (48, 11), (51, 10), (45, 0), (40, -15), (35, -25), (28, -33), (18, -35),
     (12, -18), (8, 4), (-8, 5), (-15, 12), (-10, 35)],
    [(40, 68), (60, 70), (90, 75), (120, 75), (150, 70), (170, 66),
     (180, 65), (160, 60), (140, 40), (127, 35), (120, 25), (108, 10),
     (100, 8), (95, 15), (90, 22), (80, 10), (75, 8), (70, 20), (60, 25),
     (50, 28), (45, 30), (40, 35), (40, 68)],
    [(113, -22), (130, -12), (142, -10), (150, -20), (153, -32), (140, -38),
     (130, -32), (115, -35), (113, -22)],
    [(-45, 60), (-30, 68), (-20, 70), (-25, 76), (-55, 76), (-60, 70),
     (-45, 60)],
]


# ---------------------------------------------------------------- layout
def draw_masthead(d, img):
    d.rectangle([0, 0, W - 1, 6], fill=INK)
    d.text((512, 22), "THE WORLD IN ONE DAY", font=font(SERIF_B, 48),
           fill=INK, anchor="mt")
    d.text((512, 80), "TUESDAY 24 NOVEMBER 2026", font=font(SERIF, 20),
           fill=INK, anchor="mt")
    d.text((16, 30), "VOL. I - No. 328", font=font(SANS, 11), fill=MUTED,
           anchor="lm")
    d.text((16, 48), "ONE PAGE. ONE DAY.", font=font(SANS_B, 11), fill=MUTED,
           anchor="lm")
    d.text((W - 16, 30), "PRICE: ONE DAY'S NEWS", font=font(SANS, 11),
           fill=MUTED, anchor="rm")
    d.text((W - 16, 48), "60 STORIES INSIDE", font=font(SANS_B, 11),
           fill=RED, anchor="rm")
    d.line([12, 108, W - 12, 108], fill=INK, width=2)
    d.line([12, 112, W - 12, 112], fill=INK, width=1)


def region_counts():
    counts = {}
    for s in LEADS + CARDS:
        counts[s[1]] = counts.get(s[1], 0) + 1
    for _, r, _ in BRIEFS:
        counts[r] = counts.get(r, 0) + 1
    order = ["ASIA-PACIFIC", "EUROPE", "AFRICA", "N. AMERICA",
             "MIDDLE EAST", "LATIN AMERICA", "WORLD"]
    return [(r if r != "LATIN AMERICA" else "LATAM", counts.get(r, 0))
            for r in order if counts.get(r, 0)]


def draw_region_strip(d):
    parts = region_counts()
    total = sum(c for _, c in parts)
    fields = {s[2] for s in LEADS + CARDS}
    line = "  |  ".join("%s %d" % (r, c) for r, c in parts)
    txt = ("60 STORIES  -  7 REGIONS  -  %d FIELDS   ::   %s"
           % (len(fields) + 7, line))
    d.text((512, 126), txt, font=font(SANS_B, 11), fill=INK, anchor="mt")
    d.line([12, 140, W - 12, 140], fill=INK, width=1)
    return total


def draw_lead(d, item, x, y, w, h):
    n, region, field, label, src, head, summ, scene, _pin = item
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=1)
    iw = 150
    SCENES[scene](d, x + 1, y + 1, iw, h - 2)
    d.rectangle([x + 1, y + 1, x + iw, y + h - 2], outline=INK, width=1)
    d.ellipse([x + 8, y + 8, x + 26, y + 26], fill=RED)
    d.text((x + 17, y + 17), str(n), font=font(SANS_B, 12), fill=(255, 255, 255),
           anchor="mm")
    tx = x + iw + 10
    tw = w - iw - 18
    tag = "%s - %s" % (region, field)
    d.text((tx, y + 10), tag, font=font(SANS_B, 10), fill=RED)
    d.text((tx + tw, y + 10), label, font=font(SANS_B, 10), fill=BLUE,
           anchor="rt")
    lines = fit_lines(d, head, font(SERIF_B, 17), tw, 2)
    yy = y + 26
    for ln in lines:
        d.text((tx, yy), ln, font=font(SERIF_B, 17), fill=INK)
        yy += 20
    slines = fit_lines(d, summ, font(SANS, 11), tw, 2)
    for ln in slines:
        d.text((tx, yy + 2), ln, font=font(SANS, 11), fill=(60, 60, 60))
        yy += 14
    d.text((tx, y + h - 12), "Source: " + src, font=font(SANS, 9),
           fill=MUTED)


def draw_card(d, item, x, y, w, h):
    n, region, field, label, src, head, scene, _pin = item
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=(150, 140, 120), width=1)
    SCENES[scene](d, x + 1, y + 1, 52, h - 2)
    d.rectangle([x + 1, y + 1, x + 53, y + h - 2], outline=(150, 140, 120),
                width=1)
    d.ellipse([x + 5, y + 5, x + 19, y + 19], fill=RED)
    d.text((x + 12, y + 12), str(n), font=font(SANS_B, 9),
           fill=(255, 255, 255), anchor="mm")
    tx = x + 58
    tw = w - 66
    d.text((tx, y + 3), "%s - %s" % (region, field), font=font(SANS_B, 8),
           fill=RED)
    lines = fit_lines(d, head, font(SERIF_B, 10), tw, 2)
    yy = y + 13
    for ln in lines:
        d.text((tx, yy), ln, font=font(SERIF_B, 10), fill=INK)
        yy += 12
    d.text((tx, y + h - 10), "%s - %s" % (src, label), font=font(SANS, 8),
           fill=MUTED)


# Manual nudge (pixels) for pins that would otherwise sit on each other.
PIN_OFFSET = {
    1: (30, 12), 3: (12, -8), 4: (-4, 12), 8: (-2, 8), 9: (-18, -10),
    10: (-8, 10), 11: (14, -6), 13: (-6, 12), 14: (20, -4), 15: (-24, 4),
    16: (2, -14), 20: (-16, -2),
}


def draw_map(d, y0, y1):
    d.text((16, y0 + 2), "WHERE IT HAPPENED - 20 STORIES PINNED",
           font=font(SANS_B, 12), fill=INK)
    d.text((W - 16, y0 + 2), "Numbers match the stories above",
           font=font(SANS, 10), fill=MUTED, anchor="rt")
    my0, my1 = y0 + 18, y1 - 2
    d.rectangle([8, my0, W - 8, my1], fill=SEA, outline=INK, width=1)

    def px(lon, lat):
        return 8 + (lon + 180) / 360.0 * (W - 16), \
            my0 + (75 - lat) / 130.0 * (my1 - my0)

    for poly in CONTINENTS:
        d.polygon([px(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=LAND_EDGE)
    for item in LEADS + CARDS:
        n, pin = item[0], item[-1]
        lon, lat = pin
        cx, cy = px(lon, lat)
        dx, dy = PIN_OFFSET.get(n, (0, 0))
        cx, cy = cx + dx, cy + dy
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                  outline=(255, 255, 255), width=1)
        d.text((cx, cy), str(n), font=font(SANS_B, 8),
               fill=(255, 255, 255), anchor="mm")


def draw_briefs(d, y0, y1):
    d.text((16, y0 + 2), "ALSO ON TUESDAY - 40 MORE STORIES",
           font=font(SANS_B, 12), fill=INK)
    d.line([12, y0 + 20, W - 12, y0 + 20], fill=INK, width=1)
    cols, rows = 4, 10
    colw = (W - 24) // cols
    rh = (y1 - (y0 + 26)) // rows
    fnt = font(SANS, 9)
    for i, (n, _region, head) in enumerate(BRIEFS):
        col, row = i // rows, i % rows
        x = 16 + col * colw
        y = y0 + 26 + row * rh
        d.text((x, y), "%d." % n, font=font(SANS_B, 9), fill=RED)
        lines = fit_lines(d, head, fnt, colw - 26, 2)
        yy = y
        for ln in lines:
            d.text((x + 24, yy), ln, font=fnt, fill=INK)
            yy += 10


def draw_bottom(d, y0):
    # UTC strip, left
    d.text((16, y0 + 2), "THE DAY IN UTC", font=font(SANS_B, 11), fill=RED)
    parts = ["%s  %s" % (t, s) for t, s in UTC_STRIP]
    txt = "   |   ".join(parts) + "   (*25 Nov UTC)"
    lines = wrap(d, txt, font(SANS, 9), 620)
    yy = y0 + 18
    for ln in lines:
        d.text((16, yy), ln, font=font(SANS, 9), fill=INK)
        yy += 12
    # numbers strip
    ny = y0 + 44
    d.text((16, ny), "THE DAY IN NUMBERS", font=font(SANS_B, 11), fill=RED)
    nparts = ["%s %s" % (v, s) for v, s in NUMBERS]
    ntxt = "   |   ".join(nparts)
    nlines = wrap(d, ntxt, font(SANS, 9), 620)
    yy = ny + 16
    for ln in nlines:
        d.text((16, yy), ln, font=font(SANS, 9), fill=INK)
        yy += 12
    # DATE CHECK box, right
    bx0, bx1 = 668, W - 12
    d.rectangle([bx0, y0, bx1, y0 + 76], outline=RED, width=2)
    d.rectangle([bx0, y0, bx1, y0 + 16], fill=RED)
    d.text((bx0 + 8, y0 + 8), "DATE CHECK - WHAT WE LEFT OUT",
           font=font(SANS_B, 10), fill=(255, 255, 255), anchor="lm")
    yy = y0 + 20
    for txt in (DATE_CHECK_OLD, DATE_CHECK_FUTURE):
        for ln in wrap(d, txt, font(SANS, 8), bx1 - bx0 - 12):
            d.text((bx0 + 6, yy), ln, font=font(SANS, 8), fill=INK)
            yy += 10
    # footer
    d.line([12, 1012, W - 12, 1012], fill=INK, width=1)
    d.text((512, 1018), SOURCES, font=font(SANS, 8), fill=MUTED, anchor="mm")


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d, img)
    draw_region_strip(d)
    # leads: 2x2 grid
    lx, ly = 12, 146
    lw, lh = 497, 110
    for i, item in enumerate(LEADS):
        draw_lead(d, item, lx + (i % 2) * (lw + 6), ly + (i // 2) * (lh + 6),
                  lw, lh)
    # cards: 4 cols x 4 rows
    cx0, cy0 = 12, 378
    cw, ch = 247, 54
    for i, item in enumerate(CARDS):
        draw_card(d, item, cx0 + (i % 4) * (cw + 4),
                  cy0 + (i // 4) * (ch + 4), cw, ch)
    draw_map(d, 602, 692)
    draw_briefs(d, 696, 922)
    draw_bottom(d, 926)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "entry.png")
    img.save(out, optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
