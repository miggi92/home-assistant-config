"""Zeigt an, ob eine Meldung aus den letzten 24 Stunden vorliegt."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_point_in_utc_time
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
        self._expiry_unsub = None

    @property
    def is_on(self) -> bool:
        entry = self.coordinator.latest
        published = entry.get("published") if entry else None
        if published is None:
            return False
        return dt_util.utcnow() - published < RECENT_WINDOW

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._schedule_expiry()

    async def async_will_remove_from_hass(self) -> None:
        self._cancel_expiry()
        await super().async_will_remove_from_hass()

    @callback
    def _handle_coordinator_update(self) -> None:
        self._schedule_expiry()
        super()._handle_coordinator_update()

    @callback
    def _cancel_expiry(self) -> None:
        if self._expiry_unsub is not None:
            self._expiry_unsub()
            self._expiry_unsub = None

    @callback
    def _schedule_expiry(self) -> None:
        """Erzwingt ein Update, sobald das 24h-Fenster abläuft.

        Ohne das bleibt der Sensor bis zum nächsten erfolgreichen Feed-Poll
        (stündlich, oder später bei Poll-Fehlern) fälschlicherweise "an".
        """
        self._cancel_expiry()
        entry = self.coordinator.latest
        published = entry.get("published") if entry else None
        if published is None:
            return
        expires_at = published + RECENT_WINDOW
        if expires_at <= dt_util.utcnow():
            return

        @callback
        def _expire(_now: datetime) -> None:
            self._expiry_unsub = None
            self.async_write_ha_state()

        self._expiry_unsub = async_track_point_in_utc_time(
            self.hass, _expire, expires_at
        )