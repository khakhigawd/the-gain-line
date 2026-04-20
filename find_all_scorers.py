from rugbypy.player import *
from rugbypy.team import *
import pandas as pd
import time

# Super Rugby Pacific team IDs we confirmed
TEAMS = {
    '93b14fff': 'Crusaders',
    'ada90f2c': 'Hurricanes',
    'b302dfcf': 'Waratahs',
    '9f706321': 'Brumbies',
    'b6b6eba1': 'Queensland Reds',
    'f921cb8b': 'Highlanders',
    'b8b8b698': 'Fijian Drua',
    'ef5d2d5d': 'Moana Pasifika',
    '510fa4b4': 'Western Force',
    '32f13a5d': 'Melbourne Rebels',
}

def find_team_try_scorers(team_id, team_name):
    print("\nScanning " + team_name + "...")
    try:
        team_stats = fetch_team_stats(team_id=team_id)
        if team_stats is None or len(team_stats) == 0:
            print("  No data for " + team_name)
            return []

        # Get all match IDs for this team
        match_ids = team_stats['match_id'].dropna().unique().tolist()
        print("  Found " + str(len(match_ids)) + " matches")
        return match_ids
    except Exception as e:
        print("  Error: " + str(e))
        return []

def scan_all_teams():
    all_match_ids = []
    for team_id, team_name in TEAMS.items():
        match_ids = find_team_try_scorers(team_id, team_name)
        all_match_ids.extend(match_ids)
        time.sleep(1)

    unique_matches = list(set(all_match_ids))
    print("\n" + "="*50)
    print("Total unique Super Rugby matches found: " + str(len(unique_matches)))
    print("="*50)

    # Save match IDs to file for next step
    with open('match_ids.txt', 'w') as f:
        for mid in unique_matches:
            f.write(mid + '\n')

    print("\nMatch IDs saved to match_ids.txt")
    print("Next step: scan these matches for try scorers")

scan_all_teams()