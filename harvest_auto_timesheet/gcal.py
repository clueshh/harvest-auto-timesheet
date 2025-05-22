from datetime import date, datetime
from zoneinfo import ZoneInfo

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pydantic import AwareDatetime, BaseModel, Field, TypeAdapter


class DateTime(BaseModel):
    date_: date | None = Field(None, alias="date")
    datetime: AwareDatetime | None = Field(None, alias="dateTime")


class CalendarEvent(BaseModel):
    status: str
    summary: str
    start: DateTime
    end: DateTime

    def is_all_day(self) -> bool:
        """Check if the event is an all-day event."""
        return self.start.date_ is not None and self.start.datetime is None


def get_calendar_events(
    creds: Credentials,
    calendar_id: str,
    time_min: datetime,
    time_max: datetime,
    timezone: ZoneInfo | None = None,
) -> list[CalendarEvent]:
    """Get events from Google Calendar.

    Args:
        creds (Credentials): The credentials to use for the Google Calendar API.
        calendar_id (str): The ID of the calendar to get events from.
        time_min (datetime): The minimum time for the events to be returned.
        time_max (datetime): The maximum time for the events to be returned.
        timezone (ZoneInfo | None): The timezone used in the response. Defaults to UTC.

    Returns:
        list[dict]: A list of events.

    """
    tz = timezone or ZoneInfo("UTC")

    service = build("calendar", "v3", credentials=creds)

    events_result = (
        service.events()
        .list(
            calendarId=calendar_id,
            eventTypes=["default"],
            singleEvents=True,
            orderBy="startTime",
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            timeZone=str(tz),
        )
        .execute()
    )

    events = events_result.get("items", [])
    adapter = TypeAdapter(list[CalendarEvent])

    return adapter.validate_python(events)
