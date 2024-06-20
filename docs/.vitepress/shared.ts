import { defineConfig } from "vitepress";

export const shared = defineConfig({
	base: "/home-assistant-config",
	lastUpdated: true,
	cleanUrls: true,
	metaChunk: true,
	head: [
		["link", { rel: "icon", href: "/home-assistant-config/favicon.ico" }],
		[
			"meta",
			{
				property: "og:url",
				content: "https://miggi92.github.io/home-assistant-config/",
			},
		],
		[
			"meta",
			{
				property: "twitter:url",
				content: "https://miggi92.github.io/home-assistant-config/",
			},
		],
		["meta", { property: "og:type", content: "website" }],
		[
			"meta",
			{ property: "og:image", content: "/home-assistant-config/logo_transparent.png" },
		],
		[
			"meta",
			{
				property: "twitter:image",
				content: "/home-assistant-config/logo_transparent.png",
			},
		],
		["meta", { property: "og:site_name", content: "Miggi92 Home assistant config" }],
		["meta", { property: "twitter:card", content: "summary_large_image" }],
		["meta", { property: "twitter:domain", content: "miggi92.github.io" }],
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
		search: {
			provider: "local",
		},
		externalLinkIcon: true,
		logo: "/logo_transparent.png",
		outline: [2, 6],
		socialLinks: [
			{ icon: "github", link: "https://github.com/miggi92/home-assistant-config" },
		],
	},
});
