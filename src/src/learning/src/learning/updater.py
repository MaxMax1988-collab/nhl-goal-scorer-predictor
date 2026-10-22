from typing import List, Dict
import yaml
from pathlib import Path


def update_weights(
    predictions: List[Dict],
    actual_goals: Dict[str, int],
    weights_path: str = "config/weights.yaml",
    learning_rate: float = 0.02
):
    """
    Prosta aktualizacja wag na podstawie wyników.
    
    predictions: lista typów z generate_ranking
    actual_goals: dict {player_name: liczba_goli}
    """
    with open(weights_path, "r") as f:
        weights = yaml.safe_load(f)

    # Prosta logika: jeśli gracz z wysokim score nie strzelił → lekko obniżamy wagi formy i residual
    # Jeśli gracz z niskim score strzelił → podnosimy residual i hidden_edge

    hits = 0
    misses = 0

    for pred in predictions:
        name = pred["player"]
        score = pred["score"]
        goals = actual_goals.get(name, 0)

        if goals > 0:
            hits += 1
            # Gracz strzelił – wzmacniamy cechy, które miały wysoki wpływ
            if score > 0.7:
                weights["form"] = min(weights["form"] + learning_rate * 0.3, 0.25)
                weights["residual"] = min(weights["residual"] + learning_rate * 0.4, 0.15)
        else:
            misses += 1
            # Gracz nie strzelił mimo wysokiego score
            if score > 0.75:
                weights["form"] = max(weights["form"] - learning_rate * 0.2, 0.08)
                weights["matchup"] = max(weights["matchup"] - learning_rate * 0.15, 0.10)

    # Normalizacja wag (żeby suma ≈ 1.0)
    total = sum(weights.values())
    for k in weights:
        weights[k] = round(weights[k] / total, 3)

    # Zapisujemy zaktualizowane wagi
    with open(weights_path, "w") as f:
        yaml.dump(weights, f, default_flow_style=False)

    return {
        "hits": hits,
        "misses": misses,
        "new_weights": weights
    }
