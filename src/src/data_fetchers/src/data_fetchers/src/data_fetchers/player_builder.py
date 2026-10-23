from datetime import datetime
from typing import List
import requests
from src.scoring.engine import PlayerFeatures


def fetch_todays_schedule() -> List[dict]:
    """Pobiera dzisiejszy terminarz meczów NHL z oficjalnego API webowego."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api-web.nhle.com/v1/schedule/{today_str}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            for game_week in data.get("gameWeek", []):
                if game_week.get("date") == today_str:
                    return game_week.get("games", [])
        return []
    except Exception as e:
        print(f"Błąd podczas pobierania terminarza NHL: {e}")
        return []


def get_fallback_players() -> List[PlayerFeatures]:
    """Zwraca bezpieczną listę testową zawodników w przypadku braku meczów dzisiaj."""
    return [
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


def build_players_for_today() -> List[PlayerFeatures]:
    """
    Buduje listę obiektów PlayerFeatures na dany dzień.
    Pobiera mecze z oficjalnego API NHL i przetwarza je.
    """
    games = fetch_todays_schedule()
    
    if not games:
        print("Brak dzisiejszych meczów w API NHL – uruchomiono tryb awaryjny (fallback).")
        return get_fallback_players()

    players = []
    
    # Przetwarzanie spotkań z oficjalnego harmonogramu NHL
    for game in games:
        home_team = game.get("homeTeam", {}).get("abbrev", "HOM")
        away_team = game.get("awayTeam", {}).get("abbrev", "AWY")
        
        # W kolejnym etapie w tym miejscu podepniemy dynamiczne pobieranie rosterów 
        # dla konkretnych spotkań z endpointów klubowych. 
        # Na ten moment funkcja poprawnie weryfikuje harmonogram live.
        
    # Jeśli API zwróciło mecze, ale nie zdążyliśmy rozebrać rosterów na czynniki pierwsze,
    # jako zabezpieczenie zwracamy na razie fallback, aby interfejs zawsze coś wyświetlił.
    if not players:
        return get_fallback_players()

    return players
    
