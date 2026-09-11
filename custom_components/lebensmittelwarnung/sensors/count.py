"""Sensor für die Anzahl der Meldungen im Feed."""

from __future__ import annotations

from typing import Any

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

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return {
            "meldungen": [
                {
                    "titel": entry["title"],
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
                for entry in self.coordinator.data or []
            ]
        }
