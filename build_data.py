import pandas as pd
import requests
import io
import json
import os
from datetime import datetime, timedelta

print("=" * 60)
print("THE GAIN LINE — DATA PIPELINE")
print("Building complete ATP + WTA player database...")
print("=" * 60)

# ─── DATA SOURCES ───────────────────────────────────────────
ATP_URLS = [
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2022.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2023.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv",
    "https://stats.tennismylife.org/data/2025.csv",
    "https://stats.tennismylife.org/data/2026.csv",
]

WTA_URLS = [
    "https://raw.githubusercontent.com/JeffSackmann/tennis_wta/master/wta_matches_2022.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_wta/master/wta_matches_2023.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_wta/master/wta_matches_2024.csv",
]

ATP_PLAYERS_URL = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_players.csv"
WTA_PLAYERS_URL = "https://raw.githubusercontent.com/JeffSackmann/tennis_wta/master/wta_players.csv"

NUMERIC_COLS = ['w_ace','w_df','w_svpt','w_1stIn','w_1stWon','w_2ndWon',
                'w_bpSaved','w_bpFaced','l_ace','l_df','l_svpt','l_1stIn',
                'l_1stWon','l_2ndWon','l_bpSaved','l_bpFaced',
                'winner_rank','loser_rank']

# ─── LOAD DATA ───────────────────────────────────────────────
def load_csv(url):
    print("  Loading " + url.split('/')[-1] + "...")
    r = requests.get(url)
    df = pd.read_csv(io.StringIO(r.text), low_memory=False)
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def load_players(url):
    r = requests.get(url)
    df = pd.read_csv(io.StringIO(r.text), low_memory=False)
    df['full_name'] = df['name_first'] + ' ' + df['name_last']
    return df

# ─── DERIVE CURRENT RANKINGS FROM MATCH DATA ─────────────────
def derive_rankings(df, players_df):
    print("  Deriving current rankings from match data...")
    df_sorted = df.copy()
    df_sorted['tourney_date'] = pd.to_numeric(df_sorted['tourney_date'], errors='coerce')
    df_sorted = df_sorted.sort_values('tourney_date', ascending=False)

    rankings = {}
    bio = {}

    # Build bio lookup from players file
    for _, row in players_df.iterrows():
        name = str(row['full_name'])
        bio[name] = {
            'ioc': str(row.get('ioc', 'N/A')),
            'height': row.get('height', None),
            'dob': row.get('dob', None),
            'hand': str(row.get('hand', 'N/A')) if not pd.isna(row.get('hand', float('nan'))) else 'N/A'
        }

    # Get most recent ranking for each player
    for _, row in df_sorted.iterrows():
        w = str(row['winner_name'])
        l = str(row['loser_name'])
        if w not in rankings and not pd.isna(row.get('winner_rank', float('nan'))):
            rankings[w] = int(float(row['winner_rank']))
        if l not in rankings and not pd.isna(row.get('loser_rank', float('nan'))):
            rankings[l] = int(float(row['loser_rank']))

    return rankings, bio

# ─── ELO CALCULATOR ──────────────────────────────────────────
def calculate_elo(df):
    print("  Calculating Elo ratings...")
    BASE = 1500
    K_BASE, K_GS, K_MASTERS = 32, 40, 36

    elo = {'overall': {}, 'Clay': {}, 'Hard': {}, 'Grass': {}}
    history = {}

    df_sorted = df.copy()
    df_sorted['tourney_date'] = pd.to_numeric(df_sorted['tourney_date'], errors='coerce')
    df_sorted = df_sorted.sort_values('tourney_date').reset_index(drop=True)

    def get_e(surface, p): return elo[surface].get(p, BASE)
    def exp_s(a, b): return 1 / (1 + 10 ** ((b - a) / 400))

    def update(surface, w, l, k):
        we = get_e(surface, w)
        le = get_e(surface, l)
        ew = exp_s(we, le)
        elo[surface][w] = round(we + k * (1 - ew), 1)
        elo[surface][l] = round(le + k * (0 - (1 - ew)), 1)

    def track(player, surface, val):
        key = player + '_' + surface
        if key not in history: history[key] = []
        history[key].append(val)
        if len(history[key]) > 15: history[key] = history[key][-15:]

    def trend(player, surface):
        key = player + '_' + surface
        h = history.get(key, [])
        if len(h) < 4: return '—'
        recent = sum(h[-3:]) / 3
        older = sum(h[-6:-3]) / 3 if len(h) >= 6 else h[0]
        diff = recent - older
        if diff > 15: return '↑↑'
        if diff > 5: return '↑'
        if diff < -15: return '↓↓'
        if diff < -5: return '↓'
        return '—'

    for _, row in df_sorted.iterrows():
        w = str(row['winner_name'])
        l = str(row['loser_name'])
        s = str(row['surface'])
        lv = str(row['tourney_level'])
        k = K_GS if lv == 'G' else K_MASTERS if lv == 'M' else K_BASE
        update('overall', w, l, k)
        if s in ['Clay', 'Hard', 'Grass']:
            update(s, w, l, k)
            track(w, s, get_e(s, w))
            track(l, s, get_e(s, l))

    def get_player_elo(name):
        return {
            'overall': int(elo['overall'].get(name, BASE)),
            'clay': int(elo['Clay'].get(name, BASE)),
            'hard': int(elo['Hard'].get(name, BASE)),
            'grass': int(elo['Grass'].get(name, BASE)),
            'clay_trend': trend(name, 'Clay'),
            'hard_trend': trend(name, 'Hard'),
            'grass_trend': trend(name, 'Grass'),
        }

    return get_player_elo

