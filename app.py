import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da página e Estética Fasiclin
st.set_page_config(page_title="Dashboard Metas Fasiclin", layout="wide")

# Link direto para exportação CSV da sua planilha
SHEET_URL = "https://docs.google.com/spreadsheets/d/1EbU1VaMWgao1F848cSUfYGCIPyhLExhffQ935opaDEY/export?format=csv&gid=0"

@st.cache_data
def load_data():
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

try:
    df = load_data()
    
    # --- HEADER E INDICADORES (Igual ao modelo Sinop) ---
    st.title("📊 Monitoramento de Metas Clínicas - Fasiclin")
    
    # Cálculos para os indicadores
    meses_col = ['FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO']
    meta_total = df['QUANTIDADE DE PROCEDIMENTO POR SEMESTRE'].sum()
    realizado_total = df[df.columns.intersection(meses_col)].sum().sum()
    faltam = meta_total - realizado_total
    eficiencia = (realizado_total / meta_total * 100) if meta_total > 0 else 0

    # Barra de Acompanhamento azul clara (estilo imagem enviada)
    st.info(f"**Acompanhamento de Metas:** Faltam {int(faltam)} procedimentos. Média necessária: {int(faltam/2)}/mês.")

    col_meta1, col_meta2 = st.columns([1, 2])
    
    with col_meta1:
        # Gráfico de Rosca de Eficiência Total
        fig_donut = go.Figure(go.Pie(
            values=[eficiencia, 100-eficiencia],
            labels=['Realizado', 'Restante'],
            hole=.7,
            marker_colors=['#003366', '#f0f2f6'],
            showlegend=False
        ))
        fig_donut.add_annotation(text=f"Eficiência Total<br><b>{int(eficiencia)}%</b>", showarrow=False, font_size=20)
        fig_donut.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_meta2:
        # Gráfico de Barras Comparativo Realizado vs Meta
        realizado_por_clinica = df.groupby('CLINICA')[df.columns.intersection(meses_col)].sum().sum(axis=1)
        meta_por_clinica = df.groupby('CLINICA')['QUANTIDADE DE PROCEDIMENTO POR SEMESTRE'].sum()
        
        fig_bar = go.Figure(data=[
            go.Bar(name='Realizado', x=realizado_por_clinica.index, y=realizado_por_clinica, marker_color='#16a34a'),
            go.Bar(name='Meta', x=meta_por_clinica.index, y=meta_por_clinica, marker_color='#003366')
        ])
        fig_bar.update_layout(barmode='group', title="Realizado vs Meta por Clínica", height=350)
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- TABELA DE DETALHAMENTO ---
    st.markdown("### Detalhamento dos Procedimentos")
    st.dataframe(df[['CLINICA', 'SEMESTRE', 'PROCEDIMENTO', 'QUANTIDADE DE PROCEDIMENTO POR SEMESTRE']], use_container_width=True)

except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
    st.write("Colunas detetadas na planilha:", list(df.columns) if 'df' in locals() else "Não foi possível ler a planilha.")
