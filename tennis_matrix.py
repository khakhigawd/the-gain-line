import pandas as pd
import requests
import io
import json
import webbrowser
import os
import traceback
from datetime import datetime, timedelta

print("Building Enhanced Tennis Matrix with H2H...")

url_2024 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv"
url_2023 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2023.csv"
url_2022 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2022.csv"

def load_match_data(url):
    r = requests.get(url)
    return pd.read_csv(io.StringIO(r.text))

def load_rankings():
    print("Loading player names...")
    players_r = requests.get('https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_players.csv')
    players_df = pd.read_csv(io.StringIO(players_r.text), low_memory=False)
    players_df['full_name'] = players_df['name_first'] + ' ' + players_df['name_last']
    print("Loading rankings...")
    rankings_r = requests.get('https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_rankings_current.csv')
    rankings_df = pd.read_csv(io.StringIO(rankings_r.text))
    latest_date = rankings_df['ranking_date'].max()
    current = rankings_df[rankings_df['ranking_date'] == latest_date].head(100)
    merged = current.merge(
        players_df[['player_id', 'full_name', 'ioc', 'height', 'dob', 'hand']],
        left_on='player', right_on='player_id'
    )
    return merged[['rank', 'full_name', 'ioc', 'points', 'height', 'dob', 'hand']].sort_values('rank')

def get_tennis_odds():
    try:
        url = 'https://api.the-odds-api.com/v4/sports/tennis_atp_madrid_open/odds/'
        params = {'apiKey': 'a3fd838c65e47cfdce22a13933f01a75', 'regions': 'us', 'markets': 'h2h', 'oddsFormat': 'american'}
        r = requests.get(url, params=params)
        data = r.json()
        odds_dict = {}
        for match in data:
            for bm in match['bookmakers']:
                if bm['key'] in ['draftkings', 'fanduel']:
                    for market in bm['markets']:
                        if market['key'] == 'h2h':
                            for outcome in market['outcomes']:
                                player = outcome['name']
                                price = outcome['price']
                                if player not in odds_dict or bm['key'] == 'draftkings':
                                    odds_dict[player] = {'price': price, 'book': 'DraftKings' if bm['key'] == 'draftkings' else 'FanDuel'}
        return odds_dict
    except Exception as e:
        print("Odds error: " + str(e))
        return {}

