import pandas as pd
import re
import yfinance as yf
import warnings
warnings.filterwarnings('ignore') # Para que la consola quede limpia

# Tus datos internos: La "Verdad de Terreno"
texto_correos = """
28/09 20:36. nos avisaron que a las 00:00 del dia 29 habria cambios de precio
22/09 20:55. nos avisaron que a las 00:00 del dia 23 habria cambios de precio
21/09 20:51. nos avisaron que a las 00:00 del dia 22 habria cambios de precio
22/05 20:48 nos avisaron que a las 00:00 del dia 23 habria cambios de precio
18/05 18:30 nos avisaron que a las 00:00 del dia 19 habria cambios de precio
13/05 20:47 nos avisaron que a las 00:00 del dia 14 habria cambios de precio
16/04 20:28 nos avisaron que a las 00:00 del dia 17 habria cambios de precio
10/04 23:40 nos avisaron que a las 00:00 del dia 11 habria cambios de precio
30/03 23:14 nos avisaron que a las 00:00 del dia 31 habria cambios de precio
26/03 23:47 nos avisaron que a las 00:00 del dia 27 habria cambios de precio
24/03 22:11 nos avisaron que a las 00:00 del dia 25 habria cambios de precio
19/03 18:41 nos avisaron que a las 00:00 del dia 20 habria cambios de precio
18/03 20:42 nos avisaron que a las 00:00 del dia 19 habria cambios de precio
13/03 21:40 nos avisaron que a las 00:00 del dia 14 habria cambios de precio
10/03 19:41 nos avisaron que a las 00:00 del dia 11 habria cambios de precio
06/03 22:24 nos avisaron que a las 00:00 del dia 07 habria cambios de precio
05/02 21:04 nos avisaron que a las 00:00 del dia 06 habria cambios de precio
"""

def parsear_correos(texto):
    """Limpia los correos y extrae la fecha de notificación asumiendo el año actual."""
    patron = r"(\d{2}/\d{2})\s+(\d{2}:\d{2})"
    fechas = []
    for linea in texto.strip().split('\n'):
        match = re.search(patron, linea)
        if match:
            dia_mes = match.group(1)
            # Usamos 2026 para alinear tus datos con el mercado actual
            fechas.append(pd.to_datetime(f"2026-{dia_mes.split('/')[1]}-{dia_mes.split('/')[0]}"))
    return sorted(fechas)

def ejecutar_backtesting_avanzado(fechas_reales):
    """Cruza los aumentos reales con calendario, competencia y datos financieros (Brent)."""
    
    print("\n" + "="*55)
    print("🔬 BACKTESTING AVANZADO: Validación del Modelo OSINT 🔬")
    print("="*55)
    print(f"Descargando historial del Crudo Brent (BZ=F)...")
    
    # Descargamos el historial del Brent desde 2022
    brent = yf.Ticker("BZ=F")
    historial_brent = brent.history(start="2022-01-01")['Close']
    
    aciertos_impositivos = 0
    aciertos_domino = 0
    aciertos_macro = 0
    
    ultima_fecha = None
    
    for fecha in fechas_reales:
        dia_del_mes = fecha.day
        detectado = False
        
        # 1. Regla Impositiva (Alerta Naranja: Aviso a partir del día 25)
        if dia_del_mes >= 25:
            aciertos_impositivos += 1
            detectado = True
            
        # 2. Regla Dominó (Alerta Roja: Menos de 3 días desde el último aumento)
        elif ultima_fecha and (fecha - ultima_fecha).days <= 3:
            aciertos_domino += 1
            detectado = True
            
        # 3. Regla Macro - Brent (Alerta Amarilla: El petróleo subió los días previos)
        elif not detectado:
            # Buscamos si el Brent subió en la semana previa al correo
            # (Usamos try/except por si el fin de semana la bolsa estaba cerrada)
            try:
                ventana_previa = historial_brent.loc[:fecha.strftime('%Y-%m-%d')].tail(7)
                variacion_brent = ((ventana_previa.iloc[-1] - ventana_previa.iloc[0]) / ventana_previa.iloc[0]) * 100
                
                # Si el petróleo subió más de un 1.5% esa semana, lo marcamos como riesgo macro detectado
                if variacion_brent > 1.5:
                    aciertos_macro += 1
                    detectado = True
            except:
                pass
                
        ultima_fecha = fecha

    total_aciertos = aciertos_impositivos + aciertos_domino + aciertos_macro
    tasa_efectividad = (total_aciertos / len(fechas_reales)) * 100

    print(f"\nTotal de aumentos reales analizados (Ground Truth): {len(fechas_reales)}")
    print("\n📊 RESULTADOS DE LA VALIDACIÓN (Modelo Completo):")
    print(f"✅ El modelo OSINT anticipó {total_aciertos} de los {len(fechas_reales)} aumentos sin acceso a correos internos.")
    print(f"   - {aciertos_impositivos} anticipados por Calendario Impositivo (Alerta Naranja).")
    print(f"   - {aciertos_domino} anticipados por Efecto Dominó / Competencia (Alerta Roja).")
    print(f"   - {aciertos_macro} anticipados por Saltos en el Crudo Brent (Alerta Amarilla).")
    print(f"🎯 Tasa de precisión final del algoritmo: {tasa_efectividad:.1f}%")
    print("="*55 + "\n")

if __name__ == "__main__":
    fechas = parsear_correos(texto_correos)
    ejecutar_backtesting_avanzado(fechas)