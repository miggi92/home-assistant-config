"""Einzelne Sensoren für die jüngste Meldung, je Feld eine eigene Datei."""

from __future__ import annotations

from .batch import LmwBatchSensor
from .count import LmwCountSensor
from .expiry import LmwExpirySensor
from .latest import LmwLatestSensor
from .manufacturer import LmwManufacturerSensor
from .previous import LmwPreviousSensor
from .product import LmwProductSensor
from .published import LmwPublishedSensor
from .reason import LmwReasonSensor

SENSOR_CLASSES = (
    LmwLatestSensor,
    LmwPreviousSensor,
    LmwReasonSensor,
    LmwBatchSensor,
    LmwExpirySensor,
    LmwProductSensor,
    LmwManufacturerSensor,
    LmwPublishedSensor,
    LmwCountSensor,
)
