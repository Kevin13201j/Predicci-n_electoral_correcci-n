import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from wordcloud import WordCloud
from dotenv import load_dotenv
from groq import Groq
import random

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY no está definido. Verifica tu archivo .env")

# Inicializar el cliente de Groq
qclient = Groq(api_key=api_key)

# Configurar la pantalla de inicio
st.title("📊 Predicción Electoral")
st.subheader("Analiza y predice tendencias en los comentarios electorales")

# Subida de archivos
uploaded_file = st.file_uploader("Sube un archivo XLSX con los comentarios", type=["xlsx"])

if uploaded_file:
    with st.spinner("Procesando archivo..."):
        df = pd.read_excel(uploaded_file, engine="openpyxl")

        # Extraer la columna 'text' y eliminar valores nulos
        text_data = df['text'].dropna()

        # Opción para mostrar una muestra aleatoria de la data
        sample_size = st.slider("Cantidad de comentarios a mostrar", 1, len(text_data), 10)
        sample_data = text_data.sample(n=sample_size, random_state=42)
        st.subheader("Muestra de Comentarios")
        st.write(sample_data)

        # Clasificar votos en base a la columna 'text'
        def clasificar_voto(text):
            if 'Noboa' in text:
                return 'Voto Noboa'
            elif 'Luisa' in text:
                return 'Voto Luisa'
            else:
                return 'Voto Nulo'

        df['Etiqueta'] = df['text'].apply(clasificar_voto)

        # Contar los votos
        conteo = df['Etiqueta'].value_counts().to_dict()

        # Mostrar resultados
        st.subheader("Resultados de la Predicción")
        st.write(conteo)

        # Visualizar en gráfico de barras
        st.subheader("Distribución de Votos")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x=list(conteo.keys()), y=list(conteo.values()), palette="viridis", ax=ax)
        ax.set_xlabel("Tipo de Voto")
        ax.set_ylabel("Cantidad")
        ax.set_title("Distribución de Votos por Candidato")
        st.pyplot(fig)

        # Contar votos nulos y conclusión
        votos_nulos = conteo.get('Voto Nulo', 0)
        total_votos = sum(conteo.values())
        porcentaje_nulos = (votos_nulos / total_votos) * 100 if total_votos > 0 else 0
        st.subheader("Conclusión sobre Votos Nulos")
        st.write(f"Total de votos nulos: {votos_nulos} ({porcentaje_nulos:.2f}%)")
        
        if porcentaje_nulos > 20:
            st.warning("El porcentaje de votos nulos es alto, lo que podría indicar descontento en la población.")
        else:
            st.success("El porcentaje de votos nulos es bajo, lo que sugiere una elección clara entre los candidatos.")

        # Nube de palabras
        full_text = " ".join(text_data)
        wordcloud = WordCloud(width=800, height=400, background_color="white", colormap="viridis").generate(full_text)
        st.subheader("Nube de Palabras")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # Chatbot para analizar comentarios
        if st.button("Hacer consulta al chatbot", key="chatbot_button"):
            response = requests.post("http://127.0.0.1:5000/procesar", json={"comentarios": full_text})
            if response.status_code == 200:
                st.subheader("Respuesta del Chatbot")
                st.write(response.json()["respuesta"])
            else:
                st.error("Error al obtener la respuesta del chatbot.")

st.success("Análisis completado. Se han generado gráficos, nube de palabras y consulta al chatbot.")