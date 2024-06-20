import { defineConfig, type DefaultTheme } from "vitepress";

export const de = defineConfig({
	title: "Home assistant Konfiguration",
	description: "Meine Home Assistant Konfiguration",
	lang: "de",
	head: [["meta", { property: "og:locale", content: "de" }]],
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
		{ text: "Startseite", link: "/" },
		{ text: "Konfiguration", link: "/config", activeMatch: "/config/" },
		{ text: "Featured", link: "/featured", activeMatch: "/featured/" },
	];
}

function sidebarConfig(): DefaultTheme.SidebarItem[] {
	return [];
}

function sidebarFeatured(): DefaultTheme.SidebarItem[] {
	return [
		{
			text: "Featured",
			link: "/featured/",
		},
	];
}
