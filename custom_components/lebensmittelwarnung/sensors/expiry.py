"""Sensor für die Haltbarkeit der jüngsten Meldung."""

from __future__ import annotations

from .base import LmwSensorBase, shorten


class LmwExpirySensor(LmwSensorBase):
    """Haltbarkeit des von der jüngsten Meldung betroffenen Produkts."""

    key = "expiry"
    _attr_translation_key = "expiry"

    @property
    def native_value(self) -> str | None:
        entry = self.coordinator.latest
        return shorten(entry.get("expiry")) if entry else None
