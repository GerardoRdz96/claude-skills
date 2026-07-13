#!/usr/bin/env bash
# css-tokens.sh — verbatim CSS design-token capture for /design-blueprint v2.
# Fetches a page + its stylesheets and extracts REAL tokens (custom properties,
# font stacks, radii, shadows, load-bearing class rules) — no LLM, no invention.
# The deterministic complement to extract.sh's LLM-summarized read.
#
# usage: css-tokens.sh <URL> [max_sheets=6]
# stdout: a markdown "Verbatim token capture" section (empty findings stay honest)
# stderr: fetch notes. exit 1 only if the page itself is unreachable.
set -uo pipefail

URL="${1:?usage: css-tokens.sh <URL> [max_sheets]}"
MAX_SHEETS="${2:-6}"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
TMP="$(mktemp -d /tmp/css-tokens.XXXXXX)"
trap 'rm -rf "$TMP"' EXIT

if ! curl -fsSL --max-time 30 -A "$UA" "$URL" -o "$TMP/page.html" 2>>"$TMP/err"; then
  echo "css-tokens: page unreachable: $URL" >&2
  exit 1
fi

# Collect stylesheet URLs (resolved + scheme/host-vetted) + inline <style> blocks
python3 - "$URL" "$TMP" <<'PYEOF'
import re, sys
from urllib.parse import urljoin, urlparse
url, tmp = sys.argv[1], sys.argv[2]
html = open(f"{tmp}/page.html", encoding="utf-8", errors="replace").read()

PRIVATE = re.compile(r'^(localhost$|127\.|0\.|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1)')
page_host = (urlparse(url).hostname or "").lower()

def allowed(sheet_url):
    """http/https only; private/loopback hosts only if the page itself lives there
    (keeps localhost dev use working, blocks SSRF pivots from hostile public pages)."""
    p = urlparse(sheet_url)
    if p.scheme not in ("http", "https"):
        return False
    host = (p.hostname or "").lower()
    if not host:
        return False
    if PRIVATE.match(host) or host.endswith(".local"):
        return host == page_host
    return True

hrefs, seen = [], set()
for tag in re.findall(r'<link\b[^>]*>', html, re.I):
    rel = re.search(r'rel=["\']?([^"\'>]+)', tag, re.I)
    if not rel or "stylesheet" not in rel.group(1).lower().split():
        continue
    m = re.search(r'href=["\']?([^"\' >]+)', tag, re.I)
    if not m:
        continue
    h = urljoin(url, m.group(1))
    if h in seen:
        continue
    seen.add(h)
    if allowed(h):
        hrefs.append(h)
    else:
        print(f"skipped (scheme/host policy): {h}", file=sys.stderr)
open(f"{tmp}/sheets.txt", "w").write("\n".join(hrefs))
inline = re.findall(r'<style[^>]*>(.*?)</style>', html, re.S | re.I)
open(f"{tmp}/inline.css", "w").write("\n".join(inline))
PYEOF

# Fetch external sheets (capped)
FETCHED=0
: > "$TMP/external.css"
while IFS= read -r sheet && [ "$FETCHED" -lt "$MAX_SHEETS" ]; do
  [ -z "$sheet" ] && continue
  if curl -fsSL --max-time 20 -A "$UA" "$sheet" >> "$TMP/external.css" 2>>"$TMP/err"; then
    FETCHED=$((FETCHED+1))
    echo "fetched: $sheet" >&2
  else
    echo "failed:  $sheet" >&2
  fi
  echo >> "$TMP/external.css"
done < "$TMP/sheets.txt"

# Parse tokens out of inline + external CSS
python3 - "$URL" "$TMP" "$FETCHED" <<'PYEOF'
import re, sys
from collections import Counter, OrderedDict
url, tmp, fetched = sys.argv[1], sys.argv[2], int(sys.argv[3])
css = open(f"{tmp}/inline.css", encoding="utf-8", errors="replace").read()
css += "\n" + open(f"{tmp}/external.css", encoding="utf-8", errors="replace").read()

