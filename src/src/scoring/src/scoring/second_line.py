from typing import List
from .engine import PlayerFeatures


def detect_l2_edge(players: List[PlayerFeatures]) -> List[PlayerFeatures]:
    """
    Wykrywa Second Line Edge na podstawie prostych reguł.
    Modyfikuje flagi is_l2_edge i is_l2_hot.
    """
    # Grupujemy graczy według drużyny
    teams = {}
    for p in players:
        if p.team not in teams:
            teams[p.team] = []
        teams[p.team].append(p)

    for team, team_players in teams.items():
        # Szukamy L1 i L2
        l1 = [p for p in team_players if p.line == 1]
        l2 = [p for p in team_players if p.line == 2]

        if not l1 or not l2:
            continue

        # Średnia forma L1 vs L2
        avg_l1_goals = sum(p.recent_goals for p in l1) / len(l1)
        avg_l2_goals = sum(p.recent_goals for p in l2) / len(l2)

        avg_l1_sog = sum(p.recent_sog for p in l1) / len(l1)
        avg_l2_sog = sum(p.recent_sog for p in l2) / len(l2)

        avg_l1_residual = sum(p.residual for p in l1) / len(l1)
        avg_l2_residual = sum(p.residual for p in l2) / len(l2)

        # Reguła L2 Edge
        l2_has_edge = (
            avg_l2_goals >= avg_l1_goals * 0.85 or
            avg_l2_sog >= avg_l1_sog * 0.9 or
            avg_l2_residual > avg_l1_residual + 0.15
        )

        for p in l2:
            if l2_has_edge:
                p.is_l2_edge = True

            # L2 Hot – indywidualna forma
            if p.recent_goals >= 0.4 or p.residual > 0.35:
                p.is_l2_hot = True

    return players
