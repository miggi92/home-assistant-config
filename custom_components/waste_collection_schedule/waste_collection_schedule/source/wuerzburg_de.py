import datetime
import logging

import requests
from bs4 import BeautifulSoup
from waste_collection_schedule import Collection  # type: ignore[attr-defined]
from waste_collection_schedule.exceptions import (
    SourceArgumentExceptionMultiple,
    SourceArgumentNotFoundWithSuggestions,
)

LOGGER = logging.getLogger(__name__)
TITLE = "Abfallkalender Würzburg (deprecated)"
DESCRIPTION = "Deprecated: Use the ICS source instead. Source for waste collection in the city of Würzburg, Germany."
URL = "https://www.wuerzburg.de"
TEST_CASES = {
    "District only": {"district": "Altstadt"},
    "Street only": {"street": "Juliuspromenade"},
    "District + Street": {"district": "Altstadt", "street": "Juliuspromenade"},
    "District + Street diff": {"district": "Altstadt", "street": "Oberer Burgweg"},
}

API_URL = "https://www.wuerzburg.de/themen/umwelt-klima/vorsorge-entsorgung/abfallkalender/32208.Abfallkalender.html"
HEADERS = {"user-agent": "Mozilla/5.0 (xxxx Windows NT 10.0; Win64; x64)"}


PARAM_TRANSLATIONS = {
    "de": {
        "district": "Stadtteil",
        "street": "Straße",
    }
}


class Source:
    def __init__(self, district: str | None = None, street: str | None = None):
        self._district = district
        self._street = street
        self._district_id = None

    @staticmethod
    def map_district_id(district: str | None = None, street: str | None = None):
        """Map `street` or `district` to `district_id`, giving priority to `street`.

        Parameters must exactly be the same as visible in dropdowns on `URL`.
        """
        if not district and not street:
            raise ValueError("One of ['district', 'street'] is required.")

        r = requests.get(API_URL, headers=HEADERS)
        r.raise_for_status()
        selects = BeautifulSoup(r.content, "html.parser").body.find_all("select")

        if street:
            strlist = next(iter([s for s in selects if s["id"] == "strlist"]))
            strdict = {
                option.text: option.attrs["value"]
                for option in strlist.children
                if hasattr(option, "attrs") and "value" in option.attrs
            }

            hasattr(strlist.contents[2], "attr")

            try:
                return strdict[street]
            except KeyError:
                raise SourceArgumentNotFoundWithSuggestions(
                    "street", street, strdict.keys()
                )

        if district:
            reglist = next(iter([s for s in selects if s["id"] == "reglist"]))
            regdict = {
                option.text: option.attrs["value"]
                for option in reglist.children
                if hasattr(option, "attrs") and "value" in option.attrs
            }

            try:
                return regdict[district]
            except KeyError:
                raise SourceArgumentNotFoundWithSuggestions(
                    "district", district, regdict.keys()
                )

    def fetch(self):
        LOGGER.warning(
            "The Abfallkalender Würzburg source is deprecated and might not work with all addresses anymore."
            " Please use the ICS source instead: https://github.com/mampfes/hacs_waste_collection_schedule/blob/master/doc/ics/wuerzburg_de.md"
        )

        # Get & parse full HTML only on first call to fetch() to map district or street to district_id
        if not self._district_id:
            self._district_id = self.map_district_id(self._district, self._street)

        if not self._district_id:
            raise ValueError("'_district_id' is not set!")

        now = datetime.datetime.now().date()

        r = requests.get(
            API_URL,
            headers=HEADERS,
            params={
                "_func": "evList",
                "_mod": "events",
                "ev[start]": str(now),
                "ev[end]": str(now + datetime.timedelta(days=365)),
                "ev[addr]": self._district_id,
            },
        )
        r.raise_for_status()

        entries = []
        for event in r.json()["contents"].values():
            entries.append(
                Collection(
                    datetime.datetime.fromisoformat(event["start"]).date(),
                    event["title"],
                    picture=event.get("thumb", {}).get("url"),
                )
            )

        return entries
