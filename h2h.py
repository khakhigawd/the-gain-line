import pandas as pd
import requests
import io

print("Loading match data for H2H...")

url_2024 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv"
url_2023 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2023.csv"
url_2022 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2022.csv"
url_2021 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2021.csv"
url_2020 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2020.csv"

def load_data(url):
    r = requests.get(url)
    return pd.read_csv(io.StringIO(r.text))

def get_h2h(player1, player2, df):
    p1_wins = df[(df['winner_name'] == player1) & (df['loser_name'] == player2)]
    p2_wins = df[(df['winner_name'] == player2) & (df['loser_name'] == player1)]

    total = len(p1_wins) + len(p2_wins)

    if total == 0:
        return None

    print("\n" + "="*60)
    print(player1 + " vs " + player2)
    print("="*60)
    print("Overall H2H: " + player1 + " leads " + str(len(p1_wins)) + "-" + str(len(p2_wins)))

    # Surface breakdown
    for surface in ['Clay', 'Hard', 'Grass']:
        p1_surface = len(p1_wins[p1_wins['surface'] == surface])
        p2_surface = len(p2_wins[p2_wins['surface'] == surface])
        if p1_surface + p2_surface > 0:
            print(surface + ": " + str(p1_surface) + "-" + str(p2_surface))

    # Recent meetings
    all_meetings = pd.concat([
        p1_wins[['tourney_date', 'tourney_name', 'surface', 'round', 'winner_name', 'loser_name', 'score']],
        p2_wins[['tourney_date', 'tourney_name', 'surface', 'round', 'winner_name', 'loser_name', 'score']]
    ]).sort_values('tourney_date', ascending=False)

    print("\nRecent meetings:")
    for _, match in all_meetings.head(5).iterrows():
        print("  " + str(match['tourney_date'])[:4] + " " +
              str(match['tourney_name']) + " (" + str(match['surface']) + ") — " +
              str(match['winner_name']) + " def. " + str(match['loser_name']) +
              " " + str(match['score']))

    return {
        'p1': player1,
        'p2': player2,
        'p1_wins': len(p1_wins),
        'p2_wins': len(p2_wins),
        'total': total
    }

# Load data
dfs = []
for url in [url_2020, url_2021, url_2022, url_2023, url_2024]:
    dfs.append(load_data(url))
df = pd.concat(dfs, ignore_index=True)
print("Loaded " + str(len(df)) + " matches")

# Test some Madrid Open relevant matchups
matchups = [
    ('Carlos Alcaraz', 'Jannik Sinner'),
    ('Carlos Alcaraz', 'Novak Djokovic'),
    ('Jannik Sinner', 'Alexander Zverev'),
    ('Carlos Alcaraz', 'Alexander Zverev'),
    ('Novak Djokovic', 'Alexander Zverev'),
]

for p1, p2 in matchups:
    get_h2h(p1, p2, df)