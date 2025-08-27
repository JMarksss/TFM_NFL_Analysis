import streamlit as st
import pandas as pd
import os

# --- Configuración de la Página ---
st.set_page_config(
    page_title="NFL Analytics Hub - Principal",
    page_icon="🏈",
    layout="wide"
)

# --- Carga de Datos ---
# Carga de datos solo una vez para que la app sea más rápida.
@st.cache_data
def load_data(file_path):
    """Carga un fichero CSV desde la ruta especificada."""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error(f"Error: No se encontró el fichero '{file_path}'. Asegúrate de que está en la misma carpeta que el script.")
        return None

# Cargar los datos
of = load_data('offensive_team_stats_advanced_2020-2024.csv')
df = load_data('defensive_team_stats_advanced_2020-2024.csv')
pl = load_data('detailed_player_stats_advanced_2020-2024.csv')


# --- Contenido de la Página ---

# Título y Bienvenida
st.title("🏈 NFL Analytics Hub")
st.caption('Juan Marcos Díaz')
st.image('./Images/analytics.png', width=650)
st.markdown("""
Bienvenido a **NFL Analytics Hub**, una interfaz simple e interactiva para facilitar el análisis de equipos y jugadores de NFL a través de las últimas 5 temporadas regulares (2020-2024).
Este proyecto nace con el objetivo de transformar la inmensa cantidad de datos generados cada temporada en gráficos sencillos y visualmente atráctivos
para poder llevar a cabo análisis que permitan descubrir patrones y evaluar el rendimiento tanto de los equipos como de los jugadores.
""")
st.divider()


# Sección "Cómo Empezar"
st.header("¿Cómo Empezar?")
st.markdown("Utiliza la barra de navegación de la izquierda para explorar las diferentes herramientas de análisis disponibles en esta web:")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Análisis de Equipos")
    st.info("""
    Explora una visión macro del rendimiento de la liga. Filtra por temporada, conferencia o división para encontrar a los líderes
    en las métricas ofensivas y defensivas más importantes. Ideal para entender qué equipos dominaron en cada faceta del juego.
    """)

    st.subheader("⚔️ Comparador de Equipos")
    st.info("""
    Enfréntate a dos equipos en un análisis "Head-to-Head". Compara sus perfiles estadísticos a través de un gráfico de radar
    que muestra sus fortalezas y debilidades.
    """)
    
    st.subheader("📈 Evolución y Tendencias")
    st.info("""
    Visualiza la progresión de dos equipos o jugadores a lo largo de las últimas 5 temporadas regulares (2020-2024). Ideal para identificar
    trayectorias ascendentes, picos de rendimiento y posibles declives.
    """)


with col2:
    st.subheader("🏃 Análisis de Jugadores Ofensivos")
    st.info("""
    Analiza el rendimiento individual de los jugadores ofensivos en las principales posiciones medibles: Quarterbacks, Running Backs y Receptores (WRs y TEs). Filtra por posición, equipo y temporada para descubrir a las estrellas
    destacadas y ordena la información por las métricas más relevantes.
    """)

    st.subheader("🎯 Comparador de Jugadores Ofensivos")
    st.info("""
    Análogo al comparador de equipos, filtra por posición y compara a dos jugadores en un análisis a través de un gráfico de radar.
    """)
    
    st.subheader("🧠 Modelado Analítico")
    st.info("""
    Sumérgete en el análisis avanzado con Machine Learning. Descubre arquetipos de jugadores por posición a través del **Clustering**
    o encuentra perfiles estadísticos similares con el **buscador basado en PCA**.
    """)


st.divider()

#KPI's destacados
st.header("El Proyecto en Cifras")

if of is not None:
    # Calcular algunas métricas agregadas del dataset
    total_seasons = of['year'].nunique()
    total_tds = of['offensive_tds'].sum()
    total_yards = of['total_yards'].sum()

    # Mostrar las métricas en tarjetas
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric(label="Temporadas Analizadas", value=f"{int(total_seasons)}")
    kpi_col2.metric(label="Touchdowns Ofensivos Anotados", value=f"{int(total_tds):,}")
    kpi_col3.metric(label="Yardas Ofensivas Generadas", value=f"{int(total_yards):,}")

else:
    st.warning("No se pudieron cargar los datos para mostrar las cifras del proyecto.")

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