import pandas as pd
import requests
import io
import json
import webbrowser
import os
import random
from datetime import datetime, timedelta

print("Building Match Simulator...")

url_2022 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2022.csv"
url_2023 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2023.csv"
url_2024 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv"
url_2025 = "https://stats.tennismylife.org/data/2025.csv"
url_2026 = "https://stats.tennismylife.org/data/2026.csv"

def load_match_data(url):
    r = requests.get(url)
    df = pd.read_csv(io.StringIO(r.text), low_memory=False)
    numeric_cols = ['w_ace', 'w_df', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon',
                    'w_bpSaved', 'w_bpFaced', 'l_ace', 'l_df', 'l_svpt', 'l_1stIn',
                    'l_1stWon', 'l_2ndWon', 'l_bpSaved', 'l_bpFaced']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

def load_rankings():
    players_r = requests.get('https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_players.csv')
    players_df = pd.read_csv(io.StringIO(players_r.text), low_memory=False)
    players_df['full_name'] = players_df['name_first'] + ' ' + players_df['name_last']
    rankings_r = requests.get('https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_rankings_current.csv')
    rankings_df = pd.read_csv(io.StringIO(rankings_r.text))
    latest_date = rankings_df['ranking_date'].max()
    current = rankings_df[rankings_df['ranking_date'] == latest_date].head(200)
    merged = current.merge(
        players_df[['player_id', 'full_name', 'ioc']],
        left_on='player', right_on='player_id'
    )
    return merged[['rank', 'full_name', 'ioc']].sort_values('rank')

def calculate_elo(df):
    BASE_ELO = 1500
    K_BASE = 32
    K_GS = 40
    K_MASTERS = 36
    elo_clay = {}
    elo_hard = {}
    elo_grass = {}
    elo_overall = {}

    df_sorted = df.copy()
    df_sorted['tourney_date'] = pd.to_numeric(df_sorted['tourney_date'], errors='coerce')
    df_sorted = df_sorted.sort_values('tourney_date').reset_index(drop=True)

    def get_e(d, p): return d.get(p, BASE_ELO)
    def exp_score(a, b): return 1 / (1 + 10 ** ((b - a) / 400))
    def update(d, w, l, k):
        we = get_e(d, w)
        le = get_e(d, l)
        ew = exp_score(we, le)
        d[w] = round(we + k * (1 - ew), 1)
        d[l] = round(le + k * (0 - (1 - ew)), 1)

    for _, row in df_sorted.iterrows():
        w = str(row['winner_name'])
        l = str(row['loser_name'])
        s = str(row['surface'])
        lv = str(row['tourney_level'])
        k = K_GS if lv == 'G' else K_MASTERS if lv == 'M' else K_BASE
        update(elo_overall, w, l, k)
        if s == 'Clay': update(elo_clay, w, l, k)
        elif s == 'Hard': update(elo_hard, w, l, k)
        elif s == 'Grass': update(elo_grass, w, l, k)

    def get_surface_elo(name, surface):
        d = elo_clay if surface == 'Clay' else elo_hard if surface == 'Hard' else elo_grass
        return d.get(name, BASE_ELO)

    return get_surface_elo, elo_overall

