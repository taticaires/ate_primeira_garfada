import json
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Até a Primeira Garfada",
    page_icon="🍽️",
    layout="wide",
)

ARQUIVO_BUFFET = (
    Path(__file__).parent
    / "modulos"
    / "monitoramento_buffet"
    / "dados_buffet.json"
)


def carregar_dados_buffet():
    try:
        if not ARQUIVO_BUFFET.exists():
            return None
        with ARQUIVO_BUFFET.open("r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return None


st.markdown("""
<style>
:root {
    --page: #f5f6f3;
    --surface: #ffffff;
    --surface-soft: #eef2ed;
    --ink: #26332d;
    --muted: #738078;
    --line: #e1e7e1;
    --green: #2d6a4f;
    --green-soft: #e5f1e9;
    --amber: #a96d20;
    --amber-soft: #fff2dc;
    --red: #b64b4b;
    --red-soft: #fff0ee;
}
.stApp {
    background: var(--page);
    color: var(--ink);
}
[data-testid="stHeader"] {
    background: transparent;
}
.block-container {
    max-width: 1440px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}
section[data-testid="stSidebar"] {
    background: #edf1ec;
    border-right: 1px solid #dce4dc;
}
section[data-testid="stSidebar"] * {
    color: #34483c;
}
section[data-testid="stSidebar"] [aria-current="page"] {
    background: #dcebe0;
    border-radius: 9px;
}
.hero {
    background: linear-gradient(115deg, #244c3a 0%, #2f6b50 70%, #3b795d 100%);
    border-radius: 20px;
    padding: 27px 32px;
    margin: 0 0 22px 0;
    color: #ffffff;
    box-shadow: 0 8px 24px rgba(36, 76, 58, .12);
}
.hero .eyebrow {
    color: #d8e9dd;
    font-size: .75rem;
    letter-spacing: .12em;
    text-transform: uppercase;
    font-weight: 700;
    margin-bottom: 8px;
}
.hero h1 {
    color: #ffffff !important;
    font-size: 2rem !important;
    line-height: 1.2;
    margin: 0 0 9px 0;
}
.hero p {
    color: #e3eee6 !important;
    font-size: .98rem;
    margin: 0;
}
.location-line {
    color: #718078;
    font-size: .76rem;
    font-weight: 700;
    letter-spacing: .07em;
    margin: 0 0 8px 2px;
}
.section-heading {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 22px 0 4px 0;
}
.section-heading h2 {
    color: #26332d !important;
    font-size: 1.35rem !important;
    margin: 0 !important;
}
.section-subtitle {
    color: #7a877f;
    font-size: .88rem;
    margin: 4px 0 16px 0;
}
div[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 15px;
    padding: 17px 19px;
    box-shadow: 0 3px 12px rgba(34, 54, 42, .035);
    min-height: 118px;
}
div[data-testid="stMetricLabel"] {
    color: #738078 !important;
    font-size: .82rem !important;
}
div[data-testid="stMetricValue"] {
    color: #26332d !important;
    font-size: 2rem !important;
    font-weight: 700;
}
div[data-testid="stMetricDelta"] {
    font-size: .75rem !important;
}
div[data-testid="stAlert"] {
    border-radius: 12px;
}
.alert-card {
    background: var(--red-soft);
    border: 1px solid #f1d5d1;
    border-left: 4px solid var(--red);
    border-radius: 12px;
    padding: 13px 16px;
    margin: 8px 0;
}
.alert-card strong {
    color: #883b3b;
    display: block;
    font-size: .95rem;
    margin-bottom: 3px;
}
.alert-card span {
    color: #9c5550;
    font-size: .82rem;
}
.food-card {
    background: #ffffff;
    border: 1px solid var(--line);
    border-radius: 12px;
    padding: 13px 15px;
    margin-bottom: 10px;
}
.food-top {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
    margin-bottom: 9px;
}
.food-name {
    color: #34443a;
    font-weight: 650;
    font-size: .9rem;
}
.food-area {
    color: #87928b;
    font-size: .75rem;
    margin-top: 2px;
}
.pill {
    display: inline-block;
    white-space: nowrap;
    border-radius: 20px;
    padding: 4px 10px;
    font-size: .72rem;
    font-weight: 700;
}
.pill-ok { background: #e6f2e9; color: #2d6a4f; }
.pill-mid { background: #fff1d9; color: #9b671f; }
.pill-low { background: #fbe5e2; color: #a64040; }
.progress-track {
    background: #edf0ec;
    height: 7px;
    border-radius: 20px;
    overflow: hidden;
}
.progress-fill {
    height: 7px;
    border-radius: 20px;
}
.module-card {
    background: #ffffff;
    border: 1px solid #e1e7e1;
    border-radius: 15px;
    padding: 18px 19px;
    min-height: 120px;
    margin-bottom: 12px;
    transition: border-color .15s ease, transform .15s ease;
}
.module-card:hover {
    border-color: #b9d1c1;
    transform: translateY(-1px);
}
.module-card h3 {
    color: #2d4938 !important;
    font-size: 1rem !important;
    margin: 0 0 8px 0 !important;
}
.module-card p {
    color: #78847c !important;
    font-size: .83rem;
    line-height: 1.5;
    margin: 0;
}
.stButton > button {
    border-radius: 9px;
    border: 1px solid #cbd9ce;
    background: #ffffff;
    color: #2d6a4f;
    font-weight: 600;
}
.stButton > button:hover {
    border-color: #2d6a4f;
    color: #244c3a;
}
hr {
    border-color: #e1e7e1 !important;
}
footer {visibility: hidden;}

.kpi-card {
    background: #ffffff;
    border: 1px solid #d5dfd6;
    border-radius: 14px;
    padding: 16px 18px 14px;
    min-height: 108px;
    box-shadow: 0 2px 7px rgba(28, 45, 33, .035);
}
.kpi-label {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    opacity: 1 !important;
    font-size: .82rem;
    font-weight: 750;
    letter-spacing: .01em;
    margin-bottom: 11px;
}
.kpi-value {
    color: #111111 !important;
    -webkit-text-fill-color: #111111 !important;
    opacity: 1 !important;
    font-size: 2.15rem;
    line-height: 1;
    font-weight: 800;
}
.kpi-label * { color: #111111 !important; opacity: 1 !important; }
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* Dashboard de leitura rápida */
.stApp { background: #f3f5f1; }
section[data-testid="stSidebar"] { background: #e9eee8; }
.block-container { max-width: 1500px; padding-top: 1.25rem; }
.hero {
    background: linear-gradient(110deg, #244b38, #367454);
    border: 0; border-radius: 16px; padding: 23px 28px;
    margin-bottom: 15px; box-shadow: none;
}
.hero .eyebrow { font-size: .72rem; letter-spacing: .1em; opacity: .85; }
.hero h1 { font-size: 1.85rem !important; margin-bottom: 5px !important; }
.hero p { font-size: .92rem; }
.location-line { margin-bottom: 5px; }
.section-heading { margin-top: 15px; }
.section-heading h2 { font-size: 1.18rem !important; }
.section-subtitle { font-size: .85rem; margin-bottom: 12px; }

.status-strip {
    display:flex; align-items:center; justify-content:space-between;
    gap:18px; padding:16px 20px; background:#fff;
    border:1px solid #e0e7df; border-radius:14px; margin: 10px 0 17px;
}
.status-main { display:flex; align-items:center; gap:13px; }
.status-dot { width:15px; height:15px; border-radius:50%; background:#d59a32;
    box-shadow:0 0 0 5px #fff2d9; flex:0 0 auto; }
.status-title { color:#2b3d31; font-size:1.12rem; font-weight:750; line-height:1.2; }
.status-caption { color:#7a877d; font-size:.82rem; margin-top:4px; }
.status-tag { background:#fff1d8; color:#98651e; border-radius:7px;
    padding:7px 11px; font-size:.78rem; font-weight:750; white-space:nowrap; }

div[data-testid="stMetric"] {
    background:#fff; border:1px solid #e1e7df; border-radius:13px;
    padding:15px 17px; min-height:105px; box-shadow:none;
}
div[data-testid="stMetricLabel"] { font-size:.78rem !important; color:#7a877e !important; }
div[data-testid="stMetricValue"] { font-size:2.15rem !important; font-weight:750; color:#26372d !important; }
div[data-testid="stMetricDelta"] { font-size:.72rem !important; }
.priority-panel {
    background:#fff; border:1px solid #e1e7df; border-radius:15px;
    padding:17px 18px; min-height:100%;
}
.priority-kicker { color:#9c6a24; text-transform:uppercase; letter-spacing:.08em;
    font-size:.7rem; font-weight:800; margin-bottom:8px; }
.priority-name { font-size:1.28rem; font-weight:750; color:#344238; line-height:1.25; }
.priority-location { font-size:.88rem; color:#7d8980; margin-top:5px; }
.priority-action { display:inline-block; margin-top:13px; padding:7px 10px;
    background:#fff0ed; color:#a3423e; border-radius:7px; font-size:.8rem; font-weight:750; }
.no-alert {
    background:#e7f2e9; border:1px solid #d2e5d7; border-radius:15px;
    padding:22px; color:#2c6a49; font-weight:700; font-size:1.05rem;
}
.food-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:9px; }
.food-tile { background:#fff; border:1px solid #e1e7df; border-radius:11px;
    padding:12px 13px; min-width:0; }
.food-tile-head { display:flex; justify-content:space-between; align-items:center; gap:8px; }
.food-title { font-size:.84rem; font-weight:700; color:#344238; line-height:1.25; }
.food-sub { color:#879188; font-size:.72rem; margin-top:4px; }
.food-badge { font-size:.68rem; font-weight:800; border-radius:6px;
    padding:4px 7px; white-space:nowrap; }
.badge-full { background:#e5f2e8; color:#34714c; }
.badge-mid { background:#fff1d8; color:#98651e; }
.badge-low { background:#fbe7e4; color:#a3423e; }
.level-track { height:5px; background:#edf0eb; border-radius:9px; overflow:hidden; margin-top:10px; }
.level-fill { height:5px; border-radius:9px; }
.activity-summary { display:flex; flex-wrap:wrap; gap:8px; margin-top:13px; }
.activity-chip { border:1px solid #e2e8e0; background:#f8faf7; color:#657268;
    padding:7px 10px; border-radius:8px; font-size:.76rem; }
div[data-testid="stAlert"] { border-radius:10px; }
.stButton > button { border-radius:9px; font-weight:650; }
hr { border-color:#e1e7df !important; }
@media (max-width: 900px) {
    .food-grid { grid-template-columns:1fr; }
    .status-strip { align-items:flex-start; flex-direction:column; }
}
</style>
""", unsafe_allow_html=True)


def nivel_visual(nivel):
    mapa = {
        "Cheio": (90, "pill-ok", "#4b9870"),
        "Médio": (55, "pill-mid", "#d6a044"),
        "Baixo": (25, "pill-low", "#d16a5f"),
        "Vazio": (5, "pill-low", "#b64b4b"),
    }
    return mapa.get(nivel, (0, "pill-mid", "#aab4ac"))


def visao_geral():
    import html

    dados = carregar_dados_buffet()
    alimentos = dados.get("alimentos", []) if dados else []
    criticos = [x for x in alimentos if x.get("nivel") in ("Baixo", "Vazio")]
    atencao = [x for x in alimentos if x.get("nivel") == "Médio"]
    historico = dados.get("historico", []) if dados else []

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">Painel de operação · demonstração</div>
        <h1>🍽️ Até a Primeira Garfada</h1>
        <p>Inteligência operacional para transformar a experiência do restaurante.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="location-line">BOVINU’S GRILL & BEER  ·  AUGUSTA</div>', unsafe_allow_html=True)

    # Um status de leitura imediata: primeiro a situação, depois os números.
    if criticos:
        dot = "#c4544c"
        status = "Ação necessária"
        resumo = f"{len(criticos)} item(ns) precisam de reposição."
        tag = "ATENÇÃO"
        tag_style = "background:#fbe7e4;color:#a3423e;"
    elif atencao:
        dot = "#d59a32"
        status = "Operação em atenção"
        resumo = f"{len(atencao)} item(ns) estão em nível médio."
        tag = "ACOMPANHAR"
        tag_style = "background:#fff1d8;color:#98651e;"
    else:
        dot = "#4b9870"
        status = "Tudo em ordem"
        resumo = "Nenhum item crítico identificado no registro atual."
        tag = "NORMAL"
        tag_style = "background:#e5f2e8;color:#34714c;"

    st.markdown(
        f'<div class="status-strip"><div class="status-main">'
        f'<span class="status-dot" style="background:{dot};box-shadow:0 0 0 5px {dot}22;"></span>'
        f'<div><div class="status-title">{status}</div>'
        f'<div class="status-caption">{resumo}</div></div></div>'
        f'<span class="status-tag" style="{tag_style}">{tag}</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-heading"><h2>Resumo agora</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Indicadores essenciais, sem precisar entrar em cada módulo.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    indicadores = [
        ("🍲  ITENS NO BUFFET", len(alimentos) if dados else "—"),
        ("🔴  REPOSIÇÃO", len(criticos) if dados else "—"),
        ("🟡  EM ATENÇÃO", len(atencao) if dados else "—"),
        ("↻  ATIVIDADES", len(historico) if dados else "—"),
    ]
    for coluna, (rotulo, valor) in zip((c1, c2, c3, c4), indicadores):
        coluna.markdown(
            f'<div class="kpi-card"><div class="kpi-label">{rotulo}</div>'
            f'<div class="kpi-value">{valor}</div></div>',
            unsafe_allow_html=True,
        )

    if dados:
        st.caption(f"Última atualização: {dados.get('atualizado_em', 'não informada')}  ·  Dados simulados")
    else:
        st.warning("Dados do buffet ainda não disponíveis. Abra o módulo e registre uma leitura.")

    st.markdown('<div class="section-heading"><h2>O que precisa da equipe?</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Prioridade à esquerda. Visão completa do buffet à direita.</div>', unsafe_allow_html=True)

    left, right = st.columns([0.82, 1.55], gap="large")
    with left:
        if criticos:
            item = criticos[0]
            nome = html.escape(str(item.get("nome", "Alimento")))
            area = html.escape(str(item.get("area", "Área não informada")))
            nivel = html.escape(str(item.get("nivel", "")))
            total = len(criticos)
            st.markdown(
                f'<div class="priority-panel"><div class="priority-kicker">🔔 Prioridade principal</div>'
                f'<div class="priority-name">{nome}</div>'
                f'<div class="priority-location">{area}</div>'
                f'<div class="priority-action">REPOR AGORA · {nivel.upper()}</div>'
                f'<div class="activity-summary"><span class="activity-chip">+{total-1} outro(s) item(ns) crítico(s)</span></div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if total > 1:
                with st.expander("Ver outras prioridades"):
                    for x in criticos[1:]:
                        st.write(f"🔴 {x.get('nome', 'Alimento')} · {x.get('area', '')}")
        elif atencao:
            st.markdown(
                f'<div class="priority-panel"><div class="priority-kicker">🟡 Monitorar</div>'
                f'<div class="priority-name">{len(atencao)} item(ns)</div>'
                f'<div class="priority-location">Nível médio de abastecimento</div>'
                f'<div class="priority-action" style="background:#fff1d8;color:#98651e;">ACOMPANHAR</div></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="no-alert">✓<br>Sem reposições pendentes</div>', unsafe_allow_html=True)

        if st.button("↻ Atualizar painel", use_container_width=True):
            st.rerun()

    with right:
        st.markdown("#### Nível do buffet")
        if alimentos:
            tiles = []
            for item in alimentos:
                nome = html.escape(str(item.get("nome", "Alimento")))
                area = html.escape(str(item.get("area", "")))
                nivel = str(item.get("nivel", "Não informado"))
                pct, cls, cor = nivel_visual(nivel)
                nivel_safe = html.escape(nivel)
                tiles.append(
                    f'<div class="food-tile"><div class="food-tile-head">'
                    f'<div class="food-title">{nome}</div><span class="food-badge {cls}">{nivel_safe}</span></div>'
                    f'<div class="food-sub">{area}</div>'
                    f'<div class="level-track"><div class="level-fill" style="width:{pct}%;background:{cor};"></div></div></div>'
                )
            st.markdown('<div class="food-grid">' + "".join(tiles) + '</div>', unsafe_allow_html=True)
        else:
            st.info("Os níveis aparecerão aqui após a primeira leitura.")

    st.markdown('<div class="section-heading"><h2>Atalhos dos módulos</h2></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Os detalhes continuam disponíveis no menu lateral.</div>', unsafe_allow_html=True)
    a, b = st.columns(2, gap="medium")
    with a:
        st.markdown("""
        <div class="module-card"><h3>⚖️ Balança Inteligente</h3><p>Pesagem e análise do prato.</p></div>
        <div class="module-card"><h3>🍲 Monitoramento do Buffet</h3><p>Níveis das cubas e reposição.</p></div>
        <div class="module-card"><h3>♻️ Desperdício e Experiência</h3><p>Consumo, sobras e experiência.</p></div>
        """, unsafe_allow_html=True)
    with b:
        st.markdown("""
        <div class="module-card"><h3>👥 Fluxo e Atendimento</h3><p>Movimento, filas e espera.</p></div>
        <div class="module-card"><h3>🪑 Gestão de Mesas</h3><p>Ocupação e disponibilidade.</p></div>
        """, unsafe_allow_html=True)

    st.caption("Protótipo acadêmico · dados simulados para demonstração.")



st.markdown("""
<style>
/* Ajustes finais de contraste e legibilidade */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #d4ded5 !important;
}
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] *,
div[data-testid="stMetricLabel"] p {
    color: #43564a !important;
    opacity: 1 !important;
    font-weight: 650 !important;
}
div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] * {
    color: #20372a !important;
    opacity: 1 !important;
}
div[data-testid="stMetricDelta"],
div[data-testid="stMetricDelta"] * {
    color: #52645a !important;
    opacity: 1 !important;
}
.stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
    color: #596a60 !important;
    opacity: 1 !important;
}
.section-subtitle, .location-line, .food-sub, .priority-location {
    color: #5c6c62 !important;
}
.food-title, .module-card h3, .section-heading h2 {
    color: #263b2e !important;
}
.food-badge, .pill, .status-tag {
    font-weight: 800 !important;
}
.status-caption {
    color: #596a60 !important;
}
.priority-kicker {
    color: #875719 !important;
}
.activity-chip {
    color: #4c5d52 !important;
    background: #f4f7f3 !important;
}
</style>
""", unsafe_allow_html=True)



st.markdown("""
<style>
/* Força texto preto nos títulos dos cartões de indicadores */
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label *,
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] *,
div[data-testid="stMetricLabel"] p,
div[data-testid="stMetricLabel"] span,
div[data-testid="stMetricLabel"] svg,
[data-testid="stMetric"] [data-testid="stMarkdownContainer"],
[data-testid="stMetric"] [data-testid="stMarkdownContainer"] * {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    opacity: 1 !important;
}
</style>
""", unsafe_allow_html=True)


pagina = st.navigation(
    [
        st.Page(visao_geral, title="Visão Geral", icon="🏠", default=True, url_path="visao-geral"),
        st.Page("modulos/balanca_inteligente/app.py", title="Balança Inteligente", icon="⚖️", url_path="balanca-inteligente"),
        st.Page("modulos/monitoramento_buffet/app.py", title="Monitoramento do Buffet", icon="🍲", url_path="monitoramento-buffet"),
        st.Page("modulos/atendimento/app.py", title="Fluxo e Atendimento", icon="👥", url_path="fluxo-atendimento"),
        st.Page("modulos/gestao_mesas/app.py", title="Gestão de Mesas", icon="🪑", url_path="gestao-mesas"),
        st.Page("modulos/desperdicio/app.py", title="Desperdício e Experiência", icon="♻️", url_path="desperdicio-experiencia"),
    ],
    position="sidebar",
)

pagina.run()
