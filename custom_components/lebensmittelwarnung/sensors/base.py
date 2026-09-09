"""Gemeinsame Basis für die einzelnen Meldungs-Sensoren."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity

from ..entity import LmwEntity

# Zustände sind auf 255 Zeichen begrenzt. Felder wie "Haltbarkeit" oder
# "Produktbezeichnung" listen bei Sammelrückrufen schnell mehr auf.
MAX_STATE_LENGTH = 255


def shorten(value: Any) -> str | None:
    """Mehrzeilige bzw. zu lange Werte auf die State-Länge kürzen."""
    if value is None:
        return None
    text = str(value).replace("\n", " | ")
    return text[:MAX_STATE_LENGTH]


class LmwSensorBase(LmwEntity, SensorEntity):
    """Basis für einen Sensor, der ein Feld der jüngsten Meldung zeigt."""

    key: str

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator, self.key)
