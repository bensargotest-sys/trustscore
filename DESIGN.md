# TrustScore Website - Design System

## Design Philosophy

**Dual Audience Design:** A website that serves both **humans** (visual, emotional) and **AI agents** (structured, queryable).

### Core Principles

1. **Visual Clarity** (Human layer)
   - Apple-like simplicity
   - Flat design, no unnecessary shadows/gradients
   - White space for breathing room
   - Typography-driven hierarchy

2. **Structured Data** (Agent layer)
   - JSON-LD schema markup
   - Machine-readable API endpoints
   - Semantic HTML
   - Queryable data attributes

3. **Interaction Design**
   - Both audiences can navigate
   - Humans see beautiful UI
   - Agents extract structured data

---

## Color System

### Primary Colors
```css
--orange: #FF6B35;    /* Primary accent, CTA buttons, highlights */
--white: #FFFFFF;      /* Primary background, clean canvas */
--black: #1A1A1A;      /* Primary text, footer background */
```

### Neutral Colors
```css
--grey-light: #F5F5F5;  /* Section backgrounds, cards */
--grey-mid: #E0E0E0;    /* Borders, dividers */
--grey-dark: #757575;   /* Secondary text, captions */
```

### Usage Guidelines
- **Orange:** CTAs, active states, trust scores, brand accents
- **White:** Primary background, cards, clean space
- **Black:** Text, footer, code blocks
- **Grey-light:** Section backgrounds, inactive tiles
- **Grey-mid:** Borders, separators
- **Grey-dark:** Secondary text, labels

---

## Typography

### Font Stack
```css
font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif;
```

### Scale
- **H1:** 56px / 1.1 line-height (Hero headlines)
- **H2:** 42px / 1.2 line-height (Section titles)
- **H3:** 24px / 1.3 line-height (Card titles)
- **Body:** 16px / 1.6 line-height (Default text)
- **Small:** 14px / 1.4 line-height (Labels, captions)

### Weights
- **600:** Headings (semi-bold, Apple-like)
- **500:** Buttons, nav links (medium)
- **400:** Body text (regular)

### Letter Spacing
- **Headings:** -0.02em (tighter for display)
- **Labels:** 0.05em (wider for legibility)

---

## Spacing System

### Scale (8px base)
```css
--spacing-xs: 8px;    /* Tight spacing, icon gaps */
--spacing-sm: 16px;   /* Default gap between elements */
--spacing-md: 24px;   /* Card padding, section margins */
--spacing-lg: 48px;   /* Large gaps, nav spacing */
--spacing-xl: 96px;   /* Section padding, hero */
```

### Usage
- **8px:** Internal button padding, icon spacing
- **16px:** Between cards in grid
- **24px:** Card internal padding, container padding
- **48px:** Between major sections
- **96px:** Hero top/bottom padding

---

## Layout Components

### 1. Tile System

**Purpose:** Modular, scannable information blocks

**Structure:**
```html
<div class="tile">
  <div class="tile-icon">📊</div>
  <h3>Title</h3>
  <p>Description</p>
</div>
```

**Behavior:**
- Hover: Lift 4px + border color change to orange
- Grid: Auto-fit, min 280px
- Responsive: Collapses to single column on mobile

**For Agents:**
- Each tile contains `data-feature` attribute
- Structured content in semantic HTML
- Queryable via DOM

### 2. Stats Dashboard

**Purpose:** Live metrics, both visual and machine-readable

**Structure:**
```html
<div class="stats-dashboard">
  <div class="stat-tile" data-metric="servers" data-value="201">
    <div class="stat-number">201</div>
    <div class="stat-label">Servers Tracked</div>
  </div>
</div>
```

**Dual Audience:**
- **Humans:** See visual tile with large number
- **Agents:** Query `data-metric` and `data-value` attributes

### 3. API Explorer

**Purpose:** Show code examples (humans) + provide API schema (agents)

**Design:**
- Black background (code editor aesthetic)
- Syntax highlighting (orange, green, blue)
- Tabbed interface (Check, Report, Rank)
- Copy button (future enhancement)

**For Agents:**
- Hidden `<div class="api-endpoint">` tags with endpoint data
- OpenAPI spec link (future)

### 4. Live Data Section

**Purpose:** Real-time trust scores

**Components:**
- Pulse indicator (shows "live" status)
- Provider list with progress bars
- Score values in orange

**For Agents:**
- Each provider has `data-provider-id` and `data-trust-score`
- Queryable, parseable

---

## Interaction Patterns

### Hover States
```css
.tile:hover {
  transform: translateY(-4px);
  border-color: var(--orange);
}
```

**Philosophy:** Subtle lift + color change (Apple-like)

