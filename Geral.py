import streamlit as st
from PIL import Image

st.set_page_config( page_title='Geral', page_icon='🏠', layout='wide' )

# -----------------------------------------
# Funções
# -----------------------------------------

st.sidebar.markdown('# Dashboard Futsal ')

image2 = Image.open(r'images/logo.png')
st.sidebar.image( image2, use_column_width=True)

st.sidebar.markdown("""---""")

st.write( "# Dashbord Futsal" )


st.markdown(
    """
    Bem-vindo(a) ao Dashboard Futsal, desenvolvido para explorar de forma interativa as estatísticas de partidas de futsal reais disputadas semanalmente por um grupo de amigos.
    ### Como utulizar o Dashboard?
    - Barra Lateral:
        - Utilize a barra lateral para aplicar filtros e explorar estatísticas detalhadas das partidas e dos jogadores.
    - Classificação:
        - Visualize as tabelas de classificação de pontos, artilheiros e principais assistentes.
    - Gols:
        - Explore indicadores como data, local das partidas (quadras de futsal) e a análise dos gols marcados ao longo do ano.
    - Jogador:
        - Acompanhe diversos indicadores do jogador selecionado, incluindo análises de gols, partidas e interações com companheiros de equipe.

     #### Contato:
     - Linkedin: https://www.linkedin.com/in/thomas-kunzler/
    """
)    
