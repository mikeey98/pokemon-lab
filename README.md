# Pokémon Lab

A playful Streamlit app for exploring Pokémon from generation 1–6.

| Page | What you can do |
|---|---|
| Twins | Find the five Pokémon with the most similar base stats |
| Mega Evolution | See how a Mega form changes a Pokémon's stats |
| Compare | Put two Pokémon side by side |
| Who's That Pokémon? | Guess the silhouette, with hints after each wrong guess |
| Pokédex | Pokédex entry, evolution family and Mega forms |
| Team Builder | Build a team of six and see its shared weaknesses |
| Pokébot | Chat about a Pokémon with a local AI model (optional) |

## Run it

```bash
pip install -r requirements.txt
streamlit run app.py
```

Pokébot needs [Ollama](https://ollama.com) running locally with the `qwen3:1.7b` model:

```bash
ollama pull qwen3:1.7b
```

All other pages work without it.

## Project structure

```
app.py               navigation between the pages
pages/               one file per page
shared/              data loading, page layout, type icons, AI helper
data/                raw and cleaned CSV
pipeline.ipynb       cleans PokemonData.csv into PokemonData_clean.csv
experiments/         small scripts for trying things out
tests/               pytest tests for the shared helpers
```

## Tests

```bash
pip install pytest
python3 -m pytest
```

## Data and credits

- Base stats: Pokémon dataset (gen 1–6), cleaned in `pipeline.ipynb`.
- Sprites, Pokédex entries, evolutions and type matchups: [PokeAPI](https://pokeapi.co).
- Type symbols: [duiker101/pokemon-type-svg-icons](https://github.com/duiker101/pokemon-type-svg-icons).

Fan project, not affiliated with Nintendo, Game Freak or The Pokémon Company.
Pokémon and Pokémon names are trademarks of their respective owners.
