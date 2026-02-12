import os
import subprocess
import sys

# Forza l'installazione della libreria se manca
try:
    import pokemontcgsdk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pokemontcgsdk"])

import streamlit as st
import pandas as pd
import sqlite3
from pokemontcgsdk import Card, RestClient

# --- CHIAVE API ---
RestClient.configure('19494342-bdb4-4cb0-959e-30fec288780b')

st.set_page_config(page_title="PokéVault Pro", layout="wide")

# Database
conn = sqlite3.connect('vault_v6.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS inventory (id TEXT, name TEXT, lang TEXT, cond TEXT, price REAL, img TEXT)')
conn.commit()

st.title("🛡️ PokéVault Pro")

query = st.text_input("Inserisci il nome (es: Pikachu)", placeholder="Scrivi qui...")

if query:
    try:
        # Ricerca diretta
        cards = Card.where(q=f'name:"{query}"')
        if cards:
            for card in cards[:10]:
                col1, col2 = st.columns([1, 2])
                price = card.cardmarket.prices.averageSellPrice if card.cardmarket else 0.0
                with col1:
                    st.image(card.images.small)
                with col2:
                    st.subheader(card.name)
                    st.write(f"Valore: €{price}")
                    if st.button("Aggiungi", key=card.id):
                        c.execute("INSERT INTO inventory VALUES (?,?,?,?,?,?)", (card.id, card.name, "Ita", "NM", price, card.images.small))
                        conn.commit()
                        st.success("Salvato!")
        else:
            st.warning("Nessun risultato. Controlla il nome.")
    except Exception as e:
        st.error(f"Errore tecnico: {e}")
