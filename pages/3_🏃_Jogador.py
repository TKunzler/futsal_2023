import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config( page_title='Jogador', page_icon='🏃', layout='wide' )

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



def listar_jogadores(df_vd):
    colunas = ['Time Vencedor', 'Time Perdedor', 'Time Empate 1', 'Time Empate 2']
    
    # Usar um conjunto para armazenar jogadores únicos
    jogadores = set()
    
    # Iterar sobre as colunas e coletar jogadores
    for coluna in colunas:
        # Extrair os jogadores, dividir e adicionar ao conjunto
        players = df_vd[coluna].apply(lambda x: str(x).split(', ')).explode().tolist()
        jogadores.update(players)  # Atualiza o conjunto com jogadores da coluna

    # Remover 'nan' se estiver presente
    jogadores.discard('nan')
    
    return list(jogadores)  # Retornar a lista de jogadores únicos


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



def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))



def plot_player_img():
    # Definir valores padrão (0) caso o jogador não tenha jogado ainda
    n_partidas = str(df_players_points.loc[df_players_points['Jogador'] == jogador, 'Partidas'].values[0]) if not df_players_points.loc[df_players_points['Jogador'] == jogador, 'Partidas'].empty else '0'
    n_pontos = str(df_players_points.loc[df_players_points['Jogador'] == jogador, 'Pontos'].values[0]) if not df_players_points.loc[df_players_points['Jogador'] == jogador, 'Pontos'].empty else '0'
    n_win = str(df_players_points.loc[df_players_points['Jogador'] == jogador, 'Vitorias'].values[0]) if not df_players_points.loc[df_players_points['Jogador'] == jogador, 'Vitorias'].empty else '0'
    n_draw = str(df_players_points.loc[df_players_points['Jogador'] == jogador, 'Empates'].values[0]) if not df_players_points.loc[df_players_points['Jogador'] == jogador, 'Empates'].empty else '0'
    n_lose = str(df_players_points.loc[df_players_points['Jogador'] == jogador, 'Derrotas'].values[0]) if not df_players_points.loc[df_players_points['Jogador'] == jogador, 'Derrotas'].empty else '0'
    # Ajustar a lógica para a participação direta corretamente
    n_gols = df[df['Goleador'] == jogador].shape[0]  # Número de gols
    n_assists = df[df['Assistente'] == jogador].shape[0]  # Número de assistências
    
    # Se o jogador tiver pelo menos 1 gol ou 1 assistência, a participação direta será a soma
    # Caso contrário, será 0
    n_part_diret = str(n_gols + n_assists) if (n_gols + n_assists) > 0 else '0'
    
    # Converter para string para exibir no gráfico
    n_gols = str(n_gols)
    n_assists = str(n_assists)

    
    
    # Carregar a imagem
    img = Image.open('images/player.jpg')
    
    # Criar um objeto de desenho
    d = ImageDraw.Draw(img)
    
    # Dicionário de valores, cores, tamanhos, estilos e alinhamento
    values_colors_sizes_styles = {
        "nome_jogador": {"value": jogador.upper(), "color": "#161620", "size": 70, "italic": True, "align": "left"}, 
        "n_partidas": {"value": n_partidas, "color": "#FFFFFF", "size": 100, "italic": True, "align": "center"},   
        "n_pontos": {"value": n_pontos, "color": "#C5D92A", "size": 95, "italic": True, "align": "center"},  
        "n_win": {"value": n_win, "color": "#00B050", "size": 70, "italic": False, "align": "center"},   
        "n_draw": {"value": n_draw, "color": "#FFC000", "size": 70, "italic": False, "align": "center"},  
        "n_lose": {"value": n_lose, "color": "#C00000", "size": 70, "italic": False, "align": "center"},   
        "n_part_diret": {"value": n_part_diret, "color": "#FFFFFF", "size": 85, "italic": True, "align": "center"},
        "n_gols": {"value": n_gols, "color": "#ED7D31", "size": 35, "italic": False, "align": "center"},   
        "n_assists": {"value": n_assists, "color": "#38DBCC", "size": 35, "italic": False, "align": "center"}
    }
    
    # Definir as posições onde os valores serão inseridos
    positions = [(100, 65), (108, 222), (230, 385), (115, 555), (228, 555), 
                 (341, 555), (963, 120), (536, 460), (1182, 330)]
    
    # Adicionar os valores na imagem com suas respectivas cores, tamanhos, estilos e alinhamento
    for i, props in enumerate(values_colors_sizes_styles.values()):
        value = props['value']  # Pega o valor real para ser exibido
        rgb_color = hex_to_rgb(props['color'])  # Converte a cor hexadecimal para RGB
        
        # Carregar a fonte com base no estilo
        if props['italic']:
            font = ImageFont.truetype('fonts/source-sans-pr-boldItalic.ttf', size=props['size'])  # Fonte itálica
        else:
            font = ImageFont.truetype('fonts/source-sans-pro-bold.ttf', size=props['size'])  # Fonte em negrito
    
        # Calcular a largura do texto para ajustar o alinhamento
        text_bbox = d.textbbox((0, 0), value, font=font)
        text_width = text_bbox[2] - text_bbox[0]  # Largura do texto
        
        # Ajustar a posição com base no alinhamento
        if props['align'] == "center":
            x = positions[i][0] - text_width // 2  # Centralizado
        elif props['align'] == "right":
            x = positions[i][0] - text_width  # Alinhado à direita
        else:  # Padrão é à esquerda
            x = positions[i][0]
    
        y = positions[i][1]
        
        # Desenhar o texto na imagem
        d.text((x, y), value, font=font, fill=rgb_color)
    
    # Exibir a imagem no Streamlit
    st.image(img, use_column_width=True)    



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
        font=custom_styles['font'],
        title=custom_styles['title'],  # Adiciona o título ao gráfico
        legend=dict(font=dict(color='white'))
    )

    return fig



