import json
import html

COUNTRY_FLAGS = {
    'USA': '🇺🇸', 'ESP': '🇪🇸', 'SRB': '🇷🇸', 'ITA': '🇮🇹', 'GER': '🇩🇪',
    'FRA': '🇫🇷', 'AUS': '🇦🇺', 'CAN': '🇨🇦', 'GBR': '🇬🇧', 'AUT': '🇦🇹',
    'SWE': '🇸🇪', 'NOR': '🇳🇴', 'DNK': '🇩🇰', 'RUS': '🇷🇺', 'UKR': '🇺🇦',
    'POL': '🇵🇱', 'CZE': '🇨🇿', 'SVK': '🇸🇰', 'HUN': '🇭🇺', 'ROU': '🇷🇴',
    'BUL': '🇧🇬', 'HRV': '🇭🇷', 'SRB': '🇷🇸', 'BIH': '🇧🇦', 'GRC': '🇬🇷',
    'ALB': '🇦🇱', 'SVN': '🇸🇮', 'NLD': '🇳🇱', 'BEL': '🇧🇪', 'CHE': '🇨🇭',
    'POR': '🇵🇹', 'JPN': '🇯🇵', 'CHN': '🇨🇳', 'KOR': '🇰🇷', 'IND': '🇮🇳',
    'PAK': '🇵🇰', 'BRA': '🇧🇷', 'ARG': '🇦🇷', 'MEX': '🇲🇽', 'CHL': '🇨🇱',
    'COL': '🇨🇴', 'ECU': '🇪🇨', 'URY': '🇺🇾', 'PER': '🇵🇪', 'VEN': '🇻🇪',
    'THA': '🇹🇭', 'MYS': '🇲🇾', 'SGP': '🇸🇬', 'PHI': '🇵🇭', 'IDN': '🇮🇩',
    'VNM': '🇻🇳', 'TWN': '🇹🇼', 'HKG': '🇭🇰', 'MUS': '🇲🇺', 'RSA': '🇿🇦',
    'EGY': '🇪🇬', 'MAR': '🇲🇦', 'TUN': '🇹🇳', 'NGR': '🇳🇬', 'KEN': '🇰🇪',
    'ISR': '🇮🇱', 'JOR': '🇯🇴', 'LBN': '🇱🇧', 'UZB': '🇺🇿', 'KAZ': '🇰🇿',
    'TKM': '🇹🇲', 'TJK': '🇹🇯', 'KGZ': '🇰🇬', 'BLR': '🇧🇾', 'MDA': '🇲🇩',
    'GEO': '🇬🇪', 'ARM': '🇦🇲', 'AZE': '🇦🇿', 'TUR': '🇹🇷', 'LTU': '🇱🇹',
    'LVA': '🇱🇻', 'EST': '🇪🇪', 'FIN': '🇫🇮', 'ISL': '🇮🇸', 'IRL': '🇮🇪',
    'MLT': '🇲🇹', 'CYP': '🇨🇾', 'NZL': '🇳🇿', 'FJI': '🇫🇯', 'PNG': '🇵🇬',
    'TLS': '🇹🇱', 'KHM': '🇰🇭', 'LAO': '🇱🇦', 'MMR': '🇲🇲', 'BGD': '🇧🇩',
    'SRL': '🇱🇰', 'AFG': '🇦🇫', 'IRN': '🇮🇷', 'IRQ': '🇮🇶', 'SAU': '🇸🇦',
    'ARE': '🇦🇪', 'QAT': '🇶🇦', 'KWT': '🇰🇼', 'BHR': '🇧🇭', 'OMN': '🇴🇲',
    'YEM': '🇾🇪', 'SYR': '🇸🇾', 'PSE': '🇵🇸', 'LBY': '🇱🇾', 'ALG': '🇩🇿',
    'MAR': '🇲🇦', 'WAL': '🇬🇧', 'ENG': '🇬🇧', 'SCT': '🇬🇧', 'NIR': '🇬🇧',
}

def get_flag(country_code):
    """Convert country code to flag emoji, with fallback."""
    return COUNTRY_FLAGS.get(country_code, '🏳️')

