#!/usr/bin/env python3
"""
Amore Mio — daily personalized morning newspaper generator.

Fetches real data from free sources, sends to Claude API for content,
injects into template.html, writes index.html.

Usage:
    ANTHROPIC_API_KEY=... python generate.py

Requires: anthropic feedparser requests yfinance
"""

import os
import sys
import json
import random
import re
import time
import datetime

# ─── Daily Wordle word list ────────────────────────────────────────────────────

WORDLE_WORDS = [
    "ABBEY","ABIDE","ABODE","ABOVE","ACUTE","ADORE","AFOOT","AGILE","AGING","AGLOW",
    "AISLE","ALARM","ALBUM","ALGAE","ALOFT","ALOOF","ALTER","AMBER","AMBLE","AMEND",
    "AMPLE","ANGEL","ANGER","ANGLE","ANIME","ANKLE","ANVIL","APHID","APPLE","APPLY",
    "APRIL","APRON","ARISE","ARMOR","AROMA","ARROW","ARTSY","ASIDE","ASSET","ATONE",
    "ATTIC","AUDIT","AVAIL","AVID","AVOID","AWAKE","AWARD","AWARE","AWFUL","BACON",
    "BADGE","BADLY","BAKER","BASED","BASIC","BASIL","BASIS","BATCH","BAYOU","BEACH",
    "BEADY","BEGAN","BEGIN","BEING","BELLY","BELOW","BENCH","BILLY","BIRCH","BISON",
    "BLADE","BLAND","BLANK","BLAZE","BLEAK","BLEED","BLEND","BLESS","BLISS","BLOCK",
    "BLOND","BLOOD","BLOOM","BLOWN","BLUNT","BLURT","BLUSH","BOARD","BOAST","BOKEH",
    "BONUS","BOOST","BOOTH","BOSSY","BOTCH","BOUGH","BOUND","BOXER","BRAID","BRAVE",
    "BRAVO","BRAWN","BREAD","BREAK","BREED","BRICK","BRIDE","BRIEF","BRINE","BRISK",
    "BROOD","BROOK","BROTH","BROWN","BRUNT","BRUSH","BUDDY","BUDGE","BUILT","BULGE",
    "BUNCH","BUNNY","BURLY","BURST","BYLAW","CAMEL","CAMEO","CANAL","CANDY","CARGO",
    "CARRY","CARVE","CEDAR","CHAIR","CHALK","CHEAP","CHECK","CHEEK","CHEER","CHESS",
    "CHEST","CHIEF","CHILD","CHILL","CHIMP","CHOIR","CHUNK","CIDER","CIVIC","CIVIL",
    "CLAIM","CLAMP","CLANG","CLANK","CLASH","CLASP","CLASS","CLEAN","CLEAR","CLERK",
    "CLICK","CLIFF","CLING","CLOAK","CLOCK","CLONE","CLOSE","CLOTH","CLOUD","CLOUT",
    "CLOVE","CLOWN","COACH","COAST","COBRA","COMET","COMIC","CORAL","COUCH","COULD",
    "COUNT","COURT","COVER","COVET","CRAFT","CRANE","CRAVE","CRAWL","CREAK","CREEK",
    "CRISP","CROON","CROSS","CROWD","CROWN","CRUSH","CRUSE","CRUST","CUBIC","CURLY",
    "CYCLE","DAILY","DANCE","DANDY","DAZED","DEALT","DEBUT","DECOY","DECRY","DELVE",
    "DENSE","DEPOT","DEPTH","DERBY","DIGIT","DIRTY","DISCO","DITTY","DIVOT","DIZZY",
    "DODGY","DOING","DOMED","DOUGH","DRAFT","DRAIN","DRAPE","DRAWL","DREAM","DREDGE",
    "DRINK","DRIFT","DRIVE","DROOL","DROOP","DROVE","DUCHY","DUVET","DWARF","DWELL",
    "EAGLE","EARLY","EARTH","EASEL","EIGHT","EJECT","ELDER","ELITE","EMPTY","ENJOY",
    "EQUAL","ERROR","ETHIC","EVOKE","EXACT","EXERT","EXILE","EXTRA","FABLE","FANCY",
    "FEAST","FERAL","FIELD","FIERY","FIFTH","FIFTY","FIGHT","FINAL","FIRST","FIXED",
    "FJORD","FLAME","FLANK","FLARE","FLASK","FLAIR","FLEET","FLESH","FLING","FLOCK",
    "FLORA","FLOUR","FLUTE","FOCUS","FOGGY","FOLIO","FOLLY","FORGE","FORTH","FORTY",
    "FORUM","FOUND","FRAIL","FRAME","FRANK","FRAUD","FRESH","FROND","FRONT","FROZE",
    "FRUGAL","FRUIT","FULLY","FUNKY","FUNNY","GAUZY","GAVEL","GAWKY","GENRE","GHOST",
    "GIANT","GIDDY","GIVEN","GLAND","GLARE","GLASS","GLEAM","GLIDE","GLOOM","GLOSS",
    "GLOVE","GLYPH","GNOME","GOING","GOLEM","GOOSE","GRACE","GRADE","GRAND","GRAPE",
    "GRASP","GRASS","GRAZE","GREET","GRIEF","GRIND","GROAN","GROIN","GROPE","GROSS",
    "GROUP","GROVE","GROWL","GRUEL","GUESS","GUIDE","GUILD","GUILE","GUSTO","HAPPY",
    "HARSH","HAVEN","HEART","HEAVY","HEDGE","HEIST","HELIX","HENCE","HINGE","HIPPO",
    "HOLLY","HOMER","HORDE","HOTEL","HOUND","HOUSE","HUMAN","HUMUS","HURRY","HYENA",
    "IDEAL","IGLOO","IMPLY","INDEX","INDIE","INFER","INFIX","INNER","INPUT","INTER",
    "IRONY","ISSUE","IVORY","JELLY","JETTY","JEWEL","JIFFY","JOINT","JOUST","JUDGE",
    "JUICE","JUICY","JUMPY","KARMA","KAYAK","KHAKI","KINKY","KNACK","KNEEL","KNIFE",
    "KNOCK","KNOWN","KOALA","LANCE","LAPEL","LARCH","LASER","LATCH","LATER","LATHE",
    "LAUDS","LAUGH","LAYER","LEAPT","LEARN","LEASE","LEASH","LEAST","LEDGE","LEMON",
    "LEVEL","LIGHT","LINEN","LINER","LIVER","LODGE","LOFTY","LOGIC","LOOSE","LOWER",
    "LOYAL","LUCID","LUCKY","LUNAR","LUNCH","LUSTY","LYRIC","MAGIC","MAJOR","MAMBO",
    "MANOR","MAPLE","MARCH","MATCH","MAUVE","MAXIM","MAYOR","MEATY","MEDIA","MERCY",
    "MERGE","MERIT","MESSY","METAL","MIGHT","MIRTH","MIXED","MODEL","MOLDY","MONKS",
    "MONTH","MOODY","MORAL","MOSSY","MOTEL","MOTIF","MOUNT","MOURN","MOUTH","MOVED",
    "MURAL","MUSIC","NASAL","NERVE","NEVER","NIGHT","NINJA","NOBLE","NOISE","NYMPH",
    "OAKEN","OASIS","OCEAN","OFFER","OFTEN","OLIVE","ONSET","OPERA","ORDER","OTHER",
    "OTTER","OUTER","OVOID","OXIDE","OZONE","PAINT","PANDA","PANEL","PANIC","PAPER",
    "PARTY","PASTA","PATCH","PAUSE","PEACE","PEACH","PEARL","PEDAL","PERCH","PESKY",
    "PHASE","PHONE","PHOTO","PIANO","PILOT","PIXEL","PIZZA","PLACE","PLAIN","PLANE",
    "PLANK","PLANT","PLATE","PLAZA","PLEAD","PLUCK","PLUMB","PLUMP","PLUNGE","PLUNK",
    "POINT","POKER","POLAR","PORCH","POWER","PRANK","PRESS","PRICE","PRICK","PRIDE",
    "PRIME","PRINT","PRIOR","PRIZE","PROBE","PRUNE","PSALM","PULSE","PUNCH","PUPIL",
    "QUEEN","QUERY","QUEUE","QUIET","QUOTA","QUOTE","RABBI","RADAR","RADIO","RAINY",
    "RALLY","RANCH","RANGE","RAPID","RAVEN","REACH","REALM","REBEL","REGAL","REIGN",
    "RELAX","REMIX","REPAY","RIDER","RIDGE","RIFLE","RISKY","RIVET","ROBIN","ROCKY",
    "ROGUE","ROMAN","ROOST","ROUGE","ROUGH","ROUND","ROWDY","ROYAL","RUGBY","RULER",
    "RUSTY","SADLY","SALSA","SANDY","SAUNA","SAVOR","SCALD","SCALE","SCALP","SCANT",
    "SCARE","SCARF","SCENE","SCONE","SCOOP","SCORE","SCOUT","SCOWL","SCRUB","SEIZE",
    "SERVO","SEVEN","SHAKE","SHALL","SHAME","SHAPE","SHARE","SHARK","SHARP","SHAVE",
    "SHEEN","SHEER","SHELF","SHELL","SHINY","SHIRT","SHOCK","SHORE","SHORT","SHOUT",
    "SIGHT","SINCE","SIXTH","SIXTY","SKILL","SKIMP","SKIRT","SLATE","SLEPT","SLIDE",
    "SLIME","SLING","SLOPE","SLOTH","SMALL","SMART","SMASH","SMELL","SMILE","SMIRK",
    "SMITE","SMOKE","SNACK","SNAIL","SNAKE","SNARE","SNEAK","SNORE","SOLAR","SOLID",
    "SOLVE","SONIC","SORRY","SOUTH","SPACE","SPARE","SPARK","SPAWN","SPEAK","SPEAR",
    "SPECK","SPEND","SPICY","SPIKE","SPINE","SPITE","SPLAT","SPLIT","SPOOL","SPOON",
    "SPORT","SPRAY","SPRIG","SPUNK","SQUAD","SQUAT","SQUID","STACK","STAGE","STAIN",
    "STALE","STALL","STAMP","STAND","STARE","START","STASH","STEEL","STEEP","STEER",
    "STERN","STOCK","STOMP","STONE","STOOD","STORE","STORK","STORM","STOUT","STRAP",
    "STRAW","STRAY","STRIP","STRUT","STUCK","STUDY","STUNT","STYLE","SUGAR","SUITE",
    "SUNNY","SUPER","SURGE","SWAMP","SWARM","SWEAR","SWEET","SWEPT","SWIRL","SWOOP",
    "TABLE","TABOO","TANGO","TAPAS","TASTE","TEETH","TEMPO","TENOR","TENSE","TEPID",
    "THANE","THANK","THICK","THIGH","THING","THINK","THORN","THOSE","THREE","THREW",
    "THROW","THUMB","THUMP","TIARA","TIDAL","TIGER","TIGHT","TILDE","TIMER","TITAN",
    "TODAY","TOKEN","TONAL","TONIC","TOOTH","TOPIC","TORCH","TOUCH","TOUGH","TOWEL",
    "TOWER","TOXIC","TRACE","TRACK","TRADE","TRAIL","TRAIN","TRAIT","TRASH","TREAT",
    "TREND","TRIAL","TRIBE","TRICK","TRITE","TROLL","TROOP","TROPE","TROUT","TROVE",
    "TRUCK","TRULY","TRUNK","TRUST","TRUTH","TUBER","TULIP","TUNED","TURBO","TUTOR",
    "TWEAK","TWEED","TWEET","TWICE","TWIRL","TWIST","TYING","UDDER","ULCER","ULTRA",
    "UNCLE","UNDER","UNDUE","UNFED","UNFIT","UNIFY","UNION","UNITE","UNITY","UNTIE",
    "UNTIL","UPPER","UPSET","URBAN","URGED","USAGE","USHER","USING","USUAL","UTTER",
    "VAGUE","VALET","VALID","VALOR","VALUE","VALVE","VAPID","VAPOR","VAULT","VAUNT",
    "VEGAN","VENOM","VERGE","VERSE","VERVE","VIDEO","VIGIL","VILLA","VINYL","VIOLA",
    "VIRAL","VISIT","VISOR","VISTA","VITAL","VIVID","VIXEN","VOCAL","VOGUE","VOICE",
    "VOILA","VOTER","VOUCH","VOWEL","VYING","WACKY","WAFER","WAGER","WAIST","WAIVE",
    "WALTZ","WATER","WAVER","WEARY","WEAVE","WEDGE","WEIGH","WEIRD","WHALE","WHARF",
    "WHEAT","WHEEL","WHELP","WHERE","WHICH","WHILE","WHINE","WHIRL","WHISK","WHITE",
    "WHOLE","WHOOP","WHORL","WHOSE","WIDEN","WIDOW","WIDTH","WIELD","WINCE","WINDY",
    "WIPED","WIRED","WISER","WITCH","WITTY","WOMAN","WOMEN","WOODY","WOOER","WORLD",
    "WORRY","WORSE","WORTH","WOULD","WOUND","WOVEN","WRACK","WRATH","WRECK","WREST",
    "WRIST","WRITE","WRUNG","WRYLY","YACHT","YEAST","YIELD","YOUNG","YOUTH","ZEBRA",
    "ZESTY",
]

