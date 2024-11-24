# -*- coding: utf-8 -*-
"""Banxico-Fed.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1TAn6JRFdMaFUAM5VihHu-AQ4c3Q9VxTx
"""

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Configuración de las claves API
BANXICO_TOKEN = '4f55b130139d44190c5e841c2af22a5fe0ffdbc9496d89d813b84a20f6ca7353'
FED_API_KEY = 'ad32a40782702b7ecc1ec9a4b2c85bf7'

# Variables macroeconómicas
variables = {
    "Tasa de Interés (Banxico)": "SF43718",
    "Inflación (Banxico)": "SP1",
    "PIB (FED)": "GDP",
    "Tasa de Desempleo (FED)": "UNRATE",
    "Índice de Producción Industrial (FED)": "INDPRO"
}

# Función para obtener datos de Banxico
def obtener_datos_banxico(serie_id, fecha_inicio, fecha_fin):
    url = f"https://www.banxico.org.mx/SieAPIRest/service/v1/series/{serie_id}/datos/{fecha_inicio}/{fecha_fin}"
    headers = {"Bmx-Token": BANXICO_TOKEN}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        datos = response.json()["bmx"]["series"][0]["datos"]
        df = pd.DataFrame(datos)
        df["fecha"] = pd.to_datetime(df["fecha"])
        df["dato"] = pd.to_numeric(df["dato"], errors="coerce")
        return df
    else:
        st.error("Error al obtener datos de Banxico")
        return pd.DataFrame()

# Función para obtener datos de la FED
def obtener_datos_fed(serie_id, fecha_inicio, fecha_fin):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": serie_id,
        "api_key": FED_API_KEY,
        "file_type": "json",
        "observation_start": fecha_inicio,
        "observation_end": fecha_fin,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        datos = response.json()["observations"]
        df = pd.DataFrame(datos)
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        return df.rename(columns={"date": "fecha", "value": "dato"})
    else:
        st.error("Error al obtener datos de la FED")
        return pd.DataFrame()

# Configuración de la app
st.title("App de Análisis Macroeconómico")
st.sidebar.header("Opciones de Selección")

# Selección de variable y rango de fechas
variable_seleccionada = st.sidebar.selectbox("Selecciona una variable macroeconómica", list(variables.keys()))
fecha_inicio = st.sidebar.date_input("Fecha de inicio", datetime(2015, 1, 1))
fecha_fin = st.sidebar.date_input("Fecha de fin", datetime.today())

# Descargar y graficar datos
if st.sidebar.button("Generar Gráfico"):
    if fecha_inicio > fecha_fin:
        st.error("La fecha de inicio no puede ser mayor que la fecha de fin.")
    else:
        serie_id = variables[variable_seleccionada]
        fecha_inicio_str = fecha_inicio.strftime("%Y-%m-%d")
        fecha_fin_str = fecha_fin.strftime("%Y-%m-%d")

        # Obtener datos
        if "Banxico" in variable_seleccionada:
            datos = obtener_datos_banxico(serie_id, fecha_inicio_str, fecha_fin_str)
        else:
            datos = obtener_datos_fed(serie_id, fecha_inicio_str, fecha_fin_str)

        # Graficar datos
        if not datos.empty:
            st.subheader(f"Gráfico de {variable_seleccionada}")
            plt.figure(figsize=(10, 5))
            plt.plot(datos["fecha"], datos["dato"], marker="o", label=variable_seleccionada)
            plt.title(variable_seleccionada)
            plt.xlabel("Fecha")
            plt.ylabel("Valor")
            plt.grid()
            plt.legend()
            st.pyplot(plt.gcf())
        else:
            st.warning("No se encontraron datos para el rango de fechas seleccionado.")