# ─── PLAYER STATS CALCULATOR ─────────────────────────────────
def get_player_stats(player_name, df, surface=None, months=None, tourney_level=None, last_n=None):
    won = df[df['winner_name'] == player_name].copy()
    won['aces'] = won['w_ace']
    won['df_col'] = won['w_df']
    won['svpt'] = won['w_svpt']
    won['firstIn'] = won['w_1stIn']
    won['firstWon'] = won['w_1stWon']
    won['secondWon'] = won['w_2ndWon']
    won['bpSaved'] = won['w_bpSaved']
    won['bpFaced'] = won['w_bpFaced']
    won['opp_svpt'] = won['l_svpt']
    won['opp_firstIn'] = won['l_1stIn']
    won['opp_firstWon'] = won['l_1stWon']
    won['opp_secondWon'] = won['l_2ndWon']
    won['opp_bpSaved'] = won['l_bpSaved']
    won['opp_bpFaced'] = won['l_bpFaced']
    won['result'] = 1

    lost = df[df['loser_name'] == player_name].copy()
    lost['aces'] = lost['l_ace']
    lost['df_col'] = lost['l_df']
    lost['svpt'] = lost['l_svpt']
    lost['firstIn'] = lost['l_1stIn']
    lost['firstWon'] = lost['l_1stWon']
    lost['secondWon'] = lost['l_2ndWon']
    lost['bpSaved'] = lost['l_bpSaved']
    lost['bpFaced'] = lost['l_bpFaced']
    lost['opp_svpt'] = lost['w_svpt']
    lost['opp_firstIn'] = lost['w_1stIn']
    lost['opp_firstWon'] = lost['w_1stWon']
    lost['opp_secondWon'] = lost['w_2ndWon']
    lost['opp_bpSaved'] = lost['w_bpSaved']
    lost['opp_bpFaced'] = lost['w_bpFaced']
    lost['result'] = 0

    cols = ['surface', 'tourney_level', 'tourney_date', 'score', 'result',
            'aces', 'df_col', 'svpt', 'firstIn', 'firstWon', 'secondWon',
            'bpSaved', 'bpFaced', 'opp_svpt', 'opp_firstIn', 'opp_firstWon',
            'opp_secondWon', 'opp_bpSaved', 'opp_bpFaced']

    all_m = pd.concat([won[cols], lost[cols]], ignore_index=True)
    all_m['tourney_date'] = pd.to_numeric(all_m['tourney_date'], errors='coerce')
    all_m = all_m.sort_values('tourney_date')

    if surface and surface != 'all':
        all_m = all_m[all_m['surface'] == surface.capitalize()]
    if tourney_level:
        all_m = all_m[all_m['tourney_level'] == tourney_level]
    if months:
        cutoff = int((datetime.now() - timedelta(days=months*30)).strftime('%Y%m%d'))
        all_m = all_m[all_m['tourney_date'] >= cutoff]
    if last_n:
        all_m = all_m.tail(last_n)

    if len(all_m) == 0:
        return None

    def s(col): return pd.to_numeric(all_m[col], errors='coerce').sum()

    matches = len(all_m)
    wins = int(all_m['result'].sum())
    win_rate = round(wins / matches * 100, 1)

    svpt = s('svpt')
    firstIn = s('firstIn')
    firstWon = s('firstWon')
    secondWon = s('secondWon')
    second_att = svpt - firstIn
    bpFaced = s('bpFaced')
    bpSaved = s('bpSaved')
    opp_svpt = s('opp_svpt')
    opp_firstIn = s('opp_firstIn')
    opp_firstWon = s('opp_firstWon')
    opp_secondWon = s('opp_secondWon')
    opp_second_att = opp_svpt - opp_firstIn
    opp_bpFaced = s('opp_bpFaced')
    opp_bpSaved = s('opp_bpSaved')

    first_in_pct = round(firstIn / svpt * 100, 1) if svpt > 0 else 0
    first_won_pct = round(firstWon / firstIn * 100, 1) if firstIn > 0 else 0
    second_won_pct = round(secondWon / second_att * 100, 1) if second_att > 0 else 0
    bp_save_pct = round(bpSaved / bpFaced * 100, 1) if bpFaced > 0 else 0
    bp_convert_pct = round((opp_bpFaced - opp_bpSaved) / opp_bpFaced * 100, 1) if opp_bpFaced > 0 else 0

    ret_first_won = round((opp_firstIn - opp_firstWon) / opp_firstIn * 100, 1) if opp_firstIn > 0 else 0
    ret_second_won = round((opp_second_att - opp_secondWon) / opp_second_att * 100, 1) if opp_second_att > 0 else 0

    player_pts = firstWon + secondWon
    opp_pts = opp_firstWon + opp_secondWon
    total_pts = player_pts + opp_pts
    tpw_pct = round(player_pts / total_pts * 100, 1) if total_pts > 0 else 0

    srv_pts_won = player_pts / svpt if svpt > 0 else 0
    opp_srv_pts_won = opp_pts / opp_svpt if opp_svpt > 0 else 0
    dominance_ratio = round(srv_pts_won / opp_srv_pts_won, 2) if opp_srv_pts_won > 0 else 0

    avg_aces = round(float(pd.to_numeric(all_m['aces'], errors='coerce').mean()), 1)
    avg_df = round(float(pd.to_numeric(all_m['df_col'], errors='coerce').mean()), 1)
    ace_df_ratio = round(avg_aces / avg_df, 2) if avg_df > 0 else 0

    # Service and return games won
    srv_games_won = round(wins / matches * 100, 1) if matches > 0 else 0

    # Tiebreak win rate from scores
    tb_wins = 0
    tb_total = 0
    for _, row in all_m.iterrows():
        score = str(row.get('score', ''))
        if '7-6' in score or '6-7' in score:
            tb_total += 1
            if row['result'] == 1:
                tb_wins += 1
    tb_win_rate = round(tb_wins / tb_total * 100, 1) if tb_total > 0 else 0

    # Deciding set win rate
    dec_wins = 0
    dec_total = 0
    for _, row in all_m.iterrows():
        score = str(row.get('score', ''))
        sets = [s for s in score.split() if '-' in s and s[0].isdigit()]
        if len(sets) >= 3:
            dec_total += 1
            if row['result'] == 1:
                dec_wins += 1
    dec_set_win_rate = round(dec_wins / dec_total * 100, 1) if dec_total > 0 else 0

    return {
        'matches': matches,
        'wins': wins,
        'win_rate': win_rate,
        'tpw_pct': tpw_pct,
        'dominance_ratio': dominance_ratio,
        'first_serve_in_pct': first_in_pct,
        'first_serve_win_pct': first_won_pct,
        'second_serve_win_pct': second_won_pct,
        'bp_save_pct': bp_save_pct,
        'bp_convert_pct': bp_convert_pct,
        'ret_first_won_pct': ret_first_won,
        'ret_second_won_pct': ret_second_won,
        'avg_aces': avg_aces,
        'avg_df': avg_df,
        'ace_df_ratio': ace_df_ratio,
        'tb_win_rate': tb_win_rate,
        'dec_set_win_rate': dec_set_win_rate,
    }

