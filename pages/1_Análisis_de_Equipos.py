"""
Created on Tue Jul 8 20:37:21 2025

@author: jmarcos
"""

# Importamos las librerías
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Análisis de Equipos",
    page_icon="📊",
    layout="wide"
)

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

# --- Barra Lateral de Filtros ---
st.sidebar.header("Filtros de Visualización")

if offensive_df is not None and defensive_df is not None: #Filtro año
    selected_year = st.sidebar.selectbox(
        'Selecciona una Temporada',
        options=sorted(offensive_df['year'].unique(), reverse=True)
    )

    conference_options = ['Ambas'] + sorted(offensive_df['conference'].dropna().unique()) #Filtro conferencia
    selected_conference = st.sidebar.selectbox(
        'Selecciona una Conferencia',
        options=conference_options
    )

    if selected_conference == 'Ambas': #Condición de la dicisión en función de la conferencia
        division_options = ['Todas']
    else:
        division_options = ['Todas'] + sorted(offensive_df[offensive_df['conference'] == selected_conference]['division'].dropna().unique())
    
    selected_division = st.sidebar.selectbox( #Filtro división
        'Selecciona una División',
        options=division_options
    )

    filtered_offensive_df = offensive_df[offensive_df['year'] == selected_year]
    filtered_defensive_df = defensive_df[defensive_df['year'] == selected_year]

    if selected_conference != 'Ambas':
        filtered_offensive_df = filtered_offensive_df[filtered_offensive_df['conference'] == selected_conference]
        filtered_defensive_df = filtered_defensive_df[filtered_defensive_df['conference'] == selected_conference]
        if selected_division != 'Todas':
            filtered_offensive_df = filtered_offensive_df[filtered_offensive_df['division'] == selected_division]
            filtered_defensive_df = filtered_defensive_df[filtered_defensive_df['division'] == selected_division]
else:
    st.warning("No se pudieron cargar los datos. Por favor, verifica la ruta de los ficheros CSV.")
    st.stop()

# --- Título Principal ---
st.title(f"📊 Análisis de Equipos - Temporada Regular {selected_year}")
st.markdown("Explora y compara el rendimiento de los equipos de la NFL en diferentes facetas del juego. Utiliza los menús desplegables para ver las estadísticas.")
st.markdown("---")


# --- Funciones para crear gráficos ---
LOWER_IS_BETTER_METRICS = [ #En estas variables un valor más bajo es mejor (importante para los gráficos)
    'total_turnovers', 'interceptions', 'fumbles_lost', 'sacks_taken',
    'total_yards_allowed', 'total_plays_faced', 'yards_per_play_allowed',
    'completions_allowed', 'pass_attempts_faced', 'passing_yards_allowed', 'passing_tds_allowed',
    'opponent_cmp_percentage', 'yards_per_pass_allowed', 'offensive_tds_allowed',
    'rush_attempts_faced', 'rushing_yards_allowed', 'rushing_tds_allowed', 'yards_per_rush_allowed'
]

def create_plotly_barchart(df, metric_col, metric_name):
    """Crea un gráfico de barras horizontal, ordenado y con colores graduales."""
    st.markdown(f"**Ranking por {metric_name}**")
    lower_is_better = any(keyword in metric_col for keyword in LOWER_IS_BETTER_METRICS) 
    chart_data = df.sort_values(by=metric_col, ascending=lower_is_better) #Ordenamos de menos a más si la métrica pertenece a la anterior lista
    color_scale = px.colors.diverging.RdYlGn_r if lower_is_better else px.colors.diverging.RdYlGn #Escala de colores gradual Verde/Amarillo/Rojo
    fig = px.bar(chart_data, x=metric_col, y='team', orientation='h', color=metric_col, color_continuous_scale=color_scale, text_auto='.2s', labels={'team': 'Equipo', metric_col: metric_name})
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis=(dict(showgrid=False)), yaxis={'categoryorder':'total ascending'}, coloraxis_showscale=False, height=max(400, len(df) * 20))
    fig.update_traces(textposition='outside', marker_line_color='rgb(8,48,107)', marker_line_width=1.5)
    st.plotly_chart(fig, use_container_width=True)

