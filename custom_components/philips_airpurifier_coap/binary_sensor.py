"""Philips Air Purifier & Humidifier Binary Sensors."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any, cast

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_CLASS, CONF_ENTITY_CATEGORY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .config_entry_data import ConfigEntryData
from .const import BINARY_SENSOR_TYPES, DOMAIN, FanAttributes
from .philips import PhilipsEntity, model_to_class

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[list[Entity], bool], None],
) -> None:
    """Set up platform for binary_sensor."""

    config_entry_data: ConfigEntryData = hass.data[DOMAIN][entry.entry_id]

    model = config_entry_data.device_information.model
    status = config_entry_data.latest_status

    model_class = model_to_class.get(model)
    available_binary_sensors = []

    if model_class:
        for cls in reversed(model_class.__mro__):
            cls_available_binary_sensors = getattr(cls, "AVAILABLE_BINARY_SENSORS", [])
            available_binary_sensors.extend(cls_available_binary_sensors)

    binary_sensors = [
        PhilipsBinarySensor(hass, entry, config_entry_data, binary_sensor)
        for binary_sensor in BINARY_SENSOR_TYPES
        if binary_sensor in status and binary_sensor in available_binary_sensors
    ]

    async_add_entities(binary_sensors, update_before_add=False)


class PhilipsBinarySensor(PhilipsEntity, BinarySensorEntity):
    """Define a Philips AirPurifier binary_sensor."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        config_entry_data: ConfigEntryData,
        kind: str,
    ) -> None:
        """Initialize the binary sensor."""

        super().__init__(hass, config, config_entry_data)

        self._model = config_entry_data.device_information.model
        name = config_entry_data.device_information.name

        self._description = BINARY_SENSOR_TYPES[kind]
        self._icon_map = self._description.get(FanAttributes.ICON_MAP)
        self._norm_icon = (
            next(iter(self._icon_map.items()))[1]
            if self._icon_map is not None
            else None
        )
        self._attr_device_class = self._description.get(ATTR_DEVICE_CLASS)
        self._attr_entity_category = self._description.get(CONF_ENTITY_CATEGORY)
        self._attr_name = (
            f"{name} {self._description[FanAttributes.LABEL].replace('_', ' ').title()}"
        )

        model = config_entry_data.device_information.model
        device_id = config_entry_data.device_information.device_id
        self._attr_unique_id = f"{model}-{device_id}-{kind.lower()}"

        self._attrs: dict[str, Any] = {}
        self.kind = kind

    @property
    def is_on(self) -> bool:
        """Return the state of the binary sensor."""
        value = self._device_status[self.kind]
        convert = self._description.get(FanAttributes.VALUE)
        if convert:
            value = convert(value)
        return cast(bool, value)

    @property
    def icon(self) -> str:
        """Return the icon of the binary sensor."""
        icon = self._norm_icon
        if not self._icon_map:
            return icon

        return self._icon_map[self.is_on]
