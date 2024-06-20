import { defineConfig, type DefaultTheme } from "vitepress";

export const en = defineConfig({
	title: "Home assistant config",
	description: "A home assistant config of my home.",
	lang: "en-US",
	head: [["meta", { property: "og:locale", content: "en" }]],
	themeConfig: {
		nav: nav(),
		sidebar: {
			"/config/": { base: "/config/", items: sidebarConfig() },
			"/featured/": { base: "/config/", items: sidebarFeatured() },
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
					link: "/",
					base: "/config/automations/",
					items: [
						{
							text: "Notifications",
							link: "/",
							base: "/config/automations/notifications/",
							collapsed: true,
							items: [{ text: "Calls", link: "call" }],
						},
					],
				},
				{
					text: "Integrations",
					link: "/",
					base: "/config/integrations/",
					items: [
						{ text: "Waste", link: "waste" },
						{ text: "Food warnings", link: "food_warnings" },
						{
							text: "MQTT",
							link: "/",
							base: "/config/integrations/mqtt/",
							items: [
								{
									text: "HASS Agent",
									link: "hassagent",
								},
							],
						},
					],
				},
				{
					text: "Lovelace",
					link: "/",
					base: "/config/lovelace/",
					items: [
						{ text: "Birthdays", link: "birthdays" },
						{ text: "Vacations", link: "vacations" },
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
