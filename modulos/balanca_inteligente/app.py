
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Até a Primeira Garfada | Balança Inteligente",
    page_icon="⚖️",
    layout="wide"
)

UNIDADE = "Bovinu'S Grill & Beer - Augusta"
PASTA = Path(__file__).parent
IMAGEM = PASTA / "prato_na_balanca.png"
ARQUIVO_JSON = PASTA / "dados_balanca.json"

# Dados demonstrativos definidos a partir da imagem criada para o hackathon.
# A leitura de 452 g aparece no visor da balança da fotografia.
DADOS_DEMO = {
    "registro_id": "DEMO-452",
    "unidade": UNIDADE,
    "peso_g": 452,
    "alimentos": [
        {"nome": "Arroz branco", "confianca_simulada": 25},
        {"nome": "Feijão carioca", "confianca_simulada": 25},
        {"nome": "Carne bovina", "confianca_simulada": 10},
        {"nome": "Frango grelhado", "confianca_simulada": 10},
        {"nome": "Linguiça", "confianca_simulada": 10},
        {"nome": "Ovos de codorna", "confianca_simulada": 10},
        {"nome": "Salada", "confianca_simulada": 10}
    ],
    "temperatura_c": 42.5,
    "temperatura_status": "simulada",
    "modo": "simulacao",
    "horario": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

if "analise" not in st.session_state:
    st.session_state.analise = DADOS_DEMO.copy()
if "historico" not in st.session_state:
    st.session_state.historico = [DADOS_DEMO.copy()]

st.title("⚖️ Balança Inteligente")
st.caption(f"{UNIDADE} · Até a Primeira Garfada")
st.info("Demonstração do hackathon: imagem real criada para o protótipo e dados fictícios preenchidos automaticamente.")

# KPI cards, já preenchidos
dados = st.session_state.analise
k1, k2, k3, k4 = st.columns(4)
k1.metric("Peso identificado na imagem", f'{dados["peso_g"]} g')
k2.metric("Alimentos simuladamente reconhecidos", len(dados["alimentos"]))
k3.metric("Temperatura demonstrativa", f'{dados["temperatura_c"]:.1f} °C')
k4.metric("Status da análise", "Concluída")

st.divider()
camera, resultados = st.columns([1.15, 1])

with camera:
    st.subheader("📷 Imagem analisada")
    if IMAGEM.exists():
        st.image(str(IMAGEM), caption="Prato sobre balança digital · imagem demonstrativa", use_container_width=True)
    else:
        st.error("Imagem do prato não encontrada. Mantenha prato_na_balanca.png junto ao app.py.")
    if st.button("🔍 Executar análise simulada novamente", type="primary", use_container_width=True):
        novo = DADOS_DEMO.copy()
        novo["horario"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.analise = novo
        st.session_state.historico.insert(0, novo.copy())
        st.session_state.historico = st.session_state.historico[:50]
        st.rerun()

with resultados:
    st.subheader("🧠 Resultado da visão computacional")
    st.success("Imagem processada · identificação demonstrativa")
    st.warning(
        f'Temperatura ilustrativa: {dados["temperatura_c"]:.1f} °C. '
        "Valor fictício para apresentação; não foi medido pela câmera nem por sensor."
    )
    st.markdown("**Peso lido visualmente do visor:**")
    st.markdown(f'<div style="font-size:42px;font-weight:700;color:#52d6a4">{dados["peso_g"]} <span style="font-size:20px">g</span></div>', unsafe_allow_html=True)
    st.markdown("**Alimentos identificados (dados fictícios):**")
    for alimento in dados["alimentos"]:
        nome = alimento["nome"]
        conf = alimento["confianca_simulada"]
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:8px 10px;margin:5px 0;border:1px solid #39434a;border-radius:8px">'
            f'<span>{nome}</span><span style="color:#55d6a5;font-weight:600">{conf}%</span></div>',
            unsafe_allow_html=True
        )
    st.caption("Percentuais ilustrativos, não produzidos por um modelo de IA real.")

st.divider()
st.subheader("📋 Dados preenchidos automaticamente")
d1, d2 = st.columns(2)
with d1:
    st.text_input("Peso do prato", value=f'{dados["peso_g"]} g', disabled=True)
    st.text_input(
        "Temperatura demonstrativa",
        value=f'{dados["temperatura_c"]:.1f} °C · simulada',
        disabled=True
    )
with d2:
    st.text_area("Alimentos do prato", value=", ".join(a["nome"] for a in dados["alimentos"]), height=105, disabled=True)
    st.text_input("Origem dos dados", value="Imagem + simulação demonstrativa", disabled=True)

with st.expander("📚 Histórico da demonstração"):
    hist = st.session_state.historico
    if hist:
        tabela = pd.DataFrame([
            {"Horário": r["horario"], "Peso (g)": r["peso_g"],
             "Temperatura simulada (°C)": r.get("temperatura_c", "N/D"),
             "Alimentos": ", ".join(a["nome"] for a in r["alimentos"]),
             "Modo": r["modo"]}
            for r in hist
        ])
        st.dataframe(tabela, use_container_width=True, hide_index=True)

with st.expander("🔗 Dados estruturados para integração"):
    payload = {
        "unidade": UNIDADE,
        "modulo": "balanca_inteligente",
        "modo": "demonstracao_simulada",
        "atualizado_em": dados["horario"],
        "pesagem": dados
    }
    st.json(payload)
    st.download_button(
        "Baixar JSON da demonstração",
        data=json.dumps(payload, ensure_ascii=False, indent=2),
        file_name="dados_balanca.json",
        mime="application/json"
    )
