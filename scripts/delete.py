"""Helper script to delete all time entries for the current week."""

from dotenv import load_dotenv
from rich.console import Console

from harvest_auto_timesheet.context import Context
from harvest_auto_timesheet.util import get_end_of_week, get_start_of_week

load_dotenv(override=True)

console = Console()
context = Context()
harvest = context.harvest

response = harvest.get_time_entries(
    from_date=get_start_of_week(),
    to_date=get_end_of_week(),
)

for entry in response:
    harvest.delete_time_entry(
        time_entry_id=entry["id"],
    )