def load_atp_data():
    """Load ATP player data from JSON."""
    try:
        with open('atp_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both formats: dict with 'players' key, or direct list
            if isinstance(data, dict) and 'players' in data:
                return data['players']
            elif isinstance(data, list):
                return data
            else:
                print("Error: Unexpected JSON structure")
                return []
    except FileNotFoundError:
        print("Error: atp_data.json not found. Run build_data.py first.")
        return []

def format_stat(value, stat_type='general'):
    """Format stat value with appropriate styling."""
    if value is None or value == '':
        return 'N/A'
    
    try:
        val_float = float(value)
    except (ValueError, TypeError):
        return str(value)
    
    if stat_type == 'percentage':
        return f"{val_float:.1f}%"
    elif stat_type == 'ratio':
        return f"{val_float:.2f}"
    else:
        if val_float == int(val_float):
            return str(int(val_float))
        return f"{val_float:.1f}"

def get_color_class(value, stat_type='general'):
    """Determine color class based on stat value."""
    if value is None or value == '':
        return 'neutral'
    
    try:
        val_float = float(value)
    except (ValueError, TypeError):
        return 'neutral'
    
    if stat_type == 'percentage':
        if val_float >= 65: return 'elite'
        elif val_float >= 55: return 'good'
        elif val_float >= 45: return 'weak'
        else: return 'poor'
    elif stat_type == 'ratio':
        if val_float >= 2.0: return 'elite'
        elif val_float >= 1.5: return 'good'
        elif val_float >= 1.0: return 'weak'
        else: return 'poor'
    else:
        return 'neutral'

def get_trend_symbol(trend):
    """Convert trend value to arrow symbols."""
    if not trend:
        return ''
    
    trend_map = {
        'strong_up': '⬆⬆',
        'up': '⬆',
        'stable': '→',
        'down': '⬇',
        'strong_down': '⬇⬇'
    }
    
    return trend_map.get(trend, '')

def generate_html(players):
    """Generate HTML table for ATP tennis players."""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ATP Tennis Matrix</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #00d084 0%, #00d084 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .data-timestamp {
            color: #aaa;
            font-size: 0.9em;
        }
        
        .nav-tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .nav-btn {
            padding: 10px 20px;
            border: 2px solid #00d084;
            background: transparent;
            color: #fff;
            cursor: pointer;
            border-radius: 5px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .nav-btn.active {
            background: #00d084;
            color: #1a1a2e;
        }
        
        .nav-btn:hover {
            background: #00d084;
            color: #1a1a2e;
        }
        
        .table-wrapper {
            overflow-x: auto;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
        }
        
        thead {
            background: rgba(0, 208, 132, 0.1);
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        th {
            padding: 12px 8px;
            text-align: left;
            font-weight: bold;
            color: #00d084;
            border-bottom: 2px solid #00d084;
            white-space: nowrap;
        }
        
        td {
            padding: 10px 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        tr:hover {
            background: rgba(0, 208, 132, 0.05);
        }
        
        .rank {
            font-weight: bold;
            color: #00d084;
            width: 50px;
        }
        
        .player-name {
            font-weight: 600;
            color: #fff;
            min-width: 150px;
        }
        
        .flag-cell {
            font-size: 1.5em;
            text-align: center;
            width: 50px;
        }
        
        .stat {
            text-align: center;
            padding: 8px;
        }
        
        .elite {
            background: rgba(76, 175, 80, 0.2);
            color: #4CAF50;
        }
        
        .good {
            background: rgba(255, 193, 7, 0.2);
            color: #FFD600;
        }
        
        .weak {
            background: rgba(244, 67, 54, 0.2);
            color: #FF6B6B;
        }
        
        .poor {
            background: rgba(244, 67, 54, 0.3);
            color: #FF5252;
        }
        
        .neutral {
            color: #ccc;
        }
        
        .trend {
            color: #00d084;
            font-weight: bold;
        }
        
        .h2h-btn {
            background: #00d084;
            color: #1a1a2e;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            font-size: 0.85em;
            transition: all 0.3s ease;
        }
        
        .h2h-btn:hover {
            background: #00b870;
            transform: scale(1.05);
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: #16213e;
            padding: 30px;
            border-radius: 10px;
            max-width: 500px;
            width: 90%;
            border: 2px solid #00d084;
        }
        
        .close-btn {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close-btn:hover {
            color: #fff;
        }
        
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8em;
            }
            
            table {
                font-size: 0.75em;
            }
            
            th, td {
                padding: 6px 4px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>ATP Tennis Player Matrix</h1>
            <p class="data-timestamp">Live data updated</p>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-btn" onclick="navigateTo('index.html')">Home</button>
            <button class="nav-btn" onclick="navigateTo('rugby.html')">Rugby</button>
            <button class="nav-btn" onclick="navigateTo('soccer.html')">Soccer</button>
            <button class="nav-btn active" onclick="navigateTo('tennis_matrix.html')">ATP Tennis</button>
            <button class="nav-btn" onclick="navigateTo('wta_matrix.html')">WTA Tennis</button>
            <button class="nav-btn" onclick="navigateTo('match_simulator.html')">Simulator</button>
        </div>
        
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Player</th>
                        <th>Flag</th>
                        <th>Age</th>
                        <th>Hand</th>
                        <th>Ht(cm)</th>
                        <th>Matches</th>
                        <th>Win%</th>
                        <th>1st In%</th>
                        <th>1st Srv Win%</th>
                        <th>2nd Srv Win%</th>
                        <th>BP Saved%</th>
                        <th>BP Conv%</th>
                        <th>Ret 1st%</th>
                        <th>Trend</th>
                        <th>Elo</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    for player in players:
        flag = get_flag(player.get('country', 'N/A'))
        rank = player.get('rank', 'N/A')
        name = player.get('name', 'Unknown')
        age = player.get('age', 'N/A')
        hand = player.get('hand', 'N/A')
        height = player.get('height', 'N/A')
        matches = player.get('matches', 'N/A')
        win_pct = player.get('win_pct', 'N/A')
        first_serve_in = player.get('first_serve_in_pct', 'N/A')
        first_srv_win = player.get('first_srv_win_pct', 'N/A')
        second_srv_win = player.get('second_srv_win_pct', 'N/A')
        bp_saved = player.get('bp_saved_pct', 'N/A')
        bp_conv = player.get('bp_conv_pct', 'N/A')
        ret_first = player.get('ret_first_pct', 'N/A')
        trend = player.get('trend', '')
        elo = player.get('elo', 'N/A')
        
        trend_symbol = get_trend_symbol(trend)
        
        win_color = get_color_class(win_pct, 'percentage')
        first_srv_color = get_color_class(first_srv_win, 'percentage')
        second_srv_color = get_color_class(second_srv_win, 'percentage')
        
        html_content += f'''                    <tr>
                        <td class="rank">{rank}</td>
                        <td class="player-name">{html.escape(name)}</td>
                        <td class="flag-cell" title="{player.get('country', 'N/A')}">{flag}</td>
                        <td class="stat">{age}</td>
                        <td class="stat">{hand}</td>
                        <td class="stat">{height}</td>
                        <td class="stat">{matches}</td>
                        <td class="stat {win_color}">{format_stat(win_pct, 'percentage')}</td>
                        <td class="stat">{format_stat(first_serve_in, 'percentage')}</td>
                        <td class="stat {first_srv_color}">{format_stat(first_srv_win, 'percentage')}</td>
                        <td class="stat {second_srv_color}">{format_stat(second_srv_win, 'percentage')}</td>
                        <td class="stat">{format_stat(bp_saved, 'percentage')}</td>
                        <td class="stat">{format_stat(bp_conv, 'percentage')}</td>
                        <td class="stat">{format_stat(ret_first, 'percentage')}</td>
                        <td class="stat trend">{trend_symbol}</td>
                        <td class="stat">{format_stat(elo, 'general')}</td>
                        <td class="stat"><button class="h2h-btn" onclick="showH2H('{html.escape(name)}')">H2H</button></td>
                    </tr>
'''
    
    html_content += '''                </tbody>
            </table>
        </div>
    </div>
    
    <div id="h2hModal" class="modal">
        <div class="modal-content">
            <span class="close-btn" onclick="closeH2H()">&times;</span>
            <h2 id="h2hTitle"></h2>
            <p id="h2hContent"></p>
        </div>
    </div>
    
    <script>
        function navigateTo(page) {
            window.location.href = page;
        }
        
        function showH2H(playerName) {
            document.getElementById('h2hTitle').textContent = playerName + ' Head-to-Head';
            document.getElementById('h2hContent').textContent = 'H2H data loading...';
            document.getElementById('h2hModal').classList.add('active');
        }
        
        function closeH2H() {
            document.getElementById('h2hModal').classList.remove('active');
        }
        
        window.onclick = function(event) {
            const modal = document.getElementById('h2hModal');
            if (event.target == modal) {
                modal.classList.remove('active');
            }
        }
    </script>
</body>
</html>'''
    
    return html_content

def main():
    """Main function to generate ATP tennis matrix."""
    players = load_atp_data()
    
    if not players:
        print("No player data found.")
        return
    
    print(f"Loaded {len(players)} ATP players")
    
    html_output = generate_html(players)
    
    with open('tennis_matrix.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print("✅ tennis_matrix.html generated successfully!")
    print(f"📊 {len(players)} players displayed")

if __name__ == '__main__':
    main()