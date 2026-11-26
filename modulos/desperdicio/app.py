from __future__ import annotations

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

# ==============================================================================
# CONFIGURAÇÕES GERAIS DO MÓDULO
# ==============================================================================
PROJETO_NOME = "Até a Primeira Garfada"
MODULO_NOME = "desperdicio_experiencia_cliente"
MODULO_TITULO = "Desperdício e Experiência do Cliente"
UNIDADE_RESTAURANTE = "Bovinu'S Grill & Beer - Augusta"
MODO_FUNCIONAMENTO = "simulacao_e_registro_manual"

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_JSON = BASE_DIR / "dados_desperdicio.json"

PERIODOS_LISTA = [
    "Almoço (11h30–13h30)",
    "Almoço Tarde (13h30–15h30)",
    "Jantar / Grill (18h30–22h00)",
]

CATEGORIAS_LISTA = [
    "Carnes & Grelhados",
    "Acompanhamentos",
    "Guarnições & Fritos",
    "Saladas & Frios",
    "Massas",
]

DISPONIBILIDADE_OPCOES = [
    "Alta (reposição constante)",
    "Média (reposição moderada)",
    "Baixa (faltou no buffet)",
]

CATALOGO_ALIMENTOS: dict[str, str] = {
    "Picanha na Brasa": "Carnes & Grelhados",
    "Fraldinha Grelhada": "Carnes & Grelhados",
    "Arroz Branco": "Acompanhamentos",
    "Feijão Carioca": "Acompanhamentos",
    "Farofa da Casa": "Acompanhamentos",
    "Batata Frita": "Guarnições & Fritos",
    "Polenta Frita": "Guarnições & Fritos",
    "Salada de Folhas & Legumes": "Saladas & Frios",
    "Maionese de Batata": "Saladas & Frios",
    "Penne ao Molho Branco": "Massas",
}

REGISTROS_INICIAIS_SIMULADOS = [
    {"alimento": "Picanha na Brasa", "categoria": "Carnes & Grelhados", "periodo": "Almoço (11h30–13h30)", "consumido_kg": 18.5, "descartado_kg": 0.9, "disponibilidade": "Média (reposição moderada)"},
    {"alimento": "Fraldinha Grelhada", "categoria": "Carnes & Grelhados", "periodo": "Almoço (11h30–13h30)", "consumido_kg": 14.0, "descartado_kg": 1.1, "disponibilidade": "Alta (reposição constante)"},
    {"alimento": "Arroz Branco", "categoria": "Acompanhamentos", "periodo": "Almoço (11h30–13h30)", "consumido_kg": 16.2, "descartado_kg": 4.8, "disponibilidade": "Alta (reposição constante)"},
    {"alimento": "Feijão Carioca", "categoria": "Acompanhamentos", "periodo": "Almoço (11h30–13h30)", "consumido_kg": 12.4, "descartado_kg": 2.9, "disponibilidade": "Alta (reposição constante)"},
    {"alimento": "Farofa da Casa", "categoria": "Acompanhamentos", "periodo": "Almoço Tarde (13h30–15h30)", "consumido_kg": 7.5, "descartado_kg": 2.6, "disponibilidade": "Alta (reposição constante)"},
    {"alimento": "Batata Frita", "categoria": "Guarnições & Fritos", "periodo": "Almoço Tarde (13h30–15h30)", "consumido_kg": 11.0, "descartado_kg": 3.7, "disponibilidade": "Média (reposição moderada)"},
    {"alimento": "Polenta Frita", "categoria": "Guarnições & Fritos", "periodo": "Almoço Tarde (13h30–15h30)", "consumido_kg": 5.2, "descartado_kg": 3.4, "disponibilidade": "Alta (reposição constante)"},
    {"alimento": "Salada de Folhas & Legumes", "categoria": "Saladas & Frios", "periodo": "Almoço (11h30–13h30)", "consumido_kg": 9.8, "descartado_kg": 2.1, "disponibilidade": "Alta (reposição constante)"},
    {"alimento": "Maionese de Batata", "categoria": "Saladas & Frios", "periodo": "Jantar / Grill (18h30–22h00)", "consumido_kg": 4.6, "descartado_kg": 2.3, "disponibilidade": "Alta (reposição constante)"},
    {"alimento": "Penne ao Molho Branco", "categoria": "Massas", "periodo": "Jantar / Grill (18h30–22h00)", "consumido_kg": 6.4, "descartado_kg": 3.1, "disponibilidade": "Média (reposição moderada)"},
    {"alimento": "Picanha na Brasa", "categoria": "Carnes & Grelhados", "periodo": "Jantar / Grill (18h30–22h00)", "consumido_kg": 15.8, "descartado_kg": 0.7, "disponibilidade": "Baixa (faltou no buffet)"},
    {"alimento": "Arroz Branco", "categoria": "Acompanhamentos", "periodo": "Jantar / Grill (18h30–22h00)", "consumido_kg": 9.5, "descartado_kg": 2.4, "disponibilidade": "Alta (reposição constante)"},
]

