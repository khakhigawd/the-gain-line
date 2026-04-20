from rugbypy.player import *
import pandas as pd
import webbrowser
import os
import time

PLAYERS = [
    {'id': '5181c94c', 'name': 'Sevu Reece', 'team': 'Crusaders'},
    {'id': '4bb2a971', 'name': 'Leicester Faingaanuku', 'team': 'Crusaders'},
    {'id': '8cf8cdd3', 'name': 'Will Jordan', 'team': 'Crusaders'},
    {'id': 'ebe2fb3f', 'name': 'Macca Springer', 'team': 'Crusaders'},
    {'id': 'a0a316de', 'name': 'Wes Goosen', 'team': 'Hurricanes'},
    {'id': '95bfb363', 'name': 'Joshua Moorby', 'team': 'Hurricanes'},
    {'id': 'b72e9e7c', 'name': 'Salesi Rayasi', 'team': 'Hurricanes'},
    {'id': '67661a18', 'name': 'Ardie Savea', 'team': 'Hurricanes'},
    {'id': 'e7a7d9bd', 'name': 'Caleb Clarke', 'team': 'Blues'},
    {'id': '012b0dd1', 'name': 'Mark Telea', 'team': 'Blues'},
    {'id': '47bc6611', 'name': 'Hoskins Sotutu', 'team': 'Blues'},
    {'id': 'bf368581', 'name': 'Rieko Ioane', 'team': 'Blues'},
    {'id': '369b6d45', 'name': 'Corey Toole', 'team': 'Brumbies'},
    {'id': '257b3e51', 'name': 'Charlie Cale', 'team': 'Brumbies'},
    {'id': '8831a08a', 'name': 'Tom Wright', 'team': 'Brumbies'},
    {'id': 'ca3d8ac3', 'name': 'Jacob Ratumaitavuki', 'team': 'Highlanders'},
    {'id': '662cb4d7', 'name': 'Jonah Lowe', 'team': 'Highlanders'},
    {'id': '2c5a0566', 'name': 'Jona Nareki', 'team': 'Highlanders'},
    {'id': '7e93e195', 'name': 'Tim Ryan', 'team': 'Reds'},
    {'id': '7a64da48', 'name': 'Josh Flook', 'team': 'Reds'},
    {'id': '1d77d514', 'name': 'Lachie Anderson', 'team': 'Reds'},
    {'id': '55bd884d', 'name': 'Mark Nawaqanitawase', 'team': 'Waratahs'},
    {'id': '843673f2', 'name': 'Folau Fainga\'a', 'team': 'Waratahs'},
    {'id': '5364ab74', 'name': 'Zach Kibirige', 'team': 'Western Force'},
    {'id': 'e3cfdc94', 'name': 'Carlo Tizzano', 'team': 'Western Force'},
    {'id': '3f1466db', 'name': 'Iosefo Masi', 'team': 'Fijian Drua'},
    {'id': '7cec07ed', 'name': 'Taniela Rakuro', 'team': 'Fijian Drua'},
    {'id': 'e44732cf', 'name': 'Miracle Faiilagi', 'team': 'Moana Pasifika'},
    {'id': '275e39aa', 'name': 'Fine Inisi', 'team': 'Moana Pasifika'},
]

TEAM_COLORS = {
    'Crusaders': '#E31937',
    'Hurricanes': '#003087',
    'Blues': '#0047AB',
    'Brumbies': '#00305E',
    'Highlanders': '#003087',
    'Reds': '#C8102E',
    'Waratahs': '#00205B',
    'Western Force': '#002147',
    'Fijian Drua': '#00843D',
    'Moana Pasifika': '#003F87',
}

def get_super_rugby_stats(player_id):
    stats = fetch_player_stats(player_id=player_id)
    super_rugby = stats[stats['competition'].str.contains('Super', case=False, na=False)]
    return super_rugby

