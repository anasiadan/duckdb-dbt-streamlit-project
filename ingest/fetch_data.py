import requests
import duckdb
import time

DB_PATH = "data/pokemon.duckdb"
POKEAPI_BASE = "https://pokeapi.co/api/v2"
POKEMON_LIMIT = 150

# Fetch list of Pokemon 
def fetch_pokemon_list(limit: int) -> list:
    url = f"{POKEAPI_BASE}/pokemon?limit={limit}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["results"]

# Fetch detailed data for a single Pokemon
def fetch_pokemon_detail(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# Extract relevant fields for the Pokemon record, parsing stats from a list into flat fields.
def extract_pokemon_record(data: dict) -> dict:
    return {
        "id": data["id"],
        "name": data["name"],
        "base_experience": data["base_experience"],
        "height": data["height"],
        "weight": data["weight"],
        "hp": next((s["base_stat"] for s in data["stats"] if s["stat"]["name"] == "hp"), None),
        "attack": next((s["base_stat"] for s in data["stats"] if s["stat"]["name"] == "attack"), None),
        "defense": next((s["base_stat"] for s in data["stats"] if s["stat"]["name"] == "defense"), None),
        "speed": next((s["base_stat"] for s in data["stats"] if s["stat"]["name"] == "speed"), None),
        "special_attack": next((s["base_stat"] for s in data["stats"] if s["stat"]["name"] == "special-attack"), None),
        "special_defense": next((s["base_stat"] for s in data["stats"] if s["stat"]["name"] == "special-defense"), None),
        "primary_type": data["types"][0]["type"]["name"],
        "secondary_type": data["types"][1]["type"]["name"] if len(data["types"]) > 1 else None,
    }


# Create raw tables in DuckDB from the extracted pokemon and type records.
def save_to_duckdb(pokemon_records: list) -> None:
    con = duckdb.connect(DB_PATH)

    con.execute("DROP TABLE IF EXISTS raw_pokemon")
    con.execute("""
        CREATE TABLE raw_pokemon AS
        SELECT * FROM (VALUES {values}) AS t(
            id, name, base_experience, height, weight,
            hp, attack, defense, speed, special_attack, special_defense, primary_type, secondary_type
        )
    """.format(
        values=", ".join(
            f"({r['id']}, '{r['name']}', {r['base_experience'] or 'NULL'}, "
            f"{r['height']}, {r['weight']}, "
            f"{r['hp'] or 'NULL'}, {r['attack'] or 'NULL'}, "
            f"{r['defense'] or 'NULL'}, {r['speed'] or 'NULL'}, "
            f"{r['special_attack'] or 'NULL'}, {r['special_defense'] or 'NULL'}, "
            f"'{r['primary_type']}', {'NULL' if r['secondary_type'] is None else repr(r['secondary_type'])})"
            for r in pokemon_records
        )
    ))


    con.close()

def main():
    print("Fetching Pokémon data from PokéAPI...")
    pokemon_list = fetch_pokemon_list(POKEMON_LIMIT)

    pokemon_records = []

    for i, entry in enumerate(pokemon_list):
        print(f"  Fetching {entry['name']} ({i+1}/{len(pokemon_list)})")
        detail = fetch_pokemon_detail(entry["url"])
        pokemon_records.append(extract_pokemon_record(detail))
        time.sleep(0.05)  # Be polite to the API

    # Write to DuckDB
    save_to_duckdb(pokemon_records)
    print(f"Done! {len(pokemon_records)} Pokémon saved to {DB_PATH}")


if __name__ == "__main__":
    main()