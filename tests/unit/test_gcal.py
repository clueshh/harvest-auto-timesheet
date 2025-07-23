from datetime import UTC, date, datetime
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from harvest_auto_timesheet.gcal import CalendarEvent, DateTime, get_calendar_events


def test_get_calendar_events() -> None:
    event = CalendarEvent(
        status="some status",
        summary="some summary",
        start=DateTime(datetime=datetime(year=2025, month=1, day=1, tzinfo=UTC)),  # type: ignore[call-arg]
        end=DateTime(datetime=datetime(year=2025, month=1, day=2, tzinfo=UTC)),  # type: ignore[call-arg]
    )
    items = [event.model_dump(mode="json")]

    with patch("harvest_auto_timesheet.gcal.build") as mock_build:
        mock_build.return_value.events.return_value.list.return_value.execute.return_value = {  # noqa: E501
            "items": items
        }

        events = get_calendar_events(
            creds=MagicMock(),
            calendar_id="calendar_id",
            time_min=datetime.now(tz=UTC),
            time_max=datetime.now(tz=UTC),
            timezone=ZoneInfo("UTC"),
        )

    assert events == [event]


def test_calendar_event() -> None:
    event = CalendarEvent(
        status="some status",
        summary="some summary",
        start=DateTime(date=date(year=2025, month=1, day=1)),  # type: ignore[call-arg]
        end=DateTime(date=date(year=2025, month=1, day=2)),  # type: ignore[call-arg]
    )
    assert event.is_all_day()

    event.start.datetime = datetime(year=2025, month=1, day=2, tzinfo=UTC)
    assert not event.is_all_day()
