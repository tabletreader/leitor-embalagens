
import streamlit as st
from PIL import Image
import pandas as pd
import io
import requests
import base64
import unicodedata

st.title("Leitor de Embalagens de Medicamentos (OCR + Reconhecimento por Palavras-Chave)")

API_KEY = "helloworld"  # chave gratuita da OCR.Space

# Lista de palavras-chave de medicamentos comuns
palavras_chave = [
    "loratadina", "dipirona", "ibuprofeno", "paracetamol", "doril", "buprovil", "transamin", 
    "ácido tranexâmico", "amoxicilina", "neo loratadin", "neosoro", "losartana", "omeprazol"
]

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

uploaded_file = st.file_uploader("Envie uma imagem da embalagem", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem carregada", use_container_width=True)

    with st.spinner("Extraindo texto da imagem..."):
        texto_ocr = ocr_space_api(image)

    texto_normalizado = normalizar(texto_ocr)
    st.subheader("Texto OCR (normalizado):")
    st.text(texto_normalizado)

    encontrados = [palavra for palavra in palavras_chave if palavra in texto_normalizado]

    if encontrados:
        st.subheader("Medicamentos identificados:")
        df = pd.DataFrame({"Medicamento identificado": encontrados})
        st.dataframe(df)

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Medicamentos")

        st.download_button(
            label="Baixar planilha Excel",
            data=buffer.getvalue(),
            file_name="medicamentos_identificados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Nenhum medicamento conhecido foi identificado no texto extraído.")
