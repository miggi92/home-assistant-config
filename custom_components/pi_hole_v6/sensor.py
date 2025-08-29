"""Support for getting statistical data from a Pi-hole system."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, List

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CONF_NAME, PERCENTAGE, EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from . import PiHoleV6ConfigEntry
from .api import API as ClientAPI
from .common import sensor_update_timer
from .entity import PiHoleV6Entity

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="remaining_until_blocking_mode",
        translation_key="remaining_until_blocking_mode",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="ads_blocked_today",
        translation_key="ads_blocked_today",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="ads_percentage_blocked_today",
        translation_key="ads_percentage_blocked_today",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=2,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="seen_clients",
        translation_key="seen_clients",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dns_queries_today",
        translation_key="dns_queries_today",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="domains_blocked",
        translation_key="domains_blocked",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dns_queries_cached",
        translation_key="dns_queries_cached",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dns_queries_forwarded",
        translation_key="dns_queries_forwarded",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dns_queries_frequency",
        translation_key="dns_queries_frequency",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="dns_unique_clients",
        translation_key="dns_unique_clients",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dns_unique_domains",
        translation_key="dns_unique_domains",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="configured_clients",
        translation_key="configured_clients",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        entity_category=EntityCategory.DIAGNOSTIC,
        key="latest_data_refresh",
        translation_key="latest_data_refresh",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        entity_category=EntityCategory.DIAGNOSTIC,
        key="memory_use",
        translation_key="memory_use",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        entity_category=EntityCategory.DIAGNOSTIC,
        key="cpu_use",
        translation_key="cpu_use",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        key="ftl_info_message_count",
        translation_key="ftl_info_message_count",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    SensorEntityDescription(
        entity_category=EntityCategory.DIAGNOSTIC,
        key="auth_sessions",
        translation_key="auth_sessions",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        entity_registry_enabled_default=False,
    ),
)

context_name: str = ""


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PiHoleV6ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Pi-hole V6 sensor."""
    name = entry.data[CONF_NAME]
    hole_data = entry.runtime_data
    sensors = [
        PiHoleV6Sensor(
            hole_data.api,
            hole_data.coordinator,
            name,
            entry.entry_id,
            description,
        )
        for description in SENSOR_TYPES
    ]
    async_add_entities(sensors, True)

    hass.data[f"pi_hole_entities_sensor_{name}"] = []
    hass.data[f"pi_hole_entities_sensor_{name}"].extend(sensors)

    async def update_timer(now: Any) -> None:
        """..."""
        await sensor_update_timer(hass, now, name)

    async_track_time_interval(hass, update_timer, timedelta(seconds=1))


class PiHoleV6Sensor(PiHoleV6Entity, SensorEntity):
    """Representation of a Pi-hole V6 sensor."""

    entity_description: SensorEntityDescription

    def __init__(
        self,
        api: ClientAPI,
        coordinator: DataUpdateCoordinator[None],
        name: str,
        server_unique_id: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize a Pi-hole V6 sensor."""
        super().__init__(api, coordinator, name, server_unique_id)
        self.entity_description = description
        self._attr_unique_id = f"{self._server_unique_id}/{description.key}"
        self.entity_id = f"sensor.{name}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the device."""

        match self.entity_description.key:
            case "latest_data_refresh":
                return self.api.last_refresh
            case "ads_blocked_today":
                return self.api.cache_summary["queries"]["blocked"]
            case "ads_percentage_blocked_today":
                return self.api.cache_summary["queries"]["percent_blocked"]
            case "seen_clients":
                return self.api.cache_summary["clients"]["total"]
            case "dns_queries_today":
                return self.api.cache_summary["queries"]["total"]
            case "domains_blocked":
                return self.api.cache_summary["gravity"]["domains_being_blocked"]
            case "dns_queries_cached":
                return self.api.cache_summary["queries"]["cached"]
            case "dns_queries_forwarded":
                return self.api.cache_summary["queries"]["forwarded"]
            case "dns_unique_clients":
                return self.api.cache_summary["clients"]["active"]
            case "dns_unique_domains":
                return self.api.cache_summary["queries"]["unique_domains"]
            case "dns_queries_frequency":
                return round(self.api.cache_summary["queries"]["frequency"] * 60, 0)
            case "memory_use":
                return self.api.cache_padd["%mem"]
            case "cpu_use":
                return self.api.cache_padd["%cpu"]
            case "ftl_info_message_count":
                return self.api.cache_ftl_info["message_count"]
            case "remaining_until_blocking_mode":
                return self.native_remaining_until_blocking_mode()
            case "configured_clients":
                return len(self.api.cache_configured_clients)
            case "auth_sessions":
                return len(self.api.cache_auth_sessions)

        return ""

    def native_remaining_until_blocking_mode(self) -> int:
        """..."""

        value = round(self.api.cache_blocking["timer"]) if self.api.cache_blocking["timer"] is not None else 0

        if value > 0:
            until_date: datetime = datetime.now() + timedelta(seconds=value)
            self.api.cache_remaining_dates[f"{self._name}_sensor/global"] = until_date
        elif f"{self._name}_sensor/global" in self.api.cache_remaining_dates:
            del self.api.cache_remaining_dates[f"{self._name}_sensor/global"]

        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the state attributes of the Pi-hole V6."""

        if self.entity_description.key == "memory_use":
            return self.api.cache_padd["system"]["memory"]

        if self.entity_description.key == "cpu_use":
            return self.api.cache_padd["system"]["cpu"]

        if self.entity_description.key == "ftl_info_message_count":
            raw_messages: List[Any] = self.api.cache_ftl_info["message_list"]
            messages: List[Any] = [{k: v for k, v in message.items() if k != "html"} for message in raw_messages]
            status: str = self.api.cache_ftl_info["status"]
            return {"messages": messages, "status": status, "note": "Total number of Pi-hole diagnosis messages."}

        if self.entity_description.key == "configured_clients":
            raw_clients: List[Any] = self.api.cache_configured_clients
            excluding: List[str] = ["date_added", "date_modified"]
            clients: List[Any] = [{k: v for k, v in client.items() if k not in excluding} for client in raw_clients]
            return {"clients": clients, "note": "Total number of configured clients."}

        if self.entity_description.key == "auth_sessions":
            raw_sessions: List[Any] = self.api.cache_auth_sessions
            excluding: List[str] = ["tls", "x_forwarded_for"]
            sessions: List[Any] = [{k: v for k, v in session.items() if k not in excluding} for session in raw_sessions]
            return {"sessions": sessions, "note": "Total number of auth sessions."}

        match self.entity_description.key:
            case "ads_blocked_today":
                return {"note": "Number of blocked queries during the last 24h."}
            case "ads_percentage_blocked_today":
                return {"note": "Percent of blocked queries during the last 24h."}
            case "seen_clients":
                return {"note": "Total number of clients seen by FTL."}
            case "dns_queries_today":
                return {"note": "Total number of queries during the last 24h."}
            case "domains_blocked":
                return {"note": "Number of domain on your Pi-hole's gravity."}
            case "dns_queries_cached":
                return {"note": "Number of queries replied to from cache or local configuration."}
            case "dns_queries_forwarded":
                return {"note": "Number of queries that have been forwarded."}
            case "dns_unique_clients":
                return {"note": "Number of active clients (seen in the last 24h)."}
            case "dns_unique_domains":
                return {"note": "Number of unique domains FTL knows."}
            case "dns_queries_frequency":
                return {"note": "Average number of DNS queries per minute."}
            case "remaining_until_blocking_mode":
                return {"note": "Remaining seconds until blocking mode is automatically changed."}

        return None
