from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

# ==============================================================================
# CONFIGURAÇÕES GERAIS DO MÓDULO
# ==============================================================================
PROJETO_NOME = "Até a Primeira Garfada"
MODULO_ID = "fluxo_inteligente_atendimento"
MODULO_TITULO = "Fluxo Inteligente de Atendimento e Filas"
UNIDADE_RESTAURANTE = "Bovinu’S Grill & Beer - Augusta"
ORIGEM_DADO_PADRAO = "simulacao_demo"

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_JSON = BASE_DIR / "dados_fluxo.json"

LIMITE_FILA_PADRAO = 12
LIMITE_TEMPO_PADRAO = 10.0  # minutos

# Etapas fixas do percurso do cliente no restaurante
ETAPAS_TEMPLATE: list[dict[str, Any]] = [
    {
        "etapa_id": "ETP-01",
        "ordem": 1,
        "nome": "Entrada e recepção",
        "tipo": "fila",
        "fator_min_por_cliente": 0.7,
        "clientes_iniciais": 6,
        "acao_recomendada": "Agilizar triagem na recepção e direcionar grupos para o salão com menor lotação.",
    },
    {
        "etapa_id": "ETP-02",
        "ordem": 2,
        "nome": "Acesso ao buffet",
        "tipo": "fila",
        "fator_min_por_cliente": 0.9,
        "clientes_iniciais": 10,
        "acao_recomendada": "Liberar circulação pelos dois lados do buffet e acelerar a reposição das cubas principais.",
    },
    {
        "etapa_id": "ETP-03",
        "ordem": 3,
        "nome": "Passagem pelas balanças",
        "tipo": "fila",
        "fator_min_por_cliente": 1.2,
        "clientes_iniciais": 11,
        "acao_recomendada": "Ativar balança auxiliar e destacar um colaborador para orientar o fluxo de pesagem.",
    },
    {
        "etapa_id": "ETP-04",
        "ordem": 4,
        "nome": "Busca por mesa",
        "tipo": "fila",
        "fator_min_por_cliente": 0.8,
        "clientes_iniciais": 5,
        "acao_recomendada": "Acionar apoio para agilizar a limpeza de mesas e sinalizar lugares livres no salão superior.",
    },
    {
        "etapa_id": "ETP-05",
        "ordem": 5,
        "nome": "Ocupação e início da refeição",
        "tipo": "refeicao",
        "fator_min_por_cliente": 0.0,
        "clientes_iniciais": 34,
        "acao_recomendada": "Reforçar equipe de salão para atendimento de bebidas e giro organizado das mesas.",
    },
]

STATUS_VISUAL: dict[str, dict[str, str]] = {
    "Normal": {
        "cor": "#22c55e",
        "bg": "#052e16",
        "borda": "#16a34a",
        "badge_texto": "Normal",
    },
    "Atenção": {
        "cor": "#eab308",
        "bg": "#422006",
        "borda": "#ca8a04",
        "badge_texto": "Atenção",
    },
    "Gargalo": {
        "cor": "#ef4444",
        "bg": "#450a0a",
        "borda": "#dc2626",
        "badge_texto": "Gargalo",
    },
}


# ==============================================================================
# REGRAS DE NEGÓCIO, CÁLCULOS E ALERTAS
# ==============================================================================
def agora_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def formatar_hora(iso_str: str) -> str:
    try:
        return datetime.fromisoformat(iso_str).strftime("%H:%M:%S")
    except ValueError:
        return iso_str


def calcular_tempo_espera(etapa: dict[str, Any]) -> float:
    if etapa["tipo"] == "refeicao":
        return 0.0
    return round(etapa["quantidade_clientes"] * etapa["fator_min_por_cliente"], 1)


def classificar_status_etapa(
    etapa: dict[str, Any],
    limite_fila: int,
    limite_tempo: float,
) -> str:
    qtd = etapa["quantidade_clientes"]
    tempo = etapa["tempo_espera_estimado_min"]

    if etapa["tipo"] == "refeicao":
        if qtd >= 65:
            return "Gargalo"
        if qtd >= 48:
            return "Atenção"
        return "Normal"

    if qtd >= limite_fila or tempo >= limite_tempo:
        return "Gargalo"
    if qtd >= max(1, int(limite_fila * 0.75)) or tempo >= round(limite_tempo * 0.75, 1):
        return "Atenção"
    return "Normal"


