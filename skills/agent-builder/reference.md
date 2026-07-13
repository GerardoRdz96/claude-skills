# Agent Builder Reference

Complete technical reference for Claude Code **subagents**. Covers the frontmatter schema, tool restriction, model selection, system-prompt patterns, the skill↔agent relationship, and troubleshooting.

Source: https://code.claude.com/docs/en/sub-agents

---

## What a Subagent Actually Is

A subagent is a separate Claude invocation that the orchestrator (your main session) delegates a task to via the Agent/Task tool. Key properties:

- **Isolated context.** It does NOT see the main conversation. It receives: its own system prompt (the file body) + the delegation task prompt + `CLAUDE.md`. Nothing else.
- **Returns one message.** Its final message is the *only* thing that flows back into the main context. Everything else (its tool calls, intermediate reasoning, files it read) stays in its own context and is discarded.
- **One level deep.** A subagent cannot spawn its own subagents. Orchestration is the main session's job.
- **Optionally tool- and model-scoped.** You can pin a restricted toolset and a specific model per agent.

The headline value is **context management** + **role specialization**: keep token-heavy or noisy work out of the main thread, and pin a narrow, repeatable role.

---

## Agent vs Skill — the relationship

| | Subagent (`.claude/agents/`) | Skill (`.claude/skills/`) |
|---|---|---|
| **Context** | Isolated — no conversation history | Runs in the main conversation |
| **What it is** | A *who* — a specialized Claude with a system prompt | A *how* — a workflow/SOP Claude follows |
| **Interactive?** | No — fire-and-return | Yes — can ask the user mid-run |
| **Returns** | One final message | Continues the conversation |
| **Best for** | Token-heavy search, repeatable narrow jobs, restricted-tool work | Multi-step procedures, interactive flows, project conventions |

They compose in **two directions**:
- A **skill with `context: fork`** runs in a subagent: the agent type supplies the system prompt, the SKILL.md content becomes the task.
- A **subagent with a `skills:` field** preloads named skills into its context before it starts.

If the thing you're describing needs back-and-forth with the user, it's a skill. If it's a self-contained job you hand off and await a result from, it's an agent.

---

## Frontmatter Field Reference

A subagent file is `<name>.md` with YAML frontmatter + a markdown body. Only `name` and `description` are required.

| Field | Required | Type | Default | Description |
|-------|----------|------|---------|-------------|
| `name` | Yes | string | — | Identifier. Must match the filename. Lowercase letters, numbers, hyphens. Max 64 chars. **Servy convention:** make it a persona that evokes the job (`warden`, `scribe`), not a flat label — see SKILL.md Round 1. Safe because delegation keys off `description`, not `name`. |
| `description` | Yes | string | — | **When to use this agent.** This is how the orchestrator decides to delegate. Lead with the trigger condition. Add "use proactively" to encourage auto-delegation. May include `<example>` blocks. |
| `tools` | No | string (comma-separated) | inherit all | Allowlist of tools the agent may use. **Omit to inherit every tool.** Set it to enforce least-privilege. |
| `model` | No | string | inherit | `haiku`, `sonnet`, `opus`, or `inherit`. Omit to inherit the main session's model. |
| `color` | No | string | none | Display color in the UI (`red`, `green`, `cyan`, … or a hex like `"#F59E0B"`). Cosmetic only. |
| `memory` | No | string | `project` | Memory scope the agent wakes up with: `project` \| `none` \| `user` \| `local`. Default `project`; pick `none` when you want an **innocent reviewer** that wakes up completely blind, no prior context (pairs with the unbiased-reviewer delegation signal). `user`/`local` almost never — Nate (6h course, 2026-07-11): "between project, user, and local, I'm probably always going to choose project." |
| `max_turns` | No | integer | none | Hard cap on the agent's turns before it must return — the runaway-control brake (e.g. `max_turns: 10` for research loops). The subagent-layer implementation of the loops-builder numeric hard cap: set it on loop-prone agents, omit for one-shot transforms. |
| `hooks` | No | object | none | Lifecycle hooks scoped to this agent (PreToolUse/PostToolUse/Stop). Same shape as skill/settings hooks. |

> The 33 GSD agents installed in this environment all set exactly `name`, `description`, `tools`, `color`. That's the reliable, house-standard minimum. Add `model` only when a tier is clearly right; add `memory: none` only for innocent reviewers; add `max_turns` only on loop-prone agents; add `hooks` only when you need lifecycle automation.

### `description` — write it for the orchestrator