### Button States
- **Default:** Orange background, white text
- **Hover:** Lift 2px + shadow
- **Active:** Scale 0.98 (future)

### Loading States
- Skeleton screens (future)
- Pulse animation for live data

---

## Machine-Readable Layer

### JSON-LD Schema
```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "TrustScore",
  "description": "Trust scoring for AI agents"
}
```

**Purpose:** Help search engines + AI agents understand the page

### Data Attributes
```html
<div data-endpoint="/api/v1/trust-scores" data-method="GET"></div>
<div data-metric="servers" data-value="201"></div>
<div data-provider-id="github_api" data-trust-score="0.82"></div>
```

**Purpose:** Queryable data for AI agents

### Semantic HTML
- Use `<section>`, `<article>`, `<aside>` appropriately
- `<header>`, `<nav>`, `<footer>` for structure
- `<h1>`-`<h6>` hierarchy for headings

---

## Responsive Behavior

### Breakpoints
- **Desktop:** 1400px container max-width
- **Tablet:** 768px (hide nav, single column tiles)
- **Mobile:** Full-width, larger touch targets

### Grid Behavior
```css
grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
```

**Philosophy:** Auto-fit based on content, not device

---

## Performance Considerations

### File Size
- **HTML:** ~26KB (single file)
- **No frameworks:** Pure HTML/CSS
- **No images:** Unicode icons, CSS shapes
- **Load time:** <1s on 3G

### Optimization
- Critical CSS inline
- No external fonts (system fonts)
- Minimal JavaScript (future: progressive enhancement)

---

## Accessibility

### Current
- Semantic HTML structure
- Color contrast ratios (WCAG AA)
- Keyboard navigation (native)

### Future Enhancements
- ARIA labels for dynamic content
- Skip to content link
- Focus indicators
- Screen reader testing

---

## Future Enhancements

### Phase 1 (Week 1)
- [ ] Real-time WebSocket data
- [ ] Interactive API explorer (try it live)
- [ ] Copy code buttons
- [ ] Dark mode toggle

### Phase 2 (Week 2)
- [ ] Animated trust score charts
- [ ] Provider detail modal
- [ ] Search/filter providers
- [ ] Status history timeline

### Phase 3 (Week 3)
- [ ] OpenAPI spec viewer
- [ ] GraphQL explorer
- [ ] Playground environment
- [ ] SDK download buttons

---

## Design Rationale

### Why Tile-Based?
- **Modular:** Each feature is self-contained
- **Scannable:** Easy to skim for both humans and agents
- **Flexible:** Can rearrange/add tiles easily
- **Mobile-friendly:** Collapses gracefully

### Why Orange/White/Black/Grey?
- **Orange:** Warm, trustworthy, stands out
- **White:** Clean, Apple-like, emphasizes content
- **Black:** Professional, technical, readable
- **Grey:** Neutral, doesn't compete with content

### Why Flat Design?
- **Clarity:** No distractions from shadows/gradients
- **Speed:** Faster rendering, smaller file size
- **Timeless:** Won't look dated in 2 years
- **Accessible:** High contrast, clear hierarchy

### Why Dual Audience?
- **Future-proof:** AI agents will increasingly browse websites
- **Practical:** APIs need documentation for both humans and machines
- **Innovative:** Shows TrustScore understands AI-first design

---

## Brand Guidelines

### Voice & Tone
- **Confident, not arrogant:** "Trust infrastructure" not "The best"
- **Technical, not jargon:** "7 dimensions" not "multi-modal trust paradigm"
- **Human, not robotic:** "Know which services to trust" not "Optimize reliability metrics"

### Messaging Hierarchy
1. **Hero:** What it is (trust infrastructure for AI agents)
2. **Stats:** Proof of scale (201 servers, 99.9% uptime)
3. **Features:** How it works (tiles with benefits)
4. **API:** Technical details (code examples)
5. **CTA:** Get started (clear path forward)

---

## Maintenance

### Update Frequency
- **Stats:** Update monthly (servers tracked, response time)
- **Live scores:** Connect to real API (future)
- **Code examples:** Keep in sync with docs
- **Integrations:** Add new frameworks as supported

### Testing Checklist
- [ ] Desktop Chrome, Firefox, Safari
- [ ] Mobile iOS Safari, Android Chrome
- [ ] Keyboard navigation works
- [ ] All links functional
- [ ] Load time <1s
- [ ] No console errors

---

**Design Version:** 2.0  
**Last Updated:** 2026-02-11  
**Designer:** @RuntimeRogue (AI Agent)  
**Design Philosophy:** Dual audience (humans + AI agents), Apple-like simplicity, data-driven
