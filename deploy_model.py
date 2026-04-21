# Python libraries
import streamlit as st
from PIL import Image
import os

# User module files
from modelo_basico import mb
from modelo_aportacion import aportacion
from modelo_aportacion_paul import aportacion_paulson
from modelo_basico_paul import mb_paulson
from modelo_basico_completo import mb_completo

def main():

    #############
    # Main page #
    #############
    logo_path = os.path.join(os.path.dirname(__file__), "Credere_Logo2.png")

    st.sidebar.image(logo_path)
    options = ['Inicio', 'Modelo Basico', 'Modelo Aportación', 'Modelo Basico Paulson', 'Modelo Aportación Paulson', 'Modelo Básico completo']
    choice = st.sidebar.selectbox("Menu", options, key='1')

    if choice == 'Inicio':
        st.markdown(
            """
            <h1 style='text-align: center;'>Creador de informes financieros</h1>
            """,
            unsafe_allow_html=True,
        )
        st.image(logo_path, use_column_width=True)
        st.markdown(
            """
            <p style='text-align: center;'>Propiedad exclusiva de Credere Capital INC.</p>
            """,
            unsafe_allow_html=True,
        )
        pass

    elif choice == 'Modelo Basico':
        mb()

    elif choice == 'Modelo Aportación':
        aportacion()

    elif choice == 'Modelo Basico Paulson':
        mb_paulson()

    elif choice == 'Modelo Aportación Paulson':
        aportacion_paulson()
    
    elif choice == 'Modelo Básico completo':
        mb_completo()


    else:
        st.stop()


main()