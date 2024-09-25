import streamlit as st
from PIL import Image
import pandas as pd

st.set_page_config( page_title='Classificação', page_icon='📊', layout='wide' )


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
    # Supondo que seu DataFrame seja df e tenha uma coluna chamada 'Data'
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')  # Converte a coluna 'Data' para datetime
    
    # Criar a coluna 'Mes' com o nome do mês em inglês e traduzir para português
    df['Mes'] = df['Data'].dt.strftime('%B')  # Extrai o mês em inglês
    df['Mes'] = df['Mes'].apply(traduzir_mes)  # Traduz os meses para português sem acentos

    # Criar a coluna 'Ano'
    df['Ano'] = df['Data'].dt.year.astype(str)
    
    return df


def n_player_matches(df_vd):
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



def criar_tabela_pontos(df_vd):
    # Crinado Tabela de Classificação 
    colunas = ['Time Vencedor', 'Time Perdedor', 'Time Empate 1', 'Time Empate 2']
    # Create a new DataFrame with players and the number of matches
    df_players = pd.DataFrame(list(players_matches.items()), columns=['Jogador', 'Partidas'])
    
    # Create a dictionary to store the number of wins for each player
    players_wins = {}
    # Create a dictionary to store the number of losses for each player
    players_losses = {}
    # Create a dictionary to store the number of draws for each player
    players_draws = {}
    
    # Iterate over the columns and count the occurrences of each player in wins
    for column in colunas:
        # Check if the column is "Winning Team"
        if column == 'Time Vencedor':
            players = df_vd[column].apply(lambda x: str(x).split(', ')).explode().tolist()
            
            for player in players:
                if player in players_wins:
                    players_wins[player] += 1
                else:
                    players_wins[player] = 1
        # Check if the column is "Losing Team"
        elif column == 'Time Perdedor':
            players = df_vd[column].apply(lambda x: str(x).split(', ')).explode().tolist()
            
            for player in players:
                if player in players_losses:
                    players_losses[player] += 1
                else:
                    players_losses[player] = 1           
    
        # Check if the column contains "Draw"
        elif 'Empate' in column:
            players = df_vd[column].apply(lambda x: str(x).split(', ')).explode().tolist()
            
            for player in players:
                if player in players_draws:
                    players_draws[player] += 1
                else:
                    players_draws[player] = 1 
                    
    # Create the "Wins" column in the df_players DataFrame
    df_players['Vitorias'] = df_players['Jogador'].map(players_wins).fillna(0).astype(int)
    
    # Create the "Losses" column in the df_players DataFrame
    df_players['Derrotas'] = df_players['Jogador'].map(players_losses).fillna(0).astype(int)
    
    # Create the "Draws" column in the df_players DataFrame
    df_players['Empates'] = df_players['Jogador'].map(players_draws).fillna(0).astype(int)
    
    # Create the "Points" column in the df_players DataFrame
    df_players['Pontos'] = df_players['Vitorias'] * 3 + df_players['Empates']
    
    # Calculate the "Efficiency" column in the df_players DataFrame
    df_players['Aproveitamento'] = (df_players['Pontos'] / (df_players['Partidas'] * 3)) * 100
    df_players['Aproveitamento'] = df_players['Aproveitamento'].map('{:.2f}%'.format)
    
    # Use the drop method to remove the 'nan' row
    df_players = df_players.drop(df_players[df_players['Jogador'] == 'nan'].index)
    
    # Sort the DataFrame based on the "Points" column in descending order
    df_players_points = df_players.sort_values(by='Pontos', ascending=False)
    
    # Create the "Position" column
    df_players_points.insert(0, 'Posicao', range(1, len(df_players) + 1))
    
    df_players_points = df_players_points.reset_index(drop=True)
    
    return df_players_points



