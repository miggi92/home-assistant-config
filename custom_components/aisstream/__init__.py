"""The aisstream.io integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_API_KEY, CONF_MMSI_FILTER, DOMAIN, SUBENTRY_TYPE_AREA
from .coordinator import AISStreamClient
from .geo import resolve_area_box

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.DEVICE_TRACKER, Platform.SENSOR]


def _collect_areas(hass: HomeAssistant, entry: ConfigEntry) -> tuple[list, list[str]]:
    """Merge every area subentry into one bounding-box list and MMSI list."""
    bounding_boxes: list = []
    mmsi_filter: set[str] = set()

    for subentry in entry.subentries.values():
        if subentry.subentry_type != SUBENTRY_TYPE_AREA:
            continue
        boxes = resolve_area_box(hass, subentry.data)
        if boxes is None:
            raise ConfigEntryNotReady(
                f"Area '{subentry.title}' references a zone that isn't"
                " available yet"
            )
        bounding_boxes.extend(boxes)
        mmsi_filter.update(subentry.data.get(CONF_MMSI_FILTER) or [])

    return bounding_boxes, sorted(mmsi_filter)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up aisstream.io from a config entry."""
    bounding_boxes, mmsi_filter = _collect_areas(hass, entry)

    client = AISStreamClient(
        hass=hass,
        entry_id=entry.entry_id,
        api_key=entry.data[CONF_API_KEY],
        bounding_boxes=bounding_boxes,
        mmsi_filter=mmsi_filter,
    )
    if bounding_boxes:
        client.start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its data, options or subentries change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        client: AISStreamClient = hass.data[DOMAIN].pop(entry.entry_id)
        await client.stop()
    return unload_ok
