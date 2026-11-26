# 🍽️ Até a Primeira Garfada

**Inteligência operacional para transformar a experiência do restaurante.**

[![Aplicação online](https://img.shields.io/badge/Aplicação-online-2E6B4F?logo=streamlit&logoColor=white)](https://ate-primeira-garfada.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Interface-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)

## 🚀 Acesse o protótipo

**[Abrir Até a Primeira Garfada](https://ate-primeira-garfada.streamlit.app/)**

Aplicação demonstrativa desenvolvida para apresentar uma proposta de inteligência operacional aplicada à rotina de um restaurante.

## 💡 Sobre o projeto

O **Até a Primeira Garfada** reúne, em uma interface única, módulos que representam diferentes pontos da operação de um restaurante. A proposta é transformar informações operacionais em sinais visuais claros, apoiar a identificação de prioridades e facilitar a compreensão do funcionamento do salão e do buffet.

O projeto foi desenvolvido como **protótipo acadêmico**. As informações exibidas são simuladas para demonstração e não representam integração ativa com sensores, balanças ou sistemas reais do estabelecimento.

## 🧭 Módulos demonstrativos

- **Visão Geral:** painel central com indicadores resumidos e prioridades operacionais.
- **Balança Inteligente:** demonstração de análise relacionada à pesagem e ao prato.
- **Monitoramento do Buffet:** acompanhamento dos níveis dos alimentos e indicação de reposição.
- **Fluxo e Atendimento:** visualização demonstrativa de fluxo, filas e atendimento.
- **Gestão de Mesas:** acompanhamento de ocupação e disponibilidade.
- **Desperdício e Experiência:** indicadores demonstrativos relacionados ao consumo, às sobras e à experiência.

## ✨ Destaques

- Navegação por módulos em uma única aplicação.
- Painel central de leitura rápida.
- Indicadores e alertas visuais.
- Dados demonstrativos armazenados em arquivos JSON.
- Interface desenvolvida com Streamlit.
- Aplicação publicada para acesso pelo navegador.

## 🛠️ Tecnologias

- Python
- Streamlit
- Pandas
- Altair
- JSON

## ▶️ Executar localmente

Pré-requisitos: Python instalado e Git (opcional, para clonar o repositório).

1. Clone o projeto:

   ```bash
   git clone https://github.com/taticaires/ate_primeira_garfada.git
   ```

2. Entre na pasta:

   ```bash
   cd ate_primeira_garfada
   ```

3. Instale as bibliotecas utilizadas:

   ```bash
   pip install streamlit pandas altair
   ```

4. Inicie a aplicação:

   ```bash
   python -m streamlit run app.py
   ```

O Streamlit abrirá a aplicação no navegador. Use o menu lateral para acessar os módulos.

## 📂 Organização do projeto

```text
ate_primeira_garfada/
├── app.py
└── modulos/
    ├── atendimento/
    ├── balanca_inteligente/
    ├── monitoramento_buffet/
    ├── gestao_mesas/
    └── desperdicio/
```

Cada módulo possui sua própria aplicação e, quando aplicável, arquivos JSON com dados demonstrativos.

## 🎓 Contexto

Projeto acadêmico desenvolvido para apresentação e avaliação, com foco em explorar como uma interface de inteligência operacional pode apoiar a experiência e a organização de um restaurante.

---

**Desenvolvido por Tatiane Caires**  
[Repositório no GitHub](https://github.com/taticaires/ate_primeira_garfada) · [Protótipo online](https://ate-primeira-garfada.streamlit.app/)
