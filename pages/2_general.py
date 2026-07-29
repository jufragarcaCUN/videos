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

# ==================== CONFIGURACIÓN DE MÉTRICAS ====================
METRICAS_CONFIG = {
    "CPM": {
        "nombre": "Cortes o interrupciones",
        "columna": "CPM",
        "unidad": "cortes/min",
        "que_mide": "Frecuencia de cortes visuales o ediciones en el video.",
        "como_mide": (
            "Se analiza el video frame por frame, detectando cambios bruscos"
            " de escena."
        ),
        "formato": "{:.1f}",
        "limite_cumple": 18.0,
        "condicion": "mayor",
        "interpretacion": ("Un valor > 18.0 indica un video dinámico con buen ritmo."),
    },
    "DME_s": {
        "nombre": "Duración del monólogo",
        "columna": "DME_s",
        "unidad": "segundos",
        "que_mide": "Tiempo continuo que habla el profesor sin hacer pausas.",
        "como_mide": (
            "Se procesa el audio del video, detectando segmentos de habla" " continua."
        ),
        "formato": "{:.1f}s",
        "limite_cumple": 3.5,
        "condicion": "menor",
        "interpretacion": (
            "Un valor < 3.5 segundos indica un ritmo dinámico con pausas" " frecuentes."
        ),
    },
    "DTE_ratio": {
        "nombre": "Porcentaje de habla",
        "columna": "DTE_ratio",
        "unidad": "",
        "que_mide": (
            "Proporción del tiempo total del video en el que el profesor tiene"
            " voz activa."
        ),
        "como_mide": (
            "Se analiza el audio y se calcula el tiempo con voz activa"
            " dividido por el total."
        ),
        "formato": "{:.3f}",
        "limite_cumple": 0.50,
        "condicion": "menor_igual",
        "interpretacion": ("Un valor ≤ 0.50 indica una clase más interactiva."),
    },
    "Jitter_Score": {
        "nombre": "Estabilidad técnica",
        "columna": "Jitter_Score",
        "unidad": "",
        "que_mide": "Mide los tirones y sacudidas del video.",
        "como_mide": "Se analiza el movimiento de la cámara entre frames.",
        "formato": "{:.3f}",
        "limite_cumple": 0.4,
        "condicion": "mayor",
        "interpretacion": "Un valor > 0.4 indica una grabación estable.",
    },
    "IMP_promedio": {
        "nombre": "Movimiento promedio",
        "columna": "IMP_promedio",
        "unidad": "",
        "que_mide": "Cantidad de movimiento del profesor en pantalla.",
        "como_mide": "Se analiza el movimiento entre frames consecutivos.",
        "formato": "{:.3f}",
        "limite_cumple": 4.0,
        "condicion": "mayor",
        "interpretacion": (
            "Un valor > 4.0 indica una clase dinámica con movimiento activo."
        ),
    },
    "sigma2_IM": {
        "nombre": "Cambios de movimiento",
        "columna": "sigma2_IM",
        "unidad": "",
        "que_mide": "Qué tan bruscos o dinámicos son los cambios de movimiento.",
        "como_mide": "Se calcula la varianza de los movimientos entre frames.",
        "formato": "{:.3f}",
        "limite_cumple": 8.5,
        "condicion": "mayor",
        "interpretacion": ("Un valor > 8.5 indica cambios de movimiento dinámicos."),
    },
    "Tone_CoV": {
        "nombre": "Variación de la voz",
        "columna": "Tone_CoV",
        "unidad": "",
        "que_mide": "Variación y modulación del tono de voz del profesor.",
        "como_mide": ("Se extrae la frecuencia fundamental y se calcula su variación."),
        "formato": "{:.3f}",
        "limite_cumple": 0.32,
        "condicion": "mayor",
        "interpretacion": (
            "Un valor > 0.32 indica una voz dinámica con variaciones de tono."
        ),
    },
    "Enthusiasm_Score": {
        "nombre": "Nivel de energía",
        "columna": "Enthusiasm_Score",
        "unidad": "",
        "que_mide": "Fuerza y entusiasmo percibido en la voz del profesor.",
        "como_mide": "Se analizan intensidad, ritmo y variaciones tonales.",
        "formato": "{:.3f}",
        "limite_cumple": 0.15,
        "condicion": "mayor",
        "interpretacion": (
            "Un valor > 0.15 indica una clase con energía y entusiasmo."
        ),
    },
}


