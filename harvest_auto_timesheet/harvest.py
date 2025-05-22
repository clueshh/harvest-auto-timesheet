from datetime import date
from typing import Any

import httpx


class Harvest:
    def __init__(self, harvest_account_id: str, harvest_access_token: str) -> None:
        self.harvest_account_id = harvest_account_id
        self.harvest_access_token = harvest_access_token
        self.client = httpx.Client(
            headers={
                "Authorization": f"Bearer {self.harvest_access_token}",
                "Harvest-Account-ID": self.harvest_account_id,
            }
        )

    def get_user(self) -> dict[str, Any]:
        """Get the user information from Harvest API.

        Returns:
            dict: User information.

        """
        url = "https://api.harvestapp.com/v2/users/me"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def get_time_entries(
        self,
        from_date: date,
        to_date: date,
    ) -> list[dict[str, Any]]:
        """Get time entries from Harvest API.

        Args:
            from_date (date): The start date for the time entries.
            to_date (date): The end date for the time entries.

        Returns:
            list[dict]: List of time entries.

        """
        url = "https://api.harvestapp.com/v2/time_entries"
        params = {
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
        }
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()["time_entries"]  # type: ignore[no-any-return]

    def add_time_entry(
        self,
        project_id: int,
        task_id: int,
        spent_date: date,
        hours: float,
        notes: str | None = None,
    ) -> dict[str, Any]:
        """Add a time entry to Harvest.

        Args:
            project_id (int): The ID of the project to associate with the time entry.
            task_id (int): The ID of the task to associate with the time entry.
            spent_date (date): The date the time entry was spent.
            hours (float): The number of hours spent.
            notes (str): Any notes to be associated with the time entry.

        """
        url = "https://api.harvestapp.com/v2/time_entries"
        data = {
            "project_id": project_id,
            "task_id": task_id,
            "spent_date": spent_date.isoformat(),
            "hours": hours,
        }

        if notes is not None:
            data["notes"] = notes

        response = self.client.post(url, json=data)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def delete_time_entry(self, time_entry_id: int) -> None:
        """Delete a time entry from Harvest.

        Args:
            time_entry_id (int): The ID of the time entry to delete.

        """
        url = f"https://api.harvestapp.com/v2/time_entries/{time_entry_id}"
        response = self.client.delete(url)
        response.raise_for_status()
