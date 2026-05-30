# KeyERP Upstream Pins

Record the upstream ERPNext commit SHA at each build. Update before running `bench build`.

| Date | ERPNext SHA | Notes |
|---|---|---|
| 2026-05-30 | 3b44419a7f1e732b4f5ba0961dedf0076fc98ee9 | Initial KeyERP scaffold |

## Re-run procedure (automatable upgrade loop)

```bash
# 1. Pull latest upstream
git pull origin develop

# 2. Record new SHA here
git rev-parse HEAD   # paste result in the table above

# 3. Build and migrate — override layer re-applies automatically
bench build
bench migrate

# 4. Verify sidebar selector still matches
grep -n "body-sidebar-container" $(pip show frappe | grep Location | cut -d' ' -f2)/frappe/public/scss/desk/sidebar.scss
# If the class name changed, update keyerp/keyerp/public/scss/keyerp.bundle.scss accordingly.

# 5. Run acceptance criteria
# See Phase 8 in the implementation plan.

# 6. Apply any entries in keyerp/keyerp/patches/CHANGELOG.md
# Halt on conflict — do not guess at resolutions.
```
