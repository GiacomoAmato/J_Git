import requests
from bs4 import BeautifulSoup
import PyPDF2
import re
import pandas as pd
import logging

# Configurazione del logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

suffisso_cir = "https://cir-reports.cir-safety.org/"
session = requests.Session()

def fetch_documenti(page):
    response = session.get(suffisso_cir + "FetchCIRReports/", params={'page': page})
    response.raise_for_status()
    return response.json()["results"]

def fetch_cookie():
    response = session.get(suffisso_cir + "FetchCIRReports/")
    response.raise_for_status()
    return response.json()["pagingcookie"]

def trova_valori(testo, indice):
    ris_valori, ris_contesto = [], []
    # Pattern regex migliorato
    pattern = rf'{indice}\D*(\d+(\.\d+)?)\s*(mg/kg|mg|g|kg)'
   
    for match in re.finditer(pattern, testo, flags=re.IGNORECASE):
        valore_numero = match.group(1)
        unita = match.group(3)
        unione_valori = f"{valore_numero} {unita}"
        contesto = estrai_contesto(testo, match.start(), match.end(), unione_valori)

        ris_valori.append(unione_valori)
        ris_contesto.append(contesto)

    if not ris_valori:
        logging.warning(f"Nessun valore trovato per l'indice '{indice}' nel testo fornito.")
   
    return ris_valori, ris_contesto

def estrai_contesto(testo, inizio, fine, valore):
    prima = testo[max(0, inizio - 100):inizio].split()[-10:]
    dopo = testo[fine: fine + 100].split()[:10]
    contesto = " ".join(prima + [valore] + dopo)
    return contesto.strip()

def fetch_ingredient_report(ingrediente_id):
    response = session.get(suffisso_cir + f"cir-ingredient-status-report/?id={ingrediente_id}")
    response.raise_for_status()
    return response.text

def fetch_pdf_link(table):
    links = table.find_all('a', href=True)
    for link in links:
        if not link['href'].startswith('javascript:alert'):
            return suffisso_cir + link['href'][2:]

def extract_text_from_pdf(pdf_content):
    full_text = ''
    with open('report.pdf', 'wb') as f:
        f.write(pdf_content)

    with open('report.pdf', 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            full_text += page.extract_text().replace('\n', ' ')
   
    # Pre-elaborazione del testo
    full_text = re.sub(r'\s+', ' ', full_text)  # Normalizza gli spazi
    return full_text

def process_ingredienti(documenti):
    ingredienti_cir, check, nomi = [], [], []
    pdf, noael, context = [], [], []

    for el in documenti:
        if el["pcpc_ingredientname"] not in check:
            ingredienti_cir.append(el)
            nomi.append(el["pcpc_ingredientname"])
            check.append(el["pcpc_ingredientname"])

    for ingrediente in ingredienti_cir:
        html_contenuto = fetch_ingredient_report(ingrediente["pcpc_ingredientid"])
        soup = BeautifulSoup(html_contenuto, "lxml")
        table = soup.find('table')

        if not table or len(table.find_all('tr')) < 2:
            noael.append(None)
            pdf.append(None)
            continue

        pdf_link = fetch_pdf_link(table)
        if not pdf_link:
            noael.append(None)
            pdf.append(None)
            continue

        response_pdf = session.get(pdf_link)
        response_pdf.raise_for_status()
        pdf.append(response_pdf.url)

        full_text = extract_text_from_pdf(response_pdf.content)
        risultati_noael, risultati_contesto = trova_valori(full_text, "NOAEL")
        noael.append(risultati_noael)
        context.append(risultati_contesto)

    return pd.DataFrame({"Ingredienti": nomi, "NOAEL": noael, "Contesto": context, "Link PDF": pdf})

def main():
    try:
        cookie = fetch_cookie()
        documento1 = fetch_documenti(1)
        documento2 = fetch_documenti(2)

        data = process_ingredienti(documento1 + documento2)
        data.to_csv('Dataset_CIR.csv', index=False)
        logging.info("File CSV generato con successo.")
    except Exception as e:
        logging.error(f"Errore durante l'elaborazione: {e}")

if __name__ == "__main__":
    main()
