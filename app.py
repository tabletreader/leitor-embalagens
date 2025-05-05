
import streamlit as st
from PIL import Image
import pytesseract
import re
import pandas as pd
import io

st.title("Leitor de Embalagens de Medicamentos")

uploaded_file = st.file_uploader("Envie uma imagem da embalagem", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Imagem carregada", use_column_width=True)

    with st.spinner("Extraindo texto da imagem..."):
        texto = pytesseract.image_to_string(image, lang="por")

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
        writer.save()
        st.download_button(
            label="Baixar planilha Excel",
            data=buffer.getvalue(),
            file_name="medicamento_extraido.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
