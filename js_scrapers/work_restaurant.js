export default async ({ page }) => {
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
