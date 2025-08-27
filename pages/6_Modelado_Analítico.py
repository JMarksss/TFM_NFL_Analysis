"""
Created on Aug Mon 18 22:31:24 2025

@author: jmarcos
"""

#Importamos las librerías
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import euclidean_distances

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Modelado Analítico",
    page_icon="🧠",
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
st.title("🧠 Modelado Analítico de Jugadores")
st.markdown("Utiliza Machine Learning para descubrir arquetipos de jugadores y encontrar perfiles estadísticamente similares.")
st.markdown("---")

# --- Pre-procesamiento de Datos ---
if player_df_raw is None:
    st.warning("No se pudieron cargar los datos. Por favor, verifica la ruta del fichero CSV.")
    st.stop()

metrics_to_check = ['passing_tds', 'rushing_tds', 'passing_first_downs', 'rushing_first_downs', 'interceptions', 'rushing_fumbles_lost', 'sack_fumbles_lost']
for col in metrics_to_check:
    if col not in player_df_raw.columns:
        player_df_raw[col] = 0
player_df_raw[metrics_to_check] = player_df_raw[metrics_to_check].fillna(0) 

player_df_raw['total_tds'] = player_df_raw['passing_tds'] + player_df_raw['rushing_tds']
player_df_raw['total_first_downs'] = player_df_raw['passing_first_downs'] + player_df_raw['rushing_first_downs']
player_df_raw['total_turnovers'] = player_df_raw['interceptions'] + player_df_raw['rushing_fumbles_lost'] + player_df_raw['sack_fumbles_lost']

# --- Funciones del Modelo ---
def get_scaled_features(df, features):
    """Escala las características seleccionadas y devuelve el array y el dataframe limpio."""
    model_df = df[features + ['player_name', 'team']].copy().reset_index(drop=True)
    model_df.fillna(0, inplace=True)
    
    scaler = StandardScaler() #Escalado estándar
    scaled_features = scaler.fit_transform(model_df[features])
    return model_df, scaled_features

def get_clustering_scores(scaled_features):
    """Calcula la inercia y el silhouette score para un rango de clústeres."""
    inertias = []
    silhouette_scores = []
    k_range = range(2, 9) #k-means, bucle de 2 a 8 clústers
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=23, n_init=10)
        kmeans.fit(scaled_features)
        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(scaled_features, kmeans.labels_))
    return k_range, inertias, silhouette_scores

def run_full_model(model_df, scaled_features, n_clusters):
    """Ejecuta PCA y K-Means con un número de clústeres definido."""
    pca = PCA(n_components=2) #PCA con 2 componentes para graficar
    principal_components = pca.fit_transform(scaled_features)
    model_df['PC1'] = principal_components[:, 0]
    model_df['PC2'] = principal_components[:, 1]
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=23, n_init=10)
    model_df['cluster'] = kmeans.fit_predict(scaled_features)
    
    return model_df

# --- Barra Lateral de Filtros ---
st.sidebar.header("Filtros del Modelo")
selected_year = st.sidebar.selectbox('Selecciona una Temporada', options=sorted(player_df_raw['year'].unique(), reverse=True))
selected_position = st.sidebar.selectbox('Selecciona una Posición', options=['QB', 'RB', 'Receptor'])

st.sidebar.markdown("---")
st.sidebar.subheader("Filtro de Participación Mínima")
if selected_position == 'QB':
    min_attempts = st.sidebar.slider("Mínimo de Intentos de Pase:", 0, 600, 150)
    filtered_df = player_df_raw[(player_df_raw['position'] == 'QB') & (player_df_raw['attempts'] >= min_attempts)]
elif selected_position == 'RB':
    min_attempts = st.sidebar.slider("Mínimo de Intentos de Carrera:", 0, 400, 75)
    filtered_df = player_df_raw[(player_df_raw['position'] == 'RB') & (player_df_raw['carries'] >= min_attempts)]
else: # Receptor
    min_attempts = st.sidebar.slider("Mínimo de Targets:", 0, 200, 60)
    filtered_df = player_df_raw[(player_df_raw['position'].isin(['WR', 'TE'])) & (player_df_raw['targets'] >= min_attempts)]

filtered_df = filtered_df[filtered_df['year'] == selected_year]

features_dict = {
    'QB': ['passing_epa', 'rushing_epa', 'pacr', 'dakota', 'total_tds', 'total_first_downs', 'sacks', 'total_turnovers', 'passing_yards', 'rushing_yards'],
    'RB': ['rushing_epa', 'rushing_tds', 'carries', 'rushing_yards', 'rushing_first_downs', 'rushing_fumbles'],
    'Receptor': ['receiving_epa', 'receiving_tds', 'racr', 'receiving_yards_after_catch', 'receiving_first_downs', 'receiving_fumbles', 'receiving_yards']
}
features = features_dict[selected_position]

