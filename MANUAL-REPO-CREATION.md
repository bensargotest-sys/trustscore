# Manual GitHub Repo Creation (2 minutes)

**Status:** Token auth failed, manual creation required  
**Time:** 2026-02-11 19:21 UTC

## Quick Steps

1. **Go to:** https://github.com/new

2. **Fill in:**
   - Repository name: `trustscore`
   - Description: `Universal trust and reputation scores for AI agents and MCP servers`
   - Public ✓
   - **Skip** README, .gitignore, license (we have them)

3. **Click:** "Create repository"

4. **Done!** Tell agent "created" or just run:
   ```bash
   bash /data/.openclaw/workspace/projects/trustscore/scripts/launch.sh
   ```

## What Happens Next (Automated)

The launch script will:
1. ✅ Push all 8 commits to GitHub
2. ✅ Tag v0.1.0 release
3. ✅ Display social media announcements
4. ✅ Show MCP Registry submission guide

**Total time:** ~2 minutes setup + 30 seconds execution

## Alternative: Try Token Fix

If you want to debug the token instead:
1. Go to: https://github.com/settings/tokens
2. Check token has `repo` scope
3. Verify token hasn't expired
4. Try regenerating token

**But manual is faster** (guaranteed to work in 2 minutes vs 10-15 minutes debugging)
