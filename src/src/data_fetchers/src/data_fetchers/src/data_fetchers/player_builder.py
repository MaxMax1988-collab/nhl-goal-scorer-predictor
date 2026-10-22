"""
Moduł odpowiedzialny za budowanie obiektów PlayerFeatures
na podstawie dostępnych danych.
Na razie działa na przykładowych / ręcznych danych.
Później podłączymy prawdziwe API.
"""

from typing import List
from src.scoring.engine import PlayerFeatures


def build_players_for_today() -> List[PlayerFeatures]:
    """
    Na razie zwraca przykładowych graczy.
    W przyszłości będzie pobierać prawdziwe dane.
    """
    
    # Przykładowi gracze (będziemy to rozbudowywać)
    players = [
        PlayerFeatures(
            player_id="8478402",
            name="Connor McDavid",
            team="EDM",
            line=1,
            pp_unit=1,
            recent_goals=0.67,
            recent_sog=3.2,
            residual=0.45,
            is_home=True,
            b2b=False,
            opponent_goalie_sv=0.910,
            matchup_quality=0.70,
            line_quality=0.95,
            context_score=0.80
        ),
        PlayerFeatures(
            player_id="8477934",
            name="Leon Draisaitl",
            team="EDM",
            line=1,
            pp_unit=1,
            recent_goals=0.89,
            recent_sog=3.5,
            residual=0.50,
            is_home=True,
            b2b=False,
            opponent_goalie_sv=0.910,
            matchup_quality=0.70,
            line_quality=0.95,
            context_score=0.80
        ),
        PlayerFeatures(
            player_id="8478493",
            name="Kirill Kaprizov",
            team="MIN",
            line=1,
            pp_unit=1,
            recent_goals=1.10,
            recent_sog=3.8,
            residual=0.55,
            is_home=False,
            b2b=False,
            opponent_goalie_sv=0.900,
            matchup_quality=0.65,
            line_quality=0.85,
            context_score=0.70
        ),
        PlayerFeatures(
            player_id="8479318",
            name="Auston Matthews",
            team="TOR",
            line=1,
            pp_unit=1,
            recent_goals=0.73,
            recent_sog=4.0,
            residual=0.40,
            is_home=True,
            b2b=False,
            opponent_goalie_sv=0.905,
            matchup_quality=0.60,
            line_quality=0.90,
            context_score=0.65
        ),
        PlayerFeatures(
            player_id="8477956",
            name="David Pastrnak",
            team="BOS",
            line=1,
            pp_unit=1,
            recent_goals=0.60,
            recent_sog=4.2,
            residual=0.35,
            is_home=True,
            b2b=False,
            opponent_goalie_sv=0.900,
            matchup_quality=0.68,
            line_quality=0.88,
            context_score=0.70
        ),
    ]
    
    return players
