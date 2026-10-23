import streamlit as st
import yaml
from src.data_fetchers.player_builder import build_players_for_today
from src.ranking.generator import generate_ranking
from src.learning.updater import update_weights
from src.utils.history import load_history, update_results, save_prediction

st.set_page_config(
    page_title="NHL Goal Scorer Predictor",
    page_icon="🏒",
    layout="wide"
)

st.title("🏒 NHL Goal Scorer Predictor")
st.markdown("Samouczący się system typowania strzelców bramek")

# --- Sidebar ---
st.sidebar.header("Ustawienia")
top_n = st.sidebar.slider("Ile graczy pokazać", 5, 15, 10)

# --- Zakładki aplikacji ---
tab1, tab2 = st.tabs(["📊 Ranking i Typy", "🎯 Rozliczanie i Nauka Wagi"])

with tab1:
    st.header("Ranking na dziś")

    if st.button("Generuj ranking", type="primary"):
        with st.spinner("Obliczam ranking..."):
            players = build_players_for_today()
            ranking = generate_ranking(players, top_n=top_n)
            
            st.session_state["ranking"] = ranking
            
            # Zapisujemy do historii
            save_prediction(ranking)
            
            st.success("Ranking wygenerowany i zapisany do historii!")

    # Wyświetlanie rankingu
    if "ranking" in st.session_state:
        ranking = st.session_state["ranking"]
        
        for i, player in enumerate(ranking, 1):
            annotations = ", ".join(player["annotations"]) if player["annotations"] else "—"
            
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

    # --- Aktualne wagi ---
    st.header("Aktualne wagi systemu")

    try:
        with open("config/weights.yaml", "r") as f:
            weights = yaml.safe_load(f)
        
        cols = st.columns(len(weights))
        for i, (key, value) in enumerate(weights.items()):
            cols[i].metric(key, f"{value:.2f}")
    except Exception as e:
        st.error(f"Nie udało się wczytać wag: {e}")

with tab2:
    st.header("🎯 Rozliczanie typów i uczenie modelu")
    
    history = load_history()
    pending_history = [h for h in history if h.get("results") is None]

    if not pending_history:
        st.info("Brak nierozliczonych historycznych typów w historii. Wygeneruj i zapisz najpierw ranking z zakładki obok.")
    else:
        dates_to_settle = [h["date"] for h in pending_history]
        selected_date = st.selectbox("Wybierz dzień do rozliczenia:", dates_to_settle)
        
        entry_to_settle = next((h for h in pending_history if h["date"] == selected_date), None)
        
        if entry_to_settle:
            st.write(f"Rozliczasz typy z dnia: **{selected_date}**")
            actual_goals_input = {}
            
            with st.form(key=f"settle_form_{selected_date}"):
                st.write("Wpisz rzeczywistą liczbę goli strzelonych przez graczy w tym dniu:")
                for pred in entry_to_settle["predictions"]:
                    p_name = pred["player"]
                    actual_goals_input[p_name] = st.number_input(
                        f"{p_name} ({pred['team']})", min_value=0, max_value=5, value=0, step=1
                    )
                
                submit_settle = st.form_submit_button("Zatwierdź wyniki i zaktualizuj wagi")
                
                if submit_settle:
                    update_results(selected_date, actual_goals_input)
                    res = update_weights(entry_to_settle["predictions"], actual_goals_input)
                    
                    st.success(
                        f"Zaktualizowano pomyślnie! Trafione: {res['hits']}, "
                        f"Pudła: {res['misses']}. Nowe wagi zapisane w pliku YAML."
                    )
                    st.rerun()

# --- Stopka ---
st.markdown("---")
st.caption("System uczy się na podstawie wyników. Po zakończonych meczach przejdź do zakładki rozliczania.")
