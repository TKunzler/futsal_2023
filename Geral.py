import streamlit as st
from PIL import Image

st.set_page_config( page_title='Geral', page_icon='🏠', layout='wide' )

# Custom CSS
# Definir o estilo com HTML e CSS
st.markdown(
    """
    <style>
    /* Cor de fundo da página principal */
    .stApp {
        background-color: #161620;
    }
    /* Cor de fundo da barra lateral */
    section[data-testid="stSidebar"] {
        background-color: #353541;
    }
    /* Cor da fonte */
    body, .stApp, .stSidebar {
        color: white;
    }

    /* Personaliza a cor do círculo do slider */
    .stSlider > div:nth-child(3) .st-ab {
        background: white; /* Cor do círculo */
    }
    
    /* Personaliza a cor da barra depois do ponto de controle */
    .stSlider > div:nth-child(3) .st-ax {
        background: #C5D92A; /* Cor da barra após o círculo */
    }
    </style>
    """,
    unsafe_allow_html=True
)




st.sidebar.markdown('# Futsal Temporada 2023')
st.sidebar.markdown('## Zere sua fome em qualquer lugar')
st.sidebar.markdown("""---""")

# Exemplo de slider
st.sidebar.slider("Escolha um valor:", 0, 100)

st.write ( "# Dashbord Futsal Temporada 2023" )
  
