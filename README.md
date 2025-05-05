
# Leitor de Embalagens de Medicamentos

Este é um aplicativo web construído com Streamlit para extrair informações de embalagens de medicamentos a partir de imagens. Ele utiliza OCR (Tesseract) para ler o texto e expressões regulares para identificar campos como princípio ativo, dosagem, forma farmacêutica, quantidade e laboratório.

## Como usar

1. Faça upload de uma imagem da embalagem do medicamento.
2. O app irá extrair o texto e identificar as informações principais.
3. Você poderá baixar os dados em uma planilha Excel (.xlsx).

## Publicação com Streamlit Cloud

1. Crie uma conta gratuita em https://share.streamlit.io
2. Conecte seu GitHub com este repositório
3. Clique em "New App", selecione o repositório e o arquivo `app.py`
4. Seu site estará no ar em poucos segundos

---

## Requisitos

- Python 3.8+
- Bibliotecas:
  - streamlit
  - pytesseract
  - pillow
  - pandas
  - xlsxwriter
