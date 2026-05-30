# KeyERP

KeyERP — Property of SKYRISE.

KeyERP is a proprietary SaaS ERP product by SKYRISE, built as a branded and
UX-refined layer on top of ERPNext v17. All KeyERP differentiation lives in
this custom Frappe app (`keyerp`), co-located in the ERPNext fork repository.
**Zero edits** are made to upstream ERPNext or Frappe source: the sidebar is
hidden via CSS, the top navigation is injected via JS/Vue, and branding is
applied through hooks and template overrides.

## Architecture overview

- **Top navigation** — a Vue 3 single-file component (`KeyERPNav.vue`) mounted
  into the desk on the `app_ready` event. The nav contents come from a manifest
  injected into `frappe.boot` by `boot.py`.
- **Nav manifest** — stored as data in two custom DocTypes,
  `KeyERP Nav Section` and its child `KeyERP Nav Item`. Seeded via fixtures.
- **Profiles** — the active profile (`distribution` or `manufacturing`) is
  derived from the active ERPNext Domains. Manufacturing is Distribution plus an
  overlay/delta (the additional "Make" section and manufacturing-only items).
- **Workspaces** — KeyERP-branded Workspace fixtures, one per nav section, with
  Manufacturing variants restricted by `restrict_to_domain`.
- **Branding** — driven through the Website Settings fixture (`app_name`,
  `app_logo`, `favicon`, `footer_powered`) plus the `app_logo_url` hook, so the
  stock login and desk render KeyERP branding with no fragile template override.

## Installation (live bench)

```bash
cd ~/frappe-bench
pip install -e /path/to/KeyERPFork/keyerp
bench install-app keyerp
bench migrate
bench build --app keyerp
```

## Security boundary

> KeyERP profiles control which navigation sections and workspaces are
> **visible**. They do **NOT** grant or restrict database-level access. Any
> access control requirement must be enforced through ERPNext roles and
> permissions. A user whose profile shows the "Make" section can still only
> create Work Orders if they hold the Manufacturing User or Manufacturing
> Manager role. Profile switching is presentation-only and reversible; it never
> touches data.

## Upgrade loop

See `UPSTREAM_PINS.md` at the repository root for the pinned upstream SHAs and
the re-build / re-validate procedure. The CSS selector used to hide the Frappe
sidebar (`.body-sidebar-container`) is upgrade-sensitive and must be re-verified
against the installed Frappe version at each upgrade.
