---
name: eval
description: Use to score a code diff against Servy's audited code-review rubric (PReMISE-style, judge = Codex). Triggers - "eval this diff", "score this code", "rubric-score", "/eval score". Phase 1 = score mode; audit/repair/discover land in later phases.
---

# /eval

Rubric-judge eval for Servy. Phase 1 ships `score` mode: judge a diff against
`references/rubrics/code-review.json` using Codex (No-Self-Review Law — never
Claude reviewing Claude's own code).

## score

1. Get the diff to score (a file path, or `git diff` piped in).
2. Run:
   `git diff | python3 scripts/eval_judge.py score --diff - --rubric references/rubrics/code-review.json`
   (add `--json` for machine output).
3. Read back the scorecard: per-dimension scores + weighted total + normalized %.
4. If scoring Servy's own just-written code, this satisfies the No-Self-Review
   step of the `/build` doctrine — the judge is Codex, a different lineage.

The deterministic scoring logic is covered by `tests/eval/test_eval_judge.py`
(stdlib unittest — `python3 tests/eval/test_eval_judge.py`). The only model
call is the Codex judge.

Audit / repair / discover modes (PReMISE rubric auditing) are Phase 2-4.
Spec: `docs/superpowers/specs/2026-06-01-rubric-judge-eval-design.md`.
Plan: `docs/superpowers/plans/2026-06-01-rubric-judge-eval-p1.md`.
