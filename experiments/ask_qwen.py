from pathlib import Path

import pandas as pd
from shared.pokemon_facts import build_pokemon_facts
from shared.qwen import ask_qwen

# Go from experiments/ to the project folder, then find the cleaned CSV.
data_path = Path(__file__).resolve().parent.parent / "data" / "PokemonData_clean.csv"
pokemon = pd.read_csv(data_path)

# Let the user choose which row to send to Qwen.
name = input("Choose a Pokémon: ").strip()
matches = pokemon.loc[pokemon["Name"].str.casefold().eq(name.casefold())]

if matches.empty:
    raise ValueError(f"{name!r} was not found in the dataset.")

selected = matches.iloc[0]

types = [selected["Type1"]]

if pd.notna(selected["Type2"]):
    types.append(selected["Type2"])

facts = build_pokemon_facts(selected)

question = input("Ask a question about this Pokémon: ").strip()

answer = ask_qwen(facts, question)

print("Facts sent to Qwen:")
print(facts)
print("\nQwen's answer:")
print(answer)