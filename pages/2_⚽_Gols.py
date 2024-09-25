import streamlit as st
from PIL import Image
import pandas as pd
import datetime
import plotly.express as px


st.set_page_config( page_title='Gols', page_icon='⚽', layout='wide' )

# =====================================
# Funções
# =====================================


# Função para traduzir os meses para português sem acentos
def traduzir_mes(mes_ingles):
    traducao = {
        'January': 'Janeiro',
        'February': 'Fevereiro',
        'March': 'Marco',
        'April': 'Abril',
        'May': 'Maio',
        'June': 'Junho',
        'July': 'Julho',
        'August': 'Agosto',
        'September': 'Setembro',
        'October': 'Outubro',
        'November': 'Novembro',
        'December': 'Dezembro'
    }
    return traducao.get(mes_ingles, mes_ingles)



def add_col_mes_ano(df):
    '''
        Adiciona as colunas Mes e Ano ao dataframe DF 
    '''
    # Supondo que seu DataFrame seja df e tenha uma coluna chamada 'Data'
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')  # Converte a coluna 'Data' para datetime
    
    # Criar a coluna 'Mes' com o nome do mês em inglês e traduzir para português
    df['Mes'] = df['Data'].dt.strftime('%B')  # Extrai o mês em inglês
    df['Mes'] = df['Mes'].apply(traduzir_mes)  # Traduz os meses para português sem acentos

    # Criar a coluna 'Ano'
    df['Ano'] = df['Data'].dt.year.astype(str)
    
    return df


def n_player_matches(df_vd):
    '''
    
    Retorna um Dicionário com a chave jogador e o número de jogos do mesmo.
    
    '''
    colunas = ['Time Vencedor', 'Time Perdedor', 'Time Empate 1', 'Time Empate 2']
    
    # Create a dictionary to store the number of matches each player participated in
    players_matches = {}
    
    # Iterate over the columns and count the occurrences of each player
    for coluna in colunas:
        players = df_vd[coluna].apply(lambda x: str(x).split(', ')).explode().tolist()
        
        for player in players:
            if player in players_matches:
                players_matches[player] += 1
            else:
                players_matches[player] = 1
    
    # Remove the 'nan' key
    if 'nan' in players_matches:
        players_matches.pop('nan')

    return players_matches

def apply_custom_styles(fig, titulo):
    """
    Aplica estilos personalizados ao gráfico Plotly.

    Parâmetros:
    - fig: O objeto figura Plotly a ser estilizado.
    
    Retorna:
    - fig: O objeto figura Plotly estilizado.
    """
    # Definir os estilos personalizados
    custom_styles = {
        'plot_bgcolor': 'rgba(0,0,0,0)',  # Cor de fundo do gráfico
        'paper_bgcolor': 'rgba(0,0,0,0)',  # Cor de fundo da área do "papel"
        'xaxis': {
            'title_font': {'color': '#ffffff'},  # Cor do título do eixo X
            'tickfont': {'color': '#ffffff'},    # Cor dos ticks do eixo X
            'gridcolor': '#222C36'               # Cor da grade do eixo X
        },
        'yaxis': {
            'title_font': {'color': '#ffffff'},  # Cor do título do eixo Y
            'tickfont': {'color': '#ffffff'},    # Cor dos ticks do eixo Y
            'gridcolor': '#222C36'               # Cor da grade do eixo Y
        },
        'colorway': ['#C5D92A'],  # Define a cor das barras (sequência de cores)
        'font': {'color': '#ffffff'},  # Cor padrão dos rótulos (labels)
        'title': {  # Estilos para o título
            'text': titulo,  # Defina o título do gráfico
            'y': 0.95,  # Ajuste da posição vertical do título
            'x': 0.5,  # Centraliza o título horizontalmente
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'color': '#ffffff', 'size': 20}  # Define cor branca e tamanho
        }
    }
    
    # Aplicar estilos ao gráfico
    fig.update_layout(
        plot_bgcolor=custom_styles['plot_bgcolor'],
        paper_bgcolor=custom_styles['paper_bgcolor'],
        xaxis=dict(
            title_font=custom_styles['xaxis']['title_font'],
            tickfont=custom_styles['xaxis']['tickfont'],
            gridcolor=custom_styles['xaxis']['gridcolor']
        ),
        yaxis=dict(
            title_font=custom_styles['yaxis']['title_font'],
            tickfont=custom_styles['yaxis']['tickfont'],
            gridcolor=custom_styles['yaxis']['gridcolor']
        ),
        colorway=custom_styles['colorway'],
        font=custom_styles['font'],
        title=custom_styles['title'], # Adiciona o título ao gráfico
        legend=dict(font=dict(color='white'))
    )

    # Remover bordas das barras
    fig.update_traces(
        marker=dict(line=dict(color='rgba(0,0,0,0)', width=0))  # Remover bordas
    )

    # Definir a cor das barras diretamente
    fig.update_traces(marker=dict(color='#C5D92A'))  # Aqui você define a cor das barras
    
    return fig


