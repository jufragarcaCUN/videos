"""
Dashboard - Visión General
Vista 100% basada en Porcentaje de Cumplimiento (%)
"""

import warnings
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

warnings.filterwarnings("ignore")


def altura():
    return st.session_state.get("altura_grafica", 600)


# METRICAS Y REGLAS DE CUMPLIMIENTO
METRICAS_CONFIG = {
    "DME_s": {"nombre": "Duración del monólogo", "limite": 3.5, "condicion": "menor"},
    "DTE_ratio": {
        "nombre": "Porcentaje de habla",
        "limite": 0.5,
        "condicion": "menor_igual",
    },
    "Tone_CoV": {"nombre": "Variación de la voz", "limite": 0.32, "condicion": "mayor"},
    "sigma2_IM": {
        "nombre": "Cambios de movimiento",
        "limite": 8.5,
        "condicion": "mayor",
    },
    "Jitter_Score": {
        "nombre": "Estabilidad técnica",
        "limite": 0.4,
        "condicion": "mayor",
    },
    "IMP_promedio": {
        "nombre": "Movimiento promedio",
        "limite": 4.0,
        "condicion": "mayor",
    },
    "Enthusiasm_Score": {
        "nombre": "Nivel de energía",
        "limite": 0.15,
        "condicion": "mayor",
    },
}


def calcular_cumplimiento(valor, config):
    """Convierte el valor directamente a % de cumplimiento (0-100%)."""
    if pd.isna(valor):
        return np.nan
    try:
        val = float(str(valor).replace(",", "."))
    except ValueError:
        return np.nan

    limite = config["limite"]
    condicion = config["condicion"]

    if condicion in ["mayor", "mayor_igual"]:
        porcentaje = (val / limite) * 100 if limite != 0 else 100.0
    elif condicion in ["menor", "menor_igual"]:
        porcentaje = (limite / val) * 100 if val != 0 else 100.0
    else:
        porcentaje = np.nan

    return float(np.clip(porcentaje, 0.0, 100.0))


