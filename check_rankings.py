import requests
import pandas as pd
import io

print("Checking current rankings from 2026 match data...")

r = requests.get('https://stats.tennismylife.org/data/2026.csv')
df = pd.read_csv(io.StringIO(r.text), low_memory=False)
df['tourney_date'] = pd.to_numeric(df['tourney_date'], errors='coerce')
df = df.sort_values('tourney_date', ascending=False)

rankings = {}
for _, row in df.iterrows():
    w = str(row['winner_name'])
    l = str(row['loser_name'])
    if w not in rankings and str(row['winner_rank']) != 'nan':
        try:
            rankings[w] = int(float(row['winner_rank']))
        except:
            pass
    if l not in rankings and str(row['loser_rank']) != 'nan':
        try:
            rankings[l] = int(float(row['loser_rank']))
        except:
            pass

sorted_r = sorted(rankings.items(), key=lambda x: x[1])
print("Total players with current rankings: " + str(len(sorted_r)))
print()
print("ATP Top 30 from 2026 match data:")
for name, rank in sorted_r[:30]:
    print("#" + str(rank) + " " + name)

# Check for Katie Boulter and Eva Lys in WTA data
print()
r2 = requests.get('https://raw.githubusercontent.com/JeffSackmann/tennis_wta/master/wta_matches_2024.csv')
df2 = pd.read_csv(io.StringIO(r2.text), low_memory=False)
for player in ['Katie Boulter', 'Eva Lys']:
    matches = df2[(df2['winner_name'] == player) | (df2['loser_name'] == player)]
    print(player + " — matches in WTA 2024 data: " + str(len(matches)))