AVALIACOES_INICIAIS_SIMULADAS = [
    {"nota": 5, "periodo": "Almoço (11h30–13h30)", "disponibilidade_percebida": "Alta (reposição constante)", "categoria_destaque": "Carnes & Grelhados", "observacao": "Carnes no ponto e buffet bem abastecido."},
    {"nota": 4, "periodo": "Almoço (11h30–13h30)", "disponibilidade_percebida": "Média (reposição moderada)", "categoria_destaque": "Acompanhamentos", "observacao": "Boa variedade, apenas demora leve na reposição da picanha."},
    {"nota": 3, "periodo": "Almoço Tarde (13h30–15h30)", "disponibilidade_percebida": "Média (reposição moderada)", "categoria_destaque": "Guarnições & Fritos", "observacao": "Polenta e batata frita já estavam frias no fim do almoço."},
    {"nota": 5, "periodo": "Almoço (11h30–13h30)", "disponibilidade_percebida": "Alta (reposição constante)", "categoria_destaque": "Saladas & Frios", "observacao": "Saladas frescas e ótima apresentação."},
    {"nota": 2, "periodo": "Jantar / Grill (18h30–22h00)", "disponibilidade_percebida": "Baixa (faltou no buffet)", "categoria_destaque": "Carnes & Grelhados", "observacao": "Corte principal demorou para ser reposto no horário de pico."},
    {"nota": 4, "periodo": "Jantar / Grill (18h30–22h00)", "disponibilidade_percebida": "Alta (reposição constante)", "categoria_destaque": "Carnes & Grelhados", "observacao": "Experiência muito boa, atendimento rápido."},
    {"nota": 3, "periodo": "Jantar / Grill (18h30–22h00)", "disponibilidade_percebida": "Média (reposição moderada)", "categoria_destaque": "Massas", "observacao": "Massa um pouco ressecada na cuba."},
    {"nota": 5, "periodo": "Almoço (11h30–13h30)", "disponibilidade_percebida": "Alta (reposição constante)", "categoria_destaque": "Carnes & Grelhados", "observacao": "Excelente qualidade e variedade."},
]


# ==============================================================================
# CÁLCULOS ANALÍTICOS, TENDÊNCIAS E RECOMENDAÇÕES
# ==============================================================================
def agora_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def formatar_hora(iso_str: str) -> str:
    try:
        return datetime.fromisoformat(iso_str).strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return iso_str


def calcular_percentual(descartado: float, consumido: float) -> float:
    total = consumido + descartado
    if total <= 0:
        return 0.0
    return round((descartado / total) * 100, 1)


def consolidar_dados_consumo(registros: list[dict[str, Any]]) -> dict[str, Any]:
    if not registros:
        return {"por_alimento": [], "por_categoria": [], "por_periodo": []}

    df = pd.DataFrame(registros)

    # Por alimento
    grp_alimento = (
        df.groupby(["alimento", "categoria"], as_index=False)[["consumido_kg", "descartado_kg"]]
        .sum()
    )
    grp_alimento["total_servido_kg"] = (
        grp_alimento["consumido_kg"] + grp_alimento["descartado_kg"]
    ).round(2)
    grp_alimento["percentual_desperdicio"] = grp_alimento.apply(
        lambda r: calcular_percentual(r["descartado_kg"], r["consumido_kg"]), axis=1
    )
    grp_alimento["consumido_kg"] = grp_alimento["consumido_kg"].round(2)
    grp_alimento["descartado_kg"] = grp_alimento["descartado_kg"].round(2)

    # Por categoria
    grp_cat = df.groupby("categoria", as_index=False)[["consumido_kg", "descartado_kg"]].sum()
    grp_cat["total_servido_kg"] = (grp_cat["consumido_kg"] + grp_cat["descartado_kg"]).round(2)
    grp_cat["percentual_desperdicio"] = grp_cat.apply(
        lambda r: calcular_percentual(r["descartado_kg"], r["consumido_kg"]), axis=1
    )
    grp_cat["consumido_kg"] = grp_cat["consumido_kg"].round(2)
    grp_cat["descartado_kg"] = grp_cat["descartado_kg"].round(2)

    # Por período
    grp_per = df.groupby("periodo", as_index=False)[["consumido_kg", "descartado_kg"]].sum()
    grp_per["percentual_desperdicio"] = grp_per.apply(
        lambda r: calcular_percentual(r["descartado_kg"], r["consumido_kg"]), axis=1
    )
    grp_per["consumido_kg"] = grp_per["consumido_kg"].round(2)
    grp_per["descartado_kg"] = grp_per["descartado_kg"].round(2)
    ordem_periodos = {p: i for i, p in enumerate(PERIODOS_LISTA)}
    grp_per["ordem"] = grp_per["periodo"].map(lambda p: ordem_periodos.get(p, 99))
    grp_per = grp_per.sort_values("ordem").drop(columns=["ordem"])

    return {
        "por_alimento": grp_alimento.to_dict(orient="records"),
        "por_categoria": grp_cat.to_dict(orient="records"),
        "por_periodo": grp_per.to_dict(orient="records"),
    }


def calcular_tendencia_desperdicio(por_periodo: list[dict[str, Any]]) -> dict[str, Any]:
    if len(por_periodo) < 2:
        return {"status": "Estável (simulado)", "variacao_pp": 0.0}

    primeiro = por_periodo[0]["percentual_desperdicio"]
    ultimo = por_periodo[-1]["percentual_desperdicio"]
    variacao = round(ultimo - primeiro, 1)

    if variacao >= 2.0:
        status = f"Em alta (+{variacao:.1f} p.p.)"
    elif variacao <= -2.0:
        status = f"Em queda ({variacao:.1f} p.p.)"
    else:
        status = f"Estável ({variacao:+.1f} p.p.)"

    return {"status": status, "variacao_pp": variacao}


