import streamlit as st
import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
TZ = ZoneInfo("America/Argentina/Buenos_Aires")  # el servidor puede estar en UTC

st.set_page_config(page_title="Alerta Surtidor", page_icon="⛽", layout="wide")

NIVELES = {
    0: ("VERDE", "#2e7d32", "Riesgo bajo",
        "Sin señales activas. Cargá solo lo necesario."),
    1: ("AMARILLO", "#f9a825", "Riesgo moderado",
        "Hay una señal activa. Si pasás por una estación, podés cargar."),
    2: ("NARANJA", "#ef6c00", "Riesgo alto",
        "Dos señales activas. Conviene adelantar la carga."),
    3: ("ROJO", "#c62828", "Riesgo crítico",
        "Las tres señales activas: es el escenario en el que más conviene adelantar la carga."),
}


# ---------------------------------------------------------------------------
# Datos y lógica
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def cargar_brent():
    """Cierres diarios del Brent (BZ=F), últimos 3 meses. Cache de 1 hora."""
    cierres = yf.Ticker("BZ=F").history(period="3mo")["Close"].dropna()
    cierres.index = cierres.index.tz_localize(None)
    return cierres


def variacion_brent(cierres, ruedas=7):
    """Variación % entre la rueda -N y la última (misma ventana que el backtesting)."""
    if cierres is None or len(cierres) < ruedas:
        return None
    return (cierres.iloc[-1] / cierres.iloc[-ruedas] - 1) * 100


def evaluar(hoy, variacion, umbral_brent, dia_ventana, aumento_reciente):
    """Devuelve las tres señales y cuántas están activas."""
    senales = [
        {
            "nombre": "Presión del Brent",
            "activa": variacion is not None and variacion > umbral_brent,
        },
        {
            "nombre": "Ventana de fin de mes",
            "activa": hoy.day >= dia_ventana,
        },
        {
            "nombre": "Aumento reciente (72 h)",
            "activa": aumento_reciente,
        },
    ]
    return senales, sum(s["activa"] for s in senales)


# ---------------------------------------------------------------------------
# Barra lateral: parámetros
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Parámetros")
    umbral_brent = st.slider(
        "Umbral de suba del Brent (%)", 0.5, 5.0, 1.5, 0.1,
        help="Variación mínima en las últimas 7 ruedas para activar la señal.",
    )
    dia_ventana = st.number_input(
        "La ventana de fin de mes empieza el día", 20, 31, 25,
    )
    aumento_reciente = st.toggle(
        "¿Hubo un aumento en las últimas 72 h?",
        help="Un aviso, una noticia o un cambio visto en el surtidor.",
    )
    st.caption("Los parámetros por defecto son los del backtesting.")

# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------
hoy = datetime.now(TZ)

try:
    cierres = cargar_brent()
    error_datos = None
except Exception as e:  # noqa: BLE001
    cierres = None
    error_datos = str(e)

variacion = variacion_brent(cierres)
senales, nivel = evaluar(hoy, variacion, umbral_brent, dia_ventana, aumento_reciente)
nombre, color, titulo, mensaje = NIVELES[nivel]

# ---------------------------------------------------------------------------
# Interfaz
# ---------------------------------------------------------------------------
st.title("⛽ Alerta Surtidor")
st.caption(
    "Sistema de alerta temprana de aumentos de combustibles en Argentina, "
    "basado en señales públicas: petróleo Brent y calendario."
)

st.markdown(
    f"""
    <div style="background:{color};padding:1.2rem 1.5rem;border-radius:12px;color:white;">
        <div style="font-size:0.85rem;opacity:0.9;letter-spacing:0.08em;">
            NIVEL ACTUAL · {nombre}
        </div>
        <div style="font-size:1.8rem;font-weight:700;">{titulo}</div>
        <div style="font-size:1rem;margin-top:0.3rem;">{mensaje}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if error_datos:
    st.warning(
        "No se pudo obtener el Brent desde Yahoo Finance. "
        "El nivel se calculó solo con las otras dos señales."
    )

st.write("")
col1, col2, col3 = st.columns(3)

with col1:
    if variacion is None:
        st.metric("Brent · últimas 7 ruedas", "Sin datos")
    else:
        st.metric("Brent · últimas 7 ruedas", f"{variacion:+.2f}%")
    st.caption(f"{'🔴 Activa' if senales[0]['activa'] else '⚪ Inactiva'} · umbral {umbral_brent:.1f}%")

with col2:
    st.metric("Día del mes", hoy.day)
    st.caption(f"{'🔴 Activa' if senales[1]['activa'] else '⚪ Inactiva'} · desde el día {dia_ventana}")

with col3:
    st.metric("Aumento en 72 h", "Sí" if aumento_reciente else "No")
    st.caption("🔴 Activa" if senales[2]["activa"] else "⚪ Inactiva")

st.divider()

st.subheader("Crudo Brent (BZ=F) · últimas 30 ruedas")
if cierres is not None and len(cierres) > 0:
    st.line_chart(cierres.tail(30), height=320)
    st.caption("Fuente: Yahoo Finance. Precios de cierre en USD por barril.")
else:
    st.info("Gráfico no disponible por el momento.")

with st.expander("Metodología y limitaciones"):
    st.markdown(
        """
        **Cómo se calcula el nivel:** se evalúan tres señales (Brent, fin de mes y
        aumento reciente). El nivel es la cantidad de señales activas: 0 verde,
        1 amarillo, 2 naranja, 3 rojo.

        **Limitaciones:**
        - Las reglas salen de un backtesting exploratorio con pocos eventos (17 avisos),
          sin validación fuera de muestra ni comparación contra un baseline aleatorio.
        - Es una herramienta de análisis, no una predicción garantizada.
        - Los cambios de precio también dependen de decisiones de las petroleras,
          del tipo de cambio e impuestos, que este modelo no observa.
        """
    )

st.caption(f"Última actualización: {hoy.strftime('%d/%m/%Y %H:%M')} (hora de Argentina)")