"""Produktbild der jüngsten Meldung.

Der Grund für eine eigene Image-Entity statt eines Template-Bild-Helfers:
lebensmittelwarnung.de weist Anfragen mit dem aiohttp-Standard-User-Agent
sporadisch mit "Server disconnected without sending a response" ab. Hier
können wir Header setzen und bei Fehlschlag erneut versuchen.
"""

from __future__ import annotations

import asyncio
import logging

from homeassistant.components.image import ImageEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import LmwConfigEntry
from .const import USER_AGENT
from .coordinator import LebensmittelwarnungCoordinator
from .entity import LmwEntity

_LOGGER = logging.getLogger(__name__)

RETRIES = 3
RETRY_DELAY = 2.0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LmwConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([LmwImage(hass, entry.runtime_data)])


class LmwImage(LmwEntity, ImageEntity):
    """Produktfoto der jüngsten Meldung."""

    _attr_translation_key = "product_image"

    def __init__(
        self, hass: HomeAssistant, coordinator: LebensmittelwarnungCoordinator
    ) -> None:
        LmwEntity.__init__(self, coordinator, "image")
        ImageEntity.__init__(self, hass)
        self._cached: bytes | None = None
        self._cached_url: str | None = None
        self._attr_image_last_updated = dt_util.utcnow()

    @property
    def _url(self) -> str | None:
        entry = self.coordinator.latest
        if entry is None or not entry.get("has_real_image"):
            return None
        return entry.get("image")

    def _handle_coordinator_update(self) -> None:
        if self._url != self._cached_url:
            self._cached = None
            self._attr_image_last_updated = dt_util.utcnow()
        super()._handle_coordinator_update()

    async def async_image(self) -> bytes | None:
        url = self._url
        if url is None:
            return None
        if self._cached is not None and self._cached_url == url:
            return self._cached

        session = self.coordinator._session  # noqa: SLF001
        for attempt in range(1, RETRIES + 1):
            try:
                response = await session.get(
                    url, headers={"User-Agent": USER_AGENT}
                )
                response.raise_for_status()
                # aiohttp trennt den MIME-Type sauber vom charset-Parameter.
                # Der rohe Content-Type-Header (z.B. "image/jpeg; charset=UTF-8")
                # lässt sich nicht direkt an web.Response übergeben - das lehnt
                # ein charset im content_type-Argument mit ValueError ab.
                content_type = response.content_type
                data = await response.read()
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug(
                    "Bild-Abruf %s fehlgeschlagen (Versuch %s/%s): %s",
                    url,
                    attempt,
                    RETRIES,
                    err,
                )
                if attempt < RETRIES:
                    await asyncio.sleep(RETRY_DELAY)
                continue

            # Ohne "?__blob=normal" liefert der Server eine HTML-Seite
            # statt der Bilddatei - die wollen wir nicht cachen.
            if not content_type.startswith("image/"):
                _LOGGER.warning(
                    "Unerwarteter Content-Type %s für %s", content_type, url
                )
                return None

            self._attr_content_type = content_type
            self._cached = data
            self._cached_url = url
            return data

        _LOGGER.warning("Bild %s nach %s Versuchen nicht abrufbar", url, RETRIES)
        return None