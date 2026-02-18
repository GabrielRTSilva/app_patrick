# mod_graficos.py (gold)
import plotly.express as px
import pandas as pd

def graf_linha_novos_planos(serie: pd.DataFrame):
    fig = px.line(
        serie, x="dia", y="qtd_membros",
        markers=True,
        title="Novos membros por dia (Data de início do plano - mock)"
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=320)
    return fig

def graf_bar_distribuicao(df: pd.DataFrame, col: str, titulo: str):
    aux = df[col].value_counts(dropna=False).reset_index()
    aux.columns = [col, "qtd"]
    fig = px.bar(aux, x=col, y="qtd", title=titulo)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=320)
    return fig

def graf_pie_distribuicao(df: pd.DataFrame, col: str, titulo: str):
    aux = df[col].value_counts(dropna=False).reset_index()
    aux.columns = [col, "qtd"]
    fig = px.pie(aux, names=col, values="qtd", title=titulo, hole=0.45)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=320, legend_title_text=col)
    return fig

def graf_heatmap_turmas(df_turmas: pd.DataFrame):
    # Pivot para um heatmap simples por Horário e combinação Turno+Dias
    df_turmas = df_turmas.copy()
    df_turmas["turma"] = df_turmas["Escolha um turno"].astype(str) + " | " + df_turmas["Escolha os dias"].astype(str)

    pv = df_turmas.pivot_table(
        index="Escolha um horário",
        columns="turma",
        values="qtd_membros",
        aggfunc="sum",
        fill_value=0
    ).reset_index()

    pv_melt = pv.melt(id_vars=["Escolha um horário"], var_name="Turma", value_name="qtd_membros")

    fig = px.density_heatmap(
        pv_melt,
        x="Turma",
        y="Escolha um horário",
        z="qtd_membros",
        histfunc="sum",
        title="Distribuição das turmas (Turno x Dias x Horário)"
    )
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=420)
    return fig

def graf_bar_receita(df_receita: pd.DataFrame, col: str, titulo: str):
    fig = px.bar(df_receita, x=col, y="vl_receita", title=titulo)
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=320)
    return fig

def graf_bar_pagamentos(df_dist: pd.DataFrame):
    df = df_dist.copy()

    # Blindagem: tenta detectar colunas
    if "Forma de Pagamento" not in df.columns:
        # se veio como primeira coluna sem nome esperado
        df.columns = ["Forma de Pagamento", "qtd"] if len(df.columns) >= 2 else df.columns

    if "qtd" not in df.columns and "count" in df.columns:
        df = df.rename(columns={"count": "qtd"})

    fig = px.bar(df, x="Forma de Pagamento", y="qtd", title="Distribuição de Forma de Pagamento")
    fig.update_layout(margin=dict(l=10, r=10, t=50, b=10), height=320)
    return fig

