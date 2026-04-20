import soccerdata as sd
import pandas as pd
import requests
import webbrowser
import os
import json

API_KEY = 'a3fd838c65e47cfdce22a13933f01a75'

print("Connecting to FBref for EPL data...")

def get_epl_odds():
    try:
        url = 'https://api.the-odds-api.com/v4/sports/soccer_epl/odds/'
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'h2h',
            'oddsFormat': 'american'
        }
        r = requests.get(url, params=params)
        matches = r.json()
        odds_dict = {}
        for match in matches:
            home = match['home_team']
            away = match['away_team']
            for bm in match['bookmakers']:
                if bm['key'] == 'draftkings':
                    for market in bm['markets']:
                        if market['key'] == 'h2h':
                            for outcome in market['outcomes']:
                                odds_dict[outcome['name']] = outcome['price']
        return odds_dict
    except:
        return {}

try:
    fbref = sd.FBref(leagues="ENG-Premier League", seasons="2425")
    stats = fbref.read_player_season_stats(stat_type="standard")
    stats = stats.reset_index()
    stats.columns = ['_'.join(col).strip('_') for col in stats.columns]

    # Filter outfield players with at least 5 appearances
    outfield = stats[
        (stats['pos'] != 'GK') &
        (stats['Playing Time_MP'] >= 5)
    ].copy()

    # Sort by goals per 90
    outfield = outfield.sort_values('Per 90 Minutes_Gls', ascending=False)

    print("Top 30 EPL goal scorers loaded")
    print("Fetching match odds...")
    team_odds = get_epl_odds()

    # Build player rows for top scorers
    top_players = outfield

    # Build JavaScript data
    js_players = []
    for _, row in top_players.iterrows():
        goals = int(row['Performance_Gls']) if not pd.isna(row['Performance_Gls']) else 0
        assists = int(row['Performance_Ast']) if not pd.isna(row['Performance_Ast']) else 0
        matches = int(row['Playing Time_MP']) if not pd.isna(row['Playing Time_MP']) else 0
        gls_per90 = round(float(row['Per 90 Minutes_Gls']), 2) if not pd.isna(row['Per 90 Minutes_Gls']) else 0
        ast_per90 = round(float(row['Per 90 Minutes_Ast']), 2) if not pd.isna(row['Per 90 Minutes_Ast']) else 0
        ga_per90 = round(float(row['Per 90 Minutes_G+A']), 2) if not pd.isna(row['Per 90 Minutes_G+A']) else 0
        team = str(row['team'])
        player = str(row['player'])
        pos = str(row['pos'])

        # Get team odds if available
        team_line = team_odds.get(team, None)
        odds_str = ('+' + str(team_line) if team_line and team_line > 0 else str(team_line)) if team_line else 'N/A'

        js_players.append({
            'name': player,
            'team': team,
            'pos': pos,
            'matches': matches,
            'goals': goals,
            'assists': assists,
            'glsPer90': gls_per90,
            'astPer90': ast_per90,
            'gaPer90': ga_per90,
            'teamOdds': odds_str
        })

    js_data = 'const soccerData = ' + json.dumps(js_players) + ';\n'

    # Team colors for EPL
    team_colors = {
        'Arsenal': '#EF0107',
        'Chelsea': '#034694',
        'Liverpool': '#C8102E',
        'Manchester City': '#6CABDD',
        'Manchester Utd': '#DA291C',
        'Tottenham': '#132257',
        'Newcastle Utd': '#241F20',
        'Aston Villa': '#95BFE5',
        'West Ham': '#7A263A',
        'Brighton': '#0057B8',
        'Brentford': '#e30613',
        'Fulham': '#CC0000',
        'Crystal Palace': '#1B458F',
        'Wolves': '#FDB913',
        'Everton': '#003399',
        'Leicester City': '#003090',
        'Nottm Forest': '#E53233',
        'Bournemouth': '#DA291C',
        'Ipswich Town': '#0044A9',
        'Southampton': '#D71920',
        'Sunderland': '#EB172B',
    }

    colors_js = 'const teamColors = ' + json.dumps(team_colors) + ';\n'

    html = '''<!DOCTYPE html>
<html>
<head>
<title>The Gain Line — EPL Soccer</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #0a0a0a; color: #ffffff; }
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
.container { padding: 20px; max-width: 1400px; margin: 0 auto; }
.matrix-title { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
.matrix-subtitle { font-size: 12px; color: #666; margin-bottom: 15px; }
table { width: 100%; border-collapse: collapse; }
th { background: #1a1a1a; padding: 10px 12px; text-align: center; font-size: 11px; color: #888; letter-spacing: 1px; border-bottom: 2px solid #333; text-transform: uppercase; }
th.left { text-align: left; }
td { padding: 10px 12px; text-align: center; border-bottom: 1px solid #151515; font-size: 14px; }
.player-name { text-align: left; font-weight: bold; font-size: 14px; }
.team-badge { font-size: 10px; font-weight: bold; padding: 3px 8px; border-radius: 3px; white-space: nowrap; display: inline-block; }
.stat-cell { font-weight: bold; font-size: 16px; border-radius: 4px; padding: 6px 10px; display: inline-block; min-width: 50px; }
.odds-cell { font-size: 13px; color: #4CAF50; font-weight: bold; }
tr:hover { background: #111; }
.pos-badge { font-size: 10px; padding: 2px 6px; border-radius: 3px; background: #222; color: #888; }
.count-badge { background: #333; color: #888; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; }
.footer { text-align: center; color: #333; font-size: 11px; padding: 20px; border-top: 1px solid #111; margin-top: 20px; }
.legend { display: flex; gap: 20px; justify-content: center; margin: 15px 0; font-size: 12px; color: #888; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-box { width: 12px; height: 12px; border-radius: 2px; }
</style>
</head>
<body>

<div class="header">
  <div class="logo">THE <span>GAIN</span> LINE</div>
  <div class="nav-tabs">
    <div class="nav-tab">Super Rugby Pacific</div>
    <div class="nav-tab active">EPL Soccer</div>
    <div class="nav-tab">Tennis</div>
  </div>
</div>

<div class="controls">
  <div class="control-group">
    <span class="control-label">Team</span>
    <select id="teamFilter" onchange="renderTable()">
      <option value="all">All Teams</option>
    </select>
  </div>
  <div class="control-group">
    <span class="control-label">Position</span>
    <select id="posFilter" onchange="renderTable()">
      <option value="all">All Positions</option>
      <option value="FW">Forwards</option>
      <option value="MF">Midfielders</option>
      <option value="DF">Defenders</option>
    </select>
  </div>
  <div class="control-group">
    <span class="control-label">Sort By</span>
    <select id="sortBy" onchange="renderTable()">
      <option value="goals">Total Goals</option>
      <option value="per90">Goals Per 90</option>
      <option value="ga">Goals + Assists</option>
      <option value="team">Team</option>
    </select>
  </div>
  <div class="control-group search-box">
    <span class="control-label">Search Player</span>
    <input type="text" id="searchBox" placeholder="Search player name..." oninput="renderTable()">
  </div>
</div>

<div class="container">
  <div class="matrix-title">EPL Goal Scorer Matrix <span class="count-badge" id="playerCount"></span></div>
  <div class="matrix-subtitle">2024/25 Season stats from FBref | Live match odds from DraftKings | Updated Daily</div>

  <div class="legend">
    <div class="legend-item"><div class="legend-box" style="background:#1a7a1a"></div>0.5+ goals per 90</div>
    <div class="legend-item"><div class="legend-box" style="background:#7a6a00"></div>0.3-0.49 per 90</div>
    <div class="legend-item"><div class="legend-box" style="background:#7a1a1a"></div>Under 0.3 per 90</div>
  </div>

  <table>
    <thead>
      <tr>
        <th class="left">PLAYER</th>
        <th>TEAM</th>
        <th>POS</th>
        <th>MATCHES</th>
        <th>TOTAL GOALS</th>
        <th>TOTAL ASSISTS</th>
        <th>GOALS PER 90</th>
        <th>ASSISTS PER 90</th>
        <th>G+A PER 90</th>
        <th>TEAM ODDS (DK)</th>
      </tr>
    </thead>
    <tbody id="tableBody"></tbody>
  </table>

  <div class="footer">The Gain Line | EPL Soccer | FBref Data | DraftKings Odds | Built for the American soccer bettor</div>
</div>

<script>
''' + js_data + colors_js + '''

function getColor(per90) {
  if (per90 >= 0.5) return '#1a7a1a';
  if (per90 >= 0.3) return '#7a6a00';
  return '#7a1a1a';
}

function populateFilters() {
  const teams = [...new Set(soccerData.map(p => p.team))].sort();
  const select = document.getElementById('teamFilter');
  teams.forEach(team => {
    const opt = document.createElement('option');
    opt.value = team;
    opt.textContent = team;
    select.appendChild(opt);
  });
}

function renderTable() {
  const teamFilter = document.getElementById('teamFilter').value;
  const posFilter = document.getElementById('posFilter').value;
  const sortBy = document.getElementById('sortBy').value;
  const search = document.getElementById('searchBox').value.toLowerCase();

  let filtered = soccerData.filter(p => {
    if (teamFilter !== 'all' && p.team !== teamFilter) return false;
    if (posFilter !== 'all' && !p.pos.includes(posFilter)) return false;
    if (search && !p.name.toLowerCase().includes(search)) return false;
    return true;
  });

  if (sortBy === 'goals') filtered.sort((a, b) => b.goals - a.goals);
  else if (sortBy === 'per90') filtered.sort((a, b) => b.glsPer90 - a.glsPer90);
  else if (sortBy === 'ga') filtered.sort((a, b) => b.gaPer90 - a.gaPer90);
  else filtered.sort((a, b) => a.team.localeCompare(b.team) || b.goals - a.goals);

  document.getElementById('playerCount').textContent = filtered.length + ' players';

  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';

  filtered.forEach(p => {
    const color = getColor(p.glsPer90);
    const teamColor = teamColors[p.team] || '#333';
    const row = document.createElement('tr');
    row.innerHTML =
      '<td class="player-name">' + p.name + '</td>' +
      '<td><span class="team-badge" style="background:' + teamColor + '">' + p.team + '</span></td>' +
      '<td><span class="pos-badge">' + p.pos + '</span></td>' +
      '<td>' + p.matches + '</td>' +
      '<td><span class="stat-cell" style="background:' + color + '">' + p.goals + '</span></td>' +
      '<td>' + p.assists + '</td>' +
      '<td><span class="stat-cell" style="background:' + color + '">' + p.glsPer90 + '</span></td>' +
      '<td>' + p.astPer90 + '</td>' +
      '<td>' + p.gaPer90 + '</td>' +
      '<td class="odds-cell">' + p.teamOdds + '</td>';
    tbody.appendChild(row);
  });
}

populateFilters();
renderTable();
</script>
</body>
</html>'''

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'epl_matrix.html')
    with open(filepath, 'w') as f:
        f.write(html)

    print("EPL Matrix generated! Opening in browser...")
    webbrowser.open('file:///' + filepath)

except Exception as e:
    print("Error: " + str(e))
    import traceback
    traceback.print_exc()