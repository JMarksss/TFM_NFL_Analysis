"""
Created on Aug Tue 12 11:27:54 2025

@author: jmarcos
"""

# Imporamos las librerías
import streamlit as st
import pandas as pd
import os
import plotly.express as px

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Evolución y Tendencias",
    page_icon="📈",
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

offensive_df = load_data('offensive_team_stats_advanced_2020-2024.csv')
defensive_df = load_data('defensive_team_stats_advanced_2020-2024.csv')
player_df_raw = load_data('detailed_player_stats_advanced_2020-2024.csv')

# --- Título Principal ---
st.title("📈 Evolución y Tendencias Temporales")
st.markdown("Analiza la progresión de dos equipos o jugadores y permite comparar su evolución a lo largo de las temporadas regulares 2020-2024.")
st.divider()

# --- Pre-procesamiento y Unión de Datos ---
if offensive_df is None or defensive_df is None or player_df_raw is None:
    st.warning("No se pudieron cargar todos los datos necesarios. Por favor, verifica la ruta de los ficheros CSV.")
    st.stop()

# Unir dataframes de equipos
team_df = pd.merge(offensive_df, defensive_df, on=['team', 'year', 'conference', 'division'])
player_df = player_df_raw.copy()


# --- Función para crear gráficos de líneas ---
def create_line_chart(df, entities, metric_col, metric_name, entity_col):
    """Crea un gráfico de líneas para comparar la evolución de dos entidades."""
    
    chart_data = df[df[entity_col].isin(entities)]
    
    if chart_data.empty or chart_data.shape[0] < 2: #Mínimo 2 años/temporadas
        st.warning(f"No hay suficientes datos para mostrar la evolución de '{metric_name}'. Uno de los seleccionados podría no tener datos para el rango de años.")
        return

    fig = px.line(
        chart_data,
        x='year',
        y=metric_col,
        color=entity_col,
        markers=True,
        labels={'year': 'Temporada', metric_col: metric_name, entity_col: 'Entidad'}
    )
    
    fig.update_layout(
        title=f'Evolución de {metric_name} ({entities[0]} vs. {entities[1]})',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, type='category'), # Tratar años como categorías
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),
        legend_title_text=''
    )
    st.plotly_chart(fig, use_container_width=True)


# --- Selección Principal: Equipo o Jugador ---
analysis_type = st.selectbox("¿Qué deseas analizar?", ["Equipos", "Jugadores"])
st.divider()

