"""
Moduł do zapisywania, wczytywania i aktualizowania historii typów oraz wyników w projekcie NHL (Supabase).
"""
from datetime import datetime
from typing import List, Dict
import streamlit as st
from supabase import create_client

def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


def load_history() -> List[Dict]:
    """Wczytuje historię typów z tabeli nhl_history w Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("nhl_history").select("*").order("date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Błąd wczytywania historii z Supabase: {e}")
        return []


def save_prediction(ranking: List[Dict], date: str = None) -> bool:
    """Zapisuje lub aktualizuje ranking dla danego dnia w Supabase w sposób w pełni kontrolowany."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        supabase = get_supabase_client()
        
        # Sprawdzamy, czy wpis dla tej daty już istnieje w bazie
        existing = supabase.table("nhl_history").select("date").eq("date", date).execute()
        
        if existing.data:
            # Jeśli istnieje, aktualizujemy tylko predykcje
            response = supabase.table("nhl_history").update({"predictions": ranking}).eq("date", date).execute()
        else:
            # Jeśli nie istnieje, wstawiamy nowy rekord
            payload = {
                "date": date,
                "predictions": ranking,
                "results": None
            }
            response = supabase.table("nhl_history").insert(payload).execute()
            
        return True
    except Exception as e:
        st.error(f"Błąd zapisu historii do Supabase: {e}")
        return False


def update_results(date: str, results: Dict[str, int]) -> bool:
    """Uzupełnia faktyczne wyniki goli dla danego dnia w historii w Supabase."""
    try:
        supabase = get_supabase_client()
        supabase.table("nhl_history").update({"results": results}).eq("date", date).execute()
        return True
    except Exception as e:
        st.error(f"Błąd aktualizacji wyników w historii Supabase: {e}")
        return False
        
