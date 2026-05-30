import frappe


# Map active domain sets to KeyERP profile names.
# Manufacturing profile requires the Manufacturing domain to be active.
def _resolve_profile(active_domains: set) -> str:
	if "Manufacturing" in active_domains:
		return "manufacturing"
	return "distribution"  # default / fallback for Distribution or empty


def boot_session(bootinfo):
	"""
	Called by Frappe for every authenticated session boot.
	Source: frappe/boot.py — hooks["boot_session"] loop.
	bootinfo is a frappe._dict; attributes set here appear in frappe.boot on the client.
	"""
	if frappe.session.user == "Guest":
		return

	active_domains = set(frappe.get_active_domains())  # e.g. {"Distribution"} or {"Manufacturing"}
	profile = _resolve_profile(active_domains)

	bootinfo.keyerp_active_profile = profile
	bootinfo.keyerp_nav_manifest = _build_manifest(profile)


def _build_manifest(profile: str) -> dict:
	"""
	Build the nav manifest dict consumed by KeyERPNav.vue.
	Manufacturing is Distribution + overlay: fetch all "all" sections plus
	profile-specific sections, then merge overlay records into their base sections.
	"""
	# Base sections: apply to all profiles or the active one
	sections = frappe.get_all(
		"KeyERP Nav Section",
		filters={
			"profile": ["in", ["all", profile]],
			"disabled": 0,
			"is_overlay": 0,
		},
		fields=["name", "section_id", "label", "icon", "order", "route"],
		order_by="`order` asc",
	)

	# Overlay sections (manufacturing-only modifications to base sections)
	overlay_by_base = {}
	if profile == "manufacturing":
		overlays = frappe.get_all(
			"KeyERP Nav Section",
			filters={"is_overlay": 1, "profile": "manufacturing", "disabled": 0},
			fields=["name", "section_id", "base_section", "label", "icon", "order", "route"],
		)
		overlay_by_base = {o["base_section"]: o for o in overlays}

	result = []
	for section in sections:
		if section["name"] in overlay_by_base:
			# Manufacturing overlay: merge non-null overlay fields into base section
			ov = overlay_by_base[section["name"]]
			for field in ("label", "icon", "order", "route"):
				if ov.get(field):
					section[field] = ov[field]

		# Fetch nav items for this section (shared + profile-specific)
		items = frappe.get_all(
			"KeyERP Nav Item",
			filters={
				"parent": section["name"],
				"profile": ["in", ["all", profile]],
			},
			fields=["label", "link_type", "link_to", "order"],
			order_by="`order` asc",
		)
		section["items"] = items
		result.append(section)

	# Re-sort after overlay may have changed section.order
	result.sort(key=lambda s: s.get("order", 0))

	return {"profile": profile, "sections": result}
