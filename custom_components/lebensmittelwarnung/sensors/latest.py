"""Sensor für die jüngste Meldung insgesamt."""

from __future__ import annotations

from typing import Any

from .base import LmwSensorBase, shorten


class LmwLatestSensor(LmwSensorBase):
    """Titel der jüngsten Meldung, mit allen Details als Attribute."""

    key = "latest"
    _attr_translation_key = "latest"

    @property
    def native_value(self) -> str | None:
        entry = self.coordinator.latest
        return shorten(entry["title"]) if entry else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        entry = self.coordinator.latest
        if entry is None:
            return None
        return {
            "link": entry["link"],
            "grund": entry.get("reason"),
            "gruende": entry.get("reasons"),
            "charge": entry.get("batch"),
            "haltbarkeit": entry.get("expiry"),
            "produkt": entry.get("product"),
            "verpackungseinheit": entry.get("package"),
            "hersteller": entry.get("manufacturer"),
            "bild": entry.get("image"),
            "bilder": entry.get("images"),
            "veroeffentlicht": entry.get("published"),
        }
