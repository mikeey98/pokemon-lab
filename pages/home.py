import streamlit as st
from shared.data import load_pokemon, sprite_url_for_id
from shared.ui import NAVY, POKEBALL_EMBLEM, page_header

pokemon = load_pokemon()

# One card per page: (page file, title, description, sprite IDs, hide sprites)
FEATURES = [
    (
        "pages/quiz.py",
        "Who's That Pokémon?",
        "Guess the Pokémon from its silhouette. Wrong guesses unlock hints.",
        [25],
        True,
    ),
    (
        "pages/pokedex.py",
        "Pokédex",
        "Look up any Pokémon and click through its evolution family.",
        [1, 2, 3],
        False,
    ),
    (
        "pages/team.py",
        "Team Builder",
        "Pick a team of six and find out which types it is weak against.",
        [4, 7, 1],
        False,
    ),
    (
        "pages/twins.py",
        "Twins",
        "Find the Pokémon whose base stats are closest to your favourite.",
        [311, 312],
        False,
    ),
    (
        "pages/compare.py",
        "Compare",
        "Put two Pokémon side by side and see who wins each stat.",
        [25, 26],
        False,
    ),
    (
        "pages/mega.py",
        "Mega Evolution",
        "See how much stronger a Pokémon gets when it Mega Evolves.",
        [6, 10034],
        False,
    ),
    (
        "pages/pokebot.py",
        "Pokébot",
        "Chat about a Pokémon with a small AI model (runs locally).",
        [137],
        False,
    ),
]


def sprites_html(sprite_ids: list[int], hidden: bool) -> str:
    """A row of sprites. Hidden sprites are shown as black silhouettes."""
    silhouette = "filter:brightness(0);" if hidden else ""
    images = "".join(
        f'<img src="{sprite_url_for_id(sprite_id)}" alt="" '
        # Sprites shrink when three of them do not fit in a narrow card
        f'style="flex:0 1 80px; min-width:0; height:80px; object-fit:contain;'
        f' image-rendering:pixelated; {silhouette}">'
        for sprite_id in sprite_ids
    )
    return (
        '<div style="display:flex; justify-content:center; gap:4px;'
        f' height:80px;">{images}</div>'
    )


page_header("Welcome, trainer!", POKEBALL_EMBLEM)

species_count = pokemon["Num"].nunique()
st.html(f"""
<p style="color:{NAVY}; font-size:1.1rem; margin:0 0 8px;">
    Explore, compare and guess {species_count} Pokémon from generation 1–6.
    Pick something to try below.
</p>
""")

for start in range(0, len(FEATURES), 3):
    row = FEATURES[start : start + 3]

    for column, (page, title, description, sprite_ids, hidden) in zip(
        st.columns(3), row
    ):
        with column, st.container(border=True):
            st.html(sprites_html(sprite_ids, hidden))
            st.markdown(f"**{title}**")
            st.caption(description)
            st.page_link(page, label="Open →")
