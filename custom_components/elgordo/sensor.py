from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import CURRENCY_EURO
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DEFAULT_TICKET_TYPE,
    DOMAIN,
    MANUFACTURER,
    normalize_ticket_number,
    prize_for_ticket_type,
)


@dataclass(frozen=True, kw_only=True)
class MainPrizeSensorEntityDescription(SensorEntityDescription):
    """Describe an El Gordo main prize sensor."""

    api_key: str


MAIN_PRIZE_SENSORS = (
    MainPrizeSensorEntityDescription(
        key="first_prize",
        translation_key="first_prize",
        api_key="numero1",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="second_prize",
        translation_key="second_prize",
        api_key="numero2",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="third_prize",
        translation_key="third_prize",
        api_key="numero3",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fourth_prize_1",
        translation_key="fourth_prize_1",
        api_key="numero4",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fourth_prize_2",
        translation_key="fourth_prize_2",
        api_key="numero5",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fifth_prize_1",
        translation_key="fifth_prize_1",
        api_key="numero6",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fifth_prize_2",
        translation_key="fifth_prize_2",
        api_key="numero7",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fifth_prize_3",
        translation_key="fifth_prize_3",
        api_key="numero8",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fifth_prize_4",
        translation_key="fifth_prize_4",
        api_key="numero9",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fifth_prize_5",
        translation_key="fifth_prize_5",
        api_key="numero10",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fifth_prize_6",
        translation_key="fifth_prize_6",
        api_key="numero11",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fifth_prize_7",
        translation_key="fifth_prize_7",
        api_key="numero12",
        icon="mdi:trophy-variant",
    ),
    MainPrizeSensorEntityDescription(
        key="fifth_prize_8",
        translation_key="fifth_prize_8",
        api_key="numero13",
        icon="mdi:trophy-variant",
    ),
)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    tickets_str = entry.options.get("tickets", entry.data.get("tickets", ""))
    tickets = [t.strip() for t in tickets_str.split(",") if t.strip()]
    ticket_type = entry.options.get(
        "ticket_type", entry.data.get("ticket_type", DEFAULT_TICKET_TYPE)
    )

    entities = []
    # Individual Ticket Sensors
    for ticket in tickets:
        entities.append(TicketPrizeSensor(coordinator, ticket, ticket_type))

    entities.extend(
        MainPrizeSensor(coordinator, description)
        for description in MAIN_PRIZE_SENSORS
    )

    async_add_entities(entities)


class ElGordoBaseSensor(CoordinatorEntity, SensorEntity):
    """Base sensor with shared Device Info."""

    _attr_has_entity_name = True

    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "El Gordo Lottery",
            "manufacturer": MANUFACTURER,
            "model": "Spain Christmas Lottery",
        }


class TicketPrizeSensor(ElGordoBaseSensor):
    """Sensor for a specific ticket."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = CURRENCY_EURO
    _attr_suggested_display_precision = 0
    _attr_translation_key = "ticket_prize"

    def __init__(self, coordinator, ticket, ticket_type):
        super().__init__(coordinator)
        self.ticket = ticket
        self.ticket_type = ticket_type
        self._attr_translation_placeholders = {"ticket": ticket}
        self._attr_unique_id = f"{DOMAIN}_prize_{ticket}"

    @property
    def native_value(self):
        tickets = (self.coordinator.data or {}).get("tickets", {})
        ticket_data = tickets.get(self.ticket, {})
        return prize_for_ticket_type(ticket_data.get("premio"), self.ticket_type)

    @property
    def extra_state_attributes(self):
        return {
            "ticket_type": self.ticket_type,
        }

    @property
    def available(self):
        tickets = (self.coordinator.data or {}).get("tickets", {})
        return super().available and self.ticket in tickets

    @property
    def icon(self):
        return (
            "mdi:ticket-confirmation"
            if (self.native_value or 0) > 0
            else "mdi:ticket-outline"
        )


class MainPrizeSensor(ElGordoBaseSensor):
    """Sensor for general winning numbers."""

    entity_description: MainPrizeSensorEntityDescription

    def __init__(self, coordinator, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_winning_{description.key}"

    @property
    def native_value(self):
        summary = (self.coordinator.data or {}).get("summary", {})
        return normalize_ticket_number(summary.get(self.entity_description.api_key))

    @property
    def extra_state_attributes(self):
        summary = (self.coordinator.data or {}).get("summary", {})
        if "draw_year" not in summary:
            return None
        return {
            "data_source": summary.get("data_source"),
            "draw_year": summary["draw_year"],
        }
