"""Philips Air Purifier & Humidifier."""
from __future__ import annotations

from collections.abc import Callable
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import CONF_MODEL, DATA_KEY_COORDINATOR, DATA_KEY_FAN, DOMAIN
from .philips import model_to_class

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: Callable[[list[Entity], bool], None],
):
    """Set up the fan platform."""
    _LOGGER.debug("async_setup_entry called for platform fan")

    host = entry.data[CONF_HOST]
    model = entry.data[CONF_MODEL]
    name = entry.data[CONF_NAME]

    data = hass.data[DOMAIN][host]

    model_class = model_to_class.get(model)
    if model_class:
        device = model_class(
            data[DATA_KEY_COORDINATOR],
            model=model,
            name=name,
        )
    else:
        _LOGGER.error("Unsupported model: %s", model)
        return

    data[DATA_KEY_FAN] = device
    async_add_entities([device], update_before_add=True)
