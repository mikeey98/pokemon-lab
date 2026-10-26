import random
import re

import requests
import streamlit as st
from shared.data import load_pokemon, sprite_url, types_of
from shared.names import is_correct_guess, species_name
from shared.quiz import update_streak
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


GENERATIONS = ["All", 1, 2, 3, 4, 5, 6]


def pick_mystery():
    """Choose a new Pokémon from the selected generation and reset the round."""
    generation = st.session_state.get("quiz_generation", "All")
    pool = pokemon
    if generation != "All":
        pool = pokemon[pokemon["Generation"].eq(generation)]
    # Avoid showing the same Pokémon twice in a row
    numbers = [num for num in pool["Num"] if num != st.session_state.get("quiz_num")]

    st.session_state.quiz_num = random.choice(numbers)
    st.session_state.quiz_solved = False
    st.session_state.quiz_skipped = False
    st.session_state.quiz_mistakes = 0


# Keep the same mystery Pokémon when the page reruns
if "quiz_num" not in st.session_state:
    pick_mystery()

# Score and streaks survive new rounds
for key in ("quiz_score", "quiz_streak", "quiz_best_streak"):
    st.session_state.setdefault(key, 0)

mystery = pokemon.loc[pokemon["Num"].eq(st.session_state.quiz_num)].iloc[0]
# "Deoxys Normal Forme" is just "Deoxys" in the quiz
answer = species_name(str(mystery["Name"]))

st.selectbox(
    "Generation",
    GENERATIONS,
    key="quiz_generation",
    on_change=pick_mystery,
)
# Small badges in the theme's red, one per number
st.markdown(
    f":primary-badge[:material/star: Score {st.session_state.quiz_score}] "
    f":primary-badge[:material/local_fire_department: Streak "
    f"{st.session_state.quiz_streak}] "
    f":primary-badge[:material/trophy: Best {st.session_state.quiz_best_streak}]"
)

# Show the silhouette until the round is over
revealed = st.session_state.quiz_solved or st.session_state.quiz_skipped
silhouette = "" if revealed else "filter:brightness(0);"

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

    st.button("Play again", on_click=pick_mystery)

elif st.session_state.quiz_skipped:
    st.info(f"It was {answer}!")
    st.button("Next Pokémon", on_click=pick_mystery)

else:
    with st.form("guess_form", clear_on_submit=True, border=False):
        guess = st.text_input("Who is this Pokémon?")
        submitted = st.form_submit_button("Guess")

    # Reveal the answer first, then move on with "Next Pokémon"
    if st.button("Skip Pokémon", type="tertiary"):
        st.session_state.quiz_skipped = True
        st.session_state.quiz_streak, _ = update_streak(
            st.session_state.quiz_streak, st.session_state.quiz_best_streak, False
        )
        st.rerun()

    if submitted and guess.strip():
        if is_correct_guess(guess, str(mystery["Name"])):
            st.session_state.quiz_solved = True
            st.session_state.quiz_score += 1
            st.session_state.quiz_streak, st.session_state.quiz_best_streak = (
                update_streak(
                    st.session_state.quiz_streak,
                    st.session_state.quiz_best_streak,
                    True,
                )
            )
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
