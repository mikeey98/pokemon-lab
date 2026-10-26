"""Read a team from a comma-separated list of names, e.g. from the URL."""

MAX_TEAM_SIZE = 6


def parse_team(text: str, known_names: set[str]) -> list[str]:
    """Turn "Pikachu,Gengar" into a team, skipping unknown names and repeats."""
    team = []

    for name in text.split(","):
        name = name.strip()

        if name in known_names and name not in team:
            team.append(name)

    return team[:MAX_TEAM_SIZE]
