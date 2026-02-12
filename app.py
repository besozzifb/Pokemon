import streamlit as st
import pandas as pd
import sqlite3
from pokemontcgsdk import Card, RestClient

# Setup Professionale
RestClient.configure('IL_TUO_API_KEY')
st.set_page_config(page_title="PokéGold Manager", layout="wide", initial_sidebar_state="collapsed")

# CSS Personalizzato per un'estetica mozzafiato
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: white; }
    .card-box { 
        background: rgba(255, 255, 255, 0.05); 
        border-radius: 15px; 
        padding: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: 0.3s;
    }
    .card-box:hover { transform: translateY(-5px); border-color: #ffd700; }
    .price-tag { color: #00ff88; font-weight: bold; font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

# Database con gestione errori
conn = sqlite3.connect('inventory_v2.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS cards (id TEXT PRIMARY KEY, name TEXT, set_name TEXT, price REAL, qty INTEGER, img TEXT)')
conn.commit()

st.title("✨ PokéGold: Gestione Premium")

tab1, tab2, tab3 = st.tabs(["🔍 Cerca & Aggiungi", "📦 Il tuo Caveau", "📈 Analisi"])

with tab1:
    search = st.text_input("Inserisci il nome del Pokémon...", placeholder="es. Mewtwo")
    if search:
        with st.spinner('Accesso al database mondiale...'):
            cards = Card.where(q=f'name:"{search}"')
            if cards:
                for card in cards[:8]:
                    with st.container():
                        col1, col2 = st.columns([1, 2])
                        price = card.tcgplayer.prices.holofoil.market if card.tcgplayer and card.tcgplayer.prices.holofoil else 1.0
                        with col1:
                            st.image(card.images.small, width=150)
                        with col2:
                            st.subheader(card.name)
                            st.write(f"🏷️ **Set:** {card.set.name}")
                            st.markdown(f"💰 **Valore Attuale:** <span class='price-tag'>€{price}</span>", unsafe_allow_html=True)
                            if st.button(f"📥 Deposita nel Caveau", key=card.id):
                                c.execute("INSERT OR REPLACE INTO cards VALUES (?,?,?,?, COALESCE((SELECT qty FROM cards WHERE id=?),0)+1, ?)", 
                                          (card.id, card.name, card.set.name, price, card.id, card.images.small))
                                conn.commit()
                                st.balloons()
                                st.success(f"{card.name} aggiunto correttamente!")

with tab2:
    data = pd.read_sql_query("SELECT * FROM cards", conn)
    if not data.empty:
        total_value = (data['price'] * data['qty']).sum()
        st.metric("Valore Totale del Magazzino", f"€ {total_value:.2f}", delta=f"{len(data)} Carte")
        
        # Visualizzazione a Griglia
        for i in range(0, len(data), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(data):
                    row = data.iloc[i + j]
                    with cols[j]:
                        st.markdown(f"""
                        <div class='card-box'>
                            <img src='{row['img']}' width='100'><br>
                            <b>{row['name']}</b> (x{row['qty']})<br>
                            <span class='price-tag'>€ {row['price'] * row['qty']:.2f}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🗑️ Rimuovi", key=f"del_{row['id']}"):
                            c.execute("DELETE FROM cards WHERE id=?", (row['id'],))
                            conn.commit()
                            st.rerun()
    else:
        st.info("Il tuo caveau è attualmente vuoto. Inizia cercando una carta!")
