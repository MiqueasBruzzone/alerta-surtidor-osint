import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

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

# --- 2. MOTOR DE DATOS AUTOMATIZADO ---
@st.cache_data(ttl=3600)
def obtener_datos_globales():
    try:
        # Traemos 6 meses de datos para ver la tendencia real
        brent = yf.Ticker("BZ=F").history(period="6mo")['Close']
        usd_ars = yf.Ticker("ARS=X").history(period="6mo")['Close']
        if brent.empty or usd_ars.empty:
            raise ValueError("Datos vacíos")
        return brent, usd_ars
    except:
        return None, None

brent, usd = obtener_datos_globales()

if brent is None or usd is None:
    st.error("⚠️ Error de conexión con los mercados globales. El radar está fuera de línea.")
    st.stop()

# --- 3. ALGORITMO PREDICTIVO ---
# Analizamos la volatilidad de la última semana (no solo de ayer)
b_hoy = float(brent.iloc[-1])
b_semana_atras = float(brent.iloc[-7])
var_brent_semanal = ((b_hoy - b_semana_atras) / b_semana_atras) * 100

u_hoy = float(usd.iloc[-1])
u_semana_atras = float(usd.iloc[-7])
var_usd_semanal = ((u_hoy - u_semana_atras) / u_semana_atras) * 100

hoy = datetime.now()
ventana_icl = hoy.day >= 25

# Motor de inferencia
if ventana_icl or var_brent_semanal > 5.0 or var_usd_semanal > 4.0:
    alerta_lbl, titulo_sem, color_fondo = "ALERTA TEMPRANA · ROJO", "Alta Probabilidad de Ajuste", "#dc2626"
    mensaje_sem = "Los indicadores globales muestran fuerte presión. Ya sea por vencimientos impositivos o escalada en el crudo, es inminente un traslado a precios. Conviene cargar el tanque hoy."
elif var_brent_semanal > 2.0 or var_usd_semanal > 2.0:
    alerta_lbl, titulo_sem, color_fondo = "MONITOREO · AMARILLO", "Tensión en la Cadena de Costos", "#d97706"
    mensaje_sem = "El mercado internacional está absorbiendo shocks. No hay aumento confirmado para hoy, pero la presión alcista indica que adelantarse es una buena decisión financiera."
else:
    alerta_lbl, titulo_sem, color_fondo = "ESTADO · VERDE", "Mercado Estable", "#16a34a"
    mensaje_sem = "Las variables macroeconómicas y geopolíticas están en calma. No se detectan presiones para un aumento a corto plazo."

# --- 4. INTERFAZ VISUAL ---
st.title("⛽ Radar OSINT: Mercado de Combustibles")
st.markdown("Monitor predictivo automatizado. Anticipá el impacto en el surtidor entendiendo la macroeconomía y la geopolítica global.")
st.write("")

# Tarjeta de Predicción Principal
st.markdown(f"""
<div style="background-color: {color_fondo}; border-radius: 16px; padding: 1.5rem 2rem; color: white; margin-bottom: 2rem;">
    <div style="font-size: 0.9rem; letter-spacing: 0.1em; opacity: 0.9; text-transform: uppercase; font-weight: bold;">{alerta_lbl}</div>
    <div style="font-size: 2.2rem; font-weight: 800; line-height: 1.2; margin-top: 0.3rem;">{titulo_sem}</div>
    <div style="margin-top: 0.8rem; font-size: 1.1rem; opacity: 0.95;">{mensaje_sem}</div>
</div>
""", unsafe_allow_html=True)

# --- PESTAÑAS ANALÍTICAS ---
tab1, tab2, tab3 = st.tabs([
    "📊 Radar en Vivo (Brent y USD)", 
    "📈 Backtesting de Shocks", 
    "💡 ¿Cómo funciona el algoritmo?"
])

with tab1:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Barril Crudo Brent (Spot)</div>
            <div class="metric-val">USD {b_hoy:.2f}</div>
            <div class="metric-sub">Variación 7 días: <strong style="color: {'#ef4444' if var_brent_semanal > 0 else '#22c55e'};">{var_brent_semanal:+.2f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.line_chart(brent, color="#ef4444")
        
    with col_m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Tipo de Cambio OFICIAL (ARS)</div>
            <div class="metric-val">ARS {u_hoy:.2f}</div>
            <div class="metric-sub">Variación 7 días: <strong style="color: {'#ef4444' if var_usd_semanal > 0 else '#22c55e'};">{var_usd_semanal:+.2f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.line_chart(usd, color="#3b82f6")

with tab2:
    st.subheader("Algoritmo de Detección de Shocks Históricos (Backtesting)")
    st.markdown("El modelo escanea los últimos 5 años del petróleo Brent buscando **anomalías estadísticas** (saltos de precio mayores al 15% en menos de 7 días). Históricamente, estos eventos globales tardan entre **14 y 21 días** en trasladarse al precio de surtidor en Argentina.")
    
    @st.cache_data(ttl=86400) # Se actualiza una vez al día
    def calcular_anomalias_historicas():
        try:
            historico = yf.Ticker("BZ=F").history(period="5y")
            historico['Variacion_7d_pct'] = historico['Close'].pct_change(periods=7) * 100
            shocks = historico[historico['Variacion_7d_pct'] > 15.0].copy()
            shocks['Mes_Anio'] = shocks.index.to_period('M')
            shocks_unicos = shocks.drop_duplicates(subset=['Mes_Anio'], keep='first')
            return historico, shocks_unicos
        except:
            return None, None

    hist_brent, shocks_df = calcular_anomalias_historicas()

    if hist_brent is not None and not shocks_df.empty:
        tabla_shocks = pd.DataFrame({
            "Fecha del Shock": shocks_df.index.strftime("%d/%m/%Y"),
            "Precio Base (USD)": shocks_df['Close'].shift(1, fill_value=shocks_df['Close'].iloc[0]).apply(lambda x: f"${x:.2f}"),
            "Precio Post-Shock (USD)": shocks_df['Close'].apply(lambda x: f"${x:.2f}"),
            "Violencia del Salto": shocks_df['Variacion_7d_pct'].apply(lambda x: f"+{x:.1f}% en 7 días")
        })
        tabla_shocks = tabla_shocks.iloc[::-1].reset_index(drop=True)
        st.dataframe(tabla_shocks, use_container_width=True)
        
        st.markdown("""
        **¿Cómo se usa esta estadística para predecir?**
        Si el radar detecta hoy un salto de la misma magnitud que los listados arriba, el modelo activa la alerta roja. El tiempo de reacción de las petroleras marca la **ventana de oportunidad** para llenar el tanque antes del ajuste.
        """)
    else:
        st.info("Calculando matriz histórica o sin shocks recientes detectados...")

with tab3:
    st.subheader("Transparencia del Algoritmo")
    st.markdown("""
    Este tablero recolecta inteligencia de fuentes abiertas (OSINT) sin intervención humana. El modelo dispara alertas evaluando tres vectores:
    
    1. **Vector Internacional (Brent):** El crudo es el insumo primario. Si en el mercado global sube abruptamente por un conflicto geopolítico o recorte de producción (OPEP), las refinerías argentinas pierden rentabilidad y trasladan el costo.
    2. **Vector Cambiario (Dólar):** El mercado de hidrocarburos está altamente dolarizado. Una devaluación del tipo de cambio oficial encarece la importación de combustibles terminados y componentes clave.
    3. **Vector Fiscal (ICL):** En Argentina, el Impuesto a los Combustibles Líquidos se actualiza de forma programada, generalmente impactando cerca del fin de mes o primeros días del siguiente mes.
    """)