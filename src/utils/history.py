"""
Moduł diagnostyczny do weryfikacji połączenia z Supabase.
"""
from datetime import datetime
from typing import List, Dict
import streamlit as st
from supabase import create_client

def get_supabase_client():
    """Testuje i zwraca klienta Supabase, wyświetlając status w razie problemów."""
    try:
        url = st.secrets.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY")
        
        if not url or not key:
            st.warning("⚠️ Diagnostyka Supabase: Brak skonfigurowanego `SUPABASE_URL` lub `SUPABASE_KEY` w Streamlit Secrets.")
            return None
            
        return create_client(url, key)
    except Exception as e:
        st.error(f"⚠️ Diagnostyka Supabase - Błąd inicjalizacji klienta: {e}")
        return None


def load_history() -> List[Dict]:
    """Wczytuje historię z pełną diagnostyką błędu 401."""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return []
            
        response = supabase.table("nhl_history").select("*").order("date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        # Wyświetlamy jasny komunikat na ekranie, żebyśmy wiedzieli co jest grane
        err_str = str(e)
        if "401" in err_str or "Invalid API key" in err_str:
            st.error("🔑 **Błąd 401 Supabase:** Klucz API (`SUPABASE_KEY`) jest odrzucany przez serwer. Sprawdź, czy w Streamlit Secrets nie ma literówki lub zbędnych spacji.")
        else:
            st.error(f"⚠️ Błąd połączenia z bazą Supabase: {e}")
        return []


def save_prediction(ranking: List[Dict], date: str = None) -> bool:
    """Bezpieczny zapis z obsługą diagnostyki."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
        
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False
            
        existing = supabase.table("nhl_history").select("date").eq("date", date).execute()
        
        if existing.data:
            supabase.table("nhl_history").update({"predictions": ranking}).eq("date", date).execute()
        else:
            payload = {
                "date": date,
                "predictions": ranking,
                "results": None
            }
            supabase.table("nhl_history").insert(payload).execute()
        return True
    except Exception as e:
        print(f"Błąd zapisu: {e}")
        return False


def update_results(date: str, results: Dict[str, int]) -> bool:
    """Bezpieczna aktualizacja wyników."""
    try:
        supabase = get_supabase_client()
        if not supabase:
            return False
        supabase.table("nhl_history").update({"results": results}).eq("date", date).execute()
        return True
    except Exception as e:
        print(f"Błąd aktualizacji: {e}")
        return False
        
