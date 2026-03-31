-- Central fact table with one row per Pokémon

with pokemon as (
    select * from {{ ref('stg_pokemon') }}
)

select
    pokemon_id,
    pokemon_name,
    primary_type,
    secondary_type,
    hp,
    attack,
    defense,
    speed,
    special_attack,
    special_defense,
    total_base_stats,
    base_experience,
    height_dm,
    weight_hg,
    round(weight_hg / 10.0, 1)     as weight_kg,
    round(height_dm / 10.0, 1)     as height_m
from pokemon