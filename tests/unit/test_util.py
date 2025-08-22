from datetime import UTC, date, datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import httpx
import pytest

from harvest_auto_timesheet.util import (
    get_end_of_week,
    get_joke,
    get_start_of_week,
    random_numbers_sum,
)


def test_get_end_of_week() -> None:
    start_datetime = datetime(year=2024, month=12, day=30, tzinfo=UTC)
    start = start_datetime.date()
    start = date(year=2024, month=12, day=30)
    midweek = date(year=2025, month=1, day=1)
    end = date(year=2025, month=1, day=5)

    assert get_end_of_week(start) == end
    assert get_end_of_week(midweek) == end
    assert get_end_of_week(end) == end

    with patch("harvest_auto_timesheet.util.datetime") as mock_datetime:
        mock_datetime.now.return_value = start_datetime
        assert get_end_of_week() == end


def test_get_start_of_week() -> None:
    start_datetime = datetime(year=2024, month=12, day=30, tzinfo=UTC)
    start = start_datetime.date()
    midweek = date(year=2025, month=1, day=1)
    end = date(year=2025, month=1, day=5)

    assert get_start_of_week(start) == start
    assert get_start_of_week(midweek) == start
    assert get_start_of_week(end) == start

    with patch("harvest_auto_timesheet.util.datetime") as mock_datetime:
        mock_datetime.now.return_value = start_datetime
        assert get_start_of_week() == start


def test_get_joke() -> None:
    single_response = httpx.Response(
        HTTPStatus.OK,
        json={
            "type": "single",
            "joke": "random joke",
        },
        request=MagicMock(),
    )

    with patch("harvest_auto_timesheet.util.Client.get", return_value=single_response):
        assert get_joke() == "random joke"

    multi_response = httpx.Response(
        HTTPStatus.OK,
        json={
            "type": "not single",
            "setup": "some setup",
            "delivery": "some delivery",
        },
        request=MagicMock(),
    )

    with patch("harvest_auto_timesheet.util.Client.get", return_value=multi_response):
        assert get_joke() == "some setup some delivery"


def test_random_numbers_sum() -> None:
    assert random_numbers_sum(10, 2, seed=42) == [1.867826, 8.132174]
    assert random_numbers_sum(10, 3, seed=42) == [0.419611, 1.448215, 8.132174]

    for _ in range(10_000):
        numbers = random_numbers_sum(10, 5)
        assert len(numbers) == 5
        assert sum(numbers) == pytest.approx(10, rel=1e-6)
