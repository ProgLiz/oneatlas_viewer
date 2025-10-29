import streamlit as st
import requests
from io import BytesIO
from PIL import Image, ImageEnhance
import xml.etree.ElementTree as ET
import math

st.set_page_config(page_title="OneAtlas WMTS Viewer", layout="wide")
st.title("🛰️ OneAtlas WMTS Viewer")

st.markdown("""
Visualiza imágenes de **OneAtlas (Airbus)** mediante **WMTS**.  
Ingresa la URL de Capabilities y tu API Key. La app generará un mosaico de tiles automáticamente.
""")

# --- Entradas del usuario ---
api_key = st.text_input("🔑 API Key de OneAtlas", type="password")
capabilities_url = st.text_input("🌐 URL del WMTS Capabilities XML")

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitud central", value=21.86, step=0.0001)
with col2:
    lon = st.number_input("Longitud central", value=-100.02, step=0.0001)

zoom_level = st.slider("🔍 Nivel de zoom (TileMatrix)", 11, 19, 15)

# --- Ajustes visuales ---
st.markdown("### 🎨 Ajustes visuales")
col3, col4 = st.columns(2)
with col3:
    brillo = st.slider("Brillo", 0.5, 2.0, 1.0, 0.1)
with col4:
    contraste = st.slider("Contraste", 0.5, 2.0, 1.0, 0.1)

# --- Funciones ---
def download_xml(url, api_key):
    r = requests.get(url, params={"apiKey": api_key})
    r.raise_for_status()
    return r.content

def parse_wmts_capabilities(xml_data):
    """Extrae la información necesaria de los TileMatrixSets y ResourceURL"""
    ns = {
        "wmts": "http://www.opengis.net/wmts/1.0",
        "ows": "http://www.opengis.net/ows/1.1"
    }
    root = ET.fromstring(xml_data)
    # Tomamos el primer layer
    layer = root.find(".//wmts:Layer", ns)
    resource_url_template = layer.find(".//wmts:ResourceURL", ns).attrib['template']
    
    # Tomamos TileMatrixSet
    tms_link = layer.find(".//wmts:TileMatrixSetLink/wmts:TileMatrixSet", ns).text
    tms = root.find(f".//wmts:TileMatrixSet[ows:Identifier='{tms_link}']", ns)
    
    tile_matrices = {}
    for tm in tms.findall("wmts:TileMatrix", ns):
        identifier = tm.find("ows:Identifier", ns).text
        top_left = tm.find("wmts:TopLeftCorner", ns).text
        tile_width = int(tm.find("wmts:TileWidth", ns).text)
        tile_height = int(tm.find("wmts:TileHeight", ns).text)
        matrix_width = int(tm.find("wmts:MatrixWidth", ns).text)
        matrix_height = int(tm.find("wmts:MatrixHeight", ns).text)
        tile_matrices[identifier] = {
            "top_left": [float(x) for x in top_left.split()],
            "tile_width": tile_width,
            "tile_height": tile_height,
            "matrix_width": matrix_width,
            "matrix_height": matrix_height
        }
    return resource_url_template, tile_matrices

def latlon_to_tile(lat, lon, zoom_info):
    """Convierte lat/lon a índice de tile según TopLeftCorner y MatrixWidth/Height"""
    top_left_x, top_left_y = zoom_info['top_left']
    matrix_width = zoom_info['matrix_width']
    matrix_height = zoom_info['matrix_height']

    # EPSG:3857 Web Mercator
    x_merc = lon * 20037508.34 / 180
    y_merc = math.log(math.tan(math.radians(lat)/2 + math.pi/4)) * 20037508.34 / math.pi

    # Normalizamos
    tile_x = int(matrix_width * (x_merc - top_left_x) / (matrix_width * zoom_info['tile_width']))
    tile_y = int(matrix_height * (top_left_y - y_merc) / (matrix_height * zoom_info['tile_height']))
    return tile_x, tile_y

def download_tile(tile_url, api_key):
    r = requests.get(tile_url + f"?apiKey={api_key}")
    r.raise_for_status()
    return Image.open(BytesIO(r.content))

# --- Botón ---
if st.button("🌍 Generar mosaico"):
    if api_key and capabilities_url:
        try:
            xml_data = download_xml(capabilities_url, api_key)
            resource_url_template, tile_matrices = parse_wmts_capabilities(xml_data)
            
            # Tomamos el zoom elegido
            zoom_str = str(zoom_level)
            if zoom_str not in tile_matrices:
                st.error(f"Zoom {zoom_level} no disponible en TileMatrixSet.")
            else:
                zoom_info = tile_matrices[zoom_str]
                tx, ty = latlon_to_tile(lat, lon, zoom_info)

                tile_url = resource_url_template.replace("{TileMatrix}", zoom_str)\
                                                .replace("{TileCol}", str(tx))\
                                                .replace("{TileRow}", str(ty))
                img = download_tile(tile_url, api_key)
                img = ImageEnhance.Brightness(img).enhance(brillo)
                img = ImageEnhance.Contrast(img).enhance(contraste)

                st.image(img, caption=f"Tile Z{zoom_level}, X{tx}, Y{ty}", use_column_width=True)
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
    else:
        st.warning("⚠️ Ingresa Capabilities y API Key.")
