"""
Moduł do zapisywania, wczytywania i aktualizowania historii typów oraz wyników w projekcie NHL.
"""
import json
from datetime import datetime
from typing import List, Dict
from pathlib import Path

HISTORY_PATH = Path("data/history.json")


def load_history() -> List[Dict]:
    """Wczytuje historię typów z pliku JSON. Zwraca pustą listę w razie błędu lub braku pliku."""
    if not HISTORY_PATH.exists():
        return []
    
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Błąd wczytywania historii: {e}")
        return []


def save_prediction(ranking: List[Dict], date: str = None) -> bool:
    """Zapisuje dzisiejszy wygenerowany ranking do pliku historii."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = load_history()
    
    entry = {
        "date": date,
        "predictions": ranking,
        "results": None,
        "updated_weights": None
    }
    
    history = [h for h in history if h.get("date") != date]
    history.append(entry)
    
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Błąd zapisu historii: {e}")
        return False


def update_results(date: str, results: Dict[str, int]) -> bool:
    """Uzupełnia faktyczne wyniki goli dla danego dnia w historii."""
    history = load_history()
    updated = False
    
    for entry in history:
        if entry.get("date") == date:
            entry["results"] = results
            updated = True
            break
            
    if not updated:
        return False
    
    try:
        with open(HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Błąd aktualizacji wyników w historii: {e}")
        return False
      
