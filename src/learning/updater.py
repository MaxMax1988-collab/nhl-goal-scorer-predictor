"""
Moduł aktualizacji wag (Updater) - samouczący się algorytm NHL.
"""
from typing import List, Dict
import yaml


def update_weights(predictions: List[Dict], actual_results: Dict[str, int]) -> Dict[str, int]:
    """
    Aktualizuje wagi w pliku config/weights.yaml na podstawie trafności predykcji.
    """
    try:
        with open("config/weights.yaml", "r", encoding="utf-8") as f:
            weights = yaml.safe_load(f)
    except Exception as e:
        print(f"Błąd odczytu wag: {e}")
        return {"hits": 0, "misses": 0}

    hits = 0
    misses = 0

    for pred in predictions:
        p_name = pred.get("player")
        goals = actual_results.get(p_name, 0)
        
        # Jeśli zawodnik strzelił gola - delikatnie zwiększamy wagi kluczowe
        if goals > 0:
            hits += 1
            weights["role_pp"] = round(min(0.45, weights.get("role_pp", 0.24) + 0.01), 3)
            weights["form"] = round(min(0.30, weights.get("form", 0.12) + 0.01), 3)
        else:
            misses += 1
            weights["role_pp"] = round(max(0.10, weights.get("role_pp", 0.24) - 0.005), 3)

    # Zapis zaktualizowanych wag do YAML
    try:
        with open("config/weights.yaml", "w", encoding="utf-8") as f:
            yaml.dump(weights, f, default_flow_style=False)
    except Exception as e:
        print(f"Błąd zapisu wag: {e}")

    return {"hits": hits, "misses": misses}
  
