import base64
import json
import os
from dataclasses import dataclass, field

import pagerduty
from google.oauth2.service_account import Credentials

from harvest_auto_timesheet.harvest import Harvest


@dataclass
class Context:
    harvest_account_id: str = field(
        default_factory=lambda: os.environ["HARVEST_ACCOUNT_ID"]
    )
    harvest_access_token: str = field(
        default_factory=lambda: os.environ["HARVEST_ACCESS_TOKEN"]
    )

    calendar_id: str = field(default_factory=lambda: os.environ["CALENDAR_ID"])
    service_account_file: str = field(
        default_factory=lambda: os.getenv(
            "SERVICE_ACCOUNT_FILE", "service-account.json"
        )
    )
    service_account_json_b64: str | None = field(
        default_factory=lambda: os.getenv("SERVICE_ACCOUNT_JSON_B64")
    )

    pagerduty_user_id: str = field(
        default_factory=lambda: os.environ["PAGERDUTY_USER_ID"]
    )
    pagerduty_api_key: str = field(
        default_factory=lambda: os.environ["PAGERDUTY_API_TOKEN"]
    )

    credentials: Credentials = field(init=False)
    harvest: Harvest = field(init=False)
    pagerduty_client: pagerduty.RestApiV2Client = field(init=False)

    def __post_init__(self) -> None:
        scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
        # if the service_account_json_b64 is set use that instead of the file
        if self.service_account_json_b64:
            service_account_json = json.loads(
                base64.b64decode(self.service_account_json_b64)
            )
            self.credentials = Credentials.from_service_account_info(  # type: ignore[no-untyped-call]
                service_account_json,
                scopes=scopes,
            )
        else:
            self.credentials = Credentials.from_service_account_file(  # type: ignore[no-untyped-call]
                self.service_account_file,
                scopes=scopes,
            )

        self.harvest = Harvest(
            harvest_account_id=self.harvest_account_id,
            harvest_access_token=self.harvest_access_token,
        )

        self.pagerduty_client = pagerduty.RestApiV2Client(
            api_key=self.pagerduty_api_key,
        )
