"""Helper script to delete all time entries for the current week."""

from dotenv import load_dotenv
from rich.console import Console

from harvest_auto_timesheet.context import Context
from harvest_auto_timesheet.util import get_end_of_week, get_start_of_week

load_dotenv(override=True)

console = Console()
context = Context()
harvest = context.harvest


def main() -> None:
    response = harvest.get_time_entries(
        from_date=get_start_of_week(),
        to_date=get_end_of_week(),
    )

    if len(response) == 0:
        console.print("No time entries found for the current week.")
        return

    console.print(f"Deleting {len(response)} time entries for the current week")
    for entry in response:
        console.print(f"Deleting time entry {entry['id']} for {entry['spent_date']}")
        harvest.delete_time_entry(
            time_entry_id=entry["id"],
        )

    console.print("All time entries for the current week have been deleted.")


if __name__ == "__main__":
    main()
