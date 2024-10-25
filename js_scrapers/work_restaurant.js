export default async ({ page }) => {
	// Do Something with the page and return!
	// The editor will detect the return value, and either download
	// a JSON/PDF/PNG or Plain-text file. If you don't return
	// anything then nothing will happen.
	const url = hass.states["input_text.work_meal_plan_url"].state;
	await page.goto(url);

	await Promise.all([
		// Wait for navigation to complete
	]);

	await page.waitForSelector("app-category:nth-child(1)", {
		visible: true,
	});

	const html = await page.content();

	return html;
};
