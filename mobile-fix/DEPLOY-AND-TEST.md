# Deployment and Testing Guide

**Status:** Ready for deployment and testing  
**Date:** 2026-02-11  
**Emergency Level:** CRITICAL (User frustrated - multiple failed attempts)

---

## What Was Fixed

### Problem
- Code blocks overflowing on mobile devices (iPhone ~375px width)
- Text cut off on right side
- Horizontal scrollbar visible
- Affects MCP Tools section specifically

### Root Cause
- `white-space: pre` in CSS prevented text wrapping
- Code examples wider than mobile viewport
- Body `overflow-x: hidden` clipped content instead of scrolling

### Solution Applied
1. Changed `white-space: pre` → `white-space: pre-wrap`
2. Added `word-wrap`, `word-break`, `overflow-wrap` for comprehensive wrapping
3. Added `max-width: 100%` constraints at all levels (html, body, container, code-block)
4. Added mobile-specific optimizations (smaller font, reduced padding)
5. Fixed `box-sizing` to include padding in width calculations
6. Reduced API grid minmax from 350px to 280px for mobile compatibility

---

## Files Modified

### 1. `/data/.openclaw/workspace/projects/trustscore-website/index.html`
**Changes:**
- `.code-block code`: `white-space: pre-wrap` + word-break properties
- `.code-block`: Added `max-width: 100%` and `box-sizing: border-box`
- `html` and `body`: Added `max-width: 100vw`
- `.container`: Added `width: 100%` and `box-sizing: border-box`
- `.api-card`: Added `max-width: 100%`, `box-sizing`, and `overflow: hidden`
- `.api-grid`: Changed minmax from 350px to 280px
- New `@media (max-width: 480px)` block for mobile code blocks

**Total changes:** ~15 CSS property additions/modifications

### 2. Test Files Created (in `mobile-fix/` directory)
- `test-mobile.html` - Isolated test case showing before/after
- `MOBILE-FIX-DETAILED.md` - Root cause analysis
- `MOBILE-TEST-CHECKLIST.md` - Comprehensive testing checklist
- `DEPLOY-AND-TEST.md` - This file
- `MOBILE-TEST-SCREENSHOTS/` - Screenshot directory

---

## Testing Protocol

### Phase 1: Local Testing (Browser DevTools)

**Required before deployment:**

1. **Open Chrome DevTools**
   - Press F12
   - Click "Toggle device toolbar" (Ctrl+Shift+M)

2. **Test at these exact viewport sizes:**

   | Device | Viewport | Test Result |
   |--------|----------|-------------|
   | iPhone SE | 375 × 667 | ⏳ PENDING |
   | iPhone 12/13 | 390 × 844 | ⏳ PENDING |
   | iPhone 14 Pro Max | 430 × 932 | ⏳ PENDING |
   | Android | 360 × 640 | ⏳ PENDING |

