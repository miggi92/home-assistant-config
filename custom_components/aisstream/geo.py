"""Helpers to derive an aisstream.io bounding box from a point + radius."""
from __future__ import annotations

import math

from homeassistant.core import HomeAssistant

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
