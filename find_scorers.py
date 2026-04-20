from rugbypy.player import *
import pandas as pd

PLAYER_IDS = {
    # Crusaders
    '4bb2a971': 'Leicester Faingaanuku',
    '8cf8cdd3': 'Will Jordan',
    'fd886e94': 'David Havili',
    # Hurricanes
    'eef777b0': 'Jordie Barrett',
    '67661a18': 'Ardie Savea',
    'be38fbd8': 'Kini Naholo',
    # Blues
    '012b0dd1': 'Mark Telea',
    '47bc6611': 'Hoskins Sotutu',
    'bf368581': 'Rieko Ioane',
    'ad18f2af': 'Akira Ioane',
    # Brumbies
    'd110c304': 'Len Ikitau',
    'f87eaf84': 'Pete Samu',
    '22ca90cf': 'Tom Banks',
    '8636b7b6': 'Scott Penny',
    # Highlanders
    'cffe8169': 'Tomas Aoake',
    '07c2b2e1': 'James Lentjes',
    '781cbbb1': 'Marty Banks',
    # Reds
    '6cce8506': 'Matt Faessler',
    '5548': 'Liam Wright',
    # Waratahs
    '24616539': 'Jed Holloway',
}

def get_super_rugby_tries(player_id, player_name):
    try:
        stats = fetch_player_stats(player_id=player_id)
        super_rugby = stats[stats['competition'].str.contains('Super', case=False, na=False)]
        if len(super_rugby) == 0:
            return None
        total_tries = super_rugby['tries'].sum()
        games = len(super_rugby)
        team = super_rugby['team'].iloc[-1]
        last5 = super_rugby.tail(5)
        last5_tries = last5['tries'].sum()
        return {
            'name': player_name,
            'team': team,
            'games': games,
            'total_tries': int(total_tries) if not pd.isna(total_tries) else 0,
            'last5_tries': int(last5_tries) if not pd.isna(last5_tries) else 0,
            'tries_per_game': round(total_tries / games, 2) if games > 0 else 0
        }
    except:
        return None

print("\nFetching Super Rugby try scoring data...\n")
print(f"{'PLAYER':<25} {'TEAM':<25} {'GAMES':<8} {'TOTAL TRIES':<14} {'LAST 5':<10} {'PER GAME'}")
print("-" * 95)

results = []
for pid, name in PLAYER_IDS.items():
    data = get_super_rugby_tries(pid, name)
    if data:
        results.append(data)
        print(f"{data['name']:<25} {data['team']:<25} {data['games']:<8} {data['total_tries']:<14} {data['last5_tries']:<10} {data['tries_per_game']}")

print("\nDone.")