---
name: plugin-builder
description: Use when someone asks to build, create, package, bundle, optimize, or audit a Claude Code plugin or marketplace — a distributable bundle of skills + agents + commands + hooks + MCP servers installed via `/plugin`. Triggers — "build a plugin", "package this as a plugin", "bundle my skills into a plugin", "make a marketplace", "ship Servy's capabilities", "turn these skills into something shareable", "audit my plugin", or `/plugin-builder`. The packaging + distribution sibling of `/skill-builder`, `/agent-builder`, `/agents-team-builder`, `/routines-builder`. Runs a decision gate and Discovery Interview before writing files.
argument-hint: [plugin name or what to package/ship]
disable-model-invocation: true
---

## What This Skill Does

Guides the creation, optimization, and auditing of Claude Code **plugins** and **marketplaces** using verified format facts and Servy's conventions. A plugin is a single installable package that bundles any mix of commands, agents, skills, hooks, and MCP servers, distributed through a marketplace and installed with `claude plugin install`.

Use this whenever:

- **Packaging existing Servy capabilities** to share or ship (the headline path — bundle a set of skills/agents/routines you already have into one installable plugin).
- Authoring a brand-new plugin from scratch.
- Deciding **whether** something should even be a plugin (vs leaving it as a loose skill/agent/routine).
- Standing up a **marketplace** so plugins are actually installable.
- Optimizing or auditing an existing plugin/marketplace.

This is the **packaging + distribution** sibling of the four primitive builders. They each make *one loose capability* that lives in `.claude/`. This one **bundles capabilities and makes them shippable.** It sits a layer *above* the others — build primitives with their builders, then use this to ship them. Full verified schema (plugin.json, marketplace.json, MCP, hooks, CLI) lives in [reference.md](reference.md).

---

## Quick Start: What Is a Plugin?

A plugin is a directory with one required file — `.claude-plugin/plugin.json` — and components (`commands/`, `agents/`, `skills/`, `hooks/`, MCP) at its **root**. A **marketplace** (`.claude-plugin/marketplace.json`) lists plugins and is what makes them installable via `/plugin install name@marketplace`.

**Why a plugin and not just loose files?** The other four builders drop a capability into `.claude/` where *this one project* uses it. A plugin is the **unit of distribution**: it versions a bundle, names it, and ships it — to teammates, to the public, or across your own machines — with one install command. If you'll never distribute it, you probably don't need a plugin.

### Plugin vs the four primitive builders

| You want… | Use | Why |
|---|---|---|
| One reusable **workflow/SOP** in this project | **Skill** (`/skill-builder`) | Lives loose in `.claude/skills/`, no packaging needed |
| One **isolated-context** delegate job | **Agent** (`/agent-builder`) | Lives loose in `.claude/agents/` |
| A small **crew** that talks peer-to-peer | **Agent team** (`/agents-team-builder`) | Lives loose in `.claude/teams/` |
| Something that runs **unattended on a schedule** | **Routine** (`/servy-routine`) | Runs in the cloud as Gera |
| To **bundle + version + ship** any mix of the above as ONE installable thing | **Plugin** (this skill) | Distribution is the whole point |

**The relationship:** a plugin is a *container*, not a competitor. Build the skills/agents/hooks first (with their builders), then plugin-builder packages them. If the request is "make a capability," triage with the front door in CLAUDE.md first; reach for plugin-builder when the request is "**ship / share / distribute** a capability."

---

## Mode 1: Build / Package a Plugin

### Step 0 — The Decision Gate (do this FIRST, before any interview)

Pressure-test whether a plugin is the right tool:

1. **Is there a real distribution need?** Will this leave the project — go to a teammate, the public, or another machine? **No → don't build a plugin.** Leave it as a loose skill/agent/routine. A plugin you never distribute is just overhead.
2. **Is it more than a single trivial primitive?** One tiny skill used only here doesn't need a package. Bundle when there's a *set*, or when versioned/installable distribution genuinely helps.
3. **SoftServe boundary (hard gate).** A plugin is built to leave the machine. If the bundle would contain SoftServe Internal+ content, customer IP, or client code and is destined for any non-SoftServe-managed target → **stop.** Public/shared plugins are personal- or public-data only (`references/softserve-ai-usage-policy.md`).
4. **MCP check.** If the plugin's value is wrapping an external tool, prefer bundling a CLI-backed skill/command over an MCP server (CLI > API > MCP — MCP costs ~35× the tokens). If you keep MCP, justify it.

If 1–2 don't justify a plugin, recommend the right primitive builder and stop. If the SoftServe gate trips, stop and say so. Otherwise state **one sentence** on what's being shipped and to whom, then proceed.

### Step 1 — Discovery Interview

Ask with AskUserQuestion, one round at a time. Skip any round already answered upfront. Keep going until you're 95% confident you can build without guessing.

