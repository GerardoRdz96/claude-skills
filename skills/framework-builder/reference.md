# framework-builder — reference (template, quality gate, types, graduation, wiring)

Derived from analyzing Servy's real frameworks (`3ms-framework`, `four-cs`, `routine-placement-framework`, `ai-applicability-framework`) + `wiki-protocol`. The SKILL.md walks the process; this is the detailed material it leans on.

## The one non-negotiable

**A framework's output is an ACTION (pick / build / skip / score / which-home), not understanding.** If the reader finishes with thoughts but no verdict, it is a descriptive wiki page, not a framework — route it to normal `references/` ingest instead. This single test gates everything below.

## The decision rule — three proven forms (pick by the shape of the decision)

1. **ordered-rules** (`3ms-framework`, `ai-applicability`) — a numbered DO-THIS-IN-THIS-ORDER sequence where order is load-bearing. Each step = a bolded imperative + 1-3 lines, and emits a named branch (`*Drives:* ELIMINATE vs CONTINUE`). Use when the decision is a pipeline of dependent calls.
2. **flowchart / gates** (`routine-placement`) — numbered gates with yes/no branches, each branch terminating in ONE named outcome, closing with a bolded **Net rule**. Use when the decision is a small set of mutually-exclusive destinations.
3. **gated-table** (Four Cs one-line test; ai-applicability scoring) — a table whose decisive column forces a cost/verdict (not a neutral feature list). Use when N items each get the same scored test.

Order/ranking must be **stated as a rule** ("in this order", "build bottom-up", "rows most-autonomous → least"), never merely implied.

## The canonical page skeleton

```
# <Framework Name> — <the decision it makes / the axis it optimizes>
    H1: name + dash-tail = the ONE question it answers (NOT a topic label).

<One-line summary — the exact sentence that also goes in references/index.md, verbatim.>

> Adapted from <Source>™. © <year> <author>.    (ONLY if borrowed IP — page-level attribution, Nate-Herk discipline)

**<The load-bearing fact / scoping line.>**    one bolded sentence isolating the single most decisive variable
    (3Ms "Boring is Beautiful"; routine-placement "only cloud surfaces survive a closed laptop").

## The decision rule        ← THE CORE. One of the three forms above. Every step/node/row emits a named branch or verdict.

## The verdict / scoring rubric    how answers collapse into a SMALL set of named verdicts via GATED conditions
    ("SKIP if ANY of…", "ADOPT only when ALL of…") + a "guide, not arithmetic" caveat + tie-breakers/defaults
    ("default to the lowest autonomy that works"). For pure ordered-rules frameworks this can fold into the last step.

## Stop-rules / tells       when NOT to act + falsifiable tells of a bad answer ("a claim of 100% is the tell of
    overselling"; "don't automate waste"). This is what makes the framework able to say NO to itself.

## Worked application (dogfood)   apply it to a REAL case and show the output (routine-placement re-classifies every
    live Servy routine and finds a defect; ai-applicability cites the IoT/MLOps run). Proves the rule yields an action.

## Wiring        ONLY for a decision framework Servy runs — names the skill(s)/CLAUDE.md triage that call this page as
    their gate + the standing one-line instruction. (Client/Jumpstart frameworks omit this — see Types.)

**Sources:** <knowledge/ raw file or URL, or the lived event it was distilled from; mark "(digest)" if summarizing one raw source>
**Related:** [[sibling-page]], [[another-page]]    ← liberal; an orphan is a lint failure
*Created <date>, <origin event>. Later expansions noted as separate dated edits.*
```
Filename: `references/<kebab-name>-framework.md` (flat, no subfolder, no frontmatter, prose-light). The `-framework` suffix is conventional, not mandatory (cf. `four-cs.md`).

## Quality gate (ALL must hold before it graduates)

1. **Actionable decision rule** in one of the three forms — not prose. (The non-negotiable.)
2. **One optimization axis / load-bearing fact** declared up front; every gate resolves to it. No generic pros/cons lists.
3. **Order/ranking stated as a rule** with consequence, not implied.
4. **Every step/node/row emits a NAMED branch or verdict** (the `*Drives:*` pattern) — a routable node, not a discussion prompt.
5. **Terminates in a small set of named verdicts** via gated `if ANY / only when ALL` conditions + "guide not arithmetic" caveat + tie-breakers/defaults — so two people converge on the same case.
6. **Falsifiable stop-rules + named tells/anti-patterns** — it can refuse itself.
7. **Concrete scales + recallable named units** (L0–L4, 60/30/10, the Bike Method), not adjectives.
8. **Dogfooded — ≥2 real applications where possible: one ACTION case AND one STOP/boundary case** (a one-example framework overfits and only ever says "yes"). If only one real case exists → file **provisional**, or keep as normal ingest until a second validates it.
9. **Grounded in real artifacts** where applicable (personal frameworks map to Servy files/CLIs/incidents).
10. **Satisfies the wiki page skeleton** — H1 dash-tail, index-equal one-liner, **Sources:**, **Related:** with ≥1 link, kebab filename, no frontmatter.
11. **Honest provenance** — page-level attribution blockquote if borrowed IP; dated origin + later-edit footer; borrowed authority quoted verbatim + labeled.

