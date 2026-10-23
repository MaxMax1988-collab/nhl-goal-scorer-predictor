"""
Generator rankingu strzelców bramek NHL.
"""
from typing import List, Dict
from src.scoring.engine import PlayerFeatures, calculate_player_score, load_weights


def generate_ranking(players: List[PlayerFeatures], top_n: int = 15) -> List[Dict]:
    """
    Oblicza punkty (score) dla każdego gracza, uwzględnia L2 Edge i sortuje ranking.
    """
    weights = load_weights()
    ranked_players = []

    for player in players:
        score = calculate_player_score(player, weights)
        annotations = []

        # Realistyczne adnotacje analityczne
        if player.line == 2 and player.pp_unit == 1:
            annotations.append("🔥 L2 Sweet Spot (PP1)")
        elif player.line == 1 and player.pp_unit == 1:
            annotations.append("Top Power Play & Line 1")
        elif player.line == 2:
            annotations.append("Linia 2 (Easy Matchup)")
        
        if player.recent_goals >= 0.7:
            annotations.append("Hot Streak 🔥")

        ranked_players.append({
            "player_id": player.player_id,
            "player": player.name,
            "team": player.team,
            "line": player.line,
            "pp_unit": player.pp_unit,
            "score": score,
            "annotations": annotations
        })

    # Sortowanie malejąco po wyniku punktowym
    ranked_players.sort(key=lambda x: x["score"], reverse=True)
    return ranked_players[:top_n]
    
