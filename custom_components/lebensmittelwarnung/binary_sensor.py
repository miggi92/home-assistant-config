"""Zeigt an, ob eine Meldung aus den letzten 24 Stunden vorliegt."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import LmwConfigEntry
from .entity import LmwEntity

RECENT_WINDOW = timedelta(hours=24)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LmwConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([LmwRecentWarning(entry.runtime_data)])


class LmwRecentWarning(LmwEntity, BinarySensorEntity):
    """An, solange die jüngste Meldung keine 24 Stunden alt ist."""

    _attr_translation_key = "recent_warning"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, "recent")

    @property
    def is_on(self) -> bool:
        entry = self.coordinator.latest
        published = entry.get("published") if entry else None
        if published is None:
            return False
        return dt_util.utcnow() - published < RECENT_WINDOW