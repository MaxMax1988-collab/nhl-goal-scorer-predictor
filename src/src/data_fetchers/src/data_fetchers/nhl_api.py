"""
Moduł do pobierania danych z oficjalnego NHL API.
Na razie podstawowe funkcje: schedule i box score.
"""

import requests
from datetime import datetime
from typing import List, Dict, Optional


BASE_URL = "https://api-web.nhle.com/v1"


def get_schedule(date: str = None) -> List[Dict]:
    """
    Pobiera listę meczów na dany dzień.
    date format: YYYY-MM-DD
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    url = f"{BASE_URL}/schedule/{date}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        games = []
        for week in data.get("gameWeek", []):
            for game in week.get("games", []):
                games.append({
                    "game_id": game.get("id"),
                    "home_team": game.get("homeTeam", {}).get("abbrev"),
                    "away_team": game.get("awayTeam", {}).get("abbrev"),
                    "start_time": game.get("startTimeUTC"),
                    "status": game.get("gameState")
                })
        return games
    except Exception as e:
        print(f"Błąd pobierania schedule: {e}")
        return []


def get_boxscore(game_id: int) -> Optional[Dict]:
    """
    Pobiera box score konkretnego meczu.
    """
    url = f"{BASE_URL}/gamecenter/{game_id}/boxscore"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Błąd pobierania boxscore: {e}")
        return None


def get_team_roster(team_abbrev: str) -> List[Dict]:
    """
    Pobiera aktualny skład drużyny.
    """
    url = f"{BASE_URL}/roster/{team_abbrev}/current"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        players = []
        for position in ["forwards", "defensemen", "goalies"]:
            for p in data.get(position, []):
                players.append({
                    "id": p.get("id"),
                    "name": f"{p.get('firstName', {}).get('default', '')} {p.get('lastName', {}).get('default', '')}".strip(),
                    "position": p.get("positionCode"),
                    "number": p.get("sweaterNumber")
                })
        return players
    except Exception as e:
        print(f"Błąd pobierania rosteru: {e}")
        return []