if filtered_df.shape[0] < 10:
    st.warning("No hay suficientes jugadores que cumplan los filtros para ejecutar el modelo. Por favor, ajusta los filtros.")
    st.stop()

# --- Ejecución Modular del Modelo ---
model_df, scaled_features = get_scaled_features(filtered_df, features)
k_range, inertias, silhouette_scores = get_clustering_scores(scaled_features)
recommended_k = k_range[np.argmax(silhouette_scores)] # número de k clusters en función del silhouete

# --- Pestañas de Visualización ---
tab1, tab2 = st.tabs(["Clustering de Jugadores", "Buscador de Jugadores Similares"])

with tab1: #Clusters
    st.header(f"Arquetipos de {selected_position} en {selected_year}")
    
    with st.expander("Ver Análisis para Determinar el Número Óptimo de Clústeres (k)"):
        st.markdown("Estos gráficos se actualizan dinámicamente según los filtros seleccionados.")
        col1, col2 = st.columns(2)
        with col1:
            fig_inertia = px.line(x=k_range, y=inertias, title='Método del Codo (Inertia)', markers=True, labels={'x':'Número de Clústeres (k)', 'y':'Inercia'})
            st.plotly_chart(fig_inertia, use_container_width=True) #Gráfico del codo para la inercia
        with col2:
            fig_silhouette = px.line(x=k_range, y=silhouette_scores, title='Coeficiente de Silueta', markers=True, labels={'x':'Número de Clústeres (k)', 'y':'Silhouette Score'})
            st.plotly_chart(fig_silhouette, use_container_width=True) #Gráfico del codo para el silhouette
        st.success(f"**Recomendación:** El número óptimo de clústeres según el Silhouette Score es **{recommended_k}**.")

    st.markdown("---")
    selected_k = st.slider("Selecciona el número de clústeres para visualizar:", min_value=1, max_value=8, value=recommended_k)
    
    model_results_df = run_full_model(model_df, scaled_features, selected_k)
    
    plot_df = model_results_df.copy()
    plot_df['cluster'] = plot_df['cluster'].astype(str)
    fig_cluster = px.scatter( #Representación de jugadores por cluster sobre las 2 primeras componentes
        plot_df, x='PC1', y='PC2', color='cluster', hover_name='player_name',
        hover_data={'team': True, 'cluster': True, 'PC1': False, 'PC2': False},
        title=f'Clústeres de {selected_position} ({selected_year}) con k={selected_k}'
    )
    fig_cluster.update_layout(xaxis_title="Componente Principal 1", yaxis_title="Componente Principal 2", legend_title_text='Clúster')
    st.plotly_chart(fig_cluster, use_container_width=True)

    st.markdown("---")
    st.subheader("Caracterización de Arquetipos") #Tabla con las estadísticas medias de cada cluster
    st.markdown("La siguiente tabla muestra el valor medio de cada métrica para los jugadores de cada clúster, permitiendo definir cada arquetipo.")
    cluster_summary = model_results_df.groupby('cluster')[features].mean().T
    st.dataframe(cluster_summary.style.format("{:.2f}").background_gradient(cmap='Blues', axis=1)) #Escala de color azul gradual


with tab2: #Similitud
    st.header(f"Buscador de Jugadores Similares ({selected_position} en {selected_year})")
    st.markdown("Selecciona un jugador para encontrar los perfiles estadísticos más parecidos en la liga.")

    player_list = sorted(model_df['player_name'].unique())
    selected_player = st.selectbox("Selecciona un jugador:", player_list)

    if selected_player and selected_player in model_df['player_name'].values:
        player_index = model_df[model_df['player_name'] == selected_player].index[0]
        player_vector = scaled_features[player_index].reshape(1, -1) #Vector 2D (1, n)
        distances = euclidean_distances(scaled_features, player_vector) #Distancias euclideas del resto de jugadores al jugador seleccionado
        
        similarity_df = model_df.copy()
        similarity_df['distance'] = distances
        similarity_df['similarity_score'] = (1 / (1 + similarity_df['distance'])) * 100 #Formula de similitud (de 1 a 100) en función de la distancia (cuanto más cerca mayor similitud)
        
        similar_players = similarity_df[similarity_df['player_name'] != selected_player].sort_values(by='distance', ascending=True)

        st.markdown("---")
        st.subheader(f"Top 10 Jugadores más similares a {selected_player}:") #Tabla con los 10 jugadores más similares
        
        display_cols = ['player_name', 'team', 'similarity_score'] + features
        st.dataframe(
            similar_players[display_cols].head(10).style.format({'similarity_score': "{:.1f}%"}, subset=['similarity_score'])
                                                          .format("{:.2f}", subset=features)
                                                          .background_gradient(cmap='Greens', subset=['similarity_score']) #Score de similitud en escala gradual de verdes
        )
    else:
        st.warning("El jugador seleccionado no se encuentra en el conjunto de datos filtrado. Por favor, selecciona otro jugador.")


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