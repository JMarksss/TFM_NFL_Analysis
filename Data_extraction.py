"""
Created on Mon Jun 16 16:17:14 2025

@author: jmarcos
"""

#Importamos las librerías
import pandas as pd
import numpy as np
import nfl_data_py as nfl

# Diccionario con la información de Conferencia y División de cada equipo.
TEAM_INFO_MAP = {
    'ARI': {'conference': 'NFC', 'division': 'NFC West'}, 'ATL': {'conference': 'NFC', 'division': 'NFC South'},
    'BAL': {'conference': 'AFC', 'division': 'AFC North'}, 'BUF': {'conference': 'AFC', 'division': 'AFC East'},
    'CAR': {'conference': 'NFC', 'division': 'NFC South'}, 'CHI': {'conference': 'NFC', 'division': 'NFC North'},
    'CIN': {'conference': 'AFC', 'division': 'AFC North'}, 'CLE': {'conference': 'AFC', 'division': 'AFC North'},
    'DAL': {'conference': 'NFC', 'division': 'NFC East'}, 'DEN': {'conference': 'AFC', 'division': 'AFC West'},
    'DET': {'conference': 'NFC', 'division': 'NFC North'}, 'GB': {'conference': 'NFC', 'division': 'NFC North'},
    'HOU': {'conference': 'AFC', 'division': 'AFC South'}, 'IND': {'conference': 'AFC', 'division': 'AFC South'},
    'JAX': {'conference': 'AFC', 'division': 'AFC South'}, 'KC': {'conference': 'AFC', 'division': 'AFC West'},
    'LA': {'conference': 'NFC', 'division': 'NFC West'}, 'LAC': {'conference': 'AFC', 'division': 'AFC West'},
    'LV': {'conference': 'AFC', 'division': 'AFC West'}, 'MIA': {'conference': 'AFC', 'division': 'AFC East'},
    'MIN': {'conference': 'NFC', 'division': 'NFC North'}, 'NE': {'conference': 'AFC', 'division': 'AFC East'},
    'NO': {'conference': 'NFC', 'division': 'NFC South'}, 'NYG': {'conference': 'NFC', 'division': 'NFC East'},
    'NYJ': {'conference': 'AFC', 'division': 'AFC East'}, 'PHI': {'conference': 'NFC', 'division': 'NFC East'},
    'PIT': {'conference': 'AFC', 'division': 'AFC North'}, 'SEA': {'conference': 'NFC', 'division': 'NFC West'},
    'SF': {'conference': 'NFC', 'division': 'NFC West'}, 'TB': {'conference': 'NFC', 'division': 'NFC South'},
    'TEN': {'conference': 'AFC', 'division': 'AFC South'}, 'WAS': {'conference': 'NFC', 'division': 'NFC East'}
}