def gerar_alertas(
    etapas: list[dict[str, Any]],
    limite_fila: int,
    limite_tempo: float,
) -> list[dict[str, Any]]:
    alertas: list[dict[str, Any]] = []
    etapas_fila = [e for e in etapas if e["tipo"] == "fila"]
    etapas_em_gargalo = 0

    for etapa in etapas:
        qtd = etapa["quantidade_clientes"]
        tempo = etapa["tempo_espera_estimado_min"]
        nome = etapa["nome"]

        if etapa["tipo"] == "fila":
            fila_alta = qtd >= limite_fila
            tempo_alto = tempo >= limite_tempo

            if fila_alta or tempo_alto:
                etapas_em_gargalo += 1

            if fila_alta and tempo_alto:
                alertas.append(
                    {
                        "severidade": "Crítico",
                        "tipo": "Fila e tempo acima do limite",
                        "etapa": nome,
                        "problema": (
                            f"{qtd} clientes aguardando (limite: {limite_fila}) com espera estimada "
                            f"de {tempo:.1f} min (limite: {limite_tempo:.0f} min)."
                        ),
                        "acao_recomendada": etapa["acao_recomendada"],
                    }
                )
            elif fila_alta:
                alertas.append(
                    {
                        "severidade": "Crítico",
                        "tipo": "Fila acima do limite",
                        "etapa": nome,
                        "problema": f"{qtd} clientes acumulados nesta etapa (limite configurado: {limite_fila}).",
                        "acao_recomendada": etapa["acao_recomendada"],
                    }
                )
            elif tempo_alto:
                alertas.append(
                    {
                        "severidade": "Crítico",
                        "tipo": "Tempo de espera elevado",
                        "etapa": nome,
                        "problema": f"Tempo estimado em {tempo:.1f} min, acima do limite de {limite_tempo:.0f} min.",
                        "acao_recomendada": etapa["acao_recomendada"],
                    }
                )
            elif etapa["status_operacional"] == "Atenção":
                alertas.append(
                    {
                        "severidade": "Atenção",
                        "tipo": "Acúmulo de clientes",
                        "etapa": nome,
                        "problema": f"Movimento elevado ({qtd} clientes; ~{tempo:.1f} min) se aproximando do limite.",
                        "acao_recomendada": etapa["acao_recomendada"],
                    }
                )
        else:
            if etapa["status_operacional"] == "Gargalo":
                alertas.append(
                    {
                        "severidade": "Crítico",
                        "tipo": "Possível sobrecarga no atendimento",
                        "etapa": nome,
                        "problema": f"Salão com {qtd} clientes em refeição simultânea, exigindo maior apoio da equipe.",
                        "acao_recomendada": etapa["acao_recomendada"],
                    }
                )

    total_aguardando = sum(e["quantidade_clientes"] for e in etapas_fila)
    if etapas_em_gargalo >= 2 or total_aguardando >= int(limite_fila * 2.8):
        alertas.insert(
            0,
            {
                "severidade": "Crítico",
                "tipo": "Possível sobrecarga no atendimento",
                "etapa": "Operação Geral",
                "problema": (
                    f"{total_aguardando} clientes aguardando no percurso com {etapas_em_gargalo} "
                    "ponto(s) crítico(s) simultâneo(s)."
                ),
                "acao_recomendada": (
                    "Ativar protocolo de horário de pico: redistribuir equipe entre balanças, buffet "
                    "e limpeza de mesas para liberar o fluxo até a primeira garfada."
                ),
            },
        )

    return alertas


