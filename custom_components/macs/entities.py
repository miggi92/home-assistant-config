from __future__ import annotations

import json
from pathlib import Path

from homeassistant.components.select import SelectEntity
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN, MOODS, MACS_DEVICE

def _load_debug_labels() -> list[str]:
    path = Path(__file__).parent / "www" / "shared" / "constants.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if isinstance(raw, dict):
        raw = raw.get("debugTargets", [])
    if not isinstance(raw, list):
        return []
    labels: list[str] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        label = str(entry.get("label", "")).strip()
        if label:
            labels.append(label)
    return labels


def _load_frontend_defaults() -> dict:
    path = Path(__file__).parent / "www" / "shared" / "constants.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    defaults = raw.get("defaults", [])
    if not isinstance(defaults, list):
        return {}
    mapped = {}
    for entry in defaults:
        if not isinstance(entry, dict):
            continue
        entity = entry.get("entity")
        if not entity:
            continue
        mapped[str(entity)] = entry.get("default")
    return mapped


_FRONTEND_DEFAULTS = _load_frontend_defaults()


def _get_default_number(key: str, fallback: float) -> float:
    value = _FRONTEND_DEFAULTS.get(key, fallback)
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _get_default_str(key: str, fallback: str) -> str:
    value = _FRONTEND_DEFAULTS.get(key, fallback)
    return str(value) if value is not None else fallback


def _get_default_bool(key: str, fallback: bool) -> bool:
    value = _FRONTEND_DEFAULTS.get(key, fallback)
    return value if isinstance(value, bool) else fallback


DEFAULT_MOOD = _get_default_str("mood", "idle")
if DEFAULT_MOOD not in MOODS:
    DEFAULT_MOOD = "idle"

