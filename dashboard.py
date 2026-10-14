import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Radar OSINT Combustible", page_icon="⛽", layout="wide")

st.markdown("""
<style>
    .metric-card {
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1.2rem;
        height: 100%;
    }
    .metric-title { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.7); }
    .metric-val { font-size: 2rem; font-weight: 700; margin: 0.4rem 0; color: white;}
    .metric-sub { font-size: 0.9rem; color: rgba(255,255,255,0.6); }
</style>
""", unsafe_allow_html=True)

# Umbrales de las señales (se cambian acá y se actualizan solos en toda la app)
UMBRAL_BRENT = 5.0      # % de suba semanal del Brent que cuenta como señal
UMBRAL_USD = 4.0        # % de suba semanal del dólar que cuenta como señal
UMBRAL_TENSION = 2.0    # % que alcanza para pasar a amarillo
DIA_VENTANA_ICL = 25    # desde este día del mes se considera "ventana ICL"


# --- 2. MOTOR DE DATOS ---
@st.cache_data(ttl=3600)
def obtener_datos_globales():
    try:
        brent = yf.Ticker("BZ=F").history(period="6mo")['Close'].dropna()
        usd_ars = yf.Ticker("ARS=X").history(period="6mo")['Close'].dropna()
        if brent.empty or usd_ars.empty:
            raise ValueError("Datos vacíos")
        return brent, usd_ars
    except Exception:
        return None, None


def variacion_pct(serie, dias=7):
    """Devuelve (valor actual, % de variación contra hace `dias` días corridos)."""
    ultimo = float(serie.iloc[-1])
    fecha_ref = serie.index[-1] - pd.Timedelta(days=dias)
    previos = serie[serie.index <= fecha_ref]
    base = float(previos.iloc[-1]) if not previos.empty else float(serie.iloc[0])
    return ultimo, ((ultimo - base) / base) * 100


brent, usd = obtener_datos_globales()

if brent is None or usd is None:
    st.error("⚠️ Error de conexión con los mercados globales. El radar está fuera de línea.")
    st.stop()

# --- 3. LÓGICA DE SEÑALES ---
b_hoy, var_brent_semanal = variacion_pct(brent, 7)
u_hoy, var_usd_semanal = variacion_pct(usd, 7)

hoy = datetime.now()
ventana_icl = hoy.day >= DIA_VENTANA_ICL

# Cada condición que se cumple es una "señal"
senales = []
if ventana_icl:
    senales.append("estamos en la ventana de fin de mes, cuando suele actualizarse el ICL (no siempre ocurre: puede postergarse)")
if var_brent_semanal > UMBRAL_BRENT:
    senales.append(f"el Brent subió {var_brent_semanal:.2f}% en los últimos 7 días")
if var_usd_semanal > UMBRAL_USD:
    senales.append(f"el dólar subió {var_usd_semanal:.2f}% en los últimos 7 días")

razones = " y ".join(senales)
tension_moderada = var_brent_semanal > UMBRAL_TENSION or var_usd_semanal > UMBRAL_TENSION

if len(senales) >= 2:
    alerta_lbl, titulo_sem, color_fondo = "SEÑAL DE PRESIÓN · ROJO", "Varias señales de costos coinciden", "#dc2626"
    mensaje_sem = (f"Coinciden varias señales: {razones}. Aumenta la chance de un ajuste en surtidor, "
                   "pero esta herramienta no puede confirmar si ocurrirá ni cuándo.")
elif len(senales) == 1 or tension_moderada:
    alerta_lbl, titulo_sem, color_fondo = "MONITOREO · AMARILLO", "Hay presión, pero todavía moderada", "#d97706"
    if senales:
        mensaje_sem = (f"Hay una señal activa: {razones}. Una sola señal no alcanza para marcar riesgo alto; "
                       "conviene seguir la evolución en los próximos días.")
    else:
        mensaje_sem = ("Los costos se mueven algo más de lo normal, sin llegar a los umbrales de alerta. "
                       "No hay señales firmes por ahora.")
else:
    alerta_lbl, titulo_sem, color_fondo = "ESTADO · VERDE", "Mercado estable", "#16a34a"
    mensaje_sem = ("Las variables que monitorea el radar están en calma. "
                   "No se detectan presiones de costos relevantes a corto plazo.")

# --- 4. INTERFAZ VISUAL ---
st.title("⛽ Radar OSINT: Mercado de Combustibles")
st.markdown("Monitor automatizado de señales de costos. Entendé qué presiones del mercado global pueden llegar al surtidor.")
st.caption("Indicador informativo basado en reglas simples. No es una predicción ni asesoramiento.")
st.write("")

