"""
Skrypt do codziennego automatycznego generowania rankingu strzelców NHL i zapisu do historii.
"""
from src.data_fetchers.player_builder import build_players_for_today
from src.ranking.generator import generate_ranking, print_ranking
from src.utils.history import save_prediction

def main():
    print("📊 Generowanie codziennego rankingu strzelców NHL...")
    print("-" * 50)
    
    players = build_players_for_today()
    ranking = generate_ranking(players, top_n=10)
    print_ranking(ranking)
    
    # Automatyczny zapis do historii na potrzeby uczenia modelu
    save_prediction(ranking)
    print("💾 Zapisano dzisiejszy ranking do historii.")
    
    print("-" * 50)
    print("✅ Gotowe.")

if __name__ == "__main__":
    main()
    