3. **For EACH viewport:**
   - Open `index.html` in browser
   - Navigate to "MCP Tools" section (#api anchor)
   - Check all 3 code blocks:
     - `trustscore_check`
     - `trustscore_report`
     - `trustscore_rank`
   - Verify: NO horizontal scrollbar on page
   - Verify: All code text visible (not cut off)
   - Verify: Code wraps within viewport
   - Verify: Copy buttons still work
   - Take screenshot and save to `MOBILE-TEST-SCREENSHOTS/`

4. **Test Landscape Orientation:**
   - Rotate device (click rotate icon in DevTools)
   - Verify no horizontal scroll in landscape mode
   - Test at 667×375 (iPhone SE landscape)

5. **Test in Firefox:**
   - Open Responsive Design Mode (Ctrl+Shift+M)
   - Test same viewport sizes
   - Verify consistent behavior

6. **Document Results:**
   - Update `MOBILE-TEST-CHECKLIST.md` with checkmarks
   - Save screenshots with naming: `{device}-{section}-{pass|fail}.png`
   - Example: `iphone-se-api-section-pass.png`

### Phase 2: Deploy to Vercel Preview

**After Phase 1 passes:**

1. **Check Vercel credentials:**
   ```bash
   source /data/.openclaw/workspace/.vercel-credentials
   echo $VERCEL_TOKEN
   ```

2. **Deploy to preview:**
   ```bash
   cd /data/.openclaw/workspace/projects/trustscore-website
   
   # Deploy to preview (not production)
   vercel --token=$VERCEL_TOKEN
   
   # Note the preview URL (e.g., trustscore-website-abc123.vercel.app)
   ```

3. **Share preview URL with user (AB):**
   - Send preview URL via Telegram
   - Ask user to test on their iPhone
   - Provide clear instructions (see below)

### Phase 3: Real Device Testing (User AB) - REQUIRED

**User Testing Instructions (send to AB):**

```
Hey! I've deployed a fix for the mobile code overflow issue. 

Can you test it on your iPhone? Here's what to check:

1. Open this URL on your iPhone:
   https://trustscore-website-[preview-id].vercel.app

2. Scroll down to the "MCP Tools" section (black background)

3. Look at the three code examples:
   - trustscore_check
   - trustscore_report
   - trustscore_rank

4. Check these things:
   ✓ Can you see ALL the text in each code block?
   ✓ Is any text cut off on the right side?
   ✓ Can you scroll the page horizontally? (you shouldn't be able to)
   ✓ Does the code wrap to multiple lines properly?

5. Try rotating your phone to landscape - does it still work?

Please reply with:
- ✅ "Looks good, no horizontal scroll, all text visible"
OR
- ❌ "Still seeing problems: [describe what you see]"

If you can, take a screenshot of the MCP Tools section and send it.

Thanks!
```

**Success Criteria:**
- User confirms: "No horizontal scroll"
- User confirms: "All text visible"
- User confirms: "Code blocks look good"
- No screenshot shows text cutoff
- No screenshot shows horizontal scrollbar

**If user reports problems:**
- Request detailed description
- Request screenshot
- DO NOT deploy to production
- Return to diagnosis phase
- Document what failed in MOBILE-FIX-DETAILED.md

### Phase 4: Production Deployment

**ONLY proceed if Phase 3 passes!**

1. **User has approved fix? ✅**
   - If NO: Stop here, go back to diagnosis
   - If YES: Proceed to step 2

2. **Commit changes:**
   ```bash
   cd /data/.openclaw/workspace/projects/trustscore-website
   
   git add index.html
   git add mobile-fix/
   git commit -m "Fix: Mobile code block overflow (verified on iPhone)

   - Changed white-space: pre to pre-wrap for code blocks
   - Added max-width: 100% constraints at all levels
   - Added mobile-specific font size and padding optimizations
   - Tested and verified on iPhone SE/12/14 Pro Max viewports
   - User (AB) confirmed fix working on real device
   
   Closes: Mobile content overflow issue (reported multiple times)"
   ```

3. **Push to GitHub:**
   ```bash
   source /data/.openclaw/workspace/.github-credentials
   git remote set-url origin https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git
   git push origin main
   ```

4. **Deploy to Vercel production:**
   ```bash
   vercel --prod --token=$VERCEL_TOKEN
   ```

5. **Verify production deployment:**
   - Open https://trustscore-website.vercel.app
   - Navigate to #api section
   - Quick check: No horizontal scroll
   - Ask user to verify production site as final confirmation

6. **Update documentation:**
   - Mark MOBILE-TEST-CHECKLIST.md as ✅ COMPLETE
   - Update MOBILE-FIX-DETAILED.md with final test results
   - Add sign-off section with dates and approvals

---

## Quick Start Commands

### Test Locally (Browser)
```bash
# Option 1: Open in default browser
xdg-open /data/.openclaw/workspace/projects/trustscore-website/index.html

# Option 2: Python HTTP server
cd /data/.openclaw/workspace/projects/trustscore-website
python3 -m http.server 8080
# Then open http://localhost:8080 in browser with DevTools
```

### Test the Isolated Test Case
```bash
xdg-open /data/.openclaw/workspace/projects/trustscore-website/mobile-fix/test-mobile.html

# OR via HTTP server:
cd /data/.openclaw/workspace/projects/trustscore-website/mobile-fix
python3 -m http.server 8081
# Then open http://localhost:8081/test-mobile.html
```

### Deploy to Vercel Preview
```bash
cd /data/.openclaw/workspace/projects/trustscore-website
source /data/.openclaw/workspace/.vercel-credentials
vercel --token=$VERCEL_TOKEN
```

### Deploy to Vercel Production (after user approval)
```bash
cd /data/.openclaw/workspace/projects/trustscore-website
source /data/.openclaw/workspace/.vercel-credentials

# Commit and push
git add -A
git commit -m "Fix: Mobile code block overflow (user verified)"
source /data/.openclaw/workspace/.github-credentials
git remote set-url origin https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git
git push origin main

# Deploy
vercel --prod --token=$VERCEL_TOKEN
```

---

## Verification Checklist

Use this as a quick checklist during testing:

### DevTools Testing
- [ ] iPhone SE (375px) - No horizontal scroll ✅
- [ ] iPhone SE (375px) - All code visible ✅
- [ ] iPhone 12 (390px) - No horizontal scroll ✅
- [ ] iPhone 14 Pro Max (430px) - No horizontal scroll ✅
- [ ] Android (360px) - No horizontal scroll ✅
- [ ] Landscape mode - No horizontal scroll ✅
- [ ] Firefox responsive mode - No horizontal scroll ✅
- [ ] Screenshots taken and saved ✅

### Real Device Testing (Critical!)
- [ ] Preview deployed to Vercel ✅
- [ ] User (AB) tested on iPhone ✅
- [ ] User confirmed: No horizontal scroll ✅
- [ ] User confirmed: All text visible ✅
- [ ] User provided screenshot (if possible) ✅
- [ ] No issues reported by user ✅

### Production Deployment
- [ ] User approval received ✅
- [ ] Changes committed to git ✅
- [ ] Pushed to GitHub ✅
- [ ] Deployed to Vercel production ✅
- [ ] Production site verified ✅
- [ ] User verified production site ✅
- [ ] Documentation updated ✅

---

## Troubleshooting

### Issue: "Still seeing horizontal scroll on iPhone"

**Diagnosis:**
1. Which section has horizontal scroll?
2. What is the exact viewport width?
3. Is it ALL pages or just specific sections?

**Possible causes:**
- Images without max-width: 100%
- Tables without overflow wrapping
- Fixed-width elements
- SVG graphics without viewBox
- Pre-formatted text in other sections

**Solution:**
- Identify specific element causing overflow
- Apply same fix pattern: `max-width: 100%` + `box-sizing: border-box`
- Add to mobile media query if needed

### Issue: "Code blocks look weird / text too small"

**Diagnosis:**
- At what viewport size?
- "Too small" = font size or container size?

**Solution:**
- Adjust mobile media query font-size
- Current: 11px on mobile (480px and below)
- Can increase to 12px if needed:
  ```css
  @media (max-width: 480px) {
      .code-block code {
          font-size: 12px;  /* Was 11px */
      }
  }
  ```

### Issue: "Copy button doesn't work on mobile"

**Diagnosis:**
- Is button visible?
- Is it positioned correctly?
- Does it respond to touch?

**Solution:**
- Verify min-width: 44px and min-height: 44px (touch target size)
- Check z-index and positioning
- Test clipboard API works on HTTPS (required for navigator.clipboard)

### Issue: "Text wraps in weird places"

**Diagnosis:**
- Where does it wrap?
- Is it breaking in middle of words?

**Solution:**
- This is expected with `word-break: break-word`
- Better than text cut off
- Can adjust with `hyphens: auto` if needed:
  ```css
  .code-block code {
      hyphens: auto;
      -webkit-hyphens: auto;
  }
  ```

---

## Rollback Plan

If critical issues found in production:

1. **Immediate rollback:**
   ```bash
   cd /data/.openclaw/workspace/projects/trustscore-website
   git revert HEAD
   git push origin main
   vercel --prod --token=$VERCEL_TOKEN
   ```

2. **Verify rollback:**
   - Check production site
   - Confirm it's back to previous version
   - Notify user

3. **Re-diagnose:**
   - Document what went wrong
   - Create new test cases
   - Apply new fix
   - Re-test completely before redeploying

---

## Success Metrics

### Technical Metrics
- ✅ Zero horizontal scroll on viewports 360px-430px
- ✅ All code text visible (no clipping)
- ✅ Page width ≤ viewport width at all times
- ✅ Copy buttons functional on mobile
- ✅ Layout stable (no shifts) on mobile

### User Metrics
- ✅ User (AB) confirms fix working
- ✅ User can read all code examples on iPhone
- ✅ No user-reported mobile issues for 7 days post-deployment
- ✅ User satisfaction restored

### Business Metrics
- ✅ Mobile documentation usable
- ✅ API section accessible on mobile
- ✅ No mobile user complaints
- ✅ Issue marked as RESOLVED

---

## Contact

**Developer:** Subagent (mobile-ux-emergency)  
**Date:** 2026-02-11  
**User (Tester):** AB via Telegram  
**Status:** Ready for Phase 1 testing  

---

## Next Steps

**RIGHT NOW:**
1. Test in Chrome DevTools at all mobile viewports
2. Document results in MOBILE-TEST-CHECKLIST.md
3. Take screenshots

**AFTER DevTools testing passes:**
1. Deploy to Vercel preview
2. Share preview URL with user (AB)
3. Wait for user approval

**AFTER user approves:**
1. Commit to git
2. Push to GitHub
3. Deploy to production
4. Verify production
5. Mark issue as RESOLVED

**DO NOT skip user testing!** Previous fixes failed because they weren't verified on real devices. User approval is MANDATORY.
