"""Konstanten für die Lebensmittelwarnung-Integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "lebensmittelwarnung"

CONF_STATE: Final = "bundesland"
CONF_TYPE: Final = "meldungsart"

DEFAULT_SCAN_INTERVAL: Final = 3600  # Der Feed setzt ttl=60 (Minuten).

FEED_URL: Final = (
    "https://www.lebensmittelwarnung.de/___LMW-Redaktion/RSSNewsfeed/"
    "Functions/RssFeeds/rssnewsfeed_Alle_DE.xml?nn=314268"
)

# Ein Browser-User-Agent ist hier keine Kosmetik: der Government Site Builder
# hinter lebensmittelwarnung.de bricht Anfragen mit dem aiohttp-Default
# sporadisch mit "Server disconnected" ab.
USER_AGENT: Final = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)

# Schlüssel im Feed-URL -> Anzeigename
STATES: Final[dict[str, str]] = {
    "": "Alle Bundesländer",
    "badenwuerttemberg": "Baden-Württemberg",
    "bayern": "Bayern",
    "berlin": "Berlin",
    "brandenburg": "Brandenburg",
    "bremen": "Bremen",
    "hamburg": "Hamburg",
    "hessen": "Hessen",
    "mecklenburgvorpommern": "Mecklenburg-Vorpommern",
    "niedersachsen": "Niedersachsen",
    "nordrheinwestfalen": "Nordrhein-Westfalen",
    "rheinlandpfalz": "Rheinland-Pfalz",
    "saarland": "Saarland",
    "sachsen": "Sachsen",
    "sachsenanhalt": "Sachsen-Anhalt",
    "schleswigholstein": "Schleswig-Holstein",
    "thueringen": "Thüringen",
}

# Schlüssel im Feed-URL -> Anzeigename
TYPES: Final[dict[str, str]] = {
    "": "Alle Meldungsarten",
    "lebensmittel": "Lebensmittel",
    "kosmetischemittel": "Kosmetische Mittel",
    "bedarfsgegenstaende": "Bedarfsgegenstände",
    "babyundkinderprodukte": "Baby- und Kinderprodukte",
    "mittelzumtaetowieren": "Mittel zum Tätowieren",
}

# Feldname im description-HTML -> interner Schlüssel.
# Die Beschriftungen stehen im Feed als "<b>Label:</b> Wert<br/>".
FIELDS: Final[dict[str, str]] = {
    "Grund der Meldung": "reason",
    "Chargennummer / Los-Kennzeichnung": "batch",
    "Haltbarkeit": "expiry",
    "Produktbezeichnung/ -beschreibung": "product",
    "Verpackungseinheit": "package",
    "Hersteller / Inverkehrbringer": "manufacturer",
    "Kontakt": "contact",
    "Betroffene Bundesländer nach derzeitigem Stand": "states",
}

# Platzhaltergrafik der Seite, wenn kein echtes Produktfoto vorliegt.
DUMMY_IMAGE_MARKER: Final = "Bilddummy"