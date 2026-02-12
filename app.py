import streamlit as st
import pandas as pd
import sqlite3
from pokemontcgsdk import Card, RestClient

# --- CHIAVE API ATTIVA ---
RestClient.configure('19494342-bdb4-4cb0-959e-30fec288780b')

st.set_page_config(page_title="PokéVault Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card-slot { background: #1f2937; padding: 15px; border-radius: 12px; border: 1px solid #374151; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

conn = sqlite3.connect('vault_final.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS inventory (id TEXT, name TEXT, lang TEXT, cond TEXT, price REAL, img TEXT)')
conn.commit()

st.title("🛡️ PokéVault Pro")

menu = st.sidebar.radio("Menu", ["Cerca", "Magazzino"])

if menu == "Cerca":
    query = st.text_input("Inserisci nome Pokémon (es. Pikachu)", placeholder="Scrivi qui...")
    col_a, col_b = st.columns(2)
    lingua = col_a.selectbox("Lingua", ["Italiano", "Inglese", "Giapponese"])
    stato = col_b.selectbox("Condizione", ["Mint", "Near Mint", "Excellent", "Played"])

    if query:
        try:
            # Ricerca semplificata per evitare PokemonTcgException
            cards = Card.where(q=f'name:"{query}"')
            if cards:
                for card in cards[:10]:
                    with st.container():
                        st.markdown("<div class='card-slot'>", unsafe_allow_html=True)
                        c1, c2 = st.columns([1, 2])
                        price = card.cardmarket.prices.averageSellPrice if card.cardmarket else 0.0
                        c1.image(card.images.small)
                        c2.subheader(card.name)
                        c2.write(f"Prezzo: €{price}")
                        if c2.button("Aggiungi", key=card.id):
                            c.execute("INSERT INTO inventory VALUES (?,?,?,?,?,?)", (card.id, card.name, lingua, stato, price, card.images.small))
                            conn.commit()
                            st.success("Aggiunto!")
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nessun risultato. Prova a scrivere il nome correttamente.")
        except Exception as e:
            st.error("Errore di connessione. Riavvia l'app dal menu 'Manage app'.")

else:
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    if not df.empty:
        st.metric("Valore Totale", f"€ {df['price'].sum():.2f}")
        st.table(df[['name', 'lang', 'cond', 'price']])
    else:
        st.info("Vuoto.")
