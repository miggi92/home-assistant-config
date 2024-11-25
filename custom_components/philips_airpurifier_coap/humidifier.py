"""Philips Air Purifier & Humidifier Humidifier."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

from homeassistant.components.humidifier import (
    HumidifierAction,
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .config_entry_data import ConfigEntryData
from .const import ATTR_ICON, DOMAIN, HUMIDIFIER_TYPES, FanAttributes
from .philips import PhilipsGenericControlBase, model_to_class

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[list[Entity], bool], None],
) -> None:
    """Set up the humidifier platform."""

    config_entry_data: ConfigEntryData = hass.data[DOMAIN][entry.entry_id]

    model = config_entry_data.device_information.model

    model_class = model_to_class.get(model)
    if model_class:
        available_humidifiers = []
        available_preset_modes = {}

        for cls in reversed(model_class.__mro__):
            # Get the available humidifiers from the base classes
            cls_available_humidifiers = getattr(cls, "AVAILABLE_HUMIDIFIERS", [])
            available_humidifiers.extend(cls_available_humidifiers)

            # Get the available preset modes from the base classes
            cls_available_preset_modes = getattr(cls, "AVAILABLE_PRESET_MODES", [])
            available_preset_modes.update(cls_available_preset_modes)

        humidifiers = [
            PhilipsHumidifier(
                hass, entry, config_entry_data, humidifier, available_preset_modes
            )
            for humidifier in HUMIDIFIER_TYPES
            if humidifier in available_humidifiers
        ]

        async_add_entities(humidifiers, update_before_add=False)

    else:
        _LOGGER.error("Unsupported model: %s", model)
        return


class PhilipsHumidifier(PhilipsGenericControlBase, HumidifierEntity):
    """Define a Philips AirPurifier humidifier."""

    _attr_is_on: bool | None = False

    def __init__(
        self,
        hass: HomeAssistant,
        config: ConfigEntry,
        config_entry_data: ConfigEntryData,
        humidifier: str,
        available_preset_modes: list[str],
    ) -> None:
        """Initialize the select."""

        super().__init__(hass, config, config_entry_data)

        self._model = config_entry_data.device_information.model
        name = config_entry_data.device_information.name
        latest_status = config_entry_data.latest_status

        self._description = HUMIDIFIER_TYPES[humidifier]
        self._attr_device_class = HumidifierDeviceClass.HUMIDIFIER
        self._attr_name = (
            f"{name} {self._description[FanAttributes.LABEL].replace('_', ' ').title()}"
        )

        device_id = config_entry_data.device_information.device_id
        self._attr_unique_id = f"{self._model}-{device_id}-{humidifier.lower()}"

        self._available_preset_modes = available_preset_modes

        self._power_key = self._description[FanAttributes.POWER]
        self._function_key = self._description[FanAttributes.FUNCTION]
        self._humidity_target_key = humidifier.partition("#")[0]
        self._switch = self._description[FanAttributes.SWITCH]

        self._attr_min_humidity = self._description[FanAttributes.MIN_HUMIDITY]
        self._attr_max_humidity = self._description[FanAttributes.MAX_HUMIDITY]
        self._attr_target_humidity = latest_status.get(self._humidity_target_key)
        self._attr_current_humidity = latest_status.get(
            self._description[FanAttributes.HUMIDITY]
        )

        # not all humidifiers can set a mode
        if self._switch:
            self._attr_supported_features = HumidifierEntityFeature.MODES
            self._attr_available_modes = {FanAttributes.IDLE, FanAttributes.HUMIDIFYING}

    @property
    def action(self) -> str:
        """Return the current action."""
        function_status = self._device_status.get(self._function_key)
        _LOGGER.debug("function_status: %s", function_status)

        if function_status == self._description[FanAttributes.HUMIDIFYING]:
            return HumidifierAction.HUMIDIFYING

        return HumidifierAction.IDLE

    @property
    def current_humidity(self) -> int | None:
        """Return the current humidity."""
        return self._device_status.get(self._description[FanAttributes.HUMIDITY])

    @property
    def target_humidity(self) -> int | None:
        """Return the target humidity."""
        return self._device_status.get(self._humidity_target_key)

    @property
    def mode(self) -> str | None:
        """Return the current mode."""

        # not all humidifiers can set a mode
        if not self._switch:
            return None

        function_status = self._device_status.get(self._function_key)
        if function_status == self._description[FanAttributes.HUMIDIFYING]:
            return FanAttributes.HUMIDIFYING

        return FanAttributes.IDLE

    async def async_set_mode(self, mode: str) -> None:
        """Set the mode of the humidifier."""
        if mode not in self._attr_available_modes:
            return

        if mode == FanAttributes.IDLE:
            function_value = self._description[FanAttributes.IDLE]
        else:
            function_value = self._description[FanAttributes.HUMIDIFYING]

        await self.coordinator.client.set_control_values(
            data={
                self._power_key: self._description[FanAttributes.ON],
                self._function_key: function_value,
            }
        )
        self._device_status[self._power_key] = self._description[FanAttributes.ON]
        self._device_status[self._function_key] = function_value
        self._handle_coordinator_update()

    @property
    def is_on(self) -> bool | None:
        """Return the device state independent of the humidifier function."""
        if (
            self._device_status.get(self._power_key)
            == self._description[FanAttributes.OFF]
        ):
            return False

        return True

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the device."""
        await self.coordinator.client.set_control_values(
            data={
                self._power_key: self._description[FanAttributes.ON],
            }
        )
        self._device_status[self._power_key] = self._description[FanAttributes.ON]
        self._handle_coordinator_update()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the device."""
        await self.coordinator.client.set_control_values(
            data={
                self._power_key: self._description[FanAttributes.OFF],
            }
        )
        self._device_status[self._power_key] = self._description[FanAttributes.ON]
        self._handle_coordinator_update()

    async def async_set_humidity(self, humidity: str) -> None:
        """Select target humdity."""
        step = self._description[FanAttributes.STEP]
        humidity = int(humidity)

        # if the plus/minus button is pressed, the target humidity is increased/decreased by 1
        # but we use the step to increase/decrease the humidity
        current_target = self.target_humidity
        if humidity == int(current_target) + 1:
            humidity = int(current_target) + step
        elif humidity == int(current_target) - 1:
            humidity = int(current_target) - step

        # now let's make sure we're on the steps and inside the boundaries
        target = round(humidity / step) * step
        target = max(self._attr_min_humidity, min(target, self._attr_max_humidity))
        await self.coordinator.client.set_control_value(
            self._humidity_target_key, target
        )
        self._device_status[self._humidity_target_key] = humidity
        self._handle_coordinator_update()

    @property
    def icon(self) -> str:
        """Return the icon."""
        return self._description[ATTR_ICON]
