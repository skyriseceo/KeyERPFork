<template>
	<nav class="keyerp-section-nav" role="navigation" aria-label="Main Navigation">
		<ul class="keyerp-nav-list">
			<li
				v-for="section in sections"
				:key="section.section_id"
				class="keyerp-nav-item"
				:class="{ active: activeSection === section.section_id }"
				@mouseenter="openDropdown(section.section_id)"
				@mouseleave="closeDropdown"
			>
				<a class="keyerp-nav-link" @click.prevent="navigateSection(section)">
					<span class="keyerp-nav-icon" v-if="section.icon">{{ section.icon }}</span>
					<span class="keyerp-nav-label">{{ section.label }}</span>
					<span class="keyerp-caret" v-if="section.items && section.items.length">▾</span>
				</a>
				<ul
					v-if="section.items && section.items.length && activeDropdown === section.section_id"
					class="keyerp-dropdown"
				>
					<li v-for="item in section.items" :key="item.link_to">
						<a class="keyerp-dropdown-item" @click.prevent="navigateItem(item)">
							{{ item.label }}
						</a>
					</li>
				</ul>
			</li>
		</ul>
	</nav>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";

export default {
	name: "KeyERPNav",
	setup() {
		const manifest = frappe.boot.keyerp_nav_manifest || { sections: [] };
		const sections = ref(manifest.sections || []);
		const activeSection = ref(null);
		const activeDropdown = ref(null);

		function navigateSection(section) {
			if (section.route) {
				frappe.set_route(section.route);
			} else if (section.items && section.items.length) {
				navigateItem(section.items[0]);
			}
			activeSection.value = section.section_id;
			activeDropdown.value = null;
		}

		function navigateItem(item) {
			switch (item.link_type) {
				case "DocType":
					frappe.set_route("List", item.link_to);
					break;
				case "Report":
					frappe.set_route("query-report", item.link_to);
					break;
				case "Page":
					frappe.set_route(item.link_to);
					break;
				case "Workspace":
					frappe.set_route("Workspaces", item.link_to);
					break;
				default:
					if (item.route) frappe.set_route(item.route);
			}
			activeDropdown.value = null;
		}

		function openDropdown(sectionId) {
			activeDropdown.value = sectionId;
		}

		function closeDropdown() {
			activeDropdown.value = null;
		}

		function syncActiveSection() {
			const route = frappe.get_route_str();
			// Map current route to a section (basic heuristic; extend as needed)
			const routeSectionMap = {
				"purchase-order": "buy",
				"purchase-receipt": "buy",
				"purchase-invoice": "buy",
				supplier: "buy",
				"sales-order": "sell",
				"sales-invoice": "sell",
				"delivery-note": "sell",
				customer: "sell",
				"stock-entry": "stock",
				item: "stock",
				"work-order": "make",
				"job-card": "make",
				bom: "make",
				"payment-entry": "money",
				"journal-entry": "money",
			};
			const doctype = route.split("/")[1]?.toLowerCase().replace(/ /g, "-");
			if (doctype && routeSectionMap[doctype]) {
				activeSection.value = routeSectionMap[doctype];
			}
		}

		onMounted(() => {
			$(document).on("page-change.keyerp-nav", syncActiveSection);
			syncActiveSection();
		});

		onUnmounted(() => {
			$(document).off("page-change.keyerp-nav");
		});

		return {
			sections,
			activeSection,
			activeDropdown,
			navigateSection,
			navigateItem,
			openDropdown,
			closeDropdown,
		};
	},
};
</script>