The orchestrator reads only the `description` to decide whether to delegate. Make it a **trigger spec**, not a brochure:

- ✅ "Use proactively after a transcript lands in knowledge/. Summarizes it and extracts action items. Returns a structured digest."
- ❌ "A helpful agent that works with transcripts and other things."

Including `<example>` blocks (context → user line → why this agent fires) measurably improves routing for agents with subtle triggers. Example:

```
description: >
  Use when the user asks to refactor or assess refactor impact across the repo.
  <example>
  Context: user is about to change a shared module.
  user: "What breaks if I change the auth signature?"
  assistant: "I'll delegate to refactor-impact to trace callers across the repo."
  </example>
```

---

## Tool Restriction — least privilege

Omitting `tools` inherits **all** tools (including Bash, Write, Edit, network, MCP). That's rarely what you want. Pick the minimum:

| Job type | Recommended `tools` |
|---|---|
| Read-only research / search | `Read, Grep, Glob` |
| Research + write a report file | `Read, Grep, Glob, Write` |
| Code analysis that runs commands | `Read, Grep, Glob, Bash` |
| Implementer that edits code | `Read, Edit, Write, Bash, Grep, Glob` |
| Web research | `WebSearch, WebFetch, Read` |

Rules of thumb:
- A **review/audit agent should be read-only** — it reports, it doesn't fix. (Findings → orchestrator decides.)
- Grant `Bash`/`Write`/`Edit` only when the output contract genuinely requires mutation.
- Tool names match the orchestrator's tools. A tool the agent lacks mid-run surfaces as a missing capability, not a permission prompt — so under-granting silently breaks the agent. Match tools to the process steps exactly.

---

## Model Selection rubric

| Model | Use for | Cost |
|---|---|---|
| `haiku` | High-volume, mechanical, or search-heavy work — file discovery, classification, bulk passes, simple extraction | Cheapest |
| `sonnet` | The default workhorse — most analysis, summarization, structured generation, code review | Mid |
| `opus` | Genuinely hard reasoning — architecture decisions, multi-constraint planning, subtle bug hunts | Highest |
| omit (`inherit`) | When the agent should track whatever the session is using | — |

Heuristics:
- If the agent fans out across many files just to *find* things → `haiku` (this is what the built-in `Explore` agent uses).
- If it produces a judgment a human would trust → `sonnet` minimum.
- Don't put bulk search on `opus` (waste) or hard reasoning on `haiku` (fragile).

---

## System-Prompt Patterns (the body)

