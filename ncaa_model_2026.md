# 2026 NCAA Tournament Model Analysis
**Date:** March 4, 2026  
**Stage:** 13 days to Selection Sunday (March 9)  
**Status:** Pre-seeding, market highly inefficient

---

## MODEL METHODOLOGY

**Data Source:** AP Top 25 Rankings (as of March 4, 2026) + team records

**Calculation:**
1. Assign seed tier based on AP ranking:
   - AP #1-4 → 1-seed tier (base 12% championship probability)
   - AP #5-10 → 2-seed tier (base 8%)
   - AP #11-18 → 3-seed tier (base 4%)
   - AP #19+ → 4-seed tier (base 1.5%)

2. Adjust by win percentage relative to tournament average (76.0%)
   - Teams with better records get modest boost within their tier

3. Clamp final probability between 0.5% and 30%

**Rationale:** AP ranking is the strongest predictor of seeding, which is the strongest predictor of tournament success. Win-loss record is secondary but helps distinguish within tiers.

---

## MODEL TOP 15

| Rank | Team | AP# | Record | Seed Est. | Championship Prob |
|------|------|-----|--------|-----------|------------------|
| 1 | Duke | 1 | 27-2 | 1-seed | **12.62%** |
| 2 | Arizona | 2 | 27-2 | 1-seed | **12.62%** |
| 3 | Michigan | 3 | 27-2 | 1-seed | **12.62%** |
| 4 | UConn | 4 | 27-3 | 1-seed | **12.50%** |
| 5 | Nebraska | 9 | 25-4 | 2-seed | **8.24%** |
| 6 | Iowa State | 6 | 24-5 | 2-seed | **8.16%** |
| 7 | Houston | 7 | 24-5 | 2-seed | **8.16%** |
| 8 | Michigan State | 8 | 24-5 | 2-seed | **8.16%** |
| 9 | Florida | 5 | 23-6 | 2-seed | **8.08%** |
| 10 | Texas Tech | 10 | 22-7 | 2-seed | **8.00%** |
| 11 | Gonzaga | 12 | 28-3 | 3-seed | **4.17%** |
| 12 | Virginia | 13 | 25-4 | 3-seed | **4.12%** |
| 13 | St. John's | 18 | 23-6 | 3-seed | **4.04%** |
| 14 | North Carolina | 17 | 23-6 | 3-seed | **4.04%** |
| 15 | Illinois | 11 | 22-7 | 3-seed | **4.00%** |

---

## MARKET vs MODEL: EDGE ANALYSIS

### MOST SIGNIFICANT MISPRICINGS

**1. IOWA STATE — MASSIVELY UNDERPRICED ⭐⭐⭐**
- Model: 8.16%
- Market: 2.45%
- **Ratio: 3.33x underpriced**
- Edge: +5.71% absolute value
- **Status:** STRONG BUY
- Context: They're AP#6 with a 24-5 record. Market has them priced like a 4-seed. Selection Sunday will reveal their true seed — if they get 2-seed as expected, price should jump 2-3x immediately.
- Entry strategy: BUY NOW before seeding, SELL on Selection Sunday jump

**2. VIRGINIA — MASSIVELY UNDERPRICED ⭐⭐**
- Model: 4.12%
- Market: 0.75%
- **Ratio: 5.49x underpriced**
- Edge: +3.37% absolute value
- **Status:** INTERESTING BUT RISKY
- Context: AP#13, 25-4 record. Trading at 75bps like a low-ranked Cinderella, but they're a tournament-tested team. Likely 3-seed.
- Problem: We already hold Virginia at 0.75c. This suggests market is being rational if they're below their true strength. Consider: is model overestimating Virginia's tournament odds? Or is market pricing in coaching/injury concerns we don't know about?
- Decision: HOLD existing Virginia position (small, not adding)

**3. DUKE — OVERPRICED (by market standards) ⚠️**
- Model: 12.62%
- Market: 22.00%
- **Ratio: 0.57x (overpriced)**
- Edge: Market paying +9.38% premium
- **Status:** AVOID
- Context: Duke IS the AP#1, but market is pricing them at near double their model probability. This suggests market has extreme Duke recency bias or information we don't have (roster health, tournament history, coach reputation premium).
- Decision: DO NOT BUY Duke

**4. MICHIGAN — OVERPRICED ⚠️**
- Model: 12.62%
- Market: 17.50%
- **Ratio: 0.72x**
- Edge: Market paying +4.88% premium
- Decision: AVOID

**5. FLORIDA — SLIGHTLY OVERPRICED**
- Model: 8.08%
- Market: 10.55%
- **Ratio: 0.77x**
- Edge: Small, but consistent overpricing of high AP-rank teams
- Decision: PASS

**6. ARIZONA — FAIRLY PRICED ✓**
- Model: 12.62%
- Market: 11.60%
- **Ratio: 1.09x**
- Edge: Essentially none
- Decision: PASS (fair price)

---

## CURRENT HOLDINGS vs MODEL

| Team | Shares | Entry Price | Current Price | Model % | Market % | Comment |
|------|--------|-------------|---------------|---------|----------|---------|
| Illinois | 40 | 4.19c | 4.25c | 4.00% | 4.25% | FAIR: Model and market align |
| Virginia | ??? | 0.75c | 0.75c | 4.12% | 0.75% | UNDERPRICED but holding small |

---

## RECOMMENDATION SUMMARY

**DO THIS NOW (before Selection Sunday March 9):**

1. **ADD to Iowa State** — Already entered $30 position
   - Thesis: 3.33x underpriced pre-seeding
   - Strategy: Hold until Selection Sunday seeding announcement, sell on the jump
   - Expected timeline: 5 days to major catalyst

2. **CONSIDER: Take profit on Virginia if rally occurs**
   - Virginia is massively underpriced (5.49x) relative to model
   - But we got in at 0.75c for a reason — market may be right about risks we missed
   - If price rallies to 2-3c, consider trimming position to lock in gains
   - Don't add more; let it run small

3. **DO NOT ADD:**
   - Duke (overpriced)
   - Michigan (overpriced)
   - Florida (overpriced)
   - Illinois (fair, no edge to add)

**Strategy:** This is a 5-10 day window of edge. Selection Sunday on March 9 will lock in seedings and market will become much more efficient. After that, edge evaporates quickly.

---

## RISKS TO MODEL

1. **Coach/Health information we don't have** — If a key player is injured or a coach is facing issues, market might be rational to misprice
2. **Tournament experience premium** — Market might be right that some teams (Duke, Michigan) have intangible tournament factors
3. **Recent form** — Model is static; teams getting hot/cold in final weeks could shift probability
4. **Cinderella effect** — Model may underestimate upset potential (Gonzaga, Virginia, etc.)

---

## NEXT STEPS

1. Monitor Selection Sunday announcement (March 9)
2. Once seedings lock, compare to model expectations
3. Identify "seed shock" opportunities (teams seeded higher/lower than expected)
4. Flip Iowa State and Virginia positions if they rally post-seeding
5. Consider fresh entry points on teams that get shocking seeds
