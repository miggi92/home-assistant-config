import { defineConfig, type DefaultTheme } from "vitepress";

export const de = defineConfig({
	title: "Home assistant Konfiguration",
	description: "Meine Home Assistant Konfiguration",
	lang: "de",
	head: [["meta", { property: "og:locale", content: "de" }]],
	themeConfig: {
		nav: nav(),
		sidebar: {
			"/de/config/": { base: "/de/config/", items: sidebarConfig() },
			"/de/featured/": { base: "/de/featured/", items: sidebarFeatured() },
		},
	},
});

function nav(): DefaultTheme.NavItem[] {
	return [
		{ text: "Startseite", link: "/de/" },
		{ text: "Konfiguration", link: "/de/config", activeMatch: "/de/config/" },
		{ text: "Featured", link: "/de/featured", activeMatch: "/de/featured/" },
	];
}

function sidebarConfig(): DefaultTheme.SidebarItem[] {
	return [{
		text: "Konfiguration",
		link: "/",
		items: [
			{
				text: "Automationen",
				link: "/",
				base: "/de/config/automations/"
			}
		]
	}, {
		text: "Integrations",
		link: "/",
		base: "/de/config/integrations/",
	}];
}

function sidebarFeatured(): DefaultTheme.SidebarItem[] {
	return [
		{
			text: "Featured",
			link: "/featured/",
		},
	];
}
