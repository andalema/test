import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analisi Utilizzo Simulatore", layout="wide")

st.title("🏎️ Dashboard Analisi Utilizzo Simulatore")

st.write("""
Carica uno o più file CSV (uno per giornata).  
Il sistema unirà automaticamente i dati e mostrerà statistiche e grafici interattivi.
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

    # ====== STATISTICHE GENERALI ======
    st.subheader("📊 Statistiche generali")

    giorni_unici = data['Date'].dt.date.nunique()
    durata_media = data['Total Seconds'].mean()
    durata_totale = data['Total Seconds'].sum()
    vel_media = data['Average Speed (km/h)'].mean()
    vel_max = data['Top Speed (Km/h)'].max()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sessioni totali", len(data))
    col2.metric("Giorni di utilizzo", giorni_unici)
    col3.metric("Durata media (s)", f"{durata_media:.1f}" if pd.notna(durata_media) else "-")
    col4.metric("Durata totale (min)", f"{durata_totale/60:.1f}" if pd.notna(durata_totale) else "-")

    col5, col6 = st.columns(2)
    col5.metric("Velocità media (km/h)", f"{vel_media:.1f}" if pd.notna(vel_media) else "-")
    col6.metric("Velocità massima (km/h)", f"{vel_max:.1f}" if pd.notna(vel_max) else "-")

    st.divider()

    # ====== STATISTICHE DETTAGLIATE ======
    st.subheader("📈 Statistiche dettagliate (in italiano)")

    try:
        descrizione = data.describe(numeric_only=True).T
    except TypeError:
        descrizione = data.describe(include='all').T

    descrizione = descrizione.rename(columns={
        "count": "Conteggio",
        "mean": "Media",
        "std": "Deviazione std",
        "min": "Minimo",
        "25%": "1° quartile",
        "50%": "Mediana",
        "75%": "3° quartile",
        "max": "Massimo"
    })
    st.dataframe(descrizione)

    st.divider()

    # ====== ANALISI TEMPORALE ======
    st.subheader("📅 Analisi temporale")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Durata nel tempo",
        "Velocità media nel tempo",
        "Correlazioni impostazioni",
        "Utilizzo per giorno"
    ])

    with tab1:
        fig1 = px.line(data.sort_values("Date"), x="Date", y="Total Seconds",
                       title="Durata delle sessioni nel tempo")
        st.plotly_chart(fig1, use_container_width=True)

    with tab2:
        fig2 = px.scatter(data, x="Date", y="Average Speed (km/h)",
                          color="Setting Track Material",
                          title="Velocità media per sessione e materiale")
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        numeric_cols = data.select_dtypes(include="number")
        if len(numeric_cols.columns) > 1:
            fig3 = px.scatter_matrix(numeric_cols, title="Correlazioni tra parametri numerici")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.write("Nessun dato numerico sufficiente per analizzare le correlazioni.")

    with tab4:
        data['Giorno'] = data['Date'].dt.date
        by_day = data.groupby('Giorno').agg({
            'Total Seconds': 'mean',
            'Average Speed (km/h)': 'mean',
            'Date': 'count'
        }).rename(columns={'Date': 'Numero sessioni'})
        fig4 = px.bar(by_day, x=by_day.index, y='Numero sessioni',
                      title="Numero di sessioni per giorno")
        st.plotly_chart(fig4, use_container_width=True)

else:
    st.info("⬆️ Carica almeno un file CSV per iniziare l'analisi.")