## Antipatterns (reject or fix)

- All prose, no decision rule (the cardinal sin — a topic page masquerading as a framework).
- A flat/unordered taxonomy presented as a framework (no stated order/dependency).
- Steps that don't branch (discussion prompts, not routable nodes).
- No terminal verdict, or verdicts by vibes instead of gated conditions.
- No stop-rules/tells — a framework that always says "yes, build it" is a sales pitch.
- Multiple competing axes (or none) with no capstone tie-breaker.
- Adjectives instead of scales ("low/med/high risk" with no defined ladder).
- Never dogfooded; orphan (missing index/Related/Sources); re-states content that belongs elsewhere; claims a wiring it doesn't actually have (wiring must be bidirectional + real).

## Two types — same skeleton, different client

**PERSONAL thinking/decision framework** (3Ms, Four Cs, routine-placement, ai-applicability's generic half): the client is Servy/Gera. Optimizes a Servy-internal axis. **Grounded in real Servy artifacts** (italic "Servy's <X>:" mappings; dogfood = a real Servy defect). **Carries a `## Wiring` section + gets a CLAUDE.md/skill pointer** — it changes Servy's behavior. Cross-links sibling Servy frameworks (3Ms↔Four Cs).

**GENERIC client/Jumpstart delivery framework** (ai-applicability's client half; jumpstart-program style): the client is an external customer's team. **Generic by design** ("no client specifics") so it's reusable across engagements; examples are anonymized archetypes. Optimizes a client-outcome axis (time/cost/quality, in the client's own words). Carries delivery habits (lead with where AI does NOT fit; borrow the client's words; sequence by dependency to earn trust). **No CLAUDE.md behavioral pointer / no `## Wiring`** — instead consumed by a delivery skill (`/jumpstart`, `/forge`) and cross-links `jumpstart-program` + the **SoftServe data-boundary as a HARD GATE** (customer IP can independently force a stop). Canonical dual-pattern (ai-applicability): the runnable **`## The generic version`** (per-question acceptance criteria + a falsifiable verdict) is **mandatory and primary** — it IS the framework. The client-proposal narrative is optional wrapper material around it, never a substitute for the decision rule.

## Graduation (wiki-protocol)

1. Confirm the **quality gate** is met. If all prose / no decision rule → it does NOT graduate; fix or route to normal ingest.
2. **Write** `references/<kebab>-framework.md` to the skeleton.
3. **Update `references/index.md`** — one entry under the right category, summary IDENTICAL to the page's one-liner.
4. If distilled from a `knowledge/` raw source → **register it in `knowledge/README.md`** (raw→digest) + mark "(digest)" in the title. If from a lived event → record that origin in the footer.
5. **Append to `references/log.md`**: `## [YYYY-MM-DD] create | <Framework Name>` (use `update` for later expansions).
6. **Cross-links**: a `**Related:**` line with ≥1 `[[sibling]]` AND ≥1 page (or the index) linking back — no orphans.
7. **Build-triage reflex** (wiki-protocol 3.5): self-ask "does this back a skill / agent / team / routine?" — for a decision framework the answer is usually "it backs a skill" (→ Wiring). "Nothing to build, here's why" is valid.
8. Optionally fire `warden` / `wiki-audit` to lint before considering it filed.

## Wiring rule (decision frameworks only)

**WHEN:** only when it's a decision rule Servy runs repeatedly (terminates in named verdicts that change what Servy does). One-off or generic-client frameworks get no CLAUDE.md pointer.
**HOW (most get ≥2):** (1) **skill gate** — a skill's SKILL.md names this page as its source-of-truth decision content (ai-apply ↔ ai-applicability; routine-placement is the gate `/routines-builder` runs; Four Cs is what `/audit` scores). (2) **CLAUDE.md pointer** — a one-line entry under the relevant triage/section (NOT inline detail; 200-line budget). (3) **standing behavioral hook** — a one-line standing instruction when the rule should fire every turn (the Default Shift).
**PROPOSE-THEN-CONFIRM:** never auto-edit CLAUDE.md or a SKILL.md. Propose the exact one-line pointer + which section, show the diff, wait for explicit yes. The page's own `## Wiring` section can ship (it's wiki prose Servy owns); the cross-system pointer is gated. Wiring must be **bidirectional** (page names the skill AND the skill/CLAUDE.md names the page) or it's drift.
