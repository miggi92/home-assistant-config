import { defineConfig, type DefaultTheme } from "vitepress";

export const en = defineConfig({
	title: "Home assistant config",
	description: "A home assistant config of my home.",
	lang: "en-US",
	base: "/home-assistant-config",
	head: [["meta", { property: "og:locale", content: "en" }]],
	themeConfig: {
		nav: nav(),
		sidebar: {
			"/config/": { base: "/config/", items: sidebarConfig() },
			"/featured/": { base: "/featured/", items: sidebarFeatured() },
		},
	},
});
function nav(): DefaultTheme.NavItem[] {
	return [
		{ text: "Home", link: "/" },
		{ text: "Config", link: "/config", activeMatch: "/config/" },
		{ text: "Featured", link: "/featured", activeMatch: "/featured/" },
	];
}
function sidebarConfig(): DefaultTheme.SidebarItem[] {
	return [
		{
			text: "Config",
			items: [
				{
					text: "Automations",
					link: "automations",
					base: "/automations/",
					items: [
						{
							text: "Notifications",
							link: "notifications/",
							base: "/notifications/",
							collapsed: true,
							items: [{ text: "Calls", link: "call" }],
						},
					],
				},
				{
					text: "Integrations",
					link: "integrations",
					items: [
						{ text: "Waste", link: "integrations/waste" },
						{ text: "Food warnings", link: "integrations/food_warnings" },
						{
							text: "MQTT",
							link: "integrations/mqtt",
							items: [
								{
									text: "HASS Agent",
									link: "integrations/mqtt/hassagent",
								},
							],
						},
					],
				},
				{
					text: "Lovelace",
					link: "lovelace/",
					items: [
						{ text: "Birthdays", link: "lovelace/birthdays" },
						{ text: "Vacations", link: "lovelace/vacations" },
					],
				},
			],
		},
	];
}

function sidebarFeatured(): DefaultTheme.SidebarItem[] {
	return [
		{
			text: "Featured",
			link: "/featured/",
		},
	];
}
