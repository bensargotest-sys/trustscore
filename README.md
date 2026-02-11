# TrustScore Website

**Live at:** https://trustscore-website.vercel.app

## Overview

Professional landing page for TrustScore - trust infrastructure for AI agents.

**Unique Feature:** Designed for **dual audience** (humans + AI agents).

## Design Philosophy

### Dual Audience Design

**For Humans:**
- Apple-like aesthetic (orange, white, black, grey)
- Tile-based layout for scannability
- Flat design, no unnecessary effects
- Typography-driven hierarchy

**For AI Agents:**
- JSON-LD schema markup
- Machine-readable data attributes
- Semantic HTML structure
- Queryable API endpoints

## Features

### Visual Layer (Humans)
- 🎨 Modern, Apple-inspired design
- 📱 Fully responsive (mobile-first)
- ⚡ Fast loading (<1s on 3G)
- 🎯 Clear information hierarchy
- 🔄 Real-time trust score displays
- 💻 Interactive code examples

### Data Layer (Agents)
- 📊 JSON-LD structured data
- 🔍 Queryable data attributes
- 🤖 Machine-readable endpoints
- 📝 Semantic HTML markup

## Tech Stack

- **HTML5** - Semantic markup
- **CSS3** - Custom design system (no frameworks)
- **JavaScript** - Progressive enhancement (minimal)
- **Vercel** - Global CDN deployment

## Design System

### Colors
- **Orange (#FF6B35):** Primary accent, CTAs
- **White (#FFFFFF):** Primary background
- **Black (#1A1A1A):** Text, footer
- **Grey (#F5F5F5, #E0E0E0, #757575):** Backgrounds, borders

### Typography
- **Font:** SF Pro Display (system fonts)
- **Weights:** 600 (headings), 500 (buttons), 400 (body)
- **Scale:** 56px → 42px → 24px → 16px → 14px

### Spacing
- **8px:** Micro spacing
- **16px:** Element gaps
- **24px:** Card padding
- **48px:** Section gaps
- **96px:** Hero padding

See [DESIGN.md](DESIGN.md) for complete design system documentation.

## Sections

1. **Hero** - Value proposition + CTA
2. **Stats Dashboard** - Live metrics (201 servers, 7 dimensions)
3. **Features Tiles** - 6 key capabilities
4. **Live Data** - Real-time trust scores with pulse indicator
5. **API Explorer** - Code examples with syntax highlighting
6. **Integrations** - Framework support (LangGraph, CrewAI, etc.)
7. **CTA Banner** - Final call-to-action
8. **Footer** - Navigation + resources

## Deployment

### Production
```bash
npx vercel --prod
```

**URL:** https://trustscore-website.vercel.app

### Local Development
```bash
# Serve locally
npx serve .

# Or just open index.html
open index.html
```

## Performance

- **Load time:** <1s
- **File size:** 26KB (single HTML file)
- **No dependencies:** Self-contained
- **CDN:** Global edge deployment via Vercel

## Accessibility

- ✅ Semantic HTML structure
- ✅ WCAG AA color contrast
- ✅ Keyboard navigation
- ✅ System font support
- ⏳ ARIA labels (future)
- ⏳ Screen reader testing (future)

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers

## Future Enhancements

### Phase 1
- [ ] Real-time WebSocket data
- [ ] Interactive API playground
- [ ] Copy code buttons
- [ ] Dark mode toggle

### Phase 2
- [ ] Animated trust score charts
- [ ] Provider detail modals
- [ ] Search/filter functionality
- [ ] Status history timeline

### Phase 3
- [ ] OpenAPI spec viewer
- [ ] GraphQL explorer
- [ ] Live playground environment
- [ ] SDK download section

## Updates

To update the website:

1. **Edit** `index.html`
2. **Commit:** `git commit -am "Update: [description]"`
3. **Deploy:** `npx vercel --prod`

Changes are live in ~10 seconds.

## License

MIT License (same as TrustScore project)

## Credits

**Design:** @RuntimeRogue (AI Agent)  
**Philosophy:** Dual audience design (humans + AI agents)  
**Built:** 2026-02-11 in autonomous mode  
**Updated:** 2026-02-11 (v2.0 - Apple-like redesign)

---

**Design Principles:**
1. Serve both humans and AI agents
2. Apple-like simplicity and clarity
3. Tile-based, modular layout
4. Flat design, no unnecessary effects
5. Data-driven, real-time updates

See [DESIGN.md](DESIGN.md) for complete design documentation.
