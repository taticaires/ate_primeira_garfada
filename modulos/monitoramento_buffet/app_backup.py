
import json
import random
import uuid
from datetime import datetime
from pathlib import Path

import streamlit as st


# --------------------------------------------------
# CONFIGURAÇÃO
# --------------------------------------------------

st.set_page_config(
    page_title="Até a Primeira Garfada | Buffet",
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

# Áreas e alimentos do protótipo.
# Os níveis iniciais simulam uma situação operacional.

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


def agora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def nivel_critico(nivel):
    return nivel in ["Baixo", "Vazio"]


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

        st.session_state.historico = []

        for alimento in st.session_state.alimentos:
            if nivel_critico(alimento["nivel"]):
                st.session_state.historico.insert(
                    0,
                    registrar_evento(alimento, "Alerta inicial"),
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
        alimento["nivel"] = random.choice(
            transicoes[alimento["nivel"]]
        )

        alimento["ultima_leitura"] = agora()

        alimento["status"] = (
            "Reposição necessária"
            if nivel_critico(alimento["nivel"])
            else "Normal"
        )

        st.session_state.historico.insert(
            0,
            registrar_evento(alimento, "Nova leitura"),
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
                0,
                registrar_evento(alimento, "Cuba reposta"),
            )

            break

    st.session_state.historico = st.session_state.historico[:100]
    salvar_json()


inicializar()


# --------------------------------------------------
# ESTILO VISUAL
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .area-card {
        background: #202124;
        border: 1px solid #393B40;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .area-title {
        font-size: 18px;
        font-weight: 650;
        color: #F2F2F2;
        margin-bottom: 4px;
    }

    .area-subtitle {
        color: #A8A8A8;
        font-size: 13px;
        margin-bottom: 14px;
    }

    .food-row {
        padding: 10px 0;
        border-top: 1px solid #34363A;
    }

    .food-name {
        color: #E8E8E8;
        font-size: 14px;
        font-weight: 500;
    }

    .food-level {
        color: #A8A8A8;
        font-size: 12px;
        margin-top: 3px;
    }

    .critical {
        color: #FF7777;
        font-weight: 600;
    }

    .normal {
        color: #91D5A5;
        font-weight: 500;
    }

    .map-label {
        color: #B8B8B8;
        font-size: 12px;
        text-align: center;
        margin-bottom: 6px;
    }

    .station {
        background: #292B30;
        border: 1px solid #41434A;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
        color: #E7E7E7;
        font-weight: 600;
    }

    .station-small {
        font-size: 12px;
        color: #A8A8A8;
        font-weight: 400;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# CABEÇALHO
# --------------------------------------------------

st.title("Até a Primeira Garfada")
st.caption(f"{UNIDADE}  ·  Monitoramento operacional do buffet")

st.info(
    "Demonstração com leitura simulada. "
    "Os níveis representam um protótipo de monitoramento por visão computacional."
)


# --------------------------------------------------
# INDICADORES PRINCIPAIS
# --------------------------------------------------

alimentos = st.session_state.alimentos

criticos = [
    item for item in alimentos
    if nivel_critico(item["nivel"])
]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Áreas", 4)
col2.metric("Alimentos monitorados", len(alimentos))
col3.metric("Alertas críticos", len(criticos))
col4.metric("Última atualização", agora()[-8:])


# --------------------------------------------------
# ALERTAS CRÍTICOS
# --------------------------------------------------

if criticos:
    st.markdown("### Reposição imediata")

    for item in criticos:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])

            c1.markdown(
                f"**{item['area']}**  ·  {item['nome']}"
            )

            c1.markdown(
                "<span style='color:#FF7777;font-weight:600'>"
                "CRÍTICO · Trocar cuba imediatamente"
                "</span>",
                unsafe_allow_html=True,
            )

            with c2:
                if st.button(
                    "Registrar reposição",
                    key=f"alerta_{item['id']}",
                    use_container_width=True,
                ):
                    registrar_reposicao(item["id"])
                    st.rerun()
else:
    st.success("Nenhuma reposição crítica no momento.")


st.divider()


# --------------------------------------------------
# MAPA OPERACIONAL
# --------------------------------------------------

st.markdown("### Mapa operacional")

st.caption(
    "Representação simplificada da disposição do restaurante."
)


# Churrasqueira ao fundo
st.markdown(
    """
    <div class="station">
        🔥 PRAÇA DO CHURRASCO
        <div class="station-small">Ao fundo</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# Buffets 2 e 3 na ilha lateral
buffet2, buffet3 = st.columns(2)

with buffet2:
    st.markdown(
        """
        <div class="map-label">ILHA LATERAL</div>
        """,
        unsafe_allow_html=True,
    )

    render_area = "Buffet 2"

    with st.container(border=True):
        st.markdown("**BUFFET 2**")
        st.caption("Comida quente")

        itens = [
            item for item in alimentos
            if item["area"] == render_area
        ]

        for item in itens:
            critico_item = nivel_critico(item["nivel"])

            cor = "#FF7777" if critico_item else "#91D5A5"
            status = (
                "Trocar cuba imediatamente"
                if critico_item
                else "Normal"
            )

            st.markdown(
                f"""
                <div class="food-row">
                    <div class="food-name">{item['nome']}</div>
                    <div class="food-level">
                        Nível: {item['nivel']} ·
                        <span style="color:{cor}">{status}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if critico_item:
                if st.button(
                    "Registrar reposição",
                    key=f"mapa_{item['id']}",
                ):
                    registrar_reposicao(item["id"])
                    st.rerun()


with buffet3:
    st.markdown(
        """
        <div class="map-label">ILHA LATERAL</div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("**BUFFET 3**")
        st.caption("Sobremesas")

        itens = [
            item for item in alimentos
            if item["area"] == "Buffet 3"
        ]

        for item in itens:
            critico_item = nivel_critico(item["nivel"])

            cor = "#FF7777" if critico_item else "#91D5A5"
            status = (
                "Trocar cuba imediatamente"
                if critico_item
                else "Normal"
            )

            st.markdown(
                f"""
                <div class="food-row">
                    <div class="food-name">{item['nome']}</div>
                    <div class="food-level">
                        Nível: {item['nivel']} ·
                        <span style="color:{cor}">{status}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if critico_item:
                if st.button(
                    "Registrar reposição",
                    key=f"mapa_{item['id']}",
                ):
                    registrar_reposicao(item["id"])
                    st.rerun()


st.write("")

# Buffet 1 como ilha central
with st.container(border=True):
    st.markdown("**BUFFET 1 · ILHA CENTRAL**")
    st.caption("Saladas e frios")

    itens = [
        item for item in alimentos
        if item["area"] == "Buffet 1"
    ]

    for item in itens:
        critico_item = nivel_critico(item["nivel"])

        cor = "#FF7777" if critico_item else "#91D5A5"
        status = (
            "Trocar cuba imediatamente"
            if critico_item
            else "Normal"
        )

        st.markdown(
            f"""
            <div class="food-row">
                <div class="food-name">{item['nome']}</div>
                <div class="food-level">
                    Nível: {item['nivel']} ·
                    <span style="color:{cor}">{status}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if critico_item:
            if st.button(
                "Registrar reposição",
                key=f"mapa_{item['id']}",
            ):
                registrar_reposicao(item["id"])
                st.rerun()


# Balanças na entrada
st.write("")

bal1, bal2 = st.columns(2)

with bal1:
    st.markdown(
        """
        <div class="station">
            ⚖️ BALANÇA 1
            <div class="station-small">Pesagem</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with bal2:
    st.markdown(
        """
        <div class="station">
            ⚖️ BALANÇA 2
            <div class="station-small">Pesagem</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# CONTROLES E INFORMAÇÕES SECUNDÁRIAS
# --------------------------------------------------

st.divider()

col_sim, col_info = st.columns([1, 2])

with col_sim:
    if st.button(
        "Simular nova leitura",
        type="primary",
        use_container_width=True,
    ):
        simular_leitura()
        st.rerun()

with col_info:
    st.caption(
        "A leitura é simulada. "
        "A integração com câmera e sensores será uma etapa futura."
    )


with st.expander("Histórico e dados de integração"):
    st.markdown("#### Histórico recente")

    st.dataframe(
        st.session_state.historico[:20],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Payload de integração")

    st.json(
        {
            "unidade": UNIDADE,
            "modulo": "monitoramento_buffet",
            "alertas_criticos": len(criticos),
            "alimentos": alimentos,
        }
    )

    st.caption(
        f"Arquivo JSON: {ARQUIVO_JSON.name}"
    )
