# -*- coding: utf-8 -*-
"""
Dashboard - Visión General
Página de Visión General
"""

import datetime
from pathlib import Path
import warnings
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

warnings.filterwarnings("ignore")


# ==================== FUNCIÓN DE ALTURA ====================
def altura():
    return st.session_state.get("altura_grafica", 450)


# ==================== CONFIGURACIÓN DE MÉTRICAS ====================
METRICAS_CONFIG = {
    "DME_s": {
        "nombre": "Duración del Monólogo",
        "columna": "DME_s",
        "unidad": "segundos",
        "formato": "{:.1f}s",
        "limite_cumple": 3.5,
        "condicion": "menor",
    },
    "DTE_ratio": {
        "nombre": "Porcentaje de habla",
        "columna": "DTE_ratio",
        "unidad": "",
        "formato": "{:.2f}",
        "limite_cumple": 0.50,
        "condicion": "menor_igual",
    },
    "Tone_CoV": {
        "nombre": "Variación de la voz",
        "columna": "Tone_CoV",
        "unidad": "",
        "formato": "{:.3f}",
        "limite_cumple": 0.32,
        "condicion": "mayor",
    },
    "Enthusiasm_Score": {
        "nombre": "Nivel de energía",
        "columna": "Enthusiasm_Score",
        "unidad": "",
        "formato": "{:.3f}",
        "limite_cumple": 0.15,
        "condicion": "mayor",
    },
    "IMP_promedio": {
        "nombre": "Movimiento promedio",
        "columna": "IMP_promedio",
        "unidad": "",
        "formato": "{:.3f}",
        "limite_cumple": 4.0,
        "condicion": "mayor",
    },
    "sigma2_IM": {
        "nombre": "Cambios de movimiento",
        "columna": "sigma2_IM",
        "unidad": "",
        "formato": "{:.3f}",
        "limite_cumple": 8.5,
        "condicion": "mayor",
    },
    "Jitter_Score": {
        "nombre": "Estabilidad técnica",
        "columna": "Jitter_Score",
        "unidad": "",
        "formato": "{:.3f}",
        "limite_cumple": 0.4,
        "condicion": "mayor",
    },
}


# ==================== CONVERTIR COMAS DECIMALES A PUNTOS ====================
def convertir_comas_a_puntos(df, columnas_metricas):
    df_convertido = df.copy()
    for col in columnas_metricas:
        if col in df_convertido.columns:
            if df_convertido[col].dtype == "object":
                try:
                    df_convertido[col] = (
                        df_convertido[col]
                        .astype(str)
                        .str.replace(",", ".")
                        .astype(float)
                    )
                except Exception as e:
                    st.warning(f"No se pudo convertir la columna '{col}': {e}")
            elif df_convertido[col].dtype in ["float64", "int64", "float32", "int32"]:
                pass
            else:
                try:
                    df_convertido[col] = (
                        df_convertido[col]
                        .astype(str)
                        .str.replace(",", ".")
                        .astype(float)
                    )
                except Exception as e:
                    pass
    return df_convertido


# ==================== OBTENER DATOS DE LA SESIÓN ====================
if "df_filtrado" in st.session_state and st.session_state["df_filtrado"] is not None:
    df_filtrado = st.session_state["df_filtrado"].copy()
    columnas_metricas = list(METRICAS_CONFIG.keys())
    df_filtrado = convertir_comas_a_puntos(df_filtrado, columnas_metricas)
else:
    st.error(
        "No se encontraron datos cargados. Por favor, recarga el sistema desde la página principal."
    )
    st.stop()

# ==================== CONTENIDO PRINCIPAL ====================
st.header("Vision General")

# ---- FILTROS ADICIONALES ----
st.markdown("### Filtros adicionales")
col_c1, col_c2 = st.columns(2)

with col_c1:
    activar_clase = st.checkbox("Aburrido vs entretenido", key="chk_clase")
    if activar_clase and "Clase_Predicha" in df_filtrado.columns:
        opciones_clase = ["Todos"] + sorted(
            df_filtrado["Clase_Predicha"].dropna().unique().tolist()
        )
        filtro_clase = st.selectbox(
            "Seleccionar Clase", opciones_clase, key="sel_clase"
        )
    else:
        filtro_clase = "Todos"

with col_c2:
    activar_estado = st.checkbox("Estado Docente", key="chk_estado")
    if activar_estado and "Estado_Docente" in df_filtrado.columns:
        opciones_estado = ["Todos"] + sorted(
            df_filtrado["Estado_Docente"].dropna().unique().tolist()
        )
        filtro_estado = st.selectbox(
            "Seleccionar Estado", opciones_estado, key="sel_estado"
        )
    else:
        filtro_estado = "Todos"

# Aplicar filtros adicionales
if activar_clase and filtro_clase != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Clase_Predicha"] == filtro_clase]
if activar_estado and filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado_Docente"] == filtro_estado]

if df_filtrado.empty:
    st.warning("No hay datos con los filtros seleccionados.")
    st.stop()

st.info(f"Mostrando {len(df_filtrado)} registros")

# ---- KPIs ----
st.markdown("---")
st.subheader("Resumen Ejecutivo")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Grabaciones", len(df_filtrado))
with col2:
    st.metric(
        "Total Docentes",
        (
            df_filtrado["nombres_apellidos"].nunique()
            if "nombres_apellidos" in df_filtrado.columns
            else 0
        ),
    )
