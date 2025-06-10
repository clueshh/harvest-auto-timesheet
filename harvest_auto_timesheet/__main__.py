from dotenv import load_dotenv

from harvest_auto_timesheet.context import Context
from harvest_auto_timesheet.schedule import run_schedule

load_dotenv(override=True)

context = Context()

run_schedule(
    harvest=context.harvest,
    credentials=context.credentials,
    calendar_id=context.calendar_id,
    pagerduty_client=context.pagerduty_client,
    pagerduty_user_id=context.pagerduty_user_id,
)
