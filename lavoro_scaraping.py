import requests
from bs4 import BeautifulSoup
import PyPDF2
import re


# PER IL PDF, CONTROLLARE IL NOME "PUBLISHED REPORT" E POI PRENDERE IL LINK.


suffisso_url = "https://cir-reports.cir-safety.org/"

response1 = requests.get(suffisso_url + "FetchCIRReports/")
response1.raise_for_status()
cookie = response1.json()["pagingcookie"] + "&page=2"
response2 = requests.get(response1.url + "?&pagingcookie=" + cookie)

documento1 = response1.json()["results"]
documento2 = response2.json()["results"]

ingredienti_cir, check, nomi = [], [], []

for el in documento1 + documento2:
    if el["pcpc_ingredientname"] not in check:
        ingredienti_cir.append(el)
        nomi.append(el["pcpc_ingredientname"])
        check.append(el["pcpc_ingredientname"])


ingrediente_richiesto = input(
    "Inserire il nome dell'ingrediente da trovare: ")

ingrediente_trovato = None

for record in ingredienti_cir:
    if ingrediente_richiesto == record["pcpc_ingredientname"]:
        ingrediente_trovato = record

ID_ingrediente = ingrediente_trovato["pcpc_ingredientid"]
response2 = requests.get(
    suffisso_url + "cir-ingredient-status-report/?id=" + ID_ingrediente)

response2.raise_for_status()

html_contenuto = response2.text
soup = BeautifulSoup(html_contenuto, "lxml")

table = soup.find('table')
links = table.find_all('a', href=True)

for link in links:
    if not link['href'].startswith('javascript:alert'):
        href = link['href']
        break
    
response3 = requests.get(suffisso_url + href[2:])
response3.raise_for_status()


if response3.status_code == 200:
    with open('report.pdf', 'wb') as f:
        f.write(response3.content)

    pdf_file = open('report.pdf', 'rb')
    reader = PyPDF2.PdfReader(pdf_file)

    full_text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        page_text = page.extract_text().replace('\n', ' ')
        full_text += page.extract_text()
    
    pdf_file.close()


def trova_valori(testo, indice):
    risultati = []
    pattern = rf'{indice}\D*(\d+)\s*(mg|kg)\D*(\d+)(\D{{1,10}})'  # Pattern regex base

    for match in re.finditer(pattern, testo, flags=re.IGNORECASE):
        # Estrazione valore, parola successiva e contesto
        valore_numero = match.group(1)
        parola_dopo = match.group(4).strip()
        unione_valori = valore_numero + " " + parola_dopo
        contesto = estrai_contesto(testo, match.start(), match.end(), valore_numero)

        # Aggiungi risultato alla lista
        risultati.append((unione_valori, contesto))

    return risultati

def estrai_contesto(testo, inizio, fine, valore):
    # Recupera 10 parole prima e dopo l'indice
    prima = testo[max(0, inizio - 100):inizio].split()[-10:]
    dopo = testo[fine: fine + 100].split()[:10]

    # Unisci le parole con spazi e ritorna il contesto
    contesto = " ".join(prima + [valore] + dopo)
    return contesto.strip()


risultati_noael = trova_valori(full_text, "NOAEL")
