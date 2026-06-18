"""Persistent panel profile storage for Voice Satellite."""

from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import DOMAIN

_STORE_VERSION = 1
_STORE_KEY = f"{DOMAIN}.panel_settings"
_LOCK_KEY = f"{DOMAIN}_panel_settings_lock"


def _store(hass: HomeAssistant) -> Store[dict[str, Any]]:
    return Store(hass, _STORE_VERSION, _STORE_KEY)


def _lock(hass: HomeAssistant) -> asyncio.Lock:
    return hass.data.setdefault(_LOCK_KEY, asyncio.Lock())


async def async_get_panel_settings(
    hass: HomeAssistant,
    entity_id: str,
) -> dict[str, Any] | None:
    """Return the persisted panel settings for a satellite entity."""
    data = await _store(hass).async_load()
    profiles = data.get("profiles", {}) if isinstance(data, dict) else {}
    config = profiles.get(entity_id)
    return dict(config) if isinstance(config, dict) else None


async def async_save_panel_settings(
    hass: HomeAssistant,
    entity_id: str,
    config: dict[str, Any],
) -> None:
    """Persist panel settings for a satellite entity."""
    async with _lock(hass):
        store = _store(hass)
        data = await store.async_load()
        if not isinstance(data, dict):
            data = {}

        profiles = data.get("profiles")
        if not isinstance(profiles, dict):
            profiles = {}

        # Store a copy so later caller mutation cannot affect pending writes.
        clean_config = dict(config)
        clean_config["satellite_entity"] = entity_id
        profiles[entity_id] = clean_config
        data["profiles"] = profiles
        await store.async_save(data)