def safe_stats(s):
    if s is None:
        return {k: 0 for k in ['matches','wins','win_rate','tpw_pct','dominance_ratio',
                'first_serve_in_pct','first_serve_win_pct','second_serve_win_pct',
                'bp_save_pct','bp_convert_pct','ret_first_won_pct','ret_second_won_pct',
                'avg_aces','avg_df','ace_df_ratio','tb_win_rate','dec_set_win_rate']}
    return s

def calc_age(dob):
    try:
        dob_str = str(int(dob))
        birth = datetime.strptime(dob_str, '%Y%m%d')
        return (datetime.now() - birth).days // 365
    except:
        return 'N/A'

# ─── BUILD TOUR DATABASE ─────────────────────────────────────
def build_tour(tour_name, match_urls, players_url, is_wta=False):
    print("\n" + "=" * 60)
    print("Building " + tour_name + " database...")
    print("=" * 60)

    print("Loading match data...")
    dfs = []
    for url in match_urls:
        dfs.append(load_csv(url))
    df = pd.concat(dfs, ignore_index=True)
    print("Total matches: " + str(len(df)))

    print("Loading player bio data...")
    players_df = load_players(players_url)

    rankings, bio = derive_rankings(df, players_df)
    print("Players with current rankings: " + str(len(rankings)))

    get_player_elo = calculate_elo(df)

    # Build H2H match list
    print("Building H2H data...")
    matches_list = []
    for _, row in df.iterrows():
        try:
            matches_list.append({
                'w': str(row['winner_name']),
                'l': str(row['loser_name']),
                's': str(row['surface']),
                't': str(row['tourney_name']),
                'd': str(row['tourney_date']),
                'sc': str(row['score']),
                'lv': str(row['tourney_level'])
            })
        except:
            continue

    # Get all active players sorted by ranking
    sorted_players = sorted(rankings.items(), key=lambda x: x[1])
    # Take top 800
    top_players = sorted_players[:800]

    print("Processing " + str(len(top_players)) + " players...")

    players_data = []
    for player_name, rank in top_players:
        print("  #" + str(rank) + " " + player_name + "...")

        player_bio = bio.get(player_name, {})
        height_raw = player_bio.get('height', None)
        dob_raw = player_bio.get('dob', None)
        height = str(int(height_raw)) + 'cm' if height_raw and not pd.isna(height_raw) else 'N/A'
        age = calc_age(dob_raw) if dob_raw else 'N/A'
        country = player_bio.get('ioc', 'N/A')
        hand = player_bio.get('hand', 'N/A')

        elo = get_player_elo(player_name)

        # Surface stats
        clay = get_player_stats(player_name, df, 'clay')
        hard = get_player_stats(player_name, df, 'hard')
        grass = get_player_stats(player_name, df, 'grass')
        all_surf = get_player_stats(player_name, df, 'all')

        # Context filters
        form_6m = get_player_stats(player_name, df, 'all', months=6)
        form_last5 = get_player_stats(player_name, df, 'all', last_n=5)
        form_last10 = get_player_stats(player_name, df, 'all', last_n=10)
        form_last15 = get_player_stats(player_name, df, 'all', last_n=15)
        grandslam = get_player_stats(player_name, df, 'all', tourney_level='G')
        masters = get_player_stats(player_name, df, 'all', tourney_level='M' if not is_wta else 'P')

        # Surface form — last 10 on each surface
        clay_last10 = get_player_stats(player_name, df, 'clay', last_n=10)
        hard_last10 = get_player_stats(player_name, df, 'hard', last_n=10)
        grass_last10 = get_player_stats(player_name, df, 'grass', last_n=10)

        players_data.append({
            'name': player_name,
            'rank': rank,
            'country': country,
            'height': height,
            'age': age,
            'hand': hand,
            'elo': elo,
            'clay': safe_stats(clay),
            'hard': safe_stats(hard),
            'grass': safe_stats(grass),
            'all': safe_stats(all_surf),
            'form_6m': safe_stats(form_6m),
            'last5': safe_stats(form_last5),
            'last10': safe_stats(form_last10),
            'last15': safe_stats(form_last15),
            'grandslam': safe_stats(grandslam),
            'masters': safe_stats(masters),
            'clay_last10': safe_stats(clay_last10),
            'hard_last10': safe_stats(hard_last10),
            'grass_last10': safe_stats(grass_last10),
        })

    return players_data, matches_list

