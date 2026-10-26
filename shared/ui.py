"""Page headers and Pokémon cards shared by the app pages."""

import pandas as pd
import streamlit as st

from shared.data import STATS, sprite_url, types_of
from shared.type_icons import type_icons_html

RED = "#C73E3E"
NAVY = "#24334A"
BACKGROUND = "#F7F5EF"

POKEBALL_EMBLEM = f"""
<div style="position:relative; width:100%; height:100%; box-sizing:border-box;
            border:9px solid {RED}; border-radius:50%;">
    <div style="position:absolute; left:0; right:0; top:50%; height:9px;
                background:{RED}; transform:translateY(-50%);"></div>
    <div style="position:absolute; left:50%; top:50%; width:36px; height:36px;
                box-sizing:border-box; transform:translate(-50%,-50%);
                border:9px solid {RED}; border-radius:50%;
                background:{BACKGROUND};"></div>
</div>
"""

# Six circles represent the six members of a complete team.
TEAM_EMBLEM = (
    '<div style="width:100%; height:100%; display:grid;'
    ' grid-template-columns:repeat(3, 30px); gap:14px; place-content:center;">'
    + (
        f'<span style="width:30px; height:30px; border:7px solid {RED};'
        ' border-radius:50%; box-sizing:border-box;"></span>'
    )
    * 6
    + "</div>"
)


def text_emblem(text: str, font_size: int) -> str:
    """A red ring with a symbol inside, e.g. "VS" or "?"."""
    return f"""
    <div style="width:100%; height:100%; box-sizing:border-box;
                border:9px solid {RED}; border-radius:50%;
                display:flex; align-items:center; justify-content:center;
                color:{RED}; font:900 {font_size}px Nunito,sans-serif;">
        {text}
    </div>
    """


def page_header(title: str, emblem_html: str) -> None:
    """Title on the left with a faded emblem behind it on the right."""
    st.html(f"""
    <div style="position:relative; overflow:hidden; height:150px;
                display:flex; align-items:center;">
        <div style="position:absolute; right:18px; top:0;
                    width:150px; height:150px; opacity:0.25;">
            {emblem_html}
        </div>
        <h1 style="position:relative; margin:0; color:{NAVY};
                   font-family:Nunito,sans-serif;">
            {title}
        </h1>
    </div>
    """)


def stat_metrics(row: pd.Series, compare_to: pd.Series | None = None) -> None:
    """Six base stats in a row, optionally with the difference to another Pokémon."""
    for column, stat in zip(st.columns(6), STATS):
        if compare_to is None:
            column.metric(stat, int(row[stat]))
        else:
            difference = int(row[stat]) - int(compare_to[stat])
            column.metric(
                stat,
                int(row[stat]),
                delta=f"{difference:+d}",
                delta_color="off",
                delta_arrow="off",
            )


def pokemon_summary(
    row: pd.Series,
    compare_to: pd.Series | None = None,
    sprite_width: int = 150,
) -> None:
    """Sprite on the left, types and base stats on the right."""
    image_col, info_col = st.columns([1, 4])

    with image_col:
        st.image(sprite_url(row), width=sprite_width)

    with info_col:
        st.html(type_icons_html(types_of(row)))
        stat_metrics(row, compare_to)
