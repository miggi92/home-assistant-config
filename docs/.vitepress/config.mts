import { defineConfig } from "vitepress";

// https://vitepress.dev/reference/site-config
export default defineConfig({
	title: "Home assistant config",
	description: "A home assistant config of my home.",
	base: "/home-assistant-config",
	lang: "en-US",
	lastUpdated: true,
	head: [
		["link", { rel: "icon", href: "/favicon.ico" }],
		["meta", { property: "og:type", content: "website" }],
		["meta", { property: "og:locale", content: "en" }],
		["meta", { property: "og:site_name", content: "Miggi92 Home assistant config" }],
		[
			"meta",
			{
				property: "og:url",
				content: "https://miggi92.github.io/home-assistant-config/",
			},
		],
	],
	sitemap: {
		hostname: "https://miggi92.github.io/home-assistant-config/",
	},
	markdown: {
		image: {
			lazyLoading: true,
		},
	},
	themeConfig: {
		// https://vitepress.dev/reference/default-theme-config
		nav: [
			{ text: "Home", link: "/" },
			{ text: "Config", link: "/config", activeMatch: "/config/" },
			{ text: "Featured", link: "/featured", activeMatch: "/featured/" },
		],
		search: {
			provider: 'local'
		},
		externalLinkIcon: true,
		logo: "/logo_transparent.png",
		outline: [2, 6],
		lastUpdated: {
			text: "Updated at",
			formatOptions: {
				dateStyle: "full",
				timeStyle: "medium",
			},
		},
		sidebar: {
			'/config/': [
				{
					text: "Config", link: "/config/",
				items: [
					{ text: "Automations", link: "/config/automations", items: [
						{ text: "Notifications", link: "/config/automations/notifications/", collapsed: true,
						items: [
							{ text: "Calls", link: "/config/automations/notifications/call"}
					]}
					]  },
					{ text: "Integrations", link: "/config/integrations", items: [
						{ text: "Waste", link: "/config/integrations/waste" }
					] },
					{
						text: "Lovelace",
						link: "/config/lovelace/",
						items: [{ text: "Birthdays", link: "/config/lovelace/birthdays" },
						{ text: "Vacations", link: "/config/lovelace/vacations" }],
					},
				],
				}
			],
			'/featured/': [{
				text: "Featured", link: "/featured/",
			}],
		},
		socialLinks: [
			{ icon: "github", link: "https://github.com/miggi92/home-assistant-config" },
		],
	},
	locales: {
		root: {
			label: "English",
			lang: "en",
		},
	},
});
