import requests
import streamlit as st
from shared.data import find_pokemon, load_pokemon, sprite_url, sprite_url_for_id
from shared.ui import RED, page_header, pokemon_summary, text_emblem

page_header("Pokédex", text_emblem("№", font_size=52))

pokemon = load_pokemon()


def choose_pokemon(name):
    st.session_state["pokedex_selected"] = name


def sprite_button(key, image_url, target_name):
    """A button that looks like a sprite and opens that Pokémon when clicked."""
    st.html(f"""
    <style>
    .st-key-{key} button {{
        width: 100px;
        height: 100px;
        background: url("{image_url}") center / contain no-repeat;
        border: 1px solid transparent;
        color: transparent;
    }}
    .st-key-{key} button:hover {{
        border-color: {RED};
    }}
    </style>
    """)

    st.button(
        f"Open {target_name}",
        key=key,
        on_click=choose_pokemon,
        args=(target_name,),
        width=100,
    )


name = st.selectbox(
    "Choose a Pokémon",
    pokemon["Name"].sort_values(),
    key="pokedex_selected",
    index=None,
    placeholder="Search for a Pokémon...",
)

if name is None:
    st.stop()

selected = find_pokemon(pokemon, name)

# Show the selected Pokémon
st.subheader(str(selected["Name"]))
pokemon_summary(selected)


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


def species_id(species):
    return int(species["url"].rstrip("/").split("/")[-1])


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
            member_id = species_id(species)
            member_sprite_url = sprite_url_for_id(member_id)

            available_names = pokemon.loc[
                pokemon["Num"].eq(member_id)
                & ~pokemon["Name"].str.startswith("Mega "),
                "Name",
            ]

            # Later generations are not in the dataset, so they cannot be opened.
            if available_names.empty:
                st.image(member_sprite_url, width=100)
                st.markdown(f"**{species['name'].replace('-', ' ').title()}**")
            else:
                target_name = str(available_names.iloc[0])
                sprite_button(f"evolution_{member_id}", member_sprite_url, target_name)
                st.markdown(f"**{target_name}**")
            st.caption(f"Stage {level}")

# Find Mega forms belonging to this evolution family
family_ids = {species_id(species) for species, _ in members}
mega_forms = pokemon.loc[
    pokemon["Num"].isin(family_ids) & pokemon["Name"].str.startswith("Mega ")
]

if not mega_forms.empty:
    st.subheader("Mega forms")

    for start in range(0, len(mega_forms), 4):
        row = mega_forms.iloc[start : start + 4]

        for column, (index, mega) in zip(st.columns(4), row.iterrows()):
            with column, st.container(border=True):
                mega_name = str(mega["Name"])

                base_name = pokemon.loc[
                    pokemon["Num"].eq(mega["Num"])
                    & ~pokemon["Name"].str.startswith("Mega "),
                    "Name",
                ].iloc[0]

                sprite_button(f"mega_{index}", sprite_url(mega), mega_name)
                st.markdown(f"**{mega_name}**")
                st.caption(f"Form of {base_name}")
