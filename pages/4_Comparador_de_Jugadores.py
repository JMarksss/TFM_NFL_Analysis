"""
Created on Aug Wed 6 19:12:24 2025

@author: jmarcos
"""

# Importamos las librerías
import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Comparador de Jugadores Ofensivos",
    page_icon="⚔️",
    layout="wide"
)

# --- Carga de Datos ---
@st.cache_data
def load_data(file_path):
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"Error: No se encontró el fichero en la ruta: {file_path}")
        return None

player_df_raw = load_data('detailed_player_stats_advanced_2020-2024.csv')

# --- Título Principal ---
st.title("⚔️ Comparador de Jugadores Ofensivos")
st.markdown("Selecciona una posición, dos jugadores y una temporada para comparar su rendimiento.")
st.divider()

# --- Pre-procesamiento de Datos ---
if player_df_raw is not None:
    player_df = player_df_raw.copy()
    qb_metrics_to_sum = ['passing_tds', 'rushing_tds', 'passing_first_downs', 'rushing_first_downs', 'interceptions', 'rushing_fumbles_lost', 'sack_fumbles_lost', 'sacks']
    for metric in qb_metrics_to_sum:
        if metric not in player_df.columns:
            player_df[metric] = 0
    player_df.fillna(0, inplace=True)
    #Métricas combinadas (totales) para los QB
    player_df['total_tds'] = player_df['passing_tds'] + player_df['rushing_tds']
    player_df['total_first_downs'] = player_df['passing_first_downs'] + player_df['rushing_first_downs']
    player_df['total_turnovers'] = player_df['interceptions'] + player_df['rushing_fumbles_lost'] + player_df['sack_fumbles_lost']
else:
    st.warning("No se pudieron cargar los datos.")
    st.stop()

# --- Filtros Principales ---
col1, col2 = st.columns(2)
with col1:
    selected_year = st.selectbox("Selecciona una Temporada:", sorted(player_df['year'].unique(), reverse=True))
with col2:
    selected_position = st.selectbox("Selecciona una Posición:", ['QB', 'RB', 'Receptor'])

# --- Slider para Mínimo de Participación ---
st.sidebar.header("Filtro de Participación Mínima")
if selected_position == 'QB':
    min_attempts = st.sidebar.slider("Mínimo de Intentos de Pase:", 0, 600, 100, key="comp_qb")
elif selected_position == 'RB':
    min_attempts = st.sidebar.slider("Mínimo de Intentos de Carrera:", 0, 400, 50, key="comp_rb")
else: # Receptor
    min_attempts = st.sidebar.slider("Mínimo de Targets:", 0, 200, 50, key="comp_rec")

# Filtrar dataframe por año, posición y participación
year_position_df = player_df[player_df['year'] == selected_year]
if selected_position == 'Receptor':
    year_position_df = year_position_df[year_position_df['position'].isin(['WR', 'TE'])]
    year_position_df = year_position_df[year_position_df['targets'] >= min_attempts]
elif selected_position == 'QB':
    year_position_df = year_position_df[year_position_df['position'] == 'QB']
    year_position_df = year_position_df[year_position_df['attempts'] >= min_attempts]
else: # RB
    year_position_df = year_position_df[year_position_df['position'] == 'RB']
    year_position_df = year_position_df[year_position_df['carries'] >= min_attempts]

# --- Filtros de Jugadores ---
st.markdown("---")
if year_position_df.empty:
    st.warning("No hay jugadores que cumplan el criterio de participación mínima. Por favor, ajusta el filtro en la barra lateral.")
    st.stop()

col_a1, col_a2, col_b1, col_b2 = st.columns(4)
with col_a1:
    team_a_options = ['Todos'] + sorted(year_position_df['team'].dropna().unique())
    team_a_filter = st.selectbox("Filtrar Equipo A:", team_a_options, key='team_a')
with col_a2:
    players_a = year_position_df[year_position_df['team'] == team_a_filter] if team_a_filter != 'Todos' else year_position_df
    player_a_name = st.selectbox("Selecciona Jugador A:", sorted(players_a['player_name'].unique()))
with col_b1:
    team_b_options = ['Todos'] + sorted(year_position_df['team'].dropna().unique())
    team_b_filter = st.selectbox("Filtrar Equipo B:", team_b_options, key='team_b')
