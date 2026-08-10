"""Base entity for tracked aisstream.io vessels."""
from __future__ import annotations

from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN, SIGNAL_SHIP_UPDATE
from .coordinator import AISStreamClient, ShipData


class AISStreamShipEntity(Entity):
    """Base entity representing a single tracked vessel."""

    _attr_should_poll = False
    _attr_has_entity_name = True

    def __init__(self, client: AISStreamClient, mmsi: str) -> None:
        self._client = client
        self._mmsi = mmsi

    @property
    def ship(self) -> ShipData:
        """Return the latest known data for this vessel."""
        return self._client.ships[self._mmsi]

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._mmsi)},
            name=self.ship.name or f"MMSI {self._mmsi}",
            manufacturer="aisstream.io",
            model="AIS vessel",
            configuration_url="https://aisstream.io/documentation",
        )

    @property
    def available(self) -> bool:
        return self._client.available and self._mmsi in self._client.ships

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                f"{SIGNAL_SHIP_UPDATE}_{self._mmsi}",
                self._handle_update,
            )
        )

    def _handle_update(self) -> None:
        self.async_write_ha_state()
