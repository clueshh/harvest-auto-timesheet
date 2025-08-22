import random
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


def get_advice() -> str:
    """Get a random piece of advice from the Advice Slip API.

    Returns:
        str: A random piece of advice.

    """
    url = "https://api.adviceslip.com/advice"
    headers = {"Accept": "application/json"}

    with Client() as client:
        response = client.get(url, headers=headers)

    response.raise_for_status()
    advice_data = response.json()

    return advice_data["slip"]["advice"]  # type: ignore[no-any-return]


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


def random_numbers_sum(
    total_sum: float, num_elements: int, seed: int | None = None, decimals: int = 6
) -> list[float]:
    """Generate a list of random floats that sum up to a specified total.

    Args:
        total_sum (float): The desired sum of the floats in the list.
        num_elements (int): The number of elements (floats) in the list.
        seed (int | None): Optional seed for random number generation.
        decimals (int): Number of decimal places for each float.

    Returns:
        list: A list of floats that sum up to total_sum (rounded to `decimals` places).

    """
    if num_elements <= 0:
        return []
    if num_elements == 1:
        return [round(total_sum, decimals)]

    if seed is not None:
        random.seed(seed)

    scale = 10**decimals
    scaled_total = round(total_sum * scale)

    # Choose unique cut points to split the scaled total
    cuts = sorted(random.sample(range(1, scaled_total), num_elements - 1))

    # Calculate segment sizes between cuts
    parts = [b - a for a, b in zip([0, *cuts], [*cuts, scaled_total], strict=True)]

    # Convert back to floats with the specified number of decimals
    floats = [round(p / scale, decimals) for p in parts]

    # Adjust for floating point errors so the sum matches total_sum
    diff = round(total_sum - sum(floats), decimals)
    if abs(diff) > 0:
        # Add the difference to the largest element (by absolute value)
        idx = max(range(len(floats)), key=lambda i: abs(floats[i]))
        floats[idx] = round(floats[idx] + diff, decimals)

    return floats