def create_nfl_stats_report_advanced(start_year=2020, end_year=2024): #Parámetros de entrada los años de inicio y final, valores por defecto, pero se pueden modificar
    """
    Genera 3 csvs con estadísticas avanzadas para equipos y jugadores,
    utilizando únicamente datos de la temporada regular
    """
    years = list(range(start_year, end_year + 1)) #Lista de temporadas
    print(f"Iniciando la generación de reportes para las temporadas: {years}...")

    try: #Importamos los datos, exception en caso de error
        pbp_data_full = nfl.import_pbp_data(years=years)
        roster_data = nfl.import_seasonal_rosters(years=years)
        seasonal_player_data_full = nfl.import_seasonal_data(years=years)
        print("Datos cargados exitosamente.\n")
        
        # --- FILTRADO POR TEMPORADA REGULAR ---
        print("Filtrando datos para mantener solo la Temporada Regular ('REG')...")
        pbp_data = pbp_data_full[pbp_data_full['season_type'] == 'REG'].copy() #filtro
        seasonal_player_data = seasonal_player_data_full[seasonal_player_data_full['season_type'] == 'REG'].copy()
        print("Filtrado completado.\n")

    except Exception as e:
        print(f"Error al cargar los datos: {e}")
        return

    # --- TABLA 1: OFENSIVA AVANZADA POR EQUIPO Y AÑO ---
    print("--- Procesando Tabla Ofensiva Avanzada ---")
    pass_plays = pbp_data.loc[pbp_data['pass_attempt'] == 1] #jugadas de pase
    rush_plays = pbp_data.loc[pbp_data['rush_attempt'] == 1] #jugadas de carrera

    team_pass_offense = pass_plays.groupby(['posteam', 'season']).agg( #Groupby y sumatorios de las estadísticas play by play para tener datos agregados de la temporada
        pass_completions=('complete_pass', 'sum'), pass_attempts=('pass_attempt', 'sum'),
        passing_yards=('passing_yards', 'sum'), passing_tds=('pass_touchdown', 'sum'),
        interceptions=('interception', 'sum'), sacks_taken=('sack', 'sum')
    ).reset_index()

    team_rush_offense = rush_plays.groupby(['posteam', 'season']).agg(
        rush_attempts=('rush_attempt', 'sum'), rushing_yards=('rushing_yards', 'sum'),
        rushing_tds=('rush_touchdown', 'sum'), fumbles_lost=('fumble_lost', 'sum')
    ).reset_index()

    offensive_df = pd.merge(team_pass_offense, team_rush_offense, on=['posteam', 'season'], how='outer').fillna(0) #Juntamos ambos dataframes (pase y carrera) y rellenamos los nulos con 0
    offensive_df = offensive_df.rename(columns={'posteam': 'team', 'season': 'year'})

    # CÁLCULO DE MÉTRICAS 
    offensive_df['total_plays'] = offensive_df['pass_attempts'] + offensive_df['rush_attempts']
    offensive_df['total_yards'] = offensive_df['passing_yards'] + offensive_df['rushing_yards']
    offensive_df['total_turnovers'] = offensive_df['interceptions'] + offensive_df['fumbles_lost']
    offensive_df['offensive_tds'] = offensive_df['passing_tds'] + offensive_df['rushing_tds']
    
    offensive_df['yards_per_play'] = offensive_df['total_yards'] / offensive_df['total_plays']
    offensive_df['cmp_percentage'] = (offensive_df['pass_completions'] / offensive_df['pass_attempts']) * 100
    offensive_df['yards_per_pass'] = offensive_df['passing_yards'] / offensive_df['pass_attempts']
    offensive_df['yards_per_rush'] = offensive_df['rushing_yards'] / offensive_df['rush_attempts']
    offensive_df['net_yards_per_pass'] = offensive_df['passing_yards'] / (offensive_df['pass_attempts'] + offensive_df['sacks_taken'])
    offensive_df['pass_td_int_ratio'] = offensive_df['passing_tds'] / offensive_df['interceptions'].replace(0, 1)

    offensive_df['conference'] = offensive_df['team'].map(lambda x: TEAM_INFO_MAP.get(x, {}).get('conference')) #Añadimos variables de conferencia y división (diccionario)
    offensive_df['division'] = offensive_df['team'].map(lambda x: TEAM_INFO_MAP.get(x, {}).get('division'))
    
    offensive_df.to_csv(f'offensive_team_stats_advanced_{start_year}-{end_year}.csv', index=False)
    print(f"Tabla ofensiva avanzada guardada.\n")

    # --- TABLA 2: DEFENSIVA AVANZADA POR EQUIPO Y AÑO ---
    print("--- Procesando Tabla Defensiva Avanzada ---")
    team_pass_defense = pbp_data.loc[pbp_data['pass_attempt'] == 1].groupby(['defteam', 'season']).agg(
        completions_allowed=('complete_pass', 'sum'), pass_attempts_faced=('pass_attempt', 'sum'),
        passing_yards_allowed=('passing_yards', 'sum'), passing_tds_allowed=('pass_touchdown', 'sum'),
        interceptions_made=('interception', 'sum'), sacks_made=('sack', 'sum')
    ).reset_index()

    team_rush_defense = pbp_data.loc[pbp_data['rush_attempt'] == 1].groupby(['defteam', 'season']).agg(
        rush_attempts_faced=('rush_attempt', 'sum'), rushing_yards_allowed=('rushing_yards', 'sum'),
        rushing_tds_allowed=('rush_touchdown', 'sum'), fumbles_forced=('fumble_forced', 'sum')
    ).reset_index()

    defensive_df = pd.merge(team_pass_defense, team_rush_defense, on=['defteam', 'season'], how='outer').fillna(0)
    defensive_df = defensive_df.rename(columns={'defteam': 'team', 'season': 'year'})

    defensive_df['total_plays_faced'] = defensive_df['pass_attempts_faced'] + defensive_df['rush_attempts_faced']
    defensive_df['total_yards_allowed'] = defensive_df['passing_yards_allowed'] + defensive_df['rushing_yards_allowed']
    defensive_df['turnovers_forced'] = defensive_df['interceptions_made'] + defensive_df['fumbles_forced']
    defensive_df['offensive_tds_allowed'] = defensive_df['passing_tds_allowed'] + defensive_df['rushing_tds_allowed']
    
    defensive_df['yards_per_play_allowed'] = defensive_df['total_yards_allowed'] / defensive_df['total_plays_faced']
    defensive_df['opponent_cmp_percentage'] = (defensive_df['completions_allowed'] / defensive_df['pass_attempts_faced']) * 100
    defensive_df['yards_per_pass_allowed'] = defensive_df['passing_yards_allowed'] / defensive_df['pass_attempts_faced']
    defensive_df['yards_per_rush_allowed'] = defensive_df['rushing_yards_allowed'] / defensive_df['rush_attempts_faced']
    defensive_df['sack_rate'] = (defensive_df['sacks_made'] / defensive_df['pass_attempts_faced']) * 100
    
    defensive_df['conference'] = defensive_df['team'].map(lambda x: TEAM_INFO_MAP.get(x, {}).get('conference'))
    defensive_df['division'] = defensive_df['team'].map(lambda x: TEAM_INFO_MAP.get(x, {}).get('division'))
    
    defensive_df.to_csv(f'defensive_team_stats_advanced_{start_year}-{end_year}.csv', index=False)
    print(f"Tabla defensiva avanzada guardada.\n")

    # --- TABLA 3: ESTADÍSTICAS AVANZADAS POR JUGADOR Y AÑO ---
    print("--- Procesando Tabla de Jugadores Avanzada ---")
    roster_info = roster_data[['player_id', 'player_name', 'position', 'team', 'season']].drop_duplicates() #Eliminar posibles duplicados
    player_df = pd.merge(seasonal_player_data, roster_info, on=['player_id', 'season'], how='left')
    player_df = player_df.rename(columns={'season': 'year'})
    
    player_df.to_csv(f'detailed_player_stats_advanced_{start_year}-{end_year}.csv', index=False)
    print(f"Tabla de jugadores avanzada guardada.\n")
    
    print("¡Proceso completado exitosamente!")


# --- EJECUTAR LA FUNCIÓN ---
if __name__ == '__main__':
    create_nfl_stats_report_advanced(start_year=2020, end_year=2024)
