---
name: present
description: Use when Gera asks to prep a presentation, build a talk or deck, turn a wiki page or topic into slides, prepare speaker content, or "help me present X to coworkers / the team". Renders a polished, self-contained HTML presentation artifact from a wiki page or topic, following Servy's HTML-as-LLM-output doctrine.
disable-model-invocation: true
argument-hint: [wiki page name | topic | pasted content]
---

## What This Skill Does

Takes a wiki page or topic and produces a polished HTML presentation artifact Gera can present to coworkers. Serves quarter priority #5 (build a speaker profile) and activates the HTML-as-LLM-output doctrine adopted 2026-05-31 — turning "structure your response as HTML" from a trigger phrase into a repeatable speaker-prep workflow.

This has a side effect (writes an artifact file), so it is **manual-invoke only** (`/present`).

## Context to Load

1. `references/html-as-llm-output.md` — the rubric for when/how to render HTML (self-contained, polished, scannable, shareable). The output must honor this doctrine.
2. The **source**: a named wiki page in `references/`, or — if Gera names a topic — read `references/index.md` and pull the matching page(s). If he pastes raw content, use that.
3. `references/voice.md` — for any speaker notes or spoken-script text written in Gera's voice.
4. The **frontend-design** skill — invoke it to do the actual visual build so the deck avoids generic AI aesthetics.

## Steps

1. **Resolve the source.** Named wiki page → read it. Topic → search `references/index.md`, read the best-matching page(s), confirm the pick in one line. Pasted content → use directly.
2. **Clarify only what you can't infer** (one short round, skip what's obvious): audience (default: SoftServe coworkers / internal talk), length (default: a tight 5–8 slide deck), and the angle/takeaway. If Gera gave a topic with enough framing, skip this.
3. **Outline the talk**: hook → 3–5 key points → one takeaway. Show the outline in chat in 4–6 lines and let him nudge it before rendering. (Skip the pause if he said "just build it".)
4. **Render** an HTML slide deck via the frontend-design skill, following `html-as-llm-output.md`: one self-contained `.html` file, inline CSS/JS, keyboard-navigable slides, scannable, no external dependencies. Cite the source wiki page(s) on a closing slide.
5. **Save** to `artifacts/presentations/<today>-<slug>.html` and open it. Report the path.

## Output

- An HTML presentation in `artifacts/presentations/<today>-<slug>.html` (tracked in git, private repo).
- A one-line chat summary with the path and the slide count.

## Notes / Guardrails

- **Voice rule**: speaker notes / spoken script in Gera's voice (`voice.md`). But **don't finalize external-facing content** (anything leaving SoftServe, or a named client deck) without showing Gera a draft first — same rule as LinkedIn/email.
- **Cite sources.** A talk built from the wiki should name the wiki page(s) it drew from.
- **Don't fabricate** data, quotes, or claims to fill a slide. If the source page doesn't support a point, drop the point or flag the gap.
- Naming: `artifacts/presentations/<date>-<slug>.html` (date = today, ISO). One topic per file.
- This is for Gera's own presentations. For a finished client/pitch deck or brand-from-zero work, the heavier tool is **Claude Design** (`references/claude-design.md`) — mention it if the ask outgrows a wiki-page talk.
