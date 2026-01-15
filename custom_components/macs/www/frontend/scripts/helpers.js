/**
 * Frontend Helpers
 * ----------------
 * Shared utility helpers for the frontend runtime.
 */

export const QUERY_PARAMS = typeof location !== "undefined" ? new URLSearchParams(location.search) : new URLSearchParams();

let defaultsByKey = {};
let weatherConditionKeys = [];
let defaultsLoadPromise = null;


// Loads shared default constants from /macs/shared/constants.json.
// The result is cached so the file is only fetched once.
export const loadSharedConstants = () => {
	// If a load is already in progress or has completed, return the existing promise to avoid duplicate fetches.
	if (defaultsLoadPromise) return defaultsLoadPromise;

	// Create and store the promise so subsequent calls reuse it.
	defaultsLoadPromise = (async () => {
		try {
			// Fetch the JSON file, disabling cache to ensure fresh data.
			const baseUrl = new URL("/macs/shared/constants.json", window.location.origin);
			const response = await fetch(baseUrl.toString(), { cache: "no-store" });
			let data = response && response.ok ? await response.json() : null;
			if (!data) {
				try {
					const fallbackUrl = new URL("shared/constants.json", window.location.href);
					const fallbackResponse = await fetch(fallbackUrl.toString(), { cache: "no-store" });
					data = fallbackResponse && fallbackResponse.ok ? await fallbackResponse.json() : null;
				} catch (_) {
					data = null;
				}
			}

			// Extract the "defaults" array
			const defaults = data && typeof data === "object" ? data.defaults : null;

			// Only proceed if defaults is a valid array.
			if (Array.isArray(defaults)) {

				// Reset the defaults lookup object.
				defaultsByKey = {};

				// Reset the list of weather-related default keys.
				weatherConditionKeys = [];

				// Iterate over each entry in the defaults array.
				defaults.forEach((entry) => {

					// Skip invalid or non-object entries.
					if (!entry || typeof entry !== "object") return;

					// Extract the key for this default entry.
					const key = entry.key;

					// Store the default value indexed by its key.
					defaultsByKey[key] = entry.default;

					// If the entry references a weather condition entity, track its key separately for weather-related logic.
					if (
						typeof entry.entity === "string" &&
						entry.entity.startsWith("weather_conditions_")
					) {
						weatherConditionKeys.push(key);
					}
				});
			}
		} catch (_) {
			// Swallow errors
		}
	})();

	// Return the promise 
	return defaultsLoadPromise;
};


// Returns the value of a URL query parameter if present, otherwise falls back to a default value defined in defaultsByKey.
export const getQueryParamOrDefault = (param) => {
	// return the query param if present
	const value = QUERY_PARAMS.get(param);
	if (value !== null) return value;

	// otherwise use the default value
	const fallback = Object.prototype.hasOwnProperty.call(defaultsByKey, param) ? defaultsByKey[param] : undefined;
	if (fallback === null || typeof fallback === "undefined") return "";
	if (typeof fallback === "boolean") return fallback ? "true" : "false";
	return String(fallback);
};

export const getWeatherConditionKeys = () => weatherConditionKeys.slice();
