# Plugin Builder — Technical Reference

**Scope:** Authoritative reference for authoring, validating, distributing, optimizing, and auditing Claude Code **plugins** and **marketplaces**.

**Provenance:** Verified against Claude Code v2.1.152 (`claude plugin --help`) and the real installed manifests on Gera's machine — `context-mode`, `cc-gemini-plugin`, `claude-mem` (thedotmack), `openai-codex`, and `anthropics/claude-plugins-official`. Where a claim could not be ground-truthed locally it is marked `[UNVERIFIED]`.

---

## 1. Plugin anatomy & directory structure

A plugin is a directory. **Only the manifest lives in `.claude-plugin/`; every component lives at the plugin root.**

```
my-plugin/
├── .claude-plugin/
│   ├── plugin.json          # manifest — REQUIRED, the only required file
│   └── marketplace.json     # OPTIONAL — present if this repo is ALSO a marketplace
├── commands/                # slash commands — one .md per command  →  /my-plugin:cmd
├── agents/                  # subagents — one .md per agent
├── skills/                  # skills — each <name>/SKILL.md  →  my-plugin:<name>
│   └── my-skill/SKILL.md
├── hooks/
│   └── hooks.json           # hook config (scripts referenced via ${CLAUDE_PLUGIN_ROOT})
├── .mcp.json                # OPTIONAL — MCP servers (or declare them inline in plugin.json)
├── scripts/                 # any helper scripts the components call
└── README.md                # user-facing docs (strongly recommended)
```

### Discovery rules (verified)

- **`.claude-plugin/plugin.json` is the only required file.** Everything else is optional.
- **Components auto-discover at the plugin ROOT** — `commands/`, `agents/`, `skills/`, `hooks/`. You do **not** put them inside `.claude-plugin/`. (Ground truth: `cc-gemini-plugin` keeps `agents/`, `commands/`, `SKILL.md` at root with `.claude-plugin/` holding only the manifests; `context-mode` keeps `skills/` and `hooks/` at root.)
- The manifest's `commands` / `agents` / `skills` / `hooks` fields are **optional path overrides** (strings). Omit them to use the default root locations. (`context-mode` sets `"skills": "./skills/"`; `cc-gemini-plugin` and `claude-mem` set none and rely on auto-discovery.)
- **Namespacing:** a plugin's components are namespaced by plugin name. A skill at `skills/foo/SKILL.md` in plugin `bar` is invoked `bar:foo`; a command `commands/baz.md` becomes `/bar:baz`; agents and skills surface as `bar:foo` in the Agent/Skill pickers. Nested skill dirs add another colon (`bar:group:foo`). (Confirmed by the live skill list: `cc-gemini-plugin:gemini`, `context-mode:context-mode`, `superpowers:brainstorming`.)

### `${CLAUDE_PLUGIN_ROOT}`

Resolves to the absolute path of the installed plugin directory. **Mandatory** any time a component points at a sibling file inside the plugin — hook script paths, MCP server launch commands, helper-script invocations. Never hardcode an absolute path; the install location differs per machine. (Ground truth: `context-mode` launches its MCP server with `"args": ["${CLAUDE_PLUGIN_ROOT}/start.mjs"]`.)

---

## 2. plugin.json schema

### Real minimal manifest (this is genuinely all you need)

```json
{
  "name": "cc-gemini-plugin",
  "version": "1.3.5",
  "description": "Integrate Gemini CLI for long-context code exploration from Claude Code",
  "author": { "name": "thepushkarp" },
  "keywords": ["gemini", "google", "long-context"]
}
```

### Fuller annotated manifest

```json
{
  "name": "my-plugin",
  "version": "1.2.3",
  "description": "One concise sentence describing what this plugin does.",
  "author": { "name": "Your Name", "email": "you@example.com", "url": "https://github.com/you" },
  "homepage": "https://github.com/you/my-plugin#readme",
  "repository": "https://github.com/you/my-plugin",
  "license": "MIT",
  "keywords": ["ai", "productivity"],

  "commands": "./commands",     // optional path override (default: ./commands)
  "agents": "./agents",         // optional path override (default: ./agents)
  "skills": "./skills",         // optional path override (default: ./skills)
  "hooks": "./hooks/hooks.json",// optional — path to hooks.json OR a hooks dir
  "mcpServers": {               // optional — INLINE object (NOT a directory path)
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/start.mjs"]
    }
  }
}
```