def calcular_indicadores_satisfacao(
    avaliacoes: list[dict[str, Any]],
    registros: list[dict[str, Any]],
) -> dict[str, Any]:
    if not avaliacoes:
        return {
            "total_avaliacoes": 0,
            "media_geral": 0.0,
            "percentual_positivas": 0.0,
            "media_por_disponibilidade": [],
            "relacao_operacional": "Sem avaliações registradas ainda.",
        }

    df_av = pd.DataFrame(avaliacoes)
    media_geral = round(float(df_av["nota"].mean()), 2)
    positivas = round(float((df_av["nota"] >= 4).mean() * 100), 1)

    grp_disp = (
        df_av.groupby("disponibilidade_percebida", as_index=False)
        .agg(media_nota=("nota", "mean"), quantidade=("nota", "count"))
    )
    grp_disp["media_nota"] = grp_disp["media_nota"].round(2)

    media_alta = grp_disp.loc[
        grp_disp["disponibilidade_percebida"] == "Alta (reposição constante)", "media_nota"
    ]
    media_baixa = grp_disp.loc[
        grp_disp["disponibilidade_percebida"] == "Baixa (faltou no buffet)", "media_nota"
    ]

    if not media_alta.empty and not media_baixa.empty:
        diff = round(float(media_alta.iloc[0] - media_baixa.iloc[0]), 2)
        relacao = (
            f"Avaliações com alta disponibilidade atingem média {media_alta.iloc[0]:.1f}/5, "
            f"enquanto relatos de falta no buffet caem para {media_baixa.iloc[0]:.1f}/5 "
            f"(queda de {diff:.1f} pontos)."
        )
    else:
        relacao = (
            f"Satisfação média atual em {media_geral:.1f}/5 com {positivas:.0f}% de avaliações positivas "
            "baseadas em registros anônimos simulados/manuais."
        )

    if registros:
        df_reg = pd.DataFrame(registros)
        per_reg = df_reg.groupby("periodo", as_index=False)[["consumido_kg", "descartado_kg"]].sum()
        per_reg["pct_desp"] = per_reg.apply(
            lambda r: calcular_percentual(r["descartado_kg"], r["consumido_kg"]), axis=1
        )
        per_av = df_av.groupby("periodo", as_index=False)["nota"].mean().rename(columns={"nota": "nota_media"})
        cruz = pd.merge(per_reg, per_av, on="periodo", how="inner")
        if not cruz.empty:
            pior = cruz.sort_values(by=["pct_desp", "nota_media"], ascending=[False, True]).iloc[0]
            relacao += (
                f" No período '{pior['periodo']}', o desperdício atingiu {pior['pct_desp']:.1f}% "
                f"com nota média {pior['nota_media']:.1f}/5."
            )

    return {
        "total_avaliacoes": int(len(avaliacoes)),
        "media_geral": media_geral,
        "percentual_positivas": positivas,
        "media_por_disponibilidade": grp_disp.to_dict(orient="records"),
        "relacao_operacional": relacao,
    }


def gerar_recomendacoes(
    dados_consumo: dict[str, Any],
    indicadores_sat: dict[str, Any],
    registros: list[dict[str, Any]],
) -> list[dict[str, str]]:
    recomendacoes: list[dict[str, str]] = []
    por_alimento = dados_consumo["por_alimento"]
    por_categoria = dados_consumo["por_categoria"]

    if por_alimento:
        maior_sobra = max(por_alimento, key=lambda x: x["percentual_desperdicio"])
        if maior_sobra["percentual_desperdicio"] >= 20.0:
            recomendacoes.append(
                {
                    "prioridade": "Alta",
                    "foco": f"Redução de sobras — {maior_sobra['alimento']}",
                    "diagnostico": (
                        f"Índice de desperdício de {maior_sobra['percentual_desperdicio']:.1f}% "
                        f"({maior_sobra['descartado_kg']:.1f} kg descartados), o maior retorno de pratos."
                    ),
                    "acao": (
                        "Reduzir o lote preparado por fornada, usar pegadores menores no buffet e revisar "
                        "temperatura/textura de exposição para evitar rejeição após servido."
                    ),
                }
            )

        maior_kg = max(por_alimento, key=lambda x: x["descartado_kg"])
        if maior_kg["alimento"] != maior_sobra["alimento"] and maior_kg["descartado_kg"] >= 3.0:
            recomendacoes.append(
                {
                    "prioridade": "Média",
                    "foco": f"Volume de descarte — {maior_kg['alimento']}",
                    "diagnostico": (
                        f"Maior volume total descartado ({maior_kg['descartado_kg']:.1f} kg; "
                        f"{maior_kg['percentual_desperdicio']:.1f}% de desperdício)."
                    ),
                    "acao": (
                        "Reavaliar tamanho das cubas e orientar reposição fracionada na última hora de cada turno."
                    ),
                }
            )

        mais_consumido = max(por_alimento, key=lambda x: x["consumido_kg"])
        teve_falta = any(
            r["alimento"] == mais_consumido["alimento"]
            and r.get("disponibilidade") == "Baixa (faltou no buffet)"
            for r in registros
        )
        if teve_falta:
            recomendacoes.append(
                {
                    "prioridade": "Alta",
                    "foco": f"Reposição prioritária — {mais_consumido['alimento']}",
                    "diagnostico": (
                        f"Item mais consumido ({mais_consumido['consumido_kg']:.1f} kg) com apenas "
                        f"{mais_consumido['percentual_desperdicio']:.1f}% de desperdício, mas com registro de falta no buffet."
                    ),
                    "acao": (
                        "Antecipar o disparo da grelha nos horários de pico para manter disponibilidade alta "
                        "e proteger a nota de satisfação dos clientes."
                    ),
                }
            )
        else:
            recomendacoes.append(
                {
                    "prioridade": "Baixa",
                    "foco": f"Demanda líder — {mais_consumido['alimento']}",
                    "diagnostico": (
                        f"Maior saída do salão ({mais_consumido['consumido_kg']:.1f} kg consumidos) "
                        f"com desperdício controlado ({mais_consumido['percentual_desperdicio']:.1f}%)."
                    ),
                    "acao": "Manter cadência atual de reposição e priorizar insumos deste item no planejamento diário.",
                }
            )

    if por_categoria:
        cat_critica = max(por_categoria, key=lambda x: x["percentual_desperdicio"])
        if cat_critica["percentual_desperdicio"] >= 22.0:
            recomendacoes.append(
                {
                    "prioridade": "Média",
                    "foco": f"Revisão de categoria — {cat_critica['categoria']}",
                    "diagnostico": (
                        f"Categoria com maior taxa média de desperdício ({cat_critica['percentual_desperdicio']:.1f}%)."
                    ),
                    "acao": (
                        "Reduzir variedade simultânea nessa categoria fora do horário de pico e monitorar "
                        "aceitação dos pratos com maior retorno."
                    ),
                }
            )

    if indicadores_sat["total_avaliacoes"] > 0 and indicadores_sat["media_geral"] < 4.0:
        recomendacoes.append(
            {
                "prioridade": "Alta",
                "foco": "Experiência do Cliente",
                "diagnostico": (
                    f"Satisfação média em {indicadores_sat['media_geral']:.1f}/5, abaixo da meta operacional (4,0/5)."
                ),
                "acao": (
                    "Cruzar horários de menor nota com temperatura dos acompanhamentos e velocidade de reposição das carnes."
                ),
            }
        )

    return recomendacoes


