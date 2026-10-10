#!/usr/bin/env python3
"""
Builds calspark.cloud's marketing page in every app language.

  python3 tools/site/build.py

Source of truth: tools/site/template.html (markup, with {{key}} slots) and
tools/site/i18n/<lang>.json (one string per key). English is the reference:
add a new string to template.html + en.json first, then every other
<lang>.json; the build stops and names any key a language is missing.

Writes /index.html (English) and /<lang>/index.html for the rest. Legal and
support pages are not touched.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SITE = "https://calspark.cloud"

# dir ("" = site root), html lang, menu label, short label, CJK font family (Google Fonts name)
LANGS = [
    ("en", "", "en", "English", "EN", None),
    ("zh-hant", "zh-hant", "zh-Hant", "繁體中文", "繁中", "Noto Sans TC"),
    ("zh-hans", "zh-hans", "zh-Hans", "简体中文", "简中", "Noto Sans SC"),
    ("ja", "ja", "ja", "日本語", "日本語", "Noto Sans JP"),
    ("fr", "fr", "fr", "Français", "FR", None),
    ("de", "de", "de", "Deutsch", "DE", None),
    ("es", "es", "es", "Español", "ES", None),
    ("it", "it", "it", "Italiano", "IT", None),
]
SCREENS = ["home", "progress", "coach", "community"]
GLOBE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15 15 0 0 1 0 20M12 2a15 15 0 0 0 0 20"/></svg>'


def url_for(d):
    return f"{SITE}/{d + '/' if d else ''}"


def build():
    template = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
    keys = set(re.findall(r"\{\{([a-z0-9_]+)\}\}", template))
    hreflang = "".join(
        f'  <link rel="alternate" hreflang="{hl}" href="{url_for(d)}" />\n' for _, d, hl, *_ in LANGS
    ) + f'  <link rel="alternate" hreflang="x-default" href="{url_for("")}" />\n'

    for code, d, hl, label, short, cjk in LANGS:
        path = os.path.join(HERE, "i18n", f"{code}.json")
        if not os.path.exists(path):
            sys.exit(f"missing {path}")
        strings = json.load(open(path, encoding="utf-8"))
        missing = sorted(keys - set(strings))
        if missing:
            sys.exit(f"{code}.json is missing: {', '.join(missing)}")
        current = ' aria-current="page"'
        menu = "".join(
            '<a href="/%s" lang="%s" hreflang="%s"%s>%s</a>' % (d2 + "/" if d2 else "", hl2, hl2, current if c2 == code else "", lb2)
            for c2, d2, hl2, lb2, *_ in LANGS
        )
        page = template
        page = page.replace("{{LANG_MENU}}", f'<details class="lang"><summary aria-label="Language">{GLOBE}<span class="lbl">{short}</span></summary><div class="lang-list">{menu}</div></details>')
        page = page.replace("{{HREFLANG}}", hreflang)
        page = page.replace("{{LANG}}", hl).replace("{{CANONICAL}}", url_for(d))
        page = page.replace("{{FONT_PARAM}}", f"&family={cjk.replace(' ', '+')}:wght@400;500;700;900" if cjk else "")
        page = page.replace("{{CJK_FONT}}", f'"{cjk}", ' if cjk else "")
        page = page.replace("{{H_SPACING}}", "0" if cjk else "-.02em")
        page = re.sub(r"\{\{([a-z0-9_]+)\}\}", lambda m: strings[m.group(1)], page)
        # app screenshots in the page's language, when captured
        for s in SCREENS:
            loc = f"assets/screen-{s}-{code}.jpg"
            if code != "en" and os.path.exists(os.path.join(ROOT, loc)):
                page = page.replace(f"./assets/screen-{s}.jpg", "./" + loc)
        page = page.replace('content="https://calspark.cloud/assets/screen-home.jpg"',
                            f'content="{SITE}/' + (f"assets/screen-home-{code}.jpg" if code != "en" and os.path.exists(os.path.join(ROOT, f"assets/screen-home-{code}.jpg")) else "assets/screen-home.jpg") + '"')
        if d:  # one level down: point relative links back to the root
            page = page.replace('"./', '"../').replace("url(./", "url(../")
        out = os.path.join(ROOT, d, "index.html") if d else os.path.join(ROOT, "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(page)
        print(f"built {'/' + d if d else '/'} ({len(strings)} strings)")


if __name__ == "__main__":
    build()
