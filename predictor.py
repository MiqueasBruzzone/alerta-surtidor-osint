import yfinance as yf
from datetime import datetime

def obtener_variacion_brent():
    """Se conecta a internet y calcula cuánto varió el petróleo (Brent) en los últimos 5 días."""
    print("🔍 Analizando mercado internacional en segundo plano...")
    try:
        # BZ=F es el símbolo del crudo Brent en la bolsa
        brent = yf.Ticker("BZ=F")
        hist = brent.history(period="5d")
        precio_viejo = hist['Close'].iloc[0]
        precio_nuevo = hist['Close'].iloc[-1]
        variacion = ((precio_nuevo - precio_viejo) / precio_viejo) * 100
        return variacion
    except:
        return 0.0

def evaluar_riesgo_combustible(ypf_aumento_hoy):
    """Evalúa el riesgo cruzando el calendario local con el mercado internacional."""
    
    # 1. Recolección automática de datos (OSINT)
    dia_del_mes = datetime.now().day
    brent_variacion = obtener_variacion_brent()
    
    # Umbrales
    UMBRAL_BRENT = 5.0 
    presion_macro = brent_variacion >= UMBRAL_BRENT
    ventana_impositiva = dia_del_mes >= 25
    
    print("\n" + "="*50)
    print("🚦 SEMÁFORO DE COMBUSTIBLE ARGENTINO 🚦")
    print("="*50)
    
    # 2. Árbol de decisión simple para el ciudadano
    if ypf_aumento_hoy.lower() in ['si', 's', 'sí']:
        print("🔴 ALERTA ROJA: Riesgo Crítico Inminente.")
        print("💡 Acción: LLENÁ EL TANQUE HOY. Por efecto dominó, el resto de las estaciones ajusta en 24-48hs.")
        
    elif ventana_impositiva:
        print("🟠 ALERTA NARANJA: Riesgo por Calendario Impositivo.")
        print(f"💡 Acción: Hoy es día {dia_del_mes}. Conviene cargar antes del fin de mes para evitar el ajuste de impuestos (ICL).")
        
    elif presion_macro:
        print("🟡 ALERTA AMARILLA: Presión en el mercado mayorista.")
        print(f"💡 Acción: El petróleo internacional subió un {brent_variacion:.1f}%. Cargá si pasás por una estación.")
        
    else:
        print("🟢 SEMÁFORO VERDE: Riesgo Bajo.")
        print(f"💡 Acción: Mercado estable (El crudo varió {brent_variacion:.1f}%). Cargá solo lo necesario.")
    
    print("="*50 + "\n")

if __name__ == "__main__":
    print("Iniciando Alerta Surtidor...")
    
    # La ÚNICA pregunta que se le hace al usuario es algo que puede ver en la calle o en la tele
    ypf = input("¿Viste en las noticias o en la calle que YPF aumentó hoy? (si/no): ")
    evaluar_riesgo_combustible(ypf)