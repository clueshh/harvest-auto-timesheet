from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from rich.console import Console

from harvest_auto_timesheet.gcal import CalendarEvent, get_calendar_events
from harvest_auto_timesheet.harvest import Harvest
from harvest_auto_timesheet.tasks import ProjectEnum, TaskEnum
from harvest_auto_timesheet.util import get_joke, get_start_of_week

load_dotenv(override=True)

console = Console()


SCRUM_CEREMONY_WORDS = [
    "standup",
    "stand up",
    "sprint",
    "retro",
    "planning",
]


def _get_weekdays(tz: ZoneInfo | None = None) -> list[date]:
    """Get the previous 5 working days (Monday to Friday)."""
    tzone = tz or UTC
    today = datetime.now(tz=tzone).date()

    # Get the start of the week (Monday)
    start_of_week = get_start_of_week(date_=today)
    return [start_of_week + timedelta(days=i) for i in range(5)]  # Monday to Friday


def run_schedule(
    harvest: Harvest,
    credentials: Credentials,
    calendar_id: str,
) -> None:
    """Run the schedule for the week."""
    console.print("Running schedule...")

    tz = ZoneInfo("Pacific/Auckland")
    weekdays = _get_weekdays(tz)  # get the previous 5 working days

    time_min = datetime.combine(weekdays[0], time(hour=0, minute=0)).replace(tzinfo=tz)
    time_max = datetime.combine(weekdays[-1], time(hour=23, minute=59)).replace(
        tzinfo=tz
    )

    calendar_events = get_calendar_events(
        creds=credentials,
        calendar_id=calendar_id,
        time_min=time_min,
        time_max=time_max,
        timezone=tz,
    )
    console.print(f"Adding {len(calendar_events)} calendar events to the timesheet")
    for event in calendar_events:
        _add_calendar_event(harvest=harvest, event=event)

    time_entries = harvest.get_time_entries(
        from_date=weekdays[0],
        to_date=weekdays[-1],
    )

    console.print("Filling timesheet with the remaining hours")
    for weekday in weekdays:
        _fill_timesheet(
            harvest=harvest,
            time_entries=time_entries,
            weekday=weekday,
        )


def _add_calendar_event(
    harvest: Harvest,
    event: CalendarEvent,
) -> None:
    """Add a calendar event to the timesheet."""
    if event.is_all_day():
        # assuming all day events are not work related
        return

    if event.status != "confirmed":
        # if the event is not confirmed, we don't want to add it to the timesheet
        return

    assert isinstance(event.start.datetime, datetime)
    assert isinstance(event.end.datetime, datetime)

    console.print(f"Adding calendar event on {event.start.datetime}")

    spent_date = event.start.datetime.date()
    hours = (event.end.datetime - event.start.datetime).total_seconds() / 3600

    if any(word in event.summary.lower() for word in SCRUM_CEREMONY_WORDS):
        task_id = TaskEnum.SCRUM_CEREMONIES.value
    else:
        task_id = TaskEnum.INTERNAL_MEETING.value

    harvest.add_time_entry(
        project_id=ProjectEnum.FM_INTERNAL.value,
        task_id=task_id,
        spent_date=spent_date,
        hours=hours,
        notes=event.summary,
    )


def _fill_timesheet(
    harvest: Harvest,
    time_entries: list[dict[str, Any]],
    weekday: date,
) -> None:
    """Fill the timesheet with the remaining hours for the day."""
    time_entries_for_day = [
        entry for entry in time_entries if entry["spent_date"] == weekday.isoformat()
    ]
    hours = sum(entry["hours"] for entry in time_entries_for_day)

    if hours >= 8:  # noqa: PLR2004
        console.print(f"Already worked 8 hours on {weekday}")
        return

    remaining_hours = 8 - hours
    _response = harvest.add_time_entry(
        project_id=ProjectEnum.EYECUE_GENERAL.value,
        task_id=TaskEnum.ENGINEERING.value,
        spent_date=weekday,
        hours=remaining_hours,
        notes=get_joke(),
    )
    # console.print_json(data=response, indent=2)
    console.print(f"Time entry added successfully for {weekday}")
