<template>
	<nav
		class="keyerp-section-nav"
		:class="{ 'is-mobile-open': mobileOpen }"
		role="navigation"
		aria-label="KeyERP main navigation"
	>
		<!-- Mobile hamburger: reveals the section sheet on narrow viewports. -->
		<button
			class="keyerp-nav-toggle"
			type="button"
			:aria-expanded="mobileOpen ? 'true' : 'false'"
			aria-controls="keyerp-nav-list"
			:aria-label="mobileOpen ? __('Close navigation') : __('Open navigation')"
			@click="toggleMobile"
		>
			<svg class="icon" aria-hidden="true">
				<use :href="mobileOpen ? '#icon-x' : '#icon-menu'" />
			</svg>
		</button>

		<ul id="keyerp-nav-list" class="keyerp-nav-list">
			<li
				v-for="section in sections"
				:key="section.section_id"
				class="keyerp-nav-item"
				:class="{ active: activeSection === section.section_id, 'is-open': openSection === section.section_id }"
				@mouseenter="onSectionEnter(section)"
				@mouseleave="onSectionLeave"
				@focusout="onSectionFocusOut($event, section)"
			>
				<div class="keyerp-nav-trigger">
					<a
						class="keyerp-nav-link"
						href="#"
						:aria-current="activeSection === section.section_id ? 'page' : null"
						@click.prevent="navigateSection(section)"
					>
						<span v-if="iconHref(section.icon)" class="keyerp-nav-icon">
							<svg class="icon icon-sm" aria-hidden="true">
								<use :href="iconHref(section.icon)" />
							</svg>
						</span>
						<span class="keyerp-nav-label">{{ section.label }}</span>
					</a>

					<button
						v-if="hasItems(section)"
						class="keyerp-nav-caret"
						type="button"
						aria-haspopup="true"
						:aria-expanded="openSection === section.section_id ? 'true' : 'false'"
						:aria-controls="`keyerp-dd-${section.section_id}`"
						:aria-label="__('Toggle {0} menu', [section.label])"
						@click="toggleDropdown(section)"
						@keydown.escape="closeDropdownAndFocus(section)"
					>
						<svg class="icon" aria-hidden="true">
							<use href="#icon-chevron-down" />
						</svg>
					</button>
				</div>

				<transition name="keyerp-dd">
					<ul
						v-if="hasItems(section) && openSection === section.section_id"
						:id="`keyerp-dd-${section.section_id}`"
						class="keyerp-dropdown"
						@keydown.escape="closeDropdownAndFocus(section)"
					>
						<li v-for="item in section.items" :key="`${item.link_type}:${item.link_to}`">
							<a
								class="keyerp-dropdown-item"
								href="#"
								@click.prevent="navigateItem(section, item)"
							>
								{{ item.label }}
							</a>
						</li>
					</ul>
				</transition>
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
		const openSection = ref(null);
		const mobileOpen = ref(false);

		const mobileQuery = window.matchMedia("(max-width: 768px)");
		const isMobile = () => mobileQuery.matches;

		// Hover-close debounce so the cursor can travel from a trigger to its
		// menu across the 6px bridge without the menu snapping shut.
		let closeTimer = null;
		const cancelClose = () => {
			if (closeTimer) {
				clearTimeout(closeTimer);
				closeTimer = null;
			}
		};
		const scheduleClose = () => {
			cancelClose();
			closeTimer = setTimeout(() => (openSection.value = null), 150);
		};

		const iconHref = (name) => {
			// Manifest icons are Frappe sprite names (e.g. "house"); render via
			// the native #icon-<name> sprite loaded by app_include_icons.
			if (!name) return null;
			return `#icon-${name}`;
		};
		const hasItems = (section) => Array.isArray(section.items) && section.items.length > 0;

		function openDropdown(id) {
			cancelClose();
			openSection.value = id;
		}
		function toggleDropdown(section) {
			openSection.value = openSection.value === section.section_id ? null : section.section_id;
		}
		function closeDropdownAndFocus(section) {
			openSection.value = null;
			// Return focus to the section's caret for keyboard continuity. The
			// caret carries aria-controls and is always in the DOM (unlike the
			// dropdown, which v-if removes on close).
			const caret = document.querySelector(
				`.keyerp-nav-caret[aria-controls="keyerp-dd-${section.section_id}"]`
			);
			caret?.focus();
		}

		function onSectionEnter(section) {
			if (isMobile()) return; // touch/mobile uses explicit taps, not hover
			if (hasItems(section)) openDropdown(section.section_id);
		}
		function onSectionLeave() {
			if (isMobile()) return;
			scheduleClose();
		}
		function onSectionFocusOut(event, section) {
			// Close when keyboard focus leaves the whole section (e.g. Tab past
			// the last menu item).
			if (!event.currentTarget.contains(event.relatedTarget)) {
				if (openSection.value === section.section_id) openSection.value = null;
			}
		}

		function navigateSection(section) {
			if (section.route) {
				frappe.set_route(section.route);
			} else if (hasItems(section)) {
				navigateItem(section, section.items[0]);
				return;
			}
			activeSection.value = section.section_id;
			openSection.value = null;
			mobileOpen.value = false;
		}

		function navigateItem(section, item) {
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
			if (section) activeSection.value = section.section_id;
			openSection.value = null;
			mobileOpen.value = false;
		}

		function toggleMobile() {
			mobileOpen.value = !mobileOpen.value;
			openSection.value = null;
		}

		// Reset transient open-state when crossing the mobile/desktop breakpoint,
		// otherwise a menu opened in one mode is orphaned (invisible-but-open, or
		// open with no hamburger to close it) in the other.
		function onBreakpointChange() {
			openSection.value = null;
			mobileOpen.value = false;
			cancelClose();
		}

		// Close on outside click (covers click/touch-opened dropdowns and the
		// mobile sheet, which hover-leave can't catch).
		function onDocumentPointerDown(event) {
			const root = document.getElementById("keyerp-section-nav");
			if (root && !root.contains(event.target)) {
				openSection.value = null;
				mobileOpen.value = false;
			}
		}

		function syncActiveSection() {
			const route = frappe.get_route_str();
			const routeSectionMap = {
				// Buy
				"material-request": "buy",
				"purchase-order": "buy",
				"purchase-receipt": "buy",
				"purchase-invoice": "buy",
				supplier: "buy",
				"purchase-order-analysis": "buy",
				"purchase-register": "buy",
				// Sell
				quotation: "sell",
				"sales-order": "sell",
				"delivery-note": "sell",
				"sales-invoice": "sell",
				customer: "sell",
				"sales-order-analysis": "sell",
				"sales-register": "sell",
				// Make
				"work-order": "make",
				"job-card": "make",
				bom: "make",
				"production-plan": "make",
				"bom-stock-analysis": "make",
				"production-planning-report": "make",
				// Stock
				item: "stock",
				"stock-entry": "stock",
				"stock-balance": "stock",
				"stock-ledger": "stock",
				"stock-reconciliation": "stock",
				warehouse: "stock",
				// Money
				"payment-entry": "money",
				"journal-entry": "money",
				"bank-reconciliation-tool": "money",
				"accounts-receivable": "money",
				"accounts-payable": "money",
				"general-ledger": "money",
				// Workspace routes (e.g. "Workspaces/KeyERP Buy" → slug "keyerp-buy")
				"keyerp-home": "home",
				"keyerp-home-mfg": "home",
				"keyerp-buy": "buy",
				"keyerp-sell": "sell",
				"keyerp-make": "make",
				"keyerp-stock": "stock",
				"keyerp-money": "money",
				"keyerp-reports": "reports",
				"keyerp-settings": "settings",
			};
			const segment = route.split("/")[1]?.toLowerCase().replace(/ /g, "-");
			if (segment && routeSectionMap[segment]) {
				activeSection.value = routeSectionMap[segment];
			}
		}

		onMounted(() => {
			$(document).on("page-change.keyerp-nav", syncActiveSection);
			document.addEventListener("pointerdown", onDocumentPointerDown);
			mobileQuery.addEventListener("change", onBreakpointChange);
			syncActiveSection();
		});

		onUnmounted(() => {
			$(document).off("page-change.keyerp-nav");
			document.removeEventListener("pointerdown", onDocumentPointerDown);
			mobileQuery.removeEventListener("change", onBreakpointChange);
			cancelClose();
		});

		return {
			sections,
			activeSection,
			openSection,
			mobileOpen,
			iconHref,
			hasItems,
			toggleDropdown,
			closeDropdownAndFocus,
			onSectionEnter,
			onSectionLeave,
			onSectionFocusOut,
			navigateSection,
			navigateItem,
			toggleMobile,
		};
	},
};
</script>
