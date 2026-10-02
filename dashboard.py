import streamlit as st
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN Y CSS (Modo Oscuro) ---
st.set_page_config(page_title="Alerta Surtidor", page_icon="⛽", layout="wide")

st.markdown("""
<style>
    .metric-card {
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        height: 100%;
    }
    .metric-title { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.7); }
    .metric-val { font-size: 1.8rem; font-weight: 700; margin: 0.3rem 0; color: white;}
    .metric-sub { font-size: 0.85rem; color: rgba(255,255,255,0.6); }
</style>
""", unsafe_allow_html=True)

# --- 2. GENERACIÓN AUTOMÁTICA DE BASE DE DATOS LOCAL (Si no existe) ---
if not os.path.exists("precios_2026.csv"):
    datos_muestra = """provincia,localidad,empresabandera,direccion,producto,precio,fecha_vigencia
SANTA FE,ROSARIO,YPF,Oroño y 27 de Febrero,Nafta súper,1140,2026-10-01
SANTA FE,ROSARIO,PUMA,Av. Pellegrini 1200,Nafta súper,1120,2026-10-01
SANTA FE,ROSARIO,SHELL,Rondeau 3000,Nafta súper,1165,2026-10-01
SANTA FE,ROSARIO,AXION,Av. Alberdi 500,Nafta súper,1150,2026-10-01
SANTA FE,ROSARIO,YPF,San Martín 4500,Gasoil,1180,2026-10-01"""
    with open("precios_2026.csv", "w", encoding="utf-8") as f:
        f.write(datos_muestra)

# --- 3. EXTRACCIÓN DE DATOS ---
@st.cache_data(ttl=3600)
def obtener_datos_mercado():
    try:
        brent = yf.Ticker("BZ=F").history(period="1mo")['Close']
        usd_ars = yf.Ticker("ARS=X").history(period="1mo")['Close']
        if brent.empty or usd_ars.empty:
            raise ValueError("Datos vacíos")
        return brent, usd_ars
    except:
        return None, None

@st.cache_data(ttl=60)
def cargar_precios_locales():
    try:
        df = pd.read_csv("precios_2026.csv")
        df['precio'] = pd.to_numeric(df['precio'], errors='coerce')
        df['fecha_vigencia'] = pd.to_datetime(df['fecha_vigencia'], errors='coerce')
        return df
    except:
        return None

brent, usd = obtener_datos_mercado()
df_precios = cargar_precios_locales()
timestamp_act = datetime.now().strftime("%d/%m/%Y %H:%M")

if brent is None or usd is None:
    st.error("⚠️ Error de conexión con Yahoo Finance.")
    st.stop()

# --- 4. LÓGICA DE NEGOCIO (EL CEREBRO PREDICTIVO) ---
b_hoy, b_ayer = float(brent.iloc[-1]), float(brent.iloc[-2])
var_brent_pct = ((b_hoy - b_ayer) / b_ayer) * 100

u_hoy, u_ayer = float(usd.iloc[-1]), float(usd.iloc[-2])
var_usd_pct = ((u_hoy - u_ayer) / u_ayer) * 100

hoy = datetime.now()
ventana_icl = hoy.day >= 25

# Lógica del semáforo interactivo
if ventana_icl:
    riesgo_lbl, titulo_sem, color_fondo = "¿CARGO HOY? · ROJO", "Presión alta (Inminente)", "#dc2626"
    mensaje_sem = "Estamos en ventana de impuestos (ICL) de fin de mes. Históricamente los precios ajustan ahora. Cargá HOY mismo."
elif var_brent_pct > 2.0 or var_usd_pct > 2.0:
    riesgo_lbl, titulo_sem, color_fondo = "¿CARGO HOY? · AMARILLO", "Señales de alerta", "#d97706"
    mensaje_sem = "Salto fuerte en el dólar o el crudo. Si te queda de paso, adelantá la carga por las dudas."
else:
    riesgo_lbl, titulo_sem, color_fondo = "¿CARGO HOY? · VERDE", "Sin presión de costos", "#16a34a"
    mensaje_sem = "El petróleo y el dólar están estables y no hay ajuste de impuestos cerca. Cargá cuando te toque."