def criar_tabela_gols(df_p):
    # List of all players
    all_players = df_p['Jogador'].tolist()
    
    # Count occurrences of each player in the 'Scorer' column
    df_scorer = df['Goleador'].value_counts()
    
    # Convert the resulting series into a DataFrame
    df_scorer = df_scorer.reset_index()
    
    # Rename the columns of the new DataFrame
    df_scorer.columns = ['Jogador', 'Gols']
    
    # Merge the two DataFrames based on the 'Player' column
    df_merge = pd.merge(df_scorer, df_p, on='Jogador', how='right')
    
    # Fill NaN with 0
    df_merge['Gols'] = df_merge['Gols'].fillna(0)

    # Calculate the average and add the 'Average' column to df_merge
    df_merge['Media'] = (df_merge['Gols'] / df_merge['Partidas'])
    df_merge['Media'] = df_merge['Media'].round(2)  # Round to 2 decimal places
    
    # Sort the DataFrame based on the 'Goals' column in descending order
    df_merge = df_merge.sort_values(by=['Gols', 'Media'], ascending=False)
    
    # Add the 'Position' column
    df_merge['Posicao'] = range(1, len(df_merge) + 1)
    
    # Round the 'Goals' column to an integer
    df_merge['Gols'] = df_merge['Gols'].astype(int)
    
    # Reorder the columns
    df_scorer = df_merge[['Posicao', 'Jogador', 'Partidas', 'Gols', 'Media']]
    
    # Convert the resulting series into a DataFrame
    df_scorer = df_scorer.reset_index()
    df_scorer = df_scorer.drop(columns=['index'])

    return(df_scorer)


def criar_tabela_assists(df_p):
    # List of all players
    all_players = df_p['Jogador'].tolist()
    
    # Count occurrences of each player in the 'Scorer' column
    df_assists = df['Assistente'].value_counts()
    
    # Convert the resulting series into a DataFrame
    df_assists = df_assists.reset_index()
    
    # Rename the columns of the new DataFrame
    df_assists.columns = ['Jogador', 'Assistencias']
    
    # Merge the two DataFrames based on the 'Player' column
    df_merge = pd.merge(df_assists, df_p, on='Jogador', how='right')
    
    # Fill NaN with 0
    df_merge['Assistencias'] = df_merge['Assistencias'].fillna(0)
    
    # Calculate the average and add the 'Average' column to df_merge
    df_merge['Media'] = (df_merge['Assistencias'] / df_merge['Partidas'])
    df_merge['Media'] = df_merge['Media'].round(2)  # Round to 2 decimal places
    
    # Sort the DataFrame based on the 'Goals' column in descending order
    df_merge = df_merge.sort_values(by=['Assistencias', 'Media'], ascending=False)
    
    # Add the 'Position' column
    df_merge['Posicao'] = range(1, len(df_merge) + 1)
    
    # Round the 'Goals' column to an integer
    df_merge['Assistencias'] = df_merge['Assistencias'].astype(int)
    
    # Reorder the columns
    df_assists = df_merge[['Posicao', 'Jogador', 'Partidas', 'Assistencias', 'Media']]
    
    # Convert the resulting series into a DataFrame
    df_assists = df_assists.reset_index()
    df_assists = df_assists.drop(columns=['index'])

    return(df_assists)



def pontos_alternate_rows(row_index, num_columns): # Função para estilizar Tabela de Pontos
    # Alterna as cores
    if row_index % 2 == 0:
        return ['background-color: #4D550F'] * num_columns
    else:
        return ['background-color: #2C3109; color: white'] * num_columns 



def gols_alternate_rows(row_index, num_columns):  # Função para estilizar Tabela de Goleadores
    if row_index % 2 == 0:
        return ['background-color: #A64C0E'] * num_columns
    else:
        return ['background-color: #74350A; color: white'] * num_columns



def assists_alternate_rows(row_index, num_columns):  # Função para estilizar Tabela de Goleadores
    if row_index % 2 == 0:
        return ['background-color: #177B71'] * num_columns
    else:
        return ['background-color: #0F514B; color: white'] * num_columns


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

# Criando Tabela de Pontos
df_players_points = criar_tabela_pontos(df_vd)
# Aplicar a estilização a Tabela Pontos
num_columns_points = len(df_players_points.columns)
df_points_styled = df_players_points.style.apply(lambda row: pontos_alternate_rows(row.name, num_columns_points), axis=1)

# Criando Tabela de Goleadores
df_players_gols = criar_tabela_gols(df_players_points)
# Aplicar a estilização a Tabela Pontos
num_columns_gols = len(df_players_gols.columns)
df_gols_styled = df_players_gols.style \
    .apply(lambda row: gols_alternate_rows(row.name, num_columns_gols), axis=1) \
    .format({'Media': '{:.2f}'})  