def grafico_pie(df):
    # Definir os valores de gols e assistências
    gols = df[df['Goleador'] == jogador].shape[0]
    assistencias = df[df['Assistente'] == jogador].shape[0]
    
    # Criar o gráfico de pizza
    valores = [gols, assistencias]
    labels = ['Gols', 'Assists']
    
    # Definir as cores para cada fatia
    cores = ['#ED7D31', '#38DBCC']
    
    fig = go.Figure(data=[go.Pie(labels=labels, values=valores, hole=0.4, 
                                 textinfo='label+percent', textposition='inside',
                                 marker=dict(colors=cores),
                                 texttemplate='<b>%{percent:.1%}</b><br>%{value} %{label}</br>',  # Exibe porcentagem e label
                                 textfont=dict(size=14, color='#161620')  # Define o tamanho da fonte
                                )])  
    return fig



def contar_companheiros(df_vd):
    '''
        Conta o número de vezes que o jogador analisado jogou com cada companheiro.
    '''
    # Criar uma lista para armazenar as linhas que contêm exclusivamente o jogador 
    contagem_jogadores = []
    
    # Percorrer as colunas relevantes e verificar a presença exata do jogador
    for _, row in df_vd.iterrows():
        for col in ["Time Vencedor", "Time Perdedor", "Time Empate 1", "Time Empate 2"]:
            players = [player.strip() for player in str(row[col]).split(',')]
            if any(player == jogador for player in players):
                contagem_jogadores.append([p.strip() for p in players if p.strip() != jogador])
    
    # Excluir o jogador da lista
    contagem_jogadores = [player for players in contagem_jogadores for player in players]
    
    # Contar a frequência de cada jogador
    players_count = pd.Series(contagem_jogadores).value_counts()
    
    return players_count



def grafico_companheiros_frequentes(players_count):
    '''
        Gera grafico dee barras contabilizando o numero de vezes que o jogador
        analisado jogou com cada um de seus comapaheiros de time
    '''
    # Criar um DataFrame a partir da série players_count
    df_players = players_count.reset_index()
    df_players.columns = ['Jogador', 'Count']  # Renomear as colunas
    
    # Criar o gráfico de barras verticais
    fig = px.bar(df_players, x='Jogador', y='Count', 
                 labels={'Count': 'Quantidade de Jogos', 'Jogador': ' '},
                 color_discrete_sequence=['#C5D92A'])  
    
    # Adicionar rótulos com os valores em negrito e sem casas decimais
    fig.update_traces(text=df_players['Count'].astype(int).astype(str), textposition='auto')
    
    # Formatar os textos para estarem em negrito
    fig.for_each_trace(lambda t: t.update(text=[f'<b>{v}</b>' for v in t.text]))
    
    return fig



