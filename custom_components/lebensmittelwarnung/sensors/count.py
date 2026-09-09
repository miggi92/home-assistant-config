"""Sensor für die Anzahl der Meldungen im Feed."""

from __future__ import annotations

from homeassistant.const import EntityCategory

from .base import LmwSensorBase


class LmwCountSensor(LmwSensorBase):
    """Anzahl der aktuell im Feed enthaltenen Meldungen."""

    key = "count"
    _attr_translation_key = "count"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> int:
        return len(self.coordinator.data or [])
