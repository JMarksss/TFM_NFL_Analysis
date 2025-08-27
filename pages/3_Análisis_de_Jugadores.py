"""
Created on Tue Mon 21 17:42:11 2025

@author: jmarcos
"""

#Importamos las librerías
import streamlit as st
import pandas as pd
import os
import plotly.express as px

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Análisis de Jugadores Ofensivos",
    page_icon="🏃",
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
team_info_df = load_data('offensive_team_stats_advanced_2020-2024.csv')

# --- Título Principal ---
st.title("🏃 Análisis de Jugadores Ofensivos")
st.markdown("Filtra y visualiza el rendimiento de los jugadores de la NFL por posición y métricas específicas.")
st.divider()

# --- Pre-procesamiento y Unión de Datos ---
if player_df_raw is not None and team_info_df is not None:
    team_info_subset = team_info_df[['team', 'year', 'conference', 'division']].drop_duplicates()
    player_df = pd.merge(player_df_raw, team_info_subset, on=['team', 'year'], how='left')
else:
    st.warning("No se pudieron cargar los datos.")
    st.stop()

# --- Barra Lateral de Filtros ---
st.sidebar.header("Filtros de Jugadores")

selected_year = st.sidebar.selectbox(
    'Selecciona una Temporada',
    options=sorted(player_df['year'].unique(), reverse=True)
)

selected_position = st.sidebar.selectbox(
    'Selecciona una Posición',
    options=['QB', 'RB', 'Receptor']
)

# --- Slider para Mínimo de Participación ---
st.sidebar.markdown("---")
st.sidebar.subheader("Filtro de Participación Mínima")
if selected_position == 'QB':
    min_attempts = st.sidebar.slider("Mínimo de Intentos de Pase:", 0, 600, 100)
elif selected_position == 'RB':
    min_attempts = st.sidebar.slider("Mínimo de Intentos de Carrera:", 0, 400, 50)
else: # Receptor
    min_attempts = st.sidebar.slider("Mínimo de Targets:", 0, 200, 50)
st.sidebar.markdown("---")


conference_options = ['Ambas'] + sorted(player_df['conference'].dropna().unique())
selected_conference = st.sidebar.selectbox(
    'Selecciona una Conferencia',
    options=conference_options
)

if selected_conference == 'Ambas':
    division_options = ['Todas']
else:
    division_options = ['Todas'] + sorted(player_df[player_df['conference'] == selected_conference]['division'].dropna().unique())

selected_division = st.sidebar.selectbox(
    'Selecciona una División',
    options=division_options
)

# --- Filtrado de Datos ---
filtered_players = player_df[player_df['year'] == selected_year]

if selected_position == 'Receptor':
    filtered_players = filtered_players[filtered_players['position'].isin(['WR', 'TE'])]
    # Aplicar filtro de participación
    filtered_players = filtered_players[filtered_players['targets'] >= min_attempts]
elif selected_position == 'QB':
    filtered_players = filtered_players[filtered_players['position'] == 'QB']
    # Aplicar filtro de participación
    filtered_players = filtered_players[filtered_players['attempts'] >= min_attempts]
else: # RB
    filtered_players = filtered_players[filtered_players['position'] == 'RB']
    # Aplicar filtro de participación
    filtered_players = filtered_players[filtered_players['carries'] >= min_attempts]


if selected_conference != 'Ambas':
    filtered_players = filtered_players[filtered_players['conference'] == selected_conference]
    if selected_division != 'Todas':
        filtered_players = filtered_players[filtered_players['division'] == selected_division]

# --- Función para crear gráficos ---
LOWER_IS_BETTER_PLAYER_METRICS = [
    'interceptions', 'sacks', 'sack_fumbles', 'sack_fumbles_lost',
    'rushing_fumbles', 'rushing_fumbles_lost',
    'receiving_fumbles', 'receiving_fumbles_lost'
]

def create_player_barchart(df, metric_col, metric_name): #grafico de barras, top 20, análoga a la de equipos
    st.markdown(f"**Top 20 Jugadores por {metric_name}**")
    chart_df = df[df[metric_col].notna() & (df[metric_col] != 0)].copy()
    if chart_df.empty:
        st.warning("No hay jugadores que cumplan los filtros seleccionados.")
        return
    lower_is_better = any(keyword in metric_col for keyword in LOWER_IS_BETTER_PLAYER_METRICS)
    min_val, max_val = chart_df[metric_col].min(), chart_df[metric_col].max() 
    top_20 = chart_df.sort_values(by=metric_col, ascending=lower_is_better).head(20) #solo top 20
    top_20_for_plot = top_20.sort_values(by=metric_col, ascending=not lower_is_better) #ajuste para estadísticas invertidas
    color_scale = px.colors.diverging.RdYlGn_r if lower_is_better else px.colors.diverging.RdYlGn
    fig = px.bar(top_20_for_plot, x=metric_col, y='player_name', orientation='h', color=metric_col, color_continuous_scale=color_scale, range_color=[min_val, max_val], text_auto='.2s', labels={'player_name': 'Jugador', metric_col: metric_name}, hover_name='player_name', hover_data={'team': True, metric_col: ':.2f'}) #Escala de color en base a valores totales, no filtrados
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis=(dict(showgrid=False)), coloraxis_showscale=False, height=600)
    fig.update_traces(textposition='outside', marker_line_color='rgb(8,48,107)', marker_line_width=1.5)
    st.plotly_chart(fig, use_container_width=True)

