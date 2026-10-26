import random
import re

import requests
import streamlit as st
from shared.data import load_pokemon, sprite_url, types_of
from shared.names import is_correct_guess, species_name
from shared.ui import page_header, text_emblem

# Load one form per Pokédex number
pokemon = load_pokemon().drop_duplicates("Num").reset_index(drop=True)

page_header("Who's That Pokémon?", text_emblem("?", font_size=95))


@st.cache_data
def get_quiz_about(number):
    response = requests.get(
        f"https://pokeapi.co/api/v2/pokemon-species/{number}/",
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    english = [
        entry
        for entry in data["flavor_text_entries"]
        if entry["language"]["name"] == "en"
    ]
    if not english:
        return None

    return english[-1]["flavor_text"], data["name"]


# Keep the same mystery Pokémon when the page reruns
if "quiz_index" not in st.session_state:
    st.session_state.quiz_index = random.randrange(len(pokemon))

# Remember whether the player guessed correctly
if "quiz_solved" not in st.session_state:
    st.session_state.quiz_solved = False

# Count incorrect guesses
if "quiz_mistakes" not in st.session_state:
    st.session_state.quiz_mistakes = 0

mystery = pokemon.iloc[st.session_state.quiz_index]
# "Deoxys Normal Forme" is just "Deoxys" in the quiz
answer = species_name(str(mystery["Name"]))

# Show the silhouette until the answer is correct
silhouette = "" if st.session_state.quiz_solved else "filter:brightness(0);"

with st.container(border=True):
    st.html(
        f'<div style="text-align:center; padding:12px 0;">'
        f'<img src="{sprite_url(mystery)}" alt="Mystery Pokémon" '
        f'style="width:240px; image-rendering:pixelated; {silhouette}">'
        f"</div>"
    )

# Check the player's guess
if st.session_state.quiz_solved:
    st.success(f"Correct! It's {answer}!")

    if st.button("Play again"):
        st.session_state.quiz_index = random.randrange(len(pokemon))
        st.session_state.quiz_solved = False
        st.session_state.quiz_mistakes = 0
        st.rerun()

else:
    with st.form("guess_form", clear_on_submit=True, border=False):
        guess = st.text_input("Who is this Pokémon?")
        submitted = st.form_submit_button("Guess")

    # Skip to a different Pokémon
    if st.button("Skip Pokémon", type="tertiary"):
        st.session_state.quiz_index = random.choice(
            [i for i in range(len(pokemon)) if i != st.session_state.quiz_index]
        )
        st.session_state.quiz_mistakes = 0
        st.rerun()

    if submitted and guess.strip():
        if is_correct_guess(guess, str(mystery["Name"])):
            st.session_state.quiz_solved = True
            st.rerun()
        else:
            st.session_state.quiz_mistakes += 1
            st.warning("Not quite! Try again.")

    # Keep revealed hints visible between guesses
    hints = [
        f"Type: {' / '.join(types_of(mystery))}",
        f"Generation: {int(mystery['Generation'])}",
        f"Starts with: {answer[0]}",
    ]

    if st.session_state.quiz_mistakes >= 4:
        try:
            result = get_quiz_about(int(mystery["Num"]))

            if result is None:
                hints.append("About: No English Pokédex entry found.")
            else:
                about, api_name = result
                about = about.replace("\n", " ").replace("\f", " ")

                # Hide both the displayed name and the species name in the text.
                names = [answer, api_name.replace("-", " ")]
                for pokemon_name in sorted(names, key=len, reverse=True):
                    about = re.sub(
                        rf"(?<!\w){re.escape(pokemon_name)}(?!\w)",
                        "...",
                        about,
                        flags=re.IGNORECASE,
                    )

                hints.append(f"About: {about}")

        except requests.RequestException:
            hints.append("About: Could not load the Pokédex entry right now.")

    if st.session_state.quiz_mistakes > 0:
        with st.container(border=True):
            st.caption("HINTS")

            for number, hint in enumerate(
                hints[: st.session_state.quiz_mistakes], start=1
            ):
                st.markdown(f"**{number}.** {hint}")
