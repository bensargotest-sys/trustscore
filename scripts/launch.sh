#!/bin/bash
# TrustScore Launch - Execute Everything
# Auto-generated: 2026-02-11 19:21 UTC

set -e

echo "🚀 TrustScore Launch Sequence"
echo "=============================="
echo ""

# Check if repo exists
REPO_URL="https://github.com/bensargotest-sys/trustscore"
echo "Checking if repo exists..."
if curl -s -o /dev/null -w "%{http_code}" "$REPO_URL" | grep -q "200"; then
    echo "✅ Repo exists: $REPO_URL"
else
    echo "❌ Repo not found: $REPO_URL"
    echo ""
    echo "Please create the repo first:"
    echo "  1. Go to: https://github.com/new"
    echo "  2. Name: trustscore"
    echo "  3. Description: Universal trust and reputation scores for AI agents and MCP servers"
    echo "  4. Public ✓"
    echo "  5. Skip README/gitignore/license (we have them)"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo ""
echo "📦 Step 1: Push to GitHub"
echo "-------------------------"
bash /data/.openclaw/workspace/projects/trustscore/scripts/push-to-github.sh

echo ""
echo "🏷️  Step 2: Tag Release"
echo "----------------------"
cd /data/.openclaw/workspace/projects/trustscore
git tag v0.1.0
git push origin v0.1.0
echo "✅ Tagged v0.1.0"

echo ""
echo "📢 Step 3: Post Announcements"
echo "-----------------------------"
bash /data/.openclaw/workspace/projects/trustscore/scripts/post-announcements.sh

echo ""
echo "📋 Step 4: MCP Registry Submission"
echo "----------------------------------"
bash /data/.openclaw/workspace/projects/trustscore/scripts/submit-to-mcp.sh

echo ""
echo "=============================="
echo "🎉 TrustScore Launch Complete!"
echo "=============================="
echo ""
echo "Next steps:"
echo "  • Monitor GitHub stars/issues"
echo "  • Respond to community feedback"
echo "  • Track adoption metrics"
echo "  • Plan v0.2.0 features"
echo ""
echo "Links:"
echo "  • Repo: $REPO_URL"
echo "  • Website: https://trustscore-website.vercel.app"
echo "  • Docs: $REPO_URL/blob/main/README.md"
