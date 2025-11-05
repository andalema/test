import streamlit as st
import pandas as pd
import plotly.express as px
from io import StringIO

st.set_page_config(page_title="Simulator Analytics Dashboard", layout="wide")

st.title("🏎️ Simulator Usage Analytics")

st.write("""
Carica uno o più file CSV (uno per giornata).  
Il sistema unirà automaticamente i dati e calcolerà le statistiche di utilizzo.
""")

# --- Upload dei file ---
uploaded_files = st.file_uploader("Carica i file CSV", type=["csv"], accept_multiple_files=True)

if uploaded_files:
    dfs = []
    for uploaded_file in uploaded_files:
        df = pd.read_csv(uploaded_file)
        # Rimuove eventuali caratteri speciali nel nome della prima colonna
        df.columns = [c.replace("﻿", "") for c in df.columns]
        dfs.append(df)

    data = pd.concat(dfs, ignore_index=True)
    
    # --- Pulizia e formattazione base ---
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
    
    # Conversione tempo totale in secondi
    def parse_time(t):
        try:
            m, s = t.split(":")
            return float(m) * 60 + float(s)
        except:
            return None
    data["Total Seconds"] = data["Total Time"].apply(parse_time)

st.subheader("📊 Statistiche generali")

# --- conversione data e tempo ---
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

def parse_time(t):
    try:
        m, s = t.split(":")
        return float(m) * 60 + float(s)
    except:
        return None

data["Durata (s)"] = data["Total Time"].apply(parse_time)

# --- calcoli base ---
giorni_unici = data['Date'].dt.date.nunique()
primo_giorno = data['Date'].min()
ultimo_giorno = data['Date'].max()

col1, col2, col3 = st.columns(3)
col1.metric("📆 Giorni di utilizzo", giorni_unici)
col2.metric



    st.divider()

    # --- Grafici ---
    st.subheader("📉 Grafici di utilizzo")

    tab1, tab2, tab3 = st.tabs(["Durata nel tempo", "Velocità media nel tempo", "Correlazioni impostazioni"])

    with tab1:
        fig1 = px.line(data.sort_values("Date"), x="Date", y="Total Seconds", title="Durata delle sessioni nel tempo")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        fig2 = px.scatter(data, x="Date", y="Average Speed (km/h)", color="Setting Track Material",
                          title="Velocità media per sessione e materiale")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        numeric_cols = data.select_dtypes(include="number")
        if len(numeric_cols.columns) > 1:
            fig3 = px.scatter_matrix(numeric_cols, title="Correlazioni tra parametri")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.write("Nessun dato numerico sufficiente per analizzare le correlazioni.")

else:
    st.info("⬆️ Carica almeno un file CSV per iniziare l'analisi.")




