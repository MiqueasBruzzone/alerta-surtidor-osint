# ⛽ Radar OSINT: Mercado de Combustibles (Argentina)

Monitor automatizado de señales de costos, construido con Python y Streamlit. Sigue variables del mercado global (Brent y dólar) y el calendario fiscal para mostrar cuándo hay presión sobre los costos de los combustibles en Argentina.

> Es un indicador informativo basado en reglas simples. No predice aumentos ni constituye asesoramiento.

## 🎯 El problema

En Argentina, los aumentos de combustible suelen conocerse recién al llegar a la estación de servicio. Este proyecto busca dar una referencia previa mirando la presión sobre los costos, en lugar del precio final.

## 🚀 Qué hace la app

La aplicación (`dashboard.py`) tiene tres pestañas:

1. **Radar en vivo:** muestra el Brent (futuro del contrato más cercano) y el dólar en pesos (ARS=X), con su variación en los últimos 7 días corridos y los umbrales de cada señal. Los datos vienen de Yahoo Finance vía `yfinance`.
2. **Semáforo de señales:** combina tres señales y muestra un color.
3. **Shocks históricos del Brent:** registra los saltos de más de 15% en 7 ruedas de mercado de los últimos 5 años. Todavía no se comparan con los aumentos reales en surtidor.

## 🚦 Las tres señales

| Señal | Se activa cuando |
|---|---|
| Brent | sube más de 5% en 7 días |
| Dólar | sube más de 4% en 7 días |
| Calendario fiscal (ICL) | estamos desde el día 25 del mes |

- 🔴 **Rojo:** 2 o más señales activas.
- 🟡 **Amarillo:** 1 señal activa, o una suba de más de 2% en Brent o dólar.
- 🟢 **Verde:** sin señales.

Los umbrales se pueden cambiar en las primeras líneas de `dashboard.py`.

## ⚠️ Limitaciones

- Los umbrales fueron definidos por el autor y no están calibrados con aumentos reales en surtidor.
- No mide decisiones políticas, acuerdos de precios ni postergaciones del ICL.
- Las petroleras pueden absorber subas del crudo durante semanas antes de trasladarlas.
- El Brent proviene de contratos de futuros, que pueden mostrar saltos al cambiar de contrato.
- Los datos de Yahoo Finance pueden tener demora o diferir de las cotizaciones oficiales.

## 🛠️ Tecnologías

- Python 3
- Streamlit (con CSS personalizado para el tema oscuro)
- Pandas
- yfinance (datos de Yahoo Finance)

## ⚙️ Cómo ejecutarlo localmente

1. Clonar el repositorio:
```
   git clone https://github.com/MiqueasBruzzone/alerta-surtidor-osint.git
   cd alerta-surtidor-osint
```
2. Instalar las librerías:
```
   pip install streamlit yfinance pandas
```
3. Correr la app:
```
   streamlit run dashboard.py
```

## 🔜 Próximo paso

Validar las señales contra los aumentos reales de precios en surtidor.
