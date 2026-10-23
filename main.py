"""
Główny skrypt uruchomieniowy projektu NHL Goal Scorer Predictor.
"""
from src.data_fetchers.player_builder import build_players_for_today
from src.ranking.generator import generate_ranking, print_ranking

def main():
    print("🚀 Uruchamianie predykcji strzelców NHL...")
    print("-" * 50)
    
    players = build_players_for_today()
    ranking = generate_ranking(players, top_n=10)
    print_ranking(ranking)
    
    print("-" * 50)
    print("✅ Gotowe.")

if __name__ == "__main__":
    main()
    
