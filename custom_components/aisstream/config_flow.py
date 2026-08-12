"""Config flow for the aisstream.io integration."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from .const import (
    AISSTREAM_WS_URL,
    CONF_API_KEY,
    CONF_BOX_EAST,
    CONF_BOX_NORTH,
    CONF_BOX_SOUTH,
    CONF_BOX_WEST,
    CONF_LOCATION,
    CONF_MMSI_FILTER,
    CONF_ZONE,
    DEFAULT_BOX_EAST,
    DEFAULT_BOX_NORTH,
    DEFAULT_BOX_SOUTH,
    DEFAULT_BOX_WEST,
    DOMAIN,
    SUBENTRY_TYPE_AREA,
)
from .geo import bounding_box_for_location, bounding_box_for_zone

_LOGGER = logging.getLogger(__name__)

VALIDATE_TIMEOUT = 8


def _area_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Optional(
                CONF_LOCATION,
                description={"suggested_value": defaults.get(CONF_LOCATION)},
            ): selector.LocationSelector(
                selector.LocationSelectorConfig(radius=True)
            ),
            vol.Optional(
                CONF_ZONE,
                description={"suggested_value": defaults.get(CONF_ZONE)},
            ): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="zone")
            ),
            vol.Optional(
                CONF_BOX_SOUTH,
                default=defaults.get(CONF_BOX_SOUTH, DEFAULT_BOX_SOUTH),
            ): vol.Coerce(float),
            vol.Optional(
                CONF_BOX_WEST, default=defaults.get(CONF_BOX_WEST, DEFAULT_BOX_WEST)
            ): vol.Coerce(float),
            vol.Optional(
                CONF_BOX_NORTH,
                default=defaults.get(CONF_BOX_NORTH, DEFAULT_BOX_NORTH),
            ): vol.Coerce(float),
            vol.Optional(
                CONF_BOX_EAST, default=defaults.get(CONF_BOX_EAST, DEFAULT_BOX_EAST)
            ): vol.Coerce(float),
            vol.Optional(
                CONF_MMSI_FILTER, default=defaults.get(CONF_MMSI_FILTER, "")
            ): str,
        }
    )


def _parse_mmsi_filter(raw: str) -> list[str]:
    return [part.strip() for part in raw.split(",") if part.strip()]


def _is_whole_world(data: dict[str, Any]) -> bool:
    return (
        data[CONF_BOX_SOUTH] <= -89.9
        and data[CONF_BOX_WEST] <= -179.9
        and data[CONF_BOX_NORTH] >= 89.9
        and data[CONF_BOX_EAST] >= 179.9
    )


def _resolve_bounding_boxes(
    hass: HomeAssistant, user_input: dict[str, Any]
) -> tuple[list | None, str | None]:
    """Resolve the bounding box from a zone, a picked location, or manual fields.

    Returns (bounding_boxes, error_code). error_code is None on success.
    """
    if zone_entity_id := user_input.get(CONF_ZONE):
        bounding_boxes = bounding_box_for_zone(hass, zone_entity_id)
        if bounding_boxes is None:
            return None, "zone_not_found"
        return bounding_boxes, None

    if location := user_input.get(CONF_LOCATION):
        bounding_boxes = bounding_box_for_location(location)
        if bounding_boxes is None:
            return None, "invalid_location"
        return bounding_boxes, None

    mmsi_filter = _parse_mmsi_filter(user_input.get(CONF_MMSI_FILTER, ""))
    if not mmsi_filter and _is_whole_world(user_input):
        return None, "no_filter"

    return [
        [
            [user_input[CONF_BOX_SOUTH], user_input[CONF_BOX_WEST]],
            [user_input[CONF_BOX_NORTH], user_input[CONF_BOX_EAST]],
        ]
    ], None


def _area_title(hass: HomeAssistant, data: dict[str, Any]) -> str:
    if zone_entity_id := data.get(CONF_ZONE):
        state = hass.states.get(zone_entity_id)
        return state.name if state else zone_entity_id

    if location := data.get(CONF_LOCATION):
        return f"{location['latitude']:.3f}, {location['longitude']:.3f}"

    mmsi_filter = data.get(CONF_MMSI_FILTER) or []
    if isinstance(mmsi_filter, str):
        mmsi_filter = _parse_mmsi_filter(mmsi_filter)
    if mmsi_filter:
        return f"{len(mmsi_filter)} vessel(s)"

    return "Custom area"


async def _validate_api_key(
    api_key: str, bounding_boxes: list, mmsi_filter: list[str]
) -> None:
    """Open a short-lived websocket connection to verify the API key works."""
    # Send both casings - aisstream's own sources disagree on "APIKey" vs
    # "Apikey" and this environment can't reach aisstream.io to verify.
    message: dict = {
        "APIKey": api_key,
        "Apikey": api_key,
        "BoundingBoxes": bounding_boxes,
    }
    if mmsi_filter:
        message["FiltersShipMMSI"] = mmsi_filter

    try:
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(AISSTREAM_WS_URL) as ws:
                await ws.send_json(message)
                try:
                    async with asyncio.timeout(VALIDATE_TIMEOUT):
                        async for msg in ws:
                            if msg.type != aiohttp.WSMsgType.TEXT:
                                continue
                            payload = msg.json()
                            if error := payload.get("error"):
                                raise InvalidAuth(error)
                            return
                except TimeoutError:
                    # No error and no traffic yet (e.g. a small/quiet bounding
                    # box) - treat the subscription as accepted.
                    return
    except aiohttp.ClientError as err:
        raise CannotConnect from err


class AISStreamConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial (account-level) config flow for aisstream.io."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            # A world-wide box is only used here to confirm the API key is
            # accepted - the actual monitored areas are added as subentries
            # right after this step.
            try:
                await _validate_api_key(
                    user_input[CONF_API_KEY],
                    [
                        [
                            [DEFAULT_BOX_SOUTH, DEFAULT_BOX_WEST],
                            [DEFAULT_BOX_NORTH, DEFAULT_BOX_EAST],
                        ]
                    ],
                    [],
                )
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_input[CONF_API_KEY])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="AISstream.io", data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_API_KEY): str}),
            errors=errors,
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this integration."""
        return {SUBENTRY_TYPE_AREA: AreaSubentryFlowHandler}


