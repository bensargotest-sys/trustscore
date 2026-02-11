# TrustScore Website - Copy Review
**Date:** 2026-02-11  
**Standard:** Grade A professional SaaS copy (Stripe, Vercel, Anthropic level)  
**Status:** 🟡 Good foundation, needs refinement for excellence

---

## Executive Summary
The website copy is **functional and clear** but lacks the **punch and specificity** that makes top-tier SaaS copy compelling. The writing is technically accurate but reads somewhat generic—it describes *what* TrustScore is without making you *feel* why you need it.

**Overall Grade:** B+ (solid professional copy, not yet Grade A)

---

## 1. Hero Section

### "Trust Infrastructure for AI Agents"
**Issue:** Generic and vague  
- ✅ **What works:** "Infrastructure" signals seriousness  
- ❌ **What doesn't:** Could describe 50 different products  
- ❌ **Missing:** What problem does this solve? What pain point?  

**Better alternatives:**
- "Know Which AI Tools to Trust" (benefit-first)
- "Reputation System for AI Services" (clearer category)
- "Stop Guessing. Trust with Data." (problem → solution)

### Tagline: "Community-driven reliability tracking for 200+ MCP servers. Synthetic baseline refined by real agent reports."
**Issues:**
- ✅ **What works:** Specific number (200+), mentions community
- ❌ **Jargon overload:** "Synthetic baseline refined" — what does this mean to a new user?
- ❌ **Passive voice:** "refined by" — weak construction
- ❌ **Two ideas competing:** Community-driven OR synthetic baseline? Pick one for hero, explain other later.

**Recommended rewrite:**
> "Crowdsourced reliability scores for 200+ AI tools. Real agents, real usage, real trust."

### CTAs: "Get Started" / "View API"
- ✅ **Clear and standard** — no issues here
- **Minor improvement:** Consider "Browse Scores" instead of "View API" (less technical, more benefit-focused)

---

## 2. Stats Section

### Numbers: 202 / 7 / 9.3K / 2-8ms
**Issues:**
- ✅ **Specific numbers good** (not rounded)
- ❌ **"7 Trust Dimensions"** — what does this mean? Confusing without context
- ❌ **"9.3K Interactions"** — is this impressive? Needs context ("per day"? "total"?)
- ⚠️ **"2-8ms Query Time"** — excellent technical detail BUT most users don't care; save for docs

### Labels: "SERVERS TRACKED" vs alternatives
**Current labels:**
- Servers Tracked ✅
- Trust Dimensions ❌ (vague)
- Interactions ⚠️ (needs qualifier)
- Query Time ⚠️ (too technical for hero area)

**Recommended rewrites:**
- ~~"Trust Dimensions"~~ → **"Reliability Metrics"**
- ~~"Interactions"~~ → **"9.3K Reports Submitted"** or **"Daily Updates"**
- ~~"Query Time"~~ → Move to "Production Ready" section or footer

---

## 3. Features Section

### Overall Assessment
- ✅ **Clear structure** — each card has icon, title, description
- ❌ **Feature-focused, not benefit-focused** — tells what it does, not why I care
- ❌ **Some descriptions are too technical** — "Synthetic baseline refined by real usage" appears again

### Card-by-Card Review:

#### 📊 Multi-Dimensional
**Current:** "Track reliability, uptime, latency, error rate, quality, freshness, and security across 7 dimensions."

**Issues:**
- Lists features, not benefits
- "7 dimensions" repeated from stats (redundant)

**Rewrite:**
> "Compare providers across 7 metrics—uptime, speed, reliability, and more. See the full picture, not just marketing claims."

---

#### ⚡ Community-Driven
**Current:** "Trust scores update based on agent reports. Synthetic baseline refined by real usage."

**Issues:**
- "Synthetic baseline refined" — still confusing jargon
- Doesn't explain WHY community-driven matters

**Rewrite:**
> "Real agents report real outcomes. Scores improve as more tools are tested—no vendor bias, just data."

---

#### 🎯 Smart Discovery
**Current:** "Find trusted providers by category. Get ranked lists instantly with confidence levels."

**Issues:**
- Too generic ("Smart Discovery" — every SaaS claims this)
- "confidence levels" — vague

**Rewrite:**
> "Search by task, get ranked results in milliseconds. See which tools actually deliver, with sample sizes and confidence scores."

---

#### 🔌 MCP Native
**Current:** "Built as MCP server. Works with Claude Desktop, Cursor, Cline, and any MCP client."

**Issues:**
- ✅ **Actually quite good** — specific integrations
- ⚠️ Minor: "MCP Native" assumes you know what MCP is

**Rewrite (optional):**
> "Works everywhere you work. Claude Desktop, Cursor, Cline—install once, use anywhere."

---

#### 🛡️ Confidence Tracking
**Current:** "Know when scores are reliable. High/medium/low confidence based on sample size."

