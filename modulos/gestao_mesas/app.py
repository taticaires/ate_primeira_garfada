from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

# ==============================================================================
# CONFIGURAÇÕES GERAIS E CONSTANTES DO MÓDULO
# ==============================================================================
PROJETO_NOME = "Até a Primeira Garfada"
MODULO_NOME = "gestao_inteligente_mesas"
MODULO_TITULO = "Gestão Inteligente de Mesas"
UNIDADE_RESTAURANTE = "Bovinu’S Grill & Beer - Augusta"

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_JSON = BASE_DIR / "dados_mesas.json"

ESTADOS_LISTA = [
    "Livre",
    "Ocupada",
    "Aguardando limpeza",
    "Aguardando atendimento",
]

ESTADOS_CONFIG: dict[str, dict[str, str]] = {
    "Livre": {
        "cor_hex": "#22c55e",
        "cor_bg": "#052e16",
        "cor_borda": "#16a34a",
        "cor_nome": "Verde",
        "pulse": "",
    },
    "Ocupada": {
        "cor_hex": "#ef4444",
        "cor_bg": "#450a0a",
        "cor_borda": "#dc2626",
        "cor_nome": "Vermelho",
        "pulse": "",
    },
    "Aguardando limpeza": {
        "cor_hex": "#eab308",
        "cor_bg": "#422006",
        "cor_borda": "#ca8a04",
        "cor_nome": "Amarelo",
        "pulse": "led-pulse",
    },
    "Aguardando atendimento": {
        "cor_hex": "#3b82f6",
        "cor_bg": "#172554",
        "cor_borda": "#2563eb",
        "cor_nome": "Azul",
        "pulse": "led-pulse",
    },
}

SALOES_CONFIG = [
    {"codigo": "S1", "nome": "Salão Principal (Térreo)", "quantidade": 25, "inicio_num": 1},
    {"codigo": "S2", "nome": "Salão Superior (Mezanino)", "quantidade": 25, "inicio_num": 26},
]


def gerar_template_50_mesas() -> list[dict[str, Any]]:
    """Gera 50 mesas distribuídas em 2 salões (25 em cada) com cenário inicial realista."""
    padrao_capacidades = [4, 4, 2, 4, 6, 4, 2, 4, 4, 8, 6, 4, 2, 4, 6, 4, 4, 2, 6, 4, 4, 2, 4, 6, 8]
    padrao_estados_s1 = [
        "Livre", "Ocupada", "Ocupada", "Aguardando atendimento", "Livre",
        "Ocupada", "Aguardando limpeza", "Ocupada", "Livre", "Ocupada",
        "Aguardando atendimento", "Ocupada", "Livre", "Ocupada", "Aguardando limpeza",
        "Livre", "Ocupada", "Ocupada", "Livre", "Aguardando atendimento",
        "Ocupada", "Livre", "Aguardando limpeza", "Ocupada", "Livre",
    ]
    padrao_estados_s2 = [
        "Ocupada", "Livre", "Livre", "Ocupada", "Aguardando atendimento",
        "Livre", "Ocupada", "Aguardando limpeza", "Livre", "Ocupada",
        "Livre", "Aguardando atendimento", "Ocupada", "Livre", "Ocupada",
        "Aguardando limpeza", "Livre", "Ocupada", "Livre", "Livre",
        "Ocupada", "Aguardando atendimento", "Livre", "Ocupada", "Aguardando limpeza",
    ]

    padroes_por_salao = {"S1": padrao_estados_s1, "S2": padrao_estados_s2}
    mesas: list[dict[str, Any]] = []

    for salao in SALOES_CONFIG:
        cod = salao["codigo"]
        estados_salao = padroes_por_salao[cod]
        for idx in range(salao["quantidade"]):
            numero_global = salao["inicio_num"] + idx
            mesas.append(
                {
                    "id": f"AUG-{cod}-M{numero_global:02d}",
                    "nome": f"Mesa {numero_global:02d}",
                    "salao": salao["nome"],
                    "capacidade": padrao_capacidades[idx % len(padrao_capacidades)],
                    "estado_inicial": estados_salao[idx],
                }
            )
    return mesas


MESAS_INICIAIS_TEMPLATE = gerar_template_50_mesas()
TOTAL_MESAS_ESPERADO = len(MESAS_INICIAIS_TEMPLATE)


