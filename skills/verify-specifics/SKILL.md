---
name: verify-specifics
description: Use right before shipping any prose YOU (Claude) drafted — a briefing, report, blog post, LinkedIn draft, email, doc, or wiki page — to extract every specificity-class claim (named people/orgs, dates, statistics, citations, URLs, versions, quotes) and get a flagged checklist of exactly what to verify against a real source first. Triggers — "verify the specifics", "fact-check this draft", "what should I check before shipping", "flag the claims to verify", "spot-check this for fabrication", "before I post this", "/verify-specifics". Operationalizes the binding rule "fabrication concentrates in specificity" (references/anthropic-best-practices.md #12). Runs a deterministic script, not a token judgment. NOT /storm-research or /deep-research (those research a topic from scratch); this scans an existing draft for claims to check.
argument-hint: "[path to the draft, or paste the prose]"
---

# /verify-specifics — flag what to check before shipping

Generative AI is most confident exactly where it is least reliable: **fabrication
concentrates in specificity** — named people, dates, statistics, citations, URLs,
versions, quotes (references/anthropic-best-practices.md checklist #12; source
references/course-ai-capabilities-limitations.md). This skill turns a finished draft
into a to-do list of the precise claims a human or a different-lineage model must
verify before it ships. It does not judge truth — it surfaces the surface area.

**Gate 0 — SoftServe data boundary.** If the draft contains SoftServe Internal+
or customer specifics, STOP: this runs in personal Servy. Generic/public prose only.
Route real customer content to the isolated `ss` instance. The script itself is
local and network-free, but the draft must not be customer IP.

## How to run it

The work is a tested, deterministic script — **RUN it, do not re-derive the extraction
in tokens** (regex over prose is exactly the fragile-repeatable job a script owns).

1. **Point it at the draft.** A file:
   `python3 scripts/verify_specifics.py path/to/draft.md`
   or pipe pasted prose:
   `pbpaste | python3 scripts/verify_specifics.py`
   Add `--json` for machine-readable output. Exit code is always 0 (advisory).

2. **Read the grouped checklist.** Claims come grouped by class — DATES,
   NUMBERS/STATS, URLS/DOMAINS, VERSIONS, QUOTED-CLAIMS, PROPER-NOUN NAMES,
   CITATIONS — de-duplicated, each as an unchecked box with a per-class hint.

3. **Actually verify, don't rubber-stamp.** For each item, check it against a
   PRIMARY source — not your own memory, which is the thing under suspicion. This
   is where the No-Self-Review reflex applies: open the URL, resolve the citation,
   confirm the date/figure at its source, find the exact quote wording, confirm the
   named person/org exists and the attribution is right. Correct the draft in place.

4. **Report what you changed.** Tell Gera which claims you verified, which you
   corrected, and any you could NOT confirm (flag those explicitly — an unverifiable
   specific is a cut-or-hedge candidate, never a ship-anyway).

## When to fire it

- Any time you hand Gera prose with specifics in it and "ship/post/send" is next.
- Before a `/pa-post`, LinkedIn draft, briefing, or wiki page goes out.
- As the verification half after `/storm-research` / `/deep-research` synthesis,
  on the final written artifact (those verify sources during research; this catches
  specifics that crept into the prose layer).

The script is the front line; your judgment closes each box. A clean run (zero
claims) means low fabrication surface — still skim for vague unsourced assertions
the regex can't see. Engine: `scripts/verify_specifics.py`
(tests: `tests/verify-specifics/test_verify_specifics.py`).
