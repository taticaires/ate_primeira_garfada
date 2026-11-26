import json
import random
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st

# =========================================================
# ATÉ A PRIMEIRA GARPADA
# Módulo: Monitoramento Inteligente do Buffet
# MVP demonstrativo com leituras simuladas
# =========================================================

st.set_page_config(
    page_title="Até a Primeira Garfada | Monitoramento",
    page_icon="🍽️",
    layout="wide",
)

ARQUIVO_JSON = Path(__file__).parent / "dados_buffet.json"
UNIDADE = "Bovinu'S Grill & Beer - Augusta"

NIVEIS = {
    "Cheio": 90,
    "Médio": 55,
    "Baixo": 25,
    "Vazio": 5,
}

# Cadastro inicial do protótipo.
# A disposição visual é organizada por buffet, não por cuba solta.
ALIMENTOS_INICIAIS = [
    {
        "id": "B1-01",
        "area": "Buffet 1",
        "nome": "Mix de folhas e tomate",
        "nivel": "Cheio",
    },
    {
        "id": "B2-01",
        "area": "Buffet 2",
        "nome": "Arroz branco",
        "nivel": "Vazio",
    },
    {
        "id": "B2-02",
        "area": "Buffet 2",
        "nome": "Feijão carioca",
        "nivel": "Cheio",
    },
    {
        "id": "B2-03",
        "area": "Buffet 2",
        "nome": "Picanha na chapa",
        "nivel": "Médio",
    },
    {
        "id": "B2-04",
        "area": "Buffet 2",
        "nome": "Batata rústica",
        "nivel": "Cheio",
    },
    {
        "id": "B3-01",
        "area": "Buffet 3",
        "nome": "Pudim",
        "nivel": "Vazio",
    },
    {
        "id": "CH-01",
        "area": "Churrasqueira",
        "nome": "Disponibilidade de carnes",
        "nivel": "Cheio",
    },
]

DESCRICOES_AREAS = {
    "Buffet 1": "Saladas e frios · ilha central",
    "Buffet 2": "Comida quente · ilha lateral direita",
    "Buffet 3": "Sobremesas · sequência da ilha lateral",
    "Churrasqueira": "Praça do churrasco · atrás dos Buffets 2 e 3",
}

def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def nivel_critico(nivel):
    return nivel in ["Baixo", "Vazio"]

def percentual(nivel):
    return NIVEIS.get(nivel, 0)

def registrar_evento(alimento, acao):
    return {
        "id": str(uuid.uuid4())[:8].upper(),
        "alimento_id": alimento["id"],
        "area": alimento["area"],
        "alimento": alimento["nome"],
        "nivel": alimento["nivel"],
        "acao": acao,
        "horario": agora(),
        "origem": "simulada",
    }

def salvar_json():
    payload = {
        "unidade": UNIDADE,
        "modulo": "monitoramento_buffet",
        "modo": "demonstracao_simulada",
        "atualizado_em": agora(),
        "areas": {
            "buffet_1": "Saladas e frios",
            "buffet_2": "Comida quente",
            "buffet_3": "Sobremesas",
            "churrasqueira": "Praça do churrasco",
            "balancas": 2,
        },
        "alimentos": st.session_state.alimentos,
        "historico": st.session_state.historico[:100],
    }
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
        json.dump(payload, arquivo, ensure_ascii=False, indent=2)

def inicializar():
    if "alimentos" not in st.session_state:
        st.session_state.alimentos = [
            {
                **item,
                "ultima_leitura": agora(),
                "status": (
                    "Reposição necessária"
                    if nivel_critico(item["nivel"])
                    else "Normal"
                ),
            }
            for item in ALIMENTOS_INICIAIS
        ]
    if "historico" not in st.session_state:
        st.session_state.historico = []
        for alimento in st.session_state.alimentos:
            if nivel_critico(alimento["nivel"]):
                st.session_state.historico.insert(
                    0, registrar_evento(alimento, "Alerta inicial")
                )
        salvar_json()

