"""Round Pokémon type symbols and their display colours.

White SVG symbols: https://github.com/duiker101/pokemon-type-svg-icons
"""

from base64 import b64encode
from pathlib import Path


TYPE_COLORS = {
    "Normal": ("#A0A29F", "#747674"),
    "Fighting": ("#D3425F", "#C33150"),
    "Flying": ("#A1BBEC", "#577CB8"),
    "Poison": ("#B763CF", "#9850AF"),
    "Ground": ("#DA7C4D", "#AE6039"),
    "Rock": ("#C9BB8A", "#89794B"),
    "Bug": ("#92BC2C", "#6B8B1D"),
    "Ghost": ("#5F6DBC", "#4B59A4"),
    "Steel": ("#5695A3", "#397987"),
    "Fire": ("#FBA54C", "#D94A32"),
    "Water": ("#539DDF", "#2877C1"),
    "Grass": ("#5FBD58", "#358E35"),
    "Electric": ("#F2D94E", "#9A7B00"),
    "Psychic": ("#FA8581", "#D65467"),
    "Ice": ("#75D0C1", "#338F86"),
    "Dragon": ("#0C69C8", "#0C61B5"),
    "Dark": ("#595761", "#595761"),
    "Fairy": ("#EE90E6", "#BD5AB9"),
}

TYPE_ICON_DIR = Path(__file__).parent.parent / "assets" / "type_symbols"


def type_icons_html(type_names: list[str], show_names: bool = True) -> str:
    """Show each type as a round symbol followed by coloured text."""
    items = []
    for name in type_names:
        circle_color, text_color = TYPE_COLORS[name]
        svg = (TYPE_ICON_DIR / f"{name.lower()}.svg").read_bytes()
        image = b64encode(svg).decode("ascii")
        label_html = (
            f'<span style="color:{text_color};">{name}</span>' if show_names else ""
        )
        items.append(
            '<span style="display:inline-flex;align-items:center;gap:7px;'
            'white-space:nowrap;font-weight:700;">'
            f'<span style="display:inline-flex;width:28px;height:28px;'
            f"border-radius:50%;background:{circle_color};align-items:center;"
            'justify-content:center;">'
            f'<img src="data:image/svg+xml;base64,{image}" alt="" '
            'style="width:19px;height:19px;">'
            "</span>"
            f"{label_html}"
            "</span>"
        )

    return (
        '<div style="display:flex;flex-wrap:wrap;gap:14px;margin:0 0 12px;">'
        + "".join(items)
        + "</div>"
    )
