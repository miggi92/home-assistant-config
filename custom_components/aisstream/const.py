"""Constants for the aisstream.io integration."""

DOMAIN = "aisstream"

AISSTREAM_WS_URL = "wss://stream.aisstream.io/v0/stream"

CONF_API_KEY = "api_key"
CONF_BOX_SOUTH = "box_south"
CONF_BOX_WEST = "box_west"
CONF_BOX_NORTH = "box_north"
CONF_BOX_EAST = "box_east"
CONF_MMSI_FILTER = "mmsi_filter"
CONF_ZONE = "zone_entity_id"
CONF_LOCATION = "location"

DEFAULT_BOX_SOUTH = -90.0
DEFAULT_BOX_WEST = -180.0
DEFAULT_BOX_NORTH = 90.0
DEFAULT_BOX_EAST = 180.0

RECONNECT_DELAY_MIN = 5
RECONNECT_DELAY_MAX = 300

SIGNAL_NEW_SHIP = f"{DOMAIN}_new_ship"
SIGNAL_SHIP_UPDATE = f"{DOMAIN}_ship_update"

# How long a vessel is still considered "present" after its last position
# report, and how often the area count sensor re-evaluates presence.
PRESENCE_TIMEOUT_MINUTES = 20
PRESENCE_RECHECK_MINUTES = 2

# AIS navigational status codes (ITU-R M.1371)
NAVIGATIONAL_STATUS = {
    0: "Under way using engine",
    1: "At anchor",
    2: "Not under command",
    3: "Restricted manoeuvrability",
    4: "Constrained by her draught",
    5: "Moored",
    6: "Aground",
    7: "Engaged in fishing",
    8: "Under way sailing",
    9: "Reserved (HSC)",
    10: "Reserved (WIG)",
    11: "Power-driven vessel towing astern",
    12: "Power-driven vessel pushing ahead",
    13: "Reserved",
    14: "AIS-SART / MOB / EPIRB",
    15: "Undefined",
}
