import streamlit as st
import pandas as pd
import sqlite3
from pokemontcgsdk import Card, RestClient

# Configurazione Estetica per Mobile
st.set_page_config(page_title="PokéStock Pro", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: white; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #ff4b4b; color: white; }
    .card-container { border: 1px solid #333; padding: 10px; border-radius: 15px; margin-bottom: 10px; background: #262626; }
    </style>
    """, unsafe_allow_html=True)

# Connessione Database Permanente
conn = sqlite3.connect('inventory.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS cards (id TEXT PRIMARY KEY, name TEXT, set_name TEXT, price REAL, qty INTEGER, img TEXT)')
conn.commit()

# --- LOGICA APP ---
st.title("🎴 PokéStock Pro")

tab1, tab2 = st.tabs(["➕ Aggiungi", "📂 Magazzino"])

with tab1:
    search = st.text_input("Cerca Pokémon...", placeholder="es. Charizard VMAX")
    if search:
        cards = Card.where(q=f'name:"{search}"')
        for card in cards[:10]:
            with st.container():
                col1, col2 = st.columns([1, 2])
                price = card.tcgplayer.prices.holofoil.market if card.tcgplayer and card.tcgplayer.prices.holofoil else 0.0
                with col1:
                    st.image(card.images.small)
                with col2:
                    st.subheader(card.name)
                    st.write(f"Set: {card.set.name}")
                    st.write(f"Valore: **€{price}**")
                    if st.button("Aggiungi a Inventario", key=card.id):
                        c.execute("INSERT OR REPLACE INTO cards VALUES (?,?,?,?, COALESCE((SELECT qty FROM cards WHERE id=?),0)+1, ?)", 
                                  (card.id, card.name, card.set.name, price, card.id, card.images.small))
                        conn.commit()
                        st.success("Aggiunto!")

with tab2:
    data = pd.read_sql_query("SELECT * FROM cards", conn)
    if not data.empty:
        total_val = (data['price'] * data['qty']).sum()
        st.metric("Valore Totale", f"€ {total_val:.2f}")
        for _, row in data.iterrows():
            st.markdown(f"""
            <div class="card-container">
                <b>{row['name']}</b> x{row['qty']}<br>
                <small>{row['set_name']}</small><br>
                <strong>€ {row['price']}</strong>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Il magazzino è vuoto.")