# --- LÓGICA PARA ANÁLISIS DE EQUIPOS ---
if analysis_type == "Equipos":
    teams = sorted(team_df['team'].unique())
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Selecciona el Equipo A:", teams, index=teams.index('KC') if 'KC' in teams else 0)
    with col2:
        team_b = st.selectbox("Selecciona el Equipo B:", teams, index=teams.index('SF') if 'SF' in teams else 1)

    if team_a == team_b:
        st.warning("Por favor, selecciona dos equipos diferentes.")
    else:
        # Definir métricas
        offensive_total_metrics = {'Yardas Totales': 'total_yards', 'Jugadas Totales': 'total_plays', 'Yardas por Jugada': 'yards_per_play', 'TDs Ofensivos': 'offensive_tds', 'Pérdidas de Balón': 'total_turnovers'}
        offensive_pass_metrics = {'Yardas de Pase': 'passing_yards', 'TDs de Pase': 'passing_tds', 'Pases Completados': 'pass_completions', 'Intentos de Pase': 'pass_attempts', '% Pases Completados': 'cmp_percentage', 'Yardas por Intento de Pase': 'yards_per_pass', 'Yardas Netas por Pase': 'net_yards_per_pass', 'Ratio TD/INT': 'pass_td_int_ratio', 'Intercepciones Lanzadas': 'interceptions', 'Sacks Sufridos': 'sacks_taken'}
        offensive_rush_metrics = {'Yardas de Carrera': 'rushing_yards', 'TDs de Carrera': 'rushing_tds', 'Intentos de Carrera': 'rush_attempts', 'Yardas por Intento de Carrera': 'yards_per_rush', 'Fumbles Perdidos': 'fumbles_lost'}
        
        defensive_total_metrics = {'Yardas Totales Permitidas': 'total_yards_allowed', 'Jugadas Totales Enfrentadas': 'total_plays_faced', 'Yardas por Jugada Permitidas': 'yards_per_play_allowed', 'TDs Ofensivos Permitidos': 'offensive_tds_allowed', 'Pérdidas de Balón Forzadas': 'turnovers_forced'}
        defensive_pass_metrics = {'Yardas de Pase Permitidas': 'passing_yards_allowed', 'TDs de Pase Permitidos': 'passing_tds_allowed', 'Intercepciones Realizadas': 'interceptions_made', 'Sacks Realizados': 'sacks_made', '% Pases Completados del Rival': 'opponent_cmp_percentage', 'Yardas por Intento de Pase Permitidas': 'yards_per_pass_allowed', '% de Sacks por Jugada de Pase': 'sack_rate'}
        defensive_rush_metrics = {'Yardas de Carrera Permitidas': 'rushing_yards_allowed', 'TDs de Carrera Permitidos': 'rushing_tds_allowed', 'Yardas por Intento de Carrera Permitidas': 'yards_per_rush_allowed', 'Fumbles Forzados': 'fumbles_forced'}
        
        # Visualización en expanders
        with st.expander("📊 Estadísticas Totales", expanded=True):
            off_col, def_col = st.columns(2)
            with off_col:
                selected_metric_name = st.selectbox("Métrica Ofensiva:", list(offensive_total_metrics.keys()), key='off_total')
                create_line_chart(team_df, [team_a, team_b], offensive_total_metrics[selected_metric_name], selected_metric_name, 'team')
            with def_col:
                selected_metric_name = st.selectbox("Métrica Defensiva:", list(defensive_total_metrics.keys()), key='def_total')
                create_line_chart(team_df, [team_a, team_b], defensive_total_metrics[selected_metric_name], selected_metric_name, 'team')

        with st.expander("✈️ Estadísticas de Pase"):
            off_col, def_col = st.columns(2)
            with off_col:
                selected_metric_name = st.selectbox("Métrica Ofensiva:", list(offensive_pass_metrics.keys()), key='off_pass')
                create_line_chart(team_df, [team_a, team_b], offensive_pass_metrics[selected_metric_name], selected_metric_name, 'team')
            with def_col:
                selected_metric_name = st.selectbox("Métrica Defensiva:", list(defensive_pass_metrics.keys()), key='def_pass')
                create_line_chart(team_df, [team_a, team_b], defensive_pass_metrics[selected_metric_name], selected_metric_name, 'team')

        with st.expander("🏃‍♂️ Estadísticas de Carrera"):
            off_col, def_col = st.columns(2)
            with off_col:
                selected_metric_name = st.selectbox("Métrica Ofensiva:", list(offensive_rush_metrics.keys()), key='off_rush')
                create_line_chart(team_df, [team_a, team_b], offensive_rush_metrics[selected_metric_name], selected_metric_name, 'team')
            with def_col:
                selected_metric_name = st.selectbox("Métrica Defensiva:", list(defensive_rush_metrics.keys()), key='def_rush')
                create_line_chart(team_df, [team_a, team_b], defensive_rush_metrics[selected_metric_name], selected_metric_name, 'team')


