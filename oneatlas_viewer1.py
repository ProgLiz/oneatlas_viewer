import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

st.set_page_config(page_title="OneAtlas Viewer", layout="wide")

st.title("🛰️ OneAtlas Image Viewer")

st.markdown("""
Visualiza imágenes de **OneAtlas (Airbus)** mediante **WMTS**.  
Usa tu `API Key` y ajusta el brillo o contraste directamente sobre la vista del mapa.
""")

# Entradas del usuario
api_key = st.text_input("🔑 API Key de OneAtlas", type="password")
wmts_url = st.text_input("🌐 URL del servicio WMTS (sin parámetros finales)")

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitud inicial", value=19.4326, step=0.0001)
with col2:
    lon = st.number_input("Longitud inicial", value=-99.1332, step=0.0001)

zoom = st.slider("🔍 Nivel de zoom inicial", 1, 20, 10)

# Controles de imagen
st.markdown("### 🎨 Ajustes visuales")
col3, col4 = st.columns(2)
with col3:
    brillo = st.slider("Brillo", 0.5, 2.0, 1.0, 0.1)
with col4:
    contraste = st.slider("Contraste", 0.5, 2.0, 1.0, 0.1)

# Función para crear el mapa
def generar_mapa(api_key, wmts_url, lat, lon, zoom):
    m = folium.Map(location=[lat, lon], zoom_start=zoom, control_scale=True)
    tile_url = f"{wmts_url}?apiKey={api_key}"

    folium.TileLayer(
        tiles=tile_url,
        name="OneAtlas Imagery",
        attr="OneAtlas © Airbus",
        overlay=True,
        control=True
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m

# Mantener el mapa persistente
if "mapa" not in st.session_state:
    st.session_state.mapa = None

# Botón para generar mapa
if st.button("Generar mapa"):
    if api_key and wmts_url:
        st.session_state.mapa = generar_mapa(api_key, wmts_url, lat, lon, zoom)
    else:
        st.warning("⚠️ Ingresa tanto la API Key como la URL del servicio WMTS.")

# Mostrar mapa (si ya se generó)
if st.session_state.mapa:
    st_folium(st.session_state.mapa, width=1200, height=700)
    
    # Aplicar CSS al iframe
    css = f"""
    <style>
    iframe[title="folium"] {{
        filter: brightness({brillo}) contrast({contraste});
        border-radius: 10px;
        transition: all 0.3s ease;
    }}
    </style>
    """
    components.html(css, height=0)
