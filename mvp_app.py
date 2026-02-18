# Main
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PATH_PESSOAS = BASE_DIR / "data" / "dim_pessoas_novo_formulario_sintetico.xlsx"
PATH_FIN = BASE_DIR / "data" / "dim_pagamentos_sintetico.xlsx"


from mod_origens import carregar_dim_pessoas, carregar_dim_pagamentos
from mod_transformacoes import (
    enrich_pessoas, montar_fato_receita,
    kpi_media_idade_por_sexo, serie_novos_planos_por_dia, distribuicao_turmas,
    distribuicao_forma_pagamento, receita_total_mensal, receita_por, kpis_receita_modalidade_mvp
)
from mod_graficos import (
    graf_linha_novos_planos, graf_bar_distribuicao, graf_pie_distribuicao,
    graf_heatmap_turmas, graf_bar_pagamentos, graf_bar_receita
)

# =========================
# Config + Theme (UX)
# =========================
st.set_page_config(
    page_title="MVP Data CT - Futevôlei",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE = "#0173b1"
BG = "#fffeff"
INK = "#0f0f0f"

st.markdown(
    f"""
    <style>
      .stApp {{
        background: {BG};
        color: {INK};
      }}
      /* Mobile-first: reduz paddings */
      .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1200px;
      }}
      /* Header cards */
      .kpi-card {{
        border: 1px solid rgba(15,15,15,0.08);
        border-radius: 14px;
        padding: 14px 14px;
        background: white;
        box-shadow: 0 6px 18px rgba(15,15,15,0.06);
      }}
      .kpi-title {{
        font-size: 0.85rem;
        color: rgba(15,15,15,0.65);
        margin-bottom: 2px;
      }}
      .kpi-value {{
        font-size: 1.45rem;
        font-weight: 750;
        color: {INK};
      }}
      .section-title {{
        font-size: 1.1rem;
        font-weight: 750;
        margin: 0.25rem 0 0.75rem 0;
      }}
      /* Links e destaques */
      a, a:visited {{ color: {BASE}; }}
      /* Tabs */
      button[data-baseweb="tab"] {{
        font-weight: 650;
      }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Paths (do enunciado)
# =========================
PATH_PESSOAS = r"C:\Users\grtsi\OneDrive\Desktop\Geral\codigos\github\dash_patrick\dim_pessoas_novo_formulario_sintetico.xlsx"
PATH_FIN = r"C:\Users\grtsi\OneDrive\Desktop\Geral\codigos\github\dash_patrick\dim_pagamentos_sintetico.xlsx"

# =========================
# Load + Transform
# =========================
df_pessoas_raw = carregar_dim_pessoas(PATH_PESSOAS)
df_pagamentos = carregar_dim_pagamentos(PATH_FIN)

df_pessoas = enrich_pessoas(df_pessoas_raw)
fato_receita = montar_fato_receita(df_pessoas, df_pagamentos)

# KPI bases
df_media_idade_sexo = kpi_media_idade_por_sexo(df_pessoas)
serie_planos = serie_novos_planos_por_dia(df_pessoas)
df_turmas = distribuicao_turmas(df_pessoas)

dist_pag = distribuicao_forma_pagamento(df_pagamentos)
kpi_receita_total = receita_total_mensal(fato_receita)
kpi_modal = kpis_receita_modalidade_mvp(fato_receita)

# =========================
# Header
# =========================
st.markdown(f"<div class='section-title'>MVP • Inteligência de Dados para Expansão do CT</div>", unsafe_allow_html=True)
st.caption("Objetivo: identificar público, orientar expansão física, melhorar prospecção e fortalecer controle financeiro.")

# =========================
# Tabs (abas)
# =========================
tab_overview, tab_perfil, tab_capacidade, tab_fin = st.tabs([
    "📊 Overview Geral",
    "👥 Perfil dos Membros",
    "⏰ Horários e Capacidade",
    "💰 Financeiro"
])

# =========================
# OVERVIEW
# =========================
with tab_overview:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-title'>Membros (CPF únicos)</div>"
            f"<div class='kpi-value'>{df_pessoas['CPF'].nunique():,}</div></div>",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-title'>Receita Mensal Estimada (MVP)</div>"
            f"<div class='kpi-value'>R$ {kpi_receita_total:,.2f}</div></div>",
            unsafe_allow_html=True
        )
    with c3:
        # KPI de idade média total (extra útil)
        idade_media_total = float(df_pessoas["idade"].mean())
        st.markdown(
            f"<div class='kpi-card'><div class='kpi-title'>Idade Média</div>"
            f"<div class='kpi-value'>{idade_media_total:.1f}</div></div>",
            unsafe_allow_html=True
        )

    st.divider()

    st.plotly_chart(graf_linha_novos_planos(serie_planos), use_container_width=True)

    # Mix rápido (mobile-first: 2 colunas)
    colA, colB = st.columns(2)
    with colA:
        st.plotly_chart(graf_pie_distribuicao(df_pessoas, "Escolha o plano", "Mix de Planos"), use_container_width=True)
    with colB:
        st.plotly_chart(graf_pie_distribuicao(df_pessoas, "Modalidade", "Mix de Modalidades"), use_container_width=True)

# =========================
# PERFIL DOS MEMBROS
# =========================
with tab_perfil:
    # KPI solicitado: Média de Idade x Sexo
    st.markdown("<div class='section-title'>KPI • Média de Idade por Sexo</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    for i, row in df_media_idade_sexo.iterrows():
        with (col1 if i % 2 == 0 else col2):
            st.markdown(
                f"<div class='kpi-card'><div class='kpi-title'>{row['Sexo']}</div>"
                f"<div class='kpi-value'>{row['idade_media']} anos</div></div>",
                unsafe_allow_html=True
            )

    st.divider()

    # Perfil
    st.markdown("<div class='section-title'>Perfil do Público</div>", unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        st.plotly_chart(graf_bar_distribuicao(df_pessoas, "Sexo", "Distribuição por Sexo"), use_container_width=True)
    with r2:
        st.plotly_chart(graf_bar_distribuicao(df_pessoas, "faixa_etaria", "Distribuição por Faixa Etária"), use_container_width=True)

    r3, r4 = st.columns(2)
    with r3:
        st.plotly_chart(graf_bar_distribuicao(df_pessoas, "Cidade", "Distribuição por Cidade"), use_container_width=True)
    with r4:
        # Bairro pode ser grande; ainda vale para MVP
        st.plotly_chart(graf_bar_distribuicao(df_pessoas, "Bairro", "Distribuição por Bairro"), use_container_width=True)

    r5, r6 = st.columns(2)
    with r5:
        st.plotly_chart(graf_bar_distribuicao(df_pessoas, "Em que nível você se considera hoje?", "Distribuição por Nível"), use_container_width=True)
    with r6:
        st.plotly_chart(graf_bar_distribuicao(df_pessoas, "Qual seu objetivo com o esporte?", "Distribuição por Objetivo"), use_container_width=True)

# =========================
# HORÁRIOS E CAPACIDADE
# =========================
with tab_capacidade:
    st.markdown("<div class='section-title'>Distribuição das Turmas</div>", unsafe_allow_html=True)
    st.caption("Visão Turno x Dias x Horários — útil para justificar expansão física e criação de novas turmas.")
    st.plotly_chart(graf_heatmap_turmas(df_turmas), use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(graf_pie_distribuicao(df_pessoas, "Escolha um turno", "Turno (Matutino vs Noturno)"), use_container_width=True)
    with col2:
        st.plotly_chart(graf_bar_distribuicao(df_pessoas, "Escolha um horário", "Preferência por Horário"), use_container_width=True)

# =========================
# FINANCEIRO
# =========================
with tab_fin:
    st.markdown("<div class='section-title'>KPIs • Receita (MVP)</div>", unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    a.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>Receita Total Mensal</div>"
        f"<div class='kpi-value'>R$ {kpi_receita_total:,.2f}</div></div>",
        unsafe_allow_html=True
    )
    b.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>Receita Futevôlei</div>"
        f"<div class='kpi-value'>R$ {kpi_modal['Receita Futevôlei']:,.2f}</div></div>",
        unsafe_allow_html=True
    )
    c.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>Receita Vôlei</div>"
        f"<div class='kpi-value'>R$ {kpi_modal['Receita Vôlei']:,.2f}</div></div>",
        unsafe_allow_html=True
    )
    d.markdown(
        f"<div class='kpi-card'><div class='kpi-title'>Receita Beach Tennis</div>"
        f"<div class='kpi-value'>R$ {kpi_modal['Receita Beach Tennis']:,.2f}</div></div>",
        unsafe_allow_html=True
    )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(graf_bar_pagamentos(dist_pag), use_container_width=True)
    with col2:
        # Receita por plano (serviço)
        rec_plano = receita_por(fato_receita, "Serviço")
        st.plotly_chart(graf_bar_receita(rec_plano, "Serviço", "Receita por Plano (estimada)"), use_container_width=True)

    st.divider()

    st.markdown("<div class='section-title'>Receita por Recortes</div>", unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        rec_cidade = receita_por(fato_receita, "Cidade")
        st.plotly_chart(graf_bar_receita(rec_cidade, "Cidade", "Receita por Cidade (estimada)"), use_container_width=True)
    with r2:
        rec_hor = receita_por(fato_receita, "Escolha um horário")
        st.plotly_chart(graf_bar_receita(rec_hor, "Escolha um horário", "Receita por Horário (estimada)"), use_container_width=True)

    r3, r4 = st.columns(2)
    with r3:
        rec_mod = receita_por(fato_receita, "Modalidade")
        st.plotly_chart(graf_bar_receita(rec_mod, "Modalidade", "Receita por Modalidade (estimada)"), use_container_width=True)
    with r4:
        rec_bairro = receita_por(fato_receita, "Bairro")
        st.plotly_chart(graf_bar_receita(rec_bairro, "Bairro", "Receita por Bairro (estimada)"), use_container_width=True)
