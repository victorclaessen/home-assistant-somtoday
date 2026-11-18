"""Pupil details beyond the roster, such as the class (stamgroep).

The pupil portal reads ``/rest/v1/leerlingen/{id}?additional=stamgroep``; the
class then arrives as ``additionalObjects.stamgroep``, e.g. ``"1B"``.
"""

from __future__ import annotations

from typing import Any


def class_name(pupil: Any) -> str | None:
    """Class from /leerlingen/{id}?additional=stamgroep; None when there is none.

    A wrong shape raises, so a broken response is never published as "no class".
    """
    if not isinstance(pupil, dict):
        raise TypeError("pupil is not an object")
    extra = pupil.get("additionalObjects") or {}
    if not isinstance(extra, dict):
        raise TypeError("additionalObjects is not an object")
    value = extra.get("stamgroep")
    if value is None:
        return None
    if isinstance(value, dict):  # tolerate an object with a name
        value = value.get("naam")
    if not isinstance(value, str):
        raise TypeError("stamgroep is not text")
    return value.strip() or None
