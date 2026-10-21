from dataclasses import dataclass
from typing import Dict, List
import yaml


@dataclass
class PlayerFeatures:
    player_id: str
    name: str
    team: str
    line: int                    # 1, 2, 3, 4
    pp_unit: int                 # 1 = PP1, 2 = PP2, 0 = brak
    recent_goals: float          # średnia z ostatnich 5-8 meczów
    recent_sog: float            # średnia strzałów
    residual: float              # actual goals - xG
    is_home: bool
    b2b: bool
    opponent_goalie_sv: float
    matchup_quality: float       # 0.0 - 1.0
    line_quality: float          # 0.0 - 1.0
    context_score: float         # desperacja, bounce-back itp.
    is_l2_hot: bool = False
    is_l2_edge: bool = False


class GoalScorerEngine:
    def __init__(self, weights_path: str = "config/weights.yaml"):
        with open(weights_path, "r") as f:
            self.weights = yaml.safe_load(f)

    def calculate_score(self, p: PlayerFeatures) -> Dict:
        w = self.weights

        # 1. Forma (Hot Hand)
        form_score = (
            p.recent_goals * 0.6 +
            (p.recent_sog / 4.0) * 0.4
        )

        # 2. Rola / PP
        role_score = 0.0
        if p.pp_unit == 1:
            role_score = 1.0
        elif p.pp_unit == 2:
            role_score = 0.65
        else:
            role_score = 0.25

        if p.line == 1:
            role_score += 0.15
        elif p.line == 2:
            role_score += 0.08

        # 3. Matchup
        matchup_score = p.matchup_quality

        # 4. Jakość linii
        line_score = p.line_quality

        # 5. Residual
        residual_score = max(min(p.residual + 0.5, 1.5), -0.5)

        # 6. Hidden Edge
        hidden_edge = 0.0
        if p.residual > 0.3 and p.recent_sog > 3.0:
            hidden_edge = 0.7
        elif p.is_l2_hot or p.is_l2_edge:
            hidden_edge = 0.5

        # 7. Kontekst
        context = p.context_score
        if p.is_home:
            context += 0.15
        if p.b2b:
            context -= 0.20

        # Finalny score
        final_score = (
            w["form"] * form_score +
            w["role_pp"] * role_score +
            w["matchup"] * matchup_score +
            w["line_quality"] * line_score +
            w["residual"] * residual_score +
            w["hidden_edge"] * hidden_edge +
            w["context"] * context
        )

        # Bonusy Second Line
        if p.is_l2_edge:
            final_score *= 1.12
        if p.is_l2_hot:
            final_score *= 1.18

        return {
            "player": p.name,
            "team": p.team,
            "line": p.line,
            "score": round(final_score, 3),
            "annotations": self._get_annotations(p)
        }

    def _get_annotations(self, p: PlayerFeatures) -> List[str]:
        notes = []
        if p.is_l2_hot:
            notes.append("L2 Hot")
        if p.is_l2_edge:
            notes.append("L2 Edge")
        if p.pp_unit == 1:
            notes.append("PP1")
        if p.residual > 0.4:
            notes.append("Positive Residual")
        return notes
