import requests
import json
import webbrowser
import os

API_KEY = 'a3fd838c65e47cfdce22a13933f01a75'
SPORT = 'soccer_epl'

# Books we care about
TARGET_BOOKS = ['fanduel', 'draftkings', 'betmgm', 'betrivers', 'bovada']
BOOK_NAMES = {
    'fanduel': 'FanDuel',
    'draftkings': 'DraftKings',
    'betmgm': 'BetMGM',
    'betrivers': 'BetRivers',
    'bovada': 'Bovada'
}

def get_epl_odds():
    url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds/'
    params = {
        'apiKey': API_KEY,
        'regions': 'us',
        'markets': 'h2h',
        'oddsFormat': 'american'
    }
    r = requests.get(url, params=params)
    return r.json()

def format_odds(price):
    if price > 0:
        return '+' + str(price)
    return str(price)

def format_date(dt_str):
    from datetime import datetime
    dt = datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%SZ')
    return dt.strftime('%a %b %d, %Y %I:%M %p UTC')

def get_best_odds(bookmakers, team_name):
    best = None
    best_book = ''
    for bm in bookmakers:
        if bm['key'] not in TARGET_BOOKS:
            continue
        for market in bm['markets']:
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    if outcome['name'] == team_name:
                        price = outcome['price']
                        if best is None or price > best:
                            best = price
                            best_book = BOOK_NAMES.get(bm['key'], bm['key'])
    return best, best_book

def get_odds_by_book(bookmakers, team_name):
    odds = {}
    for bm in bookmakers:
        if bm['key'] not in TARGET_BOOKS:
            continue
        for market in bm['markets']:
            if market['key'] == 'h2h':
                for outcome in market['outcomes']:
                    if outcome['name'] == team_name:
                        odds[BOOK_NAMES.get(bm['key'], bm['key'])] = outcome['price']
    return odds

def odds_color(price):
    if price is None:
        return '#333333'
    if price < -150:
        return '#1a1a6e'
    elif price < 0:
        return '#003087'
    elif price < 150:
        return '#1a5c1a'
    elif price < 300:
        return '#7a6a00'
    else:
        return '#7a1a1a'

def build_match_card(match):
    home = match['home_team']
    away = match['away_team']
    date = format_date(match['commence_time'])
    bookmakers = match['bookmakers']

    home_best, home_book = get_best_odds(bookmakers, home)
    away_best, away_book = get_best_odds(bookmakers, away)
    draw_best, draw_book = get_best_odds(bookmakers, 'Draw')

    home_by_book = get_odds_by_book(bookmakers, home)
    away_by_book = get_odds_by_book(bookmakers, away)
    draw_by_book = get_odds_by_book(bookmakers, 'Draw')

    def book_cells(odds_dict):
        cells = ''
        for book in ['FanDuel', 'DraftKings', 'BetMGM', 'BetRivers', 'Bovada']:
            price = odds_dict.get(book)
            if price:
                color = odds_color(price)
                cells += '<td class="odds-cell" style="background:' + color + '">' + format_odds(price) + '</td>'
            else:
                cells += '<td class="odds-cell" style="background:#1a1a1a">N/A</td>'
        return cells

    home_color = odds_color(home_best)
    away_color = odds_color(away_best)
    draw_color = odds_color(draw_best)

    return (
        '<div class="match-card">'
        '<div class="match-header">'
        '<span class="match-teams">' + home + ' vs ' + away + '</span>'
        '<span class="match-date">' + date + '</span>'
        '</div>'
        '<table class="odds-table">'
        '<thead><tr>'
        '<th class="left">OUTCOME</th>'
        '<th>BEST ODDS</th>'
        '<th>BEST BOOK</th>'
        '<th>FanDuel</th>'
        '<th>DraftKings</th>'
        '<th>BetMGM</th>'
        '<th>BetRivers</th>'
        '<th>Bovada</th>'
        '</tr></thead>'
        '<tbody>'
        '<tr>'
        '<td class="outcome-name">' + home + '</td>'
        '<td class="best-odds" style="background:' + home_color + '">' + (format_odds(home_best) if home_best else 'N/A') + '</td>'
        '<td class="best-book">' + home_book + '</td>'
        + book_cells(home_by_book) +
        '</tr>'
        '<tr>'
        '<td class="outcome-name">Draw</td>'
        '<td class="best-odds" style="background:' + draw_color + '">' + (format_odds(draw_best) if draw_best else 'N/A') + '</td>'
        '<td class="best-book">' + draw_book + '</td>'
        + book_cells(draw_by_book) +
        '</tr>'
        '<tr>'
        '<td class="outcome-name">' + away + '</td>'
        '<td class="best-odds" style="background:' + away_color + '">' + (format_odds(away_best) if away_best else 'N/A') + '</td>'
        '<td class="best-book">' + away_book + '</td>'
        + book_cells(away_by_book) +
        '</tr>'
        '</tbody>'
        '</table>'
        '</div>'
    )

