import pandas as pd

from shared.data import types_of


def build_pokemon_facts(row: pd.Series) -> str:
    return (
        f"Name: {row['Name']}\n"
        f"Types: {' / '.join(types_of(row))}\n"
        f"HP: {int(row['HP'])}\n"
        f"Attack: {int(row['Attack'])}\n"
        f"Defense: {int(row['Defense'])}\n"
        f"Special Attack: {int(row['SpAtk'])}\n"
        f"Special Defense: {int(row['SpDef'])}\n"
        f"Speed: {int(row['Speed'])}"
    )