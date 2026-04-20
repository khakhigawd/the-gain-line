from rugbypy.player import *
import pandas as pd
import time
import os

# Load match IDs
with open('match_ids.txt', 'r') as f:
    match_ids = [line.strip() for line in f.readlines()]

print("Loaded " + str(len(match_ids)) + " match IDs")
print("Scanning player database for Super Rugby try scorers...\n")

# Fetch all players
print("Loading full player database...")
all_players = fetch_all_players()
total = len(all_players)
print("Total players in database: " + str(total))

# We'll scan players in batches and check if they have Super Rugby stats
results = []
checked = 0
found = 0

print("\nScanning players for Super Rugby try scoring data...")
print("This will take a while — checking " + str(total) + " players\n")

for _, player_row in all_players.iterrows():
    player_id = player_row['player_id']
    player_name = player_row['player_name']
    checked += 1

    if checked % 100 == 0:
        print("Checked " + str(checked) + "/" + str(total) + " players — Found " + str(found) + " scorers so far...")

    try:
        stats = fetch_player_stats(player_id=player_id)
        super_rugby = stats[stats['competition'].str.contains('Super', case=False, na=False)]

        if len(super_rugby) == 0:
            continue

        total_tries = super_rugby['tries'].sum()
        if pd.isna(total_tries) or total_tries == 0:
            continue

        games = len(super_rugby)
        team = super_rugby['team'].iloc[-1]
        last5 = super_rugby.tail(5)
        last5_tries = last5['tries'].sum()
        tries_per_game = round(total_tries / games, 2)

        results.append({
            'player_id': player_id,
            'name': player_name,
            'team': team,
            'games': games,
            'total_tries': int(total_tries),
            'last5_tries': int(last5_tries) if not pd.isna(last5_tries) else 0,
            'tries_per_game': tries_per_game
        })
        found += 1
        time.sleep(0.3)

    except:
        continue

# Save results
df = pd.DataFrame(results)
df = df.sort_values('tries_per_game', ascending=False)
df.to_csv('super_rugby_scorers.csv', index=False)

print("\n" + "="*60)
print("SCAN COMPLETE")
print("="*60)
print("Players checked: " + str(checked))
print("Try scorers found: " + str(found))
print("\nTop 20 Super Rugby Try Scorers:")
print(df.head(20).to_string(index=False))
print("\nFull results saved to super_rugby_scorers.csv")