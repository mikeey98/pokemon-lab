from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from shared.sprite_ids import special_sprite_ids
from shared.type_icons import type_icons_html

st.html("""
<div style="position:relative; overflow:hidden; height:150px;
            display:flex; align-items:center;">
    <div style="position:absolute; right:18px; top:0;
                width:150px; height:150px; box-sizing:border-box;
                border:9px solid #C73E3E; border-radius:50%;
                display:flex; align-items:center; justify-content:center;
                color:#C73E3E; font:900 52px Nunito,sans-serif;
                opacity:0.25;">№</div>
    <h1 style="position:relative; margin:0; color:#24334A;
               font-family:Nunito,sans-serif;">
        Pokédex
    </h1>
</div>
""")

data_path = Path(__file__).parent.parent / "data" / "PokemonData_clean.csv"
pokemon = pd.read_csv(data_path)


def choose_pokemon(name):
    st.session_state["pokedex_selected"] = name


name = st.selectbox(
    "Choose a Pokémon",
    pokemon["Name"].sort_values(),
    key="pokedex_selected",
    index=None,
    placeholder="Search for a Pokémon...",
)

if name is None:
    st.stop()

selected = pokemon.loc[pokemon["Name"].eq(name)].iloc[0]

# Show the selected Pokémon
st.subheader(str(selected["Name"]))

sprite_id = special_sprite_ids.get(str(selected["Name"]), int(selected["Num"]))
sprite_url = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    f"sprites/pokemon/{sprite_id}.png"
)

image_col, info_col = st.columns([1, 4])

with image_col:
    st.image(sprite_url, width=150)

with info_col:
    types = [
        str(selected[column])
        for column in ("Type1", "Type2")
        if pd.notna(selected[column])
    ]
    st.html(type_icons_html(types))

    stats = ["HP", "Attack", "Defense", "SpAtk", "SpDef", "Speed"]
    for column, stat in zip(st.columns(6), stats):
        column.metric(stat, int(selected[stat]))


@st.cache_data
def get_pokedex_entry(number):
    response = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{number}/",
        timeout=10,
    )
    response.raise_for_status()
    entries = response.json()["flavor_text_entries"]

    english_entries = [entry for entry in entries if entry["language"]["name"] == "en"]
    return english_entries[-1] if english_entries else None


try:
    entry = get_pokedex_entry(int(selected["Num"]))
    if entry:
        description = entry["flavor_text"].replace("\n", " ").replace("\f", " ")
        st.subheader("About")
        with st.container(border=True):
            st.write(description)
    else:
        st.info("No English Pokédex entry found.")
except requests.RequestException:
    st.warning("Could not load the Pokédex entry right now.")


@st.cache_data
def get_evolution_chain(number):
    species_response = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{number}/",
        timeout=10,
    )
    species_response.raise_for_status()
    chain_url = species_response.json()["evolution_chain"]["url"]

    chain_response = requests.get(chain_url, timeout=10)
    chain_response.raise_for_status()
    return chain_response.json()["chain"]


def evolution_members(chain):
    members = []
    queue = [(chain, 1)]

    while queue:
        stage, level = queue.pop(0)
        members.append((stage["species"], level))

        for next_stage in stage["evolves_to"]:
            queue.append((next_stage, level + 1))

    return members


try:
    chain = get_evolution_chain(int(selected["Num"]))
    members = evolution_members(chain)
except requests.RequestException:
    st.warning("Could not load the evolution family right now.")
    members = []

if not members:
    st.stop()

st.subheader("Evolution family")

for start in range(0, len(members), 4):
    row = members[start : start + 4]

    for column, (species, level) in zip(st.columns(4), row):
        with column, st.container(border=True):
            species_id = int(species["url"].rstrip("/").split("/")[-1])
            sprite_url = (
                "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
                f"sprites/pokemon/{species_id}.png"
            )

            available_names = pokemon.loc[
                pokemon["Num"].eq(species_id)
                & ~pokemon["Name"].str.startswith("Mega "),
                "Name",
            ]

            if available_names.empty:
                st.image(sprite_url, width=100)
                st.markdown(f"**{species['name'].replace('-', ' ').title()}**")
            else:
                target_name = str(available_names.iloc[0])

                st.html(f"""
                <style>
                .st-key-evolution_{species_id} button {{
                    width: 100px;
                    height: 100px;
                    background: url("{sprite_url}") center / contain no-repeat;
                    border: 1px solid transparent;
                    color: transparent;
                }}
                .st-key-evolution_{species_id} button:hover {{
                    border-color: #C73E3E;
                }}
                </style>
                """)

                st.button(
                    f"Open {target_name}",
                    key=f"evolution_{species_id}",
                    on_click=choose_pokemon,
                    args=(target_name,),
                    width=100,
                )
                st.markdown(f"**{target_name}**")
            st.caption(f"Stage {level}")

# Find Mega forms belonging to this evolution family
family_ids = {int(species["url"].rstrip("/").split("/")[-1]) for species, _ in members}
mega_forms = pokemon.loc[
    pokemon["Num"].isin(family_ids) & pokemon["Name"].str.startswith("Mega ")
]

if not mega_forms.empty:
    st.subheader("Mega forms")

    for start in range(0, len(mega_forms), 4):
        row = mega_forms.iloc[start : start + 4]

        for column, (_, mega) in zip(st.columns(4), row.iterrows()):
            with column, st.container(border=True):
                mega_name = str(mega["Name"])
                sprite_id = special_sprite_ids[mega_name]
                sprite_url = (
                    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
                    f"sprites/pokemon/{sprite_id}.png"
                )

                base_name = pokemon.loc[
                    pokemon["Num"].eq(mega["Num"])
                    & ~pokemon["Name"].str.startswith("Mega "),
                    "Name",
                ].iloc[0]

                st.html(f"""
                <style>
                .st-key-mega_{sprite_id} button {{
                    width: 100px;
                    height: 100px;
                    background: url("{sprite_url}") center / contain no-repeat;
                    border: 1px solid transparent;
                    color: transparent;
                }}
                .st-key-mega_{sprite_id} button:hover {{
                    border-color: #C73E3E;
                }}
                </style>
                """)

                st.button(
                    f"Open {mega_name}",
                    key=f"mega_{sprite_id}",
                    on_click=choose_pokemon,
                    args=(mega_name,),
                    width=100,
                )
                st.markdown(f"**{mega_name}**")
                st.caption(f"Form of {base_name}")