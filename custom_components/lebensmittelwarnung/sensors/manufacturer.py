"""Sensor für den Hersteller der jüngsten Meldung."""

from __future__ import annotations

from .base import LmwSensorBase, shorten


class LmwManufacturerSensor(LmwSensorBase):
    """Hersteller / Inverkehrbringer der jüngsten Meldung."""

    key = "manufacturer"
    _attr_translation_key = "manufacturer"

    @property
    def native_value(self) -> str | None:
        entry = self.coordinator.latest
        return shorten(entry.get("manufacturer")) if entry else None