### Field reference

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | ✓ | Plugin identifier. lowercase, alphanumeric + hyphens. Matches the marketplace entry name. |
| `version` | string | ✓ | Semver (`1.2.3`). Drives update detection and `claude plugin tag`. |
| `description` | string | ✓ | One sentence, shown in discovery UI. |
| `author` | object | ✗ | `{ name, email?, url? }`. `name` is the only field used in practice. |
| `homepage` | string | ✗ | Docs/landing URL. |
| `repository` | string | ✗ | Git URL. |
| `license` | string | ✗ | SPDX id (`MIT`, `Apache-2.0`, `Elastic-2.0`). |
| `keywords` | array<string> | ✗ | Search tags. |
| `commands` | string | ✗ | Path override for the commands dir. Default `./commands`. |
| `agents` | string | ✗ | Path override for the agents dir. Default `./agents`. |
| `skills` | string | ✗ | Path override for the skills dir. Default `./skills`. |
| `hooks` | string | ✗ | Path to `hooks.json` or a hooks dir. Default `./hooks`. |
| `mcpServers` | object | ✗ | **Inline** map of `server-name → { command, args, env? }`. Alternatively ship a `.mcp.json` at the plugin root. |

Notes:
- `$schema` is **not** used by the real plugin.json files. (Some marketplace.json files include it; plugin.json's don't.) Treat it as optional cosmetic.
- No real manifest sets all fields. Keep it minimal — name/version/description + author + keywords covers most plugins.

---

## 3. MCP servers inside a plugin — two valid ways

There is **no** `mcpServers/<name>/manifest.json + launcher.sh` directory convention. The two real patterns are:

**(a) Inline in plugin.json** (what `context-mode` does):
```json
"mcpServers": {
  "context-mode": { "command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/start.mjs"] }
}
```

**(b) A `.mcp.json` file at the plugin root** (what `claude-mem` does — `.mcp.json` is **not** deprecated):
```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.mjs"],
      "env": { "SOME_FLAG": "1" }
    }
  }
}
```

**Servy doctrine:** CLI > API > MCP. An MCP server inside a plugin burns ~35× the tokens of a CLI and gets less reliable as tasks compound. Bundle a skill/command that shells out to a CLI before you bundle an MCP server. If you do bundle MCP, justify it in the plugin's README.

---

## 4. Component specifics inside a plugin

| Component | Lives at | Becomes | Notes |
|-----------|----------|---------|-------|
| **Command** | `commands/<name>.md` | `/<plugin>:<name>` | Standard command markdown. May reference `${CLAUDE_PLUGIN_ROOT}`. |
| **Agent** | `agents/<name>.md` | `<plugin>:<name>` in the Agent picker | Same format as a standalone `.claude/agents/*.md`. |
| **Skill** | `skills/<name>/SKILL.md` (or a lone root `SKILL.md`) | `<plugin>:<name>` | Same format as a standalone skill. A single root `SKILL.md` validates too (single-skill plugins, e.g. `cc-gemini-plugin`); use `skills/<name>/` for multi-skill. Nested dirs add colons. |
| **Hook** | `hooks/hooks.json` | runs on events | Script paths MUST use `${CLAUDE_PLUGIN_ROOT}`. |
| **MCP** | inline `mcpServers` or `.mcp.json` | MCP tools | See §3. |

### hooks.json structure

```json
{
  "description": "What these hooks do (optional).",
  "hooks": {
    "SessionStart": [
      { "matcher": "", "hooks": [
        { "type": "command", "command": "node \"${CLAUDE_PLUGIN_ROOT}/hooks/on-start.mjs\"" }
      ] }
    ],
    "PostToolUse": [
      { "matcher": "Bash|Edit|Write", "hooks": [
        { "type": "command", "command": "node \"${CLAUDE_PLUGIN_ROOT}/hooks/check.mjs\"", "timeout": 10 }
      ] }
    ]
  }
}
```

**Shape (verified — context-mode, claude-mem):** events nest under a top-level `hooks` object (optional sibling `description`); each event is an array of `{ matcher, hooks: [ { type, command } ] }` blocks; `matcher` is `""` for events that don't match on a tool.

