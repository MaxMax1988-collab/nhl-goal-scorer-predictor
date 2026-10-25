"""
Główny plik aplikacji Streamlit - NHL Goal Scorer Predictor (wersja stabilna).
"""
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
st.markdown("Autonomiczny, samouczący się system predykcji strzelców NHL z bazą Supabase")

# --- Sidebar ---
st.sidebar.header("Ustawienia")
top_n = st.sidebar.slider("Ile graczy pokazać w rankingu", 5, 15, 10)

# --- Pobieranie faktycznych goli z API NHL dla rozliczenia ---
def fetch_actual_goals_for_date(date_str: str) -> dict:
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

# --- Bezpieczne pobieranie klasyfikacji strzelców z API NHL ---
def fetch_goal_leaders() -> list:
    """Pobiera klasyfikację strzelców z oficjalnych endpointów NHL z obsługą fallbacku."""
    endpoints = [
        "https://api-web.nhle.com/v1/skater-stats-leaders/current?cayenneExp=is defenseman=false and gameTypeId=2",
        "https://api.nhle.com/stats/rest/en/leaderboard/skaters/goals?limit=15"
    ]
    for url in endpoints:
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if isinstance(data, list) and data:
                    return data
                if isinstance(data, dict):
                    if "data" in data and data["data"]:
                        return data["data"]
                    if "goals" in data and data["goals"]:
                        return data["goals"]
        except Exception as e:
            print(f"Próbuję kolejny endpoint klasyfikacji, błąd: {e}")
    return []

# --- Zakładki aplikacji ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Ranking i Typy", 
    "🎯 Rozliczanie i Nauka", 
    "📈 Statystyki i ROI",
    "🏆 Klasyfikacja Strzelców"
])

# ==========================================
# ZAKŁADKA 1: RANKING I TYPY
# ==========================================
with tab1:
    st.header("Ranking na dziś")
    today_str = datetime.now().strftime("%Y-%m-%d")

    history = load_history()
    today_entry = next((h for h in history if h.get("date") == today_str), None)

    if "persistent_ranking" not in st.session_state:
        if today_entry and today_entry.get("predictions"):
            st.session_state["persistent_ranking"] = today_entry.get("predictions")
        elif history:
            st.session_state["persistent_ranking"] = history[0].get("predictions", [])
        else:
            st.session_state["persistent_ranking"] = []

    if st.button("Generuj nowy ranking na dziś", type="primary"):
        with st.spinner("Pobieram składy z API NHL i obliczam model analityczny..."):
            try:
                players = build_players_for_today()
                if not players:
                    st.warning("API NHL nie zwróciło dziś aktywnych zawodników lub mecze się nie odbywają.")
                else:
                    ranking = generate_ranking(players, top_n=top_n)
                    st.session_state["persistent_ranking"] = ranking
                    save_prediction(ranking, today_str)
                    st.success("Nowy ranking został wygenerowany i trwale zapisany w bazie Supabase!")
                    st.rerun()
            except Exception as e:
                st.error(f"Wystąpił błąd podczas generowania rankingu: {e}")

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
        st.info("Brak aktywnego rankingu na dzisiaj. Kliknij przycisk powyżej, aby wygenerować typy.")

    st.header("Aktualne wagi systemu")
    try:
        weights = load_weights()
        cols = st.columns(len(weights))
        for i, (key, value) in enumerate(weights.items()):
            cols[i].metric(key, f"{value:.2f}")
    except Exception as e:
        st.error(f"Nie udało się wczytać wag z Supabase: {e}")

# ==========================================
# ZAKŁADKA 2: ROZLICZANIE I NAUKA
# ==========================================
with tab2:
    st.header("🎯 Automatyczne Rozliczanie Typów i Uczenie Modelu")
    
    history = load_history()
    pending_history = [h for h in history if not h.get("results")]

    if not pending_history:
        st.info("Brak nierozliczonych historii w bazie Supabase. Wszystko jest aktualne.")
    else:
        dates_to_settle = [h["date"] for h in pending_history]
        selected_date = st.selectbox("Wybierz dzień do automatycznego rozliczenia:", dates_to_settle)
        
        entry_to_settle = next((h for h in pending_history if h["date"] == selected_date), None)
        
        if entry_to_settle:
            st.write(f"Wybrana data do rozliczenia: **{selected_date}**")
            
            if st.button("Uruchom automatyczne pobieranie wyników i uczenie wag", type="primary"):
                with st.spinner("Łączę się z API NHL, pobieram bramki i aktualizuję model..."):
                    actual_goals = fetch_actual_goals_for_date(selected_date)
                    
                    if not actual_goals:
                        st.warning("API NHL nie zwróciło jeszcze oficjalnych bramek dla tej daty.")
                    else:
                        update_results(selected_date, actual_goals)
                        res = update_weights(entry_to_settle["predictions"], actual_goals)
                        
                        st.success(
                            f"Rozliczenie zakończone! Trafione: {res['hits']}, "
                            f"Pudła: {res['misses']}. Wagi w Supabase zostały zaktualizowane!"
                        )
                        st.rerun()