def recalcular_estado_operacional(dados: dict[str, Any]) -> None:
    limite_fila = int(dados["configuracoes"]["limite_fila_clientes"])
    limite_tempo = float(dados["configuracoes"]["limite_tempo_espera_min"])

    for etapa in dados["etapas"]:
        etapa["tempo_espera_estimado_min"] = calcular_tempo_espera(etapa)
        etapa["status_operacional"] = classificar_status_etapa(
            etapa,
            limite_fila=limite_fila,
            limite_tempo=limite_tempo,
        )

    etapas_fila = [e for e in dados["etapas"] if e["tipo"] == "fila"]
    total_aguardando = sum(e["quantidade_clientes"] for e in etapas_fila)
    total_em_atendimento = sum(e["quantidade_clientes"] for e in dados["etapas"])

    tempos_espera = [e["tempo_espera_estimado_min"] for e in etapas_fila]
    tempo_medio_espera = round(sum(tempos_espera) / len(tempos_espera), 1) if tempos_espera else 0.0
    tempo_total_percurso = round(sum(tempos_espera), 1)

    etapa_pico = max(etapas_fila, key=lambda e: e["quantidade_clientes"])
    if etapa_pico["quantidade_clientes"] == 0:
        maior_concentracao = "Fluxo livre"
        maior_concentracao_qtd = 0
    else:
        maior_concentracao = etapa_pico["nome"]
        maior_concentracao_qtd = etapa_pico["quantidade_clientes"]

    alertas = gerar_alertas(dados["etapas"], limite_fila=limite_fila, limite_tempo=limite_tempo)
    etapas_criticas = [e["nome"] for e in dados["etapas"] if e["status_operacional"] == "Gargalo"]

    dados["indicadores"] = {
        "clientes_em_atendimento": total_em_atendimento,
        "clientes_aguardando": total_aguardando,
        "tempo_medio_espera_min": tempo_medio_espera,
        "tempo_total_estimado_percurso_min": tempo_total_percurso,
        "etapa_maior_concentracao": maior_concentracao,
        "clientes_maior_concentracao": maior_concentracao_qtd,
        "total_gargalos_ativos": len(etapas_criticas),
    }
    dados["alertas_ativos"] = alertas
    dados["metadados"]["ultima_atualizacao"] = agora_iso()


# ==============================================================================
# PERSISTÊNCIA E CONTRATO JSON DE INTEGRAÇÃO
# ==============================================================================
def salvar_dados(dados: dict[str, Any]) -> None:
    recalcular_estado_operacional(dados)
    ARQUIVO_JSON.parent.mkdir(parents=True, exist_ok=True)
    with ARQUIVO_JSON.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def criar_estrutura_inicial(
    limite_fila: int = LIMITE_FILA_PADRAO,
    limite_tempo: float = LIMITE_TEMPO_PADRAO,
) -> dict[str, Any]:
    timestamp = agora_iso()
    etapas = []
    for item in ETAPAS_TEMPLATE:
        etapas.append(
            {
                "etapa_id": item["etapa_id"],
                "ordem": item["ordem"],
                "nome": item["nome"],
                "tipo": item["tipo"],
                "fator_min_por_cliente": item["fator_min_por_cliente"],
                "quantidade_clientes": item["clientes_iniciais"],
                "tempo_espera_estimado_min": 0.0,
                "status_operacional": "Normal",
                "acao_recomendada": item["acao_recomendada"],
                "horario_ultima_atualizacao": timestamp,
                "origem_dado": ORIGEM_DADO_PADRAO,
            }
        )

    dados = {
        "metadados": {
            "projeto": PROJETO_NOME,
            "modulo": MODULO_ID,
            "unidade": UNIDADE_RESTAURANTE,
            "versao_schema": "1.0.0",
            "modo_simulacao": True,
            "sensores_fisicos_conectados": False,
            "origem_dado": ORIGEM_DADO_PADRAO,
            "ultima_atualizacao": timestamp,
        },
        "configuracoes": {
            "limite_fila_clientes": limite_fila,
            "limite_tempo_espera_min": limite_tempo,
        },
        "indicadores": {},
        "etapas": etapas,
        "alertas_ativos": [],
        "historico_eventos": [],
    }
    salvar_dados(dados)
    return dados


def carregar_dados() -> dict[str, Any]:
    if ARQUIVO_JSON.exists():
        try:
            with ARQUIVO_JSON.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if (
                isinstance(dados, dict)
                and isinstance(dados.get("etapas"), list)
                and len(dados["etapas"]) == len(ETAPAS_TEMPLATE)
                and isinstance(dados.get("historico_eventos"), list)
            ):
                recalcular_estado_operacional(dados)
                return dados
        except (json.JSONDecodeError, OSError):
            pass
    return criar_estrutura_inicial()


