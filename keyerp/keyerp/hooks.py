app_name = "keyerp"
app_title = "KeyERP"
app_publisher = "SKYRISE"
app_description = "KeyERP — Property of SKYRISE"
app_email = "skyriseceo@gmail.com"
app_license = "Proprietary"

# ── Branding ──────────────────────────────────────────────────
# These values appear in the browser tab, login screen, navbar logo,
# and email footers. Zero edits are made to upstream source files.
app_logo_url = "/assets/keyerp/images/keyerp-logo.svg"

# ── Asset bundles ─────────────────────────────────────────────
# keyerp.bundle.js mounts the Vue top-nav and wires the realtime
# profile-change handler. keyerp.bundle.css hides Frappe's sidebar
# and styles the KeyERP section nav bar.
app_include_js = "keyerp.bundle.js"
app_include_css = "keyerp.bundle.css"

# ── Session boot ──────────────────────────────────────────────
# Injects keyerp_active_profile and keyerp_nav_manifest into frappe.boot.
boot_session = "keyerp.boot.boot_session"

# ── Doc events ────────────────────────────────────────────────
# Regenerate / notify when Domain Settings change so the active
# profile (and therefore the nav manifest) is refreshed client-side.
doc_events = {
    "Domain Settings": {
        "on_update": "keyerp.provisioning.on_domain_settings_update",
    }
}

# ── Fixtures ──────────────────────────────────────────────────
# Exported and re-imported on `bench migrate`.
fixtures = [
    "KeyERP Nav Section",
    {"dt": "Workspace", "filters": [["app", "=", "keyerp"]]},
    {"dt": "Website Settings", "filters": []},
]