# ==============================================================================
# CAMADA DE DADOS E INTEGRAÇÃO JSON
# ==============================================================================
def agora_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def formatar_hora(iso_str: str) -> str:
    try:
        return datetime.fromisoformat(iso_str).strftime("%H:%M:%S")
    except ValueError:
        return iso_str


def resumir_lista_mesas(mesas: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(mesas)
    livres = sum(1 for m in mesas if m["estado_atual"] == "Livre")
    ocupadas = sum(1 for m in mesas if m["estado_atual"] == "Ocupada")
    limpeza = sum(1 for m in mesas if m["estado_atual"] == "Aguardando limpeza")
    atendimento = sum(1 for m in mesas if m["estado_atual"] == "Aguardando atendimento")
    taxa_ocupacao = round(((ocupadas + atendimento) / total) * 100, 1) if total > 0 else 0.0

    return {
        "total_mesas": total,
        "mesas_livres": livres,
        "mesas_ocupadas": ocupadas,
        "mesas_aguardando_limpeza": limpeza,
        "mesas_aguardando_atendimento": atendimento,
        "taxa_ocupacao_percentual": taxa_ocupacao,
    }


def calcular_metricas(mesas: list[dict[str, Any]]) -> dict[str, Any]:
    geral = resumir_lista_mesas(mesas)
    por_salao: dict[str, dict[str, Any]] = {}
    for salao in SALOES_CONFIG:
        nome_salao = salao["nome"]
        mesas_salao = [m for m in mesas if m.get("salao") == nome_salao]
        por_salao[nome_salao] = resumir_lista_mesas(mesas_salao)
    geral["por_salao"] = por_salao
    return geral


def montar_indicador_iot(estado: str) -> dict[str, Any]:
    cfg = ESTADOS_CONFIG[estado]
    return {
        "simulado": True,
        "hardware_conectado": False,
        "cor_led": cfg["cor_nome"],
        "codigo_hex": cfg["cor_hex"],
        "sinal_alerta": estado in ("Aguardando limpeza", "Aguardando atendimento"),
    }


def criar_estrutura_inicial() -> dict[str, Any]:
    timestamp = agora_iso()
    mesas = []
    for item in MESAS_INICIAIS_TEMPLATE:
        estado = item["estado_inicial"]
        mesas.append(
            {
                "id": item["id"],
                "nome": item["nome"],
                "salao": item["salao"],
                "capacidade": item["capacidade"],
                "estado_atual": estado,
                "indicador_iot": montar_indicador_iot(estado),
                "ultima_alteracao": timestamp,
            }
        )

    dados = {
        "metadados": {
            "projeto": PROJETO_NOME,
            "modulo": MODULO_NOME,
            "unidade": UNIDADE_RESTAURANTE,
            "versao_schema": "1.1.0",
            "total_saloes": len(SALOES_CONFIG),
            "mesas_por_salao": 25,
            "modo_simulacao": True,
            "hardware_conectado": False,
            "ultima_atualizacao": timestamp,
        },
        "metricas": calcular_metricas(mesas),
        "mesas": mesas,
        "historico_eventos": [],
    }
    salvar_dados(dados)
    return dados


def salvar_dados(dados: dict[str, Any]) -> None:
    dados["metadados"]["ultima_atualizacao"] = agora_iso()
    dados["metricas"] = calcular_metricas(dados["mesas"])
    ARQUIVO_JSON.parent.mkdir(parents=True, exist_ok=True)
    with ARQUIVO_JSON.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def carregar_dados() -> dict[str, Any]:
    if ARQUIVO_JSON.exists():
        try:
            with ARQUIVO_JSON.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            mesas_validas = (
                isinstance(dados, dict)
                and isinstance(dados.get("mesas"), list)
                and len(dados["mesas"]) == TOTAL_MESAS_ESPERADO
                and all("salao" in m for m in dados["mesas"])
                and isinstance(dados.get("historico_eventos"), list)
            )
            if mesas_validas:
                dados["metricas"] = calcular_metricas(dados["mesas"])
                return dados
        except (json.JSONDecodeError, OSError):
            pass
    # Se não existir ou for da versão anterior (12 mesas), gera o cenário de 50 mesas
    return criar_estrutura_inicial()


def registrar_mudanca_estado(
    dados: dict[str, Any],
    mesa_id: str,
    novo_estado: str,
    origem: str = "alteracao_manual",
    salvar: bool = True,
) -> bool:
    for mesa in dados["mesas"]:
        if mesa["id"] == mesa_id:
            estado_anterior = mesa["estado_atual"]
            if estado_anterior == novo_estado:
                return False

            agora = datetime.now()
            timestamp_iso = agora.isoformat(timespec="seconds")

            mesa["estado_atual"] = novo_estado
            mesa["indicador_iot"] = montar_indicador_iot(novo_estado)
            mesa["ultima_alteracao"] = timestamp_iso

            evento = {
                "evento_id": f"EVT-{len(dados['historico_eventos']) + 1:04d}",
                "mesa_id": mesa["id"],
                "mesa_nome": mesa["nome"],
                "salao": mesa["salao"],
                "estado_anterior": estado_anterior,
                "novo_estado": novo_estado,
                "led_iot_simulado": ESTADOS_CONFIG[novo_estado]["cor_nome"],
                "origem": origem,
                "data_hora": timestamp_iso,
                "horario_formatado": agora.strftime("%d/%m/%Y %H:%M:%S"),
            }
            dados["historico_eventos"].insert(0, evento)
            if salvar:
                salvar_dados(dados)
            return True
    return False


# ==============================================================================
# CALLBACKS DE INTERAÇÃO
# ==============================================================================
def ao_alterar_mesa(mesa_id: str, widget_key: str) -> None:
    novo_estado = st.session_state[widget_key]
    alterou = registrar_mudanca_estado(
        st.session_state.dados_salao,
        mesa_id=mesa_id,
        novo_estado=novo_estado,
        origem="alteracao_manual",
    )
    if alterou:
        st.session_state.ultimo_aviso = f"{mesa_id} atualizada para '{novo_estado}'."


def sincronizar_widgets_estado(dados: dict[str, Any]) -> None:
    for mesa in dados["mesas"]:
        st.session_state[f"select_{mesa['id']}"] = mesa["estado_atual"]


# ==============================================================================
# ESTILIZAÇÃO CSS (GRADE 5x5 COMPACTA + LEDS IOT SIMULADOS)
# ==============================================================================
def aplicar_estilos() -> None:
    st.markdown(
        """
        <style>
        .sim-banner {
            background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
            border-left: 5px solid #f59e0b;
            border-radius: 10px;
            padding: 10px 16px;
            margin-bottom: 14px;
            color: #f8fafc;
            font-size: 0.9rem;
        }
        .sim-banner strong { color: #fbbf24; }
        .legend-bar {
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 9px 14px;
            margin: 10px 0 16px 0;
            color: #e2e8f0;
            font-size: 0.85rem;
            align-items: center;
        }
        .legend-item {
            display: inline-flex;
            align-items: center;
            gap: 7px;
        }
        .kpi-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-top: 4px solid var(--accent);
            border-radius: 12px;
            padding: 12px 14px;
            color: #f8fafc;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            margin-bottom: 8px;
        }
        .kpi-title {
            font-size: 0.78rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 3px;
        }
        .kpi-value {
            font-size: 1.85rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.1;
        }
        .kpi-sub {
            font-size: 0.76rem;
            color: #cbd5e1;
            margin-top: 4px;
        }
        .salao-header {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-left: 5px solid #f59e0b;
            background: #0f172a;
            border-top: 1px solid #1e293b;
            border-right: 1px solid #1e293b;
            border-bottom: 1px solid #1e293b;
            border-radius: 8px;
            margin: 14px 0 12px 0;
            color: #f8fafc;
        }
        .salao-title {
            font-size: 1.05rem;
            font-weight: 700;
        }
        .salao-stats {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            font-size: 0.82rem;
            color: #cbd5e1;
        }
        .table-card {
            border-radius: 12px;
            padding: 10px 12px;
            margin-bottom: 6px;
            color: #f8fafc;
            box-shadow: 0 3px 10px rgba(0, 0, 0, 0.18);
        }
        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
            gap: 4px;
        }
        .table-name {
            font-size: 0.96rem;
            font-weight: 700;
        }
        .table-id {
            font-size: 0.68rem;
            opacity: 0.85;
            font-family: monospace;
            background: rgba(255, 255, 255, 0.12);
            padding: 2px 5px;
            border-radius: 5px;
        }
        .table-meta {
            font-size: 0.74rem;
            color: #cbd5e1;
            margin-bottom: 8px;
        }
        .iot-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(0, 0, 0, 0.38);
            border: 1px solid rgba(255, 255, 255, 0.16);
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 0.74rem;
            font-weight: 600;
            max-width: 100%;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .led-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            flex-shrink: 0;
        }
        @keyframes pulseGlow {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.28); opacity: 0.6; }
            100% { transform: scale(1); opacity: 1; }
        }
        .led-pulse {
            animation: pulseGlow 1.3s infinite ease-in-out;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def renderizar_kpi(titulo: str, valor: int, subtitulo: str, cor_borda: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent: {cor_borda};">
            <div class="kpi-title">{titulo}</div>
            <div class="kpi-value">{valor}</div>
            <div class="kpi-sub">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_cabecalho_salao(nome_salao: str, resumo: dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="salao-header">
            <div class="salao-title">📍 {nome_salao} ({resumo['total_mesas']} mesas)</div>
            <div class="salao-stats">
                <span>🟢 Livres: <b>{resumo['mesas_livres']}</b></span>
                <span>🔴 Ocupadas: <b>{resumo['mesas_ocupadas']}</b></span>
                <span>🟡 Limpeza: <b>{resumo['mesas_aguardando_limpeza']}</b></span>
                <span>🔵 Atendimento: <b>{resumo['mesas_aguardando_atendimento']}</b></span>
                <span>📊 Ocupação: <b>{resumo['taxa_ocupacao_percentual']}%</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_card_mesa(mesa: dict[str, Any]) -> None:
    estado = mesa["estado_atual"]
    cfg = ESTADOS_CONFIG[estado]
    hora = formatar_hora(mesa["ultima_alteracao"])

    st.markdown(
        f"""
        <div class="table-card" style="
            background: linear-gradient(145deg, {cfg['cor_bg']} 0%, #0f172a 100%);
            border: 2px solid {cfg['cor_borda']};
        ">
            <div class="table-header">
                <span class="table-name">{mesa['nome']}</span>
                <span class="table-id">{mesa['id']}</span>
            </div>
            <div class="table-meta">
                👥 {mesa['capacidade']} lug. &nbsp;•&nbsp; 🕒 {hora}
            </div>
            <div class="iot-pill" title="LED {cfg['cor_nome']} — {estado}">
                <span class="led-dot {cfg['pulse']}" style="
                    background-color: {cfg['cor_hex']};
                    box-shadow: 0 0 8px {cfg['cor_hex']}, 0 0 14px {cfg['cor_hex']};
                "></span>
                <span>{estado}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# APLICAÇÃO PRINCIPAL
# ==============================================================================
def main() -> None:
    st.set_page_config(
        page_title=f"{MODULO_TITULO} | {PROJETO_NOME}",
        page_icon="🍽️",
        layout="wide",
    )
    aplicar_estilos()

    if "dados_salao" not in st.session_state:
        st.session_state.dados_salao = carregar_dados()

    if "ultimo_aviso" not in st.session_state:
        st.session_state.ultimo_aviso = ""

    dados = st.session_state.dados_salao

    # Garante sincronização inicial das chaves dos selects
    for mesa in dados["mesas"]:
        key = f"select_{mesa['id']}"
        if key not in st.session_state:
            st.session_state[key] = mesa["estado_atual"]

    # --------------------------------------------------------------------------
    # SIDEBAR — CONTROLES DE TESTE E FILTROS
    # --------------------------------------------------------------------------
    with st.sidebar:
        st.title("🥩 Até a Primeira Garfada")
        st.caption(f"**Unidade:** {UNIDADE_RESTAURANTE}")
        st.caption(f"**Capacidade do teste:** 50 mesas (2 salões × 25)")
        st.divider()

        st.subheader("Simulação IoT (Demo)")
        st.info(
            "Ambiente de demonstração: os LEDs e eventos IoT são **simulados em software**. "
            "Não há sensores físicos conectados."
        )

        if st.button("⚡ Simular 1 Evento IoT", use_container_width=True):
            mesa_sorteada = random.choice(dados["mesas"])
            novo_estado = random.choice(
                [e for e in ESTADOS_LISTA if e != mesa_sorteada["estado_atual"]]
            )
            registrar_mudanca_estado(
                dados,
                mesa_id=mesa_sorteada["id"],
                novo_estado=novo_estado,
                origem="simulacao_sensor_iot",
            )
            sincronizar_widgets_estado(dados)
            st.session_state.ultimo_aviso = (
                f"IoT simulado: {mesa_sorteada['nome']} ({mesa_sorteada['salao']}) -> {novo_estado}."
            )
            st.rerun()

        if st.button("🔥 Simular Pico (5 Eventos IoT)", use_container_width=True):
            mesas_sorteadas = random.sample(dados["mesas"], k=5)
            for mesa_sorteada in mesas_sorteadas:
                novo_estado = random.choice(
                    [e for e in ESTADOS_LISTA if e != mesa_sorteada["estado_atual"]]
                )
                registrar_mudanca_estado(
                    dados,
                    mesa_id=mesa_sorteada["id"],
                    novo_estado=novo_estado,
                    origem="simulacao_pico_iot",
                    salvar=False,
                )
            salvar_dados(dados)
            sincronizar_widgets_estado(dados)
            st.session_state.ultimo_aviso = "Pico simulado: 5 mesas atualizadas simultaneamente!"
            st.rerun()

        if st.button("🔄 Reiniciar 50 Mesas (Padrão)", use_container_width=True):
            st.session_state.dados_salao = criar_estrutura_inicial()
            sincronizar_widgets_estado(st.session_state.dados_salao)
            st.session_state.ultimo_aviso = "Cenário de 50 mesas reiniciado com sucesso."
            st.rerun()

        st.divider()
        st.subheader("Filtros do Salão")
        nomes_saloes = [s["nome"] for s in SALOES_CONFIG]
        filtro_salao = st.selectbox("Salão", ["Todos os salões (50)"] + nomes_saloes)
        filtro_estado = st.selectbox("Estado da mesa", ["Todos"] + ESTADOS_LISTA)
        busca_mesa = st.text_input("Buscar mesa (ex.: 14 ou S2)", value="").strip().lower()

        st.divider()
        st.caption(f"📄 Integração ativa: `{ARQUIVO_JSON.name}`")
        st.caption(f"🕒 Atualizado em: `{formatar_hora(dados['metadados']['ultima_atualizacao'])}`")

    # --------------------------------------------------------------------------
    # CABEÇALHO E AVISO DE SIMULAÇÃO
    # --------------------------------------------------------------------------
    st.title("🍽️ Gestão Inteligente de Mesas")
    st.caption(f"Projeto **{PROJETO_NOME}** • {UNIDADE_RESTAURANTE} • 2 Salões / 50 Mesas")

    st.markdown(
        """
        <div class="sim-banner">
            ⚠️ <strong>MODO DEMONSTRAÇÃO (IoT SIMULADO):</strong>
            Os indicadores luminosos (LEDs) e atualizações de sensores exibidos neste painel são simulados
            para validação do MVP com 50 mesas. Nenhum hardware físico está conectado nesta etapa.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.ultimo_aviso:
        st.toast(st.session_state.ultimo_aviso, icon="✅")
        st.session_state.ultimo_aviso = ""

    # --------------------------------------------------------------------------
    # MÉTRICAS OPERACIONAIS GLOBAIS (50 MESAS)
    # --------------------------------------------------------------------------
    m = dados["metricas"]
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        renderizar_kpi(
            "Total de Mesas",
            m["total_mesas"],
            f"Ocupação ativa: {m['taxa_ocupacao_percentual']}%",
            "#94a3b8",
        )
    with col2:
        renderizar_kpi("Livres", m["mesas_livres"], "LED Verde (disponível)", "#22c55e")
    with col3:
        renderizar_kpi("Ocupadas", m["mesas_ocupadas"], "LED Vermelho (em uso)", "#ef4444")
    with col4:
        renderizar_kpi(
            "Aguardando Limpeza",
            m["mesas_aguardando_limpeza"],
            "LED Amarelo (higienização)",
            "#eab308",
        )
    with col5:
        renderizar_kpi(
            "Aguardando Atendimento",
            m["mesas_aguardando_atendimento"],
            "LED Azul (chamar garçom)",
            "#3b82f6",
        )

    st.markdown(
        """
        <div class="legend-bar">
            <strong>Indicadores Luminosos IoT (Simulados):</strong>
            <span class="legend-item">
                <span class="led-dot" style="background:#22c55e; box-shadow:0 0 8px #22c55e;"></span> Verde: Livre
            </span>
            <span class="legend-item">
                <span class="led-dot" style="background:#ef4444; box-shadow:0 0 8px #ef4444;"></span> Vermelho: Ocupada
            </span>
            <span class="legend-item">
                <span class="led-dot led-pulse" style="background:#eab308; box-shadow:0 0 8px #eab308;"></span> Amarelo: Aguardando limpeza
            </span>
            <span class="legend-item">
                <span class="led-dot led-pulse" style="background:#3b82f6; box-shadow:0 0 8px #3b82f6;"></span> Azul: Aguardando atendimento
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # ABAS PRINCIPAIS
    # --------------------------------------------------------------------------
    aba_planta, aba_historico, aba_json = st.tabs(
        [
            "🗺️ Planta dos Salões (50 Mesas)",
            f"🕒 Histórico de Alterações ({len(dados['historico_eventos'])})",
            "🔗 Integração JSON (Inteligência Operacional)",
        ]
    )

    # ABA 1: PLANTA VISUAL DOS 2 SALÕES (GRADE 5x5 POR SALÃO)
    with aba_planta:
        mesas_filtradas = [
            mesa
            for mesa in dados["mesas"]
            if (filtro_salao == "Todos os salões (50)" or mesa["salao"] == filtro_salao)
            and (filtro_estado == "Todos" or mesa["estado_atual"] == filtro_estado)
            and (
                not busca_mesa
                or busca_mesa in mesa["nome"].lower()
                or busca_mesa in mesa["id"].lower()
            )
        ]

        if not mesas_filtradas:
            st.warning("Nenhuma mesa encontrada com os filtros aplicados.")
        else:
            saloes_visiveis = [
                s["nome"]
                for s in SALOES_CONFIG
                if any(mesa["salao"] == s["nome"] for mesa in mesas_filtradas)
            ]

            for nome_salao in saloes_visiveis:
                resumo_salao = m["por_salao"][nome_salao]
                renderizar_cabecalho_salao(nome_salao, resumo_salao)

                mesas_do_salao = [mesa for mesa in mesas_filtradas if mesa["salao"] == nome_salao]

                # Grade 5 colunas por linha -> 25 mesas = matriz exata 5x5
                for i in range(0, len(mesas_do_salao), 5):
                    cols = st.columns(5)
                    for col, mesa in zip(cols, mesas_do_salao[i : i + 5]):
                        with col:
                            renderizar_card_mesa(mesa)
                            select_key = f"select_{mesa['id']}"
                            st.selectbox(
                                f"Estado {mesa['nome']}",
                                options=ESTADOS_LISTA,
                                key=select_key,
                                label_visibility="collapsed",
                                on_change=ao_alterar_mesa,
                                args=(mesa["id"], select_key),
                            )

    # ABA 2: HISTÓRICO DE ALTERAÇÕES
    with aba_historico:
        eventos = dados["historico_eventos"]
        if not eventos:
            st.info(
                "Nenhuma alteração registrada ainda. Altere o estado de qualquer mesa ou use "
                "os botões de simulação IoT na barra lateral."
            )
        else:
            df_eventos = pd.DataFrame(eventos)[
                [
                    "horario_formatado",
                    "mesa_id",
                    "mesa_nome",
                    "salao",
                    "estado_anterior",
                    "novo_estado",
                    "led_iot_simulado",
                    "origem",
                ]
            ].rename(
                columns={
                    "horario_formatado": "Data e Hora",
                    "mesa_id": "ID Mesa",
                    "mesa_nome": "Mesa",
                    "salao": "Salão",
                    "estado_anterior": "Estado Anterior",
                    "novo_estado": "Novo Estado",
                    "led_iot_simulado": "LED IoT",
                    "origem": "Origem",
                }
            )
            st.dataframe(df_eventos, use_container_width=True, hide_index=True)

    # ABA 3: ARQUIVO JSON PARA INTEGRAÇÃO CENTRAL
    with aba_json:
        st.markdown(
            f"""
            O arquivo **`dados_mesas.json`** é atualizado automaticamente a cada alteração e já inclui
            o resumo geral das **50 mesas**, o detalhamento **por salão** e o **histórico de eventos**
            para consumo futuro pela **Inteligência Operacional central** do projeto **{PROJETO_NOME}**.
            """
        )

        json_str = json.dumps(dados, ensure_ascii=False, indent=2)
        col_a, col_b = st.columns([2, 1])
        with col_a:
            st.caption(f"Caminho local gerado: `{ARQUIVO_JSON}`")
        with col_b:
            st.download_button(
                label="⬇️ Baixar dados_mesas.json",
                data=json_str.encode("utf-8"),
                file_name="dados_mesas.json",
                mime="application/json",
                use_container_width=True,
            )

        st.json(dados, expanded=False)


if __name__ == "__main__":
    main()
    