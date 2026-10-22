"""
Skrypt do generowania rankingu strzelców na dany dzień.
Na razie działa na przykładowych danych.
"""

from src.scoring.engine import PlayerFeatures
from src.ranking.generator import generate_ranking, print_ranking


def get_sample_players():
    """Przykładowi gracze – później zastąpimy prawdziwymi danymi."""
    return [
        PlayerFeatures(
            player_id="97",
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
            player_id="29",
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
            player_id="97k",
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
    ]


def main():
    print("Generowanie rankingu strzelców NHL...")
    players = get_sample_players()
    ranking = generate_ranking(players, top_n=10)
    print_ranking(ranking)


if __name__ == "__main__":
    main()
