"""
Skrypt do generowania rankingu strzelców na dany dzień.
"""

from src.data_fetchers.player_builder import build_players_for_today
from src.ranking.generator import generate_ranking, print_ranking


def main():
    print("Generowanie rankingu strzelców NHL...")
    print("-" * 40)
    
    players = build_players_for_today()
    ranking = generate_ranking(players, top_n=10)
    print_ranking(ranking)
    
    print("-" * 40)
    print("Gotowe.")


if __name__ == "__main__":
    main()
