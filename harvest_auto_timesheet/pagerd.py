from datetime import date, timedelta

import pagerduty
from pydantic import AwareDatetime, BaseModel, TypeAdapter


class _Agent(BaseModel):
    id: str  # the user ID of the agent

class IncidentLog(BaseModel):
    id: str
    type: str
    summary: str
    agent: _Agent
    created_at: AwareDatetime

class Incident(BaseModel):
    id: str
    title: str
    summary: str
    html_url: str
    resolved_at: AwareDatetime
    logs: list[IncidentLog] | None = None

    def is_incident_for_user(self, user_id: str) -> bool:
        """Check if the incident is for a specific user."""
        return any(log.agent.id == user_id for log in self.logs or [])

    @property
    def acknowledged_time(self) -> AwareDatetime | None:
        """Get the time when the incident was acknowledged."""
        for log in self.logs or []:
            if log.type == "acknowledge_log_entry":
                return log.created_at
        return None

    @property
    def resolved_time(self) -> AwareDatetime | None:
        """Get the time when the incident was resolved."""
        for log in self.logs or []:
            if log.type == "resolve_log_entry":
                return log.created_at
        return None

    @property
    def duration(self) -> timedelta | None:
        """Calculate the duration of the incident in hours."""
        try:
            return self.resolved_time - self.acknowledged_time  # type: ignore[operator]
        except TypeError:
            # If either acknowledged or resolved time is None, return None
            return None

def get_incidents(
    pd_client: pagerduty.RestApiV2Client,
    user_id: str,
    since: date,
    until: date,
) -> list[Incident]:
    """Get all resolved incidents."""
    user = pd_client.rget(f"users/{user_id}")
    assert isinstance(user, dict)

    timezone = user["time_zone"]
    incidents = get_incidents_for_teams(
        pd_client=pd_client,
        team_ids=[team["id"] for team in user["teams"]],
        since=since,
        until=until,
        timezone=timezone,
    )

    user_incidents = []
    for incident in incidents:
        logs = get_incident_logs(pd_client, incident.id, timezone)
        incident.logs = logs
        if incident.is_incident_for_user(user_id):
            user_incidents.append(incident)

    return user_incidents

def get_incidents_for_teams(
    pd_client: pagerduty.RestApiV2Client,
    team_ids: list[str],
    since: date,
    until: date,
    timezone: str = "UTC",
) -> list[Incident]:
    """Get all resolved incidents for a specific user."""
    incidents = pd_client.list_all(
        "incidents",
        params={
            "since": since.isoformat(),
            "until": until.isoformat(),
            "team_ids[]": team_ids,
            "statuses[]": ["resolved"],
            "time_zone": timezone,
        },
    )

    adapter = TypeAdapter(list[Incident])
    return adapter.validate_python(incidents)

def get_incident_logs(
    pd_client: pagerduty.RestApiV2Client,
    incident_id: str,
    timezone: str,
) -> list[IncidentLog]:
    """Get logs for a specific incident."""
    incident_logs = pd_client.rget(
        f"incidents/{incident_id}/log_entries",
        params={
            "is_overview": "true",
            "time_zone": timezone,
        }
    )

    adapter = TypeAdapter(list[IncidentLog])
    return adapter.validate_python(incident_logs)
