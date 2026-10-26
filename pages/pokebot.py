from pathlib import Path

import requests
import streamlit as st
from shared.data import find_pokemon, load_pokemon, sprite_url, types_of
from shared.pokemon_facts import build_pokemon_facts
from shared.qwen import ask_qwen
from shared.type_icons import type_icons_html
from shared.ui import NAVY

bot_icon = Path(__file__).parent.parent / "assets" / "pokebot.svg"

title_col, icon_col = st.columns([4, 1], vertical_alignment="center")

with title_col:
    st.html(f"""
    <h1 style="margin:0; color:{NAVY}; font-family:Nunito,sans-serif;">
        Pokébot
    </h1>
    """)
    st.caption("Ask about a Pokémon, or imagine something fun together.")

with icon_col:
    st.image(bot_icon, width=130)

pokemon = load_pokemon()

chosen = st.selectbox(
    "Choose a Pokémon",
    pokemon["Name"].sort_values(),
    index=None,
    placeholder="Search for a Pokémon...",
)

if chosen is None:
    st.stop()

selected = find_pokemon(pokemon, str(chosen))
facts = build_pokemon_facts(selected)

with st.container(border=True):
    image_col, info_col = st.columns([1, 4], vertical_alignment="center")

    with image_col:
        st.image(sprite_url(selected), width=120)

    with info_col:
        st.subheader(str(chosen))
        st.html(type_icons_html(types_of(selected)))
        st.caption("Ask me about its stats, or ask me to make a playful guess.")

# Start a new conversation when a different Pokémon is selected.
if st.session_state.get("pokebot_selected") != chosen:
    st.session_state["pokebot_selected"] = chosen
    st.session_state["pokebot_messages"] = []

# Show earlier questions and answers.
for message in st.session_state["pokebot_messages"]:
    avatar = bot_icon if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=avatar):
        st.write(message["content"])

question = st.chat_input("Ask about this Pokémon...")

if question:
    with st.chat_message("user"):
        st.write(question)

    try:
        with st.spinner("Pokébot is thinking..."):
            answer = ask_qwen(
                facts,
                question,
                st.session_state["pokebot_messages"],
            )
    except requests.RequestException:
        st.error("Could not reach Ollama. Check that it is running.")
    else:
        st.session_state["pokebot_messages"].extend(
            [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer},
            ]
        )

        with st.chat_message("assistant", avatar=bot_icon):
            st.write(answer)