**Round 1: Purpose & Name**
*Why: the name is the plugin id and the install target; purpose scopes the bundle.*
- What does this plugin deliver, and **who installs it** (you across machines / SoftServe teammates / the public)?
- Name it: lowercase-hyphens, unique, evokes the capability. It becomes `plugin install <name>` and namespaces every component (`<name>:skill`, `/<name>:command`). Suggest 2–3.

**Round 2: What goes in the bundle**
*Why: this is the component manifest — the heart of a packaging job.*
- Which **existing** Servy capabilities get packaged? (Name the specific skills/agents/teams/hooks/scripts. I'll copy them into the plugin and namespace them.)
- Any **new** components to author fresh for this plugin?
- Does it need an **MCP server**? (Re-check the CLI>API>MCP gate.) Hooks?

**Round 3: Marketplace & Distribution**
*Why: a plugin that can't be installed is half-built (Gera chose "include marketplace").*
- Distribution target: **local test only → Servy-as-marketplace (`.claude-plugin/marketplace.json`) → standalone public repo → Anthropic official?**
- New marketplace, or add an entry to Servy's root `marketplace.json`?
- Version to start at (default `0.1.0`).

**Round 4: Manifest & Guardrails**
*Why: minimal correct metadata + boundaries.*
- author (`name` + optional url), license (default MIT for public), keywords.
- Anything the plugin must **not** do or contain? (Re-confirm the SoftServe boundary for anything public.) Any secrets it reads — confirm they come from env at runtime, never committed.

**Round 5: Confirmation**
Summarize back, then ask "Does this capture it?":

```
## Plugin Summary: <name>

**Delivers:** <one sentence>   **Installed by:** <you | teammates | public>
**Location:** plugins/<name>/   **Version:** <x.y.z>

**Bundles:**
- commands: …   agents: …   skills: …   hooks: …   mcp: …
  (existing → copied+namespaced;  new → authored fresh)

**Distribution:** <local | Servy marketplace | standalone repo | official>
**Manifest:** author=… license=… keywords=…
**Guardrails:** SoftServe boundary check = <pass/why>; secrets via env; CLI-over-MCP = <ok/why>
```

Only build after confirmation.

### Step 2 — Build Phase

Scaffold under **`plugins/<name>/`** at the Servy repo root (the agreed convention — sits beside `projects/`, `routines/`; a clean staging area, kept out of `.claude/` because that's for Servy's *live* primitives).

1. **Manifest** — write `plugins/<name>/.claude-plugin/plugin.json`. Keep it minimal: `name`, `version`, `description`, `author`, `keywords`. Add path-override / `mcpServers` fields only if needed. (Schema + real examples: [reference.md](reference.md) §2.)
2. **Components at the ROOT** (not inside `.claude-plugin/`):
   - Packaging existing → copy the source skill/agent/command into `plugins/<name>/{skills,agents,commands}/` and adjust any internal paths.
   - New → author them in place (you may invoke `/skill-builder` or `/agent-builder` underneath to write a component correctly).
3. **Wire paths with `${CLAUDE_PLUGIN_ROOT}`** — every hook script command, MCP launch command, and helper-script reference. Never hardcode an absolute path. (reference.md §1, §3, §4.)
4. **MCP** — declare inline in `plugin.json` (`mcpServers` object) or as a `.mcp.json` at the plugin root. (reference.md §3.)
5. **Marketplace** — create/append the entry in `.claude-plugin/marketplace.json` (at the Servy repo root for Servy-as-marketplace, or `plugins/<name>/.claude-plugin/marketplace.json` with `"source": "./"` for a standalone single-plugin repo). (reference.md §5.)
6. **README.md** — what it does, install line, component list, quick start, config, troubleshooting.

### Step 3 — Validate (don't skip)

```bash
# validate the plugin manifest AND the marketplace manifest
claude plugin validate ./plugins/<name>/.claude-plugin/plugin.json
claude plugin validate ./.claude-plugin/marketplace.json
# install takes a NAME, not a path: add the marketplace root, then install
claude plugin marketplace add ./ --scope local       # "./" not "." (bare "." is rejected)
claude plugin install <name>@<marketplace> --scope local
claude plugin details <name>               # component inventory + token cost
# exercise each command/skill/agent/hook, then tear down (uninstall with the SAME scope):
claude plugin uninstall <name> --scope local && claude plugin marketplace remove <marketplace>
```

Report exactly what you ran and what passed. Don't claim it works without the validate + a local install.

### Step 4 — Document & Register

- **CLAUDE.md** — one line under a plugins area (same session — Servy's standing rule).
- **projects/REGISTRY.md** — only if the plugin ships to *users* as a public product (give it a maintenance block, like `aegis`).
- **Wiki** — note durable facts in `references/claude-code-plugins.md`; append a line to `references/log.md`.

---

## Mode 2: Optimize an Existing Plugin

Read the plugin's `plugin.json` + tree first — never optimize what you haven't read. Then look for:

- **Components in the wrong place** → must be at the plugin root, not inside `.claude-plugin/` (the #1 mistake). Fix the layout.
- **Hardcoded paths** → replace with `${CLAUDE_PLUGIN_ROOT}`.
- **MCP that should be a CLI** → if it wraps a tool with a CLI, repackage as a skill/command that shells out (token + reliability win).
- **Bloated manifest** → strip unused fields; keep it minimal.
- **Stale version** → bump semver; re-tag; update the marketplace entry's `ref`/`sha`.
- **Marketplace drift** → entry name/version must match `plugin.json` (`claude plugin tag` enforces this).
- **Missing README / secrets in the package** → add docs; move secrets to runtime env.

Show the diff and the *why* per change before applying.

---

## Mode 3: Audit an Existing Plugin

Read the files, run the checklist, fix issues before marking complete.

**Manifest**
- [ ] `.claude-plugin/plugin.json` present; `name`/`version`/`description` set; name lowercase-hyphens and matches the marketplace entry
- [ ] `version` is semver; agrees with the marketplace entry (`claude plugin tag` would pass)
- [ ] Manifest is minimal — no unused fields

**Structure**
- [ ] Components live at the plugin **root** (`commands/`, `agents/`, `skills/`, `hooks/`), not inside `.claude-plugin/`
- [ ] Skills are `skills/<name>/SKILL.md` (a lone root `SKILL.md` is also valid for a single-skill plugin); commands/agents are single `.md` files
- [ ] No hardcoded paths — `${CLAUDE_PLUGIN_ROOT}` used in every hook/MCP/script reference
- [ ] MCP declared inline or via `.mcp.json` (no fictional `mcpServers/manifest.json+launcher` layout)

**Marketplace & distribution**
- [ ] `marketplace.json` lists the plugin with a valid `source` (string path / `git-subdir` / `url`)
- [ ] `claude plugin validate` passes on both the plugin and the marketplace manifest

**Boundaries & quality (Servy)**
- [ ] SoftServe boundary: nothing Internal+/customer-IP in a plugin destined to leave the managed environment
- [ ] No secrets committed; tokens read from env at runtime
- [ ] CLI-over-MCP respected (any MCP justified in the README)
- [ ] README present and useful; documented in CLAUDE.md
- [ ] If a review of this build is requested → routed to Codex (No-Self-Review Law)

---

## Complete Example

A minimal single-plugin repo that bundles two existing skills.

```
plugins/servy-jumpstart/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── jumpstart/SKILL.md
│   └── present/SKILL.md
└── README.md
```

`plugin.json`:
```json
{
  "name": "servy-jumpstart",
  "version": "0.1.0",
  "description": "Jumpstart engagement copilot + speaker-prep, bundled for SoftServe R&D teammates.",
  "author": { "name": "Gera (GerardoRdz96)" },
  "license": "MIT",
  "keywords": ["jumpstart", "softserve", "enablement"]
}
```

`marketplace.json` (single-plugin → `"source": "./"`):
```json
{
  "name": "servy-jumpstart",
  "owner": { "name": "Gera", "email": "" },
  "metadata": { "description": "Servy capabilities packaged for sharing", "version": "0.1.0" },
  "plugins": [
    { "name": "servy-jumpstart", "source": "./", "version": "0.1.0",
      "description": "Jumpstart copilot + speaker-prep", "category": "productivity" }
  ]
}
```
Install line for a teammate: `claude plugin marketplace add GerardoRdz96/servy-jumpstart && claude plugin install servy-jumpstart@servy-jumpstart`.
*(Boundary note: only ship this publicly if the bundled skills carry no SoftServe Internal+ content.)*

---

## Servy Conventions

- **Author in `plugins/<name>/`** at the repo root. A `.claude-plugin/marketplace.json` at the Servy root turns Servy into a multi-plugin marketplace whose sources are those dirs. Publish by pushing a plugin dir to its own public repo (same flow as `aegis` / `build-2026-brief`).
- **A plugin is the ship layer.** Build primitives with their builders first; package here. It composes with the front-door triage, it doesn't replace it.
- **SoftServe boundary is a hard gate** — plugins are distribution artifacts; keep Internal+/customer IP out of anything that leaves the managed environment.
- **CLI > API > MCP** inside plugins too.
- **Update CLAUDE.md the same session** you build a plugin.
- For review of a plugin you just built, prefer a **Codex** route over self-review.

## Important Notes

- **Decision gate is not optional.** Most "make a plugin" asks are really "make a skill/agent" — only package when there's a real distribution need.
- **Always read an existing plugin before optimizing or auditing it.**
- **Components at the root, manifest in `.claude-plugin/`** — the single most common structural error.
- Validation (`claude plugin validate` + a local install) is the proof a plugin works — run it, report it.
- Full verified schema, CLI surface, MCP/hook patterns, and distribution paths: [reference.md](reference.md).
