import soccerdata as sd
import pandas as pd

print("Connecting to FBref...")

try:
    fbref = sd.FBref(leagues="ENG-Premier League", seasons="2425")
    print("Connected. Fetching player stats...")
    
    stats = fbref.read_player_season_stats(stat_type="standard")
    print("\nColumns available:")
    print(stats.columns.tolist())
    print("\nFirst 5 players:")
    print(stats.head())
    
except Exception as e:
    print("Error: " + str(e))