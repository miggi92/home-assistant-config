import { defineConfig } from "vitepress";
import { shared } from "./shared";
import { en } from "./en";
import { de } from "./de";

// https://vitepress.dev/reference/site-config
export default defineConfig({
	...shared,
	locales: {
		root: {
			label: "English",
			...en,
		},
		de: {
			label: "Deutsch",
			...de,
		},
	},
});
