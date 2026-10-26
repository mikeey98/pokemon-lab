import streamlit as st

st.set_page_config(page_title="Pokémon Lab")

page = st.navigation(
    [
        st.Page("pages/twins.py", title="Twins", default=True),
        st.Page("pages/mega.py", title="Mega Evolution"),
        st.Page("pages/compare.py", title="Compare"),
        st.Page("pages/quiz.py", title="Who's That Pokémon?"),
        st.Page("pages/pokedex.py", title="Pokédex"),
        st.Page("pages/team.py", title="Team Builder"),
        st.Page("pages/pokebot.py", title="Pokébot"),
    ],
    position="top",
)

st.caption("POKÉMON LAB")
page.run()