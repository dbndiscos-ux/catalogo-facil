import streamlit as st
import pandas as pd

# Configurar la página web
st.set_page_config(
    page_title="Consulta de Catálogo",
    page_icon="📦",
    layout="wide"
)

# Personalización visual: textos grandes y claros para adultos mayores
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-size: 22px !important;
    }
    .stMultiSelect div {
        font-size: 18px !important;
    }
    input {
        font-size: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Consulta de Catálogo Fácil")

# --- REEMPLAZA SOLO ESTE ID POR EL DE TU ARCHIVO DE GOOGLE DRIVE ---
ID_ARCHIVO_DRIVE = "1ahKLQPpoE5fKKBIq_C3g6hqYy-u2AG0r"

# Enlace directo de exportación directa a formato Excel
URL_DESCARGA_EXCEL = f"https://docs.google.com/spreadsheets/d/{ID_ARCHIVO_DRIVE}/export?format=xlsx"

# Lee el Excel y refresca la información automáticamente
@st.cache_data(ttl=60)  # Revisa cambios en el archivo cada 60 segundos
def cargar_datos(url):
    try:
        return pd.read_excel(url, engine="openpyxl")
    except Exception as e:
        st.error(f"Error al leer el archivo Excel: {e}")
        return None

df = cargar_datos(URL_DESCARGA_EXCEL)

if df is not None and not df.empty:
    columnas_disponibles = list(df.columns)

    st.markdown("### 1. Seleccione qué datos desea ver:")
    columnas_seleccionadas = st.multiselect(
        "Marque o desmarque las columnas que quiera mostrar:",
        options=columnas_disponibles,
        default=columnas_disponibles
    )

    st.markdown("### 2. Buscar un producto (Opcional):")
    busqueda = st.text_input("Escriba lo que desea buscar (ej. artista, título, código):", "")

    if columnas_seleccionadas:
        df_filtrado = df[columnas_seleccionadas]

        if busqueda:
            mascara = df_filtrado.astype(str).apply(
                lambda col: col.str.contains(busqueda, case=False, na=False)
            ).any(axis=1)
            df_filtrado = df_filtrado[mascara]

        st.markdown("### 3. Resultado del Catálogo:")
        st.dataframe(df_filtrado, use_container_width=True, height=500)
    else:
        st.warning("Por favor, seleccione al menos una columna para mostrar.")
else:
    st.info("Cargando el catálogo o verificando acceso al archivo...")
    st.error("No se pudo cargar el catálogo. Verifique el enlace de Google Sheets.")
