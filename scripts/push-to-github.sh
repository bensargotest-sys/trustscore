#!/bin/bash
# Push TrustScore to GitHub (execute once repo exists)
# Auto-generated: 2026-02-11 19:20 UTC

set -e

REPO_URL="https://github.com/bensargotest-sys/trustscore.git"
TOKEN_FILE="/data/.openclaw/workspace/.github-credentials"

cd /data/.openclaw/workspace/projects/trustscore

# Load GitHub credentials
if [ -f "$TOKEN_FILE" ]; then
    . "$TOKEN_FILE"
    AUTH_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${GITHUB_REPO}.git"
else
    echo "⚠️  No credentials file found, using unauthenticated URL"
    AUTH_URL="$REPO_URL"
fi

echo "🚀 Pushing TrustScore to GitHub..."
echo "   Repo: $REPO_URL"
echo "   Commits: $(git log --oneline | wc -l)"

# Set remote (overwrites if exists)
git remote remove origin 2>/dev/null || true
git remote add origin "$AUTH_URL"

# Push
git push -u origin main --force

echo "✅ Pushed to GitHub!"
echo "   View: ${REPO_URL%.git}"
echo ""
echo "Next steps:"
echo "  1. Tag release: git tag v0.1.0 && git push origin v0.1.0"
echo "  2. Submit to MCP Registry: bash scripts/submit-to-mcp.sh"
echo "  3. Post announcements: bash scripts/post-announcements.sh"