WORDLE_HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".wordle_history.json")


def daily_wordle_word(today: datetime.date) -> str:
    """Pick a Wordle word for `today` that hasn't been used before.

    History is persisted to .wordle_history.json. Calling this multiple times
    on the same date returns the same word. When the full list is exhausted,
    the oldest picks become eligible again (but never anything used in the
    last 60 days).
    """
    iso = today.isoformat()
    try:
        with open(WORDLE_HISTORY_PATH) as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = {}

    if iso in history:
        return history[iso]

    used = set(history.values())
    pool = [w for w in WORDLE_WORDS if w not in used]
    if not pool:
        recent_dates = sorted(history.keys())[-60:]
        recent = {history[d] for d in recent_dates}
        pool = [w for w in WORDLE_WORDS if w not in recent] or list(WORDLE_WORDS)

    word = random.Random(iso).choice(pool)
    history[iso] = word
    try:
        with open(WORDLE_HISTORY_PATH, "w") as f:
            json.dump(history, f, indent=2, sort_keys=True)
    except OSError as e:
        print(f"  [warn] couldn't write wordle history: {e}", file=sys.stderr)
    return word


import requests
import feedparser
import anthropic

# ─── Constants ────────────────────────────────────────────────────────────────

HERMOSA_LAT = 33.8622
HERMOSA_LON = -118.3995

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

