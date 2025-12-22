import asyncio
from datetime import timedelta
import logging
import requests
import json

from .const import DOMAIN, BASE_API_URL
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

class ElGordoCoordinator(DataUpdateCoordinator):
    """Class to manage fetching El Gordo data."""

    def __init__(self, hass, entry):
        """Initialize."""
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name="El Gordo",
            update_interval=timedelta(minutes=30),
        )

    def _fetch_data(self, url):
        """Fetch data and strip any JavaScript-style prefixes to get pure JSON."""
        response = requests.get(url, timeout=15)
        text = response.text
        
        start_index = text.find('{')
        if start_index != -1:
            clean_json = text[start_index:]
            import json
            return json.loads(clean_json)
        
        return None

    async def _async_update_data(self):
        # Tickets aus Optionen oder Daten laden
        tickets_str = self.entry.options.get("tickets", self.entry.data.get("tickets", ""))
        tickets = [t.strip() for t in tickets_str.split(",") if t.strip()]
        
        try:
            async with asyncio.timeout(15): # Natives Timeout
                results = {"tickets": {}, "summary": {}}
                
                # Zusammenfassung laden
                summary_url = f"{BASE_API_URL}?n=resumen"
                results["summary"] = await self.hass.async_add_executor_job(self._fetch_data, summary_url)
                
                # Alle Tickets laden
                for ticket in tickets:
                    ticket_url = f"{BASE_API_URL}?n={ticket}"
                    results["tickets"][ticket] = await self.hass.async_add_executor_job(self._fetch_data, ticket_url)

                return results
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")