def criar_df_locations(df, df_vd):
    '''
    Retorna um novo Dataframe com as seguintes Fetures:
    
        - Local
        - Total Gols
        - N Partidas
        - Media
        
    '''
    # Creating new df
    df_locations = df[['Data']].merge(df_vd[['Data', 'Local']], on='Data')
    
    # Group by Date and Venue, counting the number of occurrences in each group
    df_locations = df_locations.groupby(['Data', 'Local']).size().reset_index(name='N gols')
    
    # Group by Venue and sum the number of goals in each group
    df_locations = df_locations.groupby('Local')['N gols'].sum().reset_index(name='Total Gols')
    
    
    # Add the 'Number of Matches' column to the df_sum_goals_venues DataFrame
    df_locations['N Partidas'] = df_locations['Local'].map(df_vd['Local'].value_counts())
    
    # Display the resulting DataFrame
    df_locations['Media'] = df_locations['Total Gols'] / df_locations['N Partidas']

     # Dicionário para mapeamento das abreviações
    local_abreviations = {
        'Clube Geraldo Santana': 'CGS',
        'Colégio Bom Conselho': 'CBC',
        'Quadra Sintética PUCRS': 'PUCRS'
        }
    
    # Criar a nova coluna com as abreviações
    df_locations['Local abr'] = df_locations['Local'].map(local_abreviations)
    
    return df_locations



def grafico_barras_local(df_locations, col_1, col_2, col_2_laybel):
    '''
    Criar o gráfico de barras referebte aos locais dos jogos
    
    '''
    # Criar o gráfico de barras com plotly express
    fig = px.bar(df_locations, x=col_1, y=col_2, 
                 labels={col_1: ' ', col_2: col_2_laybel},
                 text=col_2)  # Adicionar rótulos nas barras
    
    fig.update_traces(texttemplate='<b>%{text}</b>')
    
    return fig    


def criar_df_tempo(df):
    '''
        Cria o df_tempo, com as seguintes colunas:
            - Mes
            - Ano
            - N Gols
            - N Jogos
            - Media
    '''
    # Dictionario mapeanndo abreviações em PT
    months_pt = {
        'Janeiro': 'Jan',
        'Fevereiro': 'Fev',
        'Marco': 'Mar',
        'Abril': 'Abr',
        'Maio': 'Mai',
        'Junho': 'Jun',
        'Julho': 'Jul',
        'Agosto': 'Ago',
        'Setembro': 'Set',
        'Outubro': 'Out',
        'Novembro': 'Nov',
        'Dezembro': 'Dez'
    }            
    
    # Agregar por mês e ano, contando o número de linhas
    df_aggregated = df.groupby(['Mes', 'Ano']).size().reset_index(name='N Gols')
    
    # Ordenar o DataFrame pela ordem dos meses e pelo ano
    df_aggregated['Mes'] = pd.Categorical(df_aggregated['Mes'], categories=months_pt, ordered=True)
    df_aggregated = df_aggregated.sort_values(['Ano', 'Mes']).reset_index(drop=True)
    
    # Verificar o número de valores únicos por data
    df_n_jogos = df_vd.groupby('Mes')['Data'].nunique().reset_index(name='N Jogos')
    
    # Juntar os DataFrames com base na coluna 'Mes' e 'Ano'
    df_merged = pd.merge(df_aggregated, df_n_jogos, on=['Mes'], how='inner')
    
    df_merged['Media'] = df_merged['N Gols'] / df_merged['N Jogos']
    
    # Substituir os meses no DataFrame com suas abreviações
    df_merged['Mes'] = df_merged['Mes'].map(months_pt)
    
    df_tempo = df_merged
    
    return df_tempo



