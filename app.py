import streamlit as st
from src.data_fetchers.player_builder import build_players_for_today
from src.ranking.generator import generate_ranking
from src.learning.updater import update_weights
import yaml

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

# --- Generowanie rankingu ---
st.header("Ranking na dziś")

if st.button("Generuj ranking", type="primary"):
    with st.spinner("Obliczam ranking..."):
        players = build_players_for_today()
        ranking = generate_ranking(players, top_n=top_n)
        
        st.session_state["ranking"] = ranking
        
        # Zapisujemy do historii
        from src.utils.history import save_prediction
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

# --- Stopka ---
st.markdown("---")
st.caption("System uczy się na podstawie wyników. Po meczach zaktualizuj wagi.")
