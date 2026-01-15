/**
 * Import Handler
 * -------
 * Single function which appends version to javascript imports
 */

export function importWithVersion(relativePath) {
	var baseUrl = import.meta.url;
	var url = new URL(relativePath, baseUrl);

	// window.__MACS_VERSION__ is set in the header script of macs.html
	if (typeof window !== "undefined" && window.__MACS_VERSION__) {
		url.searchParams.set("v", window.__MACS_VERSION__);
	}

	return import(url.toString());
}