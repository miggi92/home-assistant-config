"""The aisstream.io integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_API_KEY,
    CONF_BOX_EAST,
    CONF_BOX_NORTH,
    CONF_BOX_SOUTH,
    CONF_BOX_WEST,
    CONF_LOCATION,
    CONF_MMSI_FILTER,
    CONF_ZONE,
    DOMAIN,
)
from .coordinator import AISStreamClient
from .geo import bounding_box_for_location, bounding_box_for_zone

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.DEVICE_TRACKER, Platform.SENSOR]


def _resolve_bounding_boxes(hass: HomeAssistant, data: dict) -> list:
    if zone_entity_id := data.get(CONF_ZONE):
        bounding_boxes = bounding_box_for_zone(hass, zone_entity_id)
        if bounding_boxes is None:
            raise ConfigEntryNotReady(
                f"Zone '{zone_entity_id}' is not available yet"
            )
        return bounding_boxes

    if location := data.get(CONF_LOCATION):
        bounding_boxes = bounding_box_for_location(location)
        if bounding_boxes is not None:
            return bounding_boxes
        _LOGGER.warning(
            "Stored location for this entry is invalid, falling back to the"
            " manual bounding box"
        )

    return [
        [
            [data[CONF_BOX_SOUTH], data[CONF_BOX_WEST]],
            [data[CONF_BOX_NORTH], data[CONF_BOX_EAST]],
        ]
    ]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up aisstream.io from a config entry."""
    data = entry.data
    bounding_boxes = _resolve_bounding_boxes(hass, data)

    client = AISStreamClient(
        hass=hass,
        entry_id=entry.entry_id,
        api_key=data[CONF_API_KEY],
        bounding_boxes=bounding_boxes,
        mmsi_filter=data.get(CONF_MMSI_FILTER) or [],
    )
    client.start()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry when its options/data change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        client: AISStreamClient = hass.data[DOMAIN].pop(entry.entry_id)
        await client.stop()
    return unload_ok