def verificar_cumplimiento(valor, limite, condicion):
    """Verifica si un valor cumple con la condición establecida"""
    if limite is None or condicion is None:
        return None
    if condicion == "mayor":
        return valor > limite
    elif condicion == "menor":
        return valor < limite
    elif condicion == "menor_igual":
        return valor <= limite
    elif condicion == "mayor_igual":
        return valor >= limite
    return None


# ==================== OBTENER DATOS DE LA SESIÓN ====================
if "df_filtrado" in st.session_state and st.session_state["df_filtrado"] is not None:
    df_filtrado = st.session_state["df_filtrado"].copy()
else:
    st.error(
        "❌ No se encontraron datos cargados. Por favor, recarga el sistema desde la página principal."
    )
    st.stop()


# ==================== CONTENIDO PRINCIPAL DE LA PÁGINA ====================
st.header("📊 Visión General")

# ====================================================================
# FILTROS ADICIONALES CON CHECKBOX
# ====================================================================
st.markdown("### 🔍 Filtros adicionales")

col_c1, col_c2 = st.columns(2)

with col_c1:
    activar_clase = st.checkbox("🎯 Aburrido vs entretenido", key="chk_clase")
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
    activar_estado = st.checkbox("👔 Estado Docente", key="chk_estado")
    if activar_estado and "Estado_Docente" in df_filtrado.columns:
        opciones_estado = ["Todos"] + sorted(
            df_filtrado["Estado_Docente"].dropna().unique().tolist()
        )
        filtro_estado = st.selectbox(
            "Seleccionar Estado", opciones_estado, key="sel_estado"
        )
    else:
        filtro_estado = "Todos"

# ====================================================================
# APLICAR FILTROS DEL CUERPO
# ====================================================================
if activar_clase and filtro_clase != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Clase_Predicha"] == filtro_clase]
if activar_estado and filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado_Docente"] == filtro_estado]

if df_filtrado.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados.")
    st.stop()

st.info(f"📊 Mostrando {len(df_filtrado)} registros")

# ====================================================================
# KPIs
# ====================================================================
st.markdown("---")
st.subheader("📊 Resumen Ejecutivo")

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
        "Total Áreas",
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

# ====================================================================
# COLUMNAS DISPONIBLES
# ====================================================================
st.markdown("---")
st.markdown("### 📊 Columnas disponibles para comparar")

columnas_disponibles = [
    col for col in METRICAS_CONFIG.keys() if col in df_filtrado.columns
]
df_columnas = pd.DataFrame(
    {
        "Columna": columnas_disponibles,
        "Métrica": [METRICAS_CONFIG[col]["nombre"] for col in columnas_disponibles],
        "Unidad": [METRICAS_CONFIG[col]["unidad"] for col in columnas_disponibles],
        "Límite": [
            METRICAS_CONFIG[col]["limite_cumple"] for col in columnas_disponibles
        ],
        "Condición": [
            METRICAS_CONFIG[col]["condicion"] for col in columnas_disponibles
        ],
    }
)
st.dataframe(df_columnas, use_container_width=True, hide_index=True)

# ====================================================================
# SELECCIÓN DE MÉTRICA
# ====================================================================
st.markdown("---")

metricas_disponibles = [
    col for col in METRICAS_CONFIG.keys() if col in df_filtrado.columns
]

if not metricas_disponibles:
    st.warning("⚠️ No hay métricas disponibles para graficar")
    st.stop()

