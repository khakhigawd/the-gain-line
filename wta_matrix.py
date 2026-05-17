import json
import requests
import webbrowser
import os

print("Building WTA Tennis Matrix from cached data...")

# Load pre-built data
with open('wta_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    players = data['players']
    matches_list = data['matches']

generated = data['generated']
print("Data generated: " + generated)

# Fetch live odds
def get_tennis_odds():
    try:
        url = 'https://api.the-odds-api.com/v4/sports/tennis_wta_madrid_open/odds/'
        params = {'apiKey': 'a3fd838c65e47cfdc22a13933f01a75', 'regions': 'us', 'oddsFormat': 'decimal'}
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
                                    odds_dict[player] = price
        return odds_dict
    except Exception as e:
        print("Odds error: " + str(e))
        return {}

print("Fetching live odds...")
odds = get_tennis_odds()
print("Odds found for " + str(len(odds)) + " players")

# Inject odds into player data
for p in players:
    price = odds.get(p['name'], None)
    if price:
        p['odds'] = ('+' + str(price)) if price > 0 else str(price)
    else:
        p['odds'] = 'N/A'

js_data = 'const tennisData = ' + json.dumps(players, ensure_ascii=False) + ';\n'
js_data += 'const matchData = ' + json.dumps(matches_list) + ';\n'

css = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #0a0a0a; color: #ffffff; overflow-x: auto; }
.header { background: #111; border-bottom: 1px solid #222; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 22px; font-weight: bold; color: #fff; letter-spacing: 1px; }
.logo span { color: #FF1493; }
.logo-span { color: #FF1493; }
.nav-tabs { display: flex; gap: 5px; }
.nav-tab { padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 13px; background: #1a1a1a; color: #666; font-weight: bold; border: 1px solid #333; transition: all 0.3s; }
.nav-tab.active { background: #FF1493; color: #fff; border-color: #FF1493; }
.nav-tab:hover { background: #FF1493; color: #fff; border-color: #FF1493; }
.controls { display: flex; gap: 10px; padding: 15px 20px; background: #111; border-bottom: 1px solid #222; flex-wrap: wrap; }
.control-group { display: flex; flex-direction: column; }
.control-label { font-size: 11px; color: #666; text-transform: uppercase; margin-bottom: 5px; }
select, input { padding: 8px 16px; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 5px; font-size: 13px; }
select:focus, input:focus { outline: none; border-color: #FF1493; }
.search-box { flex: 1; min-width: 200px; }
.container { padding: 20px; }
.matrix-title { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
.matrix-subtitle { font-size: 12px; color: #666; margin-bottom: 15px; }
.legend { display: flex; gap: 15px; margin-bottom: 15px; flex-wrap: wrap; font-size: 12px; }
.legend-item { display: flex; align-items: center; gap: 5px; }
.legend-box { width: 12px; height: 12px; border-radius: 2px; }
table { width: 100%; border-collapse: collapse; font-size: 12px; }
thead { background: rgba(255, 20, 147, 0.1); position: sticky; top: 0; z-index: 10; }
th { padding: 12px 8px; text-align: left; font-weight: bold; color: #FF1493; border-bottom: 2px solid #FF1493; white-space: nowrap; }
td { padding: 10px 8px; border-bottom: 1px solid #222; }
tr:hover { background: rgba(255, 20, 147, 0.05); }
.left { text-align: left; }
.stat-cell { text-align: center; padding: 8px; }
.elite { background: rgba(76, 175, 80, 0.2); color: #4CAF50; font-weight: bold; }
.good { background: rgba(255, 193, 7, 0.2); color: #FFC107; font-weight: bold; }
.weak { background: rgba(244, 67, 54, 0.2); color: #FF6B6B; }
.poor { background: rgba(244, 67, 54, 0.3); color: #FF5252; }
.country-badge { padding: 2px 6px; background: rgba(255, 20, 147, 0.1); border-radius: 3px; font-weight: bold; }
.trend-up2 { color: #FF1493; font-weight: bold; }
.trend-up1 { color: #FF69B4; }
.trend-flat { color: #999; }
.trend-down1 { color: #FF9800; }
.trend-down2 { color: #F44336; font-weight: bold; }
.footer { text-align: center; padding: 20px; color: #666; font-size: 11px; border-top: 1px solid #222; margin-top: 20px; }
.footer-links { margin-top: 10px; }
.footer-link { margin: 0 15px; cursor: pointer; color: #FF1493; text-decoration: none; }
.footer-link:hover { text-decoration: underline; }
.modal-overlay { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7); align-items: center; justify-content: center; }
.modal { background: #111; padding: 30px; border-radius: 10px; max-width: 500px; width: 90%; border: 1px solid #FF1493; }
.modal-header { font-size: 16px; font-weight: bold; margin-bottom: 15px; display: flex; justify-content: space-between; }
.close-btn { cursor: pointer; font-size: 20px; color: #666; }
.close-btn:hover { color: #fff; }
"""

js_code = """
function getCountryFlag(countryCode) {
const flags = {'USA':'🇺🇸','ESP':'🇪🇸','SRB':'🇷🇸','ITA':'🇮🇹','GER':'🇩🇪','FRA':'🇫🇷','AUS':'🇦🇺','CAN':'🇨🇦','GBR':'🇬🇧','AUT':'🇦🇹','SWE':'🇸🇪','NOR':'🇳🇴','DNK':'🇩🇰','RUS':'🇷🇺','UKR':'🇺🇦','POL':'🇵🇱','CZE':'🇨🇿','SVK':'🇸🇰','HUN':'🇭🇺','ROU':'🇷🇴','BUL':'🇧🇬','HRV':'🇭🇷','BIH':'🇧🇦','GRC':'🇬🇷','ALB':'🇦🇱','SVN':'🇸🇮','NLD':'🇳🇱','BEL':'🇧🇪','CHE':'🇨🇭','POR':'🇵🇹','JPN':'🇯🇵','CHN':'🇨🇳','KOR':'🇰🇷','IND':'🇮🇳','PAK':'🇵🇰','BRA':'🇧🇷','ARG':'🇦🇷','MEX':'🇲🇽','CHL':'🇨🇱','COL':'🇨🇴','ECU':'🇪🇨','URY':'🇺🇾','PER':'🇵🇪','VEN':'🇻🇪','THA':'🇹🇭','MYS':'🇲🇾','SGP':'🇸🇬','PHI':'🇵🇭','IDN':'🇮🇩','VNM':'🇻🇳','TWN':'🇹🇼','HKG':'🇭🇰','MUS':'🇲🇺','RSA':'🇿🇦','EGY':'🇪🇬','MAR':'🇲🇦','TUN':'🇹🇳','NGR':'🇳🇬','KEN':'🇰🇪','ISR':'🇮🇱','JOR':'🇯🇴','LBN':'🇱🇧','UZB':'🇺🇿','KAZ':'🇰🇿','TKM':'🇹🇲','TJK':'🇹🇯','KGZ':'🇰🇬','BLR':'🇧🇾','MDA':'🇲🇩','GEO':'🇬🇪','ARM':'🇦🇲','AZE':'🇦🇿','TUR':'🇹🇷','LTU':'🇱🇹','LVA':'🇱🇻','EST':'🇪🇪','FIN':'🇫🇮','ISL':'🇮🇸','IRL':'🇮🇪','MLT':'🇲🇹','CYP':'🇨🇾','NZL':'🇳🇿','FJI':'🇫🇯','PNG':'🇵🇬','TLS':'🇹🇱','KHM':'🇰🇭','LAO':'🇱🇦','MMR':'🇲🇲','BGD':'🇧🇩','SRL':'🇱🇰','AFG':'🇦🇫','IRN':'🇮🇷','IRQ':'🇮🇶','SAU':'🇸🇦','ARE':'🇦🇪','QAT':'🇶🇦','KWT':'🇰🇼','BHR':'🇧🇭','OMN':'🇴🇲','YEM':'🇾🇪','SYR':'🇸🇾','PSE':'🇵🇸','LBY':'🇱🇾','ALG':'🇩🇿'};
return flags[countryCode] || '🏳️';
}
function getColor(val, high, mid) {
if (val >= high) return '#1a7a1a';
if (val >= mid) return '#7a6a00';
return '#7a1a1a';
}
function getTrendClass(trend) {
if (trend === '↑↑') return 'trend-up2';
if (trend === '↑') return 'trend-up1';
if (trend === '→') return 'trend-flat';
if (trend === '↓') return 'trend-down1';
if (trend === '↓↓') return 'trend-down2';
return 'trend-flat';
}
function getEloColor(elo) {
if (elo >= 1900) return '#FF1493';
if (elo >= 1750) return '#FF69B4';
if (elo >= 1650) return '#FFB6C1';
if (elo >= 1550) return '#FFC0CB';
return '#888';
}
function populateFilters() {
const countries = [...new Set(tennisData.map(p => p.country))].sort();
const sel = document.getElementById('countryFilter');
countries.forEach(c => {
const opt = document.createElement('option');
opt.value = c; opt.textContent = c;
sel.appendChild(opt);
});
}
function renderTable() {
const surf = document.getElementById('surfaceFilter').value;
const country = document.getElementById('countryFilter').value;
const hand = document.getElementById('handFilter').value;
const minMatches = parseInt(document.getElementById('minMatchesFilter').value);
const sortBy = document.getElementById('sortByFilter').value;
const search = document.getElementById('searchFilter').value.toLowerCase();
let filtered = tennisData.filter(p => {
const s = p[surf] || p;
if (country !== 'all' && p.country !== country) return false;
if (hand !== 'all' && p.hand !== hand) return false;
if (s.matches < minMatches) return;
if (search && !p.name.toLowerCase().includes(search)) return false;
return true;
});
filtered.sort((a, b) => {
const sa = a[sortBy];
const sb = b[sortBy];
if (sortBy === 'win_rate') return sb.win_rate - sa.win_rate;
if (sortBy === 'rank') return a.rank - b.rank;
if (sortBy === 'elo') return sb.elo[surf] - sa.elo[surf];
if (sortBy === 'dominance_ratio') return sb.dominance_ratio - sa.dominance_ratio;
if (sortBy === 'first_serve_win_pct') return sb.first_serve_win_pct - sa.first_serve_win_pct;
if (sortBy === 'second_win_pct') return sb.second_win_pct - sa.second_win_pct;
if (sortBy === 'bp_save') return sb.bp_saved_pct - sa.bp_saved_pct;
if (sortBy === 'bp_convert') return sb.bp_convert_pct - sa.bp_convert_pct;
if (sortBy === 'tb_win') return sb.tb_win_rate - sa.tb_win_rate;
if (sortBy === 'dec_set') return sb.dec_set_win_rate - sa.dec_set_win_rate;
if (sortBy === 'avg_aces') return sb.avg_aces - sa.avg_aces;
if (sortBy === 'ace_df_ratio') return sb.ace_df_ratio - sa.ace_df_ratio;
return 0;
});
document.getElementById('playerCount').textContent = filtered.length + ' players';
const tbody = document.getElementById('tableBody');
tbody.innerHTML = '';
filtered.forEach(p => {
const s = p[surf] || p;
const eloVal = s.elo[surf] || s.elo['overall'];
const trendClass = getTrendClass(p.trend || '→');
const row = document.createElement('tr');
row.innerHTML = '<td class="left">' + p.name + '</td>' +
'<td><span class="country-badge">' + getCountryFlag(p.country) + '</span></td>' +
'<td>' + p.rank + '</td>' +
'<td>' + p.age + '</td>' +
'<td>' + p.height + '</td>' +
'<td>' + p.hand + '</td>' +
'<td>' + s.matches + '</td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.win_rate,65,55) + '">' + s.win_rate.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.tpw_pct,55,50) + '">' + s.tpw_pct.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.dominance_ratio,1.3,1.1) + '">' + s.dominance_ratio.toFixed(2) + '</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.first_serve_in_pct,65,60) + '">' + s.first_serve_in_pct.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.first_serve_win_pct,70,65) + '">' + s.first_serve_win_pct.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.second_win_pct,55,50) + '">' + s.second_win_pct.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.bp_saved_pct,65,55) + '">' + s.bp_saved_pct.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.bp_convert_pct,55,45) + '">' + s.bp_convert_pct.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.ret_first_pct,35,30) + '">' + s.ret_first_pct.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.ret_second_pct,55,50) + '">' + s.ret_second_pct.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.tb_win_rate,60,50) + '">' + s.tb_win_rate.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell" style="background:' + getColor(s.dec_set_win_rate,60,50) + '">' + s.dec_set_win_rate.toFixed(1) + '%</span></td>' +
'<td><span class="stat-cell">' + s.avg_aces.toFixed(1) + '</span></td>' +
'<td><span class="stat-cell">' + s.ace_df_ratio.toFixed(2) + '</span></td>' +
'<td class="' + trendClass + '">' + (p.trend || '→') + '</td>' +
'<td><span class="stat-cell" style="color:' + getEloColor(eloVal) + '">' + eloVal + '</span></td>' +
'<td><button class="h2h-btn" onclick="openH2H(\'' + p.name.replace(/'/g, "\\'") + '\')">H2H</button></td>';
tbody.appendChild(row);
});
}
function openH2H(playerName) {
document.getElementById('h2hTitle').textContent = playerName + ' Head-to-Head';
document.getElementById('h2hContent').textContent = 'H2H data loading...';
document.getElementById('h2hModal').style.display = 'flex';
}
function closeH2H() {
document.getElementById('h2hModal').style.display = 'none';
}
window.onclick = function(event) {
const modal = document.getElementById('h2hModal');
if (event.target === modal) modal.style.display = 'none';
}
document.addEventListener('DOMContentLoaded', function() {
populateFilters();
renderTable();
document.getElementById('surfaceFilter').addEventListener('change', renderTable);
document.getElementById('countryFilter').addEventListener('change', renderTable);
document.getElementById('handFilter').addEventListener('change', renderTable);
document.getElementById('minMatchesFilter').addEventListener('change', renderTable);
document.getElementById('sortByFilter').addEventListener('change', renderTable);
document.getElementById('searchFilter').addEventListener('keyup', renderTable);
});
"""

html_parts = [
'<!DOCTYPE html><html><head>',
'<title>WTA Tennis Matrix</title>',
'<style>' + css + '</style>',
'</head><body><div class="header">',
'<div class="logo">THE <span class="logo-span">GAIN</span> LINE</div>',
'<div class="nav-tabs">',
'<button class="nav-tab" onclick="location.href=\'index.html\'">Home</button>',
'<button class="nav-tab" onclick="location.href=\'prop_matrix.html\'">Rugby</button>',
'<button class="nav-tab" onclick="location.href=\'epl_matrix.html\'">Soccer</button>',
'<button class="nav-tab" onclick="location.href=\'tennis_matrix.html\'">ATP Tennis</button>',
'<button class="nav-tab active" onclick="location.href=\'wta_matrix.html\'">WTA Tennis</button>',
'<button class="nav-tab" onclick="location.href=\'match_simulator.html\'">Simulator</button>',
'</div></div>',
'<div class="controls">',
'<div class="control-group"><label class="control-label">Surface / Context</label><select id="surfaceFilter"><option value="overall">All Surfaces</option><option value="clay">Clay Court</option><option value="hard">Hard Court</option><option value="grass">Grass Court</option><option value="form_6m">Last 6 Months</option><option value="last5">Last 5</option><option value="last10">Last 10</option><option value="last15">Last 15</option><option value="form_6m">Last 6 Months</option><option value="last10">Last 10</option><option value="grass_last10">Grass L10</option></select></div>',
'<div class="control-group"><label class="control-label">Country</label><select id="countryFilter"><option value="all">All Countries</option></select></div>',
'<div class="control-group"><label class="control-label">Hand</label><select id="handFilter"><option value="all">All</option><option value="R">Right</option><option value="L">Left</option></select></div>',
'<div class="control-group"><label class="control-label">Min Matches</label><select id="minMatchesFilter"><option value="0">0+</option><option value="10">10+</option><option value="20">20+</option><option value="30">30+</option><option value="40">40+</option></select></div>',
'<div class="control-group"><label class="control-label">Sort By</label><select id="sortByFilter"><option value="win_rate">Win Rate</option><option value="rank">Rank</option><option value="elo">Elo</option><option value="dominance_ratio">Dominance</option><option value="first_serve_win_pct">1st Srv Win %</option><option value="second_win_pct">2nd Srv Win %</option><option value="bp_save">BP Saved %</option><option value="bp_convert">BP Conv %</option><option value="tb_win">TB Win %</option><option value="dec_set">Dec Set %</option><option value="avg_aces">Aces</option><option value="ace_df_ratio">A/DF Ratio</option></select></div>',
'<div class="control-group"><label class="control-label">Search Player</label><input type="text" id="searchFilter" placeholder="Type opponent name..." class="search-box"></div>',
'</div>',
'<div class="container">',
'<div class="matrix-title">WTA Tennis Matrix <span id="playerCount"></span></div>',
'<div class="matrix-subtitle">Clay Court Stats | 2022-2024 | Madrid Open Preview</div>',
'<div class="legend">',
'<div class="legend-item"><div class="legend-box" style="background:#1a7a1a"></div>60%+ hit rate</div>',
'<div class="legend-item"><div class="legend-box" style="background:#7a6a00"></div>40-59% hit rate</div>',
'<div class="legend-item"><div class="legend-box" style="background:#7a1a1a"></div>Under 40% hit rate</div>',
'</div>',
'<table><thead><tr>',
'<th class="left">PLAYER</th><th>CTY</th><th>RNK</th><th>AGE</th><th>HT</th><th>HND</th><th>M</th><th>WIN%</th><th>TPW%</th><th>DR</th><th>1ST IN%</th><th>1ST WIN%</th><th>2ND WIN%</th><th>BP SAV%</th><th>BP CNV%</th><th>RET 1ST%</th><th>RET 2ND%</th><th>TB WIN%</th><th>DEC SET%</th><th>ACES</th><th>A/DF</th><th>TREND</th><th>ELO</th><th>H2H</th>',
'</tr></thead><tbody id="tableBody"></tbody></table>',
'</div>',
'<div class="footer">The Gain Line | WTA 535 Players | Sackmann 2022-2024 + TennisMyLife 2025-2026 | Generated ' + generated + '</div>',
'<div class="footer-links">',
'<a class="footer-link" href="index.html">Home</a>',
'<a class="footer-link" href="prop_matrix.html">Rugby</a>',
'<a class="footer-link" href="epl_matrix.html">Soccer</a>',
'<a class="footer-link" href="tennis_matrix.html">ATP Tennis</a>',
'<a class="footer-link" href="wta_matrix.html">WTA Tennis</a>',
'<a class="footer-link" href="match_simulator.html">Simulator</a>',
'</div>',
'<div id="h2hModal" class="modal-overlay">',
'<div class="modal">',
'<div class="modal-header"><div id="h2hTitle"></div><span class="close-btn" onclick="closeH2H()">&times;</span></div>',
'<div id="h2hContent"></div>',
'</div>',
'</div>',
'<script>', js_data, js_code, '</script>',
'</body></html>'
]

html = ''.join(html_parts)

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wta_matrix.html')
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ wta_matrix.html generated successfully!")
print("📊 " + str(len(players)) + " players displayed")