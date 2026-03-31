import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px

DB_PATH = "data/pokemon.duckdb"

st.set_page_config(
    page_title="Pokédex Analytics",
    page_icon="⚡",
    layout="wide"
)

@st.cache_resource
def get_connection():
    return duckdb.connect(DB_PATH, read_only=True)

con = get_connection()

st.title("⚡ Pokédex Analytics")
st.markdown("*Exploring Generation I Pokémon stats, types and strengths.*")
st.divider()

total = con.execute("SELECT COUNT(*) FROM fct_pokemon").fetchone()[0]
strongest = con.execute("SELECT pokemon_name FROM fct_pokemon ORDER BY total_base_stats DESC LIMIT 1").fetchone()[0]
heaviest = con.execute("SELECT pokemon_name FROM fct_pokemon ORDER BY weight_kg DESC LIMIT 1").fetchone()[0]
num_types = con.execute("SELECT COUNT(*) FROM dim_type").fetchone()[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pokémon tracked", total)
col2.metric("Strongest", strongest.capitalize())
col3.metric("Heaviest", heaviest.capitalize())
col4.metric("Unique types", num_types)

st.divider()

st.subheader("🏆 Top 10 Strongest Pokémon")
top10 = con.execute("""
    SELECT pokemon_name, primary_type, total_base_stats, hp, attack, defense, speed
    FROM fct_pokemon
    ORDER BY total_base_stats DESC
    LIMIT 10
""").df()
top10["pokemon_name"] = top10["pokemon_name"].str.capitalize()

fig = px.bar(
    top10,
    x="total_base_stats",
    y="pokemon_name",
    orientation="h",
    color="primary_type",
    labels={"total_base_stats": "Total Base Stats", "pokemon_name": ""},
    color_discrete_sequence=px.colors.qualitative.Bold,
)
fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=True)
st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🔥 Pokémon Count by Type")
type_dist = con.execute("""
    SELECT primary_type, pokemon_count, avg_total_stats
    FROM dim_type
    ORDER BY pokemon_count DESC
""").df()

fig2 = px.bar(
    type_dist,
    x="primary_type",
    y="pokemon_count",
    color="avg_total_stats",
    color_continuous_scale="Viridis",
    labels={"primary_type": "Type", "pokemon_count": "Number of Pokémon", "avg_total_stats": "Avg Stats"},
)
st.plotly_chart(fig2, use_container_width=True)

st.divider()

st.subheader("⚔️ Attack vs Defense")
scatter_df = con.execute("""
    SELECT pokemon_name, primary_type, attack, defense, hp, total_base_stats
    FROM fct_pokemon
""").df()
scatter_df["pokemon_name"] = scatter_df["pokemon_name"].str.capitalize()

fig3 = px.scatter(
    scatter_df,
    x="attack",
    y="defense",
    color="primary_type",
    hover_name="pokemon_name",
    size="total_base_stats",
    labels={"attack": "Attack", "defense": "Defense"},
    color_discrete_sequence=px.colors.qualitative.Bold,
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.subheader("🧬 Strongest Type Combinations")
combo_df = con.execute("""
    SELECT 
        primary_type,
        COALESCE(secondary_type, 'none') as secondary_type,
        COUNT(*) as pokemon_count,
        ROUND(AVG(total_base_stats), 1) as avg_total_stats
    FROM fct_pokemon
    GROUP BY primary_type, secondary_type
    ORDER BY avg_total_stats DESC
    LIMIT 15
""").df()

combo_df["type_combo"] = combo_df["primary_type"] + " / " + combo_df["secondary_type"]

fig4 = px.bar(
    combo_df,
    x="avg_total_stats",
    y="type_combo",
    orientation="h",
    color="avg_total_stats",
    color_continuous_scale="Viridis",
    hover_data=["pokemon_count"],
    labels={"avg_total_stats": "Avg Total Stats", "type_combo": ""},
)
fig4.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig4, use_container_width=True)

st.divider()

st.subheader("🤓 Fun Facts")

facts = con.execute("""
    SELECT
        (SELECT pokemon_name FROM fct_pokemon ORDER BY weight_kg DESC LIMIT 1) as heaviest,
        (SELECT round(weight_kg,1) FROM fct_pokemon ORDER BY weight_kg DESC LIMIT 1) as heaviest_kg,
        (SELECT pokemon_name FROM fct_pokemon ORDER BY height_m DESC LIMIT 1) as tallest,
        (SELECT round(height_m,1) FROM fct_pokemon ORDER BY height_m DESC LIMIT 1) as tallest_m,
        (SELECT pokemon_name FROM fct_pokemon ORDER BY speed DESC LIMIT 1) as fastest,
        (SELECT speed FROM fct_pokemon ORDER BY speed DESC LIMIT 1) as top_speed,
        (SELECT primary_type FROM dim_type ORDER BY pokemon_count DESC LIMIT 1) as most_common_type
""").df().iloc[0]

c1, c2, c3 = st.columns(3)
c1.info(f"🏋️ **Heaviest Pokémon:** {facts['heaviest'].capitalize()} at {facts['heaviest_kg']} kg")
c2.info(f"📏 **Tallest Pokémon:** {facts['tallest'].capitalize()} at {facts['tallest_m']} m")
c3.info(f"💨 **Fastest Pokémon:** {facts['fastest'].capitalize()} with speed {int(facts['top_speed'])}")
st.info(f"🌊 **Most common type in Gen 1:** {facts['most_common_type'].capitalize()}")

st.divider()
st.caption("Data source: PokéAPI (pokeapi.co) · Gen 1 (150 Pokémon) · Built with dbt + DuckDB + Streamlit")
