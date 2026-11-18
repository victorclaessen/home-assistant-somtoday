import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from custom_components.somtoday.api import SomtodayClient
from custom_components.somtoday.pupil import class_name
from custom_components.somtoday.sensor import SomtodayClassSensor

PUPIL = {
    "links": [{"id": 31568159740967, "rel": "self", "type": "leerling.RLeerling"}],
    "additionalObjects": {"stamgroep": "1B"},
    "roepnaam": "Bob", "achternaam": "de Ruyter",
}


def test_class_from_additional_objects():
    assert class_name(PUPIL) == "1B"
    assert class_name({**PUPIL, "additionalObjects": {"stamgroep": " 2A "}}) == "2A"
    assert class_name({**PUPIL, "additionalObjects": {"stamgroep": {"naam": "3C"}}}) == "3C"


def test_no_class_is_none():
    assert class_name({**PUPIL, "additionalObjects": {}}) is None
    assert class_name({**PUPIL, "additionalObjects": {"stamgroep": ""}}) is None
    assert class_name({"links": []}) is None


def test_broken_shape_raises_instead_of_meaning_no_class():
    for bad in (None, [], {"additionalObjects": ["1B"]}, {"additionalObjects": {"stamgroep": 12}}):
        with pytest.raises(TypeError):
            class_name(bad)


def test_client_requests_the_portal_url():
    client = SomtodayClient.__new__(SomtodayClient)
    client._get = AsyncMock(return_value=PUPIL)
    assert asyncio.run(client.student_class("31568159740967")) == "1B"
    client._get.assert_awaited_once_with(
        "/rest/v1/leerlingen/31568159740967", params=[("additional", "stamgroep")]
    )


def _sensor(data):
    sensor = SomtodayClassSensor.__new__(SomtodayClassSensor)
    sensor.coordinator = SimpleNamespace(data=data, last_update_success=True)
    sensor.student = "31568159740967"
    return sensor


def test_sensor_shows_class_and_is_unavailable_without_one():
    assert _sensor({"class_by_student": {"31568159740967": "1B"}}).native_value == "1B"
    assert _sensor({"class_by_student": {"31568159740967": None}}).available is False
    assert _sensor({}).available is False