# ─── MAIN ─────────────────────────────────────────────────────
try:
    # Build ATP
    atp_players, atp_matches = build_tour(
        "ATP",
        ATP_URLS,
        ATP_PLAYERS_URL,
        is_wta=False
    )

    # Build WTA
    wta_players, wta_matches = build_tour(
        "WTA",
        WTA_URLS,
        WTA_PLAYERS_URL,
        is_wta=True
    )

    # Save to JSON
    print("\n" + "=" * 60)
    print("Saving data to JSON files...")

    atp_data = {
        'players': atp_players,
        'matches': atp_matches,
        'generated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'total_players': len(atp_players),
        'total_matches': len(atp_matches)
    }

    wta_data = {
        'players': wta_players,
        'matches': wta_matches,
        'generated': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'total_players': len(wta_players),
        'total_matches': len(wta_matches)
    }

    with open('atp_data.json', 'w', encoding='utf-8') as f:
        json.dump(atp_data, f)
    print("Saved atp_data.json — " + str(len(atp_players)) + " players, " + str(len(atp_matches)) + " matches")

    with open('wta_data.json', 'w', encoding='utf-8') as f:
        json.dump(wta_data, f)
    print("Saved wta_data.json — " + str(len(wta_players)) + " players, " + str(len(wta_matches)) + " matches")

    print("\n" + "=" * 60)
    print("DATA PIPELINE COMPLETE")
    print("Generated: " + datetime.now().strftime('%Y-%m-%d %H:%M'))
    print("ATP players: " + str(len(atp_players)))
    print("WTA players: " + str(len(wta_players)))
    print("Run tennis_matrix.py and wta_matrix.py to regenerate dashboards")
    print("=" * 60)

except Exception as e:
    import traceback
    print("Error: " + str(e))
    traceback.print_exc()