def get_player_stats(player_name, df, surface=None):
    won = df[df['winner_name'] == player_name].copy()
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

    cols = ['surface', 'result', 'svpt', 'firstIn', 'firstWon', 'secondWon',
            'bpSaved', 'bpFaced', 'opp_svpt', 'opp_firstIn', 'opp_firstWon',
            'opp_secondWon', 'opp_bpSaved', 'opp_bpFaced']

    all_m = pd.concat([won[cols], lost[cols]], ignore_index=True)
    if surface:
        all_m = all_m[all_m['surface'] == surface]
    if len(all_m) < 5:
        all_m = pd.concat([won[cols], lost[cols]], ignore_index=True)
    if len(all_m) == 0:
        return None

    def s(col): return pd.to_numeric(all_m[col], errors='coerce').sum()

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

    first_in_pct = firstIn / svpt if svpt > 0 else 0.62
    first_won_pct = firstWon / firstIn if firstIn > 0 else 0.70
    second_won_pct = secondWon / second_att if second_att > 0 else 0.50
    bp_save_pct = bpSaved / bpFaced if bpFaced > 0 else 0.62

    # Return stats derived from opponent serve stats
    ret_first_won = (opp_firstIn - opp_firstWon) / opp_firstIn if opp_firstIn > 0 else 0.30
    ret_second_won = (opp_second_att - opp_secondWon) / opp_second_att if opp_second_att > 0 else 0.48
    bp_convert_pct = (opp_bpFaced - opp_bpSaved) / opp_bpFaced if opp_bpFaced > 0 else 0.38

    wins = int(all_m['result'].sum())
    matches = len(all_m)
    win_rate = wins / matches if matches > 0 else 0.5

    return {
        'first_in': first_in_pct,
        'first_won': first_won_pct,
        'second_won': second_won_pct,
        'bp_save': bp_save_pct,
        'ret_first_won': ret_first_won,
        'ret_second_won': ret_second_won,
        'bp_convert': bp_convert_pct,
        'win_rate': win_rate,
        'matches': matches
    }

print("Loading data...")
dfs = []
for url in [url_2022, url_2023, url_2024, url_2025, url_2026]:
    print("Loading " + url.split('/')[-1] + "...")
    dfs.append(load_match_data(url))
df = pd.concat(dfs, ignore_index=True)
print("Loaded " + str(len(df)) + " matches")

print("Calculating Elo...")
get_surface_elo, elo_overall = calculate_elo(df)

print("Loading rankings...")
rankings = load_rankings()
player_list = rankings['full_name'].tolist()

print("Building player profiles...")
player_profiles = {}
for name in player_list:
    profiles = {}
    for surface in ['Clay', 'Hard', 'Grass']:
        stats = get_player_stats(name, df, surface)
        if stats:
            profiles[surface] = stats
            profiles[surface]['elo'] = get_surface_elo(name, surface)
    all_stats = get_player_stats(name, df, None)
    if all_stats:
        profiles['All'] = all_stats
        profiles['All']['elo'] = elo_overall.get(name, 1500)
    if profiles:
        player_profiles[name] = profiles

print("Built profiles for " + str(len(player_profiles)) + " players")

js_profiles = 'const playerProfiles = ' + json.dumps(player_profiles) + ';\n'
js_players = 'const playerList = ' + json.dumps(player_list) + ';\n'