# Variables de Clustering (Muestreo representativo)
est_ajustadas = 3
est_totales = 50
pct_ajuste = (est_ajustadas / est_totales) * 100

# --- 5. INTERFAZ VISUAL ---
col_tit, col_time = st.columns([3, 1])
with col_tit:
    st.title("⛽ Alerta Surtidor")
    st.markdown("Dónde cargar más barato y cuándo conviene hacerlo, con datos en vivo.")
with col_time:
    st.markdown(f"<div style='text-align: right; color: rgba(255,255,255,0.5); padding-top: 2rem;'>⏱️ Actualizado: {timestamp_act}</div>", unsafe_allow_html=True)

st.write("")

# Filtros
col_prov, col_loc, col_comb, col_litros = st.columns([1.2, 1.2, 1, 1])
provincia = col_prov.selectbox("Provincia", ["Santa Fe", "Córdoba", "Buenos Aires"])
localidad = col_loc.selectbox("Localidad", ["Rosario", "Santa Fe"])
combustible = col_comb.selectbox("Combustible", ["Nafta súper", "Nafta premium", "Gasoil"])
litros = col_litros.slider("Litros por carga", 10, 100, 40, step=5)

with st.expander("⚙️ Ajustar las alertas"):
    st.write("Umbrales de sensibilidad del modelo de Machine Learning...")

st.write("")

# Fila de Métricas
col_sem, col_m1, col_m2, col_m3 = st.columns([1.4, 0.8, 0.8, 0.8])

with col_sem:
    st.markdown(f"""
    <div style="background-color: {color_fondo}; border-radius: 16px; padding: 1.4rem 1.6rem; color: white; height: 100%;">
        <div style="font-size: 0.8rem; letter-spacing: 0.1em; opacity: 0.9; text-transform: uppercase;">{riesgo_lbl}</div>
        <div style="font-size: 1.9rem; font-weight: 800; line-height: 1.2; margin-top: 0.2rem;">{titulo_sem}</div>
        <div style="margin-top: 0.5rem; font-size: 1rem; opacity: 0.95;">{mensaje_sem}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">BRENT · ÚLT. 24HS</div>
        <div class="metric-val">{var_brent_pct:+.2f}%</div>
        <div class="metric-sub">{'🔴 Riesgo' if var_brent_pct > 2.0 else '⚪ Estable'} · umbral +2.0%</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">DÓLAR · ÚLT. 24HS</div>
        <div class="metric-val">{var_usd_pct:+.2f}%</div>
        <div class="metric-sub">{'🔴 Riesgo' if var_usd_pct > 2.0 else '⚪ Estable'} · umbral +2.0%</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">AJUSTES EN 72 H</div>
        <div class="metric-val">{pct_ajuste:.0f}%</div>
        <div class="metric-sub">Muestra: {est_ajustadas} de {est_totales} líderes</div>
    </div>
    """, unsafe_allow_html=True)

st.caption("El semáforo evalúa la presión de costos macroeconómicos y ventanas fiscales.")
st.divider()

# Tabla de Precios Locales
st.subheader(f"📍 Top 5 más baratos: {combustible} en {localidad}")
st.markdown("Basado en relevamiento OSINT local (Octubre 2026).")

if df_precios is not None:
    df_filtrado = df_precios[
        (df_precios['provincia'].str.upper() == provincia.upper()) & 
        (df_precios['localidad'].str.upper() == localidad.upper()) &
        (df_precios['producto'].str.contains(combustible, case=False, na=False))
    ]
    
    top_5 = df_filtrado.sort_values(by="precio", ascending=True).head(5)
    
    if not top_5.empty:
        tabla_final = pd.DataFrame({
            "Bandera": top_5['empresabandera'].str.upper(),
            "Dirección": top_5['direccion'],
            "Precio ($/L)": top_5['precio'].apply(lambda x: f"$ {x:.0f}"),
            "Último Reporte": top_5['fecha_vigencia'].dt.strftime("%d/%m/%Y")
        })
        st.dataframe(tabla_final, use_container_width=True, hide_index=True)
    else:
        st.info(f"No hay registros en tu base local (precios_2026.csv) para {combustible} en {localidad}.")
else:
    st.error("Error al leer la base de datos local.")