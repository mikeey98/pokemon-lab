from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from shared.sprite_ids import special_sprite_ids
from shared.type_icons import type_icons_html

data_path = Path(__file__).parent.parent / "data" / "PokemonData_clean.csv"
pokemon = pd.read_csv(data_path)


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

    for column in ("Type1", "Type2"):
        if pd.isna(member[column]):
            continue

        relations = get_type_relations(str(member[column]))

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
        member = team_data.loc[team_data["Name"].eq(name)].iloc[0]
        sprite_id = special_sprite_ids.get(name, int(member["Num"]))
        sprite_urls.append(
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            f"sprites/pokemon/{sprite_id}.png"
        )
        names.append(name)

    with st.container(border=True):
        type_col, count_col, sprites_col = st.columns(
            [2, 1, 3], vertical_alignment="center"
        )

        with type_col:
            st.html(type_icons_html([attack_type]))

        count_col.markdown(f"**{len(weak_members)} of 6**")
        sprites_col.image(sprite_urls, width=45, alt=names)


# Six circles represent the six members of a complete team.

team_circles = (
    '<span style="width:30px;height:30px;border:7px solid #C73E3E;'
    'border-radius:50%;box-sizing:border-box;"></span>'
) * 6

st.html(f"""
<div style="position:relative;overflow:hidden;height:150px;
            display:flex;align-items:center;">
    <div style="position:absolute;right:18px;top:0;
                width:150px;height:150px;
                display:grid;grid-template-columns:repeat(3, 30px);
                gap:14px;place-content:center;opacity:0.25;">
        {team_circles}
    </div>
    <h1 style="position:relative;margin:0;color:#24334A;
               font-family:Nunito,sans-serif;">
        Team Builder
    </h1>
</div>
""")


if "team" not in st.session_state:
    st.session_state.team = []


def add_to_team():
    name = st.session_state.team_pick
    if name and name not in st.session_state.team:
        st.session_state.team.append(name)
        st.session_state.team_pick = None


def remove_from_team(name):
    st.session_state.team.remove(name)


team = st.session_state.team


if len(team) < 6:
    available = pokemon.loc[~pokemon["Name"].isin(team), "Name"].sort_values()

    selected = st.selectbox(
        "Choose a Pokémon",
        available,
        index=None,
        placeholder="Search for a Pokémon...",
        key="team_pick",
    )
    st.caption(f"{len(team)}/6 Pokémon selected")

    if selected is not None:
        chosen = pokemon.loc[pokemon["Name"].eq(selected)].iloc[0]
        sprite_id = special_sprite_ids.get(str(selected), int(chosen["Num"]))
        sprite_url = (
            "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
            f"sprites/pokemon/{sprite_id}.png"
        )

        st.subheader(str(selected))
        image_col, info_col = st.columns([1, 4])

        with image_col:
            st.image(sprite_url, width=150)

        with info_col:
            types = [
                str(chosen[column])
                for column in ("Type1", "Type2")
                if pd.notna(chosen[column])
            ]
            st.html(type_icons_html(types))

            stats = ["HP", "Attack", "Defense", "SpAtk", "SpDef", "Speed"]
            for column, stat in zip(st.columns(6), stats):
                column.metric(stat, int(chosen[stat]))

    st.button(
        "Add to team",
        on_click=add_to_team,
        disabled=selected is None,
    )
else:
    st.caption("6/6 Pokémon selected")


if team:
    st.subheader("Your team")

    for start in range(0, len(team), 3):
        row = team[start : start + 3]

        for column, name in zip(st.columns(3), row):
            member = pokemon.loc[pokemon["Name"].eq(name)].iloc[0]
            sprite_id = special_sprite_ids.get(str(name), int(member["Num"]))
            sprite_url = (
                "https://raw.githubusercontent.com/PokeAPI/sprites/master/"
                f"sprites/pokemon/{sprite_id}.png"
            )

            with column, st.container(border=True):
                st.image(sprite_url, width=120)

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


if len(team) == 6:
    team_data = pokemon.loc[pokemon["Name"].isin(team)]
    stats = ["HP", "Attack", "Defense", "SpAtk", "SpDef", "Speed"]
    averages = {stat: float(team_data[stat].mean()) for stat in stats}

    st.subheader("Analysis")

    with st.container(border=True):
        st.caption("AVERAGE BASE STATS")
        for column, stat in zip(st.columns(6), stats):
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

    highest_stat = max(stats, key=lambda stat: averages[stat])
    lowest_stat = min(stats, key=lambda stat: averages[stat])

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
                member = team_data.loc[team_data["Name"].eq(name)].iloc[0]
                multiplier = damage_multiplier(attack_type, member)

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
