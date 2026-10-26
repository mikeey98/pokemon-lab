"""Turn form names into species names and compare guesses fairly."""

import re
import unicodedata

# "Deoxys Normal Forme", "Wormadam Plant Cloak", "Meowstic Male", "Hoopa Confined" ...
FORM_SUFFIX = re.compile(
    r" (\S+ (Forme|Cloak|Mode|Size)|Male|Female|Confined|Unbound)$"
)


def species_name(name: str) -> str:
    """Drop the form part of a name: "Deoxys Normal Forme" -> "Deoxys"."""
    return FORM_SUFFIX.sub("", name)


def simplify(text: str) -> str:
    """Lowercase letters and digits only, without accents: "Flabébé" -> "flabebe"."""
    without_accents = unicodedata.normalize("NFKD", text)
    return "".join(
        character
        for character in without_accents.casefold()
        if character.isascii() and character.isalnum()
    )


def is_correct_guess(guess: str, name: str) -> bool:
    """Accept both the full name and the species name, ignoring case and symbols."""
    answers = {simplify(name), simplify(species_name(name))}
    return simplify(guess) in answers