def recalcular_modulo(dados: dict[str, Any]) -> None:
    registros = dados["registros_desperdicio"]
    avaliacoes = dados["avaliacoes_satisfacao"]

    dados_consumo = consolidar_dados_consumo(registros)
    tendencia = calcular_tendencia_desperdicio(dados_consumo["por_periodo"])
    ind_sat = calcular_indicadores_satisfacao(avaliacoes, registros)

    total_consumido = round(sum(r["consumido_kg"] for r in registros), 2)
    total_descartado = round(sum(r["descartado_kg"] for r in registros), 2)
    pct_geral = calcular_percentual(total_descartado, total_consumido)

    if dados_consumo["por_alimento"]:
        maior_sobra = max(dados_consumo["por_alimento"], key=lambda x: x["percentual_desperdicio"])
        mais_consumido = max(dados_consumo["por_alimento"], key=lambda x: x["consumido_kg"])
        alimento_maior_sobra = maior_sobra["alimento"]
        pct_maior_sobra = maior_sobra["percentual_desperdicio"]
        alimento_mais_consumido = mais_consumido["alimento"]
        kg_mais_consumido = mais_consumido["consumido_kg"]
    else:
        alimento_maior_sobra = "Sem registros"
        pct_maior_sobra = 0.0
        alimento_mais_consumido = "Sem registros"
        kg_mais_consumido = 0.0

    recomendacoes = gerar_recomendacoes(dados_consumo, ind_sat, registros)

    dados["data_hora_atualizacao"] = agora_iso()
    dados["indicadores"] = {
        "total_consumido_kg": total_consumido,
        "total_descartado_kg": total_descartado,
        "percentual_desperdicio_geral": pct_geral,
        "alimento_maior_sobra": alimento_maior_sobra,
        "percentual_maior_sobra": pct_maior_sobra,
        "alimento_mais_consumido": alimento_mais_consumido,
        "consumo_alimento_lider_kg": kg_mais_consumido,
        "indice_medio_satisfacao": ind_sat["media_geral"],
        "tendencia_desperdicio": tendencia["status"],
        "variacao_tendencia_pp": tendencia["variacao_pp"],
        "dados_simulados": True,
    }
    dados["dados_consumo"] = dados_consumo
    dados["indicadores_satisfacao"] = ind_sat
    dados["recomendacoes_geradas"] = recomendacoes


