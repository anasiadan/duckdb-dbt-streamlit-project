WITH pokemons AS (
    SELECT
        id as pokemon_id,
        name as pokemon_name,
        base_experience,
        height as height_dm,   -- decimetres
        weight as weight_hg,   -- hectograms
        hp,
        attack,
        defense,
        speed,
        special_attack,
        special_defense,
        primary_type,
        secondary_type,
        (hp + attack + defense + speed + special_attack + special_defense) as total_base_stats
    FROM raw_pokemon
)
SELECT * FROM pokemons