def get_player_stats(player_name, df, surface=None, months=None, tourney_level=None):
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
    lost['opp_firstWon'] = lost['w_1stWon']
    lost['opp_secondWon'] = lost['w_2ndWon']
    lost['opp_bpSaved'] = lost['w_bpSaved']
    lost['opp_bpFaced'] = lost['w_bpFaced']
    lost['result'] = 0

    cols = ['surface', 'tourney_level', 'tourney_date', 'result',
            'aces', 'df_col', 'svpt', 'firstIn', 'firstWon', 'secondWon',
            'bpSaved', 'bpFaced', 'opp_svpt', 'opp_firstWon', 'opp_secondWon',
            'opp_bpSaved', 'opp_bpFaced']

    all_matches = pd.concat([won[cols], lost[cols]], ignore_index=True)

    if surface and surface != 'all':
        all_matches = all_matches[all_matches['surface'] == surface.capitalize()]
    if tourney_level and tourney_level != 'all':
        all_matches = all_matches[all_matches['tourney_level'] == tourney_level]
    if months:
        cutoff = int((datetime.now() - timedelta(days=months*30)).strftime('%Y%m%d'))
        all_matches['tourney_date'] = pd.to_numeric(all_matches['tourney_date'], errors='coerce')
        all_matches = all_matches[all_matches['tourney_date'] >= cutoff]

    if len(all_matches) == 0:
        return None

    matches = len(all_matches)
    wins = int(all_matches['result'].sum())
    win_rate = round(wins / matches * 100, 1)
    avg_aces = round(float(all_matches['aces'].mean()), 1)
    avg_df = round(float(all_matches['df_col'].mean()), 1)
    ace_df_ratio = round(avg_aces / avg_df, 2) if avg_df > 0 else 0

    total_svpt = all_matches['svpt'].sum()
    total_firstIn = all_matches['firstIn'].sum()
    total_firstWon = all_matches['firstWon'].sum()
    total_secondWon = all_matches['secondWon'].sum()
    total_second_attempts = total_svpt - total_firstIn

    first_serve_in_pct = round(float(total_firstIn / total_svpt * 100), 1) if total_svpt > 0 else 0
    first_serve_win_pct = round(float(total_firstWon / total_firstIn * 100), 1) if total_firstIn > 0 else 0
    second_serve_win_pct = round(float(total_secondWon / total_second_attempts * 100), 1) if total_second_attempts > 0 else 0

    total_bpFaced = all_matches['bpFaced'].sum()
    total_bpSaved = all_matches['bpSaved'].sum()
    bp_save_pct = round(float(total_bpSaved / total_bpFaced * 100), 1) if total_bpFaced > 0 else 0

    opp_bpFaced = all_matches['opp_bpFaced'].sum()
    opp_bpSaved = all_matches['opp_bpSaved'].sum()
    bp_convert_pct = round(float((opp_bpFaced - opp_bpSaved) / opp_bpFaced * 100), 1) if opp_bpFaced > 0 else 0

    player_points = total_firstWon + total_secondWon
    opp_points = all_matches['opp_firstWon'].sum() + all_matches['opp_secondWon'].sum()
    total_points = player_points + opp_points
    tpw_pct = round(float(player_points / total_points * 100), 1) if total_points > 0 else 0

    opp_svpt = all_matches['opp_svpt'].sum()
    serve_pts_won_pct = player_points / total_svpt if total_svpt > 0 else 0
    opp_serve_pts_won_pct = opp_points / opp_svpt if opp_svpt > 0 else 0
    dominance_ratio = round(float(serve_pts_won_pct / opp_serve_pts_won_pct), 2) if opp_serve_pts_won_pct > 0 else 0

    return {
        'matches': matches, 'wins': wins, 'win_rate': win_rate,
        'avg_aces': avg_aces, 'avg_df': avg_df, 'ace_df_ratio': ace_df_ratio,
        'first_serve_in_pct': first_serve_in_pct, 'first_serve_win_pct': first_serve_win_pct,
        'second_serve_win_pct': second_serve_win_pct, 'bp_save_pct': bp_save_pct,
        'bp_convert_pct': bp_convert_pct, 'tpw_pct': tpw_pct, 'dominance_ratio': dominance_ratio,
    }

def safe_stats(s):
    if s is None:
        return {'matches': 0, 'wins': 0, 'win_rate': 0, 'avg_aces': 0, 'avg_df': 0,
                'ace_df_ratio': 0, 'first_serve_in_pct': 0, 'first_serve_win_pct': 0,
                'second_serve_win_pct': 0, 'bp_save_pct': 0, 'bp_convert_pct': 0,
                'tpw_pct': 0, 'dominance_ratio': 0}
    return s

def calc_age(dob):
    try:
        dob_str = str(int(dob))
        birth = datetime.strptime(dob_str, '%Y%m%d')
        return (datetime.now() - birth).days // 365
    except:
        return 'N/A'

try:
    print("Loading match data...")
    df_2022 = load_match_data(url_2022)
    df_2023 = load_match_data(url_2023)
    df_2024 = load_match_data(url_2024)
    df = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)
    print("Loaded " + str(len(df)) + " matches")

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
    print("H2H data built: " + str(len(matches_list)) + " matches")

    rankings = load_rankings()
    print("Loaded " + str(len(rankings)) + " ranked players")

    print("Fetching odds...")
    odds = get_tennis_odds()
    print("Odds found for " + str(len(odds)) + " players")

    js_players = []
    for _, row in rankings.iterrows():
        player_name = str(row['full_name'])
        rank = int(row['rank'])
        country = str(row['ioc'])
        height = str(int(row['height'])) + 'cm' if not pd.isna(row['height']) else 'N/A'
        age = calc_age(row['dob'])
        hand = str(row['hand']) if not pd.isna(row['hand']) else 'N/A'

        print("Processing #" + str(rank) + " " + player_name + "...")

        clay_stats = get_player_stats(player_name, df, 'clay')
        hard_stats = get_player_stats(player_name, df, 'hard')
        grass_stats = get_player_stats(player_name, df, 'grass')
        all_stats = get_player_stats(player_name, df, 'all')
        form_stats = get_player_stats(player_name, df, 'all', months=6)
        grand_slam_stats = get_player_stats(player_name, df, 'all', tourney_level='G')
        masters_stats = get_player_stats(player_name, df, 'all', tourney_level='M')

        player_odds = odds.get(player_name, None)
        odds_str = 'N/A'
        if player_odds:
            price = player_odds['price']
            odds_str = ('+' + str(price)) if price > 0 else str(price)

        js_players.append({
            'name': player_name, 'country': country, 'rank': rank,
            'height': height, 'age': age, 'hand': hand, 'odds': odds_str,
            'clay': safe_stats(clay_stats), 'hard': safe_stats(hard_stats),
            'grass': safe_stats(grass_stats), 'all': safe_stats(all_stats),
            'form': safe_stats(form_stats), 'grandslam': safe_stats(grand_slam_stats),
            'masters': safe_stats(masters_stats),
        })

    js_data = 'const tennisData = ' + json.dumps(js_players) + ';\n'
    js_data += 'const matchData = ' + json.dumps(matches_list) + ';\n'

    css = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #0a0a0a; color: #ffffff; overflow-x: auto; }
