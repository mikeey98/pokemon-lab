from pathlib import Path

import pandas as pd
import streamlit as st
from shared.sprite_ids import special_sprite_ids
from shared.type_icons import type_icons_html

data_path = Path(__file__).parent.parent / "data" / "PokemonData_clean.csv"
pokemon = pd.read_csv(data_path)

stats = ["HP", "Attack", "Defense", "SpAtk", "SpDef", "Speed"]


def show_type_icons(pokemon_row: pd.Series) -> None:
    types = [
        str(pokemon_row[column])
        for column in ("Type1", "Type2")
        if pd.notna(pokemon_row[column])
    ]
    st.html(type_icons_html(types))


# Choosing a Pokemon

st.html("""
<div style="position:relative; overflow:hidden; height:150px;
            display:flex; align-items:center;">
    <div style="position:absolute; right:18px; top:0px;
                width:150px; height:150px; box-sizing:border-box;
                border:9px solid #C73E3E; border-radius:50%;
                opacity:0.25;">
        <div style="position:absolute; left:0; right:0; top:50%;
                    height:9px; background:#C73E3E;
                    transform:translateY(-50%);"></div>
        <div style="position:absolute; left:50%; top:50%;
                    width:36px; height:36px; box-sizing:border-box;
                    transform:translate(-50%,-50%);
                    border:9px solid #C73E3E; border-radius:50%;
                    background:#F7F5EF;"></div>
    </div>
    <h1 style="position:relative; margin:0; color:#24334A;
               font-family:Nunito,sans-serif;">
        Pokémon Twins
    </h1>
</div>
""")

chosen = st.selectbox(
    "Choose a Pokémon",
    pokemon["Name"].sort_values(),
    index=None,
    placeholder="Search for a Pokémon...",
)

if chosen is None:
    st.stop()

chosen = str(chosen)

# Show the selected Pokémon

selected = pokemon.loc[pokemon["Name"] == chosen].iloc[0]
sprite_id = special_sprite_ids.get(chosen, int(selected["Num"]))
sprite_url = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    f"sprites/pokemon/{sprite_id}.png"
)

st.subheader(chosen)
image_col, info_col = st.columns([1, 4])

with image_col:
    st.image(sprite_url, width=150)

with info_col:
    show_type_icons(selected)
    for column, stat in zip(st.columns(6), stats):
        column.metric(stat, int(selected[stat]))

# Find the five closest twins

others = pokemon.loc[pokemon["Num"] != selected["Num"]].copy()

others["distance"] = (others[stats] - selected[stats].astype(int)).abs().sum(axis=1)
twins = others.nsmallest(5, "distance")

# Show each twin with its sprite and stats

st.subheader("Closest twins")
st.caption("Ranked by base stats. Gray numbers show the difference from your Pokémon.")

for rank, (_, twin) in enumerate(twins.iterrows(), start=1):
    with st.container(border=True):
        st.markdown(f"#### #{rank} {twin['Name']}")

        image_col, info_col = st.columns([1, 4])
        twin_sprite_id = special_sprite_ids.get(str(twin["Name"]), int(twin["Num"]))

        with image_col:
            st.image(
                "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
                f"sprites/pokemon/{twin_sprite_id}.png",
                width=120,
            )

        with info_col:
            show_type_icons(twin)

            for column, stat in zip(st.columns(6), stats):
                difference = int(twin[stat]) - int(selected[stat])
                column.metric(
                    stat,
                    int(twin[stat]),
                    delta=f"{difference:+d}",
                    delta_color="off",
                    delta_arrow="off",
                )