# ==========================================
# ZAKŁADKA 3: DIAGNOSTYKA I ROI
# ==========================================
with tab3:
    st.header("📈 Diagnostyka, Skuteczność i ROI")
    st.markdown("Statystyki oparte na rozliczonych dniach z bazy Supabase (kurs rynkowy **@2.50**, stawka 1 jednostka).")
    
    history = load_history()
    settled_history = [h for h in history if h.get("results")]
    
    if not settled_history:
        st.info("Brak rozliczonych danych historycznych do obliczenia statystyk ROI.")
    else:
        total_bets = 0
        total_hits = 0
        total_staked = 0.0
        total_return = 0.0
        ASSUMED_ODDS = 2.50
        
        for entry in settled_history:
            preds = entry.get("predictions", [])
            results = entry.get("results", {})
            
            for p in preds:
                p_name = p.get("player")
                goals = results.get(p_name, 0)
                
                total_bets += 1
                total_staked += 1.0
                
                if goals > 0:
                    total_hits += 1
                    total_return += ASSUMED_ODDS
        
        hit_rate = (total_hits / total_bets * 100) if total_bets > 0 else 0.0
        net_profit = total_return - total_staked
        roi = (net_profit / total_staked * 100) if total_staked > 0 else 0.0
        
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric("Wszystkie typy", total_bets)
        mcol2.metric("Trafione typy", total_hits)
        mcol3.metric("Skuteczność", f"{hit_rate:.1f}%")
        mcol4.metric("ROI", f"{roi:+.2f}%", delta_color="normal" if roi >= 0 else "inverse")
        
        st.markdown("---")
        st.subheader("Szczegółowa historia rozliczonych dni")
        
        for entry in settled_history:
            d = entry.get("date")
            preds = entry.get("predictions", [])
            results = entry.get("results", {})
            
            day_hits = sum(1 for p in preds if results.get(p.get("player"), 0) > 0)
            day_total = len(preds)
            day_rate = (day_hits / day_total * 100) if day_total > 0 else 0
            
            with st.expander(f"📅 Dzień: {d} | Skuteczność: {day_hits}/{day_total} ({day_rate:.1f}%)"):
                for p in preds:
                    p_name = p.get("player")
                    team = p.get("team")
                    goals = results.get(p_name, 0)
                    status = "✅ Trafiony" if goals > 0 else "❌ Pudło"
                    st.write(f"- **{p_name}** ({team}) — Gole: `{goals}` [{status}]")

# ==========================================
# ZAKŁADKA 4: KLASYFIKACJA STRZELCÓW
# ==========================================
with tab4:
    st.header("🏆 Klasyfikacja Strzelców NHL")
    st.markdown("Aktualna czołówka najlepszych strzelców w lidze.")
    
    leaders = fetch_goal_leaders()
    
    if not leaders:
        st.warning("Aktualnie brak danych z API NHL dla klasyfikacji strzelców (sprawdź połączenie lub status serwerów NHL).")
    else:
        for idx, player in enumerate(leaders, 1):
            name = player.get("skaterFullName", player.get("name", f"{player.get('firstName', '')} {player.get('lastName', '')}")).strip()
            team = player.get("teamAbbrevs", player.get("teamAbbrev", "—"))
            goals = player.get("goals", 0)
            games = player.get("gamesPlayed", 0)
            
            if not name or name == " ":
                name = "Nieznany zawodnik"
                
            col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
            with col1:
                st.markdown(f"**{idx}.**")
            with col2:
                st.markdown(f"**{name}** ({team})")
            with col3:
                st.markdown(f"Gole: **{goals}**")
            with col4:
                st.caption(f"Mecze: {games}")
            st.divider()

# --- Stopka ---
st.markdown("---")
st.caption("Pełna automatyzacja NHL Predictor z bazą Supabase. Dane w czasie rzeczywistym.")
            
