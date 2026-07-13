#!/usr/bin/env bash
# extract.sh <url> <slug> — Firecrawl /v2/scrape structured design extraction for /design-blueprint.
#
# Does the whole fragile call deterministically: builds the jq payload from the bundled
# extraction-prompt.txt + extraction-schema.json, POSTs to /v2/scrape, handles every HTTP
# branch (200/401/402/400/5xx-with-one-retry), runs the honesty checks, applies the
# theme-color fallback, and prints the extraction JSON (.data.json) to stdout.
# Diagnostics (creditsUsed, raw response path, notes) go to stderr.
#
# Exit codes: 0 = extraction JSON on stdout; non-zero = human-readable error on stderr.
set -euo pipefail

URL="${1:?usage: extract.sh <url> <slug>}"
SLUG="${2:?usage: extract.sh <url> <slug>}"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/../../.." && pwd)}"

# --- Auth (per CLAUDE.md "Where things live": secrets in .env) ---
set -a; source "$REPO_DIR/.env"; set +a
if [[ -z "${FIRECRAWL_BEARER_AUTH:-}" ]]; then
  echo "ERROR: FIRECRAWL_BEARER_AUTH is missing — add it to $REPO_DIR/.env" >&2
  exit 1
fi

# --- Payload from bundled files ---
PROMPT=$(cat "$SKILL_DIR/extraction-prompt.txt")
SCHEMA=$(cat "$SKILL_DIR/extraction-schema.json")

PAYLOAD=$(jq -nc --arg url "$URL" --arg prompt "$PROMPT" --argjson schema "$SCHEMA" '{
  url: $url,
  formats: [
    "rawHtml",
    {type: "json", prompt: $prompt, schema: $schema}
  ],
  onlyMainContent: false,
  maxAge: 0
}')

TMP="/tmp/fc-blueprint-${SLUG}.json"

do_post() {
  curl -sS -o "$TMP" -w "%{http_code}" \
    -X POST https://api.firecrawl.dev/v2/scrape \
    -H "Authorization: Bearer $FIRECRAWL_BEARER_AUTH" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    --max-time 180 || echo "000"
}

HTTP_CODE=$(do_post)
if [[ "$HTTP_CODE" == "000" || "$HTTP_CODE" =~ ^5 ]]; then
  echo "NOTE: Firecrawl returned $HTTP_CODE — retrying once in 5s..." >&2
  sleep 5
  HTTP_CODE=$(do_post)
fi

case "$HTTP_CODE" in
  200) : ;;
  401) echo "ERROR 401: Firecrawl key invalid/rotated — refresh FIRECRAWL_BEARER_AUTH in .env." >&2; exit 1 ;;
  402) echo "ERROR 402: Firecrawl credits exhausted — top up at firecrawl.dev/settings/billing." >&2; exit 1 ;;
  400) echo "ERROR 400: likely a bad URL. Error body:" >&2; cat "$TMP" >&2; echo >&2; exit 1 ;;
  *)   echo "ERROR $HTTP_CODE: Firecrawl-side issue persisted after retry. Body:" >&2; cat "$TMP" >&2; echo >&2; exit 1 ;;
esac

# --- Honesty checks (never render from a bad extraction) ---
if [[ "$(jq 'has("data") and (.data | has("json")) and (.data.json != null)' "$TMP")" != "true" ]]; then
  echo "ERROR: HTTP 200 but .data.json is missing/null — Firecrawl scraped but did not run the LLM extraction. Raw: $TMP" >&2
  exit 1
fi
EXTRACT_ERR=$(jq -r '.data.json.error // empty' "$TMP")
if [[ -n "$EXTRACT_ERR" ]]; then
  echo "ERROR: extraction failed (paywalled/blank/blocked): $EXTRACT_ERR" >&2
  exit 1
fi

EXTRACT=$(jq '.data.json' "$TMP")

# --- Free fallback: metadata theme-color as primary when the LLM returned empty ---
PRIMARY=$(jq -r '.data.json.color_palette.primary // empty' "$TMP")
THEME=$(jq -r '.data.metadata["theme-color"] // empty' "$TMP")
if [[ -z "$PRIMARY" && -n "$THEME" ]]; then
  EXTRACT=$(jq --arg t "$THEME" '.color_palette.primary = $t' <<<"$EXTRACT")
  echo "NOTE: color_palette.primary was empty; filled from metadata theme-color ($THEME)." >&2
fi

# --- Cost reporting ---
CREDITS=$(jq -r '.data.metadata.creditsUsed // "unknown"' "$TMP")
echo "creditsUsed: $CREDITS" >&2
echo "raw: $TMP" >&2

echo "$EXTRACT"
