# Postmortems — Finance Workspace

**Real incidents, root causes, and prevention strategies from building 未来资本 AI Trading Desk.**

---

## Purpose

Postmortems document actual problems encountered during development and deployment. Each postmortem follows a structured format to capture:
- **What went wrong** (symptom)
- **Why it happened** (root cause)
- **How we fixed it** (solution)
- **How to prevent it** (lessons learned)

Unlike generic "known issues" documentation, these are **real cases** with **real impact**.

---

## Postmortem Index

| Date | Title | Severity | Category |
|------|-------|----------|----------|
| 2026-02-05 | [.bashrc Non-Interactive Shell Trap](./2026-02-05-bashrc-env-variables.md) | High | Deployment |
| 2026-02-05 | [.gitignore Pattern Matching Trap](./2026-02-05-gitignore-pattern-trap.md) | Medium | Git Configuration |
| 2026-02-06 | [FMP Screener Returns ~976 (Not 3000+)](./2026-02-06-fmp-screener-limits.md) | Low | API Limitations |

---

## How to Use

### For Current Developers
- **Before deploying**: Read [.bashrc postmortem](./2026-02-05-bashrc-env-variables.md) to avoid environment variable traps
- **Before editing .gitignore**: Read [gitignore postmortem](./2026-02-05-gitignore-pattern-trap.md) to avoid tracking conflicts
- **Before expanding stock pool**: Read [FMP screener postmortem](./2026-02-06-fmp-screener-limits.md) to understand API limits

### For New Contributors
Start here before making changes:
1. Read all postmortems (15 min total)
2. Understand common traps in this workspace
3. Follow prevention checklists when making similar changes

### When Adding New Postmortems
Use the template structure:
1. **Symptom** — What we observed
2. **Root Cause** — Why it happened
3. **Impact Timeline** — When discovered, when resolved
4. **Solution** — What we did
5. **Prevention** — How to avoid in the future
6. **Lessons Learned** — Key takeaways

---

## Categories

### Deployment (1)
Issues related to cloud deployment, cron jobs, environment setup:
- [.bashrc Non-Interactive Shell Trap](./2026-02-05-bashrc-env-variables.md)

### Git Configuration (1)
Version control configuration traps:
- [.gitignore Pattern Matching Trap](./2026-02-05-gitignore-pattern-trap.md)

### API Limitations (1)
External API quirks and undocumented behaviors:
- [FMP Screener Returns ~976 (Not 3000+)](./2026-02-06-fmp-screener-limits.md)

---

## Prevention Checklist Reference

Quick links to prevention checklists:
- **Deploying to Cloud**: [.bashrc postmortem checklist](./2026-02-05-bashrc-env-variables.md#checklist-for-new-deployments)
- **Adding .gitignore Patterns**: [gitignore postmortem checklist](./2026-02-05-gitignore-pattern-trap.md#checklist-for-gitignore-patterns)
- **Expanding Stock Pool**: [FMP screener mitigation checklist](./2026-02-06-fmp-screener-limits.md#mitigation-checklist)

---

## Severity Levels

- **High**: System broken, deployment failed, data loss risk
- **Medium**: Feature blocked, workaround needed, time wasted
- **Low**: Confusing behavior, documentation gap, edge case

---

## Related Documentation

- **Known Traps** (quick reference): See CLAUDE.md "已知陷阱" section and MEMORY.md "Known Traps"
- **Architecture**: See [ARCHITECTURE.md](../ARCHITECTURE.md) for system design
- **API Reference**: See [terminal-api.md](../reference/terminal-api.md) for function documentation

---

Built with Claude Code by Anthropic.