def simular_leitura():
    transicoes = {
        "Cheio": ["Cheio", "Cheio", "Médio"],
        "Médio": ["Médio", "Baixo", "Cheio"],
        "Baixo": ["Baixo", "Vazio", "Médio"],
        "Vazio": ["Vazio", "Vazio", "Baixo"],
    }
    for alimento in st.session_state.alimentos:
        alimento["nivel"] = random.choice(transicoes[alimento["nivel"]])
        alimento["ultima_leitura"] = agora()
        alimento["status"] = (
            "Reposição necessária"
            if nivel_critico(alimento["nivel"])
            else "Normal"
        )
        st.session_state.historico.insert(
            0, registrar_evento(alimento, "Nova leitura")
        )
    st.session_state.historico = st.session_state.historico[:100]
    salvar_json()

def registrar_reposicao(alimento_id):
    for alimento in st.session_state.alimentos:
        if alimento["id"] == alimento_id:
            alimento["nivel"] = "Cheio"
            alimento["status"] = "Normal"
            alimento["ultima_leitura"] = agora()
            st.session_state.historico.insert(
                0, registrar_evento(alimento, "Cuba reposta")
            )
            break
    st.session_state.historico = st.session_state.historico[:100]
    salvar_json()

def renderizar_alimento(alimento, chave):
    """Cartão compacto do alimento dentro da área correspondente."""
    nivel = alimento["nivel"]
    critico = nivel_critico(nivel)
    pct = percentual(nivel)

    with st.container(border=True):
        col_nome, col_nivel = st.columns([3, 1])
        with col_nome:
            st.markdown(f"**{alimento['nome']}**")
            st.caption(f"Identificação: {alimento['id']}")
        with col_nivel:
            st.markdown(
                f"<div style='text-align:right;font-weight:700'>{pct}%</div>",
                unsafe_allow_html=True,
            )

        st.progress(pct / 100)

        if critico:
            st.error(f"CRÍTICO · {nivel} · Reposição imediata")
        elif nivel == "Médio":
            st.warning("Acompanhar nível")
        else:
            st.success("Nível adequado")

        if st.button(
            "Registrar reposição",
            key=f"reposicao_{chave}_{alimento['id']}",
            use_container_width=True,
        ):
            registrar_reposicao(alimento["id"])
            st.toast(f"{alimento['nome']}: reposição registrada")
            st.rerun()

inicializar()
alimentos = st.session_state.alimentos

# ---------------------------------------------------------
# CABEÇALHO E INDICADORES
# ---------------------------------------------------------
st.title("Até a Primeira Garfada")
st.caption(f"{UNIDADE} · Monitoramento operacional do buffet")
st.info(
    "Protótipo com leituras simuladas. A integração com câmeras e sensores "
    "será realizada em uma etapa futura."
)

criticos = [a for a in alimentos if nivel_critico(a["nivel"])]
medio = [a for a in alimentos if a["nivel"] == "Médio"]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Buffets / áreas", "4")
k2.metric("Alimentos monitorados", len(alimentos))
k3.metric("Alertas de reposição", len(criticos))
k4.metric("Eventos registrados", len(st.session_state.historico))

if criticos:
    st.markdown("### 🚨 Reposição imediata")
    for item in criticos:
        st.error(
            f'{item["area"]} · {item["nome"]} · '
            f'{item["nivel"].upper()} · Trocar / repor imediatamente'
        )
else:
    st.success("Nenhum alimento em nível crítico neste momento.")

st.divider()

# ---------------------------------------------------------
# MAPA POR ÁREAS DO RESTAURANTE
# ---------------------------------------------------------
st.subheader("Mapa operacional por buffet")
st.caption(
    "As áreas estão separadas conforme a disposição do restaurante. "
    "O mapa é esquemático e não representa escala arquitetônica."
)

