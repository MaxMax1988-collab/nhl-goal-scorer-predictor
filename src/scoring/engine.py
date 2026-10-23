"""
Silnik punktacji (Scoring Engine) dla NHL Goal Scorer Predictor.
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
    """Oblicza końcowy wynik (score) dla danego zawodnika."""
    form_score = (player.recent_goals * 0.6) + (player.recent_sog * 0.1)
    
    role_pp_score = 1.0 if (player.line == 1 and player.pp_unit == 1) else (
        0.75 if player.pp_unit == 1 else (
            0.50 if player.line == 1 else 0.25
        )
    )
    
    matchup_score = player.matchup_quality * (1.0 - player.opponent_goalie_sv) * 10
    
    score = (
        form_score * weights.get("form", 0.12) +
        role_pp_score * weights.get("role_pp", 0.24) +
        matchup_score * weights.get("matchup", 0.15) +
        player.line_quality * weights.get("line_quality", 0.18) +
        player.residual * weights.get("residual", 0.09) +
        player.context_score * weights.get("context", 0.14)
    )
    
    return round(score, 3)
  
