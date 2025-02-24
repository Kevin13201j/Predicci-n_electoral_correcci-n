from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return "El servidor Flask está corriendo correctamente."

def procesar_excel(file):
    try:
        df = pd.read_excel(file, engine="openpyxl")
    except Exception as e:
        return None, {"error": f"Error al leer el archivo: {str(e)}"}

    # Limpiar nombres de columnas
    df.columns = df.columns.str.strip().str.lower()

    # Buscar la columna de votos automáticamente con diferentes variaciones
    posibles_nombres = ["voto", "elección", "elecciones", "votación", "opción"]
    voto_col = next((col for col in df.columns if any(nombre in col for nombre in posibles_nombres)), None)

    if not voto_col:
        return None, {"error": f"El archivo no contiene una columna de votos. Columnas detectadas: {df.columns.tolist()}.\n"
                               f"Intenta cambiar el nombre de la columna que contiene los votos a 'Voto'."}

    # Renombrar la columna encontrada a "Voto"
    df = df.rename(columns={voto_col: "Voto"})
    df['Voto'] = df['Voto'].astype(str).str.strip()

    # Clasificar votos
    df['Etiqueta'] = df['Voto'].apply(lambda x: 'Voto Noboa' if 'Noboa' in x else ('Voto Luisa' if 'Luisa' in x else 'Voto Nulo'))

    # Ordenar los datos
    df = df.sort_values(by='Etiqueta')

    # Contar los votos
    conteo = df['Etiqueta'].value_counts().to_dict()

    return df, conteo

@app.route('/procesar', methods=['POST'])
def procesar():
    if 'file' not in request.files:
        return jsonify({"error": "No se recibió ningún archivo"}), 400

    file = request.files['file']
    df, conteo = procesar_excel(file)

    if df is None:
        return jsonify(conteo), 400  # Devuelve el error si no se encontró la columna

    return jsonify(conteo)

if __name__ == '__main__':
    app.run(debug=True)