The markdown body IS the agent's system prompt. Servy's house style (and the GSD agents') uses XML-tagged sections for clarity:

```markdown
<role>
You are [identity]. Your single job: [one responsibility]. Spawned by [what], to produce [what].

**CRITICAL: Mandatory Initial Read** — If the prompt contains a `<required_reading>` block, Read every file listed there before doing anything else.
</role>

## Process
1. [literal step]
2. [literal step]
...

## Output contract
Return [exact shape]. If [edge case], [what to do].

## Constraints
- [hard boundary]
- [failure handling]
- [scope cap]
```

Why each part:
- **`<role>`** — anchors identity and the *single* responsibility. Multi-job agents drift; keep it to one.
- **Mandatory read pattern** — because the agent has no conversation history, the orchestrator passes context via a `<required_reading>` block in the task prompt. Telling the agent to read those first makes hand-offs reliable.
- **Numbered process** — Claude follows literal steps far more consistently than prose.
- **Output contract** — the returned message is the entire deliverable. Specify structure (headings, fields, a written file path + summary line).
- **Constraints** — agents act semi-autonomously; state what NOT to do and how to handle empty/ambiguous input.

### `ultrathink`
Including the word `ultrathink` anywhere in the body activates extended thinking for that agent — worth it for genuine reasoning agents (architecture, root-cause), wasteful for mechanical ones.

---

## File Locations & Precedence

| Location | Path | Scope | Precedence |
|---|---|---|---|
| Project | `.claude/agents/<name>.md` | This project only | Wins over user on name clash |
| User | `~/.claude/agents/<name>.md` | All your projects | Lower |
| Plugin | `<plugin>/agents/<name>.md` | Where plugin enabled | Namespaced |

For Servy: default to **project** (`.claude/agents/`) for Servy-specific jobs; use **user** (`~/.claude/agents/`) for agents you want available in every repo you open.

---

## Hooks in Agents (optional)

Agents can declare lifecycle hooks that run only while the agent is active. Same shape as skill/settings hooks:

```yaml
hooks:
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "npx eslint --fix $FILE 2>/dev/null || true"
```

Events: `PreToolUse` (before a tool), `PostToolUse` (after), `Stop` (agent finishes → runs as SubagentStop). Exit 0 = allow, exit 2 = block. Use sparingly — most agents need none.

---

## Servy Integration Notes

- **No-Self-Review Law.** A Claude subagent reviewing Claude's output has the same architecture, hence the same blind spots. For adversarial review/verification of work the main session produced, route to **Codex** (`/codex:review`, `/codex:rescue`) — do not build a Claude review agent for that purpose. A Claude *finder* agent (different task, e.g. "list candidate issues") is fine; a Claude *judge* of Claude's own work is not.
- **CLI > API > MCP.** When an agent needs to reach an external system, prefer a printed CLI, then a `scripts/` API integration, then MCP last. Grant the agent only the tool that mechanism needs.
- **Multi-brain boundary.** Subagents are Claude-only. If the *better* worker is another lineage (Grok for live web, DeepSeek for math, Gemini for multimodal/whole-repo), that's a multi-brain route the orchestrator makes — not a subagent.
- **Cadence.** If an agent is part of a recurring ritual, document it so `/audit` credits it toward the Cadence pillar.

---

## Troubleshooting

### Agent never gets invoked
- The `description` doesn't match how the task is phrased. Rewrite it as a trigger spec with the actual words used; add `<example>` blocks.
- It's not auto-delegating when you want it to → add "use proactively" to the description.
- Confirm it's discoverable: ask the session "what agents are available?" and check the name appears.

### Agent invoked when it shouldn't be
- `description` is too broad. Narrow the trigger condition. Remove "proactively" if you only want explicit delegation.

### Agent returns nothing useful / empty
- The body is guidelines without an actionable task, OR the output contract is unstated. Add an explicit "Return X" contract.
- It depended on conversation context it never received. Move that context into the task prompt's `<required_reading>` or restate it in the body.

### Agent stops mid-task or skips a step
- It's missing a tool the step needs (e.g. needs `Bash` but `tools` omitted it). Add the tool. Under-granting silently breaks the process.

### Agent does too much / drifts
- Two responsibilities crammed into one agent. Split into two focused agents.
- Model too small for the reasoning required → bump `haiku`→`sonnet`→`opus`.

### Agent tried to spawn another agent
- Not supported — one level deep. Move the orchestration up to the main session.

---

## Mode 3 Audit Checklist

Run this when auditing an existing agent (SKILL.md Mode 3). Fix issues before marking complete.

**Frontmatter**
- [ ] `name` matches the filename
- [ ] `description` leads with the trigger condition and uses natural keywords; says "proactively" iff it should auto-fire
- [ ] **Description fits the progressive-disclosure tax.** The description loads on EVERY orchestrator turn (whether the agent fires or not); the body loads only on match. Bloated description = per-turn token waste. Cap: ~120 words. If the description is longer, trim — move detail into the body. (Per Nate's subagents doctrine — see `references/claude-code-subagents.md` § "Progressive disclosure".)
- [ ] **No skill ↔ subagent trigger collision.** Run a collision grep before merging:
  ```
  grep -rE "description:" .claude/skills/*/SKILL.md | grep -iE "<trigger phrase 1>|<trigger phrase 2>"
  ```
  Test each of the agent's primary trigger phrases against every active skill description. If any skill has a near-identical trigger, the skill usually wins (Nate's `roast` skill stole his `plan-roaster` subagent's trigger live on camera). Fixes, in order of cleanliness:
  1. Compose — have the skill explicitly invoke the agent in its body (skill = trigger, agent = clean-context worker).
  2. Disambiguate — make the agent's trigger language unambiguously distinct from the skill's.
  3. Add an explicit defer-to-X note in the agent description for the overlapping case (e.g., "Note: for 'what should I automate next' defer to `/level-up` — that's tooling, not product work.").
- [ ] `tools` is least-privilege (or omitted deliberately because it truly needs all)
- [ ] `model` is set only when a tier is clearly right; otherwise omitted to inherit
- [ ] No unnecessary fields

**System prompt (body)**
- [ ] Single, clear responsibility — not two jobs
- [ ] `name` is a persona that evokes the job (`warden`, `scribe`), not a flat label; the `<role>` opens by naming that persona
- [ ] Numbered, literal process steps
- [ ] Explicit output contract (what it returns / writes)
- [ ] **Investigative/reporting agent (reviewer, research/explorer, auditor) → output contract ends with an "Obstacles Encountered" section** so workarounds surface in the summary instead of being rediscovered by the main thread. Trivial one-shot transform agents are exempt.
- [ ] Mandatory initial reads stated if a `<required_reading>` block is expected
- [ ] Constraints + failure handling present
- [ ] No reliance on conversation history it won't have

**Integration**
- [ ] Documented in CLAUDE.md
- [ ] Doesn't duplicate a skill or script that already does the job
- [ ] If it's a review-of-Claude agent → flagged: should this be a Codex route instead? (No-Self-Review Law)

**Quality**
- [ ] A clean Claude with no prior context could execute it from the prompt alone
- [ ] Tools match the work (nothing missing, nothing extra)
- [ ] Right-sized model for cost

---

## Live Trigger Checks (post-install — the misfire-tuning loop)

Agents drift in two directions: they fire when they shouldn't, or they don't fire when they should. **Both are description bugs**, not body bugs. After the agent ships, watch the first 3–5 invocations and run the loop:

1. **Spot a misfire.** Either Gera says "you should have used `<agent>` here" (silent failure) or `<agent>` fires on a turn it shouldn't (false positive).
2. **Ask Claude *why* it did / didn't fire.** The canonical prompt:
   > *"Read the description of `.claude/agents/<agent>.md` and look back at my prompt. Help me understand why you did/didn't fire so we can make this better."*
3. **Rewrite the description from Claude's diagnosis.** Usually one of: trigger phrase too generic / too specialized, missing "use proactively" cue, collision with a competing skill (run the collision grep above), or a phrase that means something different to Claude than to Gera.
4. **Confirm with a re-test.** Re-issue the original prompt; verify the agent now fires (or doesn't) as expected.

**YAML hygiene tip:** unterminated quotes, missing colons, or stray `:` characters silently break the front-matter (Nate's own demo hit this — his `plan-roaster` stubbornly wouldn't fire because he left a quote unclosed). When a brand-new agent refuses to fire, suspect the YAML before the description.

This loop is the discipline that separates 99% of subagent owners from Nate's "better than 99%" target. Do it.

---

## Complete Example: warden

**File:** `.claude/agents/warden.md` — note the persona name (`warden`), not a label like `wiki-linter`. The `description` stays functional and trigger-rich; that's what the orchestrator matches on.

```yaml
---
name: warden
description: Use proactively after editing references/ wiki pages, or when asked to lint the knowledge wiki. Checks for contradictions, stale claims, broken [[links]], orphans, and index drift. Read-only — reports findings, never edits.
tools: Read, Grep, Glob
model: sonnet
color: green
---

<role>
You are **Warden**, the keeper of Servy's knowledge wiki. Your single job: audit the references/ wiki for integrity issues and return a findings report. You never edit files — you report, the orchestrator decides. (The name holds the boundary: a warden guards, it doesn't rewrite.)

If the prompt contains a `<required_reading>` block, Read every file listed there first.
</role>

## Process
1. Read references/index.md (the catalog) and references/wiki-protocol.md (the rules).
2. Glob references/*.md. For each page, check:
   - Contradictions against other pages or the index.
   - Stale claims (dates, versions, "currently…" that may have moved).
   - Broken [[links]] — targets that don't resolve to an existing page.
   - Orphans — pages not listed in index.md.
   - Index drift — index entries pointing at renamed/removed pages.
3. Cross-check the index against the actual file list.

## Output contract
Return a markdown report grouped by issue type. For each finding: file path, the problem, and a one-line suggested fix. End with a count summary. If the wiki is clean, say so explicitly.

**Obstacles Encountered:** Report setup issues, workarounds applied, environment quirks, commands that needed a special flag or config, and dependencies/imports that caused problems. Write "none" if the work was clean.

## Constraints
- Read-only. Never use Write or Edit (you don't have them).
- Don't invent issues to seem thorough — report "clean" when it's clean.
- Cap at the references/ tree; don't wander into knowledge/ or source code.
```

---

## Related Documentation

- **Subagents:** https://code.claude.com/docs/en/sub-agents
- **Skills:** https://code.claude.com/docs/en/skills  (and the sibling `/skill-builder`)
- **Hooks:** https://code.claude.com/docs/en/hooks
- **Memory (CLAUDE.md):** https://code.claude.com/docs/en/memory
- **Permissions:** https://code.claude.com/docs/en/permissions
