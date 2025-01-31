import streamlit as st
import pandas as pd

# Percorso del dataset
#inserire il percorso dove si è scaricato Dataset_ESFA.csv

# Creare un DataFrame per il primo dataset di prova per imitare un ipotetico DataFrame
# estratto dal sito del CIR
data1 = pd.read_csv('Dataset_CIR.csv')
# Caricare il secondo dataset
data2 = pd.read_csv('Dataset_ESFA.csv')

# Funzione per cercare le molecole
def search_molecule(data, query):
    if 'nome' not in data.columns:
        st.error("La colonna 'nome' non esiste nel DataFrame")
        return pd.DataFrame()
    result = data[data['nome'].str.contains(query, case=False, na=False)]
    return result

# Funzione per cercare gli ingredienti
def search_ingredient(data, query):
    if 'Ingredient' not in data.columns:
        st.error("La colonna 'Ingredient' non esiste nel DataFrame")
        return pd.DataFrame()
    result = data[data['Ingredient'].str.contains(query, case=False, na=False)]
    return result

# CSS personalizzato per l'app
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
    .result {
        color: #0047ab;
    }
    .dataset-label {
        color: blue;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Titolo dell'app
st.markdown("<h1 style='color: #0047ab;'>Tox-Track</h1>", unsafe_allow_html=True)

# Scritta sopra la barra di ricerca
st.markdown("<p class='dataset-label'>Scegli il dataset:</p>", unsafe_allow_html=True)

# Selezione del dataset
dataset_choice = st.selectbox("Scegli il dataset:", ["CIR", "ESFA"])

# Imposta la colonna e i dati in base alla selezione
if dataset_choice == "CIR":
    column_name = 'Ingredienti'
    data = data1
else:
    column_name = 'Ingredient'
    data = data2

# Ottieni l'elenco completo dei nomi delle molecole o degli ingredienti
all_names = data[column_name].unique()

# Barra di ricerca con suggerimenti
query = st.selectbox("Inserisci il nome di una molecola o ingrediente:", options=all_names)

# Eseguire la ricerca e mostrare i risultati
if query:
    if dataset_choice == "CIR":
        results = search_molecule(data1, query)
        if not results.empty:
            for idx, row in results.iterrows():
                st.markdown(f"<div class='result'><strong>Molecola:</strong> {row['Ingredienti']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result'><strong>Dato Numerico:</strong> {row['NOAEL']}</div>", unsafe_allow_html=True)
                #st.markdown(f"<div class='result'><strong>Contesto:</strong> {row['Contesto']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result'><strong>Link:</strong> <a href='{row['Link PDF']}' target='_blank'>Link</a></div>", unsafe_allow_html=True)
        else:
            st.write(f"<div class='result'>Nessun risultato trovato per '{query}'</div>", unsafe_allow_html=True)
    else:
        results = search_ingredient(data2, query)
        if not results.empty:
            for idx, row in results.iterrows():
                st.markdown(f"<div class='result'><strong>Ingrediente:</strong> {row['Ingredient']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result'><strong>Valore:</strong> {row['Type']} = {row['Valore']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='result'><strong>Contesto:</strong> {row['Context']}</div>", unsafe_allow_html=True)
        else:
            st.write(f"<div class='result'>Nessun risultato trovato per '{query}'</div>", unsafe_allow_html=True)
