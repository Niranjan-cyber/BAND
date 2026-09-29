#!/usr/bin/env python3
"""WCAG 2.x contrast checker. Compute ratios instead of eyeballing them.

Usage:
  python contrast_check.py "#1f2937" "#ffffff"
  python contrast_check.py --css assets/design-tokens.template.css --pairs "text:bg,text-muted:bg"
  python contrast_check.py --css tokens.css --pairs "text:bg,text-muted:surface,accent-contrast:accent"
  python contrast_check.py --css tokens.css --pairs "..." --dark      # read the dark theme block instead
Token names are the CSS custom properties without the leading dashes (text = --text).

Thresholds: AA normal text 4.5, AA large text (>=24px, or >=18.66px bold) 3.0, AA UI components 3.0, AAA normal 7.0.
Exit code 1 if any text pair fails AA (4.5) or any UI pair (name contains border/ui/icon/focus) fails 3:1.
"""
import argparse
import re
import sys


def parse_color(s):
    s = s.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", s)
    if not m:
        raise ValueError(f"unsupported colour {s!r} (use #rgb or #rrggbb)")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(rgb):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def verdict(r):
    return {
        "AA normal": r >= 4.5,
        "AA large/UI": r >= 3.0,
        "AAA normal": r >= 7.0,
    }


MEDIA_DARK_RE = re.compile(r"@media\s*\(\s*prefers-color-scheme\s*:\s*dark\s*\)\s*\{((?:[^{}]|\{[^{}]*\})*)\}")


def _blocks(css):
    return re.findall(r"([^{}]+)\{([^{}]*)\}", css)


def _decls(body):
    return {n: v.strip() for n, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", body)}


def read_vars(path, dark):
    """Return the custom properties for the light or dark theme.

    Light  = plain :root block(s).
    Dark   = light values, overridden by the prefers-color-scheme: dark media block, overridden by an explicit
             [data-theme="dark"] block.
    """
    css = open(path, encoding="utf-8").read()
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    media_vars = {}
    for m in MEDIA_DARK_RE.finditer(css):
        for _, body in _blocks(m.group(1)):
            media_vars.update(_decls(body))
    css_wo_media = MEDIA_DARK_RE.sub("", css)
    light, explicit_dark = {}, {}
    for selector, body in _blocks(css_wo_media):
        sel = selector.strip()
        if re.match(r"^:root\s*$", sel):
            light.update(_decls(body))
        elif re.search(r"data-theme\s*=\s*[\"']?dark", sel):
            explicit_dark.update(_decls(body))
    if not dark:
        return light
    merged = dict(light)
    merged.update(media_vars)
    merged.update(explicit_dark)
    return merged


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("colors", nargs="*", help="two colours: foreground background")
    ap.add_argument("--css", help="CSS file with custom properties")
    ap.add_argument("--pairs", help="comma-separated fg:bg token names, e.g. text:bg,text-muted:surface")
    ap.add_argument("--dark", action="store_true", help="read the dark theme block")
    a = ap.parse_args()

    failed = False
    if a.css:
        if not a.pairs:
            print("--css needs --pairs")
            sys.exit(2)
        v = read_vars(a.css, a.dark)
        print(f"Theme: {'dark' if a.dark else 'light'} | file: {a.css}\n")
        print(f"{'Pair':<42}{'Ratio':>7}  AA-normal AA-large AAA")
        for pair in a.pairs.split(","):
            fg, bg = [x.strip() for x in pair.split(":")]
            fg = fg if fg.startswith("--") else "--" + fg
            bg = bg if bg.startswith("--") else "--" + bg
            try:
                r = ratio(parse_color(v[fg]), parse_color(v[bg]))
            except KeyError as e:
                print(f"{pair:<42} missing token {e}")
                failed = True
                continue
            ok = verdict(r)
            is_ui = bool(re.search(r"border|ui|icon|focus", pair))
            need_aa = ok["AA large/UI"] if is_ui else ok["AA normal"]
            failed = failed or not need_aa
            mark = lambda b: "pass" if b else "FAIL"
            normal_col = "(UI pair)" if is_ui else mark(ok["AA normal"])
            print(f"{fg+' on '+bg:<42}{r:>6.2f}  {normal_col:<9} {mark(ok['AA large/UI']):<8} {mark(ok['AAA normal'])}")
    elif len(a.colors) == 2:
        fg, bg = parse_color(a.colors[0]), parse_color(a.colors[1])
        r = ratio(fg, bg)
        ok = verdict(r)
        print(f"Contrast {a.colors[0]} on {a.colors[1]}: {r:.2f}:1")
        for k, v in ok.items():
            print(f"  {k:<12} {'pass' if v else 'FAIL'}")
        failed = not ok["AA normal"]
    else:
        ap.print_help()
        sys.exit(2)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
