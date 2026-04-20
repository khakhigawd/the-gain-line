import pandas as pd
import requests
import io

print("Building ATP player profiles from 2024 data...")

url_2024 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv"
url_2023 = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2023.csv"

def load_data(url):
    r = requests.get(url)
    return pd.read_csv(io.StringIO(r.text))

try:
    df_2024 = load_data(url_2024)
    df_2023 = load_data(url_2023)
    df = pd.concat([df_2023, df_2024], ignore_index=True)
    
    print("Total matches loaded: " + str(len(df)))

    def get_player_surface_stats(player_name, surface=None):
        # Get matches where player won
        won = df[df['winner_name'] == player_name].copy()
        won['player_aces'] = won['w_ace']
        won['player_df'] = won['w_df']
        won['player_svpt'] = won['w_svpt']
        won['player_1stIn'] = won['w_1stIn']
        won['player_1stWon'] = won['w_1stWon']
        won['player_2ndWon'] = won['w_2ndWon']
        won['player_bpSaved'] = won['w_bpSaved']
        won['player_bpFaced'] = won['w_bpFaced']
        won['result'] = 1

        # Get matches where player lost
        lost = df[df['loser_name'] == player_name].copy()
        lost['player_aces'] = lost['l_ace']
        lost['player_df'] = lost['l_df']
        lost['player_svpt'] = lost['l_svpt']
        lost['player_1stIn'] = lost['l_1stIn']
        lost['player_1stWon'] = lost['l_1stWon']
        lost['player_2ndWon'] = lost['l_2ndWon']
        lost['player_bpSaved'] = lost['l_bpSaved']
        lost['player_bpFaced'] = lost['l_bpFaced']
        lost['result'] = 0

        cols = ['surface', 'tourney_name', 'result', 'player_aces', 'player_df',
                'player_svpt', 'player_1stIn', 'player_1stWon', 'player_2ndWon',
                'player_bpSaved', 'player_bpFaced']

        all_matches = pd.concat([won[cols], lost[cols]], ignore_index=True)

        if surface:
            all_matches = all_matches[all_matches['surface'] == surface]

        if len(all_matches) == 0:
            return None

        matches = len(all_matches)
        wins = all_matches['result'].sum()
        win_rate = round(wins / matches * 100, 1)
        avg_aces = round(all_matches['player_aces'].mean(), 1)
        avg_df = round(all_matches['player_df'].mean(), 1)
        
        # First serve percentage
        total_svpt = all_matches['player_svpt'].sum()
        total_1stIn = all_matches['player_1stIn'].sum()
        first_serve_pct = round(total_1stIn / total_svpt * 100, 1) if total_svpt > 0 else 0

        # Break points saved
        total_bpFaced = all_matches['player_bpFaced'].sum()
        total_bpSaved = all_matches['player_bpSaved'].sum()
        bp_save_pct = round(total_bpSaved / total_bpFaced * 100, 1) if total_bpFaced > 0 else 0

        return {
            'player': player_name,
            'surface': surface or 'All',
            'matches': matches,
            'wins': int(wins),
            'win_rate': win_rate,
            'avg_aces': avg_aces,
            'avg_df': avg_df,
            'first_serve_pct': first_serve_pct,
            'bp_save_pct': bp_save_pct
        }

    # Test with top ATP players
    players = [
        'Jannik Sinner',
        'Carlos Alcaraz',
        'Novak Djokovic',
        'Alexander Zverev',
        'Daniil Medvedev',
        'Casper Ruud',
        'Andrey Rublev',
        'Hubert Hurkacz',
        'Taylor Fritz',
        'Tommy Paul',
    ]

    print("\n" + "="*80)
    print("CLAY COURT STATS — Madrid Open Preview")
    print("="*80)
    print(f"{'PLAYER':<25} {'M':<5} {'WIN%':<8} {'ACES':<7} {'DF':<6} {'1ST SRV%':<10} {'BP SAV%'}")
    print("-"*80)

    for player in players:
        stats = get_player_surface_stats(player, 'Clay')
        if stats:
            print(f"{stats['player']:<25} {stats['matches']:<5} {stats['win_rate']:<8} {stats['avg_aces']:<7} {stats['avg_df']:<6} {stats['first_serve_pct']:<10} {stats['bp_save_pct']}")
        else:
            print(f"{player:<25} No clay data found")

    print("\n" + "="*80)
    print("ALL SURFACE STATS — Overall Form")
    print("="*80)
    print(f"{'PLAYER':<25} {'M':<5} {'WIN%':<8} {'ACES':<7} {'DF':<6} {'1ST SRV%':<10} {'BP SAV%'}")
    print("-"*80)

    for player in players:
        stats = get_player_surface_stats(player, None)
        if stats:
            print(f"{stats['player']:<25} {stats['matches']:<5} {stats['win_rate']:<8} {stats['avg_aces']:<7} {stats['avg_df']:<6} {stats['first_serve_pct']:<10} {stats['bp_save_pct']}")

    print("\nDone.")

except Exception as e:
    print("Error: " + str(e))
    import traceback
    traceback.print_exc()