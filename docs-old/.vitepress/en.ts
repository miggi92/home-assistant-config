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
			link: "/",
			items: [
				{
					text: "Automations",
					link: "/",
					base: "/config/automations/",
					collapsed: true,
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
					collapsed: true,
					items: [
						{ text: "Waste", link: "waste" },
						{ text: "Food warnings", link: "food_warnings" },
						{ text: "Work meals", link: "work_meals" },
						{ text: "Plants", link: "plants" },
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
					collapsed: true,
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
