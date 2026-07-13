# taste-skill reference: UI Snapping (Level 5)

> Part of `taste-skill`. Read this when a build needs complex/animated UI (marquees, particle effects, animated counters, fancy carousels, confetti, shaders). Doctrine source: `references/website-design-levels.md` Level 5 — *"buy the masterpiece, drop it in."*

## The rule

**Never hand-roll complex animated UI that already exists as a polished public component.** Claude inventing a particle system from scratch is how janky motion ships. Snap the finished component, then do an honest integration. (Simple motion — reveals, hovers, the canonical skeletons in `code-skeletons.md` — stays hand-built; snapping is for the expensive stuff.)

## Source order (CLI > fetch > reference-only)

1. **Magic UI** — magicui.design. 150+ free MIT animated components (React + TS + Tailwind + Motion), **shadcn-registry-native**: in a React/shadcn project, `npx shadcn@latest add "https://magicui.design/r/<component-name>"` pulls real source into the codebase (alt: `npx magicui-cli add --shadcn <component>`; components.json alias `"magicui": "@/components/magicui"`). No login, no key. Only the Pro blocks/templates are paid — not needed. First stop for React builds.
2. **Component source by URL** — Magic UI and many galleries expose per-component pages whose code is fetchable; grab the source, read it, integrate.
3. **CodePen** — codepen.io for one-off visual effects (public pens are viewable); port the technique, credit in a comment if substantial.
4. **21st.dev** — the biggest gallery (also a generation service, "Magic"), but Copy-code is login-walled and agent access is MCP-first + API-key + credit-gated (free ≈ 100 credits/mo, ~2 installs/day) → **dispreferred** under CLI > API > MCP. Use it as a *browse/reference* surface (its Featured section is well curated); if Gera copies a component's code into chat, integrate it like any pasted source.
5. **Mobbin** — mobbin.com is screenshots of real shipped products, login-walled, no code. Reference-imagery only (route it through the [[design-swipe-file]] protocol, not here).

## The honest-integration contract (the balloons-js pattern)

When the snapped component doesn't match the target stack (React component → vanilla self-contained HTML page, our common case):

1. **Identify the underlying library** the component wraps (e.g. `balloons-js` inside a React wrapper).
2. **Integrate the real thing**: CDN ES-module import + the component's exact container markup/config — never hack the JSX wrapper into a non-React page, never approximate the effect by hand.
3. **Precise placement instruction** beats vague desire: "integrate this at the bottom of the hero, triggered by the CTA" — say where and when.
4. **Verify it fires**: load the page (live preview/served file) and trigger the effect — "test it in the live preview rather than assume." A component that renders but never animates is a silent failure the diff won't show.
5. Self-contained pages stay self-contained: prefer CDN imports + inline config over adding a build step to a single-file artifact.

## Fit check before snapping

- Does the component's motion pass Section 5's "motion must be motivated" test? A gorgeous marquee is still filler if it says nothing.
- Restyle snapped components to the build's tokens (colors, radius, type) — a component in its demo palette is a slop tell.
- One showpiece per section max; snapped components are seasoning, not the meal.
