"""
Created on Tue Wed 16 12:06:07 2025

@author: jmarcos
"""

#Imporamos las librerías
import streamlit as st
import pandas as pd
import os
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Comparador de Equipos",
    page_icon="⚔️",
    layout="wide"
)

# --- Diccionario de Información de Equipos (Nombres y Logos ESPN) ---
TEAM_INFO = { 
    'ARI': {'name': 'Arizona Cardinals', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/ari.png'},
    'ATL': {'name': 'Atlanta Falcons', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/atl.png'},
    'BAL': {'name': 'Baltimore Ravens', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/bal.png'},
    'BUF': {'name': 'Buffalo Bills', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/buf.png'},
    'CAR': {'name': 'Carolina Panthers', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/car.png'},
    'CHI': {'name': 'Chicago Bears', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/chi.png'},
    'CIN': {'name': 'Cincinnati Bengals', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/cin.png'},
    'CLE': {'name': 'Cleveland Browns', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/cle.png'},
    'DAL': {'name': 'Dallas Cowboys', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/dal.png'},
    'DEN': {'name': 'Denver Broncos', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/den.png'},
    'DET': {'name': 'Detroit Lions', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/det.png'},
    'GB': {'name': 'Green Bay Packers', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/gb.png'},
    'HOU': {'name': 'Houston Texans', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/hou.png'},
    'IND': {'name': 'Indianapolis Colts', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/ind.png'},
    'JAX': {'name': 'Jacksonville Jaguars', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/jax.png'},
    'KC': {'name': 'Kansas City Chiefs', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/kc.png'},
    'LV': {'name': 'Las Vegas Raiders', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/lv.png'},
    'LAC': {'name': 'Los Angeles Chargers', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/lac.png'},
    'LA': {'name': 'Los Angeles Rams', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/lar.png'},
    'MIA': {'name': 'Miami Dolphins', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/mia.png'},
    'MIN': {'name': 'Minnesota Vikings', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/min.png'},
    'NE': {'name': 'New England Patriots', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/ne.png'},
    'NO': {'name': 'New Orleans Saints', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/no.png'},
    'NYG': {'name': 'New York Giants', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png'},
    'NYJ': {'name': 'New York Jets', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png'},
    'PHI': {'name': 'Philadelphia Eagles', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/phi.png'},
    'PIT': {'name': 'Pittsburgh Steelers', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/pit.png'},
    'SF': {'name': 'San Francisco 49ers', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png'},
    'SEA': {'name': 'Seattle Seahawks', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/sea.png'},
    'TB': {'name': 'Tampa Bay Buccaneers', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/tb.png'},
    'TEN': {'name': 'Tennessee Titans', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/ten.png'},
    'WAS': {'name': 'Washington Commanders', 'logo': 'https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png'}
}


# --- Carga de Datos ---
@st.cache_data
def load_data(file_path):
    """Carga un fichero CSV desde la ruta especificada."""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"Error: No se encontró el fichero en la ruta: {file_path}")
        return None

offensive_df = load_data('offensive_team_stats_advanced_2020-2024.csv')
defensive_df = load_data('defensive_team_stats_advanced_2020-2024.csv')

# --- Título Principal ---
st.title("⚔️ Comparador de Equipos")
st.markdown("Selecciona dos equipos y una temporada para comparar su rendimiento en métricas clave.")
st.divider()

# --- Filtros ---
if offensive_df is not None and defensive_df is not None:
    full_stats_df = pd.merge(offensive_df, defensive_df, on=['team', 'year', 'conference', 'division'])
    
    years = sorted(full_stats_df['year'].unique(), reverse=True)
    team_names = {abbr: info['name'] for abbr, info in TEAM_INFO.items() if abbr in full_stats_df['team'].unique()}
    
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_year = st.selectbox("Selecciona una Temporada:", years)
    with col2:
        team_a_name = st.selectbox("Selecciona el Equipo A:", options=list(team_names.values()), index=list(team_names.keys()).index('KC') if 'KC' in team_names else 0) #Filtro de equipo A, KC valor por defecto
        team_a = [abbr for abbr, name in team_names.items() if name == team_a_name][0]
    with col3:
        default_b_index = list(team_names.keys()).index('SF') if 'SF' in team_names and team_a != 'SF' else 1 #Filtro de equipo B, SF valor por defecto si no es el equipo A
        team_b_name = st.selectbox("Selecciona el Equipo B:", options=list(team_names.values()), index=default_b_index)
        team_b = [abbr for abbr, name in team_names.items() if name == team_b_name][0]

    year_df = full_stats_df[full_stats_df['year'] == selected_year].copy()
else:
    st.warning("No se pudieron cargar los datos. Por favor, verifica la ruta de los ficheros CSV.")
    st.stop()

# --- Lógica de Percentiles para el Gráfico de Radar ---
if team_a == team_b:
    st.warning("Por favor, selecciona dos equipos diferentes para comparar.")
else:
    radar_metrics = {
        'TDs Ofensivos': ('offensive_tds', True),
        'Yardas/Pase Netas': ('net_yards_per_pass', True),
        'Yardas/Carrera': ('yards_per_rush', True),
        'Turnovers Forzados': ('turnovers_forced', True),
        'Yardas/Pase Permitidas': ('yards_per_pass_allowed', False), #2º parámetro para indicar en qué estadísticas un valor mayor es mejor
        'Yardas/Carrera Permitidas': ('yards_per_rush_allowed', False)
    }

    for metric_name, (col_name, higher_is_better) in radar_metrics.items():
        year_df[f'{col_name}_percentile'] = year_df[col_name].rank(pct=True) #Ranking por percentiles
        if not higher_is_better:
            year_df[f'{col_name}_percentile'] = 1 - year_df[f'{col_name}_percentile'] #Invertimos para las stats donde el valor menor es mejor
        year_df[f'{col_name}_percentile'] *= 100

    team_a_percentiles = year_df[year_df['team'] == team_a]
    team_b_percentiles = year_df[year_df['team'] == team_b]

    # --- Gráfico de Radar ---
    st.subheader(f"Comparativa de Percentiles de Rendimiento: {team_a_name} vs. {team_b_name} ({selected_year})")
    st.markdown("El gráfico muestra el percentil de cada equipo en la liga (un valor más alto siempre es mejor).")

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar( #Radar equipo A
        r=[team_a_percentiles[f'{col}_percentile'].iloc[0] for col, _ in radar_metrics.values()],
        theta=list(radar_metrics.keys()),
        fill='toself',
        name=team_a_name,
        hovertemplate='<b>%{theta}</b><br>Percentil: %{r:.1f}<extra></extra>'
    ))

    fig.add_trace(go.Scatterpolar( #Radar equipo B
        r=[team_b_percentiles[f'{col}_percentile'].iloc[0] for col, _ in radar_metrics.values()],
        theta=list(radar_metrics.keys()),
        fill='toself',
        name=team_b_name,
        hovertemplate='<b>%{theta}</b><br>Percentil: %{r:.1f}<extra></extra>'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=500,
        legend=dict(yanchor="top", y=1.15, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Tablas Comparativas de Datos Brutos ---
    st.markdown("---")
    st.subheader("Estadísticas Detalladas")

    table_metrics = {
        'TDs Ofensivos Totales': 'offensive_tds',
        'Yardas por Intento de Pase': 'yards_per_pass',
        'Yardas por Intento de Carrera': 'yards_per_rush',
        'Turnovers Forzados por la Defensa': 'turnovers_forced',
        'Yardas por Pase Permitidas': 'yards_per_pass_allowed',
        'Yardas por Carrera Permitidas': 'yards_per_rush_allowed'
    }

    team_a_stats = year_df[year_df['team'] == team_a][list(table_metrics.values())].iloc[0]
    team_b_stats = year_df[year_df['team'] == team_b][list(table_metrics.values())].iloc[0]

    comparison_df = pd.DataFrame({
        team_a_name: team_a_stats,
        team_b_name: team_b_stats
    })
    comparison_df.index = list(table_metrics.keys())

    col_a, col_b = st.columns(2)
    with col_a:
        st.image(TEAM_INFO[team_a]['logo'], width=100) #Nombre y logos en la tabla
        st.markdown(f"##### {team_a_name}")
        st.dataframe(comparison_df[[team_a_name]].style.format("{:.2f}"))
    
    with col_b:
        st.image(TEAM_INFO[team_b]['logo'], width=100)
        st.markdown(f"##### {team_b_name}")
        st.dataframe(comparison_df[[team_b_name]].style.format("{:.2f}"))

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