class AreaSubentryFlowHandler(ConfigSubentryFlow):
    """Add or reconfigure a single monitored area (e.g. a harbor)."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        return await self._async_step(user_input, step_id="user")

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        subentry = self._get_reconfigure_subentry()
        return await self._async_step(
            user_input, step_id="reconfigure", current=dict(subentry.data)
        )

    async def _async_step(
        self,
        user_input: dict[str, Any] | None,
        step_id: str,
        current: dict[str, Any] | None = None,
    ) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        current = current or {}
        if isinstance(current.get(CONF_MMSI_FILTER), list):
            current = {
                **current,
                CONF_MMSI_FILTER: ", ".join(current[CONF_MMSI_FILTER]),
            }

        if user_input is not None:
            mmsi_filter = _parse_mmsi_filter(user_input.get(CONF_MMSI_FILTER, ""))
            bounding_boxes, error = _resolve_bounding_boxes(self.hass, user_input)

            if error:
                errors["base"] = error
            else:
                api_key = self._get_entry().data[CONF_API_KEY]
                try:
                    await _validate_api_key(api_key, bounding_boxes, mmsi_filter)
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except CannotConnect:
                    errors["base"] = "cannot_connect"
                else:
                    data = {**user_input, CONF_MMSI_FILTER: mmsi_filter}
                    title = _area_title(self.hass, data)
                    if step_id == "reconfigure":
                        return self.async_update_and_abort(
                            self._get_entry(),
                            self._get_reconfigure_subentry(),
                            title=title,
                            data=data,
                        )
                    return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id=step_id,
            data_schema=_area_schema(user_input or current),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect to aisstream.io."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate the API key was rejected."""
