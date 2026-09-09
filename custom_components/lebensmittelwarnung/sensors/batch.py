"""Sensor für die Chargennummer der jüngsten Meldung."""

from __future__ import annotations

from .base import LmwSensorBase, shorten


class LmwBatchSensor(LmwSensorBase):
    """Chargennummer / Los-Kennzeichnung der jüngsten Meldung."""

    key = "batch"
    _attr_translation_key = "batch"

    @property
    def native_value(self) -> str | None:
        entry = self.coordinator.latest
        return shorten(entry.get("batch")) if entry else None
