import streamlit as st
import pandas as pd
import sqlite3
from pokemontcgsdk import Card, RestClient

# --- CONFIGURAZIONE CHIAVE ---
RestClient.configure('19494342-bdb4-4cb0-959e-30fec288780b')

st.set_page_config(page_title="PokéVault Pro", layout="wide")

# Grafica stile Cardmarket
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .card-container { 
        background-color: #1f2937; 
        padding: 15px; 
        border-radius: 12px; 
        border: 1px solid #374151; 
        margin-bottom: 20px;
    }
    .price-tag { color: #10b981; font-weight: bold; font-size: 1.4em; }
    </style>
    """, unsafe_allow_html=True)

# Database
conn = sqlite3.connect('vault_v4.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS inventory (id TEXT, name TEXT, lang TEXT, cond TEXT, price REAL, img TEXT)')
conn.commit()

st.title("🛡️ PokéVault: Professional Manager")

menu = st.sidebar.radio("Menu", ["🔍 Ricerca e Prezzi", "📦 Magazzino"])

if menu == "🔍 Ricerca e Prezzi":
    st.subheader("Cerca Carta per Nome o Codice")
    
    col_input1, col_input2, col_input3 = st.columns([2, 1, 1])
    with col_input1:
        query = st.text_input("Esempio: Charizard oppure sv4-183", placeholder="Scrivi qui...")
    with col_input2:
        lingua = st.selectbox("Lingua", ["Italiano", "Inglese", "Giapponese"])
    with col_input3:
        stato = st.selectbox("Condizione", ["Mint (MT)", "Near Mint (NM)", "Excellent (EX)", "Good (GD)", "Played (PL)"])

    if query:
        with st.spinner('Sincronizzazione con il database...'):
            # Ricerca mirata
            cards = Card.where(q=f'name:"*{query}*" OR id:"{query}"')
            
            if cards:
                for card in cards[:10]:
                    st.markdown("<div class='card-container'>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([1, 2, 1])
                    
                    # Calcolo prezzo basato su mercato e condizioni
                    base_p = card.cardmarket.prices.averageSellPrice if card.cardmarket else 0.0
                    if base_p == 0: # Backup se Cardmarket non risponde
                        base_p = card.tcgplayer.prices.holofoil.market if card.tcgplayer else 0.5
                    
                    # Moltiplicatori stato
                    m = {"Mi": 1.2, "Ne": 1.0, "Ex": 0.8, "Go": 0.6, "Pl": 0.4}
                    final_p = base_p * m.get(stato[:2], 1.0)

                    with c1:
                        st.image(card.images.small)
                    with c2:
                        st.subheader(f"{card.name} ({card.id})")
                        st.write(f"**Set:** {card.set.name}")
                    with c3:
                        st.markdown(f"Valore Market<br><span class='price-tag'>€ {final_p:.2f}</span>", unsafe_allow_html=True)
                        if st.button(f"📥 Aggiungi", key=card.id):
                            c.execute("INSERT INTO inventory VALUES (?,?,?,?,?,?)", 
                                      (card.id, card.name, lingua, stato, final_p, card.images.small))
                            conn.commit()
                            st.success("Salvata!")
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("Nessun risultato trovato. Prova un nome diverso.")

elif menu == "📦 Magazzino":
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    if not df.empty:
        st.metric("Valore Totale", f"€ {df['price'].sum():.2f}")
        st.dataframe(df[['name', 'lang', 'cond', 'price']], use_container_width=True)
        if st.button("Svuota Tutto"):
            c.execute("DELETE FROM inventory")
            conn.commit()
            st.rerun()
    else:
        st.info("Il tuo magazzino è vuoto.")
