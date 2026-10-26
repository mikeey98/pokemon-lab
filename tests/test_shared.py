import pandas as pd
from shared.data import load_pokemon, sprite_url, types_of
from shared.names import is_correct_guess, species_name


def row(name, num, type1, type2=None):
    return pd.Series({"Name": name, "Num": num, "Type1": type1, "Type2": type2})


def test_species_name_drops_form():
    assert species_name("Deoxys Normal Forme") == "Deoxys"
    assert species_name("Zygarde 50% Forme") == "Zygarde"
    assert species_name("Meowstic Male") == "Meowstic"
    assert species_name("Mr. Mime") == "Mr. Mime"


def test_guess_ignores_case_accents_and_symbols():
    assert is_correct_guess("flabebe", "Flabébé")
    assert is_correct_guess("Nidoran", "Nidoran♀")
    assert is_correct_guess("mr mime", "Mr. Mime")
    assert is_correct_guess("deoxys", "Deoxys Normal Forme")
    assert not is_correct_guess("", "Pikachu")
    assert not is_correct_guess("Raichu", "Pikachu")


def test_types_of_skips_missing_second_type():
    assert types_of(row("Pikachu", 25, "Electric")) == ["Electric"]
    assert types_of(row("Bulbasaur", 1, "Grass", "Poison")) == ["Grass", "Poison"]


def test_sprite_url_uses_form_id():
    assert sprite_url(row("Pikachu", 25, "Electric")).endswith("/25.png")
    assert sprite_url(row("Mega Venusaur", 3, "Grass")).endswith("/10033.png")


def test_clean_data_has_no_broken_names():
    names = load_pokemon()["Name"]
    assert not names.str.contains("Ã|â").any()
    assert names.is_unique
