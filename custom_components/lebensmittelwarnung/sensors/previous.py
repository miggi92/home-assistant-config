"""Sensor für die vorletzte Meldung (die vor der aktuellen)."""

from __future__ import annotations

from typing import Any

from .base import LmwSensorBase, shorten


class LmwPreviousSensor(LmwSensorBase):
    """Titel der vorherigen Meldung, mit allen Details als Attribute."""

    key = "previous"
    _attr_translation_key = "previous"

    @property
    def _entry(self) -> dict[str, Any] | None:
        data = self.coordinator.data
        return data[1] if data and len(data) > 1 else None

    @property
    def native_value(self) -> str | None:
        entry = self._entry
        return shorten(entry["title"]) if entry else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        entry = self._entry
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