def gerar_listas(df_vd):
    '''
        Gera as listas necessárias para criação do grafico de aproveitamento por
        companheiro de time do jogado analisado
    '''
    # Criar listas para armazenar os jogadores em diferentes situações
    companheiros_v = []
    companheiros_d = []
    companheiros_e = []

    # Percorrer as colunas relevantes e verificar a presença exata do jogador
    for _, row in df_vd.iterrows():
        for col in ["Time Vencedor", "Time Perdedor", "Time Empate 1", "Time Empate 2"]:
            players = [player.strip() for player in str(row[col]).split(',')]
            if any(player == jogador for player in players):
                if col == "Time Vencedor":
                    companheiros_v.extend([p.strip() for p in players if p.strip() != jogador])
                elif col == "Time Perdedor":
                    companheiros_d.extend([p.strip() for p in players if p.strip() != jogador])
                elif col in ["Time Empate 1", "Time Empate 2"]:
                    companheiros_e.extend([p.strip() for p in players if p.strip() != jogador])

    # Contar a frequência de cada jogador em cada lista
    players_count_v = pd.Series(companheiros_v).value_counts()
    players_count_d = pd.Series(companheiros_d).value_counts()
    players_count_e = pd.Series(companheiros_e).value_counts()

    # Criar um DataFrame consolidado com as contagens
    df_plot = pd.DataFrame({
        'Time Vencedor': players_count_v,
        'Time Perdedor': players_count_d,
        'Time Empate': players_count_e
    }).fillna(0)

    # Transformando em int
    df_plot['Time Vencedor'] = df_plot['Time Vencedor'].astype(int)
    df_plot['Time Perdedor'] = df_plot['Time Perdedor'].astype(int)
    df_plot['Time Empate'] = df_plot['Time Empate'].astype(int)

    # Criando coluna Jogos
    df_plot['Jogos'] = df_plot['Time Vencedor'] + df_plot['Time Perdedor'] + df_plot['Time Empate']

    # Criando coluna Pontos
    df_plot['Pontos'] = df_plot['Time Vencedor'] * 3 + df_plot['Time Empate']

    # Calcular a coluna "Aproveitamento"
    df_plot['Aproveitamento'] = (df_plot['Pontos'] / (df_plot['Jogos'] * 3)) * 100
    df_plot['Aproveitamento'] = df_plot['Aproveitamento'].map('{:.0f}%'.format)

    # Criando as listas para retorno
    jogadores = df_plot.index.tolist()
    derrotas = df_plot['Time Perdedor'].tolist()
    empates = df_plot['Time Empate'].tolist()
    vitorias = df_plot['Time Vencedor'].tolist()
    aproveitamento = df_plot['Aproveitamento'].tolist()
    jogos = df_plot['Jogos'].tolist()

    return jogadores, derrotas, empates, vitorias, aproveitamento, jogos



def grafico_companheiros_aproveitamento():
    '''
        Criação do grafico de aproveitamento por
        companheiro de time do jogado analisado
    '''
    # Criando o gráfico
    fig = go.Figure()
    
    # Adicionando barras
    fig.add_trace(go.Bar(
        x=jogadores,
        y=derrotas,
        name='Derrotas',
        marker_color='#960000'
    ))
    
    fig.add_trace(go.Bar(
        x=jogadores,
        y=empates,
        name='Empates',
        marker_color='#E8D806'
    ))
    
    fig.add_trace(go.Bar(
        x=jogadores,
        y=vitorias,
        name='Vitórias',
        marker_color='#00B050'
    ))
    
    # Adicionando rótulos com texto em negrito
    for i, (player, derrota, empate, vitoria, jogo, aproveitamento_val) in enumerate(zip(jogadores, derrotas, empates, vitorias, jogos, aproveitamento)):
        if derrota != 0:
            fig.add_annotation(x=player, y=derrota / 2, text=f'<b>{derrota}</b>', showarrow=False, font=dict(color='white', size=13))
        if empate != 0:
            fig.add_annotation(x=player, y=derrota + empate / 2, text=f'<b>{empate}</b>', showarrow=False, font=dict(color='#161620', size=13))
        if vitoria != 0:
            fig.add_annotation(x=player, y=derrota + empate + vitoria / 2, text=f'<b>{vitoria}</b>', showarrow=False, font=dict(color='white', size=13))
        fig.add_annotation(x=player, y=derrota + empate + vitoria + max(jogos) / 25, text=f'<b>{aproveitamento_val}</b>', showarrow=False, font=dict(color='#C5D92A', size=10))
    
    # Configurações finais do layout
    fig.update_layout(
        barmode='stack',
        xaxis_title=' ',
        yaxis_title='Jogos',
        xaxis_tickangle=-60,
    )
    
    return fig