with col3:
    st.metric(
        "Total Areas",
        df_filtrado["area"].nunique() if "area" in df_filtrado.columns else 0,
    )
with col4:
    st.metric(
        "Total Clases",
        (
            df_filtrado["Clase_Predicha"].nunique()
            if "Clase_Predicha" in df_filtrado.columns
            else 0
        ),
    )

# ---- SELECCIÓN DE MÉTRICA ----
st.markdown("---")
metricas_disponibles = [
    col for col in METRICAS_CONFIG.keys() if col in df_filtrado.columns
]
if not metricas_disponibles:
    st.warning(
        "No hay metricas disponibles para graficar. Verifica que las columnas existan en el Excel."
    )
    st.stop()

col_metrica = st.selectbox(
    "Seleccionar metrica para graficar",
    options=metricas_disponibles,
    format_func=lambda x: f"{METRICAS_CONFIG[x]['nombre']} ({METRICAS_CONFIG[x]['columna']})",
    key="metrica_principal",
)
config = METRICAS_CONFIG[col_metrica]

# ====================================================================
# GRÁFICA 1: TOP 10 POR DOCENTE
# ====================================================================
st.markdown("### Top 10 por Docente")
if "nombres_apellidos" in df_filtrado.columns:
    datos_docentes = (
        df_filtrado.groupby("nombres_apellidos")[col_metrica].mean().reset_index()
    )
    datos_docentes = datos_docentes.dropna()
    datos_docentes = datos_docentes.sort_values(col_metrica, ascending=False).head(10)

    if not datos_docentes.empty:
        fig = px.bar(
            datos_docentes,
            x="nombres_apellidos",
            y=col_metrica,
            title=f"Top 10 Docentes - {config['nombre']}",
            color=col_metrica,
            color_continuous_scale="Viridis",
            text=datos_docentes[col_metrica].apply(
                lambda x: config["formato"].format(x)
            ),
            labels={
                "nombres_apellidos": "Docente",
                col_metrica: f"{config['nombre']} ({config['unidad']})",
            },
        )
        fig.add_hline(
            y=config["limite_cumple"],
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"Limite: {config['limite_cumple']}",
            annotation_position="top right",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            template="plotly_white",
            height=altura(),
            showlegend=False,
            xaxis_title="Docente",
            yaxis_title=f"{config['nombre']} ({config['unidad']})",
            yaxis=dict(showgrid=True, gridcolor="lightgray"),
            margin=dict(l=40, r=40, t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos de docentes para mostrar")
else:
    st.warning("Columna 'nombres_apellidos' no encontrada")

# ====================================================================
# GRÁFICA 2: TOP 10 POR ÁREA
# ====================================================================
st.markdown("### Top 10 por Area")
if "area" in df_filtrado.columns:
    datos_areas = df_filtrado.groupby("area")[col_metrica].mean().reset_index()
    datos_areas = datos_areas.dropna()
    datos_areas = datos_areas.sort_values(col_metrica, ascending=False).head(10)

    if not datos_areas.empty:
        fig = px.bar(
            datos_areas,
            x="area",
            y=col_metrica,
            title=f"Top 10 Areas - {config['nombre']}",
            color=col_metrica,
            color_continuous_scale="Viridis",
            text=datos_areas[col_metrica].apply(lambda x: config["formato"].format(x)),
            labels={
                "area": "Area",
                col_metrica: f"{config['nombre']} ({config['unidad']})",
            },
        )
        fig.add_hline(
            y=config["limite_cumple"],
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"Limite: {config['limite_cumple']}",
            annotation_position="top right",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            template="plotly_white",
            height=altura(),
            showlegend=False,
            xaxis_title="Area",
            yaxis_title=f"{config['nombre']} ({config['unidad']})",
            yaxis=dict(showgrid=True, gridcolor="lightgray"),
            margin=dict(l=40, r=40, t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos de areas para mostrar")
else:
    st.warning("Columna 'area' no encontrada")

# ====================================================================
# GRÁFICA 3: TOP 10 POR MATERIA
# ====================================================================
st.markdown("### Top 10 por Materia")
if "nom_materia" in df_filtrado.columns:
    datos_materias = (
        df_filtrado.groupby("nom_materia")[col_metrica].mean().reset_index()
    )
    datos_materias = datos_materias.dropna()
    datos_materias = datos_materias.sort_values(col_metrica, ascending=False).head(10)

    if not datos_materias.empty:
        fig = px.bar(
            datos_materias,
            x="nom_materia",
            y=col_metrica,
            title=f"Top 10 Materias - {config['nombre']}",
            color=col_metrica,
            color_continuous_scale="Viridis",
            text=datos_materias[col_metrica].apply(
                lambda x: config["formato"].format(x)
            ),
            labels={
                "nom_materia": "Materia",
                col_metrica: f"{config['nombre']} ({config['unidad']})",
            },
        )
        fig.add_hline(
            y=config["limite_cumple"],
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text=f"Limite: {config['limite_cumple']}",
            annotation_position="top right",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            template="plotly_white",
            height=altura(),
            showlegend=False,
            xaxis_title="Materia",
            yaxis_title=f"{config['nombre']} ({config['unidad']})",
            yaxis=dict(showgrid=True, gridcolor="lightgray"),
            margin=dict(l=40, r=40, t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos de materias para mostrar")
else:
    st.warning("Columna 'nom_materia' no encontrada")
