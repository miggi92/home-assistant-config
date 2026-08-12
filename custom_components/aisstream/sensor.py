"""Sensor platform for aisstream.io."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import DEGREE, UnitOfSpeed
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import (
    DOMAIN,
    NAVIGATIONAL_STATUS,
    PRESENCE_RECHECK_MINUTES,
    PRESENCE_TIMEOUT_MINUTES,
    SIGNAL_NEW_SHIP,
    SUBENTRY_TYPE_AREA,
)
from .coordinator import AISStreamClient, ShipData
from .entity import AISStreamShipEntity
from .geo import point_in_box, resolve_area_box

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class AISStreamSensorDescription(SensorEntityDescription):
    """Describes an aisstream.io sensor."""

    value_fn: Callable[[ShipData], object]


def _heading(ship: ShipData) -> int | None:
    # 511 means "not available" per the AIS spec.
    if ship.true_heading is None or ship.true_heading == 511:
        return None
    return ship.true_heading


SENSOR_DESCRIPTIONS: tuple[AISStreamSensorDescription, ...] = (
    AISStreamSensorDescription(
        key="speed",
        translation_key="speed_over_ground",
        native_unit_of_measurement=UnitOfSpeed.KNOTS,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ship: ship.sog,
    ),
    AISStreamSensorDescription(
        key="course",
        translation_key="course_over_ground",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda ship: ship.cog,
    ),
    AISStreamSensorDescription(
        key="heading",
        translation_key="true_heading",
        native_unit_of_measurement=DEGREE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_heading,
    ),
    AISStreamSensorDescription(
        key="navigational_status",
        translation_key="navigational_status",
        device_class=SensorDeviceClass.ENUM,
        options=list(NAVIGATIONAL_STATUS.values()),
        value_fn=lambda ship: (
            NAVIGATIONAL_STATUS.get(ship.navigational_status)
            if ship.navigational_status is not None
            else None
        ),
    ),
    AISStreamSensorDescription(
        key="destination",
        translation_key="destination",
        value_fn=lambda ship: ship.destination or None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for aisstream.io: one count sensor per area, plus
    per-vessel sensors added dynamically as ships are seen."""
    client: AISStreamClient = hass.data[DOMAIN][entry.entry_id]
    known_mmsi: set[str] = set()

    for subentry_id, subentry in entry.subentries.items():
        if subentry.subentry_type != SUBENTRY_TYPE_AREA:
            continue
        box = resolve_area_box(hass, subentry.data)
        if box is None:
            continue
        async_add_entities(
            [AISStreamAreaCountSensor(client, entry, subentry_id, subentry, box)],
            config_subentry_id=subentry_id,
        )

    @callback
    def _add_ship(mmsi: str) -> None:
        if mmsi in known_mmsi:
            return
        known_mmsi.add(mmsi)
        async_add_entities(
            AISStreamSensor(client, mmsi, description)
            for description in SENSOR_DESCRIPTIONS
        )

    entry.async_on_unload(
        async_dispatcher_connect(
            hass, f"{SIGNAL_NEW_SHIP}_{entry.entry_id}", _add_ship
        )
    )

    for mmsi in list(client.ships):
        _add_ship(mmsi)


class AISStreamSensor(AISStreamShipEntity, SensorEntity):
    """A single data point (speed, course, ...) of a tracked vessel."""

    entity_description: AISStreamSensorDescription

    def __init__(
        self,
        client: AISStreamClient,
        mmsi: str,
        description: AISStreamSensorDescription,
    ) -> None:
        super().__init__(client, mmsi)
        self.entity_description = description
        self._attr_unique_id = f"{mmsi}_{description.key}"

    @property
    def native_value(self):
        return self.entity_description.value_fn(self.ship)


class AISStreamAreaCountSensor(SensorEntity):
    """Number of vessels currently present in one monitored area."""

    _attr_should_poll = False
    _attr_has_entity_name = True
    _attr_translation_key = "vessels_in_area"
    _attr_native_unit_of_measurement = "vessels"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:ferry"

    def __init__(
        self,
        client: AISStreamClient,
        entry: ConfigEntry,
        subentry_id: str,
        subentry: ConfigSubentry,
        box: list,
    ) -> None:
        self._client = client
        self._entry = entry
        self._subentry_id = subentry_id
        self._subentry = subentry
        self._box = box
        self._attr_unique_id = f"{subentry_id}_vessels_in_area"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._subentry_id)},
            name=self._subentry.title,
            manufacturer="aisstream.io",
            model="AIS area monitor",
        )

    @property
    def available(self) -> bool:
        return self._client.available

    def _present_ships(self) -> list[ShipData]:
        threshold = dt_util.utcnow() - timedelta(minutes=PRESENCE_TIMEOUT_MINUTES)
        return [
            ship
            for ship in self._client.ships.values()
            if ship.last_position_update
            and ship.last_position_update >= threshold
            and ship.latitude is not None
            and ship.longitude is not None
            and point_in_box(ship.latitude, ship.longitude, self._box)
        ]

    @property
    def native_value(self) -> int:
        return len(self._present_ships())

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "vessels": sorted(
                ship.name or f"MMSI {ship.mmsi}" for ship in self._present_ships()
            ),
            "connected": self._client.available,
            "bounding_box": self._box,
            "messages_received": self._client.messages_received,
            "last_message_at": self._client.last_message_at.isoformat()
            if self._client.last_message_at
            else None,
        }

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{SIGNAL_NEW_SHIP}_{self._entry.entry_id}",
                self._handle_update,
            )
        )
        self.async_on_remove(
            async_track_time_interval(
                self.hass,
                self._handle_update,
                timedelta(minutes=PRESENCE_RECHECK_MINUTES),
            )
        )

    @callback
    def _handle_update(self, *_args) -> None:
        self.async_write_ha_state()
