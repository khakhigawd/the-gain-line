import json
import webbrowser
import os

print("Building Layback Analytics — WTA Tennis Matrix...")

with open('wta_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

players = data['players']
matches_list = data['matches']
generated = data['generated']
print("Loaded " + str(len(players)) + " players, " + str(len(matches_list)) + " matches")
print("Data generated: " + generated)

js_data = 'const wtaData = ' + json.dumps(players) + ';\n'
js_data += 'const wtaMatchData = ' + json.dumps(matches_list) + ';\n'

css = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #0a0a0a; color: #ffffff; overflow-x: auto; }
.header { background: #111; border-bottom: 2px solid #222; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 22px; font-weight: bold; color: #fff; letter-spacing: 1px; }
.logo span { color: #e91e8c; }
.nav-tabs { display: flex; gap: 5px; }
.nav-tab { padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 13px; background: #1a1a1a; color: #888; border: 1px solid #333; }
.nav-tab.active { background: #e91e8c; color: #fff; border-color: #e91e8c; }
.controls { display: flex; gap: 10px; padding: 15px 20px; background: #0f0f0f; border-bottom: 1px solid #222; flex-wrap: wrap; align-items: center; }
.control-group { display: flex; flex-direction: column; gap: 4px; }
.control-label { font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; }
select, input { background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 5px; padding: 8px 12px; font-size: 13px; cursor: pointer; }
select:focus, input:focus { outline: none; border-color: #e91e8c; }
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
tr:hover { background: #111; }
.count-badge { background: #333; color: #888; font-size: 11px; padding: 2px 8px; border-radius: 10px; margin-left: 8px; }
.footer { text-align: center; color: #333; font-size: 11px; padding: 20px; border-top: 1px solid #111; margin-top: 20px; }
.legend { display: flex; gap: 20px; justify-content: center; margin: 15px 0; font-size: 12px; color: #888; flex-wrap: wrap; }
.legend-item { display: flex; align-items: center; gap: 6px; }
.legend-box { width: 12px; height: 12px; border-radius: 2px; flex-shrink: 0; }
.trend-up2 { color: #00dd00; font-weight: bold; }
.trend-up1 { color: #88cc88; }
.trend-down2 { color: #ff4444; font-weight: bold; }
.trend-down1 { color: #cc8888; }
.trend-flat { color: #555; }
.h2h-btn { background: #3a0a1a; color: #e91e8c; border: 1px solid #e91e8c; border-radius: 4px; padding: 4px 10px; font-size: 11px; cursor: pointer; font-weight: bold; }
.h2h-btn:hover { background: #e91e8c; color: #fff; }
.modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: flex-start; padding-top: 50px; }
.modal-overlay.active { display: flex; }
.modal { background: #111; border-radius: 10px; padding: 25px; width: 90%; max-width: 700px; max-height: 80vh; overflow-y: auto; border: 1px solid #333; }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.modal-title { font-size: 16px; font-weight: bold; color: #e91e8c; }
.modal-close { background: none; border: none; color: #888; font-size: 24px; cursor: pointer; }
.modal-close:hover { color: #fff; }
.h2h-search { width: 100%; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 5px; padding: 10px; font-size: 14px; margin-bottom: 8px; }
.h2h-search:focus { outline: none; border-color: #e91e8c; }
.h2h-lookup-btn { background: #e91e8c; color: #fff; border: none; border-radius: 5px; padding: 10px 20px; font-size: 14px; font-weight: bold; cursor: pointer; width: 100%; margin-bottom: 20px; margin-top: 8px; }
.h2h-lookup-btn:hover { background: #c0166e; }
.h2h-scoreboard { display: flex; justify-content: space-around; align-items: center; background: #1a1a1a; border-radius: 8px; padding: 20px; margin-bottom: 15px; text-align: center; }
.h2h-wins { font-size: 42px; font-weight: bold; color: #e91e8c; }
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
.mwinner { font-weight: bold; color: #e91e8c; font-size: 13px; }
.mscore { color: #aaa; font-size: 12px; }
.mmeta { display: flex; gap: 6px; align-items: center; font-size: 11px; color: #666; }
.pill { padding: 2px 7px; border-radius: 10px; font-size: 10px; font-weight: bold; }
.clay-pill { background: #3a1a00; color: #cc7700; }
.hard-pill { background: #001a3a; color: #4488ff; }
.grass-pill { background: #001a00; color: #4CAF50; }
.gs-pill { background: #2a2000; color: #ccaa00; }
.m-pill { background: #3a0a1a; color: #e91e8c; }
.sugg-box { background: #1a1a1a; border: 1px solid #333; border-radius: 5px; max-height: 150px; overflow-y: auto; margin-bottom: 8px; }
.sugg-item { padding: 8px 12px; cursor: pointer; font-size: 13px; border-bottom: 1px solid #222; }
.sugg-item:hover { background: #252525; color: #e91e8c; }
"""

js_code = """
function getColor(val, high, mid) {
  if (val >= high) return '#1a7a1a';
  if (val >= mid) return '#7a6a00';
  return '#7a1a1a';
}
function getTrendClass(trend) {
  if (trend === '\u2191\u2191') return 'trend-up2';
  if (trend === '\u2191') return 'trend-up1';
  if (trend === '\u2193\u2193') return 'trend-down2';
  if (trend === '\u2193') return 'trend-down1';
  return 'trend-flat';
}
function getEloColor(elo) {
  if (elo >= 1900) return '#00dd00';
  if (elo >= 1750) return '#88cc44';
  if (elo >= 1650) return '#ccaa00';
  if (elo >= 1550) return '#cc6600';
  return '#888';
}
function populateFilters() {
  const countries = [...new Set(wtaData.map(p => p.country))].sort();
  const sel = document.getElementById('countryFilter');
  countries.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c;
    sel.appendChild(opt);
  });
}
function getSurfaceKey(surface) {
  const keys = {
    'clay':'clay','hard':'hard','grass':'grass','all':'all',
    'form_6m':'form_6m','last5':'last5','last10':'last10','last15':'last15',
    'grandslam':'grandslam','masters':'masters',
    'clay_last10':'clay_last10','hard_last10':'hard_last10','grass_last10':'grass_last10'
  };
  return keys[surface] || 'all';
}
function getEloSurface(surface) {
  if (surface === 'clay' || surface === 'clay_last10') return 'clay';
  if (surface === 'hard' || surface === 'hard_last10') return 'hard';
  if (surface === 'grass' || surface === 'grass_last10') return 'grass';
  return 'overall';
}
function renderTable() {
  const surface = document.getElementById('surfaceFilter').value;
  const country = document.getElementById('countryFilter').value;
  const hand = document.getElementById('handFilter').value;
  const minMatches = parseInt(document.getElementById('minMatches').value);
  const sortBy = document.getElementById('sortBy').value;
  const search = document.getElementById('searchBox').value.toLowerCase();
  const sKey = getSurfaceKey(surface);
  const eloSurf = getEloSurface(surface);
  const subtitles = {
    'clay': 'Clay Court Stats | 2022-2024',
    'hard': 'Hard Court Stats | 2022-2024',
    'grass': 'Grass Court Stats | 2022-2024',
    'all': 'All Surface Stats | 2022-2024',
    'form_6m': 'Last 6 Months Form',
    'last5': 'Last 5 Matches',
    'last10': 'Last 10 Matches',
    'last15': 'Last 15 Matches',
    'clay_last10': 'Clay - Last 10 Matches',
    'hard_last10': 'Hard - Last 10 Matches',
    'grass_last10': 'Grass - Last 10 Matches',
    'grandslam': 'Grand Slam Performance | 2022-2024',
    'masters': 'WTA 1000 Performance | 2022-2024'
  };
  document.getElementById('matrixSubtitle').textContent = subtitles[surface] || '';
  let filtered = wtaData.filter(p => {
    const s = p[sKey];
    if (country !== 'all' && p.country !== country) return false;
    if (hand !== 'all' && p.hand !== hand) return false;
    if (search && !p.name.toLowerCase().includes(search)) return false;
    if (!s || s.matches < minMatches) return false;
    return true;
  });
  filtered.sort((a, b) => {
    const sa = a[sKey]; const sb = b[sKey];
    if (sortBy === 'win_rate') return sb.win_rate - sa.win_rate;
    if (sortBy === 'rank') return a.rank - b.rank;
    if (sortBy === 'elo') return b.elo[eloSurf] - a.elo[eloSurf];
    if (sortBy === 'tpw') return sb.tpw_pct - sa.tpw_pct;
    if (sortBy === 'dominance') return sb.dominance_ratio - sa.dominance_ratio;
    if (sortBy === 'first_win') return sb.first_serve_win_pct - sa.first_serve_win_pct;
    if (sortBy === 'second_win') return sb.second_serve_win_pct - sa.second_serve_win_pct;
    if (sortBy === 'bp_save') return sb.bp_save_pct - sa.bp_save_pct;
    if (sortBy === 'bp_convert') return sb.bp_convert_pct - sa.bp_convert_pct;
    if (sortBy === 'tb_win') return sb.tb_win_rate - sa.tb_win_rate;
    if (sortBy === 'dec_set') return sb.dec_set_win_rate - sa.dec_set_win_rate;
    if (sortBy === 'aces') return sb.avg_aces - sa.avg_aces;
    if (sortBy === 'ace_df') return sb.ace_df_ratio - sa.ace_df_ratio;
    return 0;
  });
  document.getElementById('playerCount').textContent = filtered.length + ' players';
  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';
  filtered.forEach(p => {
    const s = p[sKey];
    if (!s || s.matches === 0) return;
    const eloVal = p.elo[eloSurf];
    const eloTrend = eloSurf === 'overall' ? '-' : p.elo[eloSurf + '_trend'];
    const trendClass = getTrendClass(eloTrend);
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
      '<td><span class="stat-cell" style="background:' + getColor(s.first_serve_in_pct,65,60) + '">' + s.first_serve_in_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.first_serve_win_pct,72,65) + '">' + s.first_serve_win_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.second_serve_win_pct,52,45) + '">' + s.second_serve_win_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.bp_save_pct,65,58) + '">' + s.bp_save_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.bp_convert_pct,45,35) + '">' + s.bp_convert_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.ret_first_won_pct,32,27) + '">' + s.ret_first_won_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.ret_second_won_pct,52,45) + '">' + s.ret_second_won_pct + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.tb_win_rate,60,50) + '">' + s.tb_win_rate + '%</span></td>' +
      '<td><span class="stat-cell" style="background:' + getColor(s.dec_set_win_rate,65,50) + '">' + s.dec_set_win_rate + '%</span></td>' +
      '<td>' + s.avg_aces + '</td>' +
      '<td>' + s.avg_df + '</td>' +
      '<td>' + s.ace_df_ratio + '</td>' +
      '<td class="elo-cell" style="color:' + getEloColor(eloVal) + '">' + eloVal + '</td>' +
      '<td class="' + trendClass + '">' + eloTrend + '</td>' +
      '<td><button class="h2h-btn" onclick="openH2H(\\'' + safeName + '\\')">H2H</button></td>';
    tbody.appendChild(row);
  });
}
var currentPlayer = '', selectedOpp = '';
function openH2H(playerName) {
  currentPlayer = playerName;
  selectedOpp = '';
  document.getElementById('modalTitle').textContent = playerName + ' - H2H';
  document.getElementById('oppInput').value = '';
  document.getElementById('oppSugg').innerHTML = '';
  document.getElementById('h2hResults').innerHTML = '';
  document.getElementById('h2hModal').classList.add('active');
}
function closeH2H() { document.getElementById('h2hModal').classList.remove('active'); }
function showOppSugg(val) {
  var box = document.getElementById('oppSugg');
  if (val.length < 2) { box.innerHTML = ''; return; }
  var v = val.toLowerCase();
  var found = wtaData.map(p => p.name).filter(n => n.toLowerCase().includes(v) && n !== currentPlayer).slice(0, 8);
  box.innerHTML = found.map(n => '<div class="sugg-item" onclick="pickOpp(this.textContent)">' + n + '</div>').join('');
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
  if (l==='P') return '<span class="pill m-pill">WTA1000</span>';
  return '';
}
function runH2H() {
  var p1 = currentPlayer;
  var p2 = selectedOpp || document.getElementById('oppInput').value.trim();
  if (!p2) { document.getElementById('h2hResults').innerHTML = '<p style="color:#888;text-align:center;padding:15px">Select an opponent</p>'; return; }
  var h2h = wtaMatchData.filter(m => (m.w===p1&&m.l===p2)||(m.w===p2&&m.l===p1));
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
    '<div class="match-card"><div><span class="mwinner">'+m.w+'</span> def. <span style="color:#888">'+m.l+'</span> <span class="mscore">'+m.sc+'</span></div>' +
    '<div class="mmeta">'+getLvlPill(m.lv)+getSurfPill(m.s)+'<span>'+m.t+' '+m.d.substring(0,4)+'</span></div></div>'
  ).join('');
  document.getElementById('h2hResults').innerHTML =
    '<div class="h2h-scoreboard"><div><div class="h2h-pname">'+p1+'</div><div class="h2h-wins">'+p1w+'</div></div>' +
    '<div class="h2h-vs">VS</div><div><div class="h2h-pname">'+p2+'</div><div class="h2h-wins">'+p2w+'</div></div></div>' +
    '<div class="surf-row">'+surfHTML+'</div>' +
    '<div class="meetings-hdr">All Meetings ('+h2h.length+')</div>'+mHTML;
}
document.getElementById('h2hModal').addEventListener('click', function(e) { if (e.target === this) closeH2H(); });
populateFilters();
renderTable();
"""

html_parts = [
    '<!DOCTYPE html><html><head>',
    '<meta charset="UTF-8">',
    '<title>Layback Analytics - WTA Tennis</title>',
    '<style>', css, '</style>',
    '</head><body>',
    '<script>if (!sessionStorage.getItem("layback_auth")) { window.location.href = "password.html"; }</script>',
    '<div class="header">',
    '<div class="logo">LAYBACK <span>ANALYTICS</span></div>',
    '<div class="nav-tabs">',
    '<div class="nav-tab" onclick="location.href=\'prop_matrix.html\'">Super Rugby Pacific</div>',
    '<div class="nav-tab" onclick="location.href=\'epl_matrix.html\'">EPL Soccer</div>',
    '<div class="nav-tab" onclick="location.href=\'tennis_matrix.html\'">ATP Tennis</div>',
    '<div class="nav-tab active">WTA Tennis</div>',
    '<div class="nav-tab" onclick="location.href=\'match_simulator.html\'">Simulator</div>',
    '</div></div>',
    '<div class="controls">',
    '<div class="control-group"><span class="control-label">Surface / Context</span>',
    '<select id="surfaceFilter" onchange="renderTable()">',
    '<option value="clay">Clay Court</option>',
    '<option value="hard">Hard Court</option>',
    '<option value="grass">Grass Court</option>',
    '<option value="all">All Surfaces</option>',
    '<option value="form_6m">Last 6 Months</option>',
    '<option value="last5">Last 5 Matches</option>',
    '<option value="last10">Last 10 Matches</option>',
    '<option value="last15">Last 15 Matches</option>',
    '<option value="clay_last10">Clay - Last 10</option>',
    '<option value="hard_last10">Hard - Last 10</option>',
    '<option value="grass_last10">Grass - Last 10</option>',
    '<option value="grandslam">Grand Slams Only</option>',
    '<option value="masters">WTA 1000 Only</option>',
    '</select></div>',
    '<div class="control-group"><span class="control-label">Country</span>',
    '<select id="countryFilter" onchange="renderTable()"><option value="all">All Countries</option></select></div>',
    '<div class="control-group"><span class="control-label">Hand</span>',
    '<select id="handFilter" onchange="renderTable()">',
    '<option value="all">All</option><option value="R">Right</option><option value="L">Left</option>',
    '</select></div>',
    '<div class="control-group"><span class="control-label">Min Matches</span>',
    '<select id="minMatches" onchange="renderTable()">',
    '<option value="0">Any</option><option value="5">5+</option><option value="10">10+</option>',
    '<option value="20" selected>20+</option><option value="30">30+</option><option value="50">50+</option>',
    '</select></div>',
    '<div class="control-group"><span class="control-label">Sort By</span>',
    '<select id="sortBy" onchange="renderTable()">',
    '<option value="win_rate">Win Rate</option>',
    '<option value="rank">WTA Ranking</option>',
    '<option value="elo">Elo Rating</option>',
    '<option value="tpw">TPW%</option>',
    '<option value="dominance">Dominance Ratio</option>',
    '<option value="first_win">1st Serve Win%</option>',
    '<option value="second_win">2nd Serve Win%</option>',
    '<option value="bp_save">BP Save%</option>',
    '<option value="bp_convert">BP Convert%</option>',
    '<option value="tb_win">Tiebreak Win%</option>',
    '<option value="dec_set">Deciding Set Win%</option>',
    '<option value="aces">Avg Aces</option>',
    '<option value="ace_df">Ace/DF Ratio</option>',
    '</select></div>',
    '<div class="control-group search-box"><span class="control-label">Search Player</span>',
    '<input type="text" id="searchBox" placeholder="Search player name..." oninput="renderTable()"></div>',
    '</div>',
    '<div class="container">',
    '<div class="matrix-title">WTA Tennis Matrix <span class="count-badge" id="playerCount"></span></div>',
    '<div class="matrix-subtitle" id="matrixSubtitle">Clay Court Stats | 2022-2024 | Updated ' + generated + '</div>',
    '<div class="legend">',
    '<div class="legend-item"><div class="legend-box" style="background:#1a7a1a"></div>Elite</div>',
    '<div class="legend-item"><div class="legend-box" style="background:#7a6a00"></div>Good</div>',
    '<div class="legend-item"><div class="legend-box" style="background:#7a1a1a"></div>Weak</div>',
    '<div class="legend-item"><span class="trend-up2">&#8593;&#8593;</span> Strong rise</div>',
    '<div class="legend-item"><span class="trend-up1">&#8593;</span> Rising</div>',
    '<div class="legend-item"><span class="trend-down1">&#8595;</span> Falling</div>',
    '<div class="legend-item"><span class="trend-down2">&#8595;&#8595;</span> Sharp fall</div>',
    '</div>',
    '<table><thead><tr>',
    '<th class="left">PLAYER</th><th>CTY</th><th>RNK</th><th>AGE</th><th>HT</th><th>HND</th>',
    '<th>M</th><th>WIN%</th><th>TPW%</th><th>DR</th>',
    '<th>1ST IN%</th><th>1ST WIN%</th><th>2ND WIN%</th>',
    '<th>BP SAV%</th><th>BP CNV%</th>',
    '<th>RET 1ST%</th><th>RET 2ND%</th>',
    '<th>TB WIN%</th><th>DEC SET%</th>',
    '<th>ACES</th><th>DF</th><th>A/DF</th>',
    '<th>ELO</th><th>TREND</th><th>H2H</th>',
    '</tr></thead>',
    '<tbody id="tableBody"></tbody></table>',
    '<div class="footer">Layback Analytics | WTA 300 Players | Sackmann 2022-2024 | Generated: ' + generated + '</div>',
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
    '<script>', js_data, js_code, '</script>',
    '</body></html>'
]

html = ''.join(html_parts)

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wta_matrix.html')
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)

print("Layback Analytics WTA Tennis Matrix generated!")
webbrowser.open('file:///' + filepath)