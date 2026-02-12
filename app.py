import streamlit as st
import pandas as pd
import sqlite3
from pokemontcgsdk import Card, RestClient

# Configurazione API
RestClient.configure('IL_TUO_API_KEY')

st.set_page_config(page_title="PokéVault Pro", layout="wide")

# CSS Personalizzato - Stile Cardmarket Dark
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .card-stat { background: #1f2937; padding: 10px; border-radius: 8px; border-left: 4px solid #facc15; }
    .price-market { color: #10b981; font-weight: bold; font-size: 1.5rem; }
    </style>
    """, unsafe_allow_html=True)

# Database
conn = sqlite3.connect('vault.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS vault 
             (id TEXT, name TEXT, set_name TEXT, condition TEXT, price REAL, img TEXT)''')
conn.commit()

st.title("🛡️ PokéVault: Gestione Professionale")

tab1, tab2 = st.tabs(["🔍 Ricerca Avanzata", "📦 Il mio Magazzino"])

with tab1:
    col_search1, col_search2 = st.columns([2, 1])
    with col_search1:
        query = st.text_input("Nome Pokémon o Codice Set (es: sv3pt5-151)", placeholder="Cerca...")
    
    if query:
        # Ricerca sia per nome che per ID
        cards = Card.where(q=f'name:"*{query}*" OR id:"{query}"')
        
        if cards:
            for card in cards[:10]:
                with st.container():
                    c1, c2, c3 = st.columns([1, 2, 1])
                    with c1:
                        st.image(card.images.small)
                    with c2:
                        st.subheader(f"{card.name} ({card.number}/{card.set.printedTotal})")
                        st.write(f"🌐 Set: {card.set.name}")
                        cond = st.selectbox("Condizione", ["Mint", "Near Mint", "Excellent", "Good", "Played"], key=f"cond_{card.id}")
                    with c3:
                        m_price = card.tcgplayer.prices.holofoil.market if card.tcgplayer and card.tcgplayer.prices.holofoil else 0.0
                        st.markdown(f"Valore Market<br><span class='price-market'>€{m_price}</span>", unsafe_allow_html=True)
                        if st.button("➕ Aggiungi", key=f"btn_{card.id}"):
                            c.execute("INSERT INTO vault VALUES (?,?,?,?,?,?)", 
                                      (card.id, card.name, card.set.name, cond, m_price, card.images.small))
                            conn.commit()
                            st.success("Aggiunta!")

with tab2:
    inventory = pd.read_sql_query("SELECT * FROM vault", conn)
    if not inventory.empty:
        total = inventory['price'].sum()
        st.metric("Valore Totale Portfolio", f"€ {total:.2f}")
        st.dataframe(inventory[['name', 'set_name', 'condition', 'price']], use_container_width=True)
        if st.button("Svuota Magazzino (Reset)"):
            c.execute("DELETE FROM vault")
            conn.commit()
            st.rerun()
    else:
        st.info("Il magazzino è vuoto. Cerca una carta per iniziare.")
