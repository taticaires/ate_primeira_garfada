
import streamlit as st

st.set_page_config(
    page_title="Até a Primeira Garfada",
    page_icon="🍽️",
    layout="wide"
)

# Identidade visual
st.markdown("""
<style>
.stApp {
    background-color: #111315;
}

section[data-testid="stSidebar"] {
    background-color: #191c20;
    border-right: 1px solid #30343a;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    background: linear-gradient(120deg, #202a36, #172027);
    border: 1px solid #354452;
    border-radius: 18px;
    padding: 28px;
    margin-bottom: 24px;
}

.hero h1 {
    color: #f4f1e9;
    font-size: 2.4rem;
    margin-bottom: 8px;
}

.hero p {
    color: #b9c5ce;
    font-size: 1rem;
    margin-bottom: 0;
}

.module-card {
    background: #1b1f23;
    border: 1px solid #343a40;
    border-radius: 14px;
    padding: 20px;
    min-height: 145px;
    margin-bottom: 12px;
}

.module-card h3 {
    color: #f2f0e9;
    font-size: 1.05rem;
    margin-bottom: 10px;
}

.module-card p {
    color: #aeb8c0;
    font-size: 0.88rem;
}

</style>
""", unsafe_allow_html=True)


# Página inicial
def visao_geral():
    st.markdown("""
    <div class="hero">
        <h1>🍽️ Até a Primeira Garfada</h1>
        <p>
        Inteligência operacional para transformar
        a experiência do restaurante.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.caption("BOVINU'S GRILL & BEER · AUGUSTA")

    st.subheader("Central de Inteligência Operacional")

    st.markdown("""
    Acompanhe os principais pontos da operação
    do restaurante em um único ambiente.
    """)

    st.divider()

    col1, col2, col3 = st.columns(3)

    col1.metric("Módulos", "05")
    col2.metric("Ambiente", "Demonstração")
    col3.metric("Integração", "Em evolução")

    st.divider()

    st.subheader("Módulos do sistema")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="module-card">
            <h3>⚖️ Balança Inteligente</h3>
            <p>Análise demonstrativa do prato, pesagem
            e identificação dos alimentos.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="module-card">
            <h3>🍲 Monitoramento do Buffet</h3>
            <p>Acompanhamento das cubas, níveis
            de alimentos e alertas de reposição.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="module-card">
            <h3>♻️ Desperdício e Experiência</h3>
            <p>Registro de consumo, sobras
            e indicadores de experiência.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="module-card">
            <h3>👥 Fluxo e Atendimento</h3>
            <p>Simulação do fluxo de clientes,
            filas e pontos de espera.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="module-card">
            <h3>🪑 Gestão de Mesas</h3>
            <p>Visualização da ocupação,
            disponibilidade e atendimento.</p>
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "Selecione um módulo no menu lateral "
        "para acessar sua demonstração."
    )


# Navegação para os módulos existentes
pagina = st.navigation(
    [
        st.Page(
            visao_geral,
            title="Visão Geral",
            icon="🏠",
            default=True
        ),
        st.Page(
            "modulos/balanca_inteligente/app.py",
            title="Balança Inteligente",
            icon="⚖️"
        ),
        st.Page(
            "modulos/monitoramento_buffet/app.py",
            title="Monitoramento do Buffet",
            icon="🍲"
        ),
        st.Page(
            "modulos/atendimento/app.py",
            title="Fluxo e Atendimento",
            icon="👥"
        ),
        st.Page(
            "modulos/gestao_mesas/app.py",
            title="Gestão de Mesas",
            icon="🪑"
        ),
        st.Page(
            "modulos/desperdicio/app.py",
            title="Desperdício e Experiência",
            icon="♻️"
        ),
    ],
    position="sidebar"
)

pagina.run()