# Linha superior: balanças no lado esquerdo e churrasco ao fundo,
# acima das ilhas laterais dos Buffets 2 e 3.
mapa_esquerda, mapa_direita = st.columns([1, 2], gap="large")

with mapa_esquerda:
    st.markdown("#### ⚖️ Ponto de pesagem")
    st.caption("Antes da saída do buffet · canto superior esquerdo")
    bal1, bal2 = st.columns(2)
    with bal1:
        st.container(border=True).markdown("**Balança 1**\\n\\nPonto de pesagem")
    with bal2:
        st.container(border=True).markdown("**Balança 2**\\n\\nPonto de pesagem")

    st.markdown("#### 🥗 Buffet 1")
    st.caption(DESCRICOES_AREAS["Buffet 1"])
    itens_b1 = [a for a in alimentos if a["area"] == "Buffet 1"]
    if itens_b1:
        for i, item in enumerate(itens_b1):
            renderizar_alimento(item, f"b1_{i}")
    else:
        st.info("Nenhum alimento cadastrado nesta área.")

with mapa_direita:
    st.markdown("#### 🔥 Praça do churrasco")
    st.caption(DESCRICOES_AREAS["Churrasqueira"])
    itens_ch = [a for a in alimentos if a["area"] == "Churrasqueira"]
    churr_cols = st.columns(max(1, min(2, len(itens_ch))))
    if itens_ch:
        for i, item in enumerate(itens_ch):
            with churr_cols[i % len(churr_cols)]:
                renderizar_alimento(item, f"ch_{i}")
    else:
        st.info("Nenhum alimento cadastrado nesta área.")

    buffet2_col, buffet3_col = st.columns(2, gap="medium")

    with buffet2_col:
        st.markdown("#### 🍲 Buffet 2")
        st.caption(DESCRICOES_AREAS["Buffet 2"])
        itens_b2 = [a for a in alimentos if a["area"] == "Buffet 2"]
        if itens_b2:
            for i, item in enumerate(itens_b2):
                renderizar_alimento(item, f"b2_{i}")
        else:
            st.info("Nenhum alimento cadastrado nesta área.")

    with buffet3_col:
        st.markdown("#### 🍰 Buffet 3")
        st.caption(DESCRICOES_AREAS["Buffet 3"])
        itens_b3 = [a for a in alimentos if a["area"] == "Buffet 3"]
        if itens_b3:
            for i, item in enumerate(itens_b3):
                renderizar_alimento(item, f"b3_{i}")
        else:
            st.info("Nenhum alimento cadastrado nesta área.")

# ---------------------------------------------------------
# CONTROLES E DADOS SECUNDÁRIOS
# ---------------------------------------------------------
st.divider()
controle, explicacao = st.columns([1, 2])

with controle:
    if st.button("🔄 Simular nova leitura", type="primary", use_container_width=True):
        simular_leitura()
        st.rerun()

with explicacao:
    st.caption(
        "A simulação atualiza os níveis e registra os eventos. "
        "Os alertas são calculados a partir dos níveis cadastrados."
    )

with st.expander("📋 Histórico recente"):
    if st.session_state.historico:
        st.dataframe(
            st.session_state.historico[:20],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Ainda não há eventos registrados.")

with st.expander("📦 Dados estruturados para integração"):
    payload_integracao = {
        "unidade": UNIDADE,
        "modulo": "monitoramento_buffet",
        "modo": "demonstracao_simulada",
        "atualizado_em": agora(),
        "alertas_criticos": len(criticos),
        "alimentos": alimentos,
        "historico": st.session_state.historico[:100],
    }
    st.json(payload_integracao)
    st.download_button(
        "Baixar JSON do monitoramento",
        data=json.dumps(payload_integracao, ensure_ascii=False, indent=2),
        file_name="dados_buffet.json",
        mime="application/json",
    )