def create_plotly_scatterplot(df, x_metric, y_metric, x_name, y_name, title, is_defensive=False):
    """Crea un gráfico de dispersión con líneas de promedio y anotaciones de cuadrantes correctas."""
    st.markdown(f"**{title}**")
    
    x_avg = df[x_metric].mean() #Medias para dar el eje
    y_avg = df[y_metric].mean()

    fig = px.scatter(
        df, x=x_metric, y=y_metric, text='team',
        labels={x_metric: x_name, y_metric: y_name},
        hover_name='team',
        hover_data={x_metric: ':.2f', y_metric: ':.2f', 'team': False}
    )
    fig.add_vline(x=x_avg, line_width=2, line_dash="dash", line_color="gray") #Ejes
    fig.add_hline(y=y_avg, line_width=2, line_dash="dash", line_color="gray")
    
    if is_defensive: #Texto a mostrar en cada cuadrante, depende del lado de la jugada
        top_right_text, top_right_color = "Peor Pase, Peor Carrera", "red"
        bottom_left_text, bottom_left_color = "Mejor Pase, Mejor Carrera", "green"
    else:
        top_right_text, top_right_color = "Mejor Pase, Mejor Carrera", "green"
        bottom_left_text, bottom_left_color = "Peor Pase, Peor Carrera", "red"

    fig.add_annotation(x=df[x_metric].max(), y=df[y_metric].max(), text=top_right_text, showarrow=False, xanchor='right', yanchor='top', font=dict(color=top_right_color, size=10), bgcolor="rgba(255,255,255,0.5)")
    fig.add_annotation(x=df[x_metric].min(), y=df[y_metric].min(), text=bottom_left_text, showarrow=False, xanchor='left', yanchor='bottom', font=dict(color=bottom_left_color, size=10), bgcolor="rgba(255,255,255,0.5)")

    fig.update_traces(textposition='top center', textfont_size=10)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig, use_container_width=True)


# --- Menús Desplegables ---
with st.expander("📊 Estadísticas Totales"): #4 expandibles y 2 columnas
   
    col_total_off, col_total_def = st.columns(2, gap="large") 
    with col_total_off:
        st.subheader("🚀 Ofensiva")
        offensive_total_metrics = {'Yardas Totales': 'total_yards', 'Jugadas Totales': 'total_plays', 'Yardas por Jugada': 'yards_per_play', 'TDs Ofensivos': 'offensive_tds', 'Pérdidas de Balón': 'total_turnovers'} #Renombramos las estadísticas
        selected_off_total_name = st.selectbox("Selecciona una métrica:", options=list(offensive_total_metrics.keys()), key='off_total') #Selección (filtro desplegable)
        create_plotly_barchart(filtered_offensive_df, offensive_total_metrics[selected_off_total_name], selected_off_total_name) #Creamos gráfico con la función
    with col_total_def:
        st.subheader("🛡️ Defensiva")
        defensive_total_metrics = {'Yardas Totales Permitidas': 'total_yards_allowed', 'Jugadas Totales Enfrentadas': 'total_plays_faced', 'Yardas por Jugada Permitidas': 'yards_per_play_allowed', 'TDs Ofensivos Permitidos': 'offensive_tds_allowed', 'Pérdidas de Balón Forzadas': 'turnovers_forced'}
        selected_def_total_name = st.selectbox("Selecciona una métrica:", options=list(defensive_total_metrics.keys()), key='def_total')
        create_plotly_barchart(filtered_defensive_df, defensive_total_metrics[selected_def_total_name], selected_def_total_name)

with st.expander("✈️ Estadísticas de Pase"):
   
    col_pass_off, col_pass_def = st.columns(2, gap="large")
    with col_pass_off:
        st.subheader("🚀 Ofensiva")
        offensive_pass_metrics = {'Yardas de Pase': 'passing_yards', 'TDs de Pase': 'passing_tds', 'Pases Completados': 'pass_completions', 'Intentos de Pase': 'pass_attempts', '% Pases Completados': 'cmp_percentage', 'Yardas por Intento de Pase': 'yards_per_pass', 'Yardas Netas por Pase': 'net_yards_per_pass', 'Ratio TD/INT': 'pass_td_int_ratio', 'Intercepciones Lanzadas': 'interceptions', 'Sacks Sufridos': 'sacks_taken'}
        selected_off_pass_name = st.selectbox("Selecciona una métrica:", options=list(offensive_pass_metrics.keys()), key='off_pass')
        create_plotly_barchart(filtered_offensive_df, offensive_pass_metrics[selected_off_pass_name], selected_off_pass_name)
    with col_pass_def:
        st.subheader("🛡️ Defensiva")
        defensive_pass_metrics = {'Yardas de Pase Permitidas': 'passing_yards_allowed', 'TDs de Pase Permitidos': 'passing_tds_allowed', 'Intercepciones Realizadas': 'interceptions_made', 'Sacks Realizados': 'sacks_made', '% Pases Completados del Rival': 'opponent_cmp_percentage', 'Yardas por Intento de Pase Permitidas': 'yards_per_pass_allowed', '% de Sacks por Jugada de Pase': 'sack_rate'}
        selected_def_pass_name = st.selectbox("Selecciona una métrica:", options=list(defensive_pass_metrics.keys()), key='def_pass')
        create_plotly_barchart(filtered_defensive_df, defensive_pass_metrics[selected_def_pass_name], selected_def_pass_name)

