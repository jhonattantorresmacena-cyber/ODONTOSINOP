import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(page_title="Dashboard Metas Fasiclin", layout="wide")

# Link da sua planilha (ajustado para exportação CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1EbU1VaMWgao1F848cSUfYGCIPyhLExhffQ935opaDEY/edit?gid=0#gid=0"

@st.cache_data
def load_data():
    df = pd.read_csv(SHEET_URL)
    # Remove espaços extras no início/fim dos nomes das colunas
    df.columns = df.columns.str.strip()
    
    # Lista de colunas para converter em número
    cols_to_fix = ['QUANTIDADE DE ALUNOS', 'QUANTIDADE DE PROCEDIMENTO POR SEMESTRE']
    
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

df = load_data()

# --- SIDEBAR (Filtros) ---
st.sidebar.image("https://metasatendimentosfasiclin.streamlit.app/logo.png", width=150) # Use o link da sua logo real
st.sidebar.title("Filtros")
clinica_sel = st.sidebar.multiselect("Selecione a Clínica", df['CLINICA'].unique(), default=df['CLINICA'].unique())
semestre_sel = st.sidebar.multiselect("Semestre", df['SEMESTRE'].unique(), default=df['SEMESTRE'].unique())

df_filtered = df[(df['CLINICA'].isin(clinica_sel)) & (df['SEMESTRE'].isin(semestre_sel))]

# --- HEADER ---
st.title("📊 Monitoramento de Metas Clínicas")
st.markdown("---")

# --- MÉTRICAS PRINCIPAIS ---
meta_total = df_filtered['QUANTIDADE DE PROCEDIMENTO POR SEMESTRE'].sum()
# Simulando um "Realizado" somando os meses da planilha (ajuste conforme suas colunas de meses)
meses_cols = ['FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO']
realizado_total = df_filtered[df_filtered.columns.intersection(meses_cols)].sum().sum()
percentual = (realizado_total / meta_total) * 100 if meta_total > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Meta Semestral Total", f"{int(meta_total)}")
col2.metric("Realizado Acumulado", f"{int(realizado_total)}", f"{percentual:.1f}%")
col3.progress(percentual / 100)

# --- GRÁFICOS ---
st.markdown("### Análise por Clínica e Procedimento")
c1, c2 = st.columns(2)

with c1:
    fig_bar = px.bar(df_filtered, 
                     x='PROCEDIMENTO', 
                     y='QUANTIDADE DE PROCEDIMENTO POR SEMESTRE',
                     color='CLINICA',
                     title="Meta por Especialidade",
                     barmode='group')
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    fig_pie = px.pie(df_filtered, values='QUANTIDADE DE PROCEDIMENTO POR SEMESTRE', names='CLINICA', 
                     title="Distribuição de Carga por Clínica",
                     hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- TABELA DETALHADA ---
st.markdown("### Dados Analíticos")
st.dataframe(df_filtered, use_container_width=True)
