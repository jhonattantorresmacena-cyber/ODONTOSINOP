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

    # --- FILTROS NA SIDEBAR ---
    st.sidebar.header("🎛️ Filtros de Análise")
    
    # Filtro de Semestre
    lista_semestres = sorted(df['SEMESTRE'].unique()) if 'SEMESTRE' in df.columns else []
    if lista_semestres:
        semestre_selecionado = st.sidebar.selectbox("Selecione o Semestre", ["Todos"] + list(lista_semestres))
    else:
        semestre_selecionado = "Todos"

    # Filtro de Clínica
    lista_clinicas = sorted(df['CLINICA'].unique()) if 'CLINICA' in df.columns else []
    if lista_clinicas:
        clinica_selecionada = st.sidebar.multiselect("Selecione as Clínicas", list(lista_clinicas), default=list(lista_clinicas))
    else:
        clinica_selecionada = []

    # Aplicando os Filtros no DataFrame
    df_filtrado = df.copy()
    if semestre_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['SEMESTRE'] == semestre_selecionado]
    if clinica_selecionada:
        df_filtrado = df_filtrado[df_filtrado['CLINICA'].isin(clinica_selecionada)]

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
    col_m3.metric("Faltam", f"{int(faltam)}")
    
    # Média mensal dinâmica baseada nos meses restantes (ex: assumindo 6 meses no semestre)
    col_m4.metric("Média p/ Mês Necessária", f"{int(faltam / 6 if faltam > 0 else 0)}")

    st.markdown("---")

    # --- GRÁFICOS ---
    col_g1, col_g2 = st.columns([1, 2])
    
    with col_g1:
        # Gráfico de Rosca de Eficiência Total (Limitado a 100% para o visual)
        exibicao_eficiencia = min(eficiencia, 100)
        fig_donut = go.Figure(go.Pie(
            values=[exibicao_eficiencia, 100 - exibicao_eficiencia],
            labels=['Realizado', 'Restante'],
            hole=.75,
            marker_colors=['#003366', '#E2E8F0'], # Azul Fasiclin e Cinza Claro
            showlegend=False,
            textinfo='none'
        ))
        fig_donut.add_annotation(
            text=f"<span style='font-size:14px; color:#64748B;'>Eficiência Total</span><br><span style='font-size:28px; font-weight:bold; color:#003366;'>{int(eficiencia)}%</span>", 
            showarrow=False
        )
        fig_donut.update_layout(
            margin=dict(t=10, b=10, l=10, r=10), 
            height=300,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

    with col_g2:
        # Gráfico de Barras Comparativo Realizado vs Meta por Clínica
        realizado_por_clinica = df_filtrado.groupby('CLINICA')[meses_existentes].sum().sum(axis=1)
        meta_por_clinica = df_filtrado.groupby('CLINICA')['QUANTIDADE DE PROCEDIMENTO POR SEMESTRE'].sum()
        
        # Unindo os dados para garantir alinhamento perfeito dos eixos
        df_grafico = pd.DataFrame({'Realizado': realizado_por_clinica, 'Meta': meta_por_clinica}).fillna(0)
        
        fig_bar = go.Figure(data=[
            go.Bar(name='Realizado', x=df_grafico.index, y=df_grafico['Realizado'], marker_color='#16a34a'),
            go.Bar(name='Meta', x=df_grafico.index, y=df_grafico['Meta'], marker_color='#003366')
        ])
        fig_bar.update_layout(
            barmode='group', 
            title="<b>Comparativo: Realizado vs Meta por Clínica</b>",
            xaxis_title="Clínicas",
            yaxis_title="Quantidade",
            height=320,
            margin=dict(t=40, b=10, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

    # --- TABELA DE DETALHAMENTO ---
    st.markdown("### 📋 Detalhamento dos Procedimentos")
    
    colunas_exibicao = ['CLINICA', 'PROCEDIMENTO', 'QUANTIDADE DE PROCEDIMENTO POR SEMESTRE']
    if 'SEMESTRE' in df_filtrado.columns:
        colunas_exibicao.insert(1, 'SEMESTRE')
        
    st.dataframe(
        df_filtrado[colunas_exibicao].reset_index(drop=True), 
        use_container_width=True
    )

else:
    st.warning("⚠️ Nenhum dado foi carregado. Verifique se a planilha possui dados ou se o link de exportação está correto.")
