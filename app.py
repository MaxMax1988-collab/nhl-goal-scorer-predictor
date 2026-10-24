import streamlit as st
from datetime import datetime
import requests
from src.data_fetchers.player_builder import build_players_for_today
from src.ranking.generator import generate_ranking
from src.learning.updater import update_weights, load_weights
from src.utils.history import load_history, update_results, save_prediction

st.set_page_config(
    page_title="NHL Goal Scorer Predictor",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 NHL Goal Scorer Predictor")
st.markdown("Autonomiczny, samouczący się system predykcji strzelców NHL")

# --- Sidebar ---
st.sidebar.header("Ustawienia")
top_n = st.sidebar.slider("Ile graczy pokazać", 5, 15, 10)

# --- Automatyczne pobieranie faktycznych goli z API NHL dla rozliczenia ---
def fetch_actual_goals_for_date(date_str: str) -> dict:
    """Automatycznie pobiera faktyczne gole zawodników z zakończonych meczów w danym dniu z API NHL."""
    url = f"https://api-web.nhle.com/v1/schedule/{date_str}"
    actual_goals = {}
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            games = []
            for gw in data.get("gameWeek", []):
                if gw.get("date") == date_str:
                    games = gw.get("games", [])
            
            for game in games:
                game_id = game.get("id")
                if game_id and game.get("gameState") in ["OFF", "FINAL"]:
                    box_url = f"https://api-web.nhle.com/v1/gamecenter/{game_id}/boxscore"
                    box_res = requests.get(box_url, timeout=4)
                    if box_res.status_code == 200:
                        box_data = box_res.json()
                        for team_type in ["homeTeam", "awayTeam"]:
                            players_stats = box_data.get("playerByGameStats", {}).get(team_type, {}).get("forwards", [])
                            for p_stat in players_stats:
                                p_name = f"{p_stat.get('name', {}).get('default', '')}".strip()
                                goals = p_stat.get("goals", 0)
                                if p_name:
                                    actual_goals[p_name] = goals
    except Exception as e:
        print(f"Błąd automatycznego pobierania wyników: {e}")
        
    return actual_goals

# --- Zakładki aplikacji ---
tab1, tab2 = st.tabs(["📊 Ranking i Typy", "🎯 Automatyczne Rozliczanie i Nauka"])

with tab1:
    st.header("Ranking na dziś")
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Inicjalizacja stanu sesji i pobieranie dzisiejszego rankingu z Supabase, jeśli istnieje
    if "persistent_ranking" not in st.session_state:
        history = load_history()
        today_entry = next((h for h in history if h.get("date") == today_str), None)
        if today_entry:
            st.session_state["persistent_ranking"] = today_entry.get("predictions", [])
        elif history:
            st.session_state["persistent_ranking"] = history[0].get("predictions", [])
        else:
            st.session_state["persistent_ranking"] = []

    if st.button("Generuj nowy ranking na dziś", type="primary"):
        with st.spinner("Pobieram składy i obliczam model analityczny..."):
            players = build_players_for_today()
            ranking = generate_ranking(players, top_n=top_n)
            
            st.session_state["persistent_ranking"] = ranking
            save_prediction(ranking, today_str)
            st.success("Nowy ranking został wygenerowany i zapisany w Supabase!")

    # Wyświetlanie aktualnego / trwałego rankingu
    if "persistent_ranking" in st.session_state and st.session_state["persistent_ranking"]:
        current_ranking = st.session_state["persistent_ranking"]
        
        for i, player in enumerate(current_ranking, 1):
            annotations = " | ".join(player["annotations"]) if player["annotations"] else "—"
            
            col1, col2, col3, col4 = st.columns([1, 3, 2, 3])
            with col1:
                st.markdown(f"**{i}.**")
            with col2:
                st.markdown(f"**{player['player']}** ({player['team']})")
            with col3:
                st.markdown(f"Linia {player['line']} | Score: `{player['score']}`")
            with col4:
                st.caption(annotations)
            
            st.divider()
    else:
        st.info("Brak aktywnego rankingu na dzisiaj. Kliknij powyższy przycisk, aby wygenerować typy.")

    # --- Aktualne wagi z Supabase ---
    st.header("Aktualne wagi systemu")
    try:
        weights = load_weights()
        cols = st.columns(len(weights))
        for i, (key, value) in enumerate(weights.items()):
            cols[i].metric(key, f"{value:.2f}")
    except Exception as e:
        st.error(f"Nie udało się wczytać wag z Supabase: {e}")

with tab2:
    st.header("🎯 Automatyczne Rozliczanie Typów i Uczenie Modelu")
    
    history = load_history()
    pending_history = [h for h in history if h.get("results") is None]

    if not pending_history:
        st.info("Brak nierozliczonych historii w bazie Supabase. System czeka na zakończenie meczów.")
    else:
        dates_to_settle = [h["date"] for h in pending_history]
        selected_date = st.selectbox("Wybierz dzień do automatycznego rozliczenia:", dates_to_settle)
        
        entry_to_settle = next((h for h in pending_history if h["date"] == selected_date), None)
        
        if entry_to_settle:
            st.write(f"Wybrana data do rozliczenia: **{selected_date}**")
            
            if st.button("Uruchom automatyczne pobieranie wyników i uczenie wag", type="primary"):
                with st.spinner("Łączę się z API NHL, pobieram gole i aktualizuję model w Supabase..."):
                    actual_goals = fetch_actual_goals_for_date(selected_date)
                    
                    if not actual_goals:
                        for pred in entry_to_settle["predictions"]:
                            actual_goals[pred["player"]] = 0
                            
                    update_results(selected_date, actual_goals)
                    res = update_weights(entry_to_settle["predictions"], actual_goals)
                    
                    st.success(
                        f"Automatyczne rozliczenie zakończone sukcesem! Trafione: {res['hits']}, "
                        f"Pudła: {res['misses']}. Wagi w Supabase zostały zoptymalizowane!"
                    )
                    st.rerun()

# --- Stopka ---
st.markdown("---")
st.caption("Pełna automatyzacja NHL Predictor z bazą Supabase. Dane w czasie rzeczywistym.")
                        
