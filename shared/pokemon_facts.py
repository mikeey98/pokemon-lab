import pandas as pd


def build_pokemon_facts(row: pd.Series) -> str:
    types = [
        str(row[column])
        for column in ("Type1", "Type2")
        if pd.notna(row[column])
    ]

    return (
        f"Name: {row['Name']}\n"
        f"Types: {' / '.join(types)}\n"
        f"HP: {int(row['HP'])}\n"
        f"Attack: {int(row['Attack'])}\n"
        f"Defense: {int(row['Defense'])}\n"
        f"Special Attack: {int(row['SpAtk'])}\n"
        f"Special Defense: {int(row['SpDef'])}\n"
        f"Speed: {int(row['Speed'])}"
    )