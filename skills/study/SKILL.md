---
name: study
description: Use when Gera asks to study, quiz himself, test his recall, make flashcards, build an active-recall deck, or "test me on X" from a wiki page or knowledge source. Also handles English vocab/phrasing drills. Turns any wiki page into a repeatable active-recall deck or an interactive chat quiz.
argument-hint: [wiki page name | topic | "english"]
---

## What This Skill Does

Turns any wiki page or knowledge source into active-recall practice — a flashcard deck, an interactive chat quiz, or a self-quiz HTML artifact. Generalizes the one-off `references/jumpstart-flashcards.md` into a repeatable workflow. Serves quarter priorities #2 (keep learning) and #3 (improve English).

Active recall beats re-reading. The point is to make Gera retrieve the answer, not recognize it.

## Context to Load

1. The **source**: a named page in `references/`, or — for a topic — read `references/index.md` and pull the matching page(s). For "english", drive vocab/phrasing drills (optionally seeded from a page he names).
2. `references/jumpstart-flashcards.md` — the format exemplar for a flashcard companion page.

## Steps

1. **Resolve the source.** Named page → read it. Topic → search `references/index.md`, read the best match, confirm the pick in one line. "english" → English mode (below).
2. **Pick the mode** (ask in one line if not stated):
   - **(a) Flashcard deck** — extract atomic Q→A pairs covering the page's key claims. One fact per card. Save as a wiki companion page `references/<slug>-flashcards.md` (same shape as the jumpstart deck), register it in `references/index.md`, and append a line to `references/log.md`.
   - **(b) Interactive quiz** — ask one question at a time in chat, wait for Gera's answer, grade it (correct / close / off, with the right answer), track a running score, and re-ask missed ones at the end. ~8–12 questions unless he says otherwise.
   - **(c) Self-quiz artifact** — render an HTML self-test to `artifacts/study/<today>-<slug>.html` (questions with reveal-on-click answers), per `references/html-as-llm-output.md`. Use when he wants something to drill later, away from chat.
3. **English mode**: pull useful vocabulary, idioms, and phrasing — ideally from real content he's working with (a wiki page, an email he's drafting). Drill meaning + usage, and flag any phrasing he got wrong with a natural correction. Keep it encouraging.

## Output

- **Flashcards**: `references/<slug>-flashcards.md` (wiki companion page) + index + log entry.
- **Interactive quiz**: runs in chat, ends with a score + which cards to review.
- **Self-quiz artifact**: `artifacts/study/<today>-<slug>.html`.

## Notes / Guardrails

- **Atomic cards** — one fact per card. Don't bundle three claims into one question.
- **Test recall, don't re-teach.** Questions should force retrieval. Avoid yes/no and giveaway phrasing.
- **Ground every card in the source.** Don't invent facts the page doesn't support; if the page is thin, say so rather than padding.
- Flashcard decks are real wiki pages — follow the wiki protocol (index update + log line) when saving one. Interactive quizzes and artifacts don't touch the wiki.
- For English, be a warm coach, not a grammar police — correct naturally, keep his confidence up.
