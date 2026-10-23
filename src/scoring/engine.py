"""
Silnik punktacji (Scoring Engine) dla NHL Goal Scorer Predictor - wersja zoptymalizowana analitycznie.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import yaml


@dataclass
class PlayerFeatures:
    player_id: str
    name: str
    team: str
    line: int
    pp_unit: int
    recent_goals: float
    recent_sog: float
    residual: float
    is_home: bool
    b2b: bool
    opponent_goalie_sv: float
    matchup_quality: float
    line_quality: float
    context_score: float


def load_weights() -> Dict[str, float]:
    """Wczytuje wagi z pliku config/weights.yaml."""
    try:
        with open("config/weights.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Błąd wczytywania wag, używam domyślnych: {e}")
        return {
            "form": 0.12,
            "role_pp": 0.24,
            "matchup": 0.15,
            "line_quality": 0.18,
            "residual": 0.09,
            "hidden_edge": 0.08,
            "context": 0.14
        }


def calculate_player_score(player: PlayerFeatures, weights: Dict[str, float]) -> float:
    """
    Oblicza końcowy wynik (score) dla danego zawodnika z uwzględnieniem 
    realnej dynamiki matchupów (faworyzowanie L2 z dostępem do PP).
    """
    form_score = (player.recent_goals * 0.6) + (player.recent_sog * 0.1)
    
    # REALISTYCZNA MATRYCA ROLI I PP (Z uwzględnieniem przewagi L2):
    # - L1 + PP1 = Klasyczny wybór (mocny, ale obciążony trudnym rywalem) -> 0.95
    # - L2 + PP1 = Analityczna perełka (słabszy obrońca rywala 5v5 + PP1) -> 1.0 (Najwyższa wartość!)
    # - L1 + PP2 = 0.70
    # - L2 + PP2 = 0.60
    if player.line == 2 and player.pp_unit == 1:
        role_pp_score = 1.00  # Premia za "L2 Sweet Spot"
    elif player.line == 1 and player.pp_unit == 1:
        role_pp_score = 0.95
    elif player.line == 1 and player.pp_unit == 2:
        role_pp_score = 0.70
    elif player.line == 2 and player.pp_unit == 2:
        role_pp_score = 0.60
    else:
        role_pp_score = 0.30

    # Modyfikator matchupu: Jeśli gracz jest w L2, dodajemy mu bonus za unikanie głównej pary obrońców
    line_matchup_multiplier = 1.15 if player.line == 2 else 1.00
    
    matchup_score = player.matchup_quality * (1.0 - player.opponent_goalie_sv) * 10 * line_matchup_multiplier
    
    score = (
        form_score * weights.get("form", 0.12) +
        role_pp_score * weights.get("role_pp", 0.24) +
        matchup_score * weights.get("matchup", 0.15) +
        player.line_quality * weights.get("line_quality", 0.18) +
        player.residual * weights.get("residual", 0.09) +
        player.context_score * weights.get("context", 0.14)
    )
    
    return round(score, 3)
    
