
import streamlit as st
from PIL import Image
import re
import pandas as pd
import io
import requests
import base64

st.title("Leitor de Embalagens de Medicamentos (via OCR API)")

API_KEY = "helloworld"  # chave de demonstração da OCR.Space (limite gratuito)

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

uploaded_file = st.file_uploader("Envie uma imagem da embalagem", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem carregada", use_column_width=True)

    with st.spinner("Extraindo texto com OCR online..."):
        texto = ocr_space_api(image)

    st.subheader("Texto extraído:")
    st.text(texto)

    principio_ativo = re.search(r'([A-Z][a-zçãéó]+(?:\s+[a-z]+)*\s+potássica)', texto, re.IGNORECASE)
    dosagem = re.search(r'(\d+\s?mg)', texto, re.IGNORECASE)
    forma = re.search(r'(comprimidos?.+)', texto, re.IGNORECASE)
    qtde = re.search(r'contém\s+(\d+)\s+comprimidos', texto, re.IGNORECASE)
    laboratorio = re.search(r'(Geolab|EMS|Medley|Eurofarma|Neo Química)', texto, re.IGNORECASE)

    data = {
        "Princípio ativo": [principio_ativo.group(1) if principio_ativo else 'Não identificado'],
        "Dosagem": [dosagem.group(1) if dosagem else 'Não identificada'],
        "Forma farmacêutica": [forma.group(1) if forma else 'Não identificada'],
        "Quantidade": [qtde.group(1) if qtde else 'Não identificada'],
        "Laboratório": [laboratorio.group(1) if laboratorio else 'Não identificado']
    }
    df = pd.DataFrame(data)

    st.subheader("Informações estruturadas:")
    st.dataframe(df)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Medicamento')

    st.download_button(
        label="Baixar planilha Excel",
        data=buffer.getvalue(),
        file_name="medicamento_extraido.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