**Issues:**
- Title is feature-focused ("Confidence Tracking"), not benefit
- Description is clear ✅

**Rewrite title:**
> "🛡️ No Guesswork"

---

#### 🚀 Production Ready
**Current:** "100% test coverage, all tests passing, comprehensive documentation."

**Issues:**
- Too engineering-focused (good for footer, not hero area)
- Doesn't communicate user benefit

**Rewrite:**
> "Battle-tested and documented. Used in production by AI agents making real decisions."

---

## 4. MCP Tools Section

### Overall Assessment
- ✅ **Code examples excellent** — clear, concise, realistic
- ✅ **Tool names descriptive** — `trustscore_check`, `trustscore_report`, `trustscore_rank`
- ❌ **Card descriptions a bit technical** — assumes MCP familiarity

### Card-by-Card Review:

#### `trustscore_check`
**Current:** "Get detailed trust data for a provider. Returns score, reliability, confidence, flags, and history."

**Issue:** Lists return values (good) but doesn't explain use case

**Rewrite:**
> "Check a provider before you use it. Get trust score, reliability metrics, red flags, and historical performance—all in one call."

---

#### `trustscore_report`
**Current:** "Report interaction outcomes. Scores update based on your reports. Help improve data quality."

**Issue:** "Help improve data quality" sounds like charity work, not a feature

**Rewrite:**
> "Report your results. Every outcome you share makes the scores more accurate—for you and everyone else."

---

#### `trustscore_rank`
**Current:** "Get ranked list of providers by trust score. Filter by task type and minimum score."

**Issue:** Minor—very clear, could be punchier

**Rewrite:**
> "Compare multiple providers at once. Filter by task, set minimum thresholds, get ranked results instantly."

---

## 5. Overall Copy Issues

### Spelling & Grammar
✅ **Perfect** — no errors found

### Tone Consistency
⚠️ **Inconsistent mix:**
- Hero section: Corporate/technical ("Trust Infrastructure")
- Features: Mix of friendly ("Smart Discovery") and technical ("MCP Native")
- API section: Developer-focused (appropriate)

**Recommendation:** Choose a consistent voice:
- **Option A:** Technical/precise (like Anthropic) — "Reliability oracle for AI agents"
- **Option B:** Clear/accessible (like Stripe) — "Trust scores for the tools your agents use"

### Jargon Audit
❌ **Too much unexplained jargon:**
- "Synthetic baseline" (appears 3x, never explained)
- "MCP server" (never explained before first use)
- "Trust dimensions" (vague, academic)
- "Confidence levels" (used without context)

**Fix:** Either explain on first use OR replace with plain language

---

### CTA Effectiveness

**Current CTAs:**
1. Hero: "Get Started" / "View API" ✅ Clear
2. Bottom: "Get Started" / "Documentation" ✅ Clear

**Issue:** No urgency, no specificity

**Improvement ideas:**
- "Browse 200+ Trust Scores" (specific action)
- "Try the API" (lower friction than "Get Started")
- "See Live Scores" (immediate value)

---

## 6. Missing Elements

### What's NOT on the page that should be:
1. **Social proof** — "Used by X agents" or testimonials
2. **Problem statement** — What happens WITHOUT TrustScore? (wasted time, broken tools, uncertainty)
3. **Comparison** — How is this different from just reading GitHub stars?
4. **Use case examples** — "When agent needs weather data, TrustScore ranks 12 providers by reliability"

---

## 7. Redundant Copy

See `REDUNDANT-TEXT.md` for removal suggestions.

---

## Priority Fixes (High → Low)

### 🔴 High Priority
1. Replace "Trust Infrastructure for AI Agents" with benefit-driven headline
2. Simplify hero tagline (remove "synthetic baseline refined")
3. Explain or remove "synthetic baseline" jargon
4. Rewrite feature cards to emphasize benefits over features

### 🟡 Medium Priority
5. Add context to stats ("9.3K interactions" → "9.3K reports submitted")
6. Remove or relocate "2-8ms query time" stat (too technical)
7. Improve feature card titles (benefit-focused)
8. Add one sentence explaining what MCP is

### 🟢 Low Priority
9. Make CTAs more specific ("Browse Scores", "Try API")
10. Add social proof or usage examples
11. Consistent tone throughout (pick technical OR accessible)

---

## Conclusion

**Strengths:**
- Technically accurate ✅
- Well-structured ✅
- Clear hierarchy ✅
- Code examples excellent ✅

**Weaknesses:**
- Generic messaging (could be any B2B SaaS)
- Jargon not explained ("synthetic baseline")
- Feature-focused, not benefit-focused
- Missing emotional hook or problem statement

**To reach Grade A:** Lead with a problem, speak in benefits, lose the jargon.

---

**Next Steps:**
1. Read `COPY-IMPROVEMENTS.md` for specific rewrites
2. Read `REDUNDANT-TEXT.md` for deletion candidates
3. Implement high-priority fixes first
4. A/B test new hero headline
