"""
Moduł do zapisywania i wczytywania historii typów.
"""

import json
from datetime import datetime
from typing import List, Dict
from pathlib import Path


HISTORY_PATH = Path("data/history.json")


def load_history() -> List[Dict]:
    """Wczytuje historię typów."""
    if not HISTORY_PATH.exists():
        return []
    
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_prediction(ranking: List[Dict], date: str = None):
    """
    Zapisuje dzisiejszy ranking do historii.
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    history = load_history()
    
    entry = {
        "date": date,
        "predictions": ranking,
        "results": None,          # uzupełnimy po meczach
        "updated_weights": None
    }
    
    # Usuwamy stary wpis z tego samego dnia (jeśli istnieje)
    history = [h for h in history if h.get("date") != date]
    history.append(entry)
    
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    return True


def update_results(date: str, results: Dict[str, int]):
    """
    Uzupełnia wyniki dla danego dnia.
    results = {"Connor McDavid": 1, "Leon Draisaitl": 0, ...}
    """
    history = load_history()
    
    for entry in history:
        if entry.get("date") == date:
            entry["results"] = results
            break
    
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    return True
