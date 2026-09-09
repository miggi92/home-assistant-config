"""Sensor-Plattform: richtet je Meldungsfeld einen Sensor ein.

Die eigentlichen Sensoren stecken einzeln im sensors/-Unterpaket.
"""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import LmwConfigEntry
from .sensors import SENSOR_CLASSES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LmwConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(sensor_cls(coordinator) for sensor_cls in SENSOR_CLASSES)
