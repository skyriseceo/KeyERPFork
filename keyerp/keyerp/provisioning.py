import frappe

PROFILE_DOMAINS = {
	"distribution": ["Distribution"],
	"manufacturing": ["Manufacturing"],  # Distribution remains active from initial provisioning
}


def setup_profile(profile_name: str):
	"""
	Activate the ERPNext domains for this profile and bust the domain cache.
	Call at: tenant provisioning, and from on_domain_settings_update.
	"""
	domains = PROFILE_DOMAINS.get(profile_name, ["Distribution"])
	_activate_domains(domains)
	frappe.cache.delete_key("active_domains")  # bust the Frappe domain cache


def _activate_domains(domains: list):
	"""Set Domain Settings.active_domains to the given list."""
	domain_settings = frappe.get_doc("Domain Settings", "Domain Settings")
	domain_settings.active_domains = []
	for domain_name in domains:
		domain_settings.append("active_domains", {"domain": domain_name})
	domain_settings.save(ignore_permissions=True)
	frappe.db.commit()


def on_domain_settings_update(doc, method=None):
	"""
	Called by the doc_events hook when Domain Settings is saved.
	Re-resolves the profile and emits a realtime event so the client can reload boot.
	"""
	active_domains = set(frappe.get_active_domains())
	profile = _resolve_profile(active_domains)
	# Guard: session.user may be absent in CLI / migration context.
	user = getattr(frappe.session, "user", None)
	if not user or user == "Guest":
		return
	frappe.publish_realtime("keyerp_profile_changed", {"profile": profile}, user=user)


def _resolve_profile(active_domains: set) -> str:
	if "Manufacturing" in active_domains:
		return "manufacturing"
	return "distribution"
