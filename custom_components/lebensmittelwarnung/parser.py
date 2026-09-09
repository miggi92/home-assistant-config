"""Zerlegt das description-HTML einer Meldung in einzelne Felder."""

from __future__ import annotations

import calendar
from datetime import UTC, datetime
import html
import re
from typing import Any

from .const import DUMMY_IMAGE_MARKER, FIELDS

# "<b>Label:</b> Wert" bis zum nächsten Tag. Die Werte enthalten selbst keine
# Tags, deshalb reicht [^<]*. "Bildquelle" ist das einzige Feld ohne Doppelpunkt
# im b-Tag, daher das optionale ":".
_FIELD_RE = re.compile(r"<b>%s:?</b>([^<]*)")
_IMG_RE = re.compile(r'<img[^>]*src="([^"]+)"')


def _clean(value: str) -> str:
    """Entities auflösen, geschützte Leerzeichen normalisieren, trimmen."""
    return html.unescape(value).replace("\xa0", " ").strip()


def extract_field(description: str, label: str) -> str | None:
    """Einzelnes Feld aus dem description-HTML holen."""
    match = _FIELD_RE.pattern % re.escape(label)
    found = re.search(match, description)
    if not found:
        return None
    value = _clean(found.group(1))
    return value or None


def extract_images(description: str) -> list[str]:
    """Alle Bild-URLs einer Meldung, in der Reihenfolge des Auftretens.

    Der Query-String muss erhalten bleiben: ohne "?__blob=normal" liefert der
    Server eine HTML-Seite statt der Bilddatei.
    """
    return [html.unescape(url) for url in _IMG_RE.findall(description)]


def parse_entry(entry: Any) -> dict[str, Any]:
    """Einen feedparser-Eintrag in ein flaches Dict überführen."""
    description: str = entry.get("description") or ""
    images = extract_images(description)

    # published ist im Feed RFC 822 ("Fri, 4 Sep 2026 15:00:00 +0200").
    # feedparser liefert daraus published_parsed als struct_time in UTC.
    published: datetime | None = None
    if parsed_time := entry.get("published_parsed"):
        published = datetime.fromtimestamp(calendar.timegm(parsed_time), tz=UTC)

    data: dict[str, Any] = {
        "title": _clean(entry.get("title") or ""),
        "link": entry.get("link"),
        "guid": entry.get("id") or entry.get("link"),
        "published": published,
        "images": images,
        "image": images[0] if images else None,
        "has_real_image": bool(images) and DUMMY_IMAGE_MARKER not in images[0],
    }

    for label, key in FIELDS.items():
        data[key] = extract_field(description, label)

    # "Grund der Meldung" kann mehrere kommagetrennte Gründe enthalten,
    # z.B. "Gesundheitsschädliche Substanz, Rückstände und Kontaminanten".
    reason = data.get("reason")
    data["reasons"] = (
        [part.strip() for part in reason.split(",") if part.strip()] if reason else []
    )

    return data