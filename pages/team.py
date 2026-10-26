import pandas as pd
import requests
import streamlit as st
from shared.data import STATS, find_pokemon, load_pokemon, sprite_url, types_of
from shared.team import MAX_TEAM_SIZE, parse_team
from shared.type_icons import type_icons_html
from shared.ui import TEAM_EMBLEM, page_header, pokemon_summary

pokemon = load_pokemon()


@st.cache_data
def get_type_relations(type_name):
    response = requests.get(
        f"https://pokeapi.co/api/v2/type/{type_name.lower()}/",
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()["damage_relations"]

    return {
        "double": {item["name"].title() for item in data["double_damage_from"]},
        "half": {item["name"].title() for item in data["half_damage_from"]},
        "none": {item["name"].title() for item in data["no_damage_from"]},
    }


def damage_multiplier(attack_type, member):
    multiplier = 1.0

    for type_name in types_of(member):
        relations = get_type_relations(type_name)

        if attack_type in relations["none"]:
            return 0.0
        if attack_type in relations["double"]:
            multiplier *= 2
        elif attack_type in relations["half"]:
            multiplier *= 0.5

    return multiplier


def show_weakness_row(attack_type, weak_members, team_data):
    sprite_urls = []
    names = []

    for name, _ in weak_members:
        sprite_urls.append(sprite_url(find_pokemon(team_data, name)))
        names.append(name)

    with st.container(border=True):
        type_col, count_col, sprites_col = st.columns(
            [2, 1, 3], vertical_alignment="center"
        )

        with type_col:
            st.html(type_icons_html([attack_type]))

        count_col.markdown(f"**{len(weak_members)} of {len(team_data)}**")
        sprites_col.image(sprite_urls, width=45, alt=names)


page_header("Team Builder", TEAM_EMBLEM)


# Start from the team in the URL, e.g. ?team=Pikachu,Gengar
if "team" not in st.session_state:
    st.session_state.team = parse_team(
        st.query_params.get("team", ""), set(pokemon["Name"])
    )


def add_to_team():
    name = st.session_state.team_pick
    if name and name not in st.session_state.team:
        st.session_state.team.append(name)
        st.session_state.team_pick = None


def remove_from_team(name):
    st.session_state.team.remove(name)


team = st.session_state.team

# Keep the URL in sync so the team can be shared or bookmarked
if team:
    st.query_params["team"] = ",".join(team)
else:
    st.query_params.pop("team", None)


if len(team) < MAX_TEAM_SIZE:
    available = pokemon.loc[~pokemon["Name"].isin(team), "Name"].sort_values()

    selected = st.selectbox(
        "Choose a Pokémon",
        available,
        index=None,
        placeholder="Search for a Pokémon...",
        key="team_pick",
    )
    st.caption(f"{len(team)}/{MAX_TEAM_SIZE} Pokémon selected")

    if selected is not None:
        st.subheader(str(selected))
        pokemon_summary(find_pokemon(pokemon, str(selected)))

    st.button(
        "Add to team",
        on_click=add_to_team,
        disabled=selected is None,
    )
else:
    st.caption(f"{MAX_TEAM_SIZE}/{MAX_TEAM_SIZE} Pokémon selected")


if team:
    st.subheader("Your team")

    for start in range(0, len(team), 3):
        row = team[start : start + 3]

        for column, name in zip(st.columns(3), row):
            member = find_pokemon(pokemon, name)

            with column, st.container(border=True):
                st.image(sprite_url(member), width=120)

                name_col, remove_col = st.columns([6, 1], vertical_alignment="center")

                with name_col:
                    st.markdown(f"**{name}**")

                with remove_col:
                    st.button(
                        ":primary[✕]",
                        key=f"remove_{name}",
                        help=f"Remove {name} from team",
                        on_click=remove_from_team,
                        args=(name,),
                        type="tertiary",
                        width="content",
                    )


if team:
    team_data = pokemon.loc[pokemon["Name"].isin(team)]
    averages = {stat: float(team_data[stat].mean()) for stat in STATS}

    st.subheader("Analysis")

    with st.container(border=True):
        st.caption("AVERAGE BASE STATS")
        for column, stat in zip(st.columns(6), STATS):
            column.metric(stat, f"{averages[stat]:.1f}")

    type_counts = (
        pd.concat([team_data["Type1"], team_data["Type2"]]).dropna().value_counts()
    )

    st.caption("TYPE MIX")

    for type_name, count in type_counts.items():
        name_col, icons_col = st.columns([1, 4], vertical_alignment="center")
        name_col.markdown(f"**{type_name}**")
        icons_col.html(
            type_icons_html([str(type_name)] * int(count), show_names=False)
        )

    highest_stat = max(STATS, key=lambda stat: averages[stat])
    lowest_stat = min(STATS, key=lambda stat: averages[stat])

    strong_col, low_col = st.columns(2)

    with strong_col.container(border=True):
        st.metric("Highest stat", highest_stat)
        st.caption(f"Team average: {averages[highest_stat]:.1f}")

    with low_col.container(border=True):
        st.metric("Lowest stat", lowest_stat)
        st.caption(f"Team average: {averages[lowest_stat]:.1f}")

    attack_types = sorted(
        set(pokemon["Type1"].dropna()) | set(pokemon["Type2"].dropna())
    )

    team_weaknesses = []

    try:
        for attack_type in attack_types:
            weak_members = []

            for name in team:
                multiplier = damage_multiplier(attack_type, find_pokemon(team_data, name))

                if multiplier > 1:
                    weak_members.append((name, multiplier))

            if weak_members:
                team_weaknesses.append((attack_type, weak_members))

        team_weaknesses.sort(
            key=lambda result: len(result[1]),
            reverse=True,
        )

        st.subheader("Weaknesses")

        for attack_type, weak_members in team_weaknesses[:3]:
            show_weakness_row(attack_type, weak_members, team_data)

        if len(team_weaknesses) > 3:
            with st.expander("See all weaknesses"):
                for attack_type, weak_members in team_weaknesses[3:]:
                    show_weakness_row(attack_type, weak_members, team_data)

    except requests.RequestException:
        st.warning("Could not load type matchups right now.")