def adicionar_coluna_segmentos(df):
    '''
        Exclui os gols que nao tem todas as informações
        Cria a etapa do jogo em que os gols ocorreram
    '''
    #Excluir estas datas
    df = df.dropna(subset=['Placar'])
    # Substituir "x" por "-"
    df['Placar'] = df['Placar'].str.replace('x', '-')
    # Criando coluna "Parcela do Jogo"
    df.loc[df['Minuto'] < 20, ['Parcela do jogo']] = "Inicio"
    df.loc[(df['Minuto'] >= 20) & (df['Minuto'] < 40), 'Parcela do jogo'] = "Meio"
    df.loc[df['Minuto'] >= 40 , ['Parcela do jogo']] = "Fim"

    return df


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



def contar_participacoes(df):
    """
    Conta as participações de um jogador em um DataFrame.

    Parâmetros:
    df (pd.DataFrame): O DataFrame contendo os dados do jogo.

    Retorna:
    tuple: Contadores das participações, gols e assistências, como pandas Series.
    """
    # Mapear os pontos para valores numéricos
    pontos_mapping = {'Inicio': 1, 'Meio': 2, 'Fim': 3}

    # Agrupar por Parcela do jogo e contar a ocorrência de cada categoria
    parcela_counts = df[(df['Goleador'] == jogador) | (df['Assistente'] == jogador)]['Parcela do jogo'].value_counts()
    parcela_counts_gols = df[df['Goleador'] == jogador]['Parcela do jogo'].value_counts()
    parcela_counts_assists = df[df['Assistente'] == jogador]['Parcela do jogo'].value_counts()

    # Mapear os pontos para valores numéricos nos índices
    parcela_counts.index = parcela_counts.index.map(pontos_mapping)
    parcela_counts_gols.index = parcela_counts_gols.index.map(pontos_mapping)
    parcela_counts_assists.index = parcela_counts_assists.index.map(pontos_mapping)

    return parcela_counts, parcela_counts_gols, parcela_counts_assists, pontos_mapping

   

def grafico_barra_segmento_jogador():
    '''
        Cria o grafico de barras da distribuição de gol e assists por segmento
    '''
    fig = go.Figure()
    
    # Adicionar as barras para Participações e exibir os valores automaticamente
    fig.add_trace(go.Bar(
        x=parcela_counts.index,
        y=parcela_counts.values,
        name='Participações',
        marker_color='#7030A0',
        text=parcela_counts.values,  # Adicionar os valores
        textposition='outside',  # Exibir os valores acima das barras
        texttemplate='<b>%{text}</b>'  # Formatar o texto em negrito
    ))
    
    # Adicionar as barras para Gols e exibir os valores automaticamente
    fig.add_trace(go.Bar(
        x=parcela_counts_gols.index,
        y=parcela_counts_gols.values,
        name='Gols',
        marker_color='#38DBCC',
        text=parcela_counts_gols.values,  # Adicionar os valores
        textposition='outside',  # Exibir os valores acima das barras
        texttemplate='<b>%{text}</b>'  # Formatar o texto em negrito
    ))
    
    # Adicionar as barras para Assists e exibir os valores automaticamente
    fig.add_trace(go.Bar(
        x=parcela_counts_assists.index,
        y=parcela_counts_assists.values,
        name='Assists',
        marker_color='#ED7D31',
        text=parcela_counts_assists.values,  # Adicionar os valores
        textposition='outside',  # Exibir os valores acima das barras
        texttemplate='<b>%{text}</b>'  # Formatar o texto em negrito
    ))
    
    # Adicionar o título
    fig.update_layout(
        title_font_size=20,
        title_font=dict(weight='bold'),
        xaxis=dict(
            tickvals=list(pontos_mapping.values()),
            ticktext=list(pontos_mapping.keys()),
            tickfont=dict(size=15, family="Arial", color="black", weight='bold'),
        ),
        yaxis=dict(
            title='Valores',  # Adicionar título ao eixo Y, se desejado
            showticklabels=True,  # Exibir labels do eixo Y
            title_font=dict(size=15, family="Arial", color="black", weight='bold'),
            tickfont=dict(size=12, family="Arial", color="black")  # Definir a fonte das labels do eixo Y
        ),
        legend=dict(
            title_text='Legenda',
            font=dict(size=15)
        ),
        barmode='group',  # Definir as barras como agrupadas
        bargap=0.15  # Espaçamento entre as barras
    )
    return fig