# macs_mood dropdown select entity
class MacsMoodSelect(SelectEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Mood"
    _attr_translation_key = "mood"
    _attr_unique_id = "macs_mood"
    _attr_suggested_object_id = "macs_mood"
    _attr_icon = "mdi:emoticon"
    _attr_options = MOODS
    _attr_current_option = DEFAULT_MOOD

    async def async_select_option(self, option: str) -> None:
        if option in MOODS:
            self._attr_current_option = option
            self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state in MOODS:
            self._attr_current_option = last_state.state

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


# macs_brightness number entity
class MacsBrightnessNumber(NumberEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Brightness"
    _attr_translation_key = "brightness"
    _attr_unique_id = "macs_brightness"
    _attr_suggested_object_id = "macs_brightness"
    _attr_icon = "mdi:brightness-6"

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER
    _attr_native_value = _get_default_number("brightness", 100)

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = max(0, min(100, value))
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        try:
            value = float(last_state.state)
        except (TypeError, ValueError):
            return
        self._attr_native_value = max(0, min(100, value))

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsBatteryChargeNumber(NumberEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Battery Charge"
    _attr_translation_key = "battery_charge"
    _attr_unique_id = "macs_battery_charge"
    _attr_suggested_object_id = "macs_battery_charge"
    _attr_icon = "mdi:battery"

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER
    _attr_native_value = _get_default_number("battery_charge", 100)

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = max(0, min(100, value))
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        try:
            value = float(last_state.state)
        except (TypeError, ValueError):
            return
        self._attr_native_value = max(0, min(100, value))

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsTemperatureNumber(NumberEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Temperature"
    _attr_translation_key = "temperature"
    _attr_unique_id = "macs_temperature"
    _attr_suggested_object_id = "macs_temperature"
    _attr_icon = "mdi:thermometer"

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER
    _attr_native_value = _get_default_number("temperature", 22)

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = max(0, min(100, value))
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        try:
            value = float(last_state.state)
        except (TypeError, ValueError):
            return
        self._attr_native_value = max(0, min(100, value))

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWindSpeedNumber(NumberEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Wind Speed"
    _attr_translation_key = "windspeed"
    _attr_unique_id = "macs_windspeed"
    _attr_suggested_object_id = "macs_windspeed"
    _attr_icon = "mdi:weather-windy"

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER
    _attr_native_value = _get_default_number("windspeed", 0)

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = max(0, min(100, value))
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        try:
            value = float(last_state.state)
        except (TypeError, ValueError):
            return
        self._attr_native_value = max(0, min(100, value))

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsPrecipitationNumber(NumberEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Precipitation"
    _attr_translation_key = "precipitation"
    _attr_unique_id = "macs_precipitation"
    _attr_suggested_object_id = "macs_precipitation"
    _attr_icon = "mdi:weather-rainy"

    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = "%"
    _attr_mode = NumberMode.SLIDER
    _attr_native_value = _get_default_number("precipitation", 0)

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = max(0, min(100, value))
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        try:
            value = float(last_state.state)
        except (TypeError, ValueError):
            return
        self._attr_native_value = max(0, min(100, value))

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsAnimationsEnabledSwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Animations Enabled"
    _attr_translation_key = "animations_enabled"
    _attr_unique_id = "macs_animations_enabled"
    _attr_suggested_object_id = "macs_animations_enabled"
    _attr_icon = "mdi:animation"
    _attr_is_on = _get_default_bool("animations_enabled", True)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsChargingSwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Charging"
    _attr_translation_key = "charging"
    _attr_unique_id = "macs_charging"
    _attr_suggested_object_id = "macs_charging"
    _attr_icon = "mdi:battery-charging"
    _attr_is_on = _get_default_bool("charging", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


_DEBUG_LABELS = _load_debug_labels()
DEBUG_OPTIONS = (
    "None",
    "All",
    *_DEBUG_LABELS,
)

DEFAULT_DEBUG = _get_default_str("debug", "None")
if DEFAULT_DEBUG not in DEBUG_OPTIONS:
    DEFAULT_DEBUG = "None"


class MacsDebugSelect(SelectEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Debug"
    _attr_translation_key = "debug"
    _attr_unique_id = "macs_debug"
    _attr_suggested_object_id = "macs_debug"
    _attr_icon = "mdi:bug"
    _attr_options = DEBUG_OPTIONS
    _attr_current_option = DEFAULT_DEBUG
    _attr_entity_category = EntityCategory.CONFIG

    async def async_select_option(self, option: str) -> None:
        if option in DEBUG_OPTIONS:
            self._attr_current_option = option
            self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state and last_state.state in DEBUG_OPTIONS:
            self._attr_current_option = last_state.state

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsSnowySwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Snowy"
    _attr_translation_key = "weather_conditions_snowy"
    _attr_unique_id = "macs_weather_conditions_snowy"
    _attr_suggested_object_id = "macs_weather_conditions_snowy"
    _attr_icon = "mdi:snowflake"
    _attr_is_on = _get_default_bool("weather_conditions_snowy", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsCloudySwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Cloudy"
    _attr_translation_key = "weather_conditions_cloudy"
    _attr_unique_id = "macs_weather_conditions_cloudy"
    _attr_suggested_object_id = "macs_weather_conditions_cloudy"
    _attr_icon = "mdi:weather-cloudy"
    _attr_is_on = _get_default_bool("weather_conditions_cloudy", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsRainySwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Rainy"
    _attr_translation_key = "weather_conditions_rainy"
    _attr_unique_id = "macs_weather_conditions_rainy"
    _attr_suggested_object_id = "macs_weather_conditions_rainy"
    _attr_icon = "mdi:weather-rainy"
    _attr_is_on = _get_default_bool("weather_conditions_rainy", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsWindySwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Windy"
    _attr_translation_key = "weather_conditions_windy"
    _attr_unique_id = "macs_weather_conditions_windy"
    _attr_suggested_object_id = "macs_weather_conditions_windy"
    _attr_icon = "mdi:weather-windy"
    _attr_is_on = _get_default_bool("weather_conditions_windy", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsSunnySwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Sunny"
    _attr_translation_key = "weather_conditions_sunny"
    _attr_unique_id = "macs_weather_conditions_sunny"
    _attr_suggested_object_id = "macs_weather_conditions_sunny"
    _attr_icon = "mdi:weather-sunny"
    _attr_is_on = _get_default_bool("weather_conditions_sunny", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsStormySwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Stormy"
    _attr_translation_key = "weather_conditions_stormy"
    _attr_unique_id = "macs_weather_conditions_stormy"
    _attr_suggested_object_id = "macs_weather_conditions_stormy"
    _attr_icon = "mdi:weather-lightning"
    _attr_is_on = _get_default_bool("weather_conditions_stormy", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsFoggySwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Foggy"
    _attr_translation_key = "weather_conditions_foggy"
    _attr_unique_id = "macs_weather_conditions_foggy"
    _attr_suggested_object_id = "macs_weather_conditions_foggy"
    _attr_icon = "mdi:weather-fog"
    _attr_is_on = _get_default_bool("weather_conditions_foggy", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsHailSwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Hail"
    _attr_translation_key = "weather_conditions_hail"
    _attr_unique_id = "macs_weather_conditions_hail"
    _attr_suggested_object_id = "macs_weather_conditions_hail"
    _attr_icon = "mdi:weather-hail"
    _attr_is_on = _get_default_bool("weather_conditions_hail", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsLightningSwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Lightning"
    _attr_translation_key = "weather_conditions_lightning"
    _attr_unique_id = "macs_weather_conditions_lightning"
    _attr_suggested_object_id = "macs_weather_conditions_lightning"
    _attr_icon = "mdi:weather-lightning"
    _attr_is_on = _get_default_bool("weather_conditions_lightning", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsPartlyCloudySwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Partly Cloudy"
    _attr_translation_key = "weather_conditions_partlycloudy"
    _attr_unique_id = "macs_weather_conditions_partlycloudy"
    _attr_suggested_object_id = "macs_weather_conditions_partlycloudy"
    _attr_icon = "mdi:weather-partly-cloudy"
    _attr_is_on = _get_default_bool("weather_conditions_partlycloudy", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsPouringSwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Pouring"
    _attr_translation_key = "weather_conditions_pouring"
    _attr_unique_id = "macs_weather_conditions_pouring"
    _attr_suggested_object_id = "macs_weather_conditions_pouring"
    _attr_icon = "mdi:weather-pouring"
    _attr_is_on = _get_default_bool("weather_conditions_pouring", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsClearNightSwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Clear Night"
    _attr_translation_key = "weather_conditions_clear_night"
    _attr_unique_id = "macs_weather_conditions_clear_night"
    _attr_suggested_object_id = "macs_weather_conditions_clear_night"
    _attr_icon = "mdi:weather-night"
    _attr_is_on = _get_default_bool("weather_conditions_clear_night", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE


class MacsWeatherConditionsExceptionalSwitch(SwitchEntity, RestoreEntity):
    _attr_has_entity_name = True
    _attr_name = "Exceptional"
    _attr_translation_key = "weather_conditions_exceptional"
    _attr_unique_id = "macs_weather_conditions_exceptional"
    _attr_suggested_object_id = "macs_weather_conditions_exceptional"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_is_on = _get_default_bool("weather_conditions_exceptional", False)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if not last_state:
            return
        self._attr_is_on = (last_state.state == "on")

    @property
    def device_info(self) -> DeviceInfo:
        return MACS_DEVICE





