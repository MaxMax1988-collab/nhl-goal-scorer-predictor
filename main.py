from src.scoring.engine import PlayerFeatures
from src.ranking.generator import generate_ranking, print_ranking


def main():
    # Przykładowi gracze (na razie ręcznie)
    players = [
        PlayerFeatures(
            player_id="1",
            name="Matvei Michkov",
            team="PHI",
            line=2,
            pp_unit=1,
            recent_goals=0.55,
            recent_sog=3.8,
            residual=0.42,
            is_home=False,
            b2b=False,
            opponent_goalie_sv=0.900,
            matchup_quality=0.65,
            line_quality=0.70,
            context_score=0.50,
            is_l2_hot=True
        ),
        PlayerFeatures(
            player_id="2",
            name="Tage Thompson",
            team="BUF",
            line=1,
            pp_unit=1,
            recent_goals=0.48,
            recent_sog=3.5,
            residual=0.25,
            is_home=True,
            b2b=False,
            opponent_goalie_sv=0.905,
            matchup_quality=0.60,
            line_quality=0.80,
            context_score=0.55
        ),
        PlayerFeatures(
            player_id="3",
            name="Brady Tkachuk",
            team="FLA",
            line=1,
            pp_unit=1,
            recent_goals=0.50,
            recent_sog=4.1,
            residual=0.30,
            is_home=False,
            b2b=False,
            opponent_goalie_sv=0.910,
            matchup_quality=0.55,
            line_quality=0.85,
            context_score=0.60
        ),
    ]

    ranking = generate_ranking(players, top_n=10)
    print_ranking(ranking)


if __name__ == "__main__":
    main()
