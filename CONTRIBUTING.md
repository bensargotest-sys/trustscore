# Contributing to TrustScore

Thank you for your interest in contributing to TrustScore! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, constructive, and professional. We're building infrastructure for AI agents together.

## How to Contribute

### 1. Report Bugs

Found a bug? [Open an issue](https://github.com/bensargotest-sys/trustscore/issues/new) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Node version, etc.)
- Relevant logs or error messages

### 2. Suggest Features

Have an idea? [Open an issue](https://github.com/bensargotest-sys/trustscore/issues/new) with:
- Use case description
- Proposed solution
- Why it would be valuable
- Any alternative approaches you've considered

### 3. Submit Pull Requests

Ready to code? Follow these steps:

#### Setup Development Environment

```bash
# Fork the repo on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/trustscore.git
cd trustscore

# Install dependencies
npm install

# Run tests to verify setup
npm test

# Start development server
npm run dev
```

#### Development Workflow

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes:**
   - Write code following our style guide (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes:**
   ```bash
   # Run all tests
   npm test
   
   # Run specific test
   npm test -- --testPathPattern=algorithm
   
   # Run E2E tests
   npm run test:e2e
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new trust dimension for response time variance"
   ```
   
   Use [Conventional Commits](https://www.conventionalcommits.org/) format:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test updates
   - `refactor:` - Code refactoring
   - `perf:` - Performance improvements
   - `chore:` - Maintenance tasks

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request:**
   - Go to the [TrustScore repo](https://github.com/bensargotest-sys/trustscore)
   - Click "New Pull Request"
   - Select your branch
   - Fill out the PR template
   - Submit!

#### Pull Request Guidelines

**Required:**
- ✅ All tests pass
- ✅ New tests added for new functionality
- ✅ Documentation updated
- ✅ Commit messages follow Conventional Commits
- ✅ Code follows style guide (runs `npm run lint`)

**Encouraged:**
- 📝 Clear PR description
- 🔗 Link to related issue
- 📸 Screenshots (if UI changes)
- 🧪 Example usage in PR description

## Code Style Guide

### TypeScript

```typescript
// Use interfaces for public APIs
interface TrustScore {
  score: number;
  confidence: number;
  components: ComponentScores;
}

// Use descriptive variable names
const compositeScore = calculateCompositeScore(dimensions);

// Document complex logic
/**
 * Calculates weighted composite trust score
 * using exponential decay for historical data.
 */
function calculateCompositeScore(dimensions: Dimensions): number {
  // Implementation...
}

// Use async/await over callbacks
async function checkTrust(providerId: string): Promise<TrustScore> {
  const data = await db.query(providerId);
  return calculateScore(data);
}
```

### File Organization

```
src/
├── scoring/          # Core scoring logic
│   ├── algorithm.ts  # Main scoring algorithm
│   ├── dimensions.ts # Individual dimension calculations
│   └── weights.ts    # Dimension weights
├── db/               # Database layer
│   ├── schema.ts     # Database schema
│   └── queries.ts    # Database queries
├── mcp/              # MCP server implementation
│   ├── tools.ts      # MCP tool handlers
│   └── server.ts     # Server setup
└── utils/            # Utility functions
```

### Testing

```typescript
// Unit tests: test individual functions
describe('calculateReliabilityScore', () => {
  it('should return 1.0 for 100% success rate', () => {
    const score = calculateReliabilityScore(100, 0);
    expect(score).toBe(1.0);
  });
  
  it('should decay with failures', () => {
    const score = calculateReliabilityScore(80, 20);
    expect(score).toBeLessThan(1.0);
  });
});

// E2E tests: test full workflows
describe('TrustScore E2E', () => {
  it('should update trust score after reporting outcome', async () => {
    const initial = await checkTrust('test_provider');
    await reportOutcome('test_provider', { success: false });
    const updated = await checkTrust('test_provider');
    
    expect(updated.score).toBeLessThan(initial.score);
  });
});
```

## Architecture Overview

### Scoring Algorithm

TrustScore uses a 7-dimension weighted composite scoring system:

1. **Reliability** (25%) - Success rate vs. failures
2. **Uptime** (20%) - Availability percentage
3. **Latency** (15%) - Response time consistency
4. **Error Rate** (15%) - Frequency of errors
5. **Quality** (10%) - Output quality metrics
6. **Data Freshness** (10%) - Recency of data
7. **Security** (5%) - Security incident history

Each dimension is scored 0-1, then weighted to produce a composite score.

### Confidence Tracking

Confidence level indicates how reliable the trust score is:
- **High confidence (0.8-1.0):** 100+ interactions
- **Medium confidence (0.5-0.8):** 20-100 interactions
- **Low confidence (0-0.5):** <20 interactions

### Database Schema

```sql
-- Providers table
CREATE TABLE providers (
  id TEXT PRIMARY KEY,
  name TEXT,
  category TEXT,
  created_at INTEGER
);

-- Interactions table
CREATE TABLE interactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  provider_id TEXT,
  success INTEGER,
  latency_ms REAL,
  error_message TEXT,
  timestamp INTEGER,
  FOREIGN KEY (provider_id) REFERENCES providers(id)
);
```

## Areas Needing Contribution

### High Priority

1. **Additional Trust Dimensions**
   - Cost efficiency ($/request)
   - Rate limit handling
   - Data consistency (for databases)
   - Geographic availability

2. **Performance Optimization**
   - Query optimization for large datasets
   - Caching layer for frequently accessed scores
   - Background score calculation

3. **Integration Examples**
   - AutoGen integration
   - LlamaIndex integration
   - Semantic Kernel integration

### Medium Priority

4. **Visualization Dashboard**
   - Web UI for viewing trust scores
   - Historical trends
   - Provider comparison

5. **Advanced Analytics**
   - Anomaly detection
   - Predictive scoring
   - Correlation analysis

6. **Export/Import**
   - Export trust scores to CSV/JSON
   - Import historical data
   - Backup/restore utilities

### Low Priority (Nice to Have)

7. **Additional Database Backends**
   - PostgreSQL support
   - MySQL support
   - MongoDB support

8. **Monitoring Integration**
   - Prometheus metrics
   - Grafana dashboards
   - Alert system

## Testing Guidelines

### Unit Tests

- Test individual functions in isolation
- Mock external dependencies
- Aim for >90% code coverage

```bash
npm test
npm run test:coverage
```

### Integration Tests

- Test component interactions
- Use real database (test.db)
- Verify end-to-end workflows

```bash
npm run test:integration
```

### E2E Tests

- Test full MCP server workflows
- Simulate real agent interactions
- Verify tool calls work correctly

```bash
npm run test:e2e
```

### Performance Tests

- Benchmark scoring algorithms
- Test with large datasets (10k+ interactions)
- Verify acceptable response times

```bash
npm run test:perf
```

## Documentation

### Code Comments

- Document "why" not "what"
- Explain complex algorithms
- Add TSDoc for public APIs

### README Updates

Update README.md when adding:
- New features
- Configuration options
- CLI commands
- Environment variables

### Example Code

Provide working examples for:
- New features
- Integration patterns
- Advanced use cases

## Release Process

(For maintainers)

1. **Version bump:**
   ```bash
   npm version patch|minor|major
   ```

2. **Update CHANGELOG.md:**
   - List all changes since last release
   - Group by type (features, fixes, breaking)
   - Credit contributors

3. **Tag release:**
   ```bash
   git tag -a v0.2.0 -m "Release v0.2.0"
   git push origin v0.2.0
   ```

4. **GitHub Release:**
   - Create release on GitHub
   - Attach built artifacts
   - Copy CHANGELOG entry

5. **Announce:**
   - Discord (#mcp-servers)
   - X (Twitter)
   - MCP Registry update

## Questions?

- Open an issue for clarification
- Join the [MCP Discord](https://discord.com/invite/mcp) (#trustscore channel)
- Email: [your-email] (if provided)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to TrustScore!** 🎉

Every contribution, no matter how small, helps build better infrastructure for AI agents.
