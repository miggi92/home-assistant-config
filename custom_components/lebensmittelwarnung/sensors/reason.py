"""Sensor für den Grund der jüngsten Meldung."""

from __future__ import annotations

from typing import Any

from .base import LmwSensorBase, shorten

# Die Gründe sind ein fester Satz von sieben Werten (siehe Filter auf
# lebensmittelwarnung.de). Bei Mehrfachnennungen gewinnt der erste Treffer.
REASON_ICONS: dict[str, str] = {
    "Krankheitserreger": "mdi:bacteria-outline",
    "Allergene": "mdi:peanut-off-outline",
    "Fremdkörper": "mdi:magnet-on",
    "Gesundheitsschädliche Substanz": "mdi:skull-crossbones-outline",
    "Rückstände und Kontaminanten": "mdi:flask-outline",
    "Irreführung und Täuschung": "mdi:eye-off-outline",
    "Sonstige Gründe": "mdi:dots-horizontal-circle-outline",
}
DEFAULT_REASON_ICON = "mdi:alert-octagon-outline"


class LmwReasonSensor(LmwSensorBase):
    """Grund der jüngsten Meldung."""

    key = "reason"
    _attr_translation_key = "reason"

    @property
    def native_value(self) -> str | None:
        entry = self.coordinator.latest
        return shorten(entry.get("reason")) if entry else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        entry = self.coordinator.latest
        if entry is None:
            return None
        return {"gruende": entry.get("reasons")}

    @property
    def icon(self) -> str:
        """Icon richtet sich nach der Art der Meldung."""
        entry = self.coordinator.latest
        if entry is None:
            return DEFAULT_REASON_ICON

        for reason in entry.get("reasons") or []:
            if icon := REASON_ICONS.get(reason):
                return icon
        return DEFAULT_REASON_ICON
