import streamlit as st
import pandas as pd

# Configurar la página web
st.set_page_config(
    page_title="Consulta de Catálogo",
    page_icon="💿",
    layout="wide"
)

# Estilos CSS adaptados para visibilidad alta (Adultos Mayores)
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-size: 22px !important;
    }
    .stSelectbox label, .stCheckbox label, .stTextInput label {
        font-size: 22px !important;
        font-weight: bold !important;
    }
    input {
        font-size: 20px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💿 Consulta de Catálogo")

# ID del archivo en Google Drive
ID_ARCHIVO_DRIVE = "1ahKLQPpoE5fKKBIq_C3g6hqYy-u2AG0r"
URL_DESCARGA_EXCEL = f"https://docs.google.com/spreadsheets/d/{ID_ARCHIVO_DRIVE}/export?format=xlsx"

# Optimización de velocidad: Caché de 10 minutos (600 segundos)
@st.cache_data(ttl=600)
def cargar_y_preparar_datos(url):
    try:
        # Cargar excel
        df = pd.read_excel(url, engine="openpyxl")
        
        # Mapeo y renombrado de columnas exactas
        columnas_deseadas = {
            'label': 'Label',
            'artist': 'Artist',
            'album': 'Album',
            'usd': 'Precio',
            'type': 'Type',
            'barcode': 'Barcode',
            'genero': 'Genero',
            'stock': 'Stock',
            'origen': 'Origen'
        }
        
        # Mapeo insensible a mayúsculas/minúsculas para evitar fallos
        columnas_existentes = {col.lower().strip(): col for col in df.columns}
        
        cols_a_seleccionar = []
        nombres_nuevos = {}
        
        for clave, nombre_nuevo in columnas_deseadas.items():
            if clave in columnas_existentes:
                col_real = columnas_existentes[clave]
                cols_a_seleccionar.append(col_real)
                nombres_nuevos[col_real] = nombre_nuevo
                
        # Filtrar y renombrar
        df_sub = df[cols_a_seleccionar].rename(columns=nombres_nuevos)
        
        # Asegurar formato numérico en Stock si existe
        if 'Stock' in df_sub.columns:
            df_sub['Stock'] = pd.to_numeric(df_sub['Stock'], errors='coerce').fillna(0)
            
        return df_sub
    except Exception as e:
        st.error(f"Error al procesar el archivo del catálogo: {e}")
        return None

# Cargar catálogo optimizado
df = cargar_y_preparar_datos(URL_DESCARGA_EXCEL)

if df is not None and not df.empty:
    
    # --- SECCIÓN DE FILTROS ---
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Filtro de Variantes de Type
        if 'Type' in df.columns:
            opciones_type = ["Todos los formatos"] + sorted([str(x) for x in df['Type'].dropna().unique() if str(x).strip() != ""])
            tipo_seleccionado = st.selectbox("1. Filtrar por Formato (Type):", opciones_type)
        else:
            tipo_seleccionado = "Todos los formatos"

    with col2:
        # Filtro de Stock cero
        ocultar_sin_stock = st.checkbox(" Ocultar productos sin stock (Stock 0)", value=True)

    # Buscador por texto
    busqueda = st.text_input("2. Buscar por Artista, Álbum, Label o Código (Opcional):", "")

    # --- APLICACIÓN DE FILTROS EN MEMORIA (Ultra Rápido) ---
    df_filtrado = df.copy()

    # 1. Filtro por Type
    if tipo_seleccionado != "Todos los formatos" and 'Type' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Type'].astype(str) == tipo_seleccionado]

    # 2. Filtro por Stock
    if ocultar_sin_stock and 'Stock' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Stock'] > 0]

    # 3. Filtro por búsqueda de texto
    if busqueda.strip():
        mascara = df_filtrado.astype(str).apply(
            lambda col: col.str.contains(busqueda.strip(), case=False, na=False)
        ).any(axis=1)
        df_filtrado = df_filtrado[mascara]

    # --- RESULTADO FINAL ---
    st.markdown(f"### Resultados encontrados: **{len(df_filtrado)}**")
    
    # Ocultar el índice (números de fila) para una vista limpia
    st.dataframe(
        df_filtrado, 
        use_container_width=True, 
        height=550,
        hide_index=True
    )

else:
    st.info("Cargando el catálogo...")