def build_player_data(player):
    print("Fetching " + player['name'] + "...")
    try:
        all_data = get_super_rugby_stats(player['id'])
        if len(all_data) == 0:
            return None

        total_games = len(all_data)
        total_tries = all_data['tries'].sum()
        career_rate = round(float(total_tries) / total_games, 2) if total_games > 0 else 0

        def get_stats_for_n_games(n):
            data = all_data.tail(n) if n > 0 else all_data
            h1 = int(len(data[data['tries'] >= 1]))
            h2 = int(len(data[data['tries'] >= 2]))
            t = len(data)
            avg_metres = round(float(data['metres_carried'].mean()), 1) if not data['metres_carried'].isna().all() else 0
            avg_def = round(float(data['defenders_beaten'].mean()), 1) if not data['defenders_beaten'].isna().all() else 0
            return {
                'h1': h1, 'h2': h2, 't': t,
                'avg_metres': avg_metres,
                'avg_def': avg_def
            }

        return {
            'name': player['name'],
            'team': player['team'],
            'total_games': total_games,
            'career_rate': career_rate,
            'last5': get_stats_for_n_games(5),
            'last10': get_stats_for_n_games(10),
            'last15': get_stats_for_n_games(15),
            'season': get_stats_for_n_games(0),
        }
    except Exception as e:
        print("  Skipped: " + str(e))
        return None

