import streamlit as st
import pandas as pd
import sqlite3
from pokemontcgsdk import Card, RestClient

# --- TUA CHIAVE INSERITA ---
RestClient.configure('19494342-bdb4-4cb0-959e-30fec288780b')

st.set_page_config(page_title="PokéMarket Pro", layout="wide")

# Design Professionale
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card-slot { background: #1f2937; padding: 15px; border-radius: 12px; border: 1px solid #374151; margin-bottom: 10px; }
    .price-tag { color: #10b981; font-weight: bold; font-size: 1.4em; }
    </style>
    """, unsafe_allow_html=True)

# Database
conn = sqlite3.connect('vault_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS inventory (id TEXT, name TEXT, lang TEXT, cond TEXT, price REAL, img TEXT)')
conn.commit()

st.title("🇪🇺 PokéMarket Pro")

tab1, tab2 = st.tabs(["🔍 Ricerca Cardmarket", "📦 Magazzino"])

with tab1:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        query = st.text_input("Codice o Nome (es: base1-4 o Charizard)", placeholder="Cerca...")
    with col2:
        lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Giapponese"])
    with col3:
        stato = st.selectbox("Condizione", ["Mint (MT)", "Near Mint (NM)", "Excellent (EX)", "Good (GD)", "Played (PL)"])

    if query:
        cards = Card.where(q=f'id:"{query}" OR name:"*{query}*"')
        if cards:
            for card in cards[:10]:
                with st.container():
                    st.markdown("<div class='card-slot'>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([1, 2, 1])
                    
                    # Logica Prezzo
                    base_price = card.cardmarket.prices.averageSellPrice if card.cardmarket else 0.0
                    mult = {"MT": 1.2, "NM": 1.0, "EX": 0.8, "GD": 0.6, "PL": 0.4}
                    final_p = base_price * mult.get(stato[:2], 1.0)

                    c1.image(card.images.small)
                    c2.subheader(card.name)
                    c2.write(f"ID: {card.id} | Set: {card.set.name}")
                    c3.markdown(f"Valore Stimato<br><span class='price-tag'>€ {final_p:.2f}</span>", unsafe_allow_html=True)
                    if c3.button("📥 Aggiungi", key=card.id):
                        c.execute("INSERT INTO inventory VALUES (?,?,?,?,?,?)", (card.id, card.name, lingua, stato, final_p, card.images.small))
                        conn.commit()
                        st.success("Salvata!")
                    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    if not df.empty:
        st.metric("Valore Totale", f"€ {df['price'].sum():.2f}")
        st.table(df[['name', 'lang', 'cond', 'price']])
    else:
        st.info("Magazzino vuoto.")
