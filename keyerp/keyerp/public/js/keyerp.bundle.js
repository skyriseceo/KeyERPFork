import { createApp } from "vue";
import KeyERPNav from "./nav/KeyERPNav.vue";

const KEYERP_NAV_ID = "keyerp-section-nav";

function mountKeyERPNav() {
	if (document.getElementById(KEYERP_NAV_ID)) return;
	if (!frappe.boot.keyerp_nav_manifest) return;

	const header = document.querySelector(".main-section header");
	if (!header) return;

	const el = document.createElement("div");
	el.id = KEYERP_NAV_ID;
	header.insertAdjacentElement("afterend", el);

	createApp(KeyERPNav).mount(el);
}

// app_ready fires once after Frappe Desk initializes.
// Source: frappe/public/js/frappe/desk.js:60
$(document).on("app_ready", function () {
	mountKeyERPNav();

	// Register after app_ready so frappe.realtime is guaranteed to be initialized.
	frappe.realtime.on("keyerp_profile_changed", function ({ profile }) {
		frappe.show_alert({
			message: __("Profile changed to {0}. Refreshing...", [profile]),
			indicator: "blue",
		});
		setTimeout(() => window.location.reload(), 1500);
	});
});
