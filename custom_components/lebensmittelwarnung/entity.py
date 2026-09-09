"""Gemeinsame Basis für alle Entities."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LebensmittelwarnungCoordinator


def device_id(type_key: str, state_key: str) -> str:
    """Geräte-/unique_id-Teil aus Meldungsart und Bundesland bilden.

    Ohne gewählte Meldungsart entspricht das exakt dem alten Format (nur
    Bundesland), damit bestehende Installationen ihre unique_ids und
    Entity-IDs behalten.
    """
    state_part = state_key or "alle"
    return f"{type_key}_{state_part}" if type_key else state_part


class LmwEntity(CoordinatorEntity[LebensmittelwarnungCoordinator]):
    """Hängt alle Entities an ein gemeinsames Gerät."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: LebensmittelwarnungCoordinator, key: str
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        device_key = device_id(coordinator.type_key, coordinator.state_key)
        self._attr_unique_id = f"{DOMAIN}_{device_key}_{key}"
        name = f"Lebensmittelwarnung {coordinator.state_name}"
        if coordinator.type_key:
            name = f"Lebensmittelwarnung {coordinator.type_name} – {coordinator.state_name}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_key)},
            name=name,
            manufacturer="BVL / Bundesländer",
            model="lebensmittelwarnung.de",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.lebensmittelwarnung.de/",
        )