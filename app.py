
import streamlit as st
from PIL import Image
import pandas as pd
import io
import requests
import base64
import re
import unicodedata

st.title("Leitor de Embalagens de Medicamentos (Extração Estruturada)")

API_KEY = "helloworld"  # OCR.Space API key gratuita

def normalizar(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFKD", texto).encode("ASCII", "ignore").decode("utf-8")
    return texto.replace("\n", " ").replace("\r", " ")

def ocr_space_api(image_file):
    url_api = "https://api.ocr.space/parse/image"
    buffered = io.BytesIO()
    image_file.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    payload = {
        'apikey': API_KEY,
        'base64Image': 'data:image/png;base64,' + image_base64,
        'language': 'por'
    }
    response = requests.post(url_api, data=payload)
    result = response.json()
    if result.get("IsErroredOnProcessing"):
        return "Erro na API OCR: " + result.get("ErrorMessage", ["Desconhecido"])[0]
    return result["ParsedResults"][0]["ParsedText"]

# Palavras comuns (listas parciais e ampliáveis)
principios_ativos = ["loratadina", "dipirona", "ibuprofeno", "paracetamol", "amoxicilina", "ácido tranexâmico"]
nomes_comerciais = ["neo loratadin", "doril", "buprovil", "transamin", "neosoro"]
fabricantes = ["neo quimica", "zydus", "ems", "medley", "eurofarma", "ache", "teva", "germed", "legrand"]

uploaded_file = st.file_uploader("Envie uma imagem da embalagem", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem carregada", use_container_width=True)

    with st.spinner("Extraindo texto da imagem..."):
        texto_ocr = ocr_space_api(image)

    texto_normalizado = normalizar(texto_ocr)
    st.subheader("Texto extraído (normalizado):")
    st.text(texto_normalizado)

    # Extrações simples com base em padrões e listas
    principio = next((p for p in principios_ativos if p in texto_normalizado), "Não identificado")
    nome_comercial = next((n for n in nomes_comerciais if n in texto_normalizado), "Não identificado")
    fabricante = next((f for f in fabricantes if f in texto_normalizado), "Não identificado")

    dosagem_match = re.search(r'(\d+\s?(mg|g|mg/ml|mcg))', texto_normalizado)
    quantidade_match = re.search(r'(\d+\s?(comprimidos|capsulas|ampolas))', texto_normalizado)

    dosagem = dosagem_match.group(0) if dosagem_match else "Não identificada"
    quantidade = quantidade_match.group(0) if quantidade_match else "Não identificada"

    dados = {
        "Princípio ativo": [principio],
        "Nome comercial": [nome_comercial],
        "Fabricante": [fabricante],
        "Dosagem": [dosagem],
        "Quantidade": [quantidade]
    }

    df = pd.DataFrame(dados)
    st.subheader("Informações estruturadas extraídas:")
    st.dataframe(df)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Medicamento")

    st.download_button(
        label="Baixar planilha Excel",
        data=buffer.getvalue(),
        file_name="medicamento_estruturado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