html_head = '''<!DOCTYPE html>
<html>
<head>
<title>The Gain Line - Match Simulator</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #0a0a0a; color: #fff; }
.header { background: #111; border-bottom: 2px solid #222; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 22px; font-weight: bold; }
.logo span { color: #4CAF50; }
.nav-tabs { display: flex; gap: 5px; }
.nav-tab { padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 13px; background: #1a1a1a; color: #888; border: 1px solid #333; }
.nav-tab.active { background: #4CAF50; color: #fff; border-color: #4CAF50; }
.container { padding: 30px; max-width: 1000px; margin: 0 auto; }
.sim-title { font-size: 22px; font-weight: bold; margin-bottom: 6px; }
.sim-subtitle { font-size: 13px; color: #666; margin-bottom: 25px; }
.matchup-box { display: flex; gap: 20px; align-items: flex-end; flex-wrap: wrap; margin-bottom: 20px; }
.player-box { flex: 1; min-width: 200px; }
.player-box label { display: block; font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.search-wrap { position: relative; }
input[type=text] { width: 100%; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 5px; padding: 10px 14px; font-size: 14px; }
input[type=text]:focus { outline: none; border-color: #4CAF50; }
.sugg-box { background: #1a1a1a; border: 1px solid #444; border-radius: 5px; max-height: 200px; overflow-y: auto; position: absolute; width: 100%; z-index: 100; top: 100%; }
.sugg-item { padding: 9px 14px; cursor: pointer; font-size: 13px; border-bottom: 1px solid #222; }
.sugg-item:hover { background: #252525; color: #4CAF50; }
.vs-label { font-size: 24px; font-weight: bold; color: #444; padding-bottom: 10px; }
.surface-box { min-width: 140px; }
.surface-box label { display: block; font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
select { background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 5px; padding: 10px 14px; font-size: 14px; cursor: pointer; width: 100%; }
select:focus { outline: none; border-color: #4CAF50; }
.format-box { min-width: 140px; }
.sim-btn { background: #4CAF50; color: #fff; border: none; border-radius: 5px; padding: 12px 30px; font-size: 15px; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 25px; }
.sim-btn:hover { background: #45a045; }
.results { display: none; }
.prob-bar-container { background: #111; border-radius: 10px; padding: 25px; margin-bottom: 20px; }
.prob-players { display: flex; justify-content: space-between; margin-bottom: 15px; }
.prob-player { text-align: center; flex: 1; }
.prob-name { font-size: 16px; font-weight: bold; margin-bottom: 6px; }
.prob-pct { font-size: 48px; font-weight: bold; }
.prob-bar-wrap { height: 12px; background: #222; border-radius: 6px; overflow: hidden; margin-bottom: 20px; }
.prob-bar-fill { height: 100%; border-radius: 6px; transition: width 0.5s ease; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }
.stat-card { background: #111; border-radius: 8px; padding: 15px; }
.stat-card-title { font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
.stat-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 13px; }
.stat-label { color: #888; }
.stat-val { font-weight: bold; }
.stat-val.better { color: #4CAF50; }
.stat-val.worse { color: #cc4444; }
.score-dist { background: #111; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
.score-dist-title { font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
.score-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.score-label { font-size: 13px; color: #aaa; min-width: 80px; }
.score-bar-wrap { flex: 1; height: 8px; background: #222; border-radius: 4px; overflow: hidden; margin: 0 10px; }
.score-bar-fill { height: 100%; border-radius: 4px; }
.score-pct { font-size: 12px; color: #888; min-width: 40px; text-align: right; }
.elo-section { background: #111; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
.elo-title { font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
.elo-row { display: flex; justify-content: space-around; text-align: center; }
.elo-item { text-align: center; }
.elo-label { font-size: 11px; color: #666; margin-bottom: 4px; }
.elo-val { font-size: 22px; font-weight: bold; }
.sim-info { font-size: 11px; color: #444; text-align: center; margin-top: 15px; }
.warning { background: #1a1a00; border: 1px solid #444400; border-radius: 6px; padding: 10px 15px; font-size: 12px; color: #888800; margin-bottom: 15px; }
</style>
</head>
<body>
<div class="header">
  <div class="logo">THE <span>GAIN</span> LINE</div>
  <div class="nav-tabs">
    <div class="nav-tab" onclick="location.href='prop_matrix.html'">Super Rugby Pacific</div>
    <div class="nav-tab" onclick="location.href='epl_matrix.html'">EPL Soccer</div>
    <div class="nav-tab" onclick="location.href='tennis_matrix.html'">ATP Tennis</div>
    <div class="nav-tab" onclick="location.href='wta_matrix.html'">WTA Tennis</div>
    <div class="nav-tab active">Match Simulator</div>
  </div>
</div>
<div class="container">
  <div class="sim-title">Match Simulator</div>
  <div class="sim-subtitle">Monte Carlo simulation — 10,000 matches run per query using serve, return, break point and Elo data</div>

  <div class="matchup-box">
    <div class="player-box">
      <label>Player 1</label>
      <div class="search-wrap" id="wrap1">
        <input type="text" id="p1input" placeholder="Type player name..." autocomplete="off">
        <div class="sugg-box" id="sugg1" style="display:none"></div>
      </div>
    </div>
    <div class="vs-label">VS</div>
    <div class="player-box">
      <label>Player 2</label>
      <div class="search-wrap" id="wrap2">
        <input type="text" id="p2input" placeholder="Type player name..." autocomplete="off">
        <div class="sugg-box" id="sugg2" style="display:none"></div>
      </div>
    </div>
    <div class="surface-box">
      <label>Surface</label>
      <select id="surfaceSelect">
        <option value="Clay">Clay</option>
        <option value="Hard">Hard</option>
        <option value="Grass">Grass</option>
      </select>
    </div>
    <div class="format-box">
      <label>Format</label>
      <select id="formatSelect">
        <option value="bo3">Best of 3</option>
        <option value="bo5">Best of 5</option>
      </select>
    </div>
  </div>

  <button class="sim-btn" onclick="runSimulation()">RUN 10,000 SIMULATIONS</button>

  <div class="results" id="results"></div>
</div>
'''