WMO_DESCRIPTIONS = {
    0:  "Sunny",
    1:  "Mostly Sunny",
    2:  "Partly Cloudy",
    3:  "Cloudy",
    45: "Foggy",
    48: "Icy Fog",
    51: "Light Drizzle",
    53: "Drizzle",
    55: "Heavy Drizzle",
    61: "Light Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Light Snow",
    73: "Moderate Snow",
    75: "Heavy Snow",
    80: "Showers",
    81: "Moderate Showers",
    82: "Heavy Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Hail",
    99: "Severe Thunderstorm",
}

RSS_SOURCES = {
    "world_news": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://feeds.reuters.com/reuters/worldNews",
        "https://rss.dw.com/xml/rss-en-world",
    ],
    "good_news": [
        "https://www.goodnewsnetwork.org/feed/",
        "https://www.positive.news/feed/",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
    ],
    "garden": [
        "https://www.apartmenttherapy.com/design.rss",
        "https://www.bhg.com/feed/",
        "https://www.gardenersworld.com/feed/",
    ],
    "dogs": [
        "https://www.thedodo.com/rss",
        "https://www.akc.org/rss/",
        "https://www.rover.com/blog/feed/",
    ],
}


# ─── Data fetching ────────────────────────────────────────────────────────────

def fetch_weather(lat: float, lon: float) -> dict:
    """Fetch current weather plus today's high/low in Fahrenheit."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,weathercode"
            f"&daily=temperature_2m_max,temperature_2m_min"
            f"&temperature_unit=fahrenheit"
            f"&timezone=America%2FLos_Angeles"
            f"&forecast_days=1"
        )
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        d = r.json()
        cur = d["current"]
        daily = d["daily"]
        code = int(cur.get("weathercode", 0))
        return {
            "temp_f":    round(float(cur["temperature_2m"])),
            "high_f":    round(float(daily["temperature_2m_max"][0])),
            "low_f":     round(float(daily["temperature_2m_min"][0])),
            "condition": WMO_DESCRIPTIONS.get(code, "Variable"),
        }
    except Exception as e:
        print(f"  [warn] weather fetch failed: {e}", file=sys.stderr)
        return {"temp_f": 68, "high_f": 72, "low_f": 62, "condition": "Sunny"}


def fetch_market_data() -> dict:
    """Fetch S&P 500, Dow Jones, Nasdaq, 10Y Treasury via yfinance."""
    try:
        import yfinance as yf
    except ImportError:
        print("  [warn] yfinance not installed; skipping live market data", file=sys.stderr)
        return {}

    symbols = {
        "^GSPC": "sp500",
        "^DJI":  "dow",
        "^IXIC": "nasdaq",
        "^TNX":  "treasury10y",
    }
    result = {}
    for symbol, key in symbols.items():
        try:
            hist = yf.Ticker(symbol).history(period="5d")
            if hist.empty:
                continue
            current = float(hist["Close"].iloc[-1])
            prev = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else current
            change_pct = ((current - prev) / prev * 100) if prev else 0.0
            result[key] = {"value": current, "change_pct": round(change_pct, 2)}
        except Exception as e:
            print(f"  [warn] market {symbol} failed: {e}", file=sys.stderr)
    return result


def format_market_value(key: str, value: float) -> str:
    if key == "treasury10y":
        return f"{value:.2f}%"
    elif key in ("sp500", "dow", "nasdaq"):
        return f"{value:,.2f}"
    else:
        return f"{value:,.2f}"


def fetch_rss_items(url: str, max_items: int = 5) -> list:
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries[:max_items]:
            summary = re.sub(r"<[^>]+>", "", getattr(entry, "summary", ""))[:400]
            items.append({
                "title":   getattr(entry, "title", "")[:200],
                "summary": summary.strip(),
                "link":    getattr(entry, "link", ""),
            })
        return items
    except Exception as e:
        print(f"  [warn] RSS {url} failed: {e}", file=sys.stderr)
        return []


def fetch_all_news() -> dict:
    news = {}
    for section, urls in RSS_SOURCES.items():
        items = []
        for url in urls:
            items.extend(fetch_rss_items(url))
        news[section] = items[:8]
    return news


# ─── Prompt builder ───────────────────────────────────────────────────────────

def build_prompt(today: datetime.date, weather: dict, markets: dict, news: dict, wordle_word: str) -> str:
    date_str = today.strftime(f"%A, %B {today.day}, %Y")

    # Market block
    mkt_lines = []
    for key, label in [("sp500", "S&P 500"), ("dow", "Dow Jones"),
                        ("nasdaq", "Nasdaq"), ("treasury10y", "10Y Treasury")]:
        if key in markets:
            m = markets[key]
            sign = "+" if m["change_pct"] > 0 else ""
            val = format_market_value(key, m["value"])
            mkt_lines.append(f"  {label}: {val} ({sign}{m['change_pct']}%)")
        else:
            mkt_lines.append(f"  {label}: data unavailable")
    markets_block = "\n".join(mkt_lines)

    def fmt_news(items):
        if not items:
            return "  (no items available)"
        lines = []
        for i, it in enumerate(items, 1):
            if it["title"]:
                link = it.get("link", "")
                link_part = f"\n    URL: {link}" if link else ""
                lines.append(
                    f"  {i}. {it['title']}: {it['summary'][:150]}{link_part}"
                )
        return "\n".join(lines) if lines else "  (no items available)"

    data_section = f"""\