def grafico_barras_tempo(df_locations, col_1, col_2, col_2_laybel):
    '''
    Criar o gráfico de barras referente ao tempo dos jogos
    '''
    fig = px.bar(df_tempo, x=col_1, y=col_2,
                 text=col_2,  # Adiciona os rótulos das barras
                 labels={col_1: ' ', col_2: col_2_laybel})

    fig.update_traces(texttemplate='<b>%{text}</b>')  # negrito
    
    return fig



def grafico_linhas_tempo(df_tempo):
    '''
    Criar o gráfico de delinhas referente ao tempo dos jogos
    '''
    # Plotar o gráfico de linha
    fig = px.line(df_tempo, x='Mes', y='Media',
    labels={'Mes': ' ', 'Media': 'Média de Gols'},
    markers=True)
    
    fig = apply_custom_styles(fig, titulo='Média de Gols por Mês')
    
    # Atualizar a cor da linha
    fig.update_traces(line=dict(color='#C5D92A'))  # Altere 'blue' para a cor desejada
    
    # Atualizar traços para mostrar os valores
    fig.add_scatter(
    x=df_tempo['Mes'],
    y=df_tempo['Media'],
    mode='markers+text',
    text=df_tempo['Media'].round(2),  # Formatar os valores
    textposition='top center',
    marker=dict(color='#C5D92A'),
    name=''    
    )
    
    return fig


def adicionar_colunas_tipo_gol(df):
    '''
    Cria um novo df e adiciona novas colunas com finalidade de criar a coluna Tipo de Gol
    '''
    # Remover linhas com valores ausentes na coluna 'Placar'
    df = df.dropna(subset=['Placar'])
    
    # Substituir "x" por "-"
    df.loc[:, 'Placar'] = df['Placar'].str.replace('x', '-')
    
    # Dividir a coluna 'Placar' em duas colunas para subtração
    df.loc[:, 'Time A'] = df['Placar'].str.split('-').str[0].astype(int)  # Garantir que seja int
    df.loc[:, 'Time B'] = df['Placar'].str.split('-').str[1].astype(int)  # Garantir que seja int
    
    # Converter para inteiros (caso não tenha sido feito anteriormente)
    df['Time A'] = pd.to_numeric(df['Time A'], errors='coerce').astype(int)
    df['Time B'] = pd.to_numeric(df['Time B'], errors='coerce').astype(int)
    
    # Criar a coluna Resultado
    df.loc[:, 'Resultado'] = df['Time A'] - df['Time B']
    df.loc[:, 'Diferença'] = df['Resultado'].abs()  # Usar a diferença absoluta
    
    # Criar a coluna "Último à Frente"
    df.loc[df['Resultado'] > 0, 'Último à Frente'] = 'Time A'
    df.loc[df['Resultado'] < 0, 'Último à Frente'] = 'Time B'
    df.loc[:, 'Último à Frente'] = df['Último à Frente'].ffill()  # Usar ffill diretamente
    
    # Marcar a primeira linha de cada nova data como Gol Desempate
    df.loc[:, 'Nova Data'] = df['Data'] != df['Data'].shift(1)
    df.loc[df['Nova Data'], 'Tipo de Gol'] = 'Gol Desempate'
    # Remover a coluna 'Nova Data' se não for mais necessária
    df = df.drop(columns=['Nova Data'])
    
    # Criar a coluna Tipo de Gol
    
    # Gol de Empate - Quando Resultado = 0
    df.loc[df['Resultado'] == 0, 'Tipo de Gol'] = 'Gol de Empate'
    
    # Gol de Vantagem
    df.loc[(df['Diferença'] > 1) & (df['Diferença'].diff() > 0), 'Tipo de Gol'] = 'Gol de Vantagem'
    
    # Gol Reduzido
    df.loc[(df['Diferença'] > 0) & (df['Diferença'].diff() < 0), 'Tipo de Gol'] = 'Gol de Desconto'
    
    # Gol Desempate
    df.loc[((df['Resultado'] == 1) | (df['Resultado'] == -1)) & (df['Resultado'].shift(1) == 0) & (df['Último à Frente'] == df['Último à Frente'].shift(1)), 'Tipo de Gol'] = 'Gol Desempate'
    
    # Gol de Virada
    df.loc[((df['Resultado'] == 1) | (df['Resultado'] == -1)) & (df['Resultado'].shift(1) == 0) & (df['Último à Frente'] != df['Último à Frente'].shift(1)), 'Tipo de Gol'] = 'Gol de Virada'
    
    # Marcar a primeira linha de cada nova data como Gol Desempate
    df.loc[:, 'Nova Data'] = df['Data'] != df['Data'].shift(1)
    df.loc[df['Nova Data'], 'Tipo de Gol'] = 'Gol Desempate'
    # Remover a coluna 'Nova Data' se não for mais necessária
    df = df.drop(columns=['Nova Data'])
    
    return df