def contar_tipos_gols():
    """
        Conta os tipos de gols e assists de um jogador em um DataFrame.
    
        Parâmetros:
        df (pd.DataFrame): O DataFrame contendo os dados do jogo.
    
        Retorna:
        tuple: Contadores das participações, gols e assistências, como pandas Series.
    """
    # Mapear os pontos para valores numéricos
    pontos_mapping = {'Gol de Vantagem': 1, 'Gol de Desconto': 2, 'Gol de Empate': 3, 'Gol Desempate': 4, 'Gol de Virada': 5}
    
    # Agrupar por Parcela do jogo e contar a ocorrência de cada categoria
    parcela_counts = df[(df['Goleador'] == jogador) | (df['Assistente'] == jogador)]['Tipo de Gol'].value_counts()
    parcela_counts_gols = df[df['Goleador'] == jogador]['Tipo de Gol'].value_counts()
    parcela_counts_assists = df[df['Assistente'] == jogador]['Tipo de Gol'].value_counts()
    
    # Mapear os pontos para valores numéricos nos índices
    parcela_counts.index = parcela_counts.index.map(pontos_mapping)
    parcela_counts_gols.index = parcela_counts_gols.index.map(pontos_mapping)
    parcela_counts_assists.index = parcela_counts_assists.index.map(pontos_mapping)
    
    return pontos_mapping, parcela_counts, parcela_counts_gols, parcela_counts_assists


def grafico_barra_tipo_gol_jogador():
    '''
        Plota o grafico dos tipos de gols e asssists do jogador
    '''
    # Criar a figura
    fig = go.Figure()
    
    # Adicionar as barras para Participações e exibir os valores automaticamente
    fig.add_trace(go.Bar(
        x=parcela_counts.index - 0.2,  # Deslocamento para a esquerda
        y=parcela_counts.values,
        name='Participações',
        marker_color='#7030A0',
        text=parcela_counts.values,  # Adicionar os valores
        textposition='outside',  # Exibir os valores acima das barras
        texttemplate='<b>%{text}</b>'  # Formatar o texto em negrito
    ))
    
    # Adicionar as barras para Gols e exibir os valores automaticamente
    fig.add_trace(go.Bar(
        x=parcela_counts_gols.index,  # Sem deslocamento
        y=parcela_counts_gols.values,
        name='Gols',
        marker_color='#38DBCC',
        text=parcela_counts_gols.values,  # Adicionar os valores
        textposition='outside',  # Exibir os valores acima das barras
        texttemplate='<b>%{text}</b>'  # Formatar o texto em negrito
    ))
    
    # Adicionar as barras para Assists e exibir os valores automaticamente
    fig.add_trace(go.Bar(
        x=parcela_counts_assists.index + 0.2,  # Deslocamento para a direita
        y=parcela_counts_assists.values,
        name='Assists',
        marker_color='#ED7D31',
        text=parcela_counts_assists.values,  # Adicionar os valores
        textposition='outside',  # Exibir os valores acima das barras
        texttemplate='<b>%{text}</b>'  # Formatar o texto em negrito
    ))
    
    # Calcular o valor máximo das barras
    max_value = max(parcela_counts.max(), parcela_counts_gols.max(), parcela_counts_assists.max())
    # Definir o limite do eixo Y com 10% a mais
    y_axis_limit = max_value * 1.1
    
    # Adicionar o título
    fig.update_layout(
        xaxis=dict(
            tickvals=list(pontos_mapping.values()),
            ticktext=list(pontos_mapping.keys()),
            tickfont=dict(size=15, family="Arial", color="black", weight='bold'),
        ),
        yaxis=dict(
            title='Valores',  # Adicionar título ao eixo Y, se desejado
            showticklabels=True,  # Exibir labels do eixo Y
            title_font=dict(size=15, family="Arial", color="black", weight='bold'),
            tickfont=dict(size=12, family="Arial", color="black"),  # Definir a fonte das labels do eixo Y
            range=[0, y_axis_limit]  # Definir o limite do eixo Y
        ),
        legend=dict(
            title_text='Legenda',
            font=dict(size=15)
        ),
        barmode='group',  # Definir as barras como agrupadas
        bargap=0  # Espaçamento entre as barras
    )

    return fig