You are generating content for "Amore Mio", a daily personalized morning newspaper \
for someone living in Hermosa Beach, California who is planning to move to Portugal. \
Write ALL content in English. Warm, elegant editorial tone — like a thoughtful friend \
curating your morning read. Culture/science/human-progress lean throughout.

TODAY: {date_str}

RAW DATA — use this to write accurate content:

HERMOSA BEACH WEATHER (Fahrenheit):
  Current: {weather['temp_f']}°F
  High: {weather['high_f']}°F  /  Low: {weather['low_f']}°F
  Conditions: {weather['condition']}

MARKETS (most recent closing prices):
{markets_block}

NEWS — WORLD / INTERNATIONAL:
{fmt_news(news.get('world_news', []))}

NEWS — UPLIFTING / GOOD NEWS:
{fmt_news(news.get('good_news', []))}

NEWS — HOME, GARDEN & PLANTS:
{fmt_news(news.get('garden', []))}

NEWS — DOGS & ANIMALS:
{fmt_news(news.get('dogs', []))}
"""

    schema_section = f"""\
─────────────────────────────────────────────────
OUTPUT: Return ONLY valid JSON (no markdown fences, no explanation) with this exact structure.

CRITICAL: HTML inside JSON strings must use SINGLE QUOTES for attributes, e.g. class='x'.
Source URLs must be copied EXACTLY from the RSS data above. Use "" if none is available.

