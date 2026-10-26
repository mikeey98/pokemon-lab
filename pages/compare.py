from pathlib import Path

import pandas as pd
import streamlit as st
from shared.sprite_ids import special_sprite_ids
from shared.type_icons import type_icons_html

# Load the same cleaned data as the other pages
data_path = Path(__file__).parent.parent / "data" / "PokemonData_clean.csv"
pokemon = pd.read_csv(data_path)
names = pokemon["Name"].sort_values()

# Page header: VS symbol matching the other pages
st.html("""
<div style="position:relative; overflow:hidden; height:150px;
            display:flex; align-items:center;">
    <div style="position:absolute; right:18px; top:0;
                width:150px; height:150px; box-sizing:border-box;
                border:9px solid #C73E3E; border-radius:50%;
                display:flex; align-items:center; justify-content:center;
                color:#C73E3E; font:900 54px Nunito,sans-serif;
                opacity:0.25;">VS</div>
    <h1 style="position:relative; margin:0; color:#24334A;
               font-family:Nunito,sans-serif;">
        Compare Pokémon
    </h1>
</div>
""")

left, right = st.columns(2)

with left:
    first = st.selectbox(
        "First Pokémon",
        names,
        index=None,
        placeholder="Search for a Pokémon...",
    )

with right:
    second = st.selectbox(
        "Second Pokémon",
        names,
        index=None,
        placeholder="Search for a Pokémon...",
    )

if first is None or second is None:
    st.stop()

if first == second:
    st.info("Choose two different Pokémon.")
    st.stop()

# Find the two selected rows
first_pokemon = pokemon.loc[pokemon["Name"].eq(str(first))].iloc[0]
second_pokemon = pokemon.loc[pokemon["Name"].eq(str(second))].iloc[0]

# Show both Pokémon using the same card layout
for column, selected in zip(st.columns(2), (first_pokemon, second_pokemon)):
    with column, st.container(border=True):
        st.subheader(str(selected["Name"]))

        sprite_id = special_sprite_ids.get(str(selected["Name"]), int(selected["Num"]))
        sprite_url = (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            f"sprites/pokemon/{sprite_id}.png"
        )
        st.image(sprite_url, width=150)

        types = [
            str(selected[type_column])
            for type_column in ("Type1", "Type2")
            if pd.notna(selected[type_column])
        ]
        st.html(type_icons_html(types))

# Compare the six base stats
stats = ["HP", "Attack", "Defense", "SpAtk", "SpDef", "Speed"]

st.subheader("Base stat comparison")
st.caption(f"Gray numbers show how {second} differs from {first}.")

with st.container(border=True):
    for stat in stats:
        first_value = int(first_pokemon[stat])
        second_value = int(second_pokemon[stat])

        stat_left, stat_right = st.columns(2)
        stat_left.metric(stat, first_value)
        stat_right.metric(
            stat,
            second_value,
            delta=f"{second_value - first_value:+d}",
            delta_color="off",
            delta_arrow="off",
        )