Events: `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `PreCompact` (standard Claude Code hook surface). Matchers are tool-name regexes (`Bash`, `Edit`, `Write`, `Read`, `Agent`, …).

---

## 5. marketplace.json — making plugins installable

A marketplace is a repo (or local dir) whose `.claude-plugin/marketplace.json` lists plugins. Two equally-valid header styles appear in the wild:

**Style A — top-level `description` + `$schema`** (official + cc-gemini):
```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "my-marketplace",
  "description": "What this marketplace offers.",
  "owner": { "name": "Your Name", "email": "you@example.com" },
  "plugins": [ /* … */ ]
}
```

**Style B — `metadata` block** (context-mode, openai-codex):
```json
{
  "name": "my-marketplace",
  "owner": { "name": "Your Name", "email": "you@example.com" },
  "metadata": { "description": "What this marketplace offers.", "version": "1.0.0" },
  "plugins": [ /* … */ ]
}
```

### Plugin entry fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | ✓ | Must match the plugin's `plugin.json` name. |
| `source` | string \| object | ✓ | Where the plugin lives. See source types below. |
| `description` | string | ✗ (recommended) | Shown in the install UI. |
| `version` | string | ✗ | Mirror plugin.json. |
| `author` | object | ✗ | `{ name }`. |
| `category` | string | ✗ | Seen: `development`, `integrations`, `security`, `design`, `productivity`. |
| `keywords` | array | ✗ | Search tags. |
| `homepage` / `repository` | string | ✗ | Links. |

### `source` types (verified against claude-plugins-official)

```json
// local path — plugin dir relative to the marketplace repo (single-plugin repo uses "./")
"source": "./"
"source": "./plugins/agent-sdk-dev"

// git subdirectory — plugin lives in a subdir of an external repo
"source": { "source": "git-subdir", "url": "https://github.com/org/repo.git",
            "path": "plugins/foo", "ref": "v1.5.5", "sha": "1db6098…" }

// url — whole external repo is the plugin (pin with sha)
"source": { "source": "url", "url": "https://github.com/org/foo.git", "sha": "1db738b…" }
```

`ref` selects a branch/tag; `sha` pins an exact commit (recommended for third-party entries). The `url` source was previously uncertain — it is **real** (`agentforce-adlc` in the official marketplace uses it).

### Single-plugin repo vs multi-plugin marketplace

- **Single-plugin repo:** `plugin.json` + `marketplace.json` both in `.claude-plugin/`, the plugin IS the repo, marketplace lists one entry with `"source": "./"`. (Pattern: `context-mode`, `cc-gemini-plugin`.)
- **Multi-plugin marketplace:** the repo's `.claude-plugin/marketplace.json` lists many plugins, each `"source": "./plugins/<name>"` (or external `url` / `git-subdir`); plugin dirs sit under `plugins/`. (Pattern: `claude-plugins-official`, `openai-codex`.)

---

## 6. CLI surface (verified — `claude plugin --help`, v2.1.152)

```
claude plugin install|i <plugin>          # install (use plugin@marketplace to disambiguate)
claude plugin uninstall|remove <plugin>
claude plugin list
claude plugin enable <plugin>
claude plugin disable [plugin]
claude plugin update <plugin>             # restart required to apply
claude plugin details <name>              # component inventory + projected token cost
claude plugin validate <path>             # validate a plugin OR a marketplace manifest
claude plugin tag [path]                  # create {name}--v{version} git tag, checks plugin.json ⇄ marketplace agree
claude plugin prune|autoremove            # remove auto-installed deps no longer needed

