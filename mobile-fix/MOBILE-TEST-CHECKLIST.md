# Mobile Deployment Checklist

**CRITICAL:** Before claiming "mobile is fixed", this checklist must be COMPLETED and VERIFIED.

## ⚠️ CRITICAL: BRAVE BROWSER REQUIRED

**User Requirement (2026-02-11 21:30 UTC):**  
*"Remember remember to verify any new changes and try everything out using Brave before finalizing and sending me any new Website related updates."*

**ALL website testing MUST be done in Brave browser.**  
Chrome/Chromium testing is acceptable for preliminary checks ONLY.

---

## Pre-Deployment Testing (Development Environment)

### Test on Brave DevTools Device Emulator (MANDATORY)
- [ ] iPhone SE (375px × 667px) - Portrait
  - [ ] No horizontal scroll on any page section
  - [ ] All code blocks visible and readable
  - [ ] Text wraps appropriately within viewport
  - [ ] Copy buttons remain functional and positioned correctly
  - [ ] Navigation menu opens/closes without layout shifts

- [ ] iPhone 12/13 (390px × 844px) - Portrait
  - [ ] No horizontal scroll on any page section
  - [ ] All code blocks visible and readable
  - [ ] Text wraps appropriately within viewport
  - [ ] Copy buttons remain functional

- [ ] iPhone 14 Pro Max (430px × 932px) - Portrait
  - [ ] No horizontal scroll on any page section
  - [ ] All code blocks visible and readable
  - [ ] Text wraps appropriately within viewport

- [ ] Android Standard (360px × 640px) - Portrait
  - [ ] No horizontal scroll on any page section
  - [ ] All code blocks visible and readable
  - [ ] Text wraps appropriately within viewport
  - [ ] Smallest common viewport - CRITICAL test

### Landscape Testing
- [ ] iPhone SE (667px × 375px) - Landscape
  - [ ] Content still fits viewport
  - [ ] No horizontal scroll
  - [ ] Readable in landscape orientation

- [ ] Android (640px × 360px) - Landscape
  - [ ] Content still fits viewport
  - [ ] No horizontal scroll

### Test in Firefox Responsive Design Mode
- [ ] 375px viewport - No horizontal scroll
- [ ] 390px viewport - No horizontal scroll
- [ ] 430px viewport - No horizontal scroll
- [ ] 360px viewport - No horizontal scroll

### Specific Section Tests
- [ ] **Hero Section** - Fits viewport on all sizes
- [ ] **Stats Dashboard** - No overflow on mobile
- [ ] **Features Tiles** - Stack properly, no horizontal scroll
- [ ] **Live Data Section** - Provider cards fit viewport
- [ ] **API Reference Section** (CRITICAL - this was the problem area)
  - [ ] `trustscore_check` code block wraps properly
  - [ ] `trustscore_report` code block wraps properly
  - [ ] `trustscore_rank` code block wraps properly
  - [ ] All three code blocks readable on 375px viewport
- [ ] **FAQ Section** - Questions/answers fit viewport
- [ ] **Integration Grid** - Icons and text fit properly
- [ ] **CTA Banner** - Buttons stack correctly on mobile
- [ ] **Footer** - Links stack properly, no overflow

## Post-Deployment Testing (Production)

### Test on ACTUAL DEVICES (REQUIRED)
- [ ] **iPhone (Real Device)** - User (AB) to test:
  - [ ] Open https://trustscore-website.vercel.app
  - [ ] Navigate to MCP Tools section (#api)
  - [ ] Verify NO horizontal scroll exists
  - [ ] Try to scroll right (should NOT be possible)
  - [ ] Check all three code examples are fully visible
  - [ ] Test in Safari browser
  - [ ] Rotate to landscape - verify still works

- [ ] **Android Device (Real Device)** - If available:
  - [ ] Open https://trustscore-website.vercel.app
  - [ ] Navigate to MCP Tools section (#api)
  - [ ] Verify NO horizontal scroll exists
  - [ ] Try to scroll right (should NOT be possible)
  - [ ] Check all three code examples are fully visible
  - [ ] Test in Chrome browser

### Screenshot Evidence
- [ ] Take screenshots at each viewport size (375px, 390px, 430px, 360px)
- [ ] Save screenshots to `MOBILE-TEST-SCREENSHOTS/` directory
- [ ] Screenshot filenames: `{device}-{section}-{pass|fail}.png`
- [ ] Include screenshots in commit

### Performance Checks
- [ ] Page loads in <3 seconds on 3G connection
- [ ] No layout shifts (CLS score)
- [ ] Touch targets are ≥44px × 44px
- [ ] Font sizes are readable (≥11px minimum)

## Success Criteria

### MANDATORY (All must pass for deployment approval)
✅ Zero horizontal scroll on ANY mobile viewport (360px-430px)  
✅ All code blocks visible and readable on 375px viewport  
✅ User (AB) confirms fix on REAL iPhone device  
✅ All text wraps appropriately within viewport  
✅ Copy buttons still functional on mobile  

### DEPLOYMENT BLOCKERS (Any ONE of these = FIX FAILED)
❌ Horizontal scroll bar visible on any page  
❌ Code text cut off on right side  
❌ User can scroll horizontally at all  
❌ Layout breaks on any tested viewport  
❌ Copy buttons overlap content or become unusable  

## Verification Protocol

1. **Developer Testing** (15 min)
   - Run through Chrome DevTools checklist
   - Test at all 4 critical viewports (360px, 375px, 390px, 430px)
   - Test landscape orientations
   - Document findings in MOBILE-FIX-REPORT.md

2. **Deploy to Staging/Preview** (5 min)
   - Deploy to Vercel preview branch
   - Open preview URL on actual mobile device
   - Test MCP Tools section specifically

3. **User Acceptance Testing** (Required)
   - User (AB) opens site on their iPhone
   - User navigates to MCP Tools section
   - User confirms: "I can see all text, no horizontal scroll"
   - User approval = PASS ✅
   - User reports issues = FAIL ❌ (go back to diagnosis)

4. **Deploy to Production** (only after UAT approval)
   - Merge to main branch
   - Deploy to production
   - Re-verify on production URL

## If ANY Test Fails

1. **DO NOT DEPLOY** to production
2. Document exact failure in MOBILE-FIX-REPORT.md
3. Re-diagnose root cause
4. Apply additional fixes
5. Re-test from beginning of checklist
6. Repeat until ALL tests pass

## Sign-Off

- [ ] Developer: All DevTools tests passed ✅
- [ ] Developer: Test file verified working ✅
- [ ] Developer: Production HTML updated ✅
- [ ] User (AB): Real device testing approved ✅
- [ ] Final verification: No horizontal scroll on any viewport ✅

**Date Completed:** _____________  
**Tested By:** _____________  
**Approved By (User AB):** _____________  

---

**ZERO TOLERANCE POLICY:** This bug has been reported MULTIPLE times. Previous "fixes" did NOT work. This checklist ensures we actually fix it this time. Do not skip ANY steps.
