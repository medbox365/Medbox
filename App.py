import streamlit as st
import anthropic
import base64
import os
import json

st.title("Teste de Extração - Fichas de Atendimento")

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

local = st.selectbox("Qual local é essa ficha?", ["HAL", "IBIS"])

uploaded_file = st.file_uploader("Envie a foto ou PDF da ficha", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file and st.button("Extrair dados"):
    file_bytes = uploaded_file.read()
    file_b64 = base64.b64encode(file_bytes).decode("utf-8")
    media_type = uploaded_file.type

    if media_type == "application/pdf":
        content_block = {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": file_b64
            }
        }
    else:
        content_block = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": file_b64
            }
        }

    if local == "HAL":
        prompt = """Esta é uma ficha de atendimento do Hospital HAL.
Extraia a data do cabeçalho (campo "Data de:") e, para cada paciente, extraia:
- nome do paciente (após "Pac:")
- número do atendimento (campo "Atend")
- convênio

Devolva SOMENTE um JSON válido, sem texto antes ou depois, no formato:
{
  "data_documento": "DD/MM/AAAA",
  "atendimentos": [
    {"paciente": "...", "numero_atendimento": "...", "convenio": "..."}
  ]
}
"""
    else:
        prompt = """Esta é uma ficha de atendimento da Clínica IBIS.
Para cada paciente, extraia data, número de atendimento, nome do paciente, e se a palavra "revisão" aparece na linha daquele paciente.

Devolva SOMENTE um JSON válido, sem texto antes ou depois, no formato:
{
  "atendimentos": [
    {"data": "DD/MM/AAAA", "paciente": "...", "numero_atendimento": "...", "revisao": true ou false}
  ]
}
"""

    with st.spinner("Analisando com IA..."):
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": [
                    content_block,
                    {"type": "text", "text": prompt}
                ]
            }]
        )

    resultado_texto = message.content[0].text
    st.subheader("Resultado bruto:")
    st.code(resultado_texto)

    try:
        resultado_json = json.loads(resultado_texto)
        st.subheader("Dados organizados:")
        st.json(resultado_json)
    except:
        st.warning("A IA respondeu, mas não veio em formato JSON perfeito (veja o texto acima).")
