import streamlit as st
from PIL import Image, ImageEnhance
import requests
from io import BytesIO
import math

st.set_page_config(page_title="OneAtlas WMTS Viewer", layout="wide")
st.title("🛰️ OneAtlas WMTS Viewer")

st.markdown("""
Visualiza imágenes de **OneAtlas (Airbus)** mediante **WMTS**.  
Ingresa la URL de tiles con placeholders `{z}`, `{x}`, `{y}` y tu API Key.
""")

# --- Entradas del usuario ---
api_key = st.text_input("🔑 API Key de OneAtlas", type="password")
wmts_url_template = st.text_input(
    "🌐 URL de tiles WMTS (usa {z}, {x}, {y}, ejemplo: .../tiles/1.0.0/default/rgb/EPSG3857/{z}/{x}/{y}.png)"
)

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitud central", value=21.86, step=0.0001)
with col2:
    lon = st.number_input("Longitud central", value=-100.02, step=0.0001)

zoom = st.slider("🔍 Nivel de zoom", 11, 19, 15)

# --- Ajustes visuales ---
st.markdown("### 🎨 Ajustes visuales")
col3, col4 = st.columns(2)
with col3:
    brillo = st.slider("Brillo", 0.5, 2.0, 1.0, 0.1)
with col4:
    contraste = st.slider("Contraste", 0.5, 2.0, 1.0, 0.1)

# --- Funciones para calcular tiles EPSG:3857 ---
def latlon_to_tile_epsg3857(lat, lon, zoom):
    """
    Convierte lat/lon a X/Y de tile en Web Mercator (EPSG:3857)
    usando la convención de Google Maps.
    """
    n = 2 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    lat_rad = math.radians(lat)
    y_tile = int((1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n)
    return x_tile, y_tile

def get_tile_image(url):
    """Descargar tile usando requests"""
    r = requests.get(url)
    r.raise_for_status()
    return Image.open(BytesIO(r.content))

# --- Botón principal ---
if st.button("🌍 Generar mapa"):
    if api_key and wmts_url_template:
        try:
            # Calcular tile central
            x, y = latlon_to_tile_epsg3857(lat, lon, zoom)

            # Armar URL del tile
            tile_url = wmts_url_template.format(z=zoom, x=x, y=y) + f"?apiKey={api_key}"

            # Descargar tile
            img = get_tile_image(tile_url)

            # Aplicar brillo y contraste
            img = ImageEnhance.Brightness(img).enhance(brillo)
            img = ImageEnhance.Contrast(img).enhance(contraste)

            # Mostrar tile
            st.image(img, caption=f"Tile Z{zoom}, X{x}, Y{y}", use_column_width=True)

        except Exception as e:
            st.error(f"❌ Error al cargar el tile: {e}")

    else:
        st.warning("⚠️ Ingresa la URL de tiles y la API Key.")
