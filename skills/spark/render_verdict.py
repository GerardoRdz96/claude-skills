#!/usr/bin/env python3
"""render_verdict.py — deterministic filler for the SPARK feasibility verdict.

WAT-shaped: the spark engine's verdict JSON (plus a little SOP-assembled context)
in, a clean self-contained HTML verdict out. Clones the template's *_BLOCK regions
per item, HTML-escapes every value, and HARD-FAILS if any {{token}}, href="#", or
block marker survives — a partial fill can never ship stale text. Sibling of
storm-research/render.py; do NOT clone its look — SPARK is a distinct identity.

Usage:
    python3 render_verdict.py <verdict.json> <output.html> [--template verdict-template.html]
    python3 render_verdict.py --sample <output.html>     # render the bundled sample (for the gate)

Verdict JSON shape (the spark engine 'verdict' return + SOP context):
    { verdict: "GO"|"NO-GO"|"PIVOT", headline, hypothesis_tested|hypothesis,
      what_was_built, confidence: 0-10,
      evidence: [{metric, baseline, result, delta?, passed: bool}],
      key_risks: [str], what_would_change_the_call, recommended_next_step, dissent?,
      topic?/idea?, reader?, goal?, date?, spike_ref?, artifact_type?, time_box?,
      codex_note?, critics_returned?, flip_concerns? }

TOKEN CONTRACT (the template MUST contain exactly these, nothing else stale):
  Scalars: {{VERDICT}} {{VERDICT_CLASS}} {{HEADLINE}} {{HYPOTHESIS}} {{WHAT_BUILT}}
           {{CONFIDENCE}} {{CONF_CLASS}} {{CONF_SEGS}} {{WHAT_WOULD_CHANGE}}
           {{NEXT_STEP}} {{DISSENT}} {{TOPIC}} {{READER}} {{GOAL}} {{DATE}}
           {{SPIKE_REF}} {{ARTIFACT_TYPE}} {{TIME_BOX}} {{CODEX_NOTE}}
           {{CRITICS_COUNT}} {{FLIP_COUNT}}
  Blocks:  <!--EVIDENCE_BLOCK--> {{EV_METRIC}} {{EV_BASELINE}} {{EV_RESULT}}
           {{EV_DELTA}} {{EV_PASS_CLASS}} {{EV_PASS_LABEL}} <!--/EVIDENCE_BLOCK-->
           <!--RISK_BLOCK--> {{RISK}} <!--/RISK_BLOCK-->
"""
import sys, os, re, json, html, datetime, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, "verdict-template.html")

# verdict label -> (css class, display label). Accept the common spellings; an
# unknown value HARD-FAILS rather than silently becoming a (real) decision.
VERDICTS = {
    "go":     ("vd--go",    "GO"),
    "no-go":  ("vd--nogo",  "NO-GO"),
    "nogo":   ("vd--nogo",  "NO-GO"),
    "no go":  ("vd--nogo",  "NO-GO"),
    "pivot":  ("vd--pivot", "PIVOT"),
}


def esc(v):
    return html.escape("" if v is None else str(v))