# --- LÓGICA PARA ANÁLISIS DE JUGADORES ---
elif analysis_type == "Jugadores":
    selected_position = st.selectbox("Selecciona una Posición:", ['QB', 'RB', 'Receptor'])

    st.sidebar.header("Filtro de Participación Mínima")
    if selected_position == 'QB':
        min_attempts = st.sidebar.slider("Mínimo de Intentos de Pase (promedio por año):", 0, 500, 100)
        player_df = player_df[player_df['attempts'] >= min_attempts]
    elif selected_position == 'RB':
        min_attempts = st.sidebar.slider("Mínimo de Intentos de Carrera (promedio por año):", 0, 300, 50)
        player_df = player_df[player_df['carries'] >= min_attempts]
    else: # Receptor
        min_attempts = st.sidebar.slider("Mínimo de Targets (promedio por año):", 0, 150, 40)
        player_df = player_df[player_df['targets'] >= min_attempts]

    # Filtrar por posición
    if selected_position == 'Receptor':
        position_filtered_df = player_df[player_df['position'].isin(['WR', 'TE'])]
    else:
        position_filtered_df = player_df[player_df['position'] == selected_position]
    
    if position_filtered_df.empty:
        st.warning("No hay jugadores que cumplan los filtros. Ajusta el filtro de participación.")
    else:
        players = sorted(position_filtered_df['player_name'].unique())
        col1, col2 = st.columns(2)
        with col1:
            player_a = st.selectbox("Selecciona el Jugador A:", players)
        with col2:
            player_b = st.selectbox("Selecciona el Jugador B:", players, index=1 if len(players) > 1 else 0)

        if player_a == player_b:
            st.warning("Por favor, selecciona dos jugadores diferentes.")
        else:
            # Definir métricas por posición
            player_metrics = {}
            if selected_position == 'QB':
                player_metrics = {'Yardas de Pase': 'passing_yards', 'TDs de Pase': 'passing_tds', 'EPA de Pase': 'passing_epa', 'Completions': 'completions', 'Intentos': 'attempts', 'Intercepciones': 'interceptions', 'Sacks': 'sacks', 'Yardas Aéreas': 'passing_air_yards', 'Yardas tras Recepción': 'passing_yards_after_catch', 'Primeros Downs de Pase': 'passing_first_downs', 'Conversiones de 2pts': 'passing_2pt_conversions', 'PACR': 'pacr', 'DAKOTA': 'dakota', 'Yardas de Carrera': 'rushing_yards', 'TDs de Carrera': 'rushing_tds', 'EPA de Carrera': 'rushing_epa', 'Intentos de Carrera': 'carries', 'Fumbles en Carrera': 'rushing_fumbles', 'Fumbles Perdidos': 'rushing_fumbles_lost', 'Primeros Downs de Carrera': 'rushing_first_downs', 'Conversiones de 2pts': 'rushing_2pt_conversions'}
            elif selected_position == 'RB':
                player_metrics = {'Yardas de Carrera': 'rushing_yards', 'TDs de Carrera': 'rushing_tds', 'EPA de Carrera': 'rushing_epa', 'Intentos de Carrera': 'carries', 'Fumbles': 'rushing_fumbles', 'Fumbles Perdidos': 'rushing_fumbles_lost', 'Primeros Downs de Carrera': 'rushing_first_downs', 'Conversiones de 2pts': 'rushing_2pt_conversions'}
            elif selected_position == 'Receptor':
                player_metrics = {'Yardas de Recepción': 'receiving_yards', 'TDs de Recepción': 'receiving_tds', 'EPA de Recepción': 'receiving_epa', 'Recepciones': 'receptions', 'Targets': 'targets', 'Yardas Aéreas': 'receiving_air_yards', 'Yardas tras Recepción': 'receiving_yards_after_catch', 'Fumbles': 'receiving_fumbles', 'Fumbles Perdidos': 'receiving_fumbles_lost', 'Primeros Downs de Recepción': 'receiving_first_downs', 'Conversiones de 2pts': 'receiving_2pt_conversions', 'RACR': 'racr', 'Cuota de Targets': 'target_share', 'Cuota de Yardas Aéreas': 'air_yards_share'}
            
            selected_metric_name = st.selectbox("Selecciona una métrica para comparar:", list(player_metrics.keys()))
            create_line_chart(position_filtered_df, [player_a, player_b], player_metrics[selected_metric_name], selected_metric_name, 'player_name')


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