def contar_assists_jogadores(df):
    # Filtrar o DataFrame
    df_jogador = df[(df['Goleador'] == jogador) | (df['Assistente'] == jogador)]
    df_jogador_gols = df[df['Goleador'] == jogador]
    df_jogador_assists = df[df['Assistente'] == jogador]
    
    # Dados para os gráficos
    assistente_counts_goleador = df_jogador[(df_jogador['Goleador'] == jogador) & (df_jogador['Assistente'] != '-')]['Assistente'].value_counts()
    no_assistente_counts = df_jogador[df_jogador['Goleador'] == jogador][df_jogador['Assistente'] == '-']['Goleador'].value_counts()
    assistente_counts_assistente = df_jogador_assists[df_jogador_assists['Goleador'] != "-"]['Goleador'].value_counts()
    
    return assistente_counts_goleador, no_assistente_counts, assistente_counts_assistente



def grafico_barras_assistencias():
    # Criar a figura
    fig = make_subplots(rows=1, cols=3, 
                        column_widths=[0.9, 0.1, 0.9],  # Ajusta as larguras para 45%, 10%, 45%
                        subplot_titles=("Assistencias Recebidas", "Sem Assist", "Assistências Concedidas"))
    
    # Inverter a ordem das barras da esquerda
    assistente_counts_goleador_inverted = assistente_counts_goleador[::-1]
    
    # Gráfico de Assistente Counts Goleador (45% à esquerda) com ordem invertida
    fig.add_trace(go.Bar(x=assistente_counts_goleador_inverted.index, 
                         y=assistente_counts_goleador_inverted.values, 
                         text=assistente_counts_goleador_inverted.values, 
                         texttemplate='<b>%{text}</b>',  # Formata os rótulos em negrito
                         textposition='auto',
                         marker_color='#38DBCC',  
                         name='Assistencias Recebidas'), 
                  row=1, col=1)
    
    # Gráfico de No Assistente Count (10% ao centro)
    fig.add_trace(go.Bar(x=no_assistente_counts.index, 
                         y=no_assistente_counts.values, 
                         text=no_assistente_counts.values, 
                         texttemplate='<b>%{text}</b>',  # Formata os rótulos em negrito
                         textposition='auto', 
                         marker_color='#7030A0',  
                         name='Sem Assistências'), 
                  row=1, col=2)
    
    # Gráfico de Assistente Counts Assistente (45% à direita)
    fig.add_trace(go.Bar(x=assistente_counts_assistente.index, 
                         y=assistente_counts_assistente.values, 
                         text=assistente_counts_assistente.values, 
                         texttemplate='<b>%{text}</b>',  # Formata os rótulos em negrito
                         textposition='auto', 
                         marker_color='#ED7D31',  
                         name='Assistências Concedidas'), 
                  row=1, col=3)
    
    # Encontrar o valor máximo e adicionar 10% de margem
    max_y = max(assistente_counts_goleador.max(), no_assistente_counts.max(), assistente_counts_assistente.max())
    y_max_with_margin = max_y * 1.1  # Adicionar 10% ao valor máximo
    
    # Ajustar os limites do eixo y para todos os gráficos com margem
    fig.update_yaxes(range=[0, y_max_with_margin], row=1, col=1)
    fig.update_yaxes(range=[0, y_max_with_margin], row=1, col=2)
    fig.update_yaxes(range=[0, y_max_with_margin], row=1, col=3)
    
    # Remover os valores do eixo y dos gráficos do meio e da direita
    fig.update_yaxes(showticklabels=False, row=1, col=2)
    fig.update_yaxes(showticklabels=False, row=1, col=3)
    
    # Adicionar rótulos ao eixo X
    fig.update_xaxes(title_text="Assistente", row=1, col=1)
    fig.update_xaxes(title_text="Goleador", row=1, col=2)
    fig.update_xaxes(title_text="Goleador", row=1, col=3)
    
    # Ajuste de layout
    fig.update_layout(height=500, width=1000, 
                      title_text=f"Distribuição das Assistências por Companheiros {jogador}", 
                      title_x=0.2,
                      title_font=dict(size=20),
                      showlegend=False)
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
players_matches2 = n_player_matches(df_vd)

