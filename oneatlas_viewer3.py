import streamlit as st
from PIL import Image, ImageEnhance
import requests
from io import BytesIO
import math

st.set_page_config(page_title="OneAtlas WMTS Viewer", layout="wide")
st.title("🛰️ OneAtlas WMTS Image Viewer")

st.markdown("""
Visualiza imágenes de **OneAtlas (Airbus)** mediante **WMTS**.  
Ingresa la URL del servicio WMTS y tu API Key, selecciona latitud, longitud y zoom, y ajusta brillo y contraste.
""")

# --- Entradas del usuario ---
api_key = st.text_input("🔑 API Key de OneAtlas", type="password")
wmts_url_template = st.text_input(
    "🌐 URL del WMTS (usa {z}, {x}, {y} para tiles, ejemplo: .../tiles/{z}/{x}/{y}.png)"
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

# --- Funciones para manejar tiles ---
def deg2num(lat_deg, lon_deg, zoom):
    """Convierte lat/lon a coordenadas de tile {x, y}"""
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def get_tile_image(url):
    """Descargar tile usando requests"""
    headers = {}  # Puedes agregar headers si el WMTS lo requiere
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return Image.open(BytesIO(r.content))

# --- Botón principal ---
if st.button("🌍 Generar mapa"):
    if api_key and wmts_url_template:
        try:
            # Obtener coordenadas del tile central
            x, y = deg2num(lat, lon, zoom)

            # Construir URL reemplazando {z},{x},{y} y agregando API Key
            tile_url = wmts_url_template.format(z=zoom, x=x, y=y) + f"?apiKey={api_key}"

            # Descargar tile
            img = get_tile_image(tile_url)

            # Aplicar brillo y contraste
            enhancer_b = ImageEnhance.Brightness(img)
            img = enhancer_b.enhance(brillo)
            enhancer_c = ImageEnhance.Contrast(img)
            img = enhancer_c.enhance(contraste)

            # Mostrar imagen
            st.image(img, caption=f"Tile Z{zoom}, X{x}, Y{y}", use_column_width=True)

        except Exception as e:
            st.error(f"❌ Error al cargar el tile: {e}")

    else:
        st.warning("⚠️ Ingresa la URL del WMTS y la API Key.")