def generate_matrix():
    print("\nBuilding Interactive Super Rugby Pacific Matrix...\n")

    all_player_data = []
    for player in PLAYERS:
        data = build_player_data(player)
        if data:
            all_player_data.append(data)
        time.sleep(1)

    # Build JavaScript data array
    js_data = "const playerData = [\n"
    for p in all_player_data:
        team_color = TEAM_COLORS.get(p['team'], '#333333')
        js_data += "  {\n"
        js_data += '    name: "' + p['name'] + '",\n'
        js_data += '    team: "' + p['team'] + '",\n'
        js_data += '    teamColor: "' + team_color + '",\n'
        js_data += '    careerRate: ' + str(p['career_rate']) + ',\n'
        js_data += '    totalGames: ' + str(p['total_games']) + ',\n'
        for key in ['last5', 'last10', 'last15', 'season']:
            s = p[key]
            js_data += '    ' + key + ': {h1:' + str(s['h1']) + ',h2:' + str(s['h2']) + ',t:' + str(s['t']) + ',avgMetres:' + str(s['avg_metres']) + ',avgDef:' + str(s['avg_def']) + '},\n'
        js_data += "  },\n"
    js_data += "];\n"

    html = '''<!DOCTYPE html>
<html>
<head>
<title>The Gain Line — Super Rugby Pacific</title>
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
th { background: #1a1a1a; padding: 10px 12px; text-align: center; font-size: 11px; color: #888; letter-spacing: 1px; border-bottom: 2px solid #333; text-transform: uppercase; position: sticky; top: 0; z-index: 10; }
th.left { text-align: left; }
td { padding: 10px 12px; text-align: center; border-bottom: 1px solid #151515; font-size: 14px; }
.player-name { text-align: left; font-weight: bold; font-size: 14px; }
.team-badge { font-size: 10px; font-weight: bold; padding: 3px 8px; border-radius: 3px; white-space: nowrap; display: inline-block; }
.matrix-cell { font-weight: bold; font-size: 16px; border-radius: 4px; padding: 8px 12px; display: inline-block; min-width: 55px; }
.career-cell { font-weight: bold; font-size: 15px; border-radius: 4px; padding: 6px 10px; display: inline-block; min-width: 50px; }
tr:hover { background: #111; }
.section-header td { background: #0f0f0f; color: #fff; font-weight: bold; font-size: 12px; letter-spacing: 2px; padding: 8px 12px; border-top: 2px solid #333; text-transform: uppercase; }
.stats-small { font-size: 11px; color: #666; display: block; }
.legend { display: flex; gap: 20px; justify-content: center; margin: 15px 0; font-size: 12px; color: #888; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-box { width: 12px; height: 12px; border-radius: 2px; }
.footer { text-align: center; color: #333; font-size: 11px; padding: 20px; border-top: 1px solid #111; margin-top: 20px; }
.count-badge { background: #333; color: #888; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; }
</style>
</head>
<body>

<div class="header">
  <div class="logo">THE <span>GAIN</span> LINE</div>
  <div class="nav-tabs">
    <div class="nav-tab active">Super Rugby Pacific</div>
    <div class="nav-tab">EPL Soccer</div>
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
    <span class="control-label">Game Count</span>
    <select id="gameCount" onchange="renderTable()">
      <option value="last5">Last 5 Games</option>
      <option value="last10">Last 10 Games</option>
      <option value="last15">Last 15 Games</option>
      <option value="season">Full Season</option>
    </select>
  </div>
  <div class="control-group">
    <span class="control-label">Sort By</span>
    <select id="sortBy" onchange="renderTable()">
      <option value="team">Team</option>
      <option value="career">Career Rate</option>
      <option value="recent">Recent Form</option>
      <option value="metres">Avg Metres</option>
    </select>
  </div>
  <div class="control-group search-box">
    <span class="control-label">Search Player</span>
    <input type="text" id="searchBox" placeholder="Search player name..." oninput="renderTable()">
  </div>
</div>

<div class="container">
  <div class="matrix-title">Try Scorer Matrix <span class="count-badge" id="playerCount"></span></div>
  <div class="matrix-subtitle">Player try scoring performance | Color coded by hit rate | Updated Daily</div>

  <div class="legend">
    <div class="legend-item"><div class="legend-box" style="background:#1a7a1a"></div>60%+ hit rate</div>
    <div class="legend-item"><div class="legend-box" style="background:#7a6a00"></div>40-59% hit rate</div>
    <div class="legend-item"><div class="legend-box" style="background:#7a1a1a"></div>Under 40% hit rate</div>
  </div>

  <table>
    <thead>
      <tr>
        <th class="left">PLAYER</th>
        <th>TEAM</th>
        <th>AVG METRES</th>
        <th>AVG DEF BEATEN</th>
        <th>ANYTIME TRY (1+)</th>
        <th>BRACE (2+)</th>
        <th>CAREER RATE</th>
      </tr>
    </thead>
    <tbody id="tableBody"></tbody>
  </table>

  <div class="footer">The Gain Line | Super Rugby Pacific | Data updated daily | Built for the American rugby bettor</div>
</div>

<script>
''' + js_data + '''

function getColor(hits, total) {
  if (total === 0) return '#333';
  const rate = hits / total;
  if (rate >= 0.6) return '#1a7a1a';
  if (rate >= 0.4) return '#7a6a00';
  return '#7a1a1a';
}

function getCareerColor(rate) {
  if (rate >= 0.5) return '#1a7a1a';
  if (rate >= 0.3) return '#7a6a00';
  return '#7a1a1a';
}

function populateTeamFilter() {
  const teams = [...new Set(playerData.map(p => p.team))].sort();
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
  const gameCount = document.getElementById('gameCount').value;
  const sortBy = document.getElementById('sortBy').value;
  const search = document.getElementById('searchBox').value.toLowerCase();

  let filtered = playerData.filter(p => {
    if (teamFilter !== 'all' && p.team !== teamFilter) return false;
    if (search && !p.name.toLowerCase().includes(search)) return false;
    return true;
  });

  if (sortBy === 'career') filtered.sort((a, b) => b.careerRate - a.careerRate);
  else if (sortBy === 'recent') filtered.sort((a, b) => (b[gameCount].h1/Math.max(b[gameCount].t,1)) - (a[gameCount].h1/Math.max(a[gameCount].t,1)));
  else if (sortBy === 'metres') filtered.sort((a, b) => b[gameCount].avgMetres - a[gameCount].avgMetres);
  else filtered.sort((a, b) => a.team.localeCompare(b.team) || a.name.localeCompare(b.name));

  document.getElementById('playerCount').textContent = filtered.length + ' players';

  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';

  let currentTeam = '';
  filtered.forEach(p => {
    const stats = p[gameCount];

    if (sortBy === 'team' && p.team !== currentTeam) {
      currentTeam = p.team;
      const headerRow = document.createElement('tr');
      headerRow.className = 'section-header';
      headerRow.innerHTML = '<td colspan="7">' + p.team.toUpperCase() + '</td>';
      tbody.appendChild(headerRow);
    }

    const c1 = getColor(stats.h1, stats.t);
    const c2 = getColor(stats.h2, stats.t);
    const cc = getCareerColor(p.careerRate);

    const row = document.createElement('tr');
    row.innerHTML =
      '<td class="player-name">' + p.name + '</td>' +
      '<td><span class="team-badge" style="background:' + p.teamColor + '">' + p.team + '</span></td>' +
      '<td>' + stats.avgMetres + 'm</td>' +
      '<td>' + stats.avgDef + '</td>' +
      '<td><span class="matrix-cell" style="background:' + c1 + '">' + stats.h1 + '/' + stats.t + '</span></td>' +
      '<td><span class="matrix-cell" style="background:' + c2 + '">' + stats.h2 + '/' + stats.t + '</span></td>' +
      '<td><span class="career-cell" style="background:' + cc + '">' + p.careerRate + '</span></td>';
    tbody.appendChild(row);
  });
}

populateTeamFilter();
renderTable();
</script>
</body>
</html>'''

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prop_matrix.html')
    with open(filepath, 'w') as f:
        f.write(html)

    print("\nMatrix generated! Opening in browser...")
    webbrowser.open('file:///' + filepath)

generate_matrix()