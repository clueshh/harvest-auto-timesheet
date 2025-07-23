from datetime import date
from http import HTTPStatus

import httpx

from harvest_auto_timesheet.harvest import Harvest
from harvest_auto_timesheet.tasks import ProjectEnum, TaskEnum


def test_harvest_get_user(mock_harvest: Harvest) -> None:
    test_client = httpx.Client(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(HTTPStatus.OK, json={"hey": "it's me"})
        )
    )

    mock_harvest.client = test_client
    assert mock_harvest.get_user() == {"hey": "it's me"}


def test_harvest_get_time_entries(mock_harvest: Harvest) -> None:
    test_client = httpx.Client(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(HTTPStatus.OK, json={"time_entries": []})
        )
    )

    mock_harvest.client = test_client
    assert (
        mock_harvest.get_time_entries(
            from_date=date(year=2025, month=1, day=1),
            to_date=date(year=2025, month=1, day=2),
        )
        == []
    )


def test_harvest_add_time_entry(mock_harvest: Harvest) -> None:
    test_client = httpx.Client(
        transport=httpx.MockTransport(
            lambda _: httpx.Response(
                HTTPStatus.CREATED, json={"statusCode": HTTPStatus.CREATED}
            )
        )
    )

    mock_harvest.client = test_client
    response = mock_harvest.add_time_entry(
        project_id=ProjectEnum.EYECUE_GENERAL,
        task_id=TaskEnum.ENGINEERING,
        spent_date=date(year=2025, month=1, day=1),
        hours=8,
        notes="tada",
    )
    assert response == {"statusCode": HTTPStatus.CREATED}


def test_harvest_delete_time_entry(mock_harvest: Harvest) -> None:
    test_client = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(HTTPStatus.NO_CONTENT))
    )

    mock_harvest.client = test_client
    mock_harvest.delete_time_entry(time_entry_id=123456)
