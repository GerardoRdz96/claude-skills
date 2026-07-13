---
name: agent-builder
description: Invoked explicitly via /agent-builder (model auto-invocation is disabled — natural asks like "make me an agent" won't fire it). Guides building, optimizing, or auditing Claude Code subagents (.claude/agents/*.md), and decides whether something should be an agent at all. Runs a decision gate and Discovery Interview before writing files.
argument-hint: [agent name or what it should do]
disable-model-invocation: true
---

## What This Skill Does

Guides the creation, optimization, and auditing of Claude Code **subagents** using official best practices and Servy's conventions. A subagent is a specialized Claude instance with its own clean context window, its own system prompt, and (optionally) a restricted toolset — defined in a single markdown file at `.claude/agents/<name>.md`.

Use this whenever:

- Building a new subagent from scratch
- Deciding **whether** a job should even be a subagent (vs a skill, a script, or a multi-brain route)
- Optimizing or auditing an existing subagent
- Troubleshooting an agent that isn't getting invoked or isn't behaving

This is the agent-side sibling of `/skill-builder`. Same discipline: **decision gate and Discovery Interview first, files second.** Full technical reference (frontmatter schema, tool restriction, model selection, prompt patterns, troubleshooting) lives in [reference.md](reference.md).

---

## Quick Start: What Is a Subagent?

A subagent is a separate Claude that the main session (the orchestrator) delegates a task to. It runs in an **isolated context window** — it does NOT see the main conversation history, only the task prompt it's handed plus its own system prompt and `CLAUDE.md`. It does its work, then returns a final message. That returned text is the *only* thing that re-enters the main context.

**Why that matters:** subagents are a context-management tool first. They keep noisy, token-heavy work (broad searches, log trawls, multi-file reads) out of the main thread, and they let you pin a narrow role + restricted tools + a cheaper model to a repeatable job.

### Agent vs Skill vs Script vs Multi-brain route

The single most common mistake is building an agent for something that should be a skill. Use this table:

| You want… | Use | Why |
|---|---|---|
| A reusable **workflow / SOP** Claude follows in the main thread | **Skill** (`/skill-builder`) | Stays in conversation, can be interactive, no context isolation needed |
| A **clean context window** for a self-contained, token-heavy, or repeatable job | **Subagent** (this skill) | Isolation is the whole point |
| Deterministic, non-LLM work (parse, transform, call an API) | **Script** (`scripts/`) | Cheaper, faster, 100% reliable — no model needed |
| A task a **different model lineage** does better (live web, math, multimodal, adversarial review) | **Multi-brain route** | Different architecture = different strengths and blind spots |

**Servy-specific:** a subagent is still Claude. For *adversarial review of Claude's own output*, a Claude subagent shares the same blind spots — route to **Codex** under the No-Self-Review Law, not a review subagent. For tooling, follow **CLI > API > MCP**. (See CLAUDE.md.)

---

## Mode 1: Build a New Agent

### Step 0 — The Decision Gate (do this FIRST, before any interview)

Before designing anything, pressure-test whether a subagent is the right tool. Ask yourself and, if unclear, the user:

1. **Does this need an isolated/clean context?** If the work is light and belongs in the main thread → it's a **skill**, not an agent. Stop and recommend `/skill-builder`.
2. **Is it deterministic with no judgment?** (parse a file, hit an API, transform data) → it's a **script**. Stop and recommend writing `scripts/<name>.py`.
3. **Would another model lineage do it better?** (current web info, heavy math, video/audio/PDF, adversarial second opinion) → it's a **multi-brain route**, not a Claude subagent.
4. **Is it repeatable and worth pinning a role + tools + model to?** If it's a one-off, just do it inline — don't build an agent.

If none of 1–4 redirect you, a subagent is justified. State **one sentence** on why ("needs a clean context window for repeatable X"), then proceed. If the user insists on an agent after a redirect, build it — but note the recommendation in your summary.

### Step 1 — Discovery Interview

Ask with AskUserQuestion, one round at a time. Skip any round the user already answered upfront. Keep going until you're 95% confident you can build the agent without further guessing.

**Round 1: Role & Name**
*Why: the role defines the system prompt; the name gives the agent an identity Gera (and the orchestrator) refer to it by.*
- What is this agent's single job? (One agent = one clear responsibility. If it's two jobs, that's two agents.)
- **Name it like a character, not a function.** Servy's agents get a *persona name that evokes the job* — a reader should sense what it does from the name (`warden` guards the wiki, `scribe` writes up calls, `scout` goes and finds things), but it should have personality, not read like a label (`wiki-linter`, `transcript-summarizer`). Rules: lowercase-hyphens, ≤64 chars, matches the filename, reasonably unique. The name can be whimsical because **delegation keys off the `description`, not the name** — so a fitting persona name costs nothing in discoverability as long as the description carries strong trigger words. Suggest 2–3 candidates and let Gera pick.

**Round 2: Invocation & Scope**
*Why: this sets `description` (how the orchestrator decides to delegate) and location.*
- When should it be invoked? Give 2–3 natural triggers ("when I drop a transcript in knowledge/", "after I finish a wiki page").
- Should the main session invoke it **proactively** (auto), or only when explicitly asked? (Proactive → say so in the description.)
- **Project-level** (`.claude/agents/`, Servy-only) or **user-level** (`~/.claude/agents/`, every project)?

**Round 3: Tools & Model**
*Why: least-privilege tools and right-sized model are what make an agent safe and cheap.*
- What tools does it actually need? Default to the **minimum** (e.g. read-only research = `Read, Grep, Glob`). Omit `tools` only if it genuinely needs everything.
- Does it write files / run commands / hit the network? (Each expands the toolset deliberately.)
- Model: `haiku` (cheap/bulk/search), `sonnet` (default workhorse), `opus` (hard reasoning), or inherit? See [reference.md](reference.md) for the rubric.

**Round 4: Inputs, Process & Output Contract**
*Why: a subagent only returns its final message — the output contract is the deliverable.*
- What does it receive in its task prompt? (Files to read, a target path, a question.)
- Walk the process: step 1, step 2, … What must it do before anything else (e.g. mandatory reads)?
- **What exactly does it return?** Structured findings? A file it wrote + a one-line summary? Be precise — vague output contracts produce useless agents.

**Round 5: Guardrails & Edge Cases**
*Why: agents act semi-autonomously; boundaries prevent surprises.*
- What should it NOT do? (Hard boundaries — e.g. "never modify source, only write to the report file.")
- Failure modes? (Empty input, missing file, ambiguous request — what should it do?)
- Cost/scope limits? (e.g. "cap at N files", "don't spawn work beyond X.") Note: subagents **cannot** spawn their own subagents — one level only.

**Round 6: Confirmation**
Summarize back in this format, then ask "Does this capture it?":

```
## Agent Summary: [name]

**Role (one sentence):** [the single job]
**Location:** .claude/agents/[name].md  (or ~/.claude/agents/)
**Invocation:** [proactive | on-request] — triggers: [phrases]
**Tools:** [minimal list, or "inherit all" + why]
**Model:** [haiku|sonnet|opus|inherit] — [why]

**Process:**
1. [step]  2. [step]  …

**Returns:** [the exact output contract]
**Guardrails:** [what it must not do; failure handling]
```

Only build after the user confirms.

### Step 2 — Build Phase

Write `<location>/<name>.md` with this structure:

**Frontmatter** (only the fields you need — see [reference.md](reference.md) for the full schema):
```yaml
---
name: <name>                    # matches filename, lowercase-hyphens
description: <when to use this agent>   # include triggers; add "use proactively" if auto
tools: Read, Grep, Glob         # OMIT to inherit all; otherwise least-privilege
model: sonnet                   # OMIT to inherit; set only if a tier is clearly right
color: cyan                     # optional, display only
---
```

**Body = the system prompt.** Servy house style (matches the 33 installed GSD agents) uses XML-tagged sections:
- `<role>` — **open by naming the persona** ("You are **Warden**, the keeper of Servy's wiki."), then state its single job and (if applicable) what spawns it. The name and the role should agree — the identity reinforces the boundary (a *warden* guards, doesn't rewrite). Include a **Mandatory Initial Read** line if the task prompt will carry a `<required_reading>` block.
- Process — numbered, literal steps. Claude follows these exactly.
- Output contract — the precise shape of the returned message or written file.
- Constraints — what NOT to do, failure handling, scope caps.

**Always-on output-contract section for investigative/reporting agents.** If the agent does investigative or reporting work (a reviewer, a research/explorer, an auditor, or anything that explores then summarizes back to the main thread), its output contract MUST end with an **Obstacles Encountered** section. The subagent returns only its final message, so any setup quirk, workaround, special flag, or problem dependency it hit is lost unless it reports it, and the main thread then rediscovers the same fix and burns time and tokens. Append this to the output contract verbatim:

```
**Obstacles Encountered:** Report setup issues, workarounds applied, environment quirks, commands that needed a special flag or config, and dependencies/imports that caused problems. Write "none" if the work was clean.
```

Skip this only for a trivial one-shot transform agent (deterministic in/out, no exploration, nothing to discover), where it adds noise. When in doubt (the agent reads, searches, or reviews before answering), include it.

Rules:
- **One responsibility per agent.** Two jobs = two agents.
- **Least-privilege tools.** Never grant write/Bash unless the job needs it.
- **Write the description for delegation**, not for humans — it's how the orchestrator decides to call it. Lead with the trigger condition.
- Keep it focused. A tight system prompt beats a sprawling one.

### Step 3 — Document & Register

- Add a one-line entry to `CLAUDE.md` (under a "Your agents" area or alongside skills): agent name, what it does, when it fires, project vs user level. Per Servy's standing rule, update CLAUDE.md in the **same session** a capability is added.
- If the agent is part of a recurring ritual, note it so `/audit` counts it toward Cadence.

### Step 4 — Verify

Subagents can't be "unit tested," but verify:
1. **Frontmatter parses** — `name` matches filename, `description` present, `tools`/`model` valid.
2. **Discoverability** — the agent appears in the Agent/Task tool's list and the `description` contains the words you'd actually use to trigger it.
3. **Dry delegation** — hand it a representative task and confirm it (a) reads what it should, (b) stays in scope, (c) returns the agreed output contract.
4. **Tool fit** — it has every tool it needs and nothing it doesn't (a denied tool mid-run = missing permission).

Report what you checked. Don't claim it works without a dry run.

---

## Mode 2: Optimize an Existing Agent

Read the agent file first — never propose changes to an agent you haven't read. Then look for:

- **Over-privileged tools** → tighten to least-privilege. Read-only? Drop Write/Edit/Bash.
- **Wrong model** → bulk/search work on opus is waste; hard reasoning on haiku is fragile. Right-size it.
- **Weak description** → if it's not getting invoked, the description lacks the trigger words; if it fires too often, it's too broad. (See Troubleshooting in [reference.md](reference.md).)
- **Fuzzy output contract** → pin down exactly what it returns.
- **Two-job creep** → split into focused agents.
- **Missing mandatory reads / guardrails** → add them.

Show the diff and the *why* for each change before applying.

---

## Mode 3: Audit an Existing Agent

Read the file, then run the **full audit checklist in [reference.md](reference.md) § "Mode 3 Audit Checklist"** — it covers frontmatter (name/description hygiene, the ~120-word progressive-disclosure cap, the skill↔subagent collision grep, least-privilege tools), system prompt (single responsibility, persona role, output contract + Obstacles Encountered), integration, and quality. Fix issues before marking complete.

After the agent ships, run the **misfire-tuning loop** — watch the first 3–5 invocations, diagnose why it did/didn't fire, rewrite the description, re-test. Full loop + YAML hygiene tip: [reference.md](reference.md) § "Live Trigger Checks".

---

## Complete Example

A full worked example — `.claude/agents/warden.md`, showing the persona name, trigger-rich description, XML-tagged body, and the Obstacles Encountered contract — lives in [reference.md](reference.md) § "Complete Example: warden".

---

## Recommended Conventions

- Project agents → `.claude/agents/<name>.md`. Cross-project agents → `~/.claude/agents/<name>.md`.
- One responsibility per agent. **Name it as a persona that evokes the job** (`warden`, `scribe`, `scout`) — characterful, not a flat label. The `<role>` opens by naming that persona; the `description` stays functional and trigger-rich (that's what the orchestrator matches on, so the name is free to have personality).
- Least-privilege tools by default. Read-only research agents get `Read, Grep, Glob`.
- Match the house style: XML-tagged system prompt (`<role>`, process, output contract, constraints).
- Document every agent in CLAUDE.md the same session you build it.
- For review of Claude's own work, prefer a Codex route over a Claude review agent.

## Important Notes

- **Decision gate is not optional.** Most "I need an agent" requests are really skills or scripts. Run the gate first.
- **Always read an existing agent before optimizing or auditing it.**
- **Subagents are one level deep** — they cannot spawn their own subagents. Design accordingly.
- A subagent's returned message is its entire deliverable to the main thread. The output contract is the product.
- For the full frontmatter schema, tool/model rubrics, prompt patterns, and troubleshooting, see [reference.md](reference.md).