def md_safe(s):
    """Neutralize markdown/HTML from untrusted CSS before rendering into tables/code spans."""
    return (s.replace("`", "'").replace("|", "&#124;")
             .replace("<", "&lt;").replace(">", "&gt;")
             .replace("\r", " ").replace("\n", " "))

def top(counter, n):
    return [f"`{md_safe(v)}` ×{c}" for v, c in counter.most_common(n)]

# 1. Custom properties (the real token layer; framework internals excluded)
INTERNAL = ('--tw-', '--radix-', '--rt-', '--un-')
props, internal_count = OrderedDict(), 0
for name, val in re.findall(r'(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]+);', css):
    name = name.strip()
    if name.startswith(INTERNAL):
        internal_count += 1
        continue
    props.setdefault(name, val.strip()[:120])

# 2. Font stacks
faces = sorted(set(re.findall(r'@font-face\s*{[^}]*?font-family\s*:\s*["\']?([^;"\'}]+)', css)))
fams = Counter(v.strip()[:100] for v in re.findall(r'font-family\s*:\s*([^;{}]+);', css))
fvs = Counter(v.strip()[:100] for v in re.findall(r'font-variation-settings\s*:\s*([^;{}]+);', css))

# 3. Geometry / depth / rhythm signals
radii = Counter(v.strip() for v in re.findall(r'border-radius\s*:\s*([^;{}]+);', css))
shadows = Counter(v.strip()[:140] for v in re.findall(r'box-shadow\s*:\s*([^;{}]+);', css))
spacing = Counter(v.strip() for v in re.findall(r'letter-spacing\s*:\s*([^;{}]+);', css))

# 4. Load-bearing rules (first full block per selector family)
rules = OrderedDict()
for pat, label in [(r'\bh1\b', 'h1'), (r'\bh2\b', 'h2'), (r'\bbody\b', 'body'),
                   (r'\bbutton\b|\.btn\b|\.button\b', 'button'),
                   (r'\.container\b|\.wrapper\b|\.max-w', 'container')]:
    m = re.search(r'((?:[^{}\n]*(?:' + pat + r')[^{}]*)\{[^{}]{10,600}\})', css)
    if m and label not in rules:
        rules[label] = re.sub(r'\s+', ' ', m.group(1)).strip()[:420]

n_sheets = len(open(f"{tmp}/sheets.txt").read().splitlines())
out = []
out.append(f"### Verbatim token capture — {url}")
out.append("")
out.append(f"*Deterministic capture (`css-tokens.sh`): {fetched}/{n_sheets} linked stylesheets fetched + inline `<style>` blocks. "
           f"{len(props)} brand custom properties found ({internal_count} framework internals filtered). "
           f"Values are the site's own CSS, verbatim — not interpreted.*")
out.append("")
if props:
    out.append(f"**Custom properties ({len(props)}, first 120):**")
    out.append("")
    out.append("| Property | Value |")
    out.append("|---|---|")
    for k, v in list(props.items())[:120]:
        out.append(f"| `{md_safe(k)}` | `{md_safe(v)}` |")
else:
    out.append("**Custom properties:** (none found — site may compile tokens away or block fetches)")
out.append("")
if faces:
    out.append("**@font-face families:** " + ", ".join(f"`{md_safe(f.strip())}`" for f in faces[:12]))
if fams:
    out.append("**font-family stacks (by frequency):** " + " · ".join(top(fams, 6)))
if fvs:
    out.append("**font-variation-settings:** " + " · ".join(top(fvs, 4)))
if radii:
    out.append("**border-radius values:** " + " · ".join(top(radii, 8)))
if shadows:
    out.append("**box-shadow recipes:** " + " · ".join(top(shadows, 4)))
if spacing:
    out.append("**letter-spacing values:** " + " · ".join(top(spacing, 6)))
if rules:
    out.append("")
    out.append("**Load-bearing rules (first match per family):**")
    out.append("")
    for label, rule in rules.items():
        out.append(f"- **{label}**: `{md_safe(rule)}`")
if not any([props, faces, fams, fvs, radii, shadows, spacing, rules]):
    out.append("")
    out.append("*(Nothing captured — heavily obfuscated/JS-injected CSS. Fall back to the LLM extraction + a Firecrawl screenshot.)*")
print("\n".join(out))
PYEOF
