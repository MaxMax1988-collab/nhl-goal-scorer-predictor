"""
Moduł historii Supabase bez buforowania, gwarantujący odczyt świeżych sekretów.
"""
from datetime import datetime
from typing import List, Dict
import streamlit as st
from supabase import create_client, Client

def get_supabase_client() -> Client:
    """Pobiera świeże sekrety i tworzy klienta bez keszowania."""
    url = st.secrets["SUPABASE_URL"].strip()
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)


def load_history() -> List[Dict]:
    """Wczytuje historię typów z Supabase."""
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
        
