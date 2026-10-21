from typing import List, Dict
from src.scoring.engine import GoalScorerEngine, PlayerFeatures
from src.scoring.second_line import detect_l2_edge


def generate_ranking(players: List[PlayerFeatures], top_n: int = 10) -> List[Dict]:
    """
    Generuje ranking strzelców na dany dzień.
    """
    # Najpierw wykrywamy Second Line Edge
    players = detect_l2_edge(players)

    # Inicjalizujemy silnik
    engine = GoalScorerEngine()

    # Liczymy score dla każdego gracza
    scored = []
    for p in players:
        result = engine.calculate_score(p)
        scored.append(result)

    # Sortujemy od najwyższego score
    scored.sort(key=lambda x: x["score"], reverse=True)

    # Zwracamy top N
    return scored[:top_n]


def print_ranking(ranking: List[Dict]):
    """
    Ładne wypisanie rankingu w konsoli.
    """
    print("\n=== RANKING STRZELCÓW ===\n")
    for i, player in enumerate(ranking, 1):
        annotations = ", ".join(player["annotations"]) if player["annotations"] else "-"
        print(f"{i}. {player['player']} ({player['team']}) | Linia {player['line']} | Score: {player['score']} | {annotations}")