def registrar_evento(
    dados: dict[str, Any],
    etapa: dict[str, Any],
    acao: str,
    origem_dado: str = ORIGEM_DADO_PADRAO,
) -> None:
    agora = datetime.now()
    timestamp_iso = agora.isoformat(timespec="seconds")
    etapa["horario_ultima_atualizacao"] = timestamp_iso
    etapa["origem_dado"] = origem_dado

    recalcular_estado_operacional(dados)

    evento = {
        "evento_id": f"FLX-{len(dados['historico_eventos']) + 1:04d}",
        "modulo": MODULO_ID,
        "unidade": UNIDADE_RESTAURANTE,
        "etapa_fluxo": etapa["nome"],
        "acao_simulada": acao,
        "quantidade_clientes": etapa["quantidade_clientes"],
        "tempo_espera_estimado_min": etapa["tempo_espera_estimado_min"],
        "status_operacional": etapa["status_operacional"],
        "horario_evento": timestamp_iso,
        "horario_formatado": agora.strftime("%d/%m/%Y %H:%M:%S"),
        "origem_dado": origem_dado,
    }
    dados["historico_eventos"].insert(0, evento)
    salvar_dados(dados)


# ==============================================================================
# AÇÕES DE SIMULAÇÃO DO FLUXO
# ==============================================================================
def simular_entrada_clientes(dados: dict[str, Any], quantidade: int) -> str:
    etapa_entrada = dados["etapas"][0]
    etapa_entrada["quantidade_clientes"] += quantidade
    registrar_evento(
        dados,
        etapa=etapa_entrada,
        acao=f"Entrada simulada de +{quantidade} cliente(s)",
        origem_dado="simulacao_entrada_clientes",
    )
    return f"+{quantidade} cliente(s) chegaram em '{etapa_entrada['nome']}'."


def simular_movimentacao_etapas(dados: dict[str, Any]) -> str:
    etapas = dados["etapas"]
    movimentados = []

    # Finalização de alguns clientes que já concluíram a refeição (etapa 5)
    saidas = min(etapas[4]["quantidade_clientes"], random.randint(2, 5))
    etapas[4]["quantidade_clientes"] -= saidas

    # Avança clientes de trás para frente (4->5, 3->4, 2->3, 1->2)
    for idx in range(len(etapas) - 2, -1, -1):
        atual = etapas[idx]
        proxima = etapas[idx + 1]
        if atual["quantidade_clientes"] > 0:
            qtd_mover = min(atual["quantidade_clientes"], random.randint(2, 5))
            atual["quantidade_clientes"] -= qtd_mover
            proxima["quantidade_clientes"] += qtd_mover
            movimentados.append((atual, proxima, qtd_mover))

    agora = datetime.now()
    timestamp_iso = agora.isoformat(timespec="seconds")
    for etapa in etapas:
        etapa["horario_ultima_atualizacao"] = timestamp_iso
        etapa["origem_dado"] = "simulacao_movimentacao_etapas"

    recalcular_estado_operacional(dados)

    etapa_destaque = max(etapas[:4], key=lambda e: e["quantidade_clientes"])
    resumo_mov = ", ".join(f"{q} ({a['ordem']}→{p['ordem']})" for a, p, q in reversed(movimentados))
    if not resumo_mov:
        resumo_mov = "Sem clientes para avançar"

    evento = {
        "evento_id": f"FLX-{len(dados['historico_eventos']) + 1:04d}",
        "modulo": MODULO_ID,
        "unidade": UNIDADE_RESTAURANTE,
        "etapa_fluxo": etapa_destaque["nome"],
        "acao_simulada": f"Movimentação do fluxo: {resumo_mov}; saídas da refeição: {saidas}",
        "quantidade_clientes": etapa_destaque["quantidade_clientes"],
        "tempo_espera_estimado_min": etapa_destaque["tempo_espera_estimado_min"],
        "status_operacional": etapa_destaque["status_operacional"],
        "horario_evento": timestamp_iso,
        "horario_formatado": agora.strftime("%d/%m/%Y %H:%M:%S"),
        "origem_dado": "simulacao_movimentacao_etapas",
    }
    dados["historico_eventos"].insert(0, evento)
    salvar_dados(dados)
    return "Movimentação entre etapas simulada com sucesso."


