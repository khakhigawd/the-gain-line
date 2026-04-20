import pandas as pd
import requests
import io
import json
import webbrowser
import os

print("Building H2H Lookup Tool...")

urls = [
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2023.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2022.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2021.csv",
    "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2020.csv",
]

def load_data(url):
    r = requests.get(url)
    return pd.read_csv(io.StringIO(r.text))

dfs = []
for url in urls:
    print("Loading " + url.split('/')[-1] + "...")
    dfs.append(load_data(url))
df = pd.concat(dfs, ignore_index=True)
print("Total matches: " + str(len(df)))

players = sorted(list(set(
    df['winner_name'].dropna().tolist() +
    df['loser_name'].dropna().tolist()
)))

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

print("Writing files...")

js_data = "var allPlayers = " + json.dumps(players) + ";\n"
js_data += "var matches = " + json.dumps(matches_list) + ";\n"

with open('h2h_data.js', 'w') as f:
    f.write(js_data)
print("Data saved to h2h_data.js")

css = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Arial, sans-serif; background: #0a0a0a; color: #fff; }
.header { background: #111; border-bottom: 2px solid #222; padding: 15px 20px; display: flex; align-items: center; justify-content: space-between; }
.logo { font-size: 22px; font-weight: bold; }
.logo span { color: #4CAF50; }
.nav-tabs { display: flex; gap: 5px; }
.nav-tab { padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 13px; background: #1a1a1a; color: #888; border: 1px solid #333; }
.nav-tab.active { background: #4CAF50; color: #fff; border-color: #4CAF50; }
.container { padding: 30px; max-width: 900px; margin: 0 auto; }
.lookup-box { background: #111; border-radius: 10px; padding: 25px; margin-bottom: 25px; border: 1px solid #222; }
.lookup-title { font-size: 16px; font-weight: bold; margin-bottom: 20px; color: #4CAF50; }
.player-selectors { display: flex; gap: 20px; align-items: flex-end; flex-wrap: wrap; }
.vs-label { font-size: 20px; font-weight: bold; color: #555; padding-bottom: 10px; }
.player-select { flex: 1; min-width: 200px; }
.player-select label { display: block; font-size: 11px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px; }
.search-wrapper { position: relative; }
input[type=text] { width: 100%; background: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 5px; padding: 10px 14px; font-size: 14px; }
input[type=text]:focus { outline: none; border-color: #4CAF50; }
.suggestions { background: #1a1a1a; border: 1px solid #444; border-radius: 5px; max-height: 200px; overflow-y: auto; position: absolute; width: 100%; z-index: 1000; top: 100%; left: 0; }
.suggestion-item { padding: 10px 14px; cursor: pointer; font-size: 13px; border-bottom: 1px solid #222; }
.suggestion-item:hover { background: #252525; color: #4CAF50; }
.lookup-btn { margin-top: 20px; background: #4CAF50; color: #fff; border: none; border-radius: 5px; padding: 12px 30px; font-size: 14px; font-weight: bold; cursor: pointer; width: 100%; }
.lookup-btn:hover { background: #45a045; }
.results { margin-top: 20px; }
.h2h-scoreboard { display: flex; justify-content: space-around; align-items: center; background: #1a1a1a; border-radius: 8px; padding: 25px; margin-bottom: 20px; text-align: center; }
.player-wins { font-size: 52px; font-weight: bold; color: #4CAF50; }
.player-name-display { font-size: 16px; font-weight: bold; margin-bottom: 8px; }
.vs-big { font-size: 28px; color: #444; font-weight: bold; }
.surface-row { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.surface-box { flex: 1; min-width: 80px; background: #1a1a1a; border-radius: 6px; padding: 12px; text-align: center; }
.surface-name { font-size: 11px; color: #888; text-transform: uppercase; margin-bottom: 6px; }
.surface-record { font-size: 18px; font-weight: bold; }
.clay-c { color: #cc7700; }
.hard-c { color: #4488ff; }
.grass-c { color: #4CAF50; }
.meetings-header { font-size: 13px; color: #666; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; font-weight: bold; }
.match-card { background: #111; border-radius: 6px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; border-left: 3px solid #333; }
.match-winner { font-weight: bold; color: #4CAF50; font-size: 14px; }
.match-loser { color: #888; font-size: 14px; }
.match-score { color: #aaa; font-size: 13px; }
.match-meta { display: flex; gap: 8px; align-items: center; font-size: 12px; }
.pill { padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold; }
.clay-pill { background: #3a1a00; color: #cc7700; }
.hard-pill { background: #001a3a; color: #4488ff; }
.grass-pill { background: #001a00; color: #4CAF50; }
.gs-pill { background: #2a2000; color: #ccaa00; }
.m-pill { background: #001a2a; color: #4488ff; }
.tourney-name { color: #666; }
.no-data { text-align: center; color: #555; padding: 30px; font-size: 14px; }
.error-msg { color: #cc4444; text-align: center; padding: 15px; font-size: 14px; }
"""

js_code = """
var sel1 = '', sel2 = '';

document.getElementById('p1input').addEventListener('input', function() {
    showSugg(this.value, 'sugg1', 1);
});
document.getElementById('p2input').addEventListener('input', function() {
    showSugg(this.value, 'sugg2', 2);
});

function showSugg(val, boxId, num) {
    var box = document.getElementById(boxId);
    if (val.length < 2) { box.style.display = 'none'; return; }
    var v = val.toLowerCase();
    var found = allPlayers.filter(function(p) { return p.toLowerCase().indexOf(v) !== -1; }).slice(0, 8);
    if (found.length === 0) { box.style.display = 'none'; return; }
    box.innerHTML = found.map(function(p) {
        return '<div class="suggestion-item" onclick="pickPlayer(' + num + ',this.innerText)">' + p + '</div>';
    }).join('');
    box.style.display = 'block';
}

function pickPlayer(num, name) {
    if (num === 1) {
        sel1 = name;
        document.getElementById('p1input').value = name;
        document.getElementById('sugg1').style.display = 'none';
    } else {
        sel2 = name;
        document.getElementById('p2input').value = name;
        document.getElementById('sugg2').style.display = 'none';
    }
}

document.addEventListener('click', function(e) {
    if (!e.target.closest('#wrapper1')) document.getElementById('sugg1').style.display = 'none';
    if (!e.target.closest('#wrapper2')) document.getElementById('sugg2').style.display = 'none';
});

function getSurfacePill(s) {
    if (s === 'Clay') return '<span class="pill clay-pill">Clay</span>';
    if (s === 'Hard') return '<span class="pill hard-pill">Hard</span>';
    if (s === 'Grass') return '<span class="pill grass-pill">Grass</span>';
    return '<span class="pill">' + s + '</span>';
}

function getLevelPill(l) {
    if (l === 'G') return '<span class="pill gs-pill">Grand Slam</span>';
    if (l === 'M') return '<span class="pill m-pill">Masters</span>';
    return '';
}

function doLookup() {
    var p1 = sel1 || document.getElementById('p1input').value.trim();
    var p2 = sel2 || document.getElementById('p2input').value.trim();

    if (!p1 || !p2) {
        document.getElementById('results').innerHTML = '<div class="error-msg">Please select both players from the dropdown.</div>';
        return;
    }

    if (p1 === p2) {
        document.getElementById('results').innerHTML = '<div class="error-msg">Please select two different players.</div>';
        return;
    }

    var h2h = matches.filter(function(m) {
        return (m.w === p1 && m.l === p2) || (m.w === p2 && m.l === p1);
    });

    if (h2h.length === 0) {
        document.getElementById('results').innerHTML = '<div class="no-data">No matches found between ' + p1 + ' and ' + p2 + ' in 2020-2024 data.</div>';
        return;
    }

    var p1wins = h2h.filter(function(m) { return m.w === p1; }).length;
    var p2wins = h2h.filter(function(m) { return m.w === p2; }).length;

    var surfaces = ['Clay', 'Hard', 'Grass'];
    var surfHTML = '';
    surfaces.forEach(function(s) {
        var p1s = h2h.filter(function(m) { return m.w === p1 && m.s === s; }).length;
        var p2s = h2h.filter(function(m) { return m.w === p2 && m.s === s; }).length;
        if (p1s + p2s > 0) {
            var cls = s === 'Clay' ? 'clay-c' : s === 'Hard' ? 'hard-c' : 'grass-c';
            surfHTML += '<div class="surface-box"><div class="surface-name ' + cls + '">' + s + '</div><div class="surface-record ' + cls + '">' + p1s + ' - ' + p2s + '</div></div>';
        }
    });

    var sorted = h2h.slice().sort(function(a,b) { return parseInt(b.d) - parseInt(a.d); });
    var matchHTML = sorted.map(function(m) {
        var winner = m.w;
        var loser = (m.l === p1) ? p1 : p2;
        var year = m.d.substring(0,4);
        return '<div class="match-card">' +
            '<div><span class="match-winner">' + winner + '</span> <span class="match-loser">def. ' + loser + '</span> <span class="match-score">' + m.sc + '</span></div>' +
            '<div class="match-meta">' + getLevelPill(m.lv) + getSurfacePill(m.s) + '<span class="tourney-name">' + m.t + ' ' + year + '</span></div>' +
        '</div>';
    }).join('');

    document.getElementById('results').innerHTML =
        '<div class="h2h-scoreboard">' +
            '<div><div class="player-name-display">' + p1 + '</div><div class="player-wins">' + p1wins + '</div></div>' +
            '<div class="vs-big">VS</div>' +
            '<div><div class="player-name-display">' + p2 + '</div><div class="player-wins">' + p2wins + '</div></div>' +
        '</div>' +
        '<div class="surface-row">' + surfHTML + '</div>' +
        '<div class="meetings-header">All Meetings (' + h2h.length + ')</div>' +
        matchHTML;
}
"""

html_parts = [
    '<!DOCTYPE html><html><head>',
    '<title>The Gain Line - H2H</title>',
    '<style>', css, '</style>',
    '</head><body>',
    '<div class="header">',
    '<div class="logo">THE <span>GAIN</span> LINE</div>',
    '<div class="nav-tabs">',
    '<div class="nav-tab">Super Rugby Pacific</div>',
    '<div class="nav-tab">EPL Soccer</div>',
    '<div class="nav-tab active">Tennis H2H</div>',
    '</div></div>',
    '<div class="container">',
    '<div class="lookup-box">',
    '<div class="lookup-title">Head to Head Lookup</div>',
    '<div class="player-selectors">',
    '<div class="player-select"><label>Player 1</label>',
    '<div class="search-wrapper" id="wrapper1">',
    '<input type="text" id="p1input" placeholder="Type player name..." autocomplete="off">',
    '<div class="suggestions" id="sugg1" style="display:none"></div>',
    '</div></div>',
    '<div class="vs-label">VS</div>',
    '<div class="player-select"><label>Player 2</label>',
    '<div class="search-wrapper" id="wrapper2">',
    '<input type="text" id="p2input" placeholder="Type player name..." autocomplete="off">',
    '<div class="suggestions" id="sugg2" style="display:none"></div>',
    '</div></div>',
    '</div>',
    '<button class="lookup-btn" onclick="doLookup()">LOOK UP H2H</button>',
    '</div>',
    '<div class="results" id="results"></div>',
    '</div>',
    '<script src="h2h_data.js"></script>',
    '<script>', js_code, '</script>',
    '</body></html>'
]

html = ''.join(html_parts)

filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'h2h_lookup.html')
with open(filepath, 'w') as f:
    f.write(html)

print("H2H tool generated!")
print("Opening browser...")
webbrowser.open('file:///' + filepath)