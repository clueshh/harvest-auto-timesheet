from datetime import UTC, date, datetime, timedelta

from httpx import Client


def get_joke() -> str:
    """Get a random joke from the JokeAPI.

    Returns:
        str: A random joke.

    """
    url = "https://v2.jokeapi.dev/joke/Programming?blacklistFlags=nsfw,racist,sexist,explicit"
    headers = {"Accept": "application/json"}

    with Client() as client:
        response = client.get(url, headers=headers)

    response.raise_for_status()
    joke_data = response.json()

    if joke_data["type"] == "single":
        return joke_data["joke"]  # type: ignore[no-any-return]

    return f"{joke_data['setup']} {joke_data['delivery']}"


def get_start_of_week(date_: date | None = None) -> date:
    """Get the start of the week for a given date.

    Args:
        date_ (date): The date to get the start of the week for.
            If None, uses the current date.

    Returns:
        date: The start of the week.

    """
    if date_ is None:
        date_ = datetime.now(tz=UTC).date()

    return date_ - timedelta(days=date_.weekday())


def get_end_of_week(date_: date | None = None) -> date:
    """Get the end of the week for a given date.

    Args:
        date_ (date): The date to get the end of the week for.
            If None, uses the current date.

    Returns:
        date: The end of the week.

    """
    if date_ is None:
        date_ = datetime.now(tz=UTC).date()

    return date_ + timedelta(days=6 - date_.weekday())