def mostrar_tabla_metricas():
    """Única tabla descriptiva del sistema."""
    st.markdown("### 📋 Diccionario de Métricas")
    st.markdown(
        """
    <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #2e7d32;">
        <p style="margin: 0; font-size: 0.9rem;">
            <strong>📖 ¿Qué significan estas métricas?</strong> Evalúan la calidad de las grabaciones de clase.
            Cada métrica mide un aspecto diferente del desempeño del docente: fluidez, energía, movimiento, estabilidad vocal, etc.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    data = [
        {
            "Métrica": "Duración del monólogo",
            "Columna": "DME_s",
            "¿Qué mide?": "Tiempo promedio que el docente habla sin interrupción.",
            "¿Cómo se mide?": "Promedio de segmentos de habla continua.",
            "Unidad": "segundos",
            "Meta": "< 3.5",
            "Tipo": "Menor es mejor",
        },
        {
            "Métrica": "Porcentaje de habla",
            "Columna": "DTE_ratio",
            "¿Qué mide?": "Relación entre tiempo de habla del docente y tiempo total.",
            "¿Cómo se mide?": "Tiempo hablado / duración total.",
            "Unidad": "adimensional",
            "Meta": "≤ 0.5",
            "Tipo": "Rango (0.0 - 0.5)",
        },
        {
            "Métrica": "Estabilidad técnica",
            "Columna": "Jitter_Score",
            "¿Qué mide?": "Estabilidad de la voz. Mide fluidez y naturalidad.",
            "¿Cómo se mide?": "Variación de la frecuencia fundamental.",
            "Unidad": "adimensional",
            "Meta": "> 0.4",
            "Tipo": "Mayor es mejor",
        },
        {
            "Métrica": "Movimiento promedio",
            "Columna": "IMP_promedio",
            "¿Qué mide?": "Cantidad de movimiento corporal del docente.",
            "¿Cómo se mide?": "Promedio de movimiento a lo largo de la grabación.",
            "Unidad": "adimensional",
            "Meta": "> 4.0",
            "Tipo": "Mayor es mejor",
        },
        {
            "Métrica": "Cambios de movimiento",
            "Columna": "sigma2_IM",
            "¿Qué mide?": "Variación en el movimiento corporal.",
            "¿Cómo se mide?": "Desviación estándar del movimiento.",
            "Unidad": "adimensional",
            "Meta": "> 8.5",
            "Tipo": "Mayor es mejor",
        },
        {
            "Métrica": "Variación de la voz",
            "Columna": "Tone_CoV",
            "¿Qué mide?": "Variación del tono de voz del docente.",
            "¿Cómo se mide?": "Coeficiente de variación del tono.",
            "Unidad": "adimensional",
            "Meta": "> 0.32",
            "Tipo": "Mayor es mejor",
        },
        {
            "Métrica": "Nivel de energía",
            "Columna": "Enthusiasm_Score",
            "¿Qué mide?": "Nivel de entusiasmo y energía del docente.",
            "¿Cómo se mide?": "Detección de patrones de entusiasmo en la voz.",
            "Unidad": "adimensional",
            "Meta": "> 0.15",
            "Tipo": "Mayor es mejor",
        },
    ]

    st.dataframe(
        pd.DataFrame(data),
        column_config={
            "Métrica": st.column_config.TextColumn("Métrica", width="medium"),
            "Columna": st.column_config.TextColumn("Columna", width="small"),
            "¿Qué mide?": st.column_config.TextColumn("¿Qué mide?", width="large"),
            "¿Cómo se mide?": st.column_config.TextColumn(
                "¿Cómo se mide?", width="large"
            ),
            "Unidad": st.column_config.TextColumn("Unidad", width="small"),
            "Meta": st.column_config.TextColumn("Meta", width="small"),
            "Tipo": st.column_config.TextColumn("Tipo", width="medium"),
        },
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("---")


# CARGA Y PROCESAMIENTO
if "df_filtrado" in st.session_state and st.session_state["df_filtrado"] is not None:
    df_filtrado = st.session_state["df_filtrado"].copy()

    for col, cfg in METRICAS_CONFIG.items():
        if col in df_filtrado.columns:
            df_filtrado[f"{col}_cumplimiento"] = df_filtrado[col].apply(
                lambda val: calcular_cumplimiento(val, cfg)
            )
else:
    st.error("❌ No hay datos cargados en la sesión.")
    st.stop()

# INTERFAZ
st.header("📊 Visión General")

# FILTROS
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

if activar_clase and filtro_clase != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Clase_Predicha"] == filtro_clase]
if activar_estado and filtro_estado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Estado_Docente"] == filtro_estado]

if df_filtrado.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados.")
    st.stop()

st.info(f"📊 Mostrando {len(df_filtrado)} registros")

# TARJETAS RESUMEN EJECUTIVO
st.markdown("---")
st.subheader("📊 Resumen Ejecutivo")

aburridos = (
    len(
        df_filtrado[df_filtrado["Clase_Predicha"].astype(str).str.upper() == "ABURRIDO"]
    )
    if "Clase_Predicha" in df_filtrado.columns
    else 0
)
entretenidos = (
    len(
        df_filtrado[
            df_filtrado["Clase_Predicha"].astype(str).str.upper() == "ENTRETENIDO"
        ]
    )
    if "Clase_Predicha" in df_filtrado.columns
    else 0
)

col1, col2, col3, col4, col5, col6 = st.columns(6)
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
with col5:
    st.metric("😴 Aburridas", aburridos)
with col6:
    st.metric("🎉 Entretenidas", entretenidos)

# SELECCIÓN DE MÉTRICA
st.markdown("---")
metricas_disponibles = [
    col for col in METRICAS_CONFIG.keys() if col in df_filtrado.columns
]

if not metricas_disponibles:
    st.warning("⚠️ No hay métricas disponibles en el dataset.")
    st.stop()

col_metrica = st.selectbox(
    "📊 Seleccionar métrica (% de Cumplimiento)",
    options=metricas_disponibles,
    format_func=lambda x: f"{METRICAS_CONFIG[x]['nombre']} ({x})",
    key="metrica_principal",
)

col_a_graficar = f"{col_metrica}_cumplimiento"

# GRÁFICA DOCENTES
if "nombres_apellidos" in df_filtrado.columns:
    datos_docentes = (
        df_filtrado.groupby("nombres_apellidos")[col_a_graficar]
        .mean()
        .reset_index()
        .dropna()
        .nlargest(10, col_a_graficar)
        .sort_values(col_a_graficar, ascending=True)
    )

    if not datos_docentes.empty:
        fig = px.bar(
            datos_docentes,
            x="nombres_apellidos",
            y=col_a_graficar,
            title=f"Top 10 Docentes - Cumplimiento % ({METRICAS_CONFIG[col_metrica]['nombre']})",
            color=col_a_graficar,
            color_continuous_scale="Viridis",
            text=datos_docentes[col_a_graficar].apply(lambda x: f"{x:.1f}%"),
            labels={"nombres_apellidos": "Docente", col_a_graficar: "Cumplimiento (%)"},
        )
        fig.add_hline(
            y=100.0,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text="Meta: 100%",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            template="plotly_white",
            height=altura(),
            showlegend=False,
            xaxis_title="Docente",
            yaxis_title="Cumplimiento (%)",
            yaxis=dict(showgrid=True, gridcolor="lightgray"),
        )
        st.plotly_chart(fig, use_container_width=True)

# GRÁFICA ÁREAS
if "area" in df_filtrado.columns:
    datos_areas = (
        df_filtrado.groupby("area")[col_a_graficar]
        .mean()
        .reset_index()
        .dropna()
        .nlargest(10, col_a_graficar)
        .sort_values(col_a_graficar, ascending=True)
    )

    if not datos_areas.empty:
        fig = px.bar(
            datos_areas,
            x="area",
            y=col_a_graficar,
            title=f"Top 10 Áreas - Cumplimiento % ({METRICAS_CONFIG[col_metrica]['nombre']})",
            color=col_a_graficar,
            color_continuous_scale="Viridis",
            text=datos_areas[col_a_graficar].apply(lambda x: f"{x:.1f}%"),
            labels={"area": "Área", col_a_graficar: "Cumplimiento (%)"},
        )
        fig.add_hline(
            y=100.0,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text="Meta: 100%",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            template="plotly_white",
            height=altura(),
            showlegend=False,
            xaxis_title="Área",
            yaxis_title="Cumplimiento (%)",
            yaxis=dict(showgrid=True, gridcolor="lightgray"),
        )
        st.plotly_chart(fig, use_container_width=True)

# GRÁFICA MATERIAS
if "nom_materia" in df_filtrado.columns:
    datos_materias = (
        df_filtrado.groupby("nom_materia")[col_a_graficar]
        .mean()
        .reset_index()
        .dropna()
        .nlargest(10, col_a_graficar)
        .sort_values(col_a_graficar, ascending=True)
    )

    if not datos_materias.empty:
        fig = px.bar(
            datos_materias,
            x="nom_materia",
            y=col_a_graficar,
            title=f"Top 10 Materias - Cumplimiento % ({METRICAS_CONFIG[col_metrica]['nombre']})",
            color=col_a_graficar,
            color_continuous_scale="Viridis",
            text=datos_materias[col_a_graficar].apply(lambda x: f"{x:.1f}%"),
            labels={"nom_materia": "Materia", col_a_graficar: "Cumplimiento (%)"},
        )
        fig.add_hline(
            y=100.0,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text="Meta: 100%",
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(
            template="plotly_white",
            height=altura(),
            showlegend=False,
            xaxis_title="Materia",
            yaxis_title="Cumplimiento (%)",
            yaxis=dict(showgrid=True, gridcolor="lightgray"),
        )
        st.plotly_chart(fig, use_container_width=True)

# DICCIONARIO ÚNICO DE MÉTRICAS
st.markdown("---")
mostrar_tabla_metricas()