{{
  "ogt_headline": "One Good Thing — an uplifting, specific story headline (8–14 words)",
  "ogt_body": "2–3 sentences. Warm, specific, makes the reader smile. Use the good news RSS if available; otherwise draw from your knowledge of genuinely uplifting recent events.",
  "ogt_source_name": "Publication name",
  "ogt_source_url": "Exact URL from RSS data, or empty string",

  "portugal_items": [
    {{
      "color": "green",
      "topic": "GOLDEN VISA",
      "detail": "1–2 sentences about current Golden Visa / D8 digital nomad visa status or recent changes."
    }},
    {{
      "color": "yellow",
      "topic": "COST OF LIVING",
      "detail": "1–2 sentences about current cost-of-living trends in Lisbon, Porto, or the Algarve."
    }},
    {{
      "color": "green",
      "topic": "NHR TAX REGIME",
      "detail": "1–2 sentences about the NHR or IFICI tax benefit for new residents."
    }},
    {{
      "color": "yellow",
      "topic": "HOUSING MARKET",
      "detail": "1–2 sentences about the rental or property market in Portugal."
    }}
  ],

  "parola_word": "An Italian word — chosen to be beautiful, useful, or evocative",
  "parola_pronunciation": "/phonetic pronunciation/ (e.g. /ah-MOH-reh/)",
  "parola_meaning": "English meaning and part of speech, e.g. 'serenity (noun)'",
  "parola_usage": "A natural Italian example sentence using the word.",
  "parola_mnemonic": "A clever, vivid English memory hook to remember this word. Be specific.",

  "news1_headline": "World news headline — culture, science, or human progress angle (8–14 words)",
  "news1_summary": "2–3 sentences. Accurate summary based on the RSS data. Insightful angle.",
  "news1_source_name": "Publication name",
  "news1_source_url": "Exact URL from RSS data, or empty string",

  "news2_headline": "Second world news headline (8–14 words)",
  "news2_summary": "2–3 sentences.",
  "news2_source_name": "Publication name",
  "news2_source_url": "Exact URL from RSS data, or empty string",

  "news3_headline": "Third world news headline (8–14 words)",
  "news3_summary": "2–3 sentences.",
  "news3_source_name": "Publication name",
  "news3_source_url": "Exact URL from RSS data, or empty string",

  "good1_headline": "Uplifting story headline (8–14 words)",
  "good1_body": "2–3 sentences. Warm, specific, genuinely feel-good.",
  "good1_source_name": "Publication name",
  "good1_source_url": "Exact URL from RSS data, or empty string",

  "good2_headline": "Second uplifting story headline (8–14 words)",
  "good2_body": "2–3 sentences.",
  "good2_source_name": "Publication name",
  "good2_source_url": "Exact URL from RSS data, or empty string",

  "garden1_headline": "Plant care headline — focus on orchids, bougainvillea, or air quality/stress/sleep plants (8–14 words)",
  "garden1_body": "2–3 sentences. Practical, warm, specific advice a plant parent would love.",
  "garden1_source_name": "Publication name, or 'Il Giardino' if synthesized from knowledge",
  "garden1_source_url": "Exact URL from RSS data, or empty string",

  "garden2_headline": "Second garden/plant care headline (8–14 words)",
  "garden2_body": "2–3 sentences.",
  "garden2_source_name": "Publication name, or 'Il Giardino' if synthesized",
  "garden2_source_url": "Exact URL from RSS data, or empty string",

  "dog_headline": "Warm, heartwarming dog story headline (8–14 words)",
  "dog_body": "2–3 sentences. Vivid, specific, makes you smile. Use dogs RSS if available; otherwise a genuine recent or timeless good-dog story.",
  "dog_source_name": "Publication name",
  "dog_source_url": "Exact URL from RSS data, or empty string",

  "wordle_hint": "A gentle, one-sentence hint for the word {wordle_word} — pointing toward its meaning or category without giving it away.",

  "quote_text": "An inspiring, elegant quote. Optimistic, timeless tone.",
  "quote_author": "Author name and optional context, e.g. 'Rainer Maria Rilke'"
}}