def truthy(v):
    """Robust pass/fail parse — a string 'false'/'0'/'no' must NOT read as PASS."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    if v is None:
        return False
    return str(v).strip().lower() in ("true", "1", "yes", "y", "pass", "passed", "ok")


def gauge(confidence):
    """10-segment confidence meter (markup, returned pre-rendered — not escaped)."""
    try:
        n = max(0, min(10, int(confidence)))
    except (TypeError, ValueError):
        n = 0
    cls = "" if n >= 7 else ("mid" if n >= 4 else "low")
    segs = "".join('<span class="seg on"></span>' if i <= n else '<span class="seg"></span>'
                   for i in range(1, 11))
    return cls, segs, n


def block(tpl, name):
    """Return (full_marker_region, inner_template) for <!--NAME-->...<!--/NAME-->."""
    m = re.search(rf"<!--{name}-->(.*?)<!--/{name}-->", tpl, re.S)
    if not m:
        raise SystemExit(f"render_verdict.py: template missing block {name}")
    return m.group(0), m.group(1)


def render(data, template_path):
    with open(template_path, encoding="utf-8") as fh:
        tpl = fh.read()

    # ── Evidence rows ────────────────────────────────────────────────────────
    full, inner = block(tpl, "EVIDENCE_BLOCK")
    rows = []
    for e in data.get("evidence", []):
        passed = truthy(e.get("passed"))
        rows.append(inner
                    .replace("{{EV_METRIC}}", esc(e.get("metric")))
                    .replace("{{EV_BASELINE}}", esc(e.get("baseline")))
                    .replace("{{EV_RESULT}}", esc(e.get("result")))
                    .replace("{{EV_DELTA}}", esc(e.get("delta") or "—"))
                    .replace("{{EV_PASS_CLASS}}", "ev--pass" if passed else "ev--fail")
                    .replace("{{EV_PASS_LABEL}}", "PASS" if passed else "FAIL"))
    tpl = tpl.replace(full, "\n".join(rows) if rows else inner
                      .replace("{{EV_METRIC}}", "No measurement captured")
                      .replace("{{EV_BASELINE}}", "—")
                      .replace("{{EV_RESULT}}", "—")
                      .replace("{{EV_DELTA}}", "—")
                      .replace("{{EV_PASS_CLASS}}", "ev--fail")
                      .replace("{{EV_PASS_LABEL}}", "N/A"))

    # ── Risks ────────────────────────────────────────────────────────────────
    full, inner = block(tpl, "RISK_BLOCK")
    rows = [inner.replace("{{RISK}}", esc(r)) for r in data.get("key_risks", [])]
    tpl = tpl.replace(full, "\n".join(rows) if rows else inner.replace("{{RISK}}", "None surfaced."))

    # ── Scalars ──────────────────────────────────────────────────────────────
    vkey = (data.get("verdict") or "").strip().lower()
    if vkey not in VERDICTS:
        raise SystemExit(f"render_verdict.py: unknown verdict {data.get('verdict')!r} "
                         "— must be GO / NO-GO / PIVOT (refusing to silently default a decision)")
    vclass, vlabel = VERDICTS[vkey]
    conf_cls, conf_segs, conf_n = gauge(data.get("confidence", 0))
    today = datetime.date.today().isoformat()
    dissent = data.get("dissent") or ""
    codex = data.get("codex_note") or ""
    scal = {
        "{{VERDICT}}": esc(vlabel),
        "{{VERDICT_CLASS}}": vclass,
        "{{HEADLINE}}": esc(data.get("headline")),
        "{{HYPOTHESIS}}": esc(data.get("hypothesis_tested") or data.get("hypothesis")),
        "{{WHAT_BUILT}}": esc(data.get("what_was_built")),
        "{{CONFIDENCE}}": str(conf_n),
        "{{CONF_CLASS}}": conf_cls,
        "{{CONF_SEGS}}": conf_segs,                        # pre-rendered markup, not escaped
        "{{WHAT_WOULD_CHANGE}}": esc(data.get("what_would_change_the_call") or "—"),
        "{{NEXT_STEP}}": esc(data.get("recommended_next_step") or "—"),
        "{{DISSENT}}": esc(dissent or "No surviving dissent — the critics aligned with the call."),
        "{{TOPIC}}": esc(data.get("topic") or data.get("idea")),
        "{{READER}}": esc(data.get("reader") or "Gera — R&D Engineer"),
        "{{GOAL}}": esc(data.get("goal") or "decide GO / NO-GO / PIVOT"),
        "{{DATE}}": esc(data.get("date") or today),
        "{{SPIKE_REF}}": esc(data.get("spike_ref") or "throwaway spike (not kept)"),
        "{{ARTIFACT_TYPE}}": esc(data.get("artifact_type") or "code"),
        "{{TIME_BOX}}": esc(data.get("time_box") or "time-boxed spike"),
        "{{CODEX_NOTE}}": esc(codex or "Cross-lineage review pending."),
        "{{CRITICS_COUNT}}": esc(data.get("critics_returned", 3)),
        "{{FLIP_COUNT}}": esc(data.get("flip_concerns", 0)),
    }
    for k, v in scal.items():
        tpl = tpl.replace(k, v)

    # ── Guard part 1: block markers — checked BEFORE comments are stripped ────
    # Block markers ARE html comments; stripping first would hide an unhandled
    # *_BLOCK region (the handled EVIDENCE_BLOCK/RISK_BLOCK were already replaced
    # by block()). So this check must run before the strip below to mean anything.
    if re.search(r"<!--/?[A-Z_]+_BLOCK-->", tpl):
        raise SystemExit("render_verdict.py GUARD FAILED — leftover *_BLOCK marker "
                         "(an unhandled repeated-row region in the template)")

    # Strip template scaffolding comments (incl. the doc block, which intentionally
    # contains {{token}}/href="#" examples) so they never leak into the verdict.
    tpl = re.sub(r"<!--.*?-->", "", tpl, flags=re.S)

    # ── Guard part 2: tokens + placeholder hrefs — AFTER the strip ────────────
    # Match only real template tokens ({{UPPER_SNAKE}}), NOT incidental "{{" in
    # escaped user data — a spike may legitimately test a prompt template whose
    # evidence text contains "{{var}}". html.escape() leaves braces intact, so a
    # broad `"{{" in tpl` check would false-fail on valid data.
    leftovers = []
    if re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}", tpl):
        leftovers.append("unfilled {{TOKEN}}")
    if 'href="#"' in tpl:
        leftovers.append('placeholder href="#"')
    if leftovers:
        raise SystemExit("render_verdict.py GUARD FAILED — would ship stale content: " + ", ".join(leftovers))
    return tpl


SAMPLE = {
    "verdict": "PIVOT",
    "headline": "A local 7B model catches the easy planted bugs but misses the subtle ones — keep Codex as the gate, use the local model only as a cheap pre-filter.",
    "hypothesis_tested": "If we swap Codex for a local 7B code model in the /eval no-self-review gate, then it catches >=90% of planted bugs at near-zero cost, measured by recall on a 20-bug seeded diff set.",
    "what_was_built": "A 40-line harness that runs the same 20 deliberately-bugged diffs through both Codex and a local qwen2.5-coder:7b prompt, scoring each on bugs caught vs missed.",
    "confidence": 7,
    "evidence": [
        {"metric": "Planted-bug recall (20-bug set)", "baseline": "Codex: 19/20 (95%)", "result": "Local 7B: 13/20 (65%)", "delta": "-30pp", "passed": False},
        {"metric": "Cost per review", "baseline": "Codex: ~$0.04", "result": "Local 7B: ~$0.00 (local)", "delta": "free", "passed": True},
        {"metric": "Wall-clock per review", "baseline": "Codex: ~22s", "result": "Local 7B: ~6s", "delta": "-16s", "passed": True},
        {"metric": "Subtle-bug recall (off-by-one, float, auth)", "baseline": "Codex: 6/6", "result": "Local 7B: 2/6", "delta": "-4 bugs", "passed": False},
    ],
    "key_risks": [
        "The 20-bug set is small and hand-authored — recall numbers carry wide error bars; a 200-bug set could move them either way.",
        "The local model's misses cluster on exactly the expensive bug classes (auth, float, off-by-one) — the ones the gate exists to catch.",
        "Free-and-fast tempts a silent downgrade of the gate; the No-Self-Review Law assumes the reviewer is actually competent.",
    ],
    "what_would_change_the_call": "If a larger local model (32B+) closed the subtle-bug gap to within ~5pp of Codex at still-near-zero cost, the call flips to GO.",
    "recommended_next_step": "Adopt the local 7B as a CHEAP PRE-FILTER (flag obvious bugs in <6s) but keep Codex as the binding gate. Re-run the spike against qwen2.5-coder:32b before considering full replacement.",
    "dissent": "The generalization critic holds that even a 95% Codex baseline is not 'safe' for unattended gating — a 1-in-20 miss on auth code is a breach waiting to happen, so neither option should run without a human on high-stakes diffs.",
    "topic": "Replacing Codex with a local model in the /eval no-self-review gate",
    "reader": "Gera — AI-focused R&D Engineer at SoftServe + Penguin Alley founder",
    "goal": "decide whether the local model can carry the cross-lineage review gate",
    "date": "2026-06-29",
    "spike_ref": "spikes/2026-06-29-local-eval-gate/",
    "artifact_type": "code",
    "time_box": "M — half-day spike",
    "codex_note": "Codex concurs with PIVOT: the recall gap on subtle bugs is the load-bearing result and the small sample is correctly flagged; would not upgrade confidence above 7 on n=20.",
    "critics_returned": 3,
    "flip_concerns": 1,
}


def emit_dossier(data, out_path):
    """After the verdict HTML ships, persist the source JSON sidecar + upsert the
    combined Arc dossier (artifacts/research/<slug>.dossier.json). Best-effort:
    a failure here must NEVER break the verdict render, so it is fully guarded."""
    try:
        out_abs = os.path.abspath(out_path)
        base = os.path.splitext(out_abs)[0]            # .../<slug>-verdict
        sidecar = base + ".json"                       # <slug>-verdict.json
        if not os.path.exists(sidecar):
            with open(sidecar, "w", encoding="utf-8") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)
        fname = os.path.basename(out_abs)              # verdict file is "<slug>-verdict.html"
        slug = fname[:-len("-verdict.html")] if fname.endswith("-verdict.html") \
            else os.path.splitext(fname)[0]
        arc = os.path.abspath(os.path.join(HERE, "..", "..", "..", "scripts", "arc-dossier.py"))
        if os.path.exists(arc):
            date = str(data.get("date") or datetime.date.today().isoformat())
            subprocess.run([sys.executable, arc, "--slug", slug, "--date", date,
                            "--verdict", sidecar], check=False)
    except Exception as e:
        print(f"render_verdict.py: dossier upsert skipped ({e})", file=sys.stderr)


def main(argv):
    args = argv[1:]
    template = DEFAULT_TEMPLATE
    if "--template" in args:
        i = args.index("--template"); template = args[i + 1]; del args[i:i + 2]
    if args and args[0] == "--sample":
        data, out = SAMPLE, (args[1] if len(args) > 1 else "spark-sample.html")
    else:
        if len(args) < 2:
            raise SystemExit(__doc__)
        with open(args[0], encoding="utf-8") as fh:
            data = json.load(fh)
        out = args[1]
    htmlout = render(data, template)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(htmlout)
    print(f"render_verdict.py: wrote {out} ({len(htmlout)} bytes, "
          f"verdict={data.get('verdict')}, {len(data.get('evidence', []))} evidence rows)")
    emit_dossier(data, out)


if __name__ == "__main__":
    main(sys.argv)
