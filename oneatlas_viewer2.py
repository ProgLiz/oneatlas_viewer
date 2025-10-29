import streamlit as st
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

# --- Configuración de la página ---
st.set_page_config(page_title="OneAtlas Viewer", layout="wide")

st.title("🛰️ OneAtlas Image Viewer")

st.markdown("""
Visualiza imágenes de **OneAtlas (Airbus)** mediante **WMTS**.  
Usa tu `API Key` y ajusta el brillo o contraste directamente sobre la vista del mapa.
""")

# --- Entradas del usuario ---
api_key = st.text_input("🔑 API Key de OneAtlas", type="password")

col1, col2 = st.columns(2)
with col1:
    lat = st.number_input("Latitud inicial", value=21.86, step=0.0001)
with col2:
    lon = st.number_input("Longitud inicial", value=-100.02, step=0.0001)

zoom = st.slider("🔍 Nivel de zoom inicial", 11, 19, 15)

# --- Controles de imagen ---
st.markdown("### 🎨 Ajustes visuales")
col3, col4 = st.columns(2)
with col3:
    brillo = st.slider("Brillo", 0.5, 2.0, 1.0, 0.1)
with col4:
    contraste = st.slider("Contraste", 0.5, 2.0, 1.0, 0.1)

# --- Botón principal ---
if st.button("🌍 Generar mapa"):
    if api_key:
        # Crear mapa base
        m = folium.Map(location=[lat, lon], zoom_start=zoom, control_scale=True)

        # URL correcta del WMTS (EPSG3857)
        tile_url = (
            "https://access.foundation.api.oneatlas.airbus.com/api/v1/"
            "items/171dd1ed-9599-4e8a-872b-7ce98eba4802/"
            "wmts/tiles/1.0.0/default/rgb/EPSG3857/{z}/{x}/{y}.png"
            f"?apiKey={api_key}"
        )

        # Añadir capa WMTS
        folium.TileLayer(
            tiles=tile_url,
            name="OneAtlas Imagery",
            attr="OneAtlas © Airbus",
            overlay=True,
            control=True,
            fmt="image/png"
        ).add_to(m)

        folium.LayerControl().add_to(m)

        # Mostrar mapa
        st_data = st_folium(m, width=1200, height=700)

        # Aplicar CSS dinámico al iframe para brillo/contraste
        css = f"""
        <style>
        iframe[title="folium"] {{
            filter: brightness({brillo}) contrast({contraste});
            border-radius: 10px;
        }}
        </style>
        """
        components.html(css, height=0)

    else:
        st.warning("⚠️ Ingresa tu API Key para visualizar la imagen.")
