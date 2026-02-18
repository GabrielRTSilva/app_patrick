# Camada 'Silver'

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Tabela de preços (regras do enunciado)
PRECO_PLANO = {
    "Mensal -1x na semana": 170.0,
    "Mensal - 2x na semana": 300.0,
    "Plano Trimestral": 840.0,   # conforme instrução (2x semana)
    "Aula Avulsa": 50.0
}

def _to_datetime_br(s: pd.Series) -> pd.Series:
    # "26/04/1999"
    return pd.to_datetime(s, format="%d/%m/%Y", errors="coerce")

def _calcular_idade(dt_nasc: pd.Series, ref: datetime | None = None) -> pd.Series:
    ref = ref or datetime.now()
    anos = (ref - dt_nasc).dt.days / 365.25
    return np.floor(anos).astype("Int64")

def _faixa_etaria(idade: pd.Series) -> pd.Categorical:
    bins = [0, 17, 24, 34, 44, 200]
    labels = ["<18", "18–24", "25–34", "35–44", "45+"]
    return pd.cut(idade.astype(float), bins=bins, labels=labels, right=True, include_lowest=True)

def enrich_pessoas(df_pessoas: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """
    - cria dt_nascimento_dt, idade, faixa_etaria
    - cria data_inicio_plano (mock) para o gráfico de linha
    """
    rng = np.random.default_rng(seed)
    df = df_pessoas.copy()

    df["dt_nascimento_dt"] = _to_datetime_br(df["Data de Nascimento"])
    df["idade"] = _calcular_idade(df["dt_nascimento_dt"])
    df["faixa_etaria"] = _faixa_etaria(df["idade"])

    # Mock de Data de Início do Plano (últimos 90 dias)
    hoje = datetime.now().date()
    offsets = rng.integers(low=0, high=90, size=len(df))
    df["data_inicio_plano"] = [hoje - timedelta(days=int(x)) for x in offsets]
    df["data_inicio_plano"] = pd.to_datetime(df["data_inicio_plano"])

    return df

def montar_fato_receita(df_pessoas_enriched: pd.DataFrame, df_pagamentos: pd.DataFrame) -> pd.DataFrame:
    """
    Junta pessoas + pagamentos por CPF.
    Calcula receita estimada com base no Serviço (plano).
    """
    dfp = df_pagamentos.copy()
    dfp = dfp.rename(columns={"CPF do Membro": "CPF"})

    # Serviço = plano da DIM_PESSOAS (regra), então podemos confiar no campo Serviço
    dfp["vl_receita"] = dfp["Serviço"].map(PRECO_PLANO).fillna(0.0)

    # join para trazer atributos analíticos (modalidade/cidade/horário etc.)
    join_cols = [
        "CPF", "Sexo", "faixa_etaria", "Cidade", "Bairro", "Modalidade",
        "Em que nível você se considera hoje?", "Qual seu objetivo com o esporte?",
        "Escolha um turno", "Escolha os dias", "Escolha um horário"
    ]
    base = df_pessoas_enriched[join_cols].copy()

    fato = dfp.merge(base, on="CPF", how="left")
    return fato

# ---------- KPIs ----------

def kpi_media_idade_por_sexo(df_pessoas_enriched: pd.DataFrame) -> pd.DataFrame:
    return (
        df_pessoas_enriched
        .groupby("Sexo", dropna=False)["idade"]
        .mean()
        .round(1)
        .reset_index(name="idade_media")
    )

def serie_novos_planos_por_dia(df_pessoas_enriched: pd.DataFrame) -> pd.DataFrame:
    s = (
        df_pessoas_enriched
        .groupby(df_pessoas_enriched["data_inicio_plano"].dt.date)["CPF"]
        .nunique()
        .reset_index(name="qtd_membros")
        .rename(columns={"data_inicio_plano": "dia"})
    )
    s["dia"] = pd.to_datetime(s["dia"])
    return s.sort_values("dia")

def distribuicao_turmas(df_pessoas_enriched: pd.DataFrame) -> pd.DataFrame:
    # Turno x Dias x Horário (contagem de membros)
    return (
        df_pessoas_enriched
        .groupby(["Escolha um turno", "Escolha os dias", "Escolha um horário"], dropna=False)["CPF"]
        .nunique()
        .reset_index(name="qtd_membros")
    )

# ---------- Financeiro (receita) ----------

def receita_total_mensal(fato_receita: pd.DataFrame) -> float:
    return float(fato_receita["vl_receita"].sum())

def receita_por(fato_receita: pd.DataFrame, col: str) -> pd.DataFrame:
    return (
        fato_receita
        .groupby(col, dropna=False)["vl_receita"]
        .sum()
        .reset_index()
        .sort_values("vl_receita", ascending=False)
    )

def distribuicao_forma_pagamento(df_pagamentos: pd.DataFrame) -> pd.DataFrame:
    out = (
        df_pagamentos["Forma de Pagamento"]
        .astype(str)
        .value_counts(dropna=False)
        .reset_index()
    )
    # O reset_index pode gerar nomes diferentes conforme versão do pandas,
    # então padronizamos explicitamente:
    out.columns = ["Forma de Pagamento", "qtd"]
    return out


def kpis_receita_modalidade_mvp(fato_receita: pd.DataFrame) -> dict:
    """
    Conforme seu KPI solicitado:
    - Receita Futevôlei (real)
    - Receita Vôlei (0)
    - Receita Beach Tennis (0)
    """
    receita_fute = float(fato_receita.loc[fato_receita["Modalidade"] == "Futevôlei", "vl_receita"].sum())
    return {
        "Receita Futevôlei": receita_fute,
        "Receita Vôlei": 0.0,
        "Receita Beach Tennis": 0.0
    }
