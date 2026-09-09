"""Sensor für den Veröffentlichungszeitpunkt der jüngsten Meldung."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass

from .base import LmwSensorBase


class LmwPublishedSensor(LmwSensorBase):
    """Veröffentlichungszeitpunkt der jüngsten Meldung."""

    key = "published"
    _attr_translation_key = "published"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        entry = self.coordinator.latest
        return entry.get("published") if entry else None
