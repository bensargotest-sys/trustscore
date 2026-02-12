#!/bin/bash

HTML_FILE="../v2-agent-optimized/v2-agent-optimized.html"
REPORT="test-results.txt"

echo "=== TrustScore v2 QA Test Suite ===" > $REPORT
echo "Test Time: $(date -u)" >> $REPORT
echo "" >> $REPORT

echo "1. FOOTER LINKS CHECK" >> $REPORT
echo "Searching for # placeholders in footer links..." >> $REPORT
grep -n 'footer.*href="#"' $HTML_FILE >> $REPORT 2>&1 || echo "✅ No # placeholder links found in footer" >> $REPORT
echo "" >> $REPORT

echo "2. COLOR CONTRAST CHECK" >> $REPORT
echo "Checking for correct orange color (#C74317)..." >> $REPORT
grep -n "#C74317" $HTML_FILE >> $REPORT 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Correct orange color found" >> $REPORT
else
    echo "❌ WARNING: #C74317 not found" >> $REPORT
fi
echo "" >> $REPORT

echo "3. COPY BUTTON IMPLEMENTATION" >> $REPORT
echo "Checking JavaScript copy functionality..." >> $REPORT
grep -A 10 "function copyCode" $HTML_FILE | head -15 >> $REPORT
echo "" >> $REPORT

echo "4. JSON-LD VALIDATION" >> $REPORT
echo "Extracting JSON-LD structured data..." >> $REPORT
sed -n '/<script type="application\/ld+json">/,/<\/script>/p' $HTML_FILE >> $REPORT
echo "" >> $REPORT

echo "5. ALL CTA LINKS" >> $REPORT
echo "Extracting all CTA button links..." >> $REPORT
grep -o 'class="btn.*href="[^"]*"' $HTML_FILE >> $REPORT
echo "" >> $REPORT

echo "6. FILE SIZE & LOAD TIME" >> $REPORT
SIZE=$(wc -c < $HTML_FILE)
echo "File size: $SIZE bytes ($(echo "scale=2; $SIZE/1024" | bc) KB)" >> $REPORT
if [ $SIZE -lt 51200 ]; then
    echo "✅ File size under 50KB (fast load)" >> $REPORT
else
    echo "⚠️ File size over 50KB" >> $REPORT
fi
echo "" >> $REPORT

echo "7. MOBILE RESPONSIVE CSS" >> $REPORT
echo "Checking mobile breakpoints..." >> $REPORT
grep -c "@media.*max-width" $HTML_FILE >> $REPORT
echo "mobile breakpoints found" >> $REPORT
echo "" >> $REPORT

echo "8. META TAGS FOR AGENTS" >> $REPORT
echo "Checking agent-specific meta tags..." >> $REPORT
grep 'meta name="install-command"' $HTML_FILE >> $REPORT
grep 'meta name="usage-command"' $HTML_FILE >> $REPORT
grep 'meta name="api-type"' $HTML_FILE >> $REPORT
echo "" >> $REPORT

cat $REPORT
