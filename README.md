# ⛽ Alerta Surtidor: Predicción OSINT de Combustibles en Argentina

Un sistema de alerta temprana diseñado para resolver la asimetría de información en el mercado de combustibles argentino, anticipando aumentos de precios mediante el uso de Inteligencia de Fuentes Abiertas (OSINT) y análisis predictivo.

## 🎯 El Problema
Recientemente, los cambios regulatorios en Argentina eliminaron la obligación de las petroleras de anunciar públicamente los aumentos de combustible con anticipación. Hoy, el consumidor descubre la suba recién al llegar al surtidor. Este proyecto busca devolverle esa visibilidad al conductor mediante el cruce de variables públicas internacionales y fiscales locales.

## 🛠️ Arquitectura del Proyecto
El proyecto se divide en dos módulos clave desarrollados en Python:

1. **`predictor.py` (Motor OSINT):** Se conecta a Yahoo Finance (`yfinance`) para leer la variación del crudo Brent en tiempo real, cruza la fecha con el calendario impositivo local (ICL) y monitorea el comportamiento de la empresa líder del mercado (YPF). Con esto, emite un "Semáforo Ciudadano" (Verde, Amarillo, Naranja, Rojo) recomendando si es conveniente o no cargar combustible en el día de la fecha.
2. **`backtesting.py` (Validación):** Para comprobar la eficacia de la lógica, se elaboró un script que contrasta las reglas del algoritmo contra un dataset confidencial de notificaciones internas de cambios de precio (Ground Truth) de los últimos meses en la ciudad de Rosario.
3.  **`Nota metodológica sobre el diseño`:** El dataset de notificaciones históricas se utiliza exclusivamente como *Ground Truth* para la auditoría de backtesting, manteniendo las variables predictivas (ICL y Brent) en un esquema estrictamente causal (*lagged features*) para prevenir sesgos y evitar la fuga de datos (*data leakage*).

## 📊 Descubrimiento de Patrones y Efectividad
El backtesting reveló que el mercado local obedece a tres variables predecibles:
1. **Presión Macro (Brent):** Traslados al surtidor días después de saltos internacionales mayores al 1.5%.
2. **Presión Fiscal:** Alta concentración de ajustes en la ventana del día 25 al 31 de cada mes por traslados impositivos.
3. **Efecto Dominó:** Si YPF ajusta, la competencia reacciona en una ventana menor a 72hs.

**Resultado del Backtesting:** Cruzando estas tres reglas, el modelo predictivo logró anticipar correctamente el **70.6% de los aumentos sorpresa**, demostrando que es posible predecir los movimientos del mercado utilizando inteligencia de fuentes abiertas y sin acceso a los reportes de costos corporativos.

## 🚀 Tecnologías Utilizadas
* **Lenguaje:** Python 3
* **Librerías:** Pandas, yfinance, Regular Expressions (RegEx), datetime.
* **Técnicas:** OSINT, Feature Engineering, Integración de APIs financieras, Backtesting.
