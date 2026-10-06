# ⛽ Radar OSINT: Mercado de Combustibles (Argentina)

Un monitor predictivo automatizado construido con Python y Streamlit. Diseñado para resolver la asimetría de información en el mercado de combustibles argentino, anticipando aumentos de precios en surtidor mediante el análisis en tiempo real de variables macroeconómicas y geopolíticas (OSINT).

## 🎯 El Problema
En Argentina, los consumidores descubren los aumentos de combustible recién al llegar a la estación de servicio. Al no haber anuncios públicos anticipados por parte de las petroleras, el ciudadano pierde la capacidad de adelantarse y proteger su poder adquisitivo. 

## 🚀 La Solución (Arquitectura del Dashboard)
Este proyecto evolucionó de un sistema de registro manual de precios a un **Radar Analítico 100% automatizado**. En lugar de rastrear el precio final, el modelo se anticipa analizando la presión en la cadena de costos de las refinerías. 

La aplicación web (`dashboard.py`) consta de tres módulos clave:

1. **Motor de Datos en Vivo (API Integration):** Se conecta a los mercados globales vía `yfinance` para trackear la cotización spot del Crudo Brent y el tipo de cambio oficial (USD/ARS).
2. **Semáforo Predictivo (Inferencia):** Un algoritmo calcula la volatilidad de los últimos 7 días. Si detecta anomalías estadísticas en los costos (ej. un salto brusco del crudo por un conflicto geopolítico) o se entra en la ventana de actualización impositiva, emite una alerta roja sugiriendo cargar combustible.
3. **Backtesting Dinámico:** Un escáner histórico que analiza los últimos 5 años de la cotización del petróleo buscando "shocks" (saltos >15% en 7 días) para demostrar empíricamente el tiempo de traslado (lag) hacia el precio local.

## 📊 Los 3 Vectores de Análisis
El modelo dispara alertas sin intervención humana evaluando:
* **Vector Internacional (Brent):** El crudo es el insumo primario. Aumentos por recortes de la OPEP o guerras impactan directo en la rentabilidad de las refinerías locales.
* **Vector Cambiario (Dólar):** Al ser un mercado dolarizado, la devaluación del tipo de cambio oficial encarece las importaciones de componentes clave.
* **Vector Fiscal (ICL):** Monitoreo de la ventana temporal de actualización programada del Impuesto a los Combustibles Líquidos (generalmente a fin de mes).

## 🛠️️ Tecnologías Utilizadas
* **Lenguaje:** Python 3
* **Frontend / UI:** Streamlit (Inyección CSS personalizada para UI oscura)
* **Procesamiento de Datos:** Pandas, NumPy
* **Extracción de Datos (OSINT):** yfinance (Yahoo Finance API)

## ⚙️ Cómo ejecutar el proyecto localmente

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/MiqueasBruzzone/alerta-surtidor-osint.git](https://github.com/MiqueasBruzzone/alerta-surtidor-osint.git)