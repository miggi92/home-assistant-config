import { defineConfig, type DefaultTheme } from "vitepress";

export const en = defineConfig({
	title: "Home assistant config",
	description: "A home assistant config of my home.",
	lang: "en-US",
	head: [["meta", { property: "og:locale", content: "en" }]],
	themeConfig: {
		nav: nav(),
		sidebar: {
			"/config/": sidebarConfig(),
			"/featured/": sidebarFeatured(),
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
					base: "/config/automations/",
					items: [
						{
							text: "Notifications",
							link: "notifications/",
							base: "/config/automations/notifications/",
							collapsed: true,
							items: [{ text: "Calls", link: "/config/automations/notifications/call" }],
						},
					],
				},
				{
					text: "Integrations",
					link: "integrations",
					items: [
						{ text: "Waste", link: "/config/integrations/waste" },
						{ text: "Food warnings", link: "/config/integrations/food_warnings" },
						{
							text: "MQTT",
							link: "/config/integrations/mqtt",
							items: [
								{
									text: "HASS Agent",
									link: "/config/integrations/mqtt/hassagent",
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