claude plugin marketplace add <source>    # ./path | https://…git | owner/repo (github shorthand)
claude plugin marketplace list
claude plugin marketplace update [name]
claude plugin marketplace remove <name>
```

In-session, the same surface is reachable interactively via `/plugin`.

**Marketplace registration sources** (`known_marketplaces.json`): `github` (`{source:"github", repo:"owner/name"}`), a git `url`, or a local `directory` (`{source:"directory", path:"…"}`).

---

## 7. Validation & authoring best practices

```bash
# validate the plugin manifest AND the marketplace manifest
claude plugin validate ./plugins/<name>/.claude-plugin/plugin.json
claude plugin validate ./.claude-plugin/marketplace.json
# local smoke-test: add the marketplace root, then install BY NAME (install takes a name, not a path)
claude plugin marketplace add ./ --scope local         # "./" not "." — points at the dir holding .claude-plugin/
claude plugin install <name>@<marketplace> --scope local   # <marketplace> = the marketplace.json `name`
claude plugin details <name>                            # component inventory + token cost
# teardown — uninstall needs the SAME scope you installed with
claude plugin uninstall <name> --scope local && claude plugin marketplace remove <marketplace>
```

1. **Name** lowercase, hyphenated, unique; matches the marketplace entry.
2. **Semver** the `version`; bump it every release (`tag` enforces plugin.json ⇄ marketplace agreement).
3. **Keep the manifest minimal** — only fields you use.
4. **No hardcoded paths** — `${CLAUDE_PLUGIN_ROOT}` everywhere a component references a sibling file.
5. **README.md** — what it does, install line, components, quick start, config, troubleshooting.
6. **No secrets in the package** — read tokens from env at runtime; never commit keys.
7. **Test before publish** — `validate` the plugin + marketplace manifests → `marketplace add --scope local` → `install <name>@<mkt> --scope local` → exercise every command/skill/agent/hook → `uninstall`.
8. **Prefer CLI/skill over MCP** when wrapping a tool (token + reliability cost).

---

## 8. Distribution paths

- **Local test:** `claude plugin marketplace add ./ --scope local` (the `./` form — a bare `.` is rejected) then `claude plugin install <name>@<marketplace> --scope local` — `install` takes a plugin **name**, not a path; `<marketplace>` is the marketplace.json `name`. Uninstall with the same `--scope`.
- **Servy-as-marketplace:** keep authored plugins in `plugins/<name>/` and a `.claude-plugin/marketplace.json` at the repo root listing them with `"source": "./plugins/<name>"`. Gera can `claude plugin marketplace add ./` and self-install (registers as a `Directory` source). (`--sparse .claude-plugin plugins` trims the checkout for a git monorepo marketplace.)
- **Standalone public repo (the publish move):** push `plugins/<name>/` to its own public GitHub repo (same flow as `aegis` / `build-2026-brief`), with `.claude-plugin/{plugin.json, marketplace.json}` and `"source": "./"`. Users run `claude plugin marketplace add GerardoRdz96/<repo>` then `claude plugin install <name>@<repo>`.
- **Anthropic official marketplace:** submit via the plugin directory submission form; reviewed for quality/security; installs as `<name>@claude-plugins-official`.
- **Updates:** bump `version`, bump the marketplace entry's `ref`/`sha` for external sources, `claude plugin tag`, users `claude plugin update <name>`.

---

## 9. Servy-specific notes

- **SoftServe boundary (hard rule).** A plugin is a *distribution* artifact — built to leave the machine. Never bundle SoftServe Internal+ content, customer IP, or client code into a plugin that ships outside the SoftServe-managed environment. Public/shared plugins = personal or public-data only, same line the multi-brain stack draws (`references/softserve-ai-usage-policy.md`).
- **Your employer already uses this mechanism.** A `softserve-skills` marketplace is registered on Gera's managed Mac as a `directory` source (`/Library/Application Support/SoftServe/ClaudeCode/seed/marketplaces/softserve`). SoftServe distributes Claude Code capabilities to engineers as a plugin marketplace — the exact thing this skill builds. (Read-only; it's theirs.)
- **CLI > API > MCP** applies inside plugins too (§3).
- **No-Self-Review Law:** if Gera asks you to review/verify a plugin you just built, route to Codex.

## 10. Resources

- Official docs: https://code.claude.com/docs/en/plugins and https://code.claude.com/docs/en/plugin-marketplaces
- Reference marketplace: `anthropics/claude-plugins-official` (`.claude-plugin/marketplace.json`; plugins under `plugins/`)
- Local ground-truth examples on this machine: `~/.claude/plugins/marketplaces/{context-mode,cc-gemini-plugin,thedotmack,openai-codex}`
- JSON schemas (community): https://github.com/hesreallyhim/claude-code-json-schema
