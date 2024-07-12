import streamlit as st
import pandas as pd

# Creare un DataFrame con i dati delle molecole
data = pd.DataFrame({
    'nome': ['Molecola1', 'Molecola2', 'Molecola3'],
    'dato_numerico': [123, 456, 789],
    'link': ['http://example.com/1', 'http://example.com/2', 'http://example.com/3']
})

# Funzione per cercare la molecola
def search_molecule(data, query):
    if 'nome' not in data.columns:
        st.error("La colonna 'nome' non esiste nel DataFrame")
        return pd.DataFrame()  # Restituisce un DataFrame vuoto
    result = data[data['nome'].str.contains(query, case=False, na=False)]
    return result

# Aggiungere stile CSS per personalizzare l'app
st.markdown(
    """
    <style>
    .stApp {
        background-color: white;
    }
    .stTextInput > label, .stTextInput > div {
        color: #0047ab;
    }
    .stTextInput > div > input {
        background-color: #0047ab;
        color: white;
    }
    .css-18ni7ap {
        background-color: #0047ab !important;
    }
    .css-1y0tads {
        background-color: white !important;
    }
    .css-h5rgaw {
        color: #0047ab !important;
    }
    .result {
        color: #0047ab;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Titolo dell'app
st.markdown("<h1 style='color: #0047ab;'>Tox-Track</h1>", unsafe_allow_html=True)

# Barra di ricerca
query = st.text_input("Inserisci il nome di una molecola:")

# Eseguire la ricerca e mostrare i risultati
if query:
    results = search_molecule(data, query)
    if not results.empty:
        for idx, row in results.iterrows():
            st.markdown(f"<div class='result'><strong>Molecola:</strong> {row['nome']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='result'><strong>Dato Numerico:</strong> {row['dato_numerico']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='result'><strong>Link:</strong> <a href='{row['link']}' target='_blank'>Link</a></div>", unsafe_allow_html=True)
    else:
        st.write(f"<div class='result'>Nessun risultato trovato per '{query}'</div>", unsafe_allow_html=True)