# ==============================================================================
# PERSISTÊNCIA E CONTRATO JSON
# ==============================================================================
def salvar_dados(dados: dict[str, Any]) -> None:
    recalcular_modulo(dados)
    ARQUIVO_JSON.parent.mkdir(parents=True, exist_ok=True)
    with ARQUIVO_JSON.open("w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def criar_estrutura_inicial() -> dict[str, Any]:
    timestamp = agora_iso()
    registros = []
    for idx, item in enumerate(REGISTROS_INICIAIS_SIMULADOS, start=1):
        registros.append(
            {
                "registro_id": f"DSP-{idx:04d}",
                "alimento": item["alimento"],
                "categoria": item["categoria"],
                "periodo": item["periodo"],
                "consumido_kg": float(item["consumido_kg"]),
                "descartado_kg": float(item["descartado_kg"]),
                "percentual_desperdicio": calcular_percentual(
                    item["descartado_kg"], item["consumido_kg"]
                ),
                "disponibilidade": item["disponibilidade"],
                "origem_dado": "simulacao_demo",
                "data_hora": timestamp,
            }
        )

    avaliacoes = []
    for idx, av in enumerate(AVALIACOES_INICIAIS_SIMULADAS, start=1):
        avaliacoes.append(
            {
                "avaliacao_id": f"SAT-{idx:04d}",
                "nota": int(av["nota"]),
                "periodo": av["periodo"],
                "disponibilidade_percebida": av["disponibilidade_percebida"],
                "categoria_destaque": av["categoria_destaque"],
                "observacao_anonima": av["observacao"],
                "origem_dado": "simulacao_demo",
                "data_hora": timestamp,
            }
        )

    dados = {
        "projeto": PROJETO_NOME,
        "unidade": UNIDADE_RESTAURANTE,
        "modulo": MODULO_NOME,
        "modo_funcionamento": MODO_FUNCIONAMENTO,
        "data_hora_atualizacao": timestamp,
        "aviso_demonstracao": {
            "dados_simulados_ou_manuais": True,
            "pesagem_automatica_ativa": False,
            "reconhecimento_visual_ativo": False,
            "pesquisa_real_integrada": False,
            "dados_pessoais_coletados": False,
        },
        "indicadores": {},
        "registros_desperdicio": registros,
        "dados_consumo": {},
        "avaliacoes_satisfacao": avaliacoes,
        "indicadores_satisfacao": {},
        "recomendacoes_geradas": [],
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
                and isinstance(dados.get("registros_desperdicio"), list)
                and isinstance(dados.get("avaliacoes_satisfacao"), list)
            ):
                recalcular_modulo(dados)
                return dados
        except (json.JSONDecodeError, OSError):
            pass
    return criar_estrutura_inicial()


def adicionar_registro_desperdicio(
    dados: dict[str, Any],
    alimento: str,
    categoria: str,
    periodo: str,
    consumido_kg: float,
    descartado_kg: float,
    disponibilidade: str,
    origem_dado: str,
) -> None:
    novo = {
        "registro_id": f"DSP-{len(dados['registros_desperdicio']) + 1:04d}",
        "alimento": alimento,
        "categoria": categoria,
        "periodo": periodo,
        "consumido_kg": round(float(consumido_kg), 2),
        "descartado_kg": round(float(descartado_kg), 2),
        "percentual_desperdicio": calcular_percentual(descartado_kg, consumido_kg),
        "disponibilidade": disponibilidade,
        "origem_dado": origem_dado,
        "data_hora": agora_iso(),
    }
    dados["registros_desperdicio"].insert(0, novo)
    salvar_dados(dados)


def adicionar_avaliacao_anonima(
    dados: dict[str, Any],
    nota: int,
    periodo: str,
    disponibilidade_percebida: str,
    categoria_destaque: str,
    observacao: str,
    origem_dado: str,
) -> None:
    nova = {
        "avaliacao_id": f"SAT-{len(dados['avaliacoes_satisfacao']) + 1:04d}",
        "nota": int(nota),
        "periodo": periodo,
        "disponibilidade_percebida": disponibilidade_percebida,
        "categoria_destaque": categoria_destaque,
        "observacao_anonima": observacao.strip() or "Sem observação adicional.",
        "origem_dado": origem_dado,
        "data_hora": agora_iso(),
    }
    dados["avaliacoes_satisfacao"].insert(0, nova)
    salvar_dados(dados)


# ==============================================================================
# ESTILIZAÇÃO CLEAN E VISUALIZAÇÃO OPERACIONAL
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
            padding: 12px 13px;
            color: #f8fafc;
            margin-bottom: 10px;
            min-height: 118px;
        }
        .kpi-label {
            font-size: 0.67rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            line-height: 1.3;
            margin-bottom: 5px;
            word-break: normal;
            overflow-wrap: normal;
        }
        .kpi-value {
            font-size: 1.55rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.15;
        }
        .kpi-value-sm {
            font-size: 1.05rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.25;
            margin-top: 3px;
        }
        .kpi-sub {
            font-size: 0.75rem;
            color: #cbd5e1;
            margin-top: 5px;
        }
        .rec-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-left: 5px solid var(--rec-color);
            border-radius: 10px;
            padding: 12px 15px;
            margin-bottom: 10px;
            color: #f8fafc;
        }
        .rec-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.92rem;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .rec-body {
            font-size: 0.85rem;
            color: #e2e8f0;
            margin-bottom: 4px;
        }
        .rec-action {
            font-size: 0.85rem;
            color: #93c5fd;
        }
        .sat-box {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 16px;
            color: #f8fafc;
            margin-bottom: 12px;
        }
        .sat-score {
            font-size: 2.2rem;
            font-weight: 800;
            color: #facc15;
            line-height: 1.1;
        }
        .sat-note {
            font-size: 0.86rem;
            color: #cbd5e1;
            margin-top: 8px;
            line-height: 1.45;
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
    compacto: bool = False,
) -> None:
    classe = "kpi-value-sm" if compacto else "kpi-value"
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent: {cor};">
            <div class="kpi-label">{titulo}</div>
            <div class="{classe}">{valor}</div>
            <div class="kpi-sub">{subtitulo}</div>
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
        page_icon="🥗",
        layout="wide",
    )
    aplicar_estilos()

    if "dados_desperdicio" not in st.session_state:
        st.session_state.dados_desperdicio = carregar_dados()

    if "aviso_desperdicio" not in st.session_state:
        st.session_state.aviso_desperdicio = ""

    dados = st.session_state.dados_desperdicio

    # --------------------------------------------------------------------------
    # SIDEBAR — SIMULAÇÃO RÁPIDA E FILTRO DE PERÍODO
    # --------------------------------------------------------------------------
    with st.sidebar:
        st.title("🥩 Até a Primeira Garfada")
        st.caption(f"**Unidade:** {UNIDADE_RESTAURANTE}")
        st.caption(f"**Módulo:** {MODULO_TITULO}")
        st.divider()

        st.subheader("Simulação Rápida (Demo)")
        st.info(
            "Os dados abaixo são **simulados ou inseridos manualmente**. "
            "Não há balança automática, visão computacional ou coleta de dados pessoais."
        )

        if st.button("🍽️ Simular Registro de Sobra", use_container_width=True):
            alimento = random.choice(list(CATALOGO_ALIMENTOS.keys()))
            categoria = CATALOGO_ALIMENTOS[alimento]
            periodo = random.choice(PERIODOS_LISTA)
            consumido = round(random.uniform(4.5, 16.0), 1)
            descartado = round(random.uniform(0.8, 4.5), 1)
            disp = random.choice(DISPONIBILIDADE_OPCOES)
            adicionar_registro_desperdicio(
                dados,
                alimento=alimento,
                categoria=categoria,
                periodo=periodo,
                consumido_kg=consumido,
                descartado_kg=descartado,
                disponibilidade=disp,
                origem_dado="simulacao_demo",
            )
            st.session_state.aviso_desperdicio = (
                f"Sobra simulada: {alimento} ({descartado:.1f} kg descartados em {periodo})."
            )
            st.rerun()

        if st.button("⭐ Simular Avaliação Anônima", use_container_width=True):
            disp = random.choice(DISPONIBILIDADE_OPCOES)
            if disp.startswith("Alta"):
                nota = random.choice([4, 5, 5])
                obs = "Reposição ágil e pratos na temperatura ideal."
            elif disp.startswith("Média"):
                nota = random.choice([3, 4])
                obs = "Boa comida, pequena espera na reposição de acompanhamentos."
            else:
                nota = random.choice([2, 3])
                obs = "Alguns itens populares faltaram temporariamente no buffet."

            adicionar_avaliacao_anonima(
                dados,
                nota=nota,
                periodo=random.choice(PERIODOS_LISTA),
                disponibilidade_percebida=disp,
                categoria_destaque=random.choice(CATEGORIAS_LISTA),
                observacao=obs,
                origem_dado="simulacao_demo",
            )
            st.session_state.aviso_desperdicio = f"Avaliação anônima simulada registrada (nota {nota}/5)."
            st.rerun()

        if st.button("🔄 Reiniciar Dados de Demo", use_container_width=True):
            st.session_state.dados_desperdicio = criar_estrutura_inicial()
            st.session_state.aviso_desperdicio = "Cenário demonstrativo reiniciado."
            st.rerun()

        st.divider()
        st.subheader("Filtro de Visualização")
        filtro_periodo = st.selectbox("Período operacional", ["Todos os períodos"] + PERIODOS_LISTA)

        st.divider()
        st.caption(f"📄 JSON ativo: `{ARQUIVO_JSON.name}`")
        st.caption(f"🕒 Atualizado: `{formatar_hora(dados['data_hora_atualizacao'])}`")

    # --------------------------------------------------------------------------
    # CABEÇALHO E AVISO DE DEMONSTRAÇÃO
    # --------------------------------------------------------------------------
    st.title("🥗 Desperdício e Experiência do Cliente")
    st.caption(f"Projeto **{PROJETO_NOME}** • {UNIDADE_RESTAURANTE} • Hackathon FMU 2026.2")

    st.markdown(
        """
        <div class="demo-banner">
            ⚠️ <strong>MODO DEMONSTRAÇÃO (DADOS SIMULADOS / MANUAIS):</strong>
            Os volumes de consumo, sobras de pratos e avaliações de satisfação são simulados ou registrados
            manualmente para validação do MVP. Não há pesagem automática, reconhecimento visual real de alimentos
            nem identificação pessoal de clientes.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.aviso_desperdicio:
        st.toast(st.session_state.aviso_desperdicio, icon="✅")
        st.session_state.aviso_desperdicio = ""

    # Aplica filtro de período apenas para visualização na tela (JSON sempre mantém consolidado total)
    if filtro_periodo == "Todos os períodos":
        registros_vis = dados["registros_desperdicio"]
        avaliacoes_vis = dados["avaliacoes_satisfacao"]
        consumo_vis = dados["dados_consumo"]
        ind_sat_vis = dados["indicadores_satisfacao"]
        recs_vis = dados["recomendacoes_geradas"]
        ind_vis = dados["indicadores"]
    else:
        registros_vis = [r for r in dados["registros_desperdicio"] if r["periodo"] == filtro_periodo]
        avaliacoes_vis = [a for a in dados["avaliacoes_satisfacao"] if a["periodo"] == filtro_periodo]
        consumo_vis = consolidar_dados_consumo(registros_vis)
        ind_sat_vis = calcular_indicadores_satisfacao(avaliacoes_vis, registros_vis)
        recs_vis = gerar_recomendacoes(consumo_vis, ind_sat_vis, registros_vis)
        tot_cons = round(sum(r["consumido_kg"] for r in registros_vis), 2)
        tot_desc = round(sum(r["descartado_kg"] for r in registros_vis), 2)
        pct_vis = calcular_percentual(tot_desc, tot_cons)
        maior_s = max(consumo_vis["por_alimento"], key=lambda x: x["percentual_desperdicio"]) if consumo_vis["por_alimento"] else None
        mais_c = max(consumo_vis["por_alimento"], key=lambda x: x["consumido_kg"]) if consumo_vis["por_alimento"] else None
        ind_vis = {
            "total_descartado_kg": tot_desc,
            "percentual_desperdicio_geral": pct_vis,
            "alimento_maior_sobra": maior_s["alimento"] if maior_s else "Sem dados",
            "percentual_maior_sobra": maior_s["percentual_desperdicio"] if maior_s else 0.0,
            "alimento_mais_consumido": mais_c["alimento"] if mais_c else "Sem dados",
            "consumo_alimento_lider_kg": mais_c["consumido_kg"] if mais_c else 0.0,
            "indice_medio_satisfacao": ind_sat_vis["media_geral"],
            "tendencia_desperdicio": dados["indicadores"]["tendencia_desperdicio"],
        }

    # --------------------------------------------------------------------------
    # INDICADORES PRINCIPAIS NO TOPO
    # --------------------------------------------------------------------------
    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:
        renderizar_kpi(
            "Desperdício Total (Simulado)",
            f"{ind_vis['total_descartado_kg']:.1f} kg",
            f"Índice geral: {ind_vis['percentual_desperdicio_geral']:.1f}% do servido",
            "#ef4444",
        )
    with k2:
        renderizar_kpi(
            "Maior Índice de Sobra",
            ind_vis["alimento_maior_sobra"],
            f"{ind_vis['percentual_maior_sobra']:.1f}% de retorno no prato",
            "#f97316",
            compacto=True,
        )
    with k3:
        renderizar_kpi(
            "Alimento Mais Consumido",
            ind_vis["alimento_mais_consumido"],
            f"{ind_vis['consumo_alimento_lider_kg']:.1f} kg consumidos",
            "#22c55e",
            compacto=True,
        )
    with k4:
        renderizar_kpi(
            "Satisfação Média (Anônima)",
            f"{ind_vis['indice_medio_satisfacao']:.1f} / 5.0",
            f"{ind_sat_vis['percentual_positivas']:.0f}% positivas ({ind_sat_vis['total_avaliacoes']} aval.)",
            "#eab308",
        )
    with k5:
        cor_tend = "#ef4444" if "alta" in ind_vis["tendencia_desperdicio"].lower() else "#38bdf8"
        renderizar_kpi(
            "Tendência de Desperdício",
            ind_vis["tendencia_desperdicio"],
            "Comparativo entre períodos",
            cor_tend,
            compacto=True,
        )

    # --------------------------------------------------------------------------
    # ABAS OPERACIONAIS
    # --------------------------------------------------------------------------
    aba_painel, aba_registrar, aba_historico = st.tabs(
        [
            "📊 Painel Operacional",
            "➕ Registrar Desperdício / Avaliação",
            "📋 Histórico e Integração JSON",
        ]
    )

    # ABA 1: PAINEL PRINCIPAL (GRÁFICOS, SATISFAÇÃO E RECOMENDAÇÕES)
    with aba_painel:
        col_esq, col_dir = st.columns(2)

        with col_esq:
            st.subheader("🗑️ Desperdício por Alimento (%)")
            if consumo_vis["por_alimento"]:
                df_al = pd.DataFrame(consumo_vis["por_alimento"]).sort_values(
                    "percentual_desperdicio", ascending=False
                )
                df_al["nivel_alerta"] = df_al["percentual_desperdicio"].apply(
                    lambda p: "Alto (≥25%)"
                    if p >= 25
                    else ("Atenção (18–24%)" if p >= 18 else "Controlado (<18%)")
                )
                chart_desp = (
                    alt.Chart(df_al)
                    .mark_bar(cornerRadiusEnd=6)
                    .encode(
                        x=alt.X("percentual_desperdicio:Q", title="Desperdício (%)"),
                        y=alt.Y("alimento:N", sort="-x", title=None),
                        color=alt.Color(
                            "nivel_alerta:N",
                            scale=alt.Scale(
                                domain=["Alto (≥25%)", "Atenção (18–24%)", "Controlado (<18%)"],
                                range=["#ef4444", "#f59e0b", "#38bdf8"],
                            ),
                            legend=alt.Legend(title=None, orient="top"),
                        ),
                        tooltip=[
                            alt.Tooltip("alimento:N", title="Alimento"),
                            alt.Tooltip("categoria:N", title="Categoria"),
                            alt.Tooltip("descartado_kg:Q", title="Descartado (kg)", format=".1f"),
                            alt.Tooltip("consumido_kg:Q", title="Consumido (kg)", format=".1f"),
                            alt.Tooltip("percentual_desperdicio:Q", title="Desperdício (%)", format=".1f"),
                        ],
                    )
                    .properties(height=320)
                )
                st.altair_chart(chart_desp, use_container_width=True)
            else:
                st.info("Sem registros para o período selecionado.")

        with col_dir:
            st.subheader("📈 Consumo vs. Descarte por Alimento (kg)")
            if consumo_vis["por_alimento"]:
                df_comp = (
                    pd.DataFrame(consumo_vis["por_alimento"])
                    .sort_values("consumido_kg", ascending=False)
                    .melt(
                        id_vars=["alimento"],
                        value_vars=["consumido_kg", "descartado_kg"],
                        var_name="tipo",
                        value_name="kg",
                    )
                )
                df_comp["tipo"] = df_comp["tipo"].replace(
                    {"consumido_kg": "Consumido (kg)", "descartado_kg": "Descartado (kg)"}
                )
                chart_comp = (
                    alt.Chart(df_comp)
                    .mark_bar(cornerRadiusEnd=4)
                    .encode(
                        x=alt.X("kg:Q", title="Quantidade Estimada (kg)"),
                        y=alt.Y("alimento:N", sort="-x", title=None),
                        color=alt.Color(
                            "tipo:N",
                            scale=alt.Scale(
                                domain=["Consumido (kg)", "Descartado (kg)"],
                                range=["#22c55e", "#ef4444"],
                            ),
                            legend=alt.Legend(title=None, orient="top"),
                        ),
                        tooltip=[
                            alt.Tooltip("alimento:N", title="Alimento"),
                            alt.Tooltip("tipo:N", title="Métrica"),
                            alt.Tooltip("kg:Q", title="Volume (kg)", format=".1f"),
                        ],
                    )
                    .properties(height=320)
                )
                st.altair_chart(chart_comp, use_container_width=True)
            else:
                st.info("Sem registros para o período selecionado.")

        st.divider()

        col_cat, col_sat = st.columns([1.15, 1])

        with col_cat:
            st.subheader("🍽️ Tendência por Categoria e Período")
            sub_cat, sub_per = st.tabs(["Por Categoria", "Por Período"])

            with sub_cat:
                if consumo_vis["por_categoria"]:
                    df_cat = pd.DataFrame(consumo_vis["por_categoria"]).sort_values(
                        "consumido_kg", ascending=False
                    )
                    st.dataframe(
                        df_cat.rename(
                            columns={
                                "categoria": "Categoria",
                                "consumido_kg": "Consumido (kg)",
                                "descartado_kg": "Descartado (kg)",
                                "percentual_desperdicio": "Desperdício (%)",
                            }
                        )[["Categoria", "Consumido (kg)", "Descartado (kg)", "Desperdício (%)"]],
                        use_container_width=True,
                        hide_index=True,
                    )

            with sub_per:
                if dados["dados_consumo"]["por_periodo"]:
                    df_per = pd.DataFrame(dados["dados_consumo"]["por_periodo"])
                    st.dataframe(
                        df_per.rename(
                            columns={
                                "periodo": "Período",
                                "consumido_kg": "Consumido (kg)",
                                "descartado_kg": "Descartado (kg)",
                                "percentual_desperdicio": "Desperdício (%)",
                            }
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

        with col_sat:
            st.subheader("⭐ Experiência do Cliente")
            estrelas = "★" * int(round(ind_sat_vis["media_geral"])) + "☆" * (
                5 - int(round(ind_sat_vis["media_geral"]))
            )
            st.markdown(
                f"""
                <div class="sat-box">
                    <div class="sat-score">{ind_sat_vis['media_geral']:.1f} / 5.0 &nbsp; {estrelas}</div>
                    <div class="sat-note">
                        <strong>Relação identificada (simulada):</strong> {ind_sat_vis['relacao_operacional']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if ind_sat_vis["media_por_disponibilidade"]:
                df_disp = pd.DataFrame(ind_sat_vis["media_por_disponibilidade"]).rename(
                    columns={
                        "disponibilidade_percebida": "Disponibilidade no Buffet",
                        "media_nota": "Nota Média",
                        "quantidade": "Avaliações",
                    }
                )
                st.dataframe(df_disp, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("💡 Recomendações Operacionais")
        if not recs_vis:
            st.info("Nenhuma recomendação crítica gerada para os filtros atuais.")
        else:
            cores_prio = {"Alta": "#ef4444", "Média": "#eab308", "Baixa": "#22c55e"}
            for rec in recs_vis:
                cor_rec = cores_prio.get(rec["prioridade"], "#38bdf8")
                st.markdown(
                    f"""
                    <div class="rec-card" style="--rec-color: {cor_rec};">
                        <div class="rec-head">
                            <span>{rec['foco']}</span>
                            <span>Prioridade: {rec['prioridade']}</span>
                        </div>
                        <div class="rec-body"><strong>Padrão observado:</strong> {rec['diagnostico']}</div>
                        <div class="rec-action"><strong>Ação recomendada:</strong> {rec['acao']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ABA 2: ENTRADA MANUAL DE DESPERDÍCIO E SATISFAÇÃO ANÔNIMA
    with aba_registrar:
        col_form1, col_form2 = st.columns(2)

        with col_form1:
            st.subheader("📝 Registrar Consumo e Descarte (Manual)")
            with st.form("form_desperdicio", clear_on_submit=True):
                alimento_sel = st.selectbox("Alimento", list(CATALOGO_ALIMENTOS.keys()))
                periodo_sel = st.selectbox("Período", PERIODOS_LISTA)
                c_in1, c_in2 = st.columns(2)
                with c_in1:
                    consumido_in = st.number_input("Consumido estimado (kg)", min_value=0.0, max_value=100.0, value=8.0, step=0.5)
                with c_in2:
                    descartado_in = st.number_input("Descartado / Sobra (kg)", min_value=0.0, max_value=50.0, value=2.0, step=0.2)
                disp_in = st.selectbox("Disponibilidade observada no buffet", DISPONIBILIDADE_OPCOES)

                enviado_desp = st.form_submit_button("Salvar Registro de Desperdício", use_container_width=True)
                if enviado_desp:
                    if consumido_in == 0 and descartado_in == 0:
                        st.error("Informe um valor maior que zero para consumo ou descarte.")
                    else:
                        adicionar_registro_desperdicio(
                            dados,
                            alimento=alimento_sel,
                            categoria=CATALOGO_ALIMENTOS[alimento_sel],
                            periodo=periodo_sel,
                            consumido_kg=consumido_in,
                            descartado_kg=descartado_in,
                            disponibilidade=disp_in,
                            origem_dado="registro_manual",
                        )
                        st.session_state.aviso_desperdicio = f"Registro manual salvo para {alimento_sel}."
                        st.rerun()

        with col_form2:
            st.subheader("⭐ Registrar Avaliação de Experiência (Anônima)")
            st.caption("Nenhum dado pessoal ou identificador individual do cliente é coletado.")
            with st.form("form_satisfacao", clear_on_submit=True):
                nota_in = st.slider("Nota geral da experiência", min_value=1, max_value=5, value=4)
                periodo_av = st.selectbox("Período da visita", PERIODOS_LISTA)
                disp_av = st.selectbox("Percepção de disponibilidade dos alimentos", DISPONIBILIDADE_OPCOES)
                cat_av = st.selectbox("Categoria que mais influenciou a nota", CATEGORIAS_LISTA)
                obs_av = st.text_input("Observação rápida (anônima e opcional)", placeholder="Ex.: Picanha excelente, mas batata estava fria.")

                enviado_av = st.form_submit_button("Salvar Avaliação Anônima", use_container_width=True)
                if enviado_av:
                    adicionar_avaliacao_anonima(
                        dados,
                        nota=nota_in,
                        periodo=periodo_av,
                        disponibilidade_percebida=disp_av,
                        categoria_destaque=cat_av,
                        observacao=obs_av,
                        origem_dado="registro_manual",
                    )
                    st.session_state.aviso_desperdicio = f"Avaliação anônima ({nota_in}/5) registrada."
                    st.rerun()

    # ABA 3: HISTÓRICO DE REGISTROS E INTEGRAÇÃO JSON
    with aba_historico:
        st.subheader("📋 Histórico de Registros de Desperdício e Consumo")
        df_reg_hist = pd.DataFrame(dados["registros_desperdicio"])[
            [
                "registro_id",
                "periodo",
                "alimento",
                "categoria",
                "consumido_kg",
                "descartado_kg",
                "percentual_desperdicio",
                "disponibilidade",
                "origem_dado",
            ]
        ].rename(
            columns={
                "registro_id": "ID",
                "periodo": "Período",
                "alimento": "Alimento",
                "categoria": "Categoria",
                "consumido_kg": "Consumido (kg)",
                "descartado_kg": "Descartado (kg)",
                "percentual_desperdicio": "Desperdício (%)",
                "disponibilidade": "Disponibilidade",
                "origem_dado": "Origem",
            }
        )
        st.dataframe(df_reg_hist, use_container_width=True, hide_index=True)

        st.subheader("💬 Histórico de Avaliações Anônimas")
        df_av_hist = pd.DataFrame(dados["avaliacoes_satisfacao"])[
            [
                "avaliacao_id",
                "periodo",
                "nota",
                "disponibilidade_percebida",
                "categoria_destaque",
                "observacao_anonima",
                "origem_dado",
            ]
        ].rename(
            columns={
                "avaliacao_id": "ID",
                "periodo": "Período",
                "nota": "Nota",
                "disponibilidade_percebida": "Disponibilidade",
                "categoria_destaque": "Categoria",
                "observacao_anonima": "Observação Anônima",
                "origem_dado": "Origem",
            }
        )
        st.dataframe(df_av_hist, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("🔗 Integração JSON (Inteligência Operacional Central)")
        json_str = json.dumps(dados, ensure_ascii=False, indent=2)
        c_p, c_b = st.columns([2, 1])
        with c_p:
            st.caption(f"Arquivo atualizado automaticamente em: `{ARQUIVO_JSON}`")
        with c_b:
            st.download_button(
                label="⬇️ Baixar dados_desperdicio.json",
                data=json_str.encode("utf-8"),
                file_name="dados_desperdicio.json",
                mime="application/json",
                use_container_width=True,
            )
        st.json(dados, expanded=False)


if __name__ == "__main__":
    main()
    