with st.expander("🏃‍♂️ Estadísticas de Carrera"):
   
    col_rush_off, col_rush_def = st.columns(2, gap="large")
    with col_rush_off:
        st.subheader("🚀 Ofensiva")
        offensive_rush_metrics = {'Yardas de Carrera': 'rushing_yards', 'TDs de Carrera': 'rushing_tds', 'Intentos de Carrera': 'rush_attempts', 'Yardas por Intento de Carrera': 'yards_per_rush', 'Fumbles Perdidos': 'fumbles_lost'}
        selected_off_rush_name = st.selectbox("Selecciona una métrica:", options=list(offensive_rush_metrics.keys()), key='off_rush')
        create_plotly_barchart(filtered_offensive_df, offensive_rush_metrics[selected_off_rush_name], selected_off_rush_name)
    with col_rush_def:
        st.subheader("🛡️ Defensiva")
        defensive_rush_metrics = {'Yardas de Carrera Permitidas': 'rushing_yards_allowed', 'TDs de Carrera Permitidos': 'rushing_tds_allowed', 'Yardas por Intento de Carrera Permitidas': 'yards_per_rush_allowed', 'Fumbles Forzados': 'fumbles_forced'}
        selected_def_rush_name = st.selectbox("Selecciona una métrica:", options=list(defensive_rush_metrics.keys()), key='def_rush')
        create_plotly_barchart(filtered_defensive_df, defensive_rush_metrics[selected_def_rush_name], selected_def_rush_name)

with st.expander("⚖️ Comparativa del Juego de Pase y de Carrera"):
    col_scatter_off, col_scatter_def = st.columns(2, gap="large")

    with col_scatter_off:
        st.subheader("🚀 Ofensiva")
        scatter_off_options = {
            "Yardas (Pase vs. Carrera)": ('passing_yards', 'rushing_yards', "Yardas de Pase", "Yardas de Carrera"),
            "Yardas por Jugada (Pase vs. Carrera)": ('yards_per_pass', 'yards_per_rush', "Yardas por Intento de Pase", "Yardas por Intento de Carrera"),
            "TDs (Pase vs. Carrera)": ('passing_tds', 'rushing_tds', "TDs de Pase", "TDs de Carrera")
        }
        selected_scatter_off_name = st.selectbox("Selecciona una comparativa:", options=list(scatter_off_options.keys()), key='scatter_off')
        x_metric_off, y_metric_off, x_name_off, y_name_off = scatter_off_options[selected_scatter_off_name]
        create_plotly_scatterplot(filtered_offensive_df, x_metric_off, y_metric_off, x_name_off, y_name_off, f"Eficiencia Ofensiva: {selected_scatter_off_name}")

    with col_scatter_def:
        st.subheader("🛡️ Defensiva")
        scatter_def_options = {
            "Yardas Permitidas (Pase vs. Carrera)": ('passing_yards_allowed', 'rushing_yards_allowed', "Yardas de Pase Permitidas", "Yardas de Carrera Permitidas"),
            "Yardas por Jugada Permitidas (Pase vs. Carrera)": ('yards_per_pass_allowed', 'yards_per_rush_allowed', "Yardas por Intento de Pase Permitidas", "Yardas por Intento de Carrera Permitidas"),
            "TDs Permitidos (Pase vs. Carrera)": ('passing_tds_allowed', 'rushing_tds_allowed', "TDs de Pase Permitidos", "TDs de Carrera Permitidos")
        }
        selected_scatter_def_name = st.selectbox("Selecciona una comparativa:", options=list(scatter_def_options.keys()), key='scatter_def')
        x_metric_def, y_metric_def, x_name_def, y_name_def = scatter_def_options[selected_scatter_def_name]
        create_plotly_scatterplot(filtered_defensive_df, x_metric_def, y_metric_def, x_name_def, y_name_def, f"Eficiencia Defensiva: {selected_scatter_def_name}", is_defensive=True)

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