.header { background: #111; border-bottom: 2px solid #222; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 22px; font-weight: bold; color: #fff; letter-spacing: 1px; }
.logo span { color: #4CAF50; }
.nav-tabs { display: flex; gap: 5px; }
.nav-tab { padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 13px; background: #1a1a1a; color: #888; border: 1px solid #333; }
.nav-tab.active { background: #4CAF50; color: #fff; border-color: #4CAF50; }
.controls { display: flex; gap: 10px; padding: 15px 20px; background: #0f0f0f; border-bottom: 1px solid #222; flex-wrap: wrap; align-items: center; }
.control-group { display: flex; flex-direction: column; gap: 4px; }
.control-label { font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; }
select, input { background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 5px; padding: 8px 12px; font-size: 13px; cursor: pointer; }
select:focus, input:focus { outline: none; border-color: #4CAF50; }
.search-box { flex: 1; min-width: 200px; }
.container { padding: 20px; }
.matrix-title { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
.matrix-subtitle { font-size: 12px; color: #666; margin-bottom: 15px; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
th { background: #1a1a1a; padding: 8px 10px; text-align: center; font-size: 10px; color: #888; letter-spacing: 1px; border-bottom: 2px solid #333; text-transform: uppercase; position: sticky; top: 0; z-index: 10; white-space: nowrap; }
th.left { text-align: left; }
td { padding: 8px 10px; text-align: center; border-bottom: 1px solid #151515; white-space: nowrap; }
.player-name { text-align: left; font-weight: bold; font-size: 13px; }
.country-badge { font-size: 10px; padding: 2px 5px; border-radius: 3px; background: #222; color: #aaa; }
.stat-cell { font-weight: bold; font-size: 13px; border-radius: 3px; padding: 4px 8px; display: inline-block; min-width: 45px; }
.odds-cell { font-size: 12px; font-weight: bold; }
tr:hover { background: #111; }
.count-badge { background: #333; color: #888; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; }
.footer { text-align: center; color: #333; font-size: 11px; padding: 20px; border-top: 1px solid #111; margin-top: 20px; }
.legend { display: flex; gap: 20px; justify-content: center; margin: 15px 0; font-size: 12px; color: #888; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-box { width: 12px; height: 12px; border-radius: 2px; flex-shrink: 0; }
.h2h-btn { background: #1a3a1a; color: #4CAF50; border: 1px solid #4CAF50; border-radius: 4px; padding: 4px 10px; font-size: 11px; cursor: pointer; font-weight: bold; }
.h2h-btn:hover { background: #4CAF50; color: #fff; }
.modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: flex-start; padding-top: 50px; }
.modal-overlay.active { display: flex; }
.modal { background: #111; border-radius: 10px; padding: 25px; width: 90%; max-width: 700px; max-height: 80vh; overflow-y: auto; border: 1px solid #333; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-title { font-size: 16px; font-weight: bold; color: #4CAF50; }
.modal-close { background: none; border: none; color: #888; font-size: 24px; cursor: pointer; line-height: 1; }
.modal-close:hover { color: #fff; }
.h2h-search { width: 100%; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 5px; padding: 10px; font-size: 14px; margin-bottom: 8px; }
.h2h-search:focus { outline: none; border-color: #4CAF50; }
.h2h-lookup-btn { background: #4CAF50; color: #fff; border: none; border-radius: 5px; padding: 10px 20px; font-size: 14px; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 20px; margin-top: 8px; }
.h2h-lookup-btn:hover { background: #45a045; }
.h2h-scoreboard { display: flex; justify-content: space-around; align-items: center; background: #1a1a1a; border-radius: 8px; padding: 20px; margin-bottom: 15px; text-align: center; }
.h2h-wins { font-size: 42px; font-weight: bold; color: #4CAF50; }
.h2h-pname { font-size: 14px; font-weight: bold; margin-bottom: 6px; }
.h2h-vs { font-size: 22px; color: #444; font-weight: bold; }
.surf-row { display: flex; gap: 10px; margin-bottom: 15px; flex-wrap: wrap; }
.surf-box { flex: 1; min-width: 80px; background: #1a1a1a; border-radius: 6px; padding: 10px; text-align: center; }
.surf-label { font-size: 10px; text-transform: uppercase; margin-bottom: 4px; }
.surf-rec { font-size: 16px; font-weight: bold; }
.clay-c { color: #cc7700; }
.hard-c { color: #4488ff; }
.grass-c { color: #4CAF50; }
.meetings-hdr { font-size: 12px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; font-weight: bold; }
.match-card { background: #0a0a0a; border-radius: 5px; padding: 10px 14px; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px; }
.mwinner { font-weight: bold; color: #4CAF50; font-size: 13px; }
.mscore { color: #aaa; font-size: 12px; }
.mmeta { display: flex; gap: 6px; align-items: center; font-size: 11px; color: #666; }
.pill { padding: 2px 7px; border-radius: 10px; font-size: 10px; font-weight: bold; }
.clay-pill { background: #3a1a00; color: #cc7700; }
.hard-pill { background: #001a3a; color: #4488ff; }
.grass-pill { background: #001a00; color: #4CAF50; }
.gs-pill { background: #2a2000; color: #ccaa00; }
.m-pill { background: #001a2a; color: #4488ff; }
.sugg-box { background: #1a1a1a; border: 1px solid #333; border-radius: 5px; max-height: 150px; overflow-y: auto; margin-bottom: 8px; }
.sugg-item { padding: 8px 12px; cursor: pointer; font-size: 13px; border-bottom: 1px solid #222; }
.sugg-item:hover { background: #252525; color: #4CAF50; }
"""

    js_code = """
function getColor(val, high, mid) {
  if (val >= high) return '#1a7a1a';
  if (val >= mid) return '#7a6a00';
  return '#7a1a1a';
}

function populateCountries() {
  const countries = [...new Set(tennisData.map(p => p.country))].sort();
  const select = document.getElementById('countryFilter');
  countries.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    select.appendChild(opt);
  });
}

function renderTable() {
  const surface = document.getElementById('surfaceFilter').value;
  const country = document.getElementById('countryFilter').value;
  const hand = document.getElementById('handFilter').value;
  const minMatches = parseInt(document.getElementById('minMatches').value);
  const sortBy = document.getElementById('sortBy').value;
  const search = document.getElementById('searchBox').value.toLowerCase();
  const subtitles = {
    'clay': 'Clay Court Stats | 2022-2024 Data | Madrid Open Preview',
    'hard': 'Hard Court Stats | 2022-2024 Data',
    'grass': 'Grass Court Stats | 2022-2024 Data | Wimbledon Preview',
    'all': 'All Surface Stats | 2022-2024 Data',
    'form': 'Last 6 Months Form | 2024 Data',
    'grandslam': 'Grand Slam Performance | 2022-2024 Data',
    'masters': 'Masters 1000 Performance | 2022-2024 Data'
  };
  document.getElementById('matrixSubtitle').textContent = subtitles[surface] || '';
  let filtered = tennisData.filter(p => {
    const s = p[surface];
    if (country !== 'all' && p.country !== country) return false;
    if (hand !== 'all' && p.hand !== hand) return false;
    if (search && !p.name.toLowerCase().includes(search)) return false;
    if (!s || s.matches < minMatches) return false;
    return true;
  });
  filtered.sort((a, b) => {
    const sa = a[surface]; const sb = b[surface];
    if (sortBy === 'win_rate') return sb.win_rate - sa.win_rate;
    if (sortBy === 'rank') return a.rank - b.rank;
    if (sortBy === 'tpw') return sb.tpw_pct - sa.tpw_pct;
    if (sortBy === 'dominance') return sb.dominance_ratio - sa.dominance_ratio;
    if (sortBy === 'first_win') return sb.first_serve_win_pct - sa.first_serve_win_pct;
    if (sortBy === 'second_win') return sb.second_serve_win_pct - sa.second_serve_win_pct;
    if (sortBy === 'bp_save') return sb.bp_save_pct - sa.bp_save_pct;
    if (sortBy === 'bp_convert') return sb.bp_convert_pct - sa.bp_convert_pct;
    if (sortBy === 'aces') return sb.avg_aces - sa.avg_aces;
    if (sortBy === 'ace_df') return sb.ace_df_ratio - sa.ace_df_ratio;
    return 0;
  });
  document.getElementById('playerCount').textContent = filtered.length + ' players';
  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';
  filtered.forEach(p => {
    const s = p[surface];
    if (!s || s.matches === 0) return;
    const oddsColor = p.odds === 'N/A' ? '#555' : p.odds.startsWith('+') ? '#4CAF50' : '#4488ff';
    const safeName = p.name.replace(/'/g, "\\\\'");
    const row = document.createElement('tr');
    row.innerHTML =
      '<td class="player-name">' + p.name + '</td>' +
      '<td><span class="country-badge">' + p.country + '</span></td>' +
      '<td>#' + p.rank + '</td>' +
      '<td>' + p.age + '</td>' +
      '<td>' + p.height + '</td>' +
      '<td>' + p.hand + '</td>' +
      '<td>' + s.matches + '</td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.win_rate,75,60) + '">' + s.win_rate + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.tpw_pct,54,50) + '">' + s.tpw_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.dominance_ratio,1.2,1.0) + '">' + s.dominance_ratio + '</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.first_serve_in_pct,68,62) + '">' + s.first_serve_in_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.first_serve_win_pct,75,68) + '">' + s.first_serve_win_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.second_serve_win_pct,55,48) + '">' + s.second_serve_win_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.bp_save_pct,68,62) + '">' + s.bp_save_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.bp_convert_pct,45,35) + '">' + s.bp_convert_pct + '%</span></td>' +
      '<td>' + s.avg_aces + '</td>' +
      '<td>' + s.avg_df + '</td>' +
      '<td>' + s.ace_df_ratio + '</td>' +
      '<td class="odds-cell" style="color:' + oddsColor + '">' + p.odds + '</td>' +
      '<td><button class="h2h-btn" onclick="openH2H(\\'' + safeName + '\\')">H2H</button></td>';
    tbody.appendChild(row);
  });
}

var currentPlayer = '';
var selectedOpp = '';

function openH2H(playerName) {
  currentPlayer = playerName;
  selectedOpp = '';
  document.getElementById('modalTitle').textContent = playerName + ' — H2H';
  document.getElementById('oppInput').value = '';
  document.getElementById('oppSugg').innerHTML = '';
  document.getElementById('h2hResults').innerHTML = '';
  document.getElementById('h2hModal').classList.add('active');
}

function closeH2H() {
  document.getElementById('h2hModal').classList.remove('active');
}

function showOppSugg(val) {
  var box = document.getElementById('oppSugg');
  if (val.length < 2) { box.innerHTML = ''; return; }
  var v = val.toLowerCase();
  var found = tennisData.map(p => p.name)
    .filter(n => n.toLowerCase().includes(v) && n !== currentPlayer)
    .slice(0, 8);
  box.innerHTML = found.map(n =>
    '<div class="sugg-item" onclick="pickOpp(this.textContent)">' + n + '</div>'
  ).join('');
}

function pickOpp(name) {
  selectedOpp = name;
  document.getElementById('oppInput').value = name;
  document.getElementById('oppSugg').innerHTML = '';
}

function getSurfPill(s) {
  if (s==='Clay') return '<span class="pill clay-pill">Clay</span>';
  if (s==='Hard') return '<span class="pill hard-pill">Hard</span>';
  if (s==='Grass') return '<span class="pill grass-pill">Grass</span>';
  return '<span class="pill">' + s + '</span>';
}

function getLvlPill(l) {
  if (l==='G') return '<span class="pill gs-pill">GS</span>';
  if (l==='M') return '<span class="pill m-pill">M</span>';
  return '';
}

function runH2H() {
  var p1 = currentPlayer;
  var p2 = selectedOpp || document.getElementById('oppInput').value.trim();
  if (!p2) { document.getElementById('h2hResults').innerHTML = '<p style="color:#888;text-align:center;padding:15px">Select an opponent</p>'; return; }
  var h2h = matchData.filter(m => (m.w===p1&&m.l===p2)||(m.w===p2&&m.l===p1));
  if (h2h.length === 0) {
    document.getElementById('h2hResults').innerHTML = '<p style="color:#555;text-align:center;padding:20px">No matches found between ' + p1 + ' and ' + p2 + '</p>';
    return;
  }
  var p1w = h2h.filter(m=>m.w===p1).length;
  var p2w = h2h.filter(m=>m.w===p2).length;
  var surfHTML = '';
  ['Clay','Hard','Grass'].forEach(s => {
    var a = h2h.filter(m=>m.w===p1&&m.s===s).length;
    var b = h2h.filter(m=>m.w===p2&&m.s===s).length;
    if (a+b>0) {
      var cls = s==='Clay'?'clay-c':s==='Hard'?'hard-c':'grass-c';
      surfHTML += '<div class="surf-box"><div class="surf-label '+cls+'">'+s+'</div><div class="surf-rec '+cls+'">'+a+'-'+b+'</div></div>';
    }
  });
  var sorted = h2h.slice().sort((a,b)=>parseInt(b.d)-parseInt(a.d));
  var mHTML = sorted.map(m =>
    '<div class="match-card">'+
      '<div><span class="mwinner">'+m.w+'</span> def. <span style="color:#888">'+m.l+'</span> <span class="mscore">'+m.sc+'</span></div>'+
      '<div class="mmeta">'+getLvlPill(m.lv)+getSurfPill(m.s)+'<span>'+m.t+' '+m.d.substring(0,4)+'</span></div>'+
    '</div>'
  ).join('');
  document.getElementById('h2hResults').innerHTML =
    '<div class="h2h-scoreboard">'+
      '<div><div class="h2h-pname">'+p1+'</div><div class="h2h-wins">'+p1w+'</div></div>'+
      '<div class="h2h-vs">VS</div>'+
      '<div><div class="h2h-pname">'+p2+'</div><div class="h2h-wins">'+p2w+'</div></div>'+
    '</div>'+
    '<div class="surf-row">'+surfHTML+'</div>'+
    '<div class="meetings-hdr">All Meetings ('+h2h.length+')</div>'+
    mHTML;
}

document.getElementById('h2hModal').addEventListener('click', function(e) {
  if (e.target === this) closeH2H();
});

populateCountries();
renderTable();
"""

    html_parts = [
        '<!DOCTYPE html><html><head>',
        '<title>The Gain Line - Tennis</title>',
        '<style>', css, '</style>',
        '</head><body>',
        '<div class="header">',
        '<div class="logo">THE <span>GAIN</span> LINE</div>',
        '<div class="nav-tabs">',
        '<div class="nav-tab">Super Rugby Pacific</div>',
        '<div class="nav-tab">EPL Soccer</div>',
        '<div class="nav-tab active">Tennis</div>',
        '</div></div>',
        '<div class="controls">',
        '<div class="control-group"><span class="control-label">Surface / Context</span>',
        '<select id="surfaceFilter" onchange="renderTable()">',
        '<option value="clay">Clay Court</option>',
        '<option value="hard">Hard Court</option>',
        '<option value="grass">Grass Court</option>',
        '<option value="all">All Surfaces</option>',
        '<option value="form">Last 6 Months</option>',
        '<option value="grandslam">Grand Slams Only</option>',
        '<option value="masters">Masters Only</option>',
        '</select></div>',
        '<div class="control-group"><span class="control-label">Country</span>',
        '<select id="countryFilter" onchange="renderTable()"><option value="all">All Countries</option></select></div>',
        '<div class="control-group"><span class="control-label">Hand</span>',
        '<select id="handFilter" onchange="renderTable()">',
        '<option value="all">All</option>',
        '<option value="R">Right</option>',
        '<option value="L">Left</option>',
        '</select></div>',
        '<div class="control-group"><span class="control-label">Min Matches</span>',
        '<select id="minMatches" onchange="renderTable()">',
        '<option value="0">Any</option>',
        '<option value="10">10+</option>',
        '<option value="20" selected>20+</option>',
        '<option value="30">30+</option>',
        '<option value="50">50+</option>',
        '</select></div>',
        '<div class="control-group"><span class="control-label">Sort By</span>',
        '<select id="sortBy" onchange="renderTable()">',
        '<option value="win_rate">Win Rate</option>',
        '<option value="rank">ATP Ranking</option>',
        '<option value="tpw">TPW%</option>',
        '<option value="dominance">Dominance Ratio</option>',
        '<option value="first_win">1st Serve Win%</option>',
        '<option value="second_win">2nd Serve Win%</option>',
        '<option value="bp_save">BP Save%</option>',
        '<option value="bp_convert">BP Convert%</option>',
        '<option value="aces">Avg Aces</option>',
        '<option value="ace_df">Ace/DF Ratio</option>',
        '</select></div>',
        '<div class="control-group search-box"><span class="control-label">Search Player</span>',
        '<input type="text" id="searchBox" placeholder="Search player name..." oninput="renderTable()"></div>',
        '</div>',
        '<div class="container">',
        '<div class="matrix-title">ATP Tennis Matrix <span class="count-badge" id="playerCount"></span></div>',
        '<div class="matrix-subtitle" id="matrixSubtitle">Clay Court Stats | 2022-2024 Data</div>',
        '<div class="legend">',
        '<div class="legend-item"><div class="legend-box" style="background:#1a7a1a"></div>Elite</div>',
        '<div class="legend-item"><div class="legend-box" style="background:#7a6a00"></div>Good</div>',
        '<div class="legend-item"><div class="legend-box" style="background:#7a1a1a"></div>Weak</div>',
        '</div>',
        '<table><thead><tr>',
        '<th class="left">PLAYER</th><th>CTY</th><th>RNK</th><th>AGE</th><th>HT</th><th>HND</th>',
        '<th>M</th><th>WIN%</th><th>TPW%</th><th>DR</th>',
        '<th>1ST IN%</th><th>1ST WIN%</th><th>2ND WIN%</th>',
        '<th>BP SAV%</th><th>BP CNV%</th>',
        '<th>ACES</th><th>DF</th><th>A/DF</th>',
        '<th>ODDS</th><th>H2H</th>',
        '</tr></thead>',
        '<tbody id="tableBody"></tbody></table>',
        '<div class="footer">The Gain Line | ATP Top 100 | Jeff Sackmann Dataset | 2022-2024 Data</div>',
        '</div>',
        '<div class="modal-overlay" id="h2hModal">',
        '<div class="modal">',
        '<div class="modal-header">',
        '<div class="modal-title" id="modalTitle">H2H Lookup</div>',
        '<button class="modal-close" onclick="closeH2H()">&#x2715;</button>',
        '</div>',
        '<input class="h2h-search" id="oppInput" type="text" placeholder="Type opponent name..." oninput="showOppSugg(this.value)" autocomplete="off">',
        '<div class="sugg-box" id="oppSugg"></div>',
        '<button class="h2h-lookup-btn" onclick="runH2H()">LOOK UP H2H</button>',
        '<div id="h2hResults"></div>',
        '</div></div>',
        '<script>',
        js_data,
        js_code,
        '</script>',
        '</body></html>'
    ]

    html = ''.join(html_parts)

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tennis_matrix.html')
    with open(filepath, 'w') as f:
        f.write(html)

    print("\nTennis Matrix with H2H generated! Opening in browser...")
    webbrowser.open('file:///' + filepath)

except Exception as e:
    print("Error: " + str(e))
    traceback.print_exc()