col_metrica = st.selectbox(
    "📊 Seleccionar métrica para graficar",
    options=metricas_disponibles,
    format_func=lambda x: f"{METRICAS_CONFIG[x]['nombre']} ({METRICAS_CONFIG[x]['columna']})",
    key="metrica_principal",
)

config = METRICAS_CONFIG[col_metrica]

# ====================================================================
# GRÁFICA 1: POR DOCENTE
# ====================================================================
with st.expander(
    f"👨‍🏫 Comparación por Docente - {config['nombre']} (columna: {config['columna']})",
    expanded=True,
):

    st.markdown(
        f"""
    **📌 Columna en Excel:** `{config['columna']}`  
    **📌 ¿Qué mide?** {config['que_mide']}  
    **🔬 ¿Cómo se mide?** {config['como_mide']}  
    **🎯 Línea roja en: {config['limite_cumple']}**  
    **📖 Interpretación:** {config['interpretacion']}
    """
    )

    if "nombres_apellidos" in df_filtrado.columns:
        datos_docentes = (
            df_filtrado.groupby("nombres_apellidos")[col_metrica].mean().reset_index()
        )
        datos_docentes = datos_docentes.dropna()
        datos_docentes = datos_docentes.sort_values(col_metrica, ascending=True)

        if not datos_docentes.empty:
            cumple_count = sum(
                1
                for _, row in datos_docentes.iterrows()
                if verificar_cumplimiento(
                    row[col_metrica], config["limite_cumple"], config["condicion"]
                )
            )
            total = len(datos_docentes)
            no_cumple = total - cumple_count

            if cumple_count == 0:
                st.warning(
                    f"⚠️ **Ningún docente cumple** con la condición ({no_cumple} de {total} por debajo del límite)"
                )
            elif no_cumple == 0:
                st.success(
                    f"✅ **Todos los docentes cumplen** con la condición ({cumple_count} de {total})"
                )
            else:
                st.info(
                    f"📊 **{cumple_count} docentes cumplen** y **{no_cumple} no cumplen** con la condición"
                )

            fig = px.bar(
                datos_docentes,
                x="nombres_apellidos",
                y=col_metrica,
                title=f"{config['nombre']} - Comparación por Docente",
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
                annotation_text=f"Límite: {config['limite_cumple']}",
                annotation_position="top right",
            )

            fig.update_traces(textposition="outside")
            fig.update_layout(
                template="plotly_white",
                height=max(400, len(datos_docentes) * 50),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Docente",
                yaxis_title=f"{config['nombre']} ({config['unidad']})",
                yaxis=dict(showgrid=True, gridcolor="lightgray"),
                margin=dict(l=50, r=50, t=80, b=50),
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos de docentes para mostrar")

# ====================================================================
# GRÁFICA 2: POR ÁREA
# ====================================================================
with st.expander(
    f"📚 Comparación por Área - {config['nombre']} (columna: {config['columna']})",
    expanded=False,
):

    st.markdown(
        f"""
    **📌 Columna en Excel:** `{config['columna']}`  
    **📌 ¿Qué mide?** {config['que_mide']}  
    **🔬 ¿Cómo se mide?** {config['como_mide']}  
    **🎯 Línea roja en: {config['limite_cumple']}**  
    **📖 Interpretación:** {config['interpretacion']}
    """
    )

    if "area" in df_filtrado.columns:
        datos_areas = df_filtrado.groupby("area")[col_metrica].mean().reset_index()
        datos_areas = datos_areas.dropna()
        datos_areas = datos_areas.sort_values(col_metrica, ascending=True)

        if not datos_areas.empty:
            cumple_count = sum(
                1
                for _, row in datos_areas.iterrows()
                if verificar_cumplimiento(
                    row[col_metrica], config["limite_cumple"], config["condicion"]
                )
            )
            total = len(datos_areas)
            no_cumple = total - cumple_count

            if cumple_count == 0:
                st.warning(
                    f"⚠️ **Ningún área cumple** con la condición ({no_cumple} de {total} por debajo del límite)"
                )
            elif no_cumple == 0:
                st.success(
                    f"✅ **Todas las áreas cumplen** con la condición ({cumple_count} de {total})"
                )
            else:
                st.info(
                    f"📊 **{cumple_count} áreas cumplen** y **{no_cumple} no cumplen** con la condición"
                )

            fig = px.bar(
                datos_areas,
                x="area",
                y=col_metrica,
                title=f"{config['nombre']} - Comparación por Área",
                color=col_metrica,
                color_continuous_scale="Viridis",
                text=datos_areas[col_metrica].apply(
                    lambda x: config["formato"].format(x)
                ),
                labels={
                    "area": "Área",
                    col_metrica: f"{config['nombre']} ({config['unidad']})",
                },
            )

            fig.add_hline(
                y=config["limite_cumple"],
                line_dash="dash",
                line_color="red",
                line_width=2,
                annotation_text=f"Límite: {config['limite_cumple']}",
                annotation_position="top right",
            )

            fig.update_traces(textposition="outside")
            fig.update_layout(
                template="plotly_white",
                height=max(400, len(datos_areas) * 60),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Área",
                yaxis_title=f"{config['nombre']} ({config['unidad']})",
                yaxis=dict(showgrid=True, gridcolor="lightgray"),
                margin=dict(l=50, r=50, t=80, b=50),
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos de áreas para mostrar")

# ====================================================================
# GRÁFICA 3: POR MATERIA
# ====================================================================
with st.expander(
    f"📖 Comparación por Materia - {config['nombre']} (columna: {config['columna']})",
    expanded=False,
):

    st.markdown(
        f"""
    **📌 Columna en Excel:** `{config['columna']}`  
    **📌 ¿Qué mide?** {config['que_mide']}  
    **🔬 ¿Cómo se mide?** {config['como_mide']}  
    **🎯 Línea roja en: {config['limite_cumple']}**  
    **📖 Interpretación:** {config['interpretacion']}
    """
    )

    if "nom_materia" in df_filtrado.columns:
        datos_materias = (
            df_filtrado.groupby("nom_materia")[col_metrica].mean().reset_index()
        )
        datos_materias = datos_materias.dropna()
        datos_materias = datos_materias.sort_values(col_metrica, ascending=True)

        if len(datos_materias) > 20:
            st.info(f"📊 Mostrando top 20 de {len(datos_materias)} materias")
            datos_materias = datos_materias.tail(20)

        if not datos_materias.empty:
            cumple_count = sum(
                1
                for _, row in datos_materias.iterrows()
                if verificar_cumplimiento(
                    row[col_metrica], config["limite_cumple"], config["condicion"]
                )
            )
            total = len(datos_materias)
            no_cumple = total - cumple_count

            if cumple_count == 0:
                st.warning(
                    f"⚠️ **Ninguna materia cumple** con la condición ({no_cumple} de {total} por debajo del límite)"
                )
            elif no_cumple == 0:
                st.success(
                    f"✅ **Todas las materias cumplen** con la condición ({cumple_count} de {total})"
                )
            else:
                st.info(
                    f"📊 **{cumple_count} materias cumplen** y **{no_cumple} no cumplen** con la condición"
                )

            fig = px.bar(
                datos_materias,
                x="nom_materia",
                y=col_metrica,
                title=f"{config['nombre']} - Comparación por Materia",
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
                annotation_text=f"Límite: {config['limite_cumple']}",
                annotation_position="top right",
            )

            fig.update_traces(textposition="outside")
            fig.update_layout(
                template="plotly_white",
                height=max(400, len(datos_materias) * 50),
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Materia",
                yaxis_title=f"{config['nombre']} ({config['unidad']})",
                yaxis=dict(showgrid=True, gridcolor="lightgray"),
                margin=dict(l=50, r=50, t=80, b=50),
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ No hay datos de materias para mostrar")