# --- Lógica de Visualización por Posición ---
if selected_position == 'QB':
    st.header(f"Análisis de Quarterbacks (QB) - {selected_year}")
    qb_pass_metrics = {'Yardas de Pase': 'passing_yards', 'TDs de Pase': 'passing_tds', 'EPA de Pase': 'passing_epa', 'Completions': 'completions', 'Intentos': 'attempts', 'Intercepciones': 'interceptions', 'Sacks': 'sacks', 'Yardas Aéreas': 'passing_air_yards', 'Yardas tras Recepción': 'passing_yards_after_catch', 'Primeros Downs de Pase': 'passing_first_downs', 'Conversiones de 2pts': 'passing_2pt_conversions', 'PACR': 'pacr', 'DAKOTA': 'dakota'}
    qb_rush_metrics = {'Yardas de Carrera': 'rushing_yards', 'TDs de Carrera': 'rushing_tds', 'EPA de Carrera': 'rushing_epa', 'Intentos de Carrera': 'carries', 'Fumbles en Carrera': 'rushing_fumbles', 'Fumbles Perdidos': 'rushing_fumbles_lost', 'Primeros Downs de Carrera': 'rushing_first_downs', 'Conversiones de 2pts': 'rushing_2pt_conversions'}
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("Estadísticas de Pase")
        selected_qb_pass_name = st.selectbox("Selecciona una métrica de pase:", options=list(qb_pass_metrics.keys()), key='qb_pass')
        create_player_barchart(filtered_players, qb_pass_metrics[selected_qb_pass_name], selected_qb_pass_name)
    with col2:
        st.subheader("Estadísticas de Carrera")
        selected_qb_rush_name = st.selectbox("Selecciona una métrica de carrera:", options=list(qb_rush_metrics.keys()), key='qb_rush')
        create_player_barchart(filtered_players, qb_rush_metrics[selected_qb_rush_name], selected_qb_rush_name)
elif selected_position == 'RB':
    st.header(f"Análisis de Running Backs (RB) - {selected_year}")
    rb_metrics = {'Yardas de Carrera': 'rushing_yards', 'TDs de Carrera': 'rushing_tds', 'EPA de Carrera': 'rushing_epa', 'Intentos de Carrera': 'carries', 'Fumbles': 'rushing_fumbles', 'Fumbles Perdidos': 'rushing_fumbles_lost', 'Primeros Downs de Carrera': 'rushing_first_downs', 'Conversiones de 2pts': 'rushing_2pt_conversions'}
    selected_rb_metric_name = st.selectbox("Selecciona una métrica de carrera:", options=list(rb_metrics.keys()), key='rb_metric')
    create_player_barchart(filtered_players, rb_metrics[selected_rb_metric_name], selected_rb_metric_name)
elif selected_position == 'Receptor':
    st.header(f"Análisis de Receptores (WR/TE) - {selected_year}")
    rec_metrics = {'Yardas de Recepción': 'receiving_yards', 'TDs de Recepción': 'receiving_tds', 'EPA de Recepción': 'receiving_epa', 'Recepciones': 'receptions', 'Targets': 'targets', 'Yardas Aéreas': 'receiving_air_yards', 'Yardas tras Recepción': 'receiving_yards_after_catch', 'Fumbles': 'receiving_fumbles', 'Fumbles Perdidos': 'receiving_fumbles_lost', 'Primeros Downs de Recepción': 'receiving_first_downs', 'Conversiones de 2pts': 'receiving_2pt_conversions', 'RACR': 'racr', 'Cuota de Targets': 'target_share', 'Cuota de Yardas Aéreas': 'air_yards_share'}
    selected_rec_metric_name = st.selectbox("Selecciona una métrica de recepción:", options=list(rec_metrics.keys()), key='rec_metric')
    create_player_barchart(filtered_players, rec_metrics[selected_rec_metric_name], selected_rec_metric_name)


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