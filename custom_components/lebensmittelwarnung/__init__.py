"""Die Lebensmittelwarnung-Integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_STATE, CONF_TYPE
from .coordinator import LebensmittelwarnungCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.IMAGE, Platform.BINARY_SENSOR]

type LmwConfigEntry = ConfigEntry[LebensmittelwarnungCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: LmwConfigEntry) -> bool:
    """Einen Feed einrichten."""
    coordinator = LebensmittelwarnungCoordinator(
        hass,
        entry,
        entry.data.get(CONF_TYPE, ""),
        entry.data.get(CONF_STATE, ""),
    )
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: LmwConfigEntry) -> bool:
    """Feed wieder entfernen."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)