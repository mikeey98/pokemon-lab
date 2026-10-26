import streamlit as st
from shared.data import STATS, find_pokemon, load_pokemon
from shared.ui import POKEBALL_EMBLEM, page_header, pokemon_summary

pokemon = load_pokemon()

page_header("Pokémon Twins", POKEBALL_EMBLEM)

chosen = st.selectbox(
    "Choose a Pokémon",
    pokemon["Name"].sort_values(),
    index=None,
    placeholder="Search for a Pokémon...",
)

if chosen is None:
    st.stop()

# Show the selected Pokémon

selected = find_pokemon(pokemon, str(chosen))

st.subheader(str(chosen))
pokemon_summary(selected)

# Find the five closest twins

others = pokemon.loc[pokemon["Num"] != selected["Num"]].copy()

others["distance"] = (others[STATS] - selected[STATS].astype(int)).abs().sum(axis=1)
twins = others.nsmallest(5, "distance")

# Show each twin with its sprite and stats

st.subheader("Closest twins")
st.caption("Ranked by base stats. Gray numbers show the difference from your Pokémon.")

for rank, (_, twin) in enumerate(twins.iterrows(), start=1):
    with st.container(border=True):
        st.markdown(f"#### #{rank} {twin['Name']}")
        pokemon_summary(twin, compare_to=selected, sprite_width=120)
