"""
Moduł do obsługi bazy Supabase z poprawną autoryzacją kluczy i nagłówków.
"""
from datetime import datetime
from typing import List, Dict
import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
    """Inicjalizuje i buforuje klienta Supabase z poprawnymi danymi uwierzytelniającymi."""
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)


def load_history() -> List[Dict]:
    """Wczytuje historię typów bezpośrednio z tabeli nhl_history w Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("nhl_history").select("*").order("date", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Błąd wczytywania historii z Supabase: {e}")
        return []


def save_prediction(ranking: List[Dict], date: str = None) -> bool:
    """Zapisuje lub aktualizuje ranking w bazie Supabase."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        supabase = get_supabase_client()
        
        # Sprawdzamy, czy wpis istnieje
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
        st.error(f"Błąd zapisu historii do Supabase: {e}")
        return False


def update_results(date: str, results: Dict[str, int]) -> bool:
    """Aktualizuje wyniki goli w bazie Supabase."""
    try:
        supabase = get_supabase_client()
        supabase.table("nhl_history").update({"results": results}).eq("date", date).execute()
        return True
    except Exception as e:
        st.error(f"Błąd aktualizacji wyników w Supabase: {e}")
        return False
        