# Criando Tabela de Assistentes
df_players_assists = criar_tabela_assists(df_players_points)
# Aplicar a estilização a Tabela Pontos
num_columns_assists = len(df_players_assists.columns)
df_assists_styled = df_players_assists.style \
    .apply(lambda row: assists_alternate_rows(row.name, num_columns_assists), axis=1) \
    .format({'Media': '{:.2f}'})  


# =====================================
# Barra Lateral
# =====================================


st.sidebar.markdown('# Dashboard Futsal ')

image2 = Image.open(r'images/logo.png')
st.sidebar.image( image2, use_column_width=True)

st.sidebar.markdown("""---""")
# Filtro Temporada
ano = st.sidebar.selectbox("Selecione a Temporada:", ("2023"))

# Filtrar por ano
df = df[df['Ano'] == ano]
df_vd = df_vd[df_vd['Ano'] == ano]


# =====================================
# Layout Streamlit 
# =====================================


st.header ( f"Tabelas de Classificação Temporada {ano}" )

tab1, tab2 = st.tabs(['Classificação Geral', 'Classificação Mensal'])

with tab1:
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:   
            partidas = len(df_vd)
            col1.metric( 'N° de Partidas', partidas )
        
        with col2:   
            jogadores = len(players_matches)
            col2.metric('N° de Jogadores', jogadores)

        with col3:
            quadras = len(df_vd['Local'].unique())
            col3.metric('N° de Quadras', quadras)

        with col4:   
            gols = len(df)
            col4.metric('N° Gols', gols)
            

    with st.container():
        st.markdown('## Tabela de Classificação')
        st.dataframe(df_points_styled, hide_index=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('### Tabela de Goleadores')              
            st.dataframe(df_gols_styled, hide_index=True)

        with col2:
            st.markdown('### Tabela de Assistentes')
            st.dataframe(df_assists_styled, hide_index=True)


with tab2:
    with st.container():  
         mes= st.radio(
                "Selecione o Mês",
                ("Janeiro", "Fevereiro", "Marco", 
                 "Abril", "Maio", "Junho",
                 "Julho", "Agosto", "Setembro",
                 "Outubro", "Novembro", "Dezembro"),
                 horizontal = True
                 )
    
    # Filtrando o DataFrame pela coluna 'Mes'
    df = df[df['Mes'] == mes]
    df_vd = df_vd[df_vd['Mes'] == mes]
    
    st.markdown("""---""")
    
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:   
            partidas = len(df_vd)
            col1.metric( 'N° de Partidas', partidas )
        
        with col2:   
            # Criando número de partidas
            players_matches = n_player_matches(df_vd)
            jogadores = len(players_matches)
            col2.metric('N° de Jogadores', jogadores)

        with col3:   
            quadras = len(df_vd['Local'].unique())
            col3.metric('N° de Quadras', quadras)

        with col4:   
            gols = len(df)
            col4.metric('N° Gols', gols)
            

    with st.container():
        st.markdown(f'## Top Pontuadores de {mes}')
        # Criando Tabela de Pontos
        df_players_points = criar_tabela_pontos(df_vd)
        # Aplicar a estilização a Tabela Pontos
        num_columns_points = len(df_players_points.columns)
        df_points_styled = df_players_points.style.apply(lambda row: pontos_alternate_rows(row.name, num_columns_points), axis=1)
        st.dataframe(df_points_styled, hide_index=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f'### Top Goleadores de {mes}')              
            # Criando Tabela de Goleadores
            df_players_gols = criar_tabela_gols(df_players_points)
            # Aplicar a estilização a Tabela Pontos
            num_columns_gols = len(df_players_gols.columns)
            df_gols_styled = df_players_gols.style \
                .apply(lambda row: gols_alternate_rows(row.name, num_columns_gols), axis=1) \
                .format({'Media': '{:.2f}'})  
            st.dataframe(df_gols_styled, hide_index=True)


        with col2:
            st.markdown(f'### Top Assistentes de {mes}')
            # Criando Tabela de Assistentes
            df_players_assists = criar_tabela_assists(df_players_points)
            # Aplicar a estilização a Tabela Pontos
            num_columns_assists = len(df_players_assists.columns)
            df_assists_styled = df_players_assists.style \
                .apply(lambda row: assists_alternate_rows(row.name, num_columns_assists), axis=1) \
                .format({'Media': '{:.2f}'})  
            st.dataframe(df_assists_styled, hide_index=True)





                        