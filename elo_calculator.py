import pandas as pd
import requests
import io
from datetime import datetime

print("Building Elo ratings from match data...")

urls = [
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2022.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2023.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv",
    "https://stats.tennismylife.org/data/2025.csv",
    "https://stats.tennismylife.org/data/2026.csv",
]

def load_data(url):
    r = requests.get(url)
    df = pd.read_csv(io.StringIO(r.text), low_memory=False)
    return df

# Load and combine all data
dfs = []
for url in urls:
    print("Loading " + url.split('/')[-1] + "...")
    dfs.append(load_data(url))
df = pd.concat(dfs, ignore_index=True)

# Sort by date so we process matches in order
df['tourney_date'] = pd.to_numeric(df['tourney_date'], errors='coerce')
df = df.sort_values('tourney_date').reset_index(drop=True)
print("Total matches: " + str(len(df)))

# Elo parameters
BASE_ELO = 1500
K_FACTOR = 32
K_GRAND_SLAM = 40
K_MASTERS = 36

def get_k(tourney_level):
    if tourney_level == 'G':
        return K_GRAND_SLAM
    if tourney_level == 'M':
        return K_MASTERS
    return K_FACTOR

def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

# Initialize ratings
elo_overall = {}
elo_clay = {}
elo_hard = {}
elo_grass = {}

# Track last 10 Elo values per player per surface for trend
elo_history = {}

def get_elo(elo_dict, player):
    return elo_dict.get(player, BASE_ELO)

def update_elo(elo_dict, winner, loser, k):
    w_elo = get_elo(elo_dict, winner)
    l_elo = get_elo(elo_dict, loser)
    exp_w = expected_score(w_elo, l_elo)
    exp_l = expected_score(l_elo, w_elo)
    elo_dict[winner] = round(w_elo + k * (1 - exp_w), 1)
    elo_dict[loser] = round(l_elo + k * (0 - exp_l), 1)

def track_history(player, surface, elo_val):
    key = player + '_' + surface
    if key not in elo_history:
        elo_history[key] = []
    elo_history[key].append(elo_val)
    if len(elo_history[key]) > 10:
        elo_history[key] = elo_history[key][-10:]

def get_trend(player, surface):
    key = player + '_' + surface
    history = elo_history.get(key, [])
    if len(history) < 4:
        return '—'
    recent = sum(history[-3:]) / 3
    older = sum(history[-6:-3]) / 3 if len(history) >= 6 else history[0]
    diff = recent - older
    if diff > 15:
        return '↑↑'
    if diff > 5:
        return '↑'
    if diff < -15:
        return '↓↓'
    if diff < -5:
        return '↓'
    return '—'

print("Calculating Elo ratings...")
for _, row in df.iterrows():
    winner = str(row['winner_name'])
    loser = str(row['loser_name'])
    surface = str(row['surface'])
    level = str(row['tourney_level'])
    k = get_k(level)

    # Update overall Elo
    update_elo(elo_overall, winner, loser, k)

    # Update surface specific Elo
    if surface == 'Clay':
        update_elo(elo_clay, winner, loser, k)
        track_history(winner, 'clay', get_elo(elo_clay, winner))
        track_history(loser, 'clay', get_elo(elo_clay, loser))
    elif surface == 'Hard':
        update_elo(elo_hard, winner, loser, k)
        track_history(winner, 'hard', get_elo(elo_hard, winner))
        track_history(loser, 'hard', get_elo(elo_hard, loser))
    elif surface == 'Grass':
        update_elo(elo_grass, winner, loser, k)
        track_history(winner, 'grass', get_elo(elo_grass, winner))
        track_history(loser, 'grass', get_elo(elo_grass, loser))

print("Elo ratings calculated!")

# Load ATP top 100 to show results
players_r = requests.get('https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_players.csv')
players_df = pd.read_csv(io.StringIO(players_r.text), low_memory=False)
players_df['full_name'] = players_df['name_first'] + ' ' + players_df['name_last']

rankings_r = requests.get('https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_rankings_current.csv')
rankings_df = pd.read_csv(io.StringIO(rankings_r.text))
latest_date = rankings_df['ranking_date'].max()
current = rankings_df[rankings_df['ranking_date'] == latest_date].head(50)
merged = current.merge(players_df[['player_id', 'full_name']], left_on='player', right_on='player_id')

print("\n" + "="*90)
print("ATP TOP 50 — ELO RATINGS (2022-2026 DATA)")
print("="*90)
print(f"{'RANK':<6} {'PLAYER':<25} {'OVERALL':<10} {'CLAY':<10} {'TREND':<8} {'HARD':<10} {'TREND':<8} {'GRASS':<10} {'TREND'}")
print("-"*90)

for _, row in merged.iterrows():
    name = str(row['full_name'])
    rank = int(row['rank'])
    overall = int(get_elo(elo_overall, name))
    clay = int(get_elo(elo_clay, name))
    hard = int(get_elo(elo_hard, name))
    grass = int(get_elo(elo_grass, name))
    clay_trend = get_trend(name, 'clay')
    hard_trend = get_trend(name, 'hard')
    grass_trend = get_trend(name, 'grass')
    print(f"#{rank:<5} {name:<25} {overall:<10} {clay:<10} {clay_trend:<8} {hard:<10} {hard_trend:<8} {grass:<10} {grass_trend}")

print("\nDone.")