st.markdown(f"""
<div style="background-color: {color_fondo}; border-radius: 16px; padding: 1.5rem 2rem; color: white; margin-bottom: 2rem;">
    <div style="font-size: 0.9rem; letter-spacing: 0.1em; opacity: 0.9; text-transform: uppercase; font-weight: bold;">{alerta_lbl}</div>
    <div style="font-size: 2.2rem; font-weight: 800; line-height: 1.2; margin-top: 0.3rem;">{titulo_sem}</div>
    <div style="margin-top: 0.8rem; font-size: 1.1rem; opacity: 0.95;">{mensaje_sem}</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📊 Radar en Vivo (Brent y USD)",
    "📈 Shocks históricos del Brent",
    "💡 ¿Cómo funciona? Límites"
])

with tab1:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Brent (futuro, contrato más cercano)</div>
            <div class="metric-val">USD {b_hoy:.2f}</div>
            <div class="metric-sub">Variación 7 días: <strong style="color: {'#ef4444' if var_brent_semanal > 0 else '#22c55e'};">{var_brent_semanal:+.2f}%</strong> · umbral de señal: +{UMBRAL_BRENT:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.line_chart(brent, color="#ef4444")

    with col_m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Dólar en pesos (ARS por USD, Yahoo Finance)</div>
            <div class="metric-val">ARS {u_hoy:.2f}</div>
            <div class="metric-sub">Variación 7 días: <strong style="color: {'#ef4444' if var_usd_semanal > 0 else '#22c55e'};">{var_usd_semanal:+.2f}%</strong> · umbral de señal: +{UMBRAL_USD:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.line_chart(usd, color="#3b82f6")

    st.caption(f"Fuente: Yahoo Finance (yfinance). Último dato de mercado: {brent.index[-1].strftime('%d/%m/%Y')}. "
               "Los datos pueden tener demora y el valor del dólar puede diferir levemente del oficial del BNA.")

with tab2:
    st.subheader("Shocks históricos del petróleo Brent")
    st.markdown("Lista los momentos de los últimos 5 años en que el Brent subió **más de 15% en 7 ruedas de mercado**. "
                "Es un registro de saltos del crudo: esta app **todavía no los compara con los aumentos reales en surtidor**, "
                "por lo que no se puede afirmar cuánto tardan en trasladarse al precio local.")

    @st.cache_data(ttl=86400)  # Se actualiza una vez al día
    def calcular_anomalias_historicas():
        try:
            historico = yf.Ticker("BZ=F").history(period="5y")
            historico['Precio_Base'] = historico['Close'].shift(7)
            historico['Variacion_7d_pct'] = historico['Close'].pct_change(periods=7) * 100
            shocks = historico[historico['Variacion_7d_pct'] > 15.0].copy()
            shocks['Mes_Anio'] = shocks.index.to_period('M')
            shocks_unicos = shocks.drop_duplicates(subset=['Mes_Anio'], keep='first')
            return historico, shocks_unicos
        except Exception:
            return None, None

    hist_brent, shocks_df = calcular_anomalias_historicas()

    if hist_brent is not None and not shocks_df.empty:
        tabla_shocks = pd.DataFrame({
            "Fecha del Shock": shocks_df.index.strftime("%d/%m/%Y"),
            "Precio 7 ruedas antes (USD)": shocks_df['Precio_Base'].apply(lambda x: f"${x:.2f}"),
            "Precio del día (USD)": shocks_df['Close'].apply(lambda x: f"${x:.2f}"),
            "Salto": shocks_df['Variacion_7d_pct'].apply(lambda x: f"+{x:.1f}% en 7 ruedas")
        })
        tabla_shocks = tabla_shocks.iloc[::-1].reset_index(drop=True)
        st.dataframe(tabla_shocks)

        st.markdown("""
        **Cómo leer esta tabla:** muestra qué tan excepcionales son los saltos del crudo. Si hoy apareciera uno de
        esta magnitud, sería una señal fuerte de presión sobre los costos. Qué pase después en el surtidor depende
        también de decisiones de las petroleras y del Gobierno.
        """)
    elif hist_brent is None:
        st.warning("No se pudieron obtener los datos históricos en este momento.")
    else:
        st.info("No se detectaron shocks de más de 15% en el período analizado.")

with tab3:
    st.subheader("Transparencia del algoritmo")
    st.markdown(f"""
    Este tablero recolecta datos de fuentes abiertas (OSINT) y evalúa tres señales con reglas simples:

    1. **Brent:** el crudo es el insumo principal. Cuenta como señal si sube más de **{UMBRAL_BRENT:.0f}%** en 7 días.
    2. **Dólar:** el mercado de combustibles está muy atado al dólar. Cuenta como señal si sube más de **{UMBRAL_USD:.0f}%** en 7 días.
    3. **Calendario fiscal (ICL):** el Impuesto a los Combustibles Líquidos suele actualizarse cerca de fin de mes. Cuenta como señal desde el día **{DIA_VENTANA_ICL}**.

    **Cómo se combinan:** con **2 o más señales** el semáforo marca rojo; con **1 señal** (o una suba moderada de más de {UMBRAL_TENSION:.0f}%) marca amarillo; sin señales, verde.
    """)

    st.subheader("Límites")
    st.markdown("""
    - Los umbrales los definió el autor; no fueron calibrados con aumentos reales en surtidor.
    - No mide decisiones políticas, acuerdos de precios ni postergaciones del ICL.
    - Las petroleras pueden absorber subas del crudo durante semanas antes de trasladarlas.
    - El Brent se toma del contrato de futuros más cercano, que puede mostrar saltos al cambiar de contrato.
    - Los datos vienen de Yahoo Finance y pueden tener demora o diferir de las cotizaciones oficiales.
    """)
