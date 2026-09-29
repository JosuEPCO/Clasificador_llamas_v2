"""Componentes visuales de la aplicación (HTML renderizado con st.markdown)."""

import base64
from html import escape
from io import BytesIO

import streamlit as st

from etapas import ETAPAS

UMBRAL_ALTA = 80
UMBRAL_MODERADA = 50


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def cargar_estilos(ruta):
    st.markdown(f"<style>{ruta.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def mostrar(bloque, destino=st):
    """Renderiza HTML sin sangrías ni líneas vacías, para que Markdown no lo altere."""
    lineas = [linea.strip() for linea in bloque.splitlines() if linea.strip()]
    destino.markdown("\n".join(lineas), unsafe_allow_html=True)


def imagen_base64(imagen, lado_max=1400):
    vista = imagen.copy()
    vista.thumbnail((lado_max, lado_max))
    buffer = BytesIO()
    vista.save(buffer, format="JPEG", quality=88)
    return base64.b64encode(buffer.getvalue()).decode()


def porcentaje(valor):
    return f"{valor:.0f}%" if valor >= 99.95 else f"{valor:.1f}%"


def nivel_confianza(valor):
    if valor >= UMBRAL_ALTA:
        return ("alta", "Alta", ICONOS["ok"],
                "La predicción es consistente. Confirma en campo si el animal está cerca del límite entre dos etapas.")
    if valor >= UMBRAL_MODERADA:
        return ("moderada", "Moderada", ICONOS["alerta"],
                "Revisa la distribución de probabilidades: la etapa contigua también podría ser plausible.")
    return ("baja", "Baja", ICONOS["error"],
            "Toma otra fotografía más nítida y frontal de los incisivos antes de concluir.")


# ---------------------------------------------------------------------------
# Iconos y esquema dental
# ---------------------------------------------------------------------------

def _icono(trazos, tam=18):
    return (f'<svg class="icono" width="{tam}" height="{tam}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'aria-hidden="true">{trazos}</svg>')


ICONOS = {
    "ok": _icono('<circle cx="12" cy="12" r="9"/><path d="m8.5 12.5 2.5 2.5 4.5-5"/>'),
    "alerta": _icono('<path d="M12 4 2.8 19.5a1 1 0 0 0 .9 1.5h16.6a1 1 0 0 0 .9-1.5L12 4Z"/>'
                     '<path d="M12 10v4"/><path d="M12 17.5h.01"/>'),
    "error": _icono('<circle cx="12" cy="12" r="9"/><path d="M12 8v5"/><path d="M12 16.5h.01"/>'),
    "check": _icono('<path d="m5 12.5 4.5 4.5L19 7.5"/>', tam=16),
    "imagen": _icono('<rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="10" r="2"/>'
                     '<path d="m21 16-5-5-9 9"/>', tam=20),
    "diente": _icono('<path d="M7 3c-2.2 0-4 1.8-4 4.2 0 2.3 1 3.6 1.6 5.6.6 2 .8 4.4 1.4 6.4.4 1.3 1 1.8 '
                     '1.7 1.8 1.1 0 1.4-1.4 1.8-3.2.3-1.5.8-2.8 2.5-2.8s2.2 1.3 2.5 2.8c.4 1.8.7 3.2 1.8 '
                     '3.2.7 0 1.3-.5 1.7-1.8.6-2 .8-4.4 1.4-6.4.6-2 1.6-3.3 1.6-5.6C21 4.8 19.2 3 17 3c-1.8 '
                     '0-2.9 1-5 1S8.8 3 7 3Z"/>', tam=20),
}


def svg_incisivos(etapa):
    """Esquema frontal de los seis incisivos inferiores para una etapa."""
    pares_permanentes = etapa.permanentes // 2
    dientes = []
    for x, par in zip((15, 33, 51, 69, 87, 105), (3, 2, 1, 1, 2, 3)):
        base = 47 - 4 * (1 - ((x - 60) / 58) ** 2)
        if par <= pares_permanentes:
            ancho, alto, radio, clase = 14, 30, 5, "d-perm"
        elif etapa.desgaste:
            ancho, alto, radio, clase = 11, 12, 2, "d-leche"
        else:
            ancho, alto, radio, clase = 11, 18, 4.5, "d-leche"
        dientes.append(f'<rect class="{clase}" x="{x - ancho / 2:.1f}" y="{base - alto:.1f}" '
                       f'width="{ancho}" height="{alto + 10}" rx="{radio}"/>')

    leche = 6 - etapa.permanentes
    descripcion = f"{etapa.permanentes} incisivos permanentes y {leche} de leche"
    if etapa.desgaste:
        descripcion += " con desgaste"
    return (f'<svg class="incisivos" viewBox="0 0 120 64" role="img" '
            f'aria-label="Esquema de incisivos inferiores: {descripcion}">'
            + "".join(dientes)
            + '<path class="encia" d="M2 48 Q60 38 118 48 L118 58 Q60 66 2 58 Z"/></svg>')


LEYENDA_DIENTES = """
<div class="leyenda">
    <span><i class="sw-perm"></i>Permanente</span>
    <span><i class="sw-leche"></i>De leche</span>
</div>
"""


# ---------------------------------------------------------------------------
# Estructura general
# ---------------------------------------------------------------------------

def barra_lateral():
    return f"""
    <div class="sb">
        <div class="sb-brand">
            <div class="sb-mark">{ICONOS["diente"]}</div>
            <div><div class="sb-name">Dentición en Llamas</div><div class="sb-version">Versión 2.0</div></div>
        </div>
        <div class="sb-section">Acerca de</div>
        <p>Herramienta de visión computacional que automatiza la evaluación de la cronología
        dentaria en llamas, optimizando el diagnóstico de edad en campo.</p>
        <div class="sb-section">Procedimiento</div>
        <ol class="sb-steps">
            <li><span>Fotografía los incisivos inferiores de frente, con buena luz.</span></li>
            <li><span>Carga la imagen en el panel principal.</span></li>
            <li><span>Presiona <b>Analizar dentición</b> y revisa el resultado.</span></li>
        </ol>
        <div class="sb-section">Equipo de investigación</div>
        <dl class="sb-team">
            <dt>Investigadores</dt><dd>Josue Pari · Zaid Alonso</dd>
            <dt>Contacto</dt><dd><a href="mailto:jjosuepco@gmail.com">jjosuepco@gmail.com</a></dd>
        </dl>
        <div class="sb-foot">Desarrollado para la investigación en Producción Animal — Universidad Nacional del Altiplano, Puno.</div>
    </div>
    """


def encabezado():
    return """
    <header class="app-header">
        <div>
            <div class="overline">UNA-Puno · Producción Animal</div>
            <div class="app-title" role="heading" aria-level="1">Clasificador de dentición en llamas</div>
            <p class="app-desc">Estima la etapa dentaria y la edad aproximada de una llama a partir de una
            fotografía de sus incisivos inferiores.</p>
        </div>
        <div class="meta">
            <span class="tag">Modelo <b>YOLOv8-cls</b></span>
            <span class="tag">Etapas <b>5</b></span>
        </div>
    </header>
    """


def cabecera_panel(titulo, paso, subtitulo):
    return f"""
    <div class="panel-head">
        <div class="panel-title" role="heading" aria-level="2">{titulo}</div>
        <div class="panel-step">{paso}</div>
    </div>
    <div class="panel-sub">{subtitulo}</div>
    """


def pie():
    return """
    <footer class="app-foot">
        <span>Producción Animal · Universidad Nacional del Altiplano, Puno</span>
        <span>Las edades son aproximadas y deben complementarse con la evaluación en campo.</span>
    </footer>
    """


# ---------------------------------------------------------------------------
# Panel de imagen
# ---------------------------------------------------------------------------

def vista_previa(b64, nombre, tamano):
    ancho, alto = tamano
    return f"""
    <figure class="preview">
        <img src="data:image/jpeg;base64,{b64}" alt="Fotografía cargada: {escape(nombre)}">
        <figcaption class="preview-meta">
            <span class="file">{escape(nombre)}</span>
            <span>{ancho} × {alto} px</span>
        </figcaption>
    </figure>
    """


def aviso(tipo, titulo, texto, icono):
    return f"""
    <div class="callout is-{tipo}" role="{'alert' if tipo == 'baja' else 'status'}">
        {icono}<div><b>{titulo}.</b> {texto}</div>
    </div>
    """


def aviso_imagen_invalida():
    return aviso("baja", "No se pudo leer la imagen",
                 "El archivo está dañado o no es una imagen válida. Prueba con otro JPG o PNG.", ICONOS["error"])


def error_modelo(ruta):
    return f"""
    <div class="panel">
        {aviso("baja", "No se pudo cargar el modelo",
               f"Verifica que el archivo <code>{ruta}</code> exista junto a <code>app.py</code> y recarga la página.",
               ICONOS["error"])}
    </div>
    """


# ---------------------------------------------------------------------------
# Panel de resultado
# ---------------------------------------------------------------------------

def panel_vacio(con_imagen):
    if con_imagen:
        titulo = "Imagen lista para analizar"
        texto = "Presiona <b>Analizar dentición</b> para obtener la etapa y la edad estimada."
    else:
        titulo = "Aún no hay resultados"
        texto = "Carga una fotografía de los incisivos para iniciar el análisis."
    consejos = (
        ("Encuadre", "incisivos inferiores de frente, con los labios retraídos."),
        ("Iluminación", "luz natural difusa, sin sombras fuertes sobre los dientes."),
        ("Enfoque", "imagen nítida, sin movimiento."),
        ("Distancia", "la boca debe ocupar la mayor parte de la foto."),
    )
    items = "".join(f'<li>{ICONOS["check"]}<span><b>{t}:</b> {d}</span></li>' for t, d in consejos)
    return f"""
    <section class="panel" aria-live="polite">
        {cabecera_panel("Resultado", "Paso 2 de 2", "Etapa dentaria, edad estimada y confianza del modelo.")}
        <div class="empty" role="status">
            <div class="empty-icon">{ICONOS["imagen"]}</div>
            <div class="empty-title">{titulo}</div>
            <p class="empty-text">{texto}</p>
        </div>
        <div class="tips">
            <div class="section-label">Recomendaciones para la fotografía</div>
            <ul class="tips-list">{items}</ul>
        </div>
    </section>
    """


def panel_cargando():
    return f"""
    <section class="panel" aria-busy="true">
        {cabecera_panel("Resultado", "Paso 2 de 2", "Analizando la imagen…")}
        <div class="skeleton-group" aria-hidden="true">
            <div class="skeleton" style="width:30%;height:12px"></div>
            <div class="skeleton" style="width:60%;height:32px;margin-top:10px"></div>
            <div class="skeleton" style="width:100%;height:72px;margin-top:20px"></div>
            <div class="skeleton" style="width:100%;height:8px;margin-top:24px"></div>
            <div class="skeleton" style="width:100%;height:120px;margin-top:24px"></div>
        </div>
    </section>
    """


def _medidor(confianza, tipo, etiqueta, icono):
    return f"""
    <div class="meter-block">
        <div class="meter-head">
            <span>Confianza del modelo</span>
            <span class="meter-status is-{tipo}">{icono}<b>{etiqueta}</b></span>
        </div>
        <div class="meter is-{tipo}" role="meter" aria-label="Confianza del modelo"
             aria-valuemin="0" aria-valuemax="100" aria-valuenow="{confianza:.1f}"
             aria-valuetext="{porcentaje(confianza)}, confianza {etiqueta.lower()}">
            <div class="meter-fill" style="width:{confianza:.1f}%"></div>
            <span class="meter-tick" style="left:{UMBRAL_MODERADA}%"></span>
            <span class="meter-tick" style="left:{UMBRAL_ALTA}%"></span>
        </div>
        <div class="meter-scale" aria-hidden="true">
            <span style="left:0">0%</span>
            <span style="left:{UMBRAL_MODERADA}%">{UMBRAL_MODERADA}%</span>
            <span style="left:{UMBRAL_ALTA}%">{UMBRAL_ALTA}%</span>
            <span style="left:100%">100%</span>
        </div>
    </div>
    """


def _distribucion(probabilidades, clave_top):
    claves = [e.clave for e in ETAPAS if e.clave in probabilidades]
    claves += [c for c in probabilidades if c not in claves]
    nombres = {e.clave: e.nombre for e in ETAPAS}
    filas = ""
    for clave in claves:
        valor = probabilidades[clave] * 100
        nombre = escape(nombres.get(clave, clave))
        es_top = clave == clave_top
        marca = '<span class="tag-pred">Predicción</span>' if es_top else ""
        filas += f"""
        <li class="dist-row{' is-top' if es_top else ''}" title="{nombre}: {valor:.1f}%">
            <span class="dist-name">{nombre}{marca}</span>
            <span class="dist-bar" aria-hidden="true"><span class="dist-fill" style="width:{valor:.1f}%"></span></span>
            <span class="dist-val">{valor:.1f}%</span>
        </li>
        """
    return f"""
    <div class="dist">
        <div class="section-label">Distribución de probabilidades</div>
        <div class="section-help">Probabilidad asignada por el modelo a cada etapa, en orden cronológico.</div>
        <ul class="dist-list">{filas}</ul>
        <div class="dist-axis" aria-hidden="true">
            <span></span>
            <span class="dist-scale"><span style="left:0">0%</span><span style="left:50%">50%</span><span style="left:100%">100%</span></span>
            <span></span>
        </div>
    </div>
    """


def panel_resultado(etapa, resultado):
    confianza = resultado["confianza"]
    tipo, etiqueta, icono, consejo = nivel_confianza(confianza)
    posicion = next((i for i, e in enumerate(ETAPAS, 1) if e.clave == etapa.clave), None)
    etapa_texto = f"Etapa {posicion} de {len(ETAPAS)}" if posicion else "Etapa no reconocida"
    subtitulo = " · ".join(filter(None, (etapa.categoria, etapa.detalle)))
    ancho, alto = resultado["tamano"]

    return f"""
    <section class="panel result" aria-live="polite">
        <div class="result-overline"><span>Etapa dentaria</span><span>{etapa_texto}</span></div>
        <div class="result-stage" role="heading" aria-level="2">{escape(etapa.nombre)}</div>
        <div class="result-sub">{subtitulo}</div>
        <dl class="kpis">
            <div class="kpi"><dt>Edad estimada</dt><dd>{etapa.edad_corta}</dd></div>
            <div class="kpi"><dt>Incisivos permanentes</dt><dd>{etapa.permanentes}<small>de 6</small></dd></div>
            <div class="kpi"><dt>Confianza</dt><dd>{porcentaje(confianza)}</dd></div>
        </dl>
        {_medidor(confianza, tipo, etiqueta, icono)}
        {aviso(tipo, f"Confianza {etiqueta.lower()}", consejo, icono)}
        <div class="diagram">
            <div class="diagram-figure">{svg_incisivos(etapa)}</div>
            <div>
                <div class="diagram-title">Edad estimada: {etapa.edad}</div>
                <div class="diagram-text">Esquema frontal de los incisivos inferiores correspondiente a esta etapa.</div>
                {LEYENDA_DIENTES}
            </div>
        </div>
        {_distribucion(resultado["probabilidades"], etapa.clave)}
        <div class="result-meta">
            <span>Tiempo de inferencia: {resultado["ms"]:.0f} ms</span>
            <span>Imagen: {ancho} × {alto} px</span>
        </div>
    </section>
    """


# ---------------------------------------------------------------------------
# Cronología de referencia
# ---------------------------------------------------------------------------

def cronologia(clave_activa=None):
    indice_activo = next((i for i, e in enumerate(ETAPAS) if e.clave == clave_activa), None)
    pasos = ""
    for i, etapa in enumerate(ETAPAS):
        estado = ""
        marcador = str(i + 1)
        bandera = ""
        if indice_activo is not None:
            if i < indice_activo:
                estado = " is-done"
            elif i == indice_activo:
                estado = " is-current"
                bandera = '<span class="step-flag">Resultado del análisis</span>'
        categoria = f" · {etapa.categoria}" if etapa.categoria else ""
        pasos += f"""
        <li class="step{estado}"{' aria-current="step"' if i == indice_activo else ''}>
            <div class="step-track"><span class="step-marker">{marcador}</span><span class="step-line"></span></div>
            <div class="step-figure">{svg_incisivos(etapa)}</div>
            <div class="step-name">{etapa.nombre}{categoria}</div>
            <div class="step-age">{etapa.edad}</div>
            <div class="step-detail">{etapa.detalle}</div>
            {bandera}
        </li>
        """
    return f"""
    <section class="panel chrono">
        <div class="chrono-head">
            <div>
                <div class="panel-title" role="heading" aria-level="2">Cronología dentaria de referencia</div>
                <div class="panel-sub">Erupción de los incisivos inferiores permanentes en llamas.</div>
            </div>
            {LEYENDA_DIENTES}
        </div>
        <ol class="steps">{pasos}</ol>
    </section>
    """
