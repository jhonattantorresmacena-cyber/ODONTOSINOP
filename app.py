import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da página e Estética Fasiclin
st.set_page_config(page_title="Dashboard Metas Fasiclin", layout="wide", page_icon="📊")

# Link direto para exportação CSV da sua planilha
SHEET_URL = "https://docs.google.com/spreadsheets/d/1EbU1VaMWgao1F848cSUfYGCIPyhLExhffQ935opaDEY/export?format=csv&gid=0"

@st.cache_data(ttl=3600)  # Atualiza o cache a cada 1 hora automaticamente
def load_data():
    try:
        # Lê a planilha e limpa os nomes das colunas de espaços extras
        df = pd.read_csv(SHEET_URL)
        df.columns = [col.strip().replace('\n', ' ') for col in df.columns]
        
        # Tratamento de colunas numéricas
        cols_numericas = ['FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 
                          'QUANTIDADE DE PROCEDIMENTO POR SEMESTRE', 'QUANTIDADE DE ALUNOS']
        
        for col in cols_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados da planilha: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- HEADER ---
    st.title("📊 Monitoramento de Metas Clínicas - Fasiclin")
    st.markdown("---")

    # --- FILTROS NO TOPO (Abaixo do Cabeçalho) ---
    col_filtros1, col_filtros2 = st.columns(2)
    
    with col_filtros1:
        # Filtro de Semestre
        lista_semestres = sorted(df['SEMESTRE'].unique()) if 'SEMESTRE' in df.columns else []
        if lista_semestres:
            semestre_selecionado = st.selectbox("Selecione o Semestre", ["Todos"] + list(lista_semestres))
        else:
            semestre_selecionado = "Todos"

    with col_filtros2:
        # Filtro de Clínica
        lista_clinicas = sorted(df['CLINICA'].unique()) if 'CLINICA' in df.columns else []
        if lista_clinicas:
            clinica_selecionada = st.multiselect("Selecione as Clínicas", list(lista_clinicas), default=list(lista_clinicas))
        else:
            clinica_selecionada = []

    # Aplicando os Filtros no DataFrame
    df_filtrado = df.copy()
    if semestre_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['SEMESTRE'] == semestre_selecionado]
    if clinica_selecionada:
        df_filtrado = df_filtrado[df_filtrado['CLINICA'].isin(clinica_selecionada)]

    st.markdown("---")

    # --- CÁLCULOS DOS INDICADORES ---
    meses_col = ['FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO']
    meses_existentes = df_filtrado.columns.intersection(meses_col)
    
    meta_total = df_filtrado['QUANTIDADE DE PROCEDIMENTO POR SEMESTRE'].sum()
    realizado_total = df_filtrado[meses_existentes].sum().sum()
    
    # Garante que "faltam" não fique negativo se superarem a meta
    faltam = max(0, meta_total - realizado_total) 
    eficiencia = (realizado_total / meta_total * 100) if meta_total > 0 else 0

    # --- CARDS DE MÉTRICAS ---
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Meta Total", f"{int(meta_total)}")
    col_m2.metric("Realizado Total", f"{int(realizado_total)}", delta=f"{int(eficiencia)}% da Meta", delta_color="normal")
    col_m3.metric("Faltam", f"{int(faltam
