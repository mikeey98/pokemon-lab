import streamlit as st
from shared.data import STATS, find_pokemon, load_pokemon, sprite_url, types_of
from shared.type_icons import type_icons_html
from shared.ui import page_header, text_emblem

pokemon = load_pokemon()
names = pokemon["Name"].sort_values()

page_header("Compare Pokémon", text_emblem("VS", font_size=54))

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
first_pokemon = find_pokemon(pokemon, str(first))
second_pokemon = find_pokemon(pokemon, str(second))

# Show both Pokémon using the same card layout
for column, selected in zip(st.columns(2), (first_pokemon, second_pokemon)):
    with column, st.container(border=True):
        st.subheader(str(selected["Name"]))
        st.image(sprite_url(selected), width=150)
        st.html(type_icons_html(types_of(selected)))

# Compare the six base stats
st.subheader("Base stat comparison")
st.caption(f"Gray numbers show how {second} differs from {first}.")

with st.container(border=True):
    for stat in STATS:
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
