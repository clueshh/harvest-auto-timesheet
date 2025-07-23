import base64
import json
from pathlib import Path
from typing import TypedDict
from unittest.mock import MagicMock

import pytest

from harvest_auto_timesheet.context import Context
from harvest_auto_timesheet.harvest import Harvest


class MockEnvVars(TypedDict):
    HARVEST_ACCOUNT_ID: str
    HARVEST_ACCESS_TOKEN: str
    CALENDAR_ID: str
    SERVICE_ACCOUNT_FILE: str
    SERVICE_ACCOUNT_JSON_B64: str
    PAGERDUTY_USER_ID: str
    PAGERDUTY_API_TOKEN: str


@pytest.fixture
def mock_service_account() -> dict[str, str]:
    private_key = Path("tests/data_files/id_rsa").read_text(encoding="utf-8")

    return {
        "type": "service_account",
        "project_id": "project key",
        "private_key_id": "private key id",
        "private_key": private_key,
        "client_email": "user@email.com",
        "client_id": "client_id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/",
        "universe_domain": "googleapis.com",
    }


@pytest.fixture
def mock_service_account_json_b64(mock_service_account: dict[str, str]) -> str:
    return base64.b64encode(json.dumps(mock_service_account).encode("utf-8")).decode(
        "utf-8"
    )


@pytest.fixture
def mock_env_vars(mock_service_account_json_b64: str) -> MockEnvVars:
    return {
        "HARVEST_ACCOUNT_ID": "1234567",
        "HARVEST_ACCESS_TOKEN": "long string",
        "CALENDAR_ID": "user@email.com",
        "SERVICE_ACCOUNT_FILE": "service-account.json",
        "SERVICE_ACCOUNT_JSON_B64": mock_service_account_json_b64,
        "PAGERDUTY_USER_ID": "1234567",
        "PAGERDUTY_API_TOKEN": "long string",
    }


@pytest.fixture
def mock_harvest(mock_env_vars: MockEnvVars) -> Harvest:
    harvest = Harvest(
        harvest_account_id=mock_env_vars["HARVEST_ACCOUNT_ID"],
        harvest_access_token=mock_env_vars["HARVEST_ACCESS_TOKEN"],
    )
    harvest.client = MagicMock()
    return harvest


@pytest.fixture
def mock_context(
    mock_env_vars: MockEnvVars,
    mock_harvest: Harvest,
) -> Context:
    ctx = Context(
        harvest_account_id=mock_env_vars["HARVEST_ACCOUNT_ID"],
        harvest_access_token=mock_env_vars["HARVEST_ACCESS_TOKEN"],
        calendar_id=mock_env_vars["CALENDAR_ID"],
        service_account_file=mock_env_vars["SERVICE_ACCOUNT_FILE"],
        service_account_json_b64=mock_env_vars["SERVICE_ACCOUNT_JSON_B64"],
        pagerduty_user_id=mock_env_vars["PAGERDUTY_USER_ID"],
        pagerduty_api_key=mock_env_vars["PAGERDUTY_API_TOKEN"],
    )

    ctx.harvest = mock_harvest
    ctx.pagerduty_client = MagicMock()

    return ctx
