"""Load the cleaned Pokémon data and look up sprites and types."""

from pathlib import Path

import pandas as pd
import streamlit as st

from shared.sprite_ids import special_sprite_ids

DATA_PATH = Path(__file__).parent.parent / "data" / "PokemonData_clean.csv"
STATS = ["HP", "Attack", "Defense", "SpAtk", "SpDef", "Speed"]
SPRITE_BASE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon"
)


@st.cache_data
def load_pokemon() -> pd.DataFrame:
    """Read the CSV once and reuse it on every page and rerun."""
    return pd.read_csv(DATA_PATH)


def find_pokemon(pokemon: pd.DataFrame, name: str) -> pd.Series:
    return pokemon.loc[pokemon["Name"].eq(name)].iloc[0]


def types_of(row: pd.Series) -> list[str]:
    return [
        str(row[column])
        for column in ("Type1", "Type2")
        if pd.notna(row[column])
    ]


def sprite_url_for_id(sprite_id: int) -> str:
    return f"{SPRITE_BASE_URL}/{sprite_id}.png"


def sprite_url(row: pd.Series) -> str:
    """Forms like Mega Venusaur share a Pokédex number, so they need their own ID."""
    sprite_id = special_sprite_ids.get(str(row["Name"]), int(row["Num"]))
    return sprite_url_for_id(sprite_id)
