-- Dimension table: one row per type with aggregated stats

with pokemon_type_stats as (
    select * from {{ ref('stg_pokemon') }}
)
    select
        primary_type,
        count(distinct pokemon_id)        as pokemon_count,
        round(avg(hp), 1)                 as avg_hp,
        round(avg(attack), 1)             as avg_attack,
        round(avg(defense), 1)            as avg_defense,
        round(avg(speed), 1)              as avg_speed,
        round(avg(total_base_stats), 1)   as avg_total_stats,
        max(total_base_stats)             as max_total_stats
    from pokemon_type_stats
    group by primary_type
order by avg_total_stats desc