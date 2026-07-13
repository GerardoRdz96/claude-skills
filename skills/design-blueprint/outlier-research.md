# Outlier research template — Mode B of /design-blueprint

The Level-6 winners-vs-losers research contract (frame-recovered from Jack Roberts' 7-levels video, 2026-07-05; adapted to Servy: Firecrawl REST instead of MCP, Codex instead of "a different model"). Fill the brackets, then execute as the research model.

---

I am launching a **[NICHE]** business in **[CITY/REGION]**.

1. Go online and find the **10 most successful** [NICHE] businesses in [CITY or the nearest big market], AND **10 that are not doing well**.
2. Do comprehensive comparative research: **what do the winners have that the losers do not?** What do the winners have in common?
3. Capture **page structure and ORDER**: what comes first — image then CTA? What IS the CTA (copy, placement, repetition)? Section sequence, social proof placement, pricing visibility.
4. Build a **scoring matrix** that determines what a great [NICHE] website is and isn't — concrete, checkable criteria with weights.
5. Output: a **clear blueprint that a different model/session can consume** to build a winning site. **Everything must be evidenced** — every claim traced to a scraped URL.
6. Cross-validate the blueprint with a different lineage (Codex) before anything is built from it.
7. Tooling: use the Firecrawl REST API for the research (`/v2/search` to find candidates, `/v2/scrape` markdown for the shortlist; `FIRECRAWL_BEARER_AUTH` from `.env`; ≤25 scrape calls, report credits used).

---

Deliverable path: `artifacts/design-blueprints/<date>-research-<niche-slug>.md`
Sections: Winners (who + why, evidenced) · Losers (who + the misses) · Winners-vs-losers contrast table · Page-order patterns · CTA patterns · Scoring matrix · The build blueprint · Sources (every URL scraped).
