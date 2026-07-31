import asyncio
from datetime import timedelta
import json
import logging

import requests

from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .const import (
    BASE_API_URL,
    DOMAIN,
    INITIAL_FALLBACK_SUMMARY,
    INITIAL_FALLBACK_TICKETS,
    STORAGE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

SUMMARY_KEYS = tuple(f"numero{index}" for index in range(1, 14))


class ElGordoCoordinator(DataUpdateCoordinator):
    """Class to manage fetching El Gordo data."""

    def __init__(self, hass, entry):
        """Initialize."""
        self.entry = entry
        self._store = Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry.entry_id}")
        self._fallback_summary = INITIAL_FALLBACK_SUMMARY.copy()
        super().__init__(
            hass,
            _LOGGER,
            name="El Gordo",
            update_interval=timedelta(minutes=30),
        )

    async def async_load_stored_summary(self):
        """Load the most recent complete draw summary from storage."""
        stored_summary = await self._store.async_load()
        if self._has_current_summary(stored_summary) and isinstance(
            stored_summary.get("draw_year"), int
        ):
            self._fallback_summary = {
                **stored_summary,
                "data_source": "stored_results",
            }

    def _fetch_data(self, url):
        """Fetch data and strip any JavaScript-style prefixes to get pure JSON."""
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        text = response.text

        start_index = text.find("{")
        if start_index == -1:
            raise ValueError("API response does not contain JSON")

        return json.loads(text[start_index:])

    @staticmethod
    def _has_current_summary(summary):
        """Return whether the API response contains a complete draw summary."""
        return isinstance(summary, dict) and all(
            summary.get(key) for key in SUMMARY_KEYS
        )

    async def _async_update_data(self):
        tickets_str = self.entry.options.get(
            "tickets", self.entry.data.get("tickets", "")
        )
        tickets = [t.strip() for t in tickets_str.split(",") if t.strip()]

        try:
            async with asyncio.timeout(15):
                results = {"tickets": {}, "summary": {}}

                summary_url = f"{BASE_API_URL}?n=resumen"
                summary = await self.hass.async_add_executor_job(
                    self._fetch_data, summary_url
                )

                if not self._has_current_summary(summary):
                    results["summary"] = self._fallback_summary.copy()
                    if self._fallback_summary.get("draw_year") == 2025:
                        results["tickets"] = {
                            ticket: INITIAL_FALLBACK_TICKETS[ticket].copy()
                            for ticket in tickets
                            if ticket in INITIAL_FALLBACK_TICKETS
                        }
                    return results

                current_summary = {
                    **summary,
                    "data_source": "live_api",
                    "draw_year": dt_util.now().year,
                }
                results["summary"] = current_summary
                self._fallback_summary = {
                    **current_summary,
                    "data_source": "stored_results",
                }
                await self._store.async_save(self._fallback_summary)

                for ticket in tickets:
                    ticket_url = f"{BASE_API_URL}?n={ticket}"
                    ticket_data = await self.hass.async_add_executor_job(
                        self._fetch_data, ticket_url
                    )
                    if not isinstance(ticket_data, dict) or "premio" not in ticket_data:
                        raise ValueError(
                            f"API returned no prize data for ticket {ticket}"
                        )
                    results["tickets"][ticket] = ticket_data

                return results
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
