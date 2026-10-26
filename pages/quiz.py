import random
import re
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from shared.sprite_ids import special_sprite_ids

# Load one form per Pokédex number
data_path = Path(__file__).parent.parent / "data" / "PokemonData_clean.csv"
pokemon = pd.read_csv(data_path)
pokemon = pokemon.drop_duplicates("Num").reset_index(drop=True)

# Page header: mystery symbol matching the other pages
st.html("""
<div style="position:relative; overflow:hidden; height:150px;
            display:flex; align-items:center;">
    <div style="position:absolute; right:18px; top:0;
                width:150px; height:150px; box-sizing:border-box;
                border:9px solid #C73E3E; border-radius:50%;
                display:flex; align-items:center; justify-content:center;
                color:#C73E3E; font:900 95px Nunito,sans-serif;
                opacity:0.25;">?</div>
    <h1 style="position:relative; margin:0; color:#24334A;
               font-family:Nunito,sans-serif;">
        Who's That Pokémon?
    </h1>
</div>
""")


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
sprite_id = special_sprite_ids.get(str(mystery["Name"]), int(mystery["Num"]))

sprite_url = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
    f"sprites/pokemon/{sprite_id}.png"
)

# Show the silhouette until the answer is correct
silhouette = "" if st.session_state.quiz_solved else "filter:brightness(0);"

with st.container(border=True):
    st.html(
        f'<div style="text-align:center; padding:12px 0;">'
        f'<img src="{sprite_url}" alt="Mystery Pokémon" '
        f'style="width:240px; image-rendering:pixelated; {silhouette}">'
        f"</div>"
    )

# Check the player's guess
if st.session_state.quiz_solved:
    st.success(f"Correct! It's {mystery['Name']}!")

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
        if guess.strip().casefold() == str(mystery["Name"]).casefold():
            st.session_state.quiz_solved = True
            st.rerun()
        else:
            st.session_state.quiz_mistakes += 1
            st.warning("Not quite! Try again.")

    # Keep revealed hints visible between guesses
    hints = [
        f"Type: {mystery['Type1']}",
        f"Generation: {int(mystery['Generation'])}",
        f"Starts with: {str(mystery['Name'])[0]}",
    ]

    if st.session_state.quiz_mistakes >= 4:
        try:
            result = get_quiz_about(int(mystery["Num"]))

            if result is None:
                hints.append("About: No English Pokédex entry found.")
            else:
                about, species_name = result
                about = about.replace("\n", " ").replace("\f", " ")

                # Hide both the displayed name and the species name in the text.
                names = [str(mystery["Name"]), species_name.replace("-", " ")]
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
