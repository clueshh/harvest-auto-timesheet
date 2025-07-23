import json
import tempfile
from pathlib import Path

from harvest_auto_timesheet.context import Context
from tests.conftest import MockEnvVars


def test_context_defaults(
    mock_context: Context,
    mock_env_vars: MockEnvVars,
) -> None:
    assert mock_context.harvest_account_id == mock_env_vars["HARVEST_ACCOUNT_ID"]
    assert mock_context.harvest_access_token == mock_env_vars["HARVEST_ACCESS_TOKEN"]
    assert mock_context.calendar_id == mock_env_vars["CALENDAR_ID"]
    assert mock_context.service_account_file == mock_env_vars["SERVICE_ACCOUNT_FILE"]
    assert (
        mock_context.service_account_json_b64
        == (mock_env_vars["SERVICE_ACCOUNT_JSON_B64"])
    )
    assert mock_context.pagerduty_user_id == mock_env_vars["PAGERDUTY_USER_ID"]
    assert mock_context.pagerduty_api_key == mock_env_vars["PAGERDUTY_API_TOKEN"]


def test_context_from_service_account_file(
    mock_env_vars: MockEnvVars,
    mock_service_account: dict[str, str],
) -> None:
    with tempfile.NamedTemporaryFile() as tmp:
        Path(tmp.name).write_text(json.dumps(mock_service_account), encoding="utf-8")

        ctx = Context(
            harvest_account_id=mock_env_vars["HARVEST_ACCOUNT_ID"],
            harvest_access_token=mock_env_vars["HARVEST_ACCESS_TOKEN"],
            calendar_id=mock_env_vars["CALENDAR_ID"],
            service_account_file=mock_env_vars["SERVICE_ACCOUNT_FILE"],
            pagerduty_user_id=mock_env_vars["PAGERDUTY_USER_ID"],
            pagerduty_api_key=mock_env_vars["PAGERDUTY_API_TOKEN"],
        )

    assert ctx.harvest_account_id == mock_env_vars["HARVEST_ACCOUNT_ID"]
    assert ctx.harvest_access_token == mock_env_vars["HARVEST_ACCESS_TOKEN"]
    assert ctx.calendar_id == mock_env_vars["CALENDAR_ID"]
    assert ctx.service_account_file == mock_env_vars["SERVICE_ACCOUNT_FILE"]
    assert ctx.service_account_json_b64 is None
    assert ctx.pagerduty_user_id == mock_env_vars["PAGERDUTY_USER_ID"]
    assert ctx.pagerduty_api_key == mock_env_vars["PAGERDUTY_API_TOKEN"]
