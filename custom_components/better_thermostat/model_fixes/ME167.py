"""Model quirks for ME167 Zigbee thermostats.

Includes device-specific offsets and behavior adaptations required for certain
ME167 based devices.
"""

import logging

_LOGGER = logging.getLogger(__name__)


def fix_local_calibration(self, entity_id, offset):
    """Adjust the local calibration offset for ME167 devices.

    Just invert the given offset for this model, as they seem to report it in reverse compared to other devices.
    """
    return -offset


def fix_target_temperature_calibration(self, entity_id, temperature):
    """Return the given target temperature unchanged."""
    return temperature


async def override_set_hvac_mode(self, entity_id, hvac_mode):
    """No HVAC mode override for ME167 devices.

    Return False to indicate no custom handling and let the adapter handle
    normal behavior.
    """
    return False


async def override_set_temperature(self, entity_id, temperature):
    """No set_temperature override for ME167 devices.

    Return False to indicate the adapter should use the default set_temperature
    implementation.
    """
    return False
