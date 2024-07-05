from flask import Flask, render_template, request

app = Flask(__name__)

# Dati fittizi
data = [
    {'name': 'Aspirin', 'noael': 50, 'ld50': 200},
    {'name': 'Ibuprofen', 'noael': 40, 'ld50': 150},
    {'name': 'Paracetamol', 'noael': 35, 'ld50': 120},
    {'name': 'Amoxicillin', 'noael': 45, 'ld50': 180}
]

def query_data(name):
    results = [entry for entry in data if name.lower() in entry['name'].lower()]
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    search_results = []
    if request.method == 'POST':
        name = request.form['name']
        search_results = query_data(name)
    return render_template('index.html', results=search_results)

if __name__ == "__main__":
    app.run(debug=True)