def get_css():
    return """
        body { font-family: Arial, sans-serif; background: #0a0a0a; color: #ffffff; margin: 0; padding: 20px; }
        h1 { text-align: center; font-size: 26px; color: #ffffff; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #888; font-size: 13px; margin-bottom: 25px; }
        .container { max-width: 1100px; margin: 0 auto; }
        .match-card { background: #111111; border-radius: 8px; margin-bottom: 20px; overflow: hidden; border: 1px solid #222; }
        .match-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: #1a1a1a; border-bottom: 1px solid #333; }
        .match-teams { font-size: 16px; font-weight: bold; }
        .match-date { font-size: 12px; color: #888; }
        .odds-table { width: 100%; border-collapse: collapse; }
        th { background: #0f0f0f; padding: 10px 12px; text-align: center; font-size: 11px; color: #aaaaaa; letter-spacing: 1px; border-bottom: 1px solid #222; text-transform: uppercase; }
        th.left { text-align: left; }
        td { padding: 10px 12px; text-align: center; border-bottom: 1px solid #1a1a1a; font-size: 14px; }
        .outcome-name { text-align: left; font-weight: bold; font-size: 15px; padding-left: 20px; }
        .best-odds { font-weight: bold; font-size: 18px; border-radius: 4px; }
        .best-book { font-size: 12px; color: #aaa; }
        .odds-cell { font-weight: bold; font-size: 14px; }
        tr:hover { background: #151515; }
        .footer { text-align: center; color: #444; font-size: 11px; margin-top: 30px; padding-top: 15px; border-top: 1px solid #1a1a1a; }
        .live-badge { background: #c00; color: white; font-size: 10px; padding: 2px 6px; border-radius: 3px; margin-left: 8px; }
    """

def generate_epl_dashboard():
    print("Fetching EPL odds...")
    matches = get_epl_odds()

    if not matches:
        print("No matches found")
        return

    print("Found " + str(len(matches)) + " matches")
    cards = ''
    for match in matches:
        cards += build_match_card(match)

    html = (
        '<!DOCTYPE html><html><head>'
        '<title>Rugby Edge — EPL Odds Dashboard</title>'
        '<style>' + get_css() + '</style>'
        '</head><body><div class="container">'
        '<h1>RUGBY EDGE — EPL ODDS DASHBOARD</h1>'
        '<p class="subtitle">Live odds from FanDuel, DraftKings, BetMGM, BetRivers & Bovada | Best odds highlighted</p>'
        + cards +
        '<div class="footer">Rugby Edge | Odds updated in real time | Powered by The Odds API</div>'
        '</div></body></html>'
    )

    filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'epl_odds.html')
    with open(filepath, 'w') as f:
        f.write(html)

    print("Dashboard generated! Opening in browser...")
    webbrowser.open('file:///' + filepath)

generate_epl_dashboard()