import streamlit as st
from PIL import Image

st.set_page_config( page_title='Geral', page_icon='🏠', layout='wide' )


st.sidebar.markdown('# Futsal Temporada 2023')
st.sidebar.markdown('## Zere sua fome em qualquer lugar')
st.sidebar.markdown("""---""")

# Exemplo de slider
st.sidebar.slider("Escolha um valor:", 0, 100)

st.write ( "# Dashbord Futsal Temporada 2023" )
  