with col_b2:
    players_b = year_position_df[year_position_df['team'] == team_b_filter] if team_b_filter != 'Todos' else year_position_df
    player_b_name = st.selectbox("Selecciona Jugador B:", sorted(players_b['player_name'].unique()), index=1 if len(players_b) > 1 else 0)

# --- Lógica de Comparación ---
if player_a_name == player_b_name:
    st.warning("Por favor, selecciona dos jugadores diferentes para comparar.")
else:
    radar_metrics = {} #Gráfico de radar, distintas estadísticas dependiendo de la posición, se tienen en cuenta las estadísticas invertidas
    if selected_position == 'QB':
        radar_metrics = {'EPA de Pase': ('passing_epa', True), 'EPA de Carrera': ('rushing_epa', True), 'PACR': ('pacr', True), 'DAKOTA': ('dakota', True), 'TDs Totales': ('total_tds', True), 'Primeros Downs': ('total_first_downs', True), 'Sacks': ('sacks', False), 'Pérdidas de Balón': ('total_turnovers', False)}
    elif selected_position == 'RB':
        radar_metrics = {'EPA de Carrera': ('rushing_epa', True), 'TDs de Carrera': 'rushing_tds', 'Intentos': 'carries', 'Yardas de Carrera': 'rushing_yards', 'Primeros Downs': 'rushing_first_downs', 'Fumbles': ('rushing_fumbles', False)}
        radar_metrics = {k: (v, True) if isinstance(v, str) else v for k, v in radar_metrics.items()}
    elif selected_position == 'Receptor':
        radar_metrics = {'EPA de Recepción': ('receiving_epa', True), 'TDs de Recepción': 'receiving_tds', 'RACR': ('racr', True), 'Yardas tras Recepción': 'receiving_yards_after_catch', 'Primeros Downs': 'receiving_first_downs', 'Fumbles': ('receiving_fumbles', False)}
        radar_metrics = {k: (v, True) if isinstance(v, str) else v for k, v in radar_metrics.items()}

    for metric_name, (col_name, higher_is_better) in radar_metrics.items():
        year_position_df[f'{col_name}_percentile'] = year_position_df[col_name].rank(pct=True) #ranking percentil
        if not higher_is_better:
            year_position_df[f'{col_name}_percentile'] = 1 - year_position_df[f'{col_name}_percentile'] #inversión
        year_position_df[f'{col_name}_percentile'] *= 100
    
    player_a_data = year_position_df[year_position_df['player_name'] == player_a_name].iloc[0]
    player_b_data = year_position_df[year_position_df['player_name'] == player_b_name].iloc[0]

    st.subheader(f"Comparativa de Percentiles: {player_a_name} vs. {player_b_name} ({selected_year})")
    st.markdown("El gráfico muestra el percentil de cada jugador entre los de su misma posición (un valor más alto siempre es mejor).")
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[player_a_data[f'{col}_percentile'] for col, _ in radar_metrics.values()], theta=list(radar_metrics.keys()), fill='toself', name=player_a_name, hovertemplate='<b>%{theta}</b><br>Percentil: %{r:.1f}<extra></extra>'))
    fig.add_trace(go.Scatterpolar(r=[player_b_data[f'{col}_percentile'] for col, _ in radar_metrics.values()], theta=list(radar_metrics.keys()), fill='toself', name=player_b_name, hovertemplate='<b>%{theta}</b><br>Percentil: %{r:.1f}<extra></extra>'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=True, height=500)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Estadísticas Detalladas") #Tabla comparativa con las estadísticas
    table_cols = [col for col, _ in radar_metrics.values()]
    comparison_df = pd.DataFrame({player_a_name: player_a_data[table_cols], player_b_name: player_b_data[table_cols]})
    comparison_df.index = list(radar_metrics.keys())
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"##### {player_a_name}")
        st.dataframe(comparison_df[[player_a_name]].style.format("{:.2f}"))
    with col_b:
        st.markdown(f"##### {player_b_name}")
        st.dataframe(comparison_df[[player_b_name]].style.format("{:.2f}"))

st.divider()
col3, col4, col5 = st.columns(3)
with col3:
    st.image('./Images/logo_sdc.png', width=250)
with col4:
    st.image('./Images/logo_nfl.png', width=120)
with col5:
    st.image('./Images/logo_ucam.jpg', width=100)
st.caption('Trabajo de Fin de Master - Master en Big Data Deportivo')
st.caption('NFL Analytics Hub')
st.caption('Juan Marcos Díaz')