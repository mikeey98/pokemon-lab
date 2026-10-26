from pathlib import Path

import streamlit as st
from shared.data import find_pokemon, load_pokemon
from shared.ui import NAVY, pokemon_summary

pokemon = load_pokemon()

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
    st.html(f"""
    <h1 style="position:relative; margin:0; color:{NAVY};
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

base = find_pokemon(pokemon, str(chosen))
available_forms = mega_forms.loc[mega_forms["Num"].eq(base["Num"])]

# Show the chosen Pokémon first
st.subheader(str(base["Name"]))
pokemon_summary(base)

# Introduce the comparison with all available Mega forms
st.subheader("Compared with its Mega form")
st.caption("Gray numbers show the change from the original Pokémon.")

# Show every Mega form for the chosen Pokémon
for _, mega in available_forms.iterrows():
    with st.container(border=True):
        st.markdown(f"#### {mega['Name']}")
        pokemon_summary(mega, compare_to=base, sprite_width=120)
