# Postmortem: .bashrc Non-Interactive Shell Trap

**Date Discovered**: 2026-02-05
**Severity**: High
**System Impact**: Cloud deployment, cron jobs
**Status**: Resolved

---

## Symptom

SSH non-interactive execution and cron jobs fail with "API key not found" errors despite environment variables being defined in `.bashrc`.

**Observable Behavior**:
```bash
# Interactive SSH works
$ ssh aliyun
$ echo $FMP_API_KEY
abc123...

# Non-interactive fails
$ ssh aliyun "echo $FMP_API_KEY"
<empty>

# Cron job logs
Error: FMP_API_KEY environment variable not set
```

---

## Root Cause

`.bashrc` contains an early exit guard for non-interactive shells:

```bash
# .bashrc line 1-2
[ -z "$PS1" ] && return
# All exports below this line are never reached in non-interactive mode
```

**Why This Exists**: `.bashrc` is for interactive shell customization (prompt, aliases, etc.). Bash intentionally skips it for non-interactive shells to avoid side effects.

**What We Did Wrong**: Stored deployment-critical environment variables (`FMP_API_KEY`, `HEPTABASE_API_TOKEN`) in `.bashrc` assuming they'd be available in all execution contexts.

---

## Impact Timeline

**2026-02-05 06:30** - First cron job failure (price data update)
**2026-02-05 07:00** - Discovered wrapper script sourcing `.bashrc` wasn't loading `FMP_API_KEY`
**2026-02-05 08:00** - Identified `.bashrc` early return as root cause
**2026-02-05 08:30** - Created standalone `.env` file, updated wrapper scripts
**2026-02-05 09:00** - Verified cron jobs working with new setup

---

## Solution

### Immediate Fix
1. Created `/root/workspace/Finance/.env` with all API keys:
   ```bash
   export FMP_API_KEY=abc123...
   export HEPTABASE_API_TOKEN=xyz789...
   ```

2. Updated wrapper scripts to source `.env` instead of `.bashrc`:
   ```bash
   # Old (broken)
   source ~/.bashrc

   # New (works)
   source /root/workspace/Finance/.env
   ```

3. Updated cron jobs to use absolute path to `.env`:
   ```cron
   30 6 * * 2-6 cd /root/workspace/Finance && source .env && .venv/bin/python scripts/update_data.py --price
   ```

### Configuration
- `.env` file location: `/root/workspace/Finance/.env`
- Permissions: `chmod 600 .env` (owner read-write only, contains secrets)
- `.gitignore`: Added `.env` to prevent secret leakage

---

## Prevention

### Rules
1. **Never store deployment-critical environment variables in `.bashrc`**
   - `.bashrc` is for interactive shell customization only
   - Non-interactive shells (SSH, cron, systemd) skip it

2. **Use standalone `.env` files for project environment variables**
   - One `.env` per project in project root
   - Explicit `source .env` in wrapper scripts
   - Absolute paths in cron jobs

3. **Test non-interactive execution before deploying**
   ```bash
   # Test command that should work
   ssh server "cd /path/to/project && source .env && echo \$API_KEY"
   ```

### Checklist for New Deployments
- [ ] Create `.env` file with all required environment variables
- [ ] Set `.env` permissions to `600` (owner only)
- [ ] Add `.env` to `.gitignore`
- [ ] Update wrapper scripts to `source .env`
- [ ] Test with `ssh server "command"` (non-interactive)
- [ ] Verify cron jobs can access environment variables

---

## Related Issues

- **SSH Config**: Different issue (VPN DNS hijacking) required SSH over port 443, but unrelated to environment variables
- **Systemd Services**: Would have same problem; always use `EnvironmentFile=` directive with standalone `.env`

---

## Lessons Learned

1. **Shell Execution Modes Matter**
   - Interactive vs. non-interactive shells have different startup files
   - `.bash_profile` / `.profile` → Login shells
   - `.bashrc` → Interactive non-login shells
   - Cron/SSH non-interactive → **NONE** (must explicitly source)

2. **Environment Variables Are Not Global**
   - Exporting in one file doesn't make them available everywhere
   - Each execution context needs explicit sourcing

3. **Test Deployment Scenarios Locally First**
   - `ssh server "command"` simulates cron environment
   - Catches sourcing issues before they break production

---

## References

- Bash Startup Files: https://www.gnu.org/software/bash/manual/html_node/Bash-Startup-Files.html
- Cron Environment: https://man7.org/linux/man-pages/man5/crontab.5.html
- Project `.env` location: `/root/workspace/Finance/.env`

---

**Author**: Claude (documentation-specialist)
**Reviewed**: 2026-02-08
**Next Review**: When deploying to new environments
