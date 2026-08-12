"""Helpers to derive an aisstream.io bounding box from a point + radius."""
from __future__ import annotations

import math

from homeassistant.core import HomeAssistant

from .const import (
    CONF_BOX_EAST,
    CONF_BOX_NORTH,
    CONF_BOX_SOUTH,
    CONF_BOX_WEST,
    CONF_LOCATION,
    CONF_ZONE,
)

_EARTH_RADIUS_M = 6371000


def bounding_box_for_point(
    latitude: float, longitude: float, radius_m: float
) -> list[list[list[float]]]:
    """Return the smallest bounding box enclosing a circle of radius_m."""
    lat_delta = math.degrees(radius_m / _EARTH_RADIUS_M)
    lon_scale = max(math.cos(math.radians(latitude)), 1e-6)
    lon_delta = math.degrees(radius_m / (_EARTH_RADIUS_M * lon_scale))

    return [
        [
            [latitude - lat_delta, longitude - lon_delta],
            [latitude + lat_delta, longitude + lon_delta],
        ]
    ]


def bounding_box_for_zone(
    hass: HomeAssistant, entity_id: str
) -> list[list[list[float]]] | None:
    """Return the bounding box enclosing an existing HA zone's circle.

    Returns None if the zone entity does not exist or has no usable
    latitude/longitude/radius attributes.
    """
    state = hass.states.get(entity_id)
    if state is None:
        return None

    try:
        latitude = float(state.attributes["latitude"])
        longitude = float(state.attributes["longitude"])
        radius = float(state.attributes.get("radius", 100))
    except (KeyError, TypeError, ValueError):
        return None

    return bounding_box_for_point(latitude, longitude, radius)


def bounding_box_for_location(location: dict) -> list[list[list[float]]] | None:
    """Return the bounding box for a selector.LocationSelector value.

    Returns None if the location dict is missing latitude/longitude.
    """
    try:
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])
        radius = float(location.get("radius", 100))
    except (KeyError, TypeError, ValueError):
        return None

    return bounding_box_for_point(latitude, longitude, radius)


def resolve_area_box(
    hass: HomeAssistant, data: dict
) -> list[list[list[float]]] | None:
    """Resolve one area subentry's bounding box from its stored config data.

    Tries a zone, then a picked location, then falls back to the manual
    south/west/north/east fields. Returns None only if a referenced zone
    entity can't be resolved right now (e.g. not loaded yet at startup).
    """
    if zone_entity_id := data.get(CONF_ZONE):
        return bounding_box_for_zone(hass, zone_entity_id)

    if location := data.get(CONF_LOCATION):
        boxes = bounding_box_for_location(location)
        if boxes is not None:
            return boxes

    return [
        [
            [data[CONF_BOX_SOUTH], data[CONF_BOX_WEST]],
            [data[CONF_BOX_NORTH], data[CONF_BOX_EAST]],
        ]
    ]


def point_in_box(
    latitude: float, longitude: float, box: list[list[list[float]]]
) -> bool:
    """Return whether a point lies within a single aisstream-format box."""
    (south, west), (north, east) = box[0]
    return south <= latitude <= north and west <= longitude <= east
