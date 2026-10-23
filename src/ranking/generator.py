"""
Generator rankingu strzelców bramek NHL.
"""
from typing import List, Dict
from src.scoring.engine import PlayerFeatures, calculate_player_score, load_weights


def generate_ranking(players: List[PlayerFeatures], top_n: int = 10) -> List[Dict]:
    """
    Oblicza punkty (score) dla każdego gracza, przypisuje adnotacje i sortuje ranking.
    """
    weights = load_weights()
    ranked_players = []

    for player in players:
        score = calculate_player_score(player, weights)
        annotations = []

        # Dodatkowe adnotacje i wskaźniki
        if player.line == 1 and player.pp_unit == 1:
            annotations.append("Top Power Play & Line 1")
        elif player.line == 2 and player.pp_unit == 1:
            annotations.append("L2 Edge")
        
        if player.recent_goals >= 0.8:
            annotations.append("Hot Streak 🔥")
        
        if player.b2b:
            annotations.append("Back-to-Back ⚠️")

        ranked_players.append({
            "player_id": player.player_id,
            "player": player.name,
            "team": player.team,
            "line": player.line,
            "pp_unit": player.pp_unit,
            "score": score,
            "annotations": annotations
        })

    # Sortowanie malejąco po wyniku
    ranked_players.sort(key=lambda x: x["score"], reverse=True)
    return ranked_players[:top_n]


def print_ranking(ranking: List[Dict]) -> None:
    """Pomocnicza funkcja do wypisania rankingu w konsoli."""
    print("\n🏆 RANKING STRZELCÓW NHL NA DZIŚ:")
    print("=" * 60)
    for i, p in enumerate(ranking, 1):
        ann = f" [{', '.join(p['annotations'])}]" if p["annotations"] else ""
        print(f"{i:2d}. {p['player']:<22} ({p['team']}) | Linia: {p['line']} | PP: {p['pp_unit']} | Score: {p['score']:.3f}{ann}")
    print("=" * 60)