RULES:
1. portugal_items: always return exactly 4 items. Colors must be "green", "yellow", or "red".
   green = encouraging/good news, yellow = neutral/watch, red = challenge/headwind.
2. World news: lean toward culture, science, human progress. Avoid gratuitous conflict/politics.
   Use actual stories from the RSS data above — do not invent sources or URLs.
3. Garden: if garden RSS has relevant articles, use them. If not, synthesize practical advice
   from your knowledge — especially orchids, bougainvillea, and plants for air quality, stress, or sleep.
5. Source URLs: copy EXACTLY from RSS data. Never invent or modify a URL.
6. Return ONLY the JSON object. Nothing before or after it.
"""

    return data_section + schema_section


# ─── Portugal watch renderer ──────────────────────────────────────────────────

def render_portugal_items(items: list) -> str:
    if not items:
        return ""
    lines = []
    for item in items:
        color = item.get("color", "yellow").lower()
        if color not in ("green", "yellow", "red"):
            color = "yellow"
        topic = item.get("topic", "").upper()
        detail = item.get("detail", "")
        # Map color to check character
        check_char = "✓" if color == "green" else ("✗" if color == "red" else "~")
        lines.append(
            f'<div class="portugal-item">\n'
            f'  <div class="portugal-check {color}">{check_char}</div>\n'
            f'  <div>\n'
            f'    <div class="portugal-topic">{topic}</div>\n'
            f'    <div class="portugal-detail">{detail}</div>\n'
            f'  </div>\n'
            f'</div>'
        )
    return "\n".join(lines)


# ─── JSON repair ─────────────────────────────────────────────────────────────

def _repair_json_html_attrs(json_str: str) -> str:
    """Fix unescaped double quotes inside HTML attribute values within JSON strings."""
    result = []
    in_string = False
    escaped = False
    i = 0
    while i < len(json_str):
        ch = json_str[i]
        if escaped:
            result.append(ch)
            escaped = False
            i += 1
            continue
        if ch == '\\' and in_string:
            result.append(ch)
            escaped = True
            i += 1
            continue
        if ch == '"':
            if not in_string:
                in_string = True
                result.append(ch)
            else:
                rest = json_str[i + 1:].lstrip()
                if rest and rest[0] in (':', ',', '}', ']', '\n', '\r'):
                    in_string = False
                    result.append(ch)
                else:
                    result.append("'")
            i += 1
            continue
        result.append(ch)
        i += 1
    return "".join(result)


# ─── Template injection ───────────────────────────────────────────────────────

def inject_template(template: str, tokens: dict) -> str:
    result = template
    for key, value in tokens.items():
        result = result.replace("{{" + key + "}}", str(value))
    return result


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    template_path = os.path.join(SCRIPT_DIR, "template.html")
    output_path   = os.path.join(SCRIPT_DIR, "index.html")

    if not os.path.exists(template_path):
        print(f"ERROR: template.html not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    with open(template_path) as f:
        template = f.read()

    today = datetime.date.today()
    wordle_word = daily_wordle_word(today)
    date_display = today.strftime(f"%A, %B {today.day}, %Y")

    print(f"Generating Amore Mio — {date_display}")

    print("  Fetching weather (Hermosa Beach)...")
    weather = fetch_weather(HERMOSA_LAT, HERMOSA_LON)

    print("  Fetching market data...")
    markets = fetch_market_data()

    print("  Fetching RSS news...")
    news = fetch_all_news()

    print("  Calling Claude API...")
    client = anthropic.Anthropic()

    prompt = build_prompt(today, weather, markets, news, wordle_word)

    max_attempts = 3
    retry_wait = 30
    response = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            break
        except anthropic.APIStatusError as e:
            if e.status_code == 529 and attempt < max_attempts:
                print(f"  [warn] Claude API overloaded (attempt {attempt}/{max_attempts}). Retrying in {retry_wait}s...", file=sys.stderr)
                time.sleep(retry_wait)
            else:
                raise


    raw = response.content[0].text.strip()

    # Strip markdown fences if Claude added them
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    # Extract the JSON object
    json_match = re.search(r"\{[\s\S]*\}", raw)
    if not json_match:
        print("ERROR: No JSON found in Claude response:", file=sys.stderr)
        print(raw[:2000], file=sys.stderr)
        sys.exit(1)

    json_str = json_match.group()

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        repaired = _repair_json_html_attrs(json_str)
        try:
            data = json.loads(repaired)
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON parse failed even after repair: {e}", file=sys.stderr)
            print(json_str[:3000], file=sys.stderr)
            sys.exit(1)

    print("  Building page...")

    # Market display helper
    def mkt(key):
        if key not in markets:
            return "—", "—", "flat"
        m = markets[key]
        val = format_market_value(key, m["value"])
        pct = m["change_pct"]
        cls  = "up" if pct > 0 else ("down" if pct < 0 else "flat")
        sign = "+" if pct > 0 else ""
        return val, f"{sign}{pct}%", cls

    sp500_price,  sp500_change,  sp500_dir  = mkt("sp500")
    dow_price,    dow_change,    dow_dir    = mkt("dow")
    nasdaq_price, nasdaq_change, nasdaq_dir = mkt("nasdaq")
    t10y_price,   t10y_change,   t10y_dir   = mkt("treasury10y")

    # Portugal watch HTML
    portugal_html = render_portugal_items(data.get("portugal_items", []))

    tokens = {
        # Header
        "DATE_DISPLAY":       date_display,
        # Weather bar
        "WEATHER_CURRENT":    weather["temp_f"],
        "WEATHER_LOW":        weather["low_f"],
        "WEATHER_HIGH":       weather["high_f"],
        "WEATHER_CONDITION":  weather["condition"],
        # One Good Thing
        "OGT_HEADLINE":       data.get("ogt_headline", ""),
        "OGT_BODY":           data.get("ogt_body", ""),
        "OGT_SOURCE_URL":     data.get("ogt_source_url", "#") or "#",
        "OGT_SOURCE_NAME":    data.get("ogt_source_name", ""),
        # Markets
        "MARKET_SP500_PRICE":   sp500_price,
        "MARKET_SP500_CHANGE":  sp500_change,
        "MARKET_SP500_DIR":     sp500_dir,
        "MARKET_DOW_PRICE":     dow_price,
        "MARKET_DOW_CHANGE":    dow_change,
        "MARKET_DOW_DIR":       dow_dir,
        "MARKET_NASDAQ_PRICE":  nasdaq_price,
        "MARKET_NASDAQ_CHANGE": nasdaq_change,
        "MARKET_NASDAQ_DIR":    nasdaq_dir,
        "MARKET_10Y_PRICE":     t10y_price,
        "MARKET_10Y_CHANGE":    t10y_change,
        "MARKET_10Y_DIR":       t10y_dir,
        # Portugal watch
        "PORTUGAL_ITEMS":     portugal_html,
        # Parola del Giorno
        "PAROLA_WORD":          data.get("parola_word", ""),
        "PAROLA_PRONUNCIATION": data.get("parola_pronunciation", ""),
        "PAROLA_MEANING":       data.get("parola_meaning", ""),
        "PAROLA_USAGE":         data.get("parola_usage", ""),
        "PAROLA_MNEMONIC":      data.get("parola_mnemonic", ""),
        # World News
        "NEWS1_HEADLINE":     data.get("news1_headline", ""),
        "NEWS1_SUMMARY":      data.get("news1_summary", ""),
        "NEWS1_SOURCE_URL":   data.get("news1_source_url", "#") or "#",
        "NEWS1_SOURCE_NAME":  data.get("news1_source_name", ""),
        "NEWS2_HEADLINE":     data.get("news2_headline", ""),
        "NEWS2_SUMMARY":      data.get("news2_summary", ""),
        "NEWS2_SOURCE_URL":   data.get("news2_source_url", "#") or "#",
        "NEWS2_SOURCE_NAME":  data.get("news2_source_name", ""),
        "NEWS3_HEADLINE":     data.get("news3_headline", ""),
        "NEWS3_SUMMARY":      data.get("news3_summary", ""),
        "NEWS3_SOURCE_URL":   data.get("news3_source_url", "#") or "#",
        "NEWS3_SOURCE_NAME":  data.get("news3_source_name", ""),
        # Good Stuff
        "GOOD1_HEADLINE":     data.get("good1_headline", ""),
        "GOOD1_BODY":         data.get("good1_body", ""),
        "GOOD1_SOURCE_URL":   data.get("good1_source_url", "#") or "#",
        "GOOD1_SOURCE_NAME":  data.get("good1_source_name", ""),
        "GOOD2_HEADLINE":     data.get("good2_headline", ""),
        "GOOD2_BODY":         data.get("good2_body", ""),
        "GOOD2_SOURCE_URL":   data.get("good2_source_url", "#") or "#",
        "GOOD2_SOURCE_NAME":  data.get("good2_source_name", ""),
        # Il Giardino
        "GARDEN1_HEADLINE":   data.get("garden1_headline", ""),
        "GARDEN1_BODY":       data.get("garden1_body", ""),
        "GARDEN1_SOURCE_URL": data.get("garden1_source_url", "#") or "#",
        "GARDEN1_SOURCE_NAME":data.get("garden1_source_name", ""),
        "GARDEN2_HEADLINE":   data.get("garden2_headline", ""),
        "GARDEN2_BODY":       data.get("garden2_body", ""),
        "GARDEN2_SOURCE_URL": data.get("garden2_source_url", "#") or "#",
        "GARDEN2_SOURCE_NAME":data.get("garden2_source_name", ""),
        # Good Boy
        "DOG_HEADLINE":       data.get("dog_headline", ""),
        "DOG_BODY":           data.get("dog_body", ""),
        "DOG_SOURCE_URL":     data.get("dog_source_url", "#") or "#",
        "DOG_SOURCE_NAME":    data.get("dog_source_name", ""),
        # Wordle
        "WORDLE_ANSWER":      wordle_word,
        "WORDLE_HINT":        data.get("wordle_hint", ""),
        # Quote
        "QUOTE_TEXT":         data.get("quote_text", ""),
        "QUOTE_AUTHOR":       data.get("quote_author", ""),
    }

    output = inject_template(template, tokens)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"  Done — index.html written ({len(output):,} bytes)")


if __name__ == "__main__":
    main()
