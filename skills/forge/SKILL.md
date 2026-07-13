---
name: forge
description: Use when Gera says "let's build", "kick off a project", "I want to build X for Y", "build something for <client>", "/forge", or starts any work for a freelance client or new Penguin Alley product. Runs a 5-phase kickoff-to-production pipeline — (1) onboarding + grill via the forge-discovery agent, (2) Superpowers spec + plan, (3) GSD execution, (4) Codex review + fix + Codex review 2, (5) production deploy. REFUSES structurally if invoked on SoftServe customer work — customer IP must never enter Servy. Penguin Alley freelance client work IS allowed (PERSONAL mode). The end-to-end pipeline Gera uses with clients.
---

# `/forge` — kickoff-to-production for Penguin Alley products + freelance clients

Owns the complete lifecycle from "I have an idea / a new client" to "it's running in production." Composes existing Servy primitives into one disciplined arc. No new machinery beyond the Phase 1 subagent and the two-pass Codex loop.

## Pipeline (5 phases, linear)

### Phase 0 — Triage + refusal guard ⛔ (synchronous, blocks everything)

Reads cwd and args, then **runs** `python3 scripts/claude-tier.py` (don't read its source — the tier verdict is its output; exit 0 = personal, 2 = softserve/managed). **Refuses** with a one-line policy message if:
- `cwd` contains `engagements/` (SoftServe engagement directory pattern)
- Any arg matches a SoftServe customer name
- Tier check returns SoftServe Enterprise context for the work

**Penguin Alley freelance clients ARE allowed.** Penguin Alley is Gera's independent freelance identity, separate from SoftServe employment. The guard only blocks SoftServe-customer work, not freelance work under Penguin Alley.

**the client-Test:** confirm there's a real named person, product, or business-line behind this. Pretend projects abort.

Writes `forge/<date>-<slug>/CAPTURE.md` — single Gera-readable resume file. If context resets mid-pipeline, `CAPTURE.md` is the recovery surface.

**Gate:** hard-stop on refusal OR the client-Test fail.
**Refusal message:** *"This skill is personal/freelance-only. For SoftServe engagement work see `/jumpstart` and the Authorized AI Tools Register. Customer IP must never enter Servy."*

### Phase 1 — Onboarding + Discovery (delegated to `forge-discovery` agent)

**Idea gate first (`/roast`, money pipeline).** For a **new Penguin Alley product / self-initiated bet** (not a paying client who already committed), run **`/roast`** before sinking discovery + build time — GO/RESHAPE/KILL + cheapest 48h test. A KILL here saves the whole engagement; a RESHAPE sharpens what you onboard. Skip when a client has already decided and paid to build their thing. Source: `references/nate-money-upgrades.md`.

Dispatch the `forge-discovery` subagent. The agent:
1. **Client onboarding** (if there's a freelance client) — one question at a time: client identity, business context, stack constraints, budget, timeline, success definition, escalation contact, existing surfaces.
2. **Product grill** via the existing `/grill-me` skill — what the product solves, who the user is, MVP features, deferred, brand/voice.

Agent captures **everything into one file** at `knowledge/grills/<date>-<slug>.md` (two sections: ONBOARDING then PRODUCT). Appends 5–10 verbatim voice samples to `CAPTURE.md` for the Phase 2 voice-anchor.

**Brand assets (standing convention):** during onboarding, ask the client for their **logo + brand guidelines** (colors, typography, icons) and collect the files into `brand_assets/` at the client-repo root. Swipe files ground *style*; `brand_assets/` grounds *identity* (`references/design-swipe-file.md`). No assets yet → note it as an open flag with an owner. Source: Nate 6h course 2026-07-11 [2:54:44].

**Gate:** discovery checkpoint reached ("done, complete") + open flags itemized with owners.
**Skill composed:** `/grill-me`, plus the agent's onboarding SOP.

### Phase 2 — Superpowers (brainstorm + spec + plan)

Fires `superpowers:brainstorming` (compressed mode — grill covered ~70%) → asks 3–5 targeted technical Q's (auth shape, tenancy primitive, repo shape, testing, backup/CI/CD, UI library, brand placement). **HARD-GATE: design approved before any plan is written.**

Then `superpowers:writing-plans` → writes two artifacts:
1. **Design spec** → `docs/superpowers/specs/<date>-<slug>-design.md`
2. **Implementation plan** → `docs/superpowers/specs/<date>-<slug>-plan.md` (bite-sized TDD tasks where bug-cost dominates)

Voice-anchor calibration on user-facing copy strings against the verbatim samples from Phase 1.

**Client-repo project CLAUDE.md (two standing clauses, written before build starts):**
1. **Brand reference:** point it at `brand_assets/` so every visual build reads the logo + guidelines *before* any visual work (pairs with the Phase 1 collection convention).
2. **Local-as-staging clause** — mandatory whenever the deploy target auto-deploys from git (GitHub→Vercel, Cloudflare Pages): *"Changes pushed to GitHub auto-deploy to production. Always test on localhost until Gera explicitly says to push/commit."* Push = production deploy; the clause keeps bad changes off the live site (`references/pa-deploy-stack.md`). Source: Nate 6h course 2026-07-11 [3:14:36].

**YAGNI gate:** before the plan is final, run it through `/ponytail` — cut every step/dependency/abstraction that doesn't earn its place. Client work especially rewards shipping the smallest correct slice. Never cut validation/security/data-loss/accessibility.
**Gate:** plan passes spec-coverage + no-placeholders + type-consistency self-review.
**Skills composed:** `superpowers:brainstorming`, `superpowers:writing-plans`, `/ponytail`.

### Phase 3 — GSD (execute the plan)

Hands off to `/gsd-execute-phase` for wave-based execution (atomic commits, deviation handling, checkpoint protocols, state management). Use `/gsd-autonomous` only if the plan is well-bounded and Gera explicitly opts in to full autopilot.

End-of-phase state: shipped code in the target repo, all GSD tasks complete, tests green.

**Self-verify before the gate (standing rule):** execution prompts end with the verify-own-work instruction — *once built, verify as a human would: run it, click through it (Playwright for web), walk it as 3 personas (beginner / engineer / business owner) and fix what the walkthrough surfaces before reporting done.* This fires **before** Phase 4, so Codex reviews code that already survived its own walkthrough (~70%→92% first-pass lift; doctrine in `references/claude-code-power-skills.md`). **For UI / user-facing surfaces, use `/verify-loop`** as the formalized walkthrough — definition-of-done loop + adversarial stress-test (`references/nate-money-upgrades.md`).

**Gate:** GSD reports phase complete + tests pass + no UAT items outstanding.
**Skill composed:** `/gsd-execute-phase` (or `/gsd-autonomous` when invoked).

### Phase 4 — Codex review → fix → Codex review 2 (two-pass adversarial loop)

The No-Self-Review Law enforced as a tight loop. Codex reviews Claude's output, Claude applies the fixes, Codex re-reviews.

1. **Codex Review 1** — `multi-brain` Codex route reviews the GSD output. Findings captured to `forge/<date>-<slug>/codex-review-1.md` (must-fix / should-fix / nit categories).
2. **Fix pass** — Claude (this session) applies the Codex must-fix findings to the code. Commits each fix atomically using `/simplify` (which is `/code-review --fix`) where appropriate. **No new features, no scope creep** — only the review's must-fix items.
3. **Codex Review 2** — Codex re-reviews the fixed code. Goal: previous must-fix items confirmed resolved + no new must-fix surfaced. Findings captured to `forge/<date>-<slug>/codex-review-2.md`.

If Codex Review 2 surfaces a new must-fix, EITHER fix it inline (small, < 30min) OR escalate to Gera with a recommendation (large). No silent skips.

**Gate:** Codex Review 2 reports no must-fix outstanding.
**Skills composed:** `multi-brain` (Codex route via `codex:rescue`), `/simplify` (fix-pass), `/code-review`.

### Phase 5 — Production deploy

Final phase: ship to production. Five steps:

1. **Pre-deploy checklist:** environment configs set, secrets in `.env`, DB migrations dry-run clean, monitoring wired (Sentry / logs / health-check endpoint). **Front-End Review Law (if the product has a UI — mandatory):** it was built *through* `frontend-design` + `taste-skill` from a real design system (Phase 2/3, never hand-rolled defaults); `scripts/frontend-review.sh <preview-url>` returns `VERDICT: PASS` (vision-model anti-slop gate, a different lineage — no self-review for design); and a public-repo product ships a **README with images** (hero/banner + real screenshots + OG card). No PASS / no README images → do not deploy. Doctrine: `references/front-end-review-framework.md`.
2. **Deploy** — depends on stack:
   - Next.js → Vercel (`vercel --prod`)
   - Static → Cloudflare Pages (`wrangler pages deploy`)
   - Supabase migrations → `supabase db push` against prod project
   - Other stacks → platform CLI of record
3. **Smoke test** — fire `/verify` against the production URL. Confirms the golden path works for real users.
4. **Registry update** — promote in `projects/REGISTRY.md` from `kickoff` → `shipped`. Add: production URL, version, maintenance trigger block, post-ship known-issues.
5. **Decision log entry** — append a "shipped" line to `decisions/log.md` with the production URL, any caveats, and the per-project git identity used (per `feedback-local-only-no-git`).
6. **Go to market (`gtm-kit`, money pipeline).** For a Penguin Alley product or sellable offer, offer the **`gtm-kit`** workflow — idea → full go-to-market kit (positioning, ≥7-competitor market research, 14-day launch plan, outreach templates + drafts, content calendar) via 6 parallel agents. Shipping ≠ selling; this closes the loop. Source: `references/nate-money-upgrades.md`.

**Gate:** smoke test green + `projects/REGISTRY.md` updated + decision log entry written.
**Skills composed:** `/verify`, platform CLIs (Vercel / Cloudflare / Supabase), `git push`, `projects/REGISTRY.md` update.

## Artifacts produced

| Artifact | Path | When |
|---|---|---|
| Resume file | `forge/<date>-<slug>/CAPTURE.md` | Phase 0 |
| Grill + onboarding capture | `knowledge/grills/<date>-<slug>.md` | Phase 1 |
| Brand assets (logo + guidelines) | `brand_assets/` in the client repo | Phase 1 |
| Design spec | `docs/superpowers/specs/<date>-<slug>-design.md` | Phase 2 |
| Implementation plan | `docs/superpowers/specs/<date>-<slug>-plan.md` | Phase 2 |
| Shipped code | target repo | Phase 3 |
| Codex review 1 | `forge/<date>-<slug>/codex-review-1.md` | Phase 4 |
| Codex review 2 | `forge/<date>-<slug>/codex-review-2.md` | Phase 4 |
| Production URL + status | `projects/REGISTRY.md` | Phase 5 |
| Decision log entry | `decisions/log.md` | Phase 5 |
| Wiki page (optional) | `references/<slug>.md` | After ship — separate wiki-protocol pass |

## What `/forge` does NOT do

- **No automatic wiki graduate.** Wiki graduation moved to post-ship per `references/wiki-protocol.md` — n=1 project pages don't earn methodology pages until 3+ runs fit the same shape.
- **No HTML artifact bundle.** Standing rule (HTML for specs) applies only on explicit request — `/forge` does not auto-bundle.
- **No state spine (JSON).** `CAPTURE.md` is the human-readable recovery surface.
- **No parallel scouts during Phase 1.** Interview is the bottleneck.
- **No judge panel at Phase 4.** Two-pass Codex IS the gate — Codex → fix → Codex.
- **No `/ultra-review` offer in v1.** Gera fires it manually if he wants exhaustive coverage on top of the two-pass loop.

## When to use · when NOT to use

**Use `/forge` when:**
- Gera starts a brand-new product (Cleia-class, side projects, future Penguin Alley apps).
- A freelance client engagement kicks off under Penguin Alley.
- The arc needs the full kickoff → spec → ship → review → production loop.

**Do NOT use `/forge` when:**
- The work involves a SoftServe customer (refused structurally at Phase 0).
- The project already exists and just needs a feature (use `/build` directly).
- The idea is half-formed and needs exploration only (use `/grill-me` standalone).
- The task is operational — log an expense, ingest a video, run a routine (use the relevant single-purpose skill).

## References

- Design spec: `docs/superpowers/specs/2026-06-08-forge-skill-design.md` (v1 originally 6-phase; updated to Gera's 5-phase per goal 2026-06-09).
- Phase 1 agent: `.claude/agents/forge-discovery.md`.
- Sibling: `.claude/skills/build/SKILL.md` (owns plan-to-shipped for existing repos).
- Doctrine: `references/claude-code-power-skills.md` (Plan → Execute → Review).
- Policy fence: `references/softserve-ai-usage-policy.md`.
- Org chart context: `references/penguin-alley-org-chart.md` + `knowledge/grills/2026-06-08-tech-company-org-chart.md`.
