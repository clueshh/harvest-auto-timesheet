from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import holidays
import pagerduty
from google.oauth2.service_account import Credentials
from rich.console import Console

from harvest_auto_timesheet.gcal import CalendarEvent, get_calendar_events
from harvest_auto_timesheet.harvest import Harvest
from harvest_auto_timesheet.pagerd import Incident, get_incidents
from harvest_auto_timesheet.tasks import ProjectEnum, TaskEnum
from harvest_auto_timesheet.util import (
    get_advice,
    get_joke,
    get_start_of_week,
    random_numbers_sum,
)

console = Console()

SCRUM_CEREMONY_WORDS = [
    "standup",
    "stand up",
    "sprint",
    "retro",
    "planning",
]

nz_holidays = holidays.NewZealand(prov="Auckland")  # type: ignore[attr-defined]


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
    pagerduty_client: pagerduty.RestApiV2Client,
    pagerduty_user_id: str,
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
        if event.is_all_day():
            # assuming all day events are not work related
            console.print(f"Skipping calendar event on {event.start.date_} (all day)")
            continue

        if event.status != "confirmed":
            # if the event is not confirmed, we don't want to add it to the timesheet
            console.print(
                f"Skipping calendar event on {event.start.datetime} (not confirmed)"
            )
            continue

        if event.start.datetime.date() in nz_holidays:  # type: ignore[union-attr]
            # if the event is on a public holiday,
            # we don't want to add it to the timesheet
            console.print(
                f"Skipping calendar event on {event.start.datetime} (holiday)"
            )
            continue

        _add_calendar_event(harvest=harvest, event=event)

    time_entries = harvest.get_time_entries(
        from_date=weekdays[0],
        to_date=weekdays[-1],
    )

    console.print("Filling timesheet with the remaining hours")
    for weekday in weekdays:
        if weekday in nz_holidays:
            _add_holiday(harvest=harvest, weekday=weekday)
            continue

        _fill_timesheet(
            harvest=harvest,
            time_entries=time_entries,
            weekday=weekday,
        )

    incidents = get_incidents(
        pd_client=pagerduty_client,
        user_id=pagerduty_user_id,
        since=weekdays[0],
        until=weekdays[-1],
    )
    _add_pager_duty_incidents(harvest=harvest, incidents=incidents)

    console.print("Timesheet completed successfully")


def _add_calendar_event(
    harvest: Harvest,
    event: CalendarEvent,
) -> None:
    """Add a calendar event to the timesheet."""
    assert isinstance(event.start.datetime, datetime)
    assert isinstance(event.end.datetime, datetime)

    console.print(f"Adding calendar event on {event.start.datetime}")

    spent_date = event.start.datetime.date()
    hours = (event.end.datetime - event.start.datetime).total_seconds() / 3600

    task_id = TaskEnum.INTERNAL_MEETING.value
    # TODO(CW): Remove this? The scrum ceremonies task got removed so no longer needed
    # if any(word in event.summary.lower() for word in SCRUM_CEREMONY_WORDS):
    #     task_id = TaskEnum.SCRUM_CEREMONIES.value
    # else:
    #     task_id = TaskEnum.INTERNAL_MEETING.value

    harvest.add_time_entry(
        project_id=ProjectEnum.FM_INTERNAL.value,
        task_id=task_id,
        spent_date=spent_date,
        hours=hours,
        notes=event.summary,
    )


def _add_holiday(
    harvest: Harvest,
    weekday: date,
) -> None:
    """Add a holiday to the timesheet."""
    if weekday in nz_holidays:
        console.print(f"Adding holiday on {weekday}")
        harvest.add_time_entry(
            project_id=ProjectEnum.FM_INTERNAL.value,
            task_id=TaskEnum.PUBLIC_HOLIDAY.value,
            spent_date=weekday,
            hours=8,
            notes="Public holiday",
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

    # Add a time entry for each project/task combination.
    task_entries_to_add = [
        (ProjectEnum.EYECUE_GENERAL.value, TaskEnum.ENGINEERING.value, get_joke),
        (ProjectEnum.SOC2.value, TaskEnum.ENGINEERING.value, get_advice),
        (
            ProjectEnum.VIDEO_STORAGE_PLAYBACK.value,
            TaskEnum.ENGINEERING.value,
            get_advice,
        ),
        (ProjectEnum.CAMERA_CONFIG_API.value, TaskEnum.ENGINEERING.value, get_advice),
    ]

    # Randomly distribute the remaining hours across the tasks.
    remaining_hours = 8 - hours
    hours_per_project: list[float] = random_numbers_sum(
        total_sum=remaining_hours,
        num_elements=len(task_entries_to_add),
    )

    console.print(
        f"Remaining hours to fill for {weekday}: {remaining_hours:.2f} "
        f"({len(task_entries_to_add)} tasks)"
    )

    for (
        project_id,
        task_id,
        notes_func,
    ), hours in zip(task_entries_to_add, hours_per_project, strict=True):
        console.print(
            f"Adding {hours:.2f} hours for project {project_id} "
            f"and task {task_id} on {weekday}"
        )
        _response = harvest.add_time_entry(
            project_id=project_id,
            task_id=task_id,
            spent_date=weekday,
            hours=hours,
            notes=notes_func(),
        )
        # console.print_json(data=response, indent=2)

    console.print(f"Filled {remaining_hours:.2f} hours for {weekday}")


def _add_pager_duty_incidents(
    harvest: Harvest,
    incidents: list[Incident],
) -> None:
    """Add PagerDuty incidents to the timesheet."""
    for incident in incidents:
        console.print(f"Adding PagerDuty incident {incident.id} to timesheet")

        if (duration := incident.duration) is None:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Incident {incident.id} "
                "has no duration. Skipping entry."
            )
            continue

        hours = duration.total_seconds() / 3600
        harvest.add_time_entry(
            project_id=ProjectEnum.EYECUE_GENERAL.value,
            task_id=TaskEnum.L3_ON_CALL.value,
            spent_date=incident.resolved_at.date(),
            hours=hours,
            notes=f"{incident.summary}\n{incident.html_url}",
        )
