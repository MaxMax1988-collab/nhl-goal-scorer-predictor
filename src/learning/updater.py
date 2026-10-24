"""
Moduł aktualizacji wag (Updater) - zintegrowany z Supabase dla NHL.
"""
from typing import List, Dict
import streamlit as st
from supabase import create_client

def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def load_weights() -> Dict[str, float]:
    """
    Pobiera aktualne wagi z tabeli nhl_weights w Supabase.
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("nhl_weights").select("weights").eq("id", 1).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["weights"]
    except Exception as e:
        print(f"Błąd pobierania wag z Supabase: {e}")
    
    # Fallback domyślny, gdyby baza nie odpowiedziała
    return {
        "form": 0.12,
        "role_pp": 0.19,
        "matchup": 0.15,
        "line_quality": 0.18,
        "residual": 0.09,
        "hidden_edge": 0.08,
        "context": 0.14
    }

def update_weights(predictions: List[Dict], actual_results: Dict[str, int]) -> Dict[str, int]:
    """
    Aktualizuje wagi w tabeli nhl_weights w Supabase na podstawie trafności predykcji.
    """
    weights = load_weights()
    hits = 0
    misses = 0

    for pred in predictions:
        p_name = pred.get("player")
        goals = actual_results.get(p_name, 0)
        
        # Jeśli zawodnik strzelił gola - zwiększamy wagi kluczowe
        if goals > 0:
            hits += 1
            weights["role_pp"] = round(min(0.45, weights.get("role_pp", 0.19) + 0.01), 3)
            weights["form"] = round(min(0.30, weights.get("form", 0.12) + 0.01), 3)
        else:
            misses += 1
            weights["role_pp"] = round(max(0.10, weights.get("role_pp", 0.19) - 0.005), 3)

    # Zapis zaktualizowanych wag z powrotem do Supabase
    try:
        supabase = get_supabase_client()
        supabase.table("nhl_weights").update({"weights": weights}).eq("id", 1).execute()
    except Exception as e:
        print(f"Błąd zapisu wag do Supabase: {e}")

    return {"hits": hits, "misses": misses}
    
