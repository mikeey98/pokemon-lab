from base64 import b64encode

import streamlit as st
from shared.ui import NAVY, POKEBALL_EMBLEM, RED, page_header

# Line icons in the style of Lucide (https://lucide.dev, ISC licence):
# 24x24 grid, round line ends, no fill. Only the inner SVG shapes are stored here.
ICONS = {
    "quiz": (
        '<circle cx="12" cy="12" r="10"/>'
        '<path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/>'
        '<path d="M12 17h.01"/>'
    ),
    "pokedex": (
        '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/>'
        '<path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>'
    ),
    "team": (
        '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M22 21v-2a4 4 0 0 0-3-3.9"/>'
        '<path d="M16 3.1a4 4 0 0 1 0 7.8"/>'
    ),
    "compare": (
        '<path d="M12 3v18"/>'
        '<path d="M7 21h10"/>'
        '<path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>'
        '<path d="m16 16 3-8 3 8c-.9.7-1.9 1-3 1s-2.1-.3-3-1z"/>'
        '<path d="m2 16 3-8 3 8c-.9.7-1.9 1-3 1s-2.1-.3-3-1z"/>'
    ),
    "twins": (
        '<circle cx="9" cy="12" r="6"/>'
        '<circle cx="15" cy="12" r="6"/>'
    ),
    "mega": (
        '<path d="M9.9 15.5a2 2 0 0 0-1.4-1.4l-6.1-1.6a.5.5 0 0 1 0-1l6.1-1.6'
        "a2 2 0 0 0 1.4-1.4l1.6-6.1a.5.5 0 0 1 1 0l1.6 6.1a2 2 0 0 0 1.4 1.4"
        "l6.1 1.6a.5.5 0 0 1 0 1l-6.1 1.6a2 2 0 0 0-1.4 1.4l-1.6 6.1"
        'a.5.5 0 0 1-1 0z"/>'
    ),
    "pokebot": (
        '<path d="M12 8V4H8"/>'
        '<rect x="4" y="8" width="16" height="12" rx="2"/>'
        '<path d="M2 14h2"/>'
        '<path d="M20 14h2"/>'
        '<path d="M15 13v2"/>'
        '<path d="M9 13v2"/>'
    ),
}

# (key, page file, title, description). The first one is shown as a wide card.
FEATURED = ("quiz", "pages/quiz.py", "Who's That Pokémon?",
            "Guess the Pokémon from its silhouette.")
FEATURES = [
    ("pokedex", "pages/pokedex.py", "Pokédex",
     "Stats, Pokédex entries and evolutions."),
    ("team", "pages/team.py", "Team Builder",
     "Build a team of six and spot its weaknesses."),
    ("compare", "pages/compare.py", "Compare",
     "Put two Pokémon head to head."),
    ("twins", "pages/twins.py", "Twins",
     "Find the Pokémon with the most similar stats."),
    ("mega", "pages/mega.py", "Mega Evolution",
     "See what changes when a Pokémon Mega Evolves."),
    ("pokebot", "pages/pokebot.py", "Pokébot",
     "Chat about any Pokémon with a local AI."),
]

# Cards are Streamlit containers with keys like "card_quiz", styled here.
# The page link is stretched over the whole card, so the full card is clickable.
CARD_CSS = f"""
<style>
/* Let every card fill its column, so all cards in a row get the same height */
.st-key-home_cards [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {{
    height: 100%;
}}
.st-key-home_cards [data-testid="stLayoutWrapper"]:has(> [class*="st-key-card_"]) {{
    flex: 1;
}}
[class*="st-key-card_"] {{
    position: relative;
    height: 100%;
    gap: 0.35rem;
    padding: 22px;
    background: #FFFFFF;
    border: 1px solid #E6E1D6;
    border-radius: 16px;
    transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
}}
[class*="st-key-card_"]:hover {{
    border-color: {RED};
    box-shadow: 0 6px 18px rgba(36, 51, 74, 0.08);
    transform: translateY(-2px);
}}
[class*="st-key-card_"] [data-testid="stPageLink-NavLink"] {{
    padding: 0;
    background: none;
}}
[class*="st-key-card_"] [data-testid="stPageLink-NavLink"] p {{
    font-size: 1.05rem;
    font-weight: 700;
    color: {NAVY};
}}
[class*="st-key-card_"] [data-testid="stElementContainer"] {{
    position: static;
}}
[class*="st-key-card_"] [data-testid="stPageLink-NavLink"]::after {{
    content: "";
    position: absolute;
    inset: 0;
    z-index: 1;
}}
</style>
"""


def icon_html(name: str) -> str:
    """A red line icon on a soft red circle."""
    # st.html removes inline <svg>, so the icon is sent as an image instead.
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
        f' stroke="{RED}" stroke-width="2" stroke-linecap="round"'
        f' stroke-linejoin="round">{ICONS[name]}</svg>'
    )
    image = b64encode(svg.encode()).decode("ascii")
    return f"""
    <div style="width:44px; height:44px; margin-bottom:10px; border-radius:50%;
                background:rgba(199, 62, 62, 0.1);
                display:flex; align-items:center; justify-content:center;">
        <img src="data:image/svg+xml;base64,{image}" alt=""
             style="width:22px; height:22px;">
    </div>
    """


def feature_card(key: str, page: str, title: str, description: str) -> None:
    with st.container(key=f"card_{key}"):
        st.html(icon_html(key))
        st.page_link(page, label=title)
        st.caption(description)


page_header("Welcome!", POKEBALL_EMBLEM)
st.html(CARD_CSS)

with st.container(key="home_cards"):
    feature_card(*FEATURED)

    for start in range(0, len(FEATURES), 3):
        for column, feature in zip(st.columns(3), FEATURES[start : start + 3]):
            with column:
                feature_card(*feature)