# Adicionar Local no df
df = pd.merge(df, df_vd[['Data', 'Local']], on='Data', how='left')

#Ajustaddo DateTime
df['Data'] = pd.to_datetime(df['Data'], format='%d-%m-%Y')
df_vd['Data'] = pd.to_datetime(df_vd['Data'], format='%d-%m-%Y')


# =====================================
# Barra Lateral
# =====================================


st.sidebar.markdown('# Dashboard Futsal ')

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

players_matches = n_player_matches(df_vd)

# Atualize a tabela de pontos
df_players_points = criar_tabela_pontos(df_vd)

# =====================================
# Layout Streamlit 
# =====================================


st.write ( f"# Análise Jogador Temporada {ano}" )

# Criar um selectbox com os nomes dos jogadores
jogador = st.selectbox("Selecione o Jogador:", sorted(players_matches2.keys()))

# Criando Tabela de Pontos
df_players_points = criar_tabela_pontos(df_vd)

tab1, tab2, tab3 = st.tabs(['Visão Geral ', 'Análise Companheiros', 'Análise Gols e Assistências'])

with tab1:
    with st.container():
        plot_player_img()

if df.empty:
    st.warning(f"Não há dados disponíveis para o jogador {jogador} na temporada {ano}.")
else:
    with tab2:
        with st.container():
            players_count = contar_companheiros(df_vd)
            fig = grafico_companheiros_frequentes(players_count)
            fig = apply_custom_styles(fig, titulo=f'Companheiros mais Frequentes de {jogador}')
            st.plotly_chart(fig)
            
        with st.container():
            jogadores, derrotas, empates, vitorias, aproveitamento, jogos = gerar_listas(df_vd)
            fig = grafico_companheiros_aproveitamento()
            fig = apply_custom_styles(fig, titulo=f'V/E/D + Aproveitamento por Comapanheiro de {jogador}')
            st.plotly_chart(fig)
    
    with tab3:
        with st.container():
            fig = grafico_pie(df)
            fig = apply_custom_styles(fig, titulo=f'Contagem de Tipos de Gol de {jogador}')
            st.plotly_chart(fig)

        # Verificar se todas as linhas da coluna 'Placar' estão vazias
        if df['Placar'].isna().all():
            st.warning('Os gols filtrados não possuem informações de características.')
        else:
            with st.container():
                df = adicionar_coluna_segmentos(df)
                df = adicionar_colunas_tipo_gol(df)
                parcela_counts, parcela_counts_gols, parcela_counts_assists, pontos_mapping = contar_participacoes(df)
                fig = grafico_barra_segmento_jogador()
                fig = apply_custom_styles(fig, titulo=f'Participações de acordo com período de jogo - {jogador}')
                st.plotly_chart(fig)
        
            with st.container():
                pontos_mapping, parcela_counts, parcela_counts_gols, parcela_counts_assists = contar_tipos_gols()
                fig = grafico_barra_tipo_gol_jogador()
                fig = apply_custom_styles(fig, titulo=f'Participações em Tipos de Gol - {jogador}')
                st.plotly_chart(fig)
        
            with st.container():
                assistente_counts_goleador, no_assistente_counts, assistente_counts_assistente = contar_assists_jogadores(df)
                fig = grafico_barras_assistencias()
                st.plotly_chart(fig)
