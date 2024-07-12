import requests
from bs4 import BeautifulSoup
import PyPDF2
import re
import string
from collections import Counter
import pandas as pd


# PER IL PDF, CONTROLLARE IL NOME "PUBLISHED REPORT" E POI PRENDERE IL LINK.


suffisso_url = "https://cir-reports.cir-safety.org/"

response = requests.get(suffisso_url + "FetchCIRReports/")
response.raise_for_status()
documento = response.json()["results"]

nomi = []

for k in range(len(documento)):
    nomi.append(documento[k]["pcpc_ingredientname"])

ingrediente_richiesto = input(
    "Inserire il nome dell'ingrediente da trovare: ")

ingrediente_trovato = None

for record in documento:
    if ingrediente_richiesto == record["pcpc_ingredientname"]:
        ingrediente_trovato = record

ID_ingrediente = ingrediente_trovato["pcpc_ingredientid"]
response2 = requests.get(
    suffisso_url + "cir-ingredient-status-report/?id=" + ID_ingrediente)

response2.raise_for_status()

html_contenuto = response2.text
soup = BeautifulSoup(html_contenuto, "lxml")

links = soup.find_all('a', href=True)

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
        full_text += page.extract_text()


def estrai_numero_moda(da_testo):
    numeri = [int(s) for s in re.findall(r'\b\d+\b', da_testo)]
    if numeri:
        moda_numero = Counter(numeri).most_common(1)[0][0]
        return moda_numero
    return None

# Codice esistente
keyword = "NOAEL"
pattern = re.compile(rf'(?<=\b{re.escape(keyword)}\b)')
risultati = []

for match in pattern.finditer(full_text):
    index = match.start()
    start_index = max(0, index - 150)
    end_index = min(len(full_text), index + len(keyword) + 150)

    risultati.append(full_text[start_index:end_index])

# Filtraggio dei risultati
risultati_filtrati = [r for r in risultati if "mg/kg/d" in r and not any(nome in r for nome in nomi)]

# Estrazione del numero con moda maggiore dai risultati filtrati
numeri_moda = [estrai_numero_moda(r) for r in risultati_filtrati]
numero_moda_maggiore = max(filter(None, numeri_moda), key=numeri_moda.count) if numeri_moda else None

print(f"Il numero con moda maggiore tra i testi filtrati è: {numero_moda_maggiore}")

if numero_moda_maggiore:
    noael  = str(numero_moda_maggiore) + " mg/kg/day"
else:
    noael = str(numero_moda_maggiore)

ris_finale = pd.DataFrame({"Nome Cercato": [ingrediente_trovato["pcpc_ingredientname"]], 
                           "NOAEL CIR": [noael], 
                           "Source PDF": [response3.url]}, index=[0])
