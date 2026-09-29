from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps, UnidentifiedImageError
from ultralytics import YOLO

import etapas
import ui

RAIZ = Path(__file__).parent
RUTA_MODELO = RAIZ / "modelo" / "best.pt"

st.set_page_config(
    page_title="Clasificador de Dentición en Llamas",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)
ui.cargar_estilos(RAIZ / "estilos.css")

with st.sidebar:
    ui.mostrar(ui.barra_lateral())

ui.mostrar(ui.encabezado())


# ---------------------------------------------------------------------------
# Modelo
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Cargando modelo…")
def cargar_modelo():
    return YOLO(str(RUTA_MODELO))


try:
    modelo = cargar_modelo()
except Exception:
    ui.mostrar(ui.error_modelo("modelo/best.pt"))
    st.stop()


def clasificar(imagen):
    r = modelo(imagen, verbose=False)[0]
    return {
        "clave": r.names[r.probs.top1],
        "confianza": r.probs.top1conf.item() * 100,
        "probabilidades": {r.names[i]: p for i, p in enumerate(r.probs.data.tolist())},
        "ms": sum(r.speed.values()),
        "tamano": imagen.size,
    }


# ---------------------------------------------------------------------------
# Contenido principal
# ---------------------------------------------------------------------------

st.session_state.setdefault("resultado", None)

col_imagen, col_resultado = st.columns([1, 1.2], gap="large")

with col_resultado:
    panel = st.empty()

imagen = None
with col_imagen:
    with st.container(key="panel_imagen"):
        ui.mostrar(ui.cabecera_panel("Fotografía", "Paso 1 de 2",
                                     "Incisivos inferiores de frente, en formato JPG o PNG."))
        archivo = st.file_uploader(
            "Fotografía de los incisivos inferiores",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
            key="foto",
        )

        if archivo is None:
            st.session_state.resultado = None
        else:
            id_archivo = getattr(archivo, "file_id", None) or f"{archivo.name}-{archivo.size}"
            previo = st.session_state.resultado
            if previo and previo["archivo"] != id_archivo:
                st.session_state.resultado = None

            try:
                imagen = ImageOps.exif_transpose(Image.open(archivo)).convert("RGB")
            except (UnidentifiedImageError, OSError):
                ui.mostrar(ui.aviso_imagen_invalida())
            else:
                ui.mostrar(ui.vista_previa(ui.imagen_base64(imagen), archivo.name, imagen.size))
                if st.button("Analizar dentición", type="primary", key="analizar"):
                    ui.mostrar(ui.panel_cargando(), destino=panel)
                    resultado = clasificar(imagen)
                    resultado["archivo"] = id_archivo
                    st.session_state.resultado = resultado

resultado = st.session_state.resultado
if resultado:
    ui.mostrar(ui.panel_resultado(etapas.buscar(resultado["clave"]), resultado), destino=panel)
else:
    ui.mostrar(ui.panel_vacio(con_imagen=imagen is not None), destino=panel)

ui.mostrar(ui.cronologia(resultado["clave"] if resultado else None))
ui.mostrar(ui.pie())
