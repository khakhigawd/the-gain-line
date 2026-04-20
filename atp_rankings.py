import requests
import pandas as pd
import io

print("Loading ATP rankings and player names...")

players_r = requests.get('https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_players.csv')
players_df = pd.read_csv(io.StringIO(players_r.text), low_memory=False)
players_df['full_name'] = players_df['name_first'] + ' ' + players_df['name_last']

rankings_r = requests.get('https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_rankings_current.csv')
rankings_df = pd.read_csv(io.StringIO(rankings_r.text))

latest_date = rankings_df['ranking_date'].max()
print("Latest ranking date: " + str(latest_date))

current = rankings_df[rankings_df['ranking_date'] == latest_date].head(100)

merged = current.merge(
    players_df[['player_id', 'full_name', 'ioc']],
    left_on='player',
    right_on='player_id'
)

merged = merged[['rank', 'full_name', 'ioc', 'points']].sort_values('rank')

print("\nCurrent ATP Top 100:")
print(merged.to_string(index=False))

# Save to CSV for use in tennis matrix
merged.to_csv('atp_top100.csv', index=False)
print("\nSaved to atp_top100.csv")