---
---

# Work meals

The meals of the work restaurant are scraped with the multiscrape integration.
Unfortunally the data of the website is loaded dynamically.

Thanks to [@danieldotnl](https://github.com/danieldotnl) I found a solution for this.
He mentioned following thread:
[[GUIDE] Scraping dynamic websites with browserless + multiscrape. v2 update](https://community.home-assistant.io/t/guide-scraping-dynamic-websites-with-browserless-multiscrape-v2-update)

## Scraping with browserless

### Steps I've done

- Installed the browserless addon
- added a input_text helper to read out the url from the secrets file
- added the js file

```js
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
```

- added the folder `browserless` to the `www` folder.
