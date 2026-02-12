import streamlit as st
import pandas as pd
import sqlite3
from pokemontcgsdk import Card, RestClient

# --- CONFIGURAZIONE CHIAVE API ---
# La tua chiave è già inserita qui sotto
RestClient.configure('19494342-bdb4-4cb0-959e-30fec288780b')

# Configurazione Pagina
st.set_page_config(page_title="PokéVault Pro", layout="wide")

# Stile Estetico
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card-box { background: #1f2937; padding: 15px; border-radius: 12px; border: 1px solid #374151; margin-bottom: 10px; }
    .price-tag { color: #10b981; font-weight: bold; font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

# Database Locale
conn = sqlite3.connect('inventory_v5.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS inventory (id TEXT, name TEXT, lang TEXT, cond TEXT, price REAL, img TEXT)')
conn.commit()

st.title("🛡️ PokéVault Pro")

menu = st.sidebar.radio("Navigazione", ["Cerca e Aggiungi", "Il Mio Magazzino"])

if menu == "Cerca e Aggiungi":
    st.subheader("🔍 Ricerca Internazionale")
    
    col_input, col_lang, col_cond = st.columns([2, 1, 1])
    with col_input:
        query = st.text_input("Inserisci il nome (es: Lugia o Pikachu)", placeholder="Scrivi qui...")
    with col_lang:
        lang = st.selectbox("Lingua", ["Italiano", "Inglese", "Giapponese"])
    with col_cond:
        cond = st.selectbox("Condizione", ["Mint (MT)", "Near Mint (NM)", "Excellent (EX)", "Played (PL)"])

    if query:
        try:
            # Ricerca semplificata per evitare errori di connessione
            cards = Card.where(q=f'name:"{query}"')
            
            if cards:
                for card in cards[:12]:
                    with st.container():
                        st.markdown("<div class='card-box'>", unsafe_allow_html=True)
                        c1, c2, c3 = st.columns([1, 2, 1])
                        
                        # Prezzo Cardmarket (se disponibile) o TCGPlayer
                        p_market = card.cardmarket.prices.averageSellPrice if card.cardmarket else 0.0
                        if p_market == 0 and card.tcgplayer:
                            p_market = card.tcgplayer.prices.holofoil.market if card.tcgplayer.prices.holofoil else 0.5

                        with c1:
                            st.image(card.images.small, width=150)
                        with c2:
                            st.subheader(card.name)
                            st.write(f"ID: {card.id} | Set: {card.set.name}")
                        with c3:
                            st.markdown(f"Valore Stimato<br><span class='price-tag'>€ {p_market:.2f}</span>", unsafe_allow_html=True)
                            if st.button("Aggiungi", key=card.id):
                                c.execute("INSERT INTO inventory VALUES (?,?,?,?,?,?)", 
                                          (card.id, card.name, lang, cond, p_market, card.images.small))
                                conn.commit()
                                st.success(f"{card.name} salvato!")
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nessuna carta trovata con questo nome.")
        except Exception as e:
            st.error("Errore di comunicazione con il database. Riprova tra un istante.")

else:
    st.subheader("📦 Magazzino Attuale")
    df = pd.read_sql_query("SELECT * FROM inventory", conn)
    if not df.empty:
        st.metric("Valore Totale", f"€ {df['price'].sum():.2f}")
        st.dataframe(df[['name', 'lang', 'cond', 'price']], use_container_width=True)
        if st.button("Cancella tutto l'inventario"):
            c.execute("DELETE FROM inventory")
            conn.commit()
            st.rerun()
    else:
        st.info("Il tuo magazzino è ancora vuoto.")
