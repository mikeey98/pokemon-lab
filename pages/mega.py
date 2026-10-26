from pathlib import Path

import pandas as pd
import streamlit as st
from shared.sprite_ids import special_sprite_ids
from shared.type_icons import type_icons_html

pokemon = pd.read_csv(
    Path(__file__).parent.parent / "data" / "PokemonData_clean.csv"
)
stats = ["HP", "Attack", "Defense", "SpAtk", "SpDef", "Speed"]

# Find Mega forms and the Pokémon that can transform into them
mega_forms = pokemon[pokemon["Name"].str.startswith("Mega ")]
base_names = pokemon.loc[
    pokemon["Num"].isin(mega_forms["Num"])
    & ~pokemon["Name"].str.startswith("Mega "),
    "Name",
].sort_values()

# Page header: title on the left, Mega symbol on the right
mega_icon = Path(__file__).parent.parent / "assets" / "mega_symbol_red.png"

title_col, icon_col = st.columns([4, 1], vertical_alignment="center")

with title_col:
    st.html("""
    <h1 style="position:relative; margin:0; color:#24334A;
               font-family:Nunito,sans-serif;">
        Mega Evolution
    </h1>
    """)

with icon_col:
    st.image(mega_icon, width=150)

chosen = st.selectbox(
    "Choose a Pokémon",
    base_names,
    index=None,
    placeholder="Search for a Pokémon...",
)

if chosen is None:
    st.stop()

base = pokemon.loc[pokemon["Name"].eq(chosen)].iloc[0]
available_forms = mega_forms.loc[mega_forms["Num"].eq(base["Num"])]

# Show the chosen Pokémon first
st.subheader(str(base["Name"]))

base_sprite_id = special_sprite_ids.get(str(base["Name"]), int(base["Num"]))
base_sprite_url = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    f"sprites/pokemon/{base_sprite_id}.png"
)

image_col, info_col = st.columns([1, 4])

with image_col:
    st.image(base_sprite_url, width=150)

with info_col:
    base_types = [
        str(base[column])
        for column in ("Type1", "Type2")
        if pd.notna(base[column])
    ]
    st.html(type_icons_html(base_types))

    for column, stat in zip(st.columns(6), stats):
        column.metric(stat, int(base[stat]))


# Introduce the comparison with all available Mega forms
st.subheader("Compared with its Mega form")
st.caption("Gray numbers show the change from the original Pokémon.")

# Show every Mega form for the chosen Pokémon
for _, mega in available_forms.iterrows():
    with st.container(border=True):
        st.markdown(f"#### {mega['Name']}")

        mega_sprite_id = special_sprite_ids.get(
            str(mega["Name"]), int(mega["Num"])
        )
        mega_sprite_url = (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            f"sprites/pokemon/{mega_sprite_id}.png"
        )

        image_col, info_col = st.columns([1, 4])

        with image_col:
            st.image(mega_sprite_url, width=120)

        with info_col:
            mega_types = [
                str(mega[column])
                for column in ("Type1", "Type2")
                if pd.notna(mega[column])
            ]
            st.html(type_icons_html(mega_types))

            for column, stat in zip(st.columns(6), stats):
                difference = int(mega[stat]) - int(base[stat])
                column.metric(
                    stat,
                    int(mega[stat]),
                    delta=f"{difference:+d}",
                    delta_color="off",
                    delta_arrow="off",
                )
