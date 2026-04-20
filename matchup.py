from rugbypy.team import *
import pandas as pd
import webbrowser
import os

HURRICANES_ID = 'ada90f2c'
CRUSADERS_ID = '93b14fff'

def clean(value):
    if pd.isna(value):
        return "N/A"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

def format_date(date_str):
    date_str = str(date_str)
    return date_str[4:6] + "/" + date_str[6:8] + "/" + date_str[0:4]

def get_team_form(team_id, games=5):
    stats = fetch_team_stats(team_id=team_id)
    recent = stats[[
        'game_date','team_vs','score','team_vs_score',
        'tries','metres_carried','clean_breaks',
        'penalties_conceded','missed_tackles'
    ]].tail(games)
    return recent

def build_game_card(row, color):
    return (
        '<div class="game-card">'
        '<div class="game-header" style="background:' + color + '">'
        '<span>' + format_date(row['game_date']) + '</span>'
        '<span>vs ' + str(row['team_vs']) + '</span>'
        '<span>Score: ' + clean(row['score']) + ' - ' + clean(row['team_vs_score']) + '</span>'
        '</div>'
        '<div class="game-stats">'
        '<div class="stat"><span class="label">Tries</span><span class="value">' + clean(row['tries']) + '</span></div>'
        '<div class="stat"><span class="label">Metres Carried</span><span class="value">' + clean(row['metres_carried']) + '</span></div>'
        '<div class="stat"><span class="label">Clean Breaks</span><span class="value">' + clean(row['clean_breaks']) + '</span></div>'
        '<div class="stat"><span class="label">Penalties</span><span class="value">' + clean(row['penalties_conceded']) + '</span></div>'
        '<div class="stat"><span class="label">Missed Tackles</span><span class="value">' + clean(row['missed_tackles']) + '</span></div>'
        '</div>'
        '</div>'
    )

def build_team_section(team_name, team_id, color, games=5):
    data = get_team_form(team_id, games)
    cards = ""
    for _, row in data.iterrows():
        cards += build_game_card(row, color)
    return (
        '<div class="team-section">'
        '<h2 style="background:' + color + '">' + team_name.upper() + ' - LAST ' + str(games) + ' GAMES</h2>'
        + cards +
        '</div>'
    )

def get_css():
    return """
        body { font-family: Arial, sans-serif; background: #0a0a0a; color: #ffffff; margin: 0; padding: 20px; }
        h1 { text-align: center; font-size: 28px; color: #ffffff; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 30px; }
        .container { max-width: 900px; margin: 0 auto; }
        .team-section { margin-bottom: 40px; }
        .team-section h2 { padding: 15px 20px; border-radius: 8px 8px 0 0; margin: 0; font-size: 18px; letter-spacing: 1px; }
        .game-card { background: #1a1a1a; margin-bottom: 10px; border-radius: 6px; overflow: hidden; border: 1px solid #333; }
        .game-header { display: flex; justify-content: space-between; padding: 10px 15px; font-weight: bold; font-size: 14px; }
        .game-stats { display: flex; flex-wrap: wrap; padding: 12px 15px; gap: 10px; }
        .stat { background: #252525; border-radius: 6px; padding: 8px 14px; display: flex; flex-direction: column; align-items: center; min-width: 100px; }
        .label { font-size: 11px; color: #888; margin-bottom: 4px; }
        .value { font-size: 20px; font-weight: bold; color: #ffffff; }
        .footer { text-align: center; color: #555; font-size: 12px; margin-top: 40px; }
    """

def generate_report():
    print("Fetching data...")
    hurricanes_html = build_team_section("Hurricanes", HURRICANES_ID, "#003087")
    crusaders_html = build_team_section("Crusaders", CRUSADERS_ID, "#E31937")

    html = (
        '<!DOCTYPE html><html><head>'
        '<title>Rugby Edge Matchup Report</title>'
        '<style>' + get_css() + '</style>'
        '</head><body><div class="container">'
        '<h1>RUGBY EDGE - MATCHUP REPORT</h1>'
        + hurricanes_html
        + crusaders_html +
        '<div class="footer">Powered by Rugby Edge | Data updated daily</div>'
        '</div></body></html>'
    )

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'matchup_report.html')
    with open(filepath, 'w') as f:
        f.write(html)

    print("Report generated! Opening in browser...")
    webbrowser.open('file:///' + filepath)

generate_report()