def simular_ajuste_fila(dados: dict[str, Any], nome_etapa: str, delta: int) -> str:
    for etapa in dados["etapas"]:
        if etapa["nome"] == nome_etapa:
            anterior = etapa["quantidade_clientes"]
            etapa["quantidade_clientes"] = max(0, anterior + delta)
            diferenca_real = etapa["quantidade_clientes"] - anterior
            sinal = f"+{diferenca_real}" if diferenca_real >= 0 else f"{diferenca_real}"
            tipo_acao = "Aumento simulado de fila" if delta > 0 else "Redução simulada de fila"
            registrar_evento(
                dados,
                etapa=etapa,
                acao=f"{tipo_acao} ({sinal} clientes)",
                origem_dado="simulacao_ajuste_fila",
            )
            return f"'{nome_etapa}': {anterior} → {etapa['quantidade_clientes']} clientes."
    return "Etapa não encontrada."


# ==============================================================================
# ESTILIZAÇÃO VISUAL CLEAN E OPERACIONAL
# ==============================================================================
def aplicar_estilos() -> None:
    st.markdown(
        """
        <style>
        .demo-banner {
            background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
            border-left: 5px solid #f59e0b;
            border-radius: 10px;
            padding: 10px 16px;
            margin-bottom: 16px;
            color: #f8fafc;
            font-size: 0.9rem;
        }
        .demo-banner strong { color: #fbbf24; }
        .kpi-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-top: 4px solid var(--accent);
            border-radius: 12px;
            padding: 14px 16px;
            color: #f8fafc;
            margin-bottom: 10px;
        }
        .kpi-label {
            font-size: 0.78rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-bottom: 4px;
        }
        .kpi-value {
            font-size: 1.75rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.15;
        }
        .kpi-value-sm {
            font-size: 1.18rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.25;
            margin-top: 4px;
        }
        .kpi-sub {
            font-size: 0.78rem;
            color: #cbd5e1;
            margin-top: 4px;
        }
        .stage-card {
            border-radius: 14px;
            padding: 14px;
            min-height: 188px;
            color: #f8fafc;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
        }
        .stage-gargalo {
            box-shadow: 0 0 0 1px #ef4444, 0 0 18px rgba(239, 68, 68, 0.32);
        }
        .stage-step {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #cbd5e1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }
        .stage-title {
            font-size: 0.98rem;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 10px;
        }
        .stage-count {
            font-size: 1.9rem;
            font-weight: 800;
            line-height: 1;
        }
        .stage-unit {
            font-size: 0.8rem;
            color: #cbd5e1;
            font-weight: 400;
        }
        .stage-wait {
            font-size: 0.84rem;
            color: #e2e8f0;
            margin: 8px 0 10px 0;
        }
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.18);
            width: fit-content;
        }
        .status-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            display: inline-block;
        }
        .arrow-box {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 188px;
            font-size: 1.4rem;
            color: #64748b;
            font-weight: 700;
        }
        .alert-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-left: 5px solid var(--alert-color);
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 10px;
            color: #f8fafc;
        }
        .alert-head {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 8px;
            margin-bottom: 4px;
            font-size: 0.92rem;
            font-weight: 700;
        }
        .alert-problem {
            font-size: 0.86rem;
            color: #e2e8f0;
            margin-bottom: 4px;
        }
        .alert-action {
            font-size: 0.86rem;
            color: #93c5fd;
        }
        .ok-box {
            background: #052e16;
            border: 1px solid #16a34a;
            border-radius: 10px;
            padding: 12px 16px;
            color: #dcfce7;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def renderizar_kpi(
    titulo: str,
    valor: str,
    subtitulo: str,
    cor: str,
    texto_compacto: bool = False,
) -> None:
    classe_valor = "kpi-value-sm" if texto_compacto else "kpi-value"
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent: {cor};">
            <div class="kpi-label">{titulo}</div>
            <div class="{classe_valor}">{valor}</div>
            <div class="kpi-sub">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_card_etapa(etapa: dict[str, Any]) -> None:
    status = etapa["status_operacional"]
    vis = STATUS_VISUAL[status]
    classe_extra = "stage-gargalo" if status == "Gargalo" else ""

    if etapa["tipo"] == "refeicao":
        linha_tempo = "🍽️ Já acomodados na mesa"
    else:
        linha_tempo = f"⏱️ Espera estimada: <b>{etapa['tempo_espera_estimado_min']:.1f} min</b>"

    st.markdown(
        f"""
        <div class="stage-card {classe_extra}" style="
            background: linear-gradient(155deg, {vis['bg']} 0%, #0f172a 100%);
            border: 2px solid {vis['borda']};
        ">
            <div>
                <div class="stage-step">
                    <span>Etapa {etapa['ordem']}</span>
                    <span>{etapa['etapa_id']}</span>
                </div>
                <div class="stage-title">{etapa['nome']}</div>
                <div class="stage-count">
                    {etapa['quantidade_clientes']} <span class="stage-unit">clientes</span>
                </div>
                <div class="stage-wait">{linha_tempo}</div>
            </div>
            <div class="status-pill">
                <span class="status-dot" style="background:{vis['cor']}; box-shadow: 0 0 8px {vis['cor']};"></span>
                <span>{vis['badge_texto']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==============================================================================
# INTERFACE PRINCIPAL
# ==============================================================================
def main() -> None:
    st.set_page_config(
        page_title=f"{MODULO_TITULO} | {PROJETO_NOME}",
        page_icon="🚶",
        layout="wide",
    )
    aplicar_estilos()

    if "dados_fluxo" not in st.session_state:
        st.session_state.dados_fluxo = carregar_dados()

    if "ultimo_aviso_fluxo" not in st.session_state:
        st.session_state.ultimo_aviso_fluxo = ""

    dados = st.session_state.dados_fluxo

    # --------------------------------------------------------------------------
    # SIDEBAR — CONTROLES DE SIMULAÇÃO E LIMITES CONFIGURÁVEIS
    # --------------------------------------------------------------------------
    with st.sidebar:
        st.title("🥩 Até a Primeira Garfada")
        st.caption(f"**Unidade:** {UNIDADE_RESTAURANTE}")
        st.caption(f"**Módulo:** {MODULO_TITULO}")
        st.divider()

        st.subheader("Controles da Simulação")
        st.info(
            "Demonstração com dados **simulados em software**. "
            "Não há câmeras, sensores físicos ou integração externa ativa nesta etapa."
        )

        qtd_entrada = st.slider("Clientes na entrada simulada", min_value=1, max_value=10, value=4)
        if st.button("➕ Simular Entrada de Clientes", use_container_width=True):
            msg = simular_entrada_clientes(dados, quantidade=qtd_entrada)
            st.session_state.ultimo_aviso_fluxo = msg
            st.rerun()

        if st.button("➡️ Simular Movimentação entre Etapas", use_container_width=True):
            msg = simular_movimentacao_etapas(dados)
            st.session_state.ultimo_aviso_fluxo = msg
            st.rerun()

        st.markdown("**Ajustar fila de uma etapa**")
        nomes_etapas = [e["nome"] for e in dados["etapas"]]
        etapa_selecionada = st.selectbox(
            "Selecione a etapa",
            options=nomes_etapas,
            index=2,  # Passagem pelas balanças por padrão
            label_visibility="collapsed",
        )
        col_inc, col_dec = st.columns(2)
        with col_inc:
            if st.button("📈 +4 Fila", use_container_width=True):
                msg = simular_ajuste_fila(dados, etapa_selecionada, delta=4)
                st.session_state.ultimo_aviso_fluxo = msg
                st.rerun()
        with col_dec:
            if st.button("📉 -4 Fila", use_container_width=True):
                msg = simular_ajuste_fila(dados, etapa_selecionada, delta=-4)
                st.session_state.ultimo_aviso_fluxo = msg
                st.rerun()

        if st.button("🔄 Reiniciar Demonstração", use_container_width=True):
            st.session_state.dados_fluxo = criar_estrutura_inicial(
                limite_fila=dados["configuracoes"]["limite_fila_clientes"],
                limite_tempo=dados["configuracoes"]["limite_tempo_espera_min"],
            )
            st.session_state.ultimo_aviso_fluxo = "Demonstração reiniciada para o cenário inicial."
            st.rerun()

        st.divider()
        st.subheader("Limites de Alerta")
        novo_limite_fila = st.slider(
            "Limite máximo de fila por etapa (clientes)",
            min_value=5,
            max_value=25,
            value=int(dados["configuracoes"]["limite_fila_clientes"]),
        )
        novo_limite_tempo = st.slider(
            "Limite de espera por etapa (minutos)",
            min_value=4,
            max_value=20,
            value=int(dados["configuracoes"]["limite_tempo_espera_min"]),
        )

        if (
            novo_limite_fila != dados["configuracoes"]["limite_fila_clientes"]
            or float(novo_limite_tempo) != float(dados["configuracoes"]["limite_tempo_espera_min"])
        ):
            dados["configuracoes"]["limite_fila_clientes"] = novo_limite_fila
            dados["configuracoes"]["limite_tempo_espera_min"] = float(novo_limite_tempo)
            salvar_dados(dados)
            st.rerun()

        st.divider()
        st.caption(f"📄 Arquivo JSON: `{ARQUIVO_JSON.name}`")
        st.caption(f"🕒 Atualizado em: `{formatar_hora(dados['metadados']['ultima_atualizacao'])}`")

    # --------------------------------------------------------------------------
    # CABEÇALHO E AVISO DE DEMONSTRAÇÃO
    # --------------------------------------------------------------------------
    st.title("🚶 Fluxo Inteligente de Atendimento e Filas")
    st.caption(f"Projeto **{PROJETO_NOME}** • {UNIDADE_RESTAURANTE} • Hackathon FMU 2026.2")

    st.markdown(
        """
        <div class="demo-banner">
            ⚠️ <strong>MODO DEMONSTRAÇÃO (DADOS SIMULADOS):</strong>
            As contagens de clientes, tempos de espera e movimentações abaixo são simulados para
            validação operacional do MVP. Não há câmeras, sensores ou hardware físico conectados.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.ultimo_aviso_fluxo:
        st.toast(st.session_state.ultimo_aviso_fluxo, icon="✅")
        st.session_state.ultimo_aviso_fluxo = ""

    # --------------------------------------------------------------------------
    # INDICADORES PRINCIPAIS NO TOPO
    # --------------------------------------------------------------------------
    ind = dados["indicadores"]
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        renderizar_kpi(
            "Clientes em Atendimento",
            str(ind["clientes_em_atendimento"]),
            "Total ativo no restaurante (fluxo + salão)",
            "#38bdf8",
        )
    with c2:
        cor_aguardando = "#ef4444" if ind["total_gargalos_ativos"] > 0 else "#22c55e"
        renderizar_kpi(
            "Clientes Aguardando",
            str(ind["clientes_aguardando"]),
            "Etapas 1 a 4 (até a primeira garfada)",
            cor_aguardando,
        )
    with c3:
        limite_tempo_cfg = dados["configuracoes"]["limite_tempo_espera_min"]
        cor_tempo = "#ef4444" if ind["tempo_medio_espera_min"] >= limite_tempo_cfg else "#f59e0b"
        renderizar_kpi(
            "Tempo Médio de Espera",
            f"{ind['tempo_medio_espera_min']:.1f} min",
            f"Percurso estimado total: {ind['tempo_total_estimado_percurso_min']:.1f} min",
            cor_tempo,
        )
    with c4:
        renderizar_kpi(
            "Maior Concentração",
            ind["etapa_maior_concentracao"],
            f"{ind['clientes_maior_concentracao']} cliente(s) nesta etapa",
            "#a855f7",
            texto_compacto=True,
        )

    # --------------------------------------------------------------------------
    # MAPA SIMPLIFICADO DO FLUXO DO CLIENTE
    # --------------------------------------------------------------------------
    st.subheader("🗺️ Mapa do Fluxo do Cliente")
    st.caption(
        f"Limites ativos — Fila: **{dados['configuracoes']['limite_fila_clientes']} clientes/etapa** • "
        f"Espera: **{dados['configuracoes']['limite_tempo_espera_min']:.0f} min/etapa**"
    )

    # 5 cards de etapa intercalados por 4 setas direcionais
    colunas_mapa = st.columns([3, 0.45, 3, 0.45, 3, 0.45, 3, 0.45, 3])
    for idx, etapa in enumerate(dados["etapas"]):
        with colunas_mapa[idx * 2]:
            renderizar_card_etapa(etapa)
        if idx < len(dados["etapas"]) - 1:
            with colunas_mapa[idx * 2 + 1]:
                st.markdown('<div class="arrow-box">→</div>', unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # ALERTAS OPERACIONAIS OBJETIVOS
    # --------------------------------------------------------------------------
    st.markdown("")
    st.subheader(f"🚨 Alertas Operacionais ({len(dados['alertas_ativos'])})")

    if not dados["alertas_ativos"]:
        st.markdown(
            """
            <div class="ok-box">
                ✅ <strong>Operação fluida:</strong> todas as etapas estão dentro dos limites
                configurados de fila e tempo de espera.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for alerta in dados["alertas_ativos"]:
            cor_alerta = "#ef4444" if alerta["severidade"] == "Crítico" else "#eab308"
            icone = "🔴" if alerta["severidade"] == "Crítico" else "🟡"
            st.markdown(
                f"""
                <div class="alert-card" style="--alert-color: {cor_alerta};">
                    <div class="alert-head">
                        <span>{icone} {alerta['tipo']} — {alerta['etapa']}</span>
                        <span>{alerta['severidade']}</span>
                    </div>
                    <div class="alert-problem"><strong>Problema:</strong> {alerta['problema']}</div>
                    <div class="alert-action"><strong>Ação recomendada:</strong> {alerta['acao_recomendada']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------------------------------------
    # ÁREA SECUNDÁRIA — HISTÓRICO E INTEGRAÇÃO JSON
    # --------------------------------------------------------------------------
    st.divider()
    aba_historico, aba_json = st.tabs(
        [
            f"🕒 Histórico de Eventos ({len(dados['historico_eventos'])})",
            "🔗 Integração JSON (Inteligência Operacional)",
        ]
    )

    with aba_historico:
        eventos = dados["historico_eventos"]
        if not eventos:
            st.info(
                "Nenhum evento registrado ainda. Use os controles na barra lateral para simular "
                "entrada de clientes, movimentação entre etapas ou alterações na fila."
            )
        else:
            df_hist = pd.DataFrame(eventos)[
                [
                    "horario_formatado",
                    "etapa_fluxo",
                    "acao_simulada",
                    "quantidade_clientes",
                    "tempo_espera_estimado_min",
                    "status_operacional",
                    "origem_dado",
                ]
            ].rename(
                columns={
                    "horario_formatado": "Horário",
                    "etapa_fluxo": "Etapa do Fluxo",
                    "acao_simulada": "Evento",
                    "quantidade_clientes": "Clientes",
                    "tempo_espera_estimado_min": "Espera (min)",
                    "status_operacional": "Status",
                    "origem_dado": "Origem do Dado",
                }
            )
            st.dataframe(df_hist, use_container_width=True, hide_index=True)

    with aba_json:
        st.markdown(
            f"""
            O arquivo **`dados_fluxo.json`** é atualizado automaticamente a cada evento simulado
            e segue o contrato padronizado para futura integração com os demais módulos do projeto
            **{PROJETO_NOME}**.
            """
        )

        json_str = json.dumps(dados, ensure_ascii=False, indent=2)
        col_path, col_btn = st.columns([2, 1])
        with col_path:
            st.caption(f"Caminho local gerado: `{ARQUIVO_JSON}`")
        with col_btn:
            st.download_button(
                label="⬇️ Baixar dados_fluxo.json",
                data=json_str.encode("utf-8"),
                file_name="dados_fluxo.json",
                mime="application/json",
                use_container_width=True,
            )

        st.json(dados, expanded=False)


if __name__ == "__main__":
    main()
    