def grafico_tipo_gols():
    '''
    Cria Garfico de Barra Tipo de Gol
    '''
    #Grafico
    tipo_gol.columns = ['Tipo de Gol', 'Count']
    # Criar o gráfico de barras
    fig = px.bar(tipo_gol, x='Tipo de Gol', y='Count',
                 text='Count',
                 labels={'Count': 'Gols', 'Tipo de Gol': 'Tipo de Gol',})
    
    fig.update_traces(texttemplate='<b>%{text}</b>')  # negrito
    return fig



def criar_df_tempo_segmentos(df):
    df.loc[df['Minuto'] < 20, 'Segmento do Jogo'] = "Início"
    df.loc[(df['Minuto'] >= 20) & (df['Minuto'] < 40), 'Segmento do Jogo'] = "Meio"
    df.loc[df['Minuto'] >= 40, 'Segmento do Jogo'] = "Fim"

    # Agrupar por Segmento do Jogo e contar ocorrências de cada categoria
    contagem_segmentos = df['Segmento do Jogo'].value_counts()

    # Reordenar os segmentos como Início, Meio, Fim
    segmentos_ordenados = ['Início', 'Meio', 'Fim']
    contagem_segmentos = contagem_segmentos.reindex(segmentos_ordenados)

    # Criar DataFrame para os segmentos
    df_segmentos = pd.DataFrame({
        'Segmento do Jogo': segmentos_ordenados,
        'Contagem': contagem_segmentos
    })

    return df_segmentos



def grafico_barra_segmento():
    # Criar o gráfico de barras
    fig = px.bar(
        df_segmentos,
        x='Segmento do Jogo',
        y='Contagem',
        text='Contagem',
        labels={'Contagem': 'Gols', 'Segmento do Jogo': ' '} 
        )
    
    # Estilizar o gráfico
    fig.update_traces(texttemplate='<b>%{text}</b>',
    marker_color=['#C5D92A', '#8D9C1C', '#4F5810'])
    
    return fig


# -----------------------------------Início da Estrutura Lógica do Código ----------------------------------

# =====================================
# Import dataset
# =====================================


df = pd.read_excel('dataset/Futsal_2023_gols.xlsx')
df_vd = pd.read_excel('dataset/Futsal_2023_game_results.xlsx')


# =====================================
# Limpeza do dataset
# =====================================


#Adicionado Mes e Ano aos 2 dfs
df = add_col_mes_ano(df)
df_vd = add_col_mes_ano(df_vd)

# Criando número de partidas
players_matches = n_player_matches(df_vd)

# Adicionar Local no df
df = pd.merge(df, df_vd[['Data', 'Local']], on='Data', how='left')

#Ajustaddo DateTime
df['Data'] = pd.to_datetime(df['Data'], format='%d-%m-%Y')
df_vd['Data'] = pd.to_datetime(df_vd['Data'], format='%d-%m-%Y')


# =====================================
# Barra Lateral
# =====================================


st.sidebar.markdown('# Dashboard Futsal')

image2 = Image.open(r'images/logo.png')
st.sidebar.image( image2, use_column_width=True)

st.sidebar.markdown("""---""")

# Filtro Temporada
ano = st.sidebar.selectbox("Selecione a Temporada:", ("2023"))

# Filtro Data
date_slider = st.sidebar.slider(
    'Selecione a data:',
    value=df_vd['Data'].max().date(),  
    min_value=df_vd['Data'].min().date(),  
    max_value=df_vd['Data'].max().date(),  
    format='DD-MM-YYYY'
)

# Filtro Temporada
local = st.sidebar.multiselect("Selecione os Locais:", 
                              df_vd['Local'].unique(),
                              default=df_vd['Local'].unique()
                              )

# Converter o valor do date_slider para datetime64[ns] antes de usar no filtro
date_slider = pd.to_datetime(date_slider)

# Filtrar por ano
df = df[df['Ano'] == ano]
df_vd = df_vd[df_vd['Ano'] == ano]

#Filtrar por Local
df = df[df['Local'].isin(local)]
df_vd = df_vd[df_vd['Local'].isin(local)]

