"""Sensor für die Produktbezeichnung der jüngsten Meldung."""

from __future__ import annotations

from .base import LmwSensorBase, shorten


class LmwProductSensor(LmwSensorBase):
    """Produktbezeichnung/-beschreibung der jüngsten Meldung."""

    key = "product"
    _attr_translation_key = "product"

    @property
    def native_value(self) -> str | None:
        entry = self.coordinator.latest
        return shorten(entry.get("product")) if entry else None
