# Camada 'Bronze' da aplicação. 
import pandas as pd
import streamlit as st

@st.cache_data(show_spinner=False)
def carregar_dim_pessoas(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    # Normalizações mínimas
    df["CPF"] = df["CPF"].astype(str).str.replace(r"\D+", "", regex=True).str.zfill(11)
    return df

@st.cache_data(show_spinner=False)
def carregar_dim_pagamentos(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df["CPF do Membro"] = df["CPF do Membro"].astype(str).str.replace(r"\D+", "", regex=True).str.zfill(11)
    return df