#filtro de data
df = df.loc[df['Data'] <= date_slider ,:]
df_vd = df_vd.loc[df_vd['Data'] <= date_slider ,:]

# =====================================
# Layout Streamlit 
# =====================================

st.write ( f"# Análise Gols Temporada {ano}" )

if df.empty:
    st.warning(f"Não há dados disponíveis.")
else:

    tab1, tab2 = st.tabs(['Data e Local', 'Características dos Gols'])
    
    with tab1:
        with st.container():
            st.markdown('### Análise por Local')
            col1, col2, col3 = st.columns(3)
            with col1:
                df_locations = criar_df_locations(df, df_vd)
                fig = grafico_barras_local(df_locations, 
                                           col_1='Local abr', 
                                           col_2='N Partidas', 
                                           col_2_laybel = 'N° de Partidas'
                                          ) 
                fig = apply_custom_styles(fig, titulo='Partidas por Quadra')
                st.plotly_chart(fig)
    
            with col2:
                fig = grafico_barras_local(df_locations, 
                                           col_1='Local abr', 
                                           col_2='Total Gols', 
                                           col_2_laybel = 'N° de Gols'
                                          ) 
                fig = apply_custom_styles(fig, titulo='Gols por Quadra')
                st.plotly_chart(fig)
    
            with col3:
                fig = grafico_barras_local(df_locations, 
                                           col_1='Local abr', 
                                           col_2='Media', 
                                           col_2_laybel = 'Media de Gols'
                                          ) 
                fig = apply_custom_styles(fig, titulo='Media de Gols por Quadra')
                fig.update_traces(texttemplate='<b>%{text:.2f}</b>')
                st.plotly_chart(fig)
    
            # Legenda para os 3 graficos
            st.markdown('<div style="text-align: center; font-size: 12px;">Clube Geraldo Santana = CGS ------ Colégio Bom Conselho = CBC ------ Quadra Sintética PUCRS = PUCRS</div>', unsafe_allow_html=True)
    
        with st.container():
            st.markdown('### Análise por Data')
            col1, col2 = st.columns(2)
            with col1:
                df_tempo = criar_df_tempo(df) 
                fig = grafico_barras_tempo(df_locations, 
                                           col_1='Mes', 
                                           col_2='N Jogos', 
                                           col_2_laybel = 'Número de Jogos'
                                          ) 
                # Customizar o layout
                fig = apply_custom_styles(fig, titulo='Partidas por Mês')
                # Mostrar o gráfico
                st.plotly_chart(fig)
    
            with col2:
                fig = grafico_barras_tempo(df_locations, 
                                           col_1='Mes', 
                                           col_2='N Gols', 
                                           col_2_laybel = 'Número de Gols'
                                          ) 
    
                fig = apply_custom_styles(fig, titulo='Gols por Mês')
                # Customizar o layout
                fig.update_traces(texttemplate='<b>%{text}</b>')  # negritp
                st.plotly_chart(fig)
    
        with st.container():
                fig = grafico_linhas_tempo(df_tempo)
                st.plotly_chart(fig)
    
    with tab2:
        # Verificar se todas as linhas da coluna 'Placar' estão vazias
        if df['Placar'].isna().all():
            st.warning('Os gols filtrados não possuem informações de características.')
        else:
        
            with st.container():
                st.markdown('### Característica dos Gols')
                
            with st.container():    
                df_tipo_gols = adicionar_colunas_tipo_gol(df)
                tipo_gol = df_tipo_gols['Tipo de Gol'].value_counts().reset_index()
                fig = grafico_tipo_gols()
                fig = apply_custom_styles(fig, titulo='Contagem de Tipos de Gol')
                st.plotly_chart(fig)
                
            with st.container():
                # Criar o DataFrame
                df_segmentos = criar_df_tempo_segmentos(df)
                fig = grafico_barra_segmento()
                fig = apply_custom_styles(fig, titulo='Gols por Segmento de Jogo')
                #fig.update_traces(texttemplate='<b>%{text}</b>',
                #marker_color=['#C5D92A', '#8D9C1C', '#4F5810'])
            
                # Exibir o gráfico no Streamlit
                st.plotly_chart(fig)
        
            # Legenda para os 3 graficos
            st.markdown('<div style="text-align: center; font-size: 12px;">Alguns gols não foram computados nos gráficos acima pois eles não possuiam minutagem.</div>', unsafe_allow_html=True)