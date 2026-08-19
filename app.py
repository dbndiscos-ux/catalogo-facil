import streamlit as st
import pandas as pd

# Configuración de la página web
st.set_page_config(
    page_title="Consulta de Catálogo",
    page_icon="📦",
    layout="wide"
)

# Estilo personalizado para agrandar fuentes y botones para adultos mayores
st.markdown("""
    <style>
    .stApp { font-size: 20px; }
    button { height: 3em !important; font-size: 20px !important; }
    div[data-baseweb="select"] { font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Consulta de Catálogo Fácil")
st.write("Seleccione la información que desea consultar de la lista a continuación:")

# --- PEGA AQUÍ TU ENLACE DE GOOGLE SHEETS ---
# Importante: Cambia la parte final del enlace de '/edit?usp=sharing' a '/export?format=csv'
URL_SHEETS = "https://docs.google.com/spreadsheets/d/1ahKLQPpoE5fKKBIq_C3g6hqYy-u2AG0r/edit?usp=sharing&ouid=104266924348859001274&rtpof=true&sd=true"

@st.cache_data(ttl=60)  # Actualiza los datos cada 60 segundos
def cargar_datos(url):
    try:
        return pd.read_csv(url)
    except Exception as e:
        return None

df = cargar_datos(URL_SHEETS)

if df is not None:
    # 1. Selección de columnas
    columnas_disponibles = list(df.columns)
    
    st.subheader("1. Elija qué datos quiere ver:")
    columnas_seleccionadas = st.multiselect(
        "Marque o desmarque las opciones:",
        options=columnas_disponibles,
        default=columnas_disponibles
    )

    # 2. Buscador opcional simple
    st.subheader("2. Buscar un producto (Opcional):")
    busqueda = st.text_input("Escriba el nombre o palabra clave a buscar:", "")

    # Aplicar filtros
    if columnas_seleccionadas:
        df_filtrado = df[columnas_seleccionadas]
        
        if busqueda:
            # Filtra en todas las columnas seleccionadas
            mascara = df_filtrado.astype(str).apply(lambda x: x.str.contains(busqueda, case=False)).any(axis=1)
            df_filtrado = df_filtrado[mascara]

        st.subheader("3. Resultado del Catálogo:")
        st.dataframe(df_filtrado, use_container_width=True, height=400)
    else:
        st.warning("Por favor, seleccione al menos una columna para mostrar.")
else:
    st.error("No se pudo cargar el catálogo. Verifique el enlace de Google Sheets.")