html_script = '''
<script>
''' + js_players + js_profiles + '''

var sel1 = '', sel2 = '';

document.getElementById('p1input').addEventListener('input', function() { showSugg(this.value, 'sugg1', 1); });
document.getElementById('p2input').addEventListener('input', function() { showSugg(this.value, 'sugg2', 2); });

function showSugg(val, boxId, num) {
  var box = document.getElementById(boxId);
  if (val.length < 2) { box.style.display = 'none'; return; }
  var v = val.toLowerCase();
  var found = playerList.filter(p => p.toLowerCase().includes(v)).slice(0, 8);
  if (!found.length) { box.style.display = 'none'; return; }
  box.innerHTML = found.map(p => '<div class="sugg-item" onclick="pickPlayer(' + num + ',this.textContent)">' + p + '</div>').join('');
  box.style.display = 'block';
}

function pickPlayer(num, name) {
  if (num === 1) { sel1 = name; document.getElementById('p1input').value = name; document.getElementById('sugg1').style.display = 'none'; }
  else { sel2 = name; document.getElementById('p2input').value = name; document.getElementById('sugg2').style.display = 'none'; }
}

document.addEventListener('click', function(e) {
  if (!e.target.closest('#wrap1')) document.getElementById('sugg1').style.display = 'none';
  if (!e.target.closest('#wrap2')) document.getElementById('sugg2').style.display = 'none';
});

function getStats(name, surface) {
  var p = playerProfiles[name];
  if (!p) return null;
  return p[surface] || p['All'] || null;
}

function simPoint(serverStats, returnerStats) {
  var firstIn = serverStats.first_in;
  var firstWon = serverStats.first_won;
  var secondWon = serverStats.second_won;
  var retFirst = returnerStats.ret_first_won;
  var retSecond = returnerStats.ret_second_won;

  var adjFirstWon = (firstWon + (1 - retFirst)) / 2;
  var adjSecondWon = (secondWon + (1 - retSecond)) / 2;

  if (Math.random() < firstIn) {
    return Math.random() < adjFirstWon;
  } else {
    return Math.random() < adjSecondWon;
  }
}

function simGame(serverStats, returnerStats, isBP) {
  var pts = [0, 0];
  while (true) {
    if (simPoint(serverStats, returnerStats)) pts[0]++;
    else pts[1]++;
    if (pts[0] >= 4 && pts[0] - pts[1] >= 2) return true;
    if (pts[1] >= 4 && pts[1] - pts[0] >= 2) return false;
    if (pts[0] === 3 && pts[1] === 3) { pts = [3, 3]; }
  }
}

function simTiebreak(p1Stats, p2Stats) {
  var pts = [0, 0];
  var server = 0;
  var pointCount = 0;
  while (true) {
    var serverStats = server === 0 ? p1Stats : p2Stats;
    var returnerStats = server === 0 ? p2Stats : p1Stats;
    if (simPoint(serverStats, returnerStats)) pts[server]++;
    else pts[1-server]++;
    pointCount++;
    if (pointCount === 1 || (pointCount > 1 && pointCount % 2 === 1)) server = 1 - server;
    if (pts[0] >= 7 && pts[0] - pts[1] >= 2) return true;
    if (pts[1] >= 7 && pts[1] - pts[0] >= 2) return false;
  }
}

function simSet(p1Stats, p2Stats, isFinalSet, bo5) {
  var games = [0, 0];
  var server = 0;
  while (true) {
    var serverStats = server === 0 ? p1Stats : p2Stats;
    var returnerStats = server === 0 ? p2Stats : p1Stats;
    if (simGame(serverStats, returnerStats)) games[server]++;
    else games[1-server]++;
    server = 1 - server;
    if (games[0] >= 6 && games[0] - games[1] >= 2) return [true, games[0] + '-' + games[1]];
    if (games[1] >= 6 && games[1] - games[0] >= 2) return [false, games[0] + '-' + games[1]];
    if (games[0] === 6 && games[1] === 6) {
      if (isFinalSet && bo5) {
        while (true) {
          var ss = server === 0 ? p1Stats : p2Stats;
          var rs = server === 0 ? p2Stats : p1Stats;
          if (simGame(ss, rs)) games[server]++;
          else games[1-server]++;
          server = 1 - server;
          if (games[0] - games[1] >= 2) return [true, games[0] + '-' + games[1]];
          if (games[1] - games[0] >= 2) return [false, games[0] + '-' + games[1]];
        }
      }
      var tbWin = simTiebreak(p1Stats, p2Stats);
      if (tbWin) return [true, '7-6'];
      else return [false, '6-7'];
    }
  }
}

function applyEloAdjustment(p1Stats, p2Stats) {
  var e1 = p1Stats.elo || 1500;
  var e2 = p2Stats.elo || 1500;
  var diff = e1 - e2;
  var adj = diff * 0.0003;
  var p1adj = JSON.parse(JSON.stringify(p1Stats));
  var p2adj = JSON.parse(JSON.stringify(p2Stats));
  p1adj.first_won = Math.min(0.95, Math.max(0.4, p1Stats.first_won + adj));
  p1adj.second_won = Math.min(0.90, Math.max(0.3, p1Stats.second_won + adj));
  p2adj.first_won = Math.min(0.95, Math.max(0.4, p2Stats.first_won - adj));
  p2adj.second_won = Math.min(0.90, Math.max(0.3, p2Stats.second_won - adj));
  return [p1adj, p2adj];
}

function simMatch(p1Stats, p2Stats, bo5) {
  var adjusted = applyEloAdjustment(p1Stats, p2Stats);
  var p1s = adjusted[0];
  var p2s = adjusted[1];
  var sets = [0, 0];
  var setScores = [];
  var setsNeeded = bo5 ? 3 : 2;
  while (sets[0] < setsNeeded && sets[1] < setsNeeded) {
    var isFinal = (sets[0] === setsNeeded-1 || sets[1] === setsNeeded-1);
    var result = simSet(p1s, p2s, isFinal && bo5, bo5);
    if (result[0]) { sets[0]++; setScores.push(result[1]); }
    else { sets[1]++; setScores.push(result[1]); }
  }
  return { p1wins: sets[0] > sets[1], sets: sets, scores: setScores };
}

function runSimulation() {
  var p1 = sel1 || document.getElementById('p1input').value.trim();
  var p2 = sel2 || document.getElementById('p2input').value.trim();
  var surface = document.getElementById('surfaceSelect').value;
  var format = document.getElementById('formatSelect').value;
  var bo5 = format === 'bo5';

  if (!p1 || !p2) {
    alert('Please select both players');
    return;
  }

  var p1Stats = getStats(p1, surface);
  var p2Stats = getStats(p2, surface);

  if (!p1Stats || !p2Stats) {
    document.getElementById('results').style.display = 'block';
    document.getElementById('results').innerHTML = '<div class="warning">Not enough data for one or both players on this surface. Try All Surfaces.</div>';
    return;
  }

  var N = 10000;
  var p1wins = 0;
  var scoreDist = {};

  for (var i = 0; i < N; i++) {
    var result = simMatch(p1Stats, p2Stats, bo5);
    if (result.p1wins) p1wins++;
    var scoreKey = result.sets[0] + '-' + result.sets[1];
    scoreDist[scoreKey] = (scoreDist[scoreKey] || 0) + 1;
  }

  var p1pct = Math.round(p1wins / N * 100);
  var p2pct = 100 - p1pct;

  var sortedScores = Object.entries(scoreDist).sort((a,b) => b[1]-a[1]);

  function fmtPct(v) { return (v * 100).toFixed(1) + '%'; }
  function cmp(a, b, higher) { return a > b ? (higher ? 'better' : 'worse') : (higher ? 'worse' : 'better'); }

  var e1 = p1Stats.elo || 1500;
  var e2 = p2Stats.elo || 1500;

  var hasWarning = (p1Stats.matches < 15 || p2Stats.matches < 15) ?
    '<div class="warning">⚠ Limited data for one or both players on ' + surface + ' — results may be less accurate</div>' : '';

  var scoreHTML = sortedScores.slice(0, 6).map(function(s) {
    var pct = Math.round(s[1] / N * 100);
    var parts = s[0].split('-');
    var winner = parseInt(parts[0]) > parseInt(parts[1]) ? p1 : p2;
    var color = winner === p1 ? '#4CAF50' : '#4488ff';
    return '<div class="score-row">' +
      '<span class="score-label">' + winner.split(' ').pop() + ' ' + s[0] + '</span>' +
      '<div class="score-bar-wrap"><div class="score-bar-fill" style="width:' + pct + '%;background:' + color + '"></div></div>' +
      '<span class="score-pct">' + pct + '%</span>' +
    '</div>';
  }).join('');

  document.getElementById('results').style.display = 'block';
  document.getElementById('results').innerHTML =
    hasWarning +
    '<div class="prob-bar-container">' +
      '<div class="prob-players">' +
        '<div class="prob-player"><div class="prob-name">' + p1 + '</div><div class="prob-pct" style="color:#4CAF50">' + p1pct + '%</div></div>' +
        '<div style="text-align:center;padding-top:20px;color:#444;font-size:18px">win probability</div>' +
        '<div class="prob-player"><div class="prob-name">' + p2 + '</div><div class="prob-pct" style="color:#4488ff">' + p2pct + '%</div></div>' +
      '</div>' +
      '<div class="prob-bar-wrap"><div class="prob-bar-fill" style="width:' + p1pct + '%;background:linear-gradient(to right,#4CAF50,#45a045)"></div></div>' +
    '</div>' +
    '<div class="elo-section">' +
      '<div class="elo-title">Elo Ratings — ' + surface + '</div>' +
      '<div class="elo-row">' +
        '<div class="elo-item"><div class="elo-label">' + p1 + '</div><div class="elo-val" style="color:#4CAF50">' + e1 + '</div></div>' +
        '<div class="elo-item"><div class="elo-label">Surface</div><div class="elo-val" style="color:#888">' + surface + '</div></div>' +
        '<div class="elo-item"><div class="elo-label">' + p2 + '</div><div class="elo-val" style="color:#4488ff">' + e2 + '</div></div>' +
      '</div>' +
    '</div>' +
    '<div class="stats-grid">' +
      '<div class="stat-card"><div class="stat-card-title">Serve Stats — ' + surface + '</div>' +
        '<div class="stat-row"><span class="stat-label">1st Serve In</span><span class="stat-val ' + cmp(p1Stats.first_in, p2Stats.first_in, true) + '">' + fmtPct(p1Stats.first_in) + '</span><span class="stat-val ' + cmp(p2Stats.first_in, p1Stats.first_in, true) + '">' + fmtPct(p2Stats.first_in) + '</span></div>' +
        '<div class="stat-row"><span class="stat-label">1st Serve Win</span><span class="stat-val ' + cmp(p1Stats.first_won, p2Stats.first_won, true) + '">' + fmtPct(p1Stats.first_won) + '</span><span class="stat-val ' + cmp(p2Stats.first_won, p1Stats.first_won, true) + '">' + fmtPct(p2Stats.first_won) + '</span></div>' +
        '<div class="stat-row"><span class="stat-label">2nd Serve Win</span><span class="stat-val ' + cmp(p1Stats.second_won, p2Stats.second_won, true) + '">' + fmtPct(p1Stats.second_won) + '</span><span class="stat-val ' + cmp(p2Stats.second_won, p1Stats.second_won, true) + '">' + fmtPct(p2Stats.second_won) + '</span></div>' +
        '<div class="stat-row"><span class="stat-label">BP Save</span><span class="stat-val ' + cmp(p1Stats.bp_save, p2Stats.bp_save, true) + '">' + fmtPct(p1Stats.bp_save) + '</span><span class="stat-val ' + cmp(p2Stats.bp_save, p1Stats.bp_save, true) + '">' + fmtPct(p2Stats.bp_save) + '</span></div>' +
      '</div>' +
      '<div class="stat-card"><div class="stat-card-title">Return Stats — ' + surface + '</div>' +
        '<div class="stat-row"><span class="stat-label">Ret 1st Serve</span><span class="stat-val ' + cmp(p1Stats.ret_first_won, p2Stats.ret_first_won, true) + '">' + fmtPct(p1Stats.ret_first_won) + '</span><span class="stat-val ' + cmp(p2Stats.ret_first_won, p1Stats.ret_first_won, true) + '">' + fmtPct(p2Stats.ret_first_won) + '</span></div>' +
        '<div class="stat-row"><span class="stat-label">Ret 2nd Serve</span><span class="stat-val ' + cmp(p1Stats.ret_second_won, p2Stats.ret_second_won, true) + '">' + fmtPct(p1Stats.ret_second_won) + '</span><span class="stat-val ' + cmp(p2Stats.ret_second_won, p1Stats.ret_second_won, true) + '">' + fmtPct(p2Stats.ret_second_won) + '</span></div>' +
        '<div class="stat-row"><span class="stat-label">BP Convert</span><span class="stat-val ' + cmp(p1Stats.bp_convert, p2Stats.bp_convert, true) + '">' + fmtPct(p1Stats.bp_convert) + '</span><span class="stat-val ' + cmp(p2Stats.bp_convert, p1Stats.bp_convert, true) + '">' + fmtPct(p2Stats.bp_convert) + '</span></div>' +
        '<div class="stat-row"><span class="stat-label">Win Rate</span><span class="stat-val ' + cmp(p1Stats.win_rate, p2Stats.win_rate, true) + '">' + fmtPct(p1Stats.win_rate) + '</span><span class="stat-val ' + cmp(p2Stats.win_rate, p1Stats.win_rate, true) + '">' + fmtPct(p2Stats.win_rate) + '</span></div>' +
      '</div>' +
    '</div>' +
    '<div class="score-dist"><div class="score-dist-title">Score Distribution</div>' + scoreHTML + '</div>' +
    '<div class="sim-info">Based on 10,000 Monte Carlo simulations using serve, return, break point and Elo data from 2022-2026 | Not financial advice</div>';
}
</script>
</body>
</html>'''

html = html_head + html_script

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'match_simulator.html')
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)

print("\nMatch Simulator generated! Opening in browser...")
webbrowser.open('file:///' + filepath)