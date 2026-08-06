"""
Página de Análisis Profundo - 6 Gráficas Interactivas
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings

warnings.filterwarnings("ignore")

# ================================================================
# CONFIGURACIÓN DE MÉTRICAS
# ================================================================

METRICAS_CONFIG = {
    "DME_s": {
        "nombre": "Duración del monólogo",
        "columna": "DME_s",
        "unidad": "segundos",
        "formato": "{:.1f}s",
        "tipo": "menor",
        "meta": 3.5,
        "limite_cumple": 3.5,
        "condicion": "menor",
    },
    "DTE_ratio": {
        "nombre": "Porcentaje de habla",
        "columna": "DTE_ratio",
        "unidad": "",
        "formato": "{:.3f}",
        "tipo": "rango",
        "min": 0.0,
        "max": 0.50,
        "limite_cumple": 0.50,
        "condicion": "menor_igual",
    },
    "Jitter_Score": {
        "nombre": "Estabilidad técnica",
        "columna": "Jitter_Score",
        "unidad": "",
        "formato": "{:.3f}",
        "tipo": "mayor",
        "meta": 0.40,
        "limite_cumple": 0.4,
        "condicion": "mayor",
    },
    "IMP_promedio": {
        "nombre": "Movimiento promedio",
        "columna": "IMP_promedio",
        "unidad": "",
        "formato": "{:.3f}",
        "tipo": "mayor",
        "meta": 4.0,
        "limite_cumple": 4.0,
        "condicion": "mayor",
    },
    "sigma2_IM": {
        "nombre": "Cambios de movimiento",
        "columna": "sigma2_IM",
        "unidad": "",
        "formato": "{:.3f}",
        "tipo": "mayor",
        "meta": 8.5,
        "limite_cumple": 8.5,
        "condicion": "mayor",
    },
    "Tone_CoV": {
        "nombre": "Variación de la voz",
        "columna": "Tone_CoV",
        "unidad": "",
        "formato": "{:.3f}",
        "tipo": "mayor",
        "meta": 0.32,
        "limite_cumple": 0.32,
        "condicion": "mayor",
    },
    "Enthusiasm_Score": {
        "nombre": "Nivel de energía",
        "columna": "Enthusiasm_Score",
        "unidad": "",
        "formato": "{:.3f}",
        "tipo": "mayor",
        "meta": 0.15,
        "limite_cumple": 0.15,
        "condicion": "mayor",
    },
}

# ================================================================
# FUNCIONES AUXILIARES
# ================================================================


def calcular_cumplimiento(valor, config):
    """Calcula el porcentaje de cumplimiento"""
    if pd.isna(valor):
        return 0.0

    tipo = config.get("tipo")
    meta = config.get("meta")

    if meta is None:
        return 0.0

    try:
        if tipo == "mayor":
            if meta == 0:
                return 0.0
            return min((valor / meta) * 100, 100.0)
        elif tipo == "menor":
            if meta == 0:
                return 0.0
            if valor <= meta:
                return 100.0
            return max(0.0, min((meta / valor) * 100, 100.0))
        elif tipo == "rango":
            min_val = config.get("min", 0)
            max_val = config.get("max", float("inf"))
            return 100.0 if min_val <= valor <= max_val else 0.0
        return 0.0
    except:
        return 0.0


def obtener_estado(pct):
    if pct >= 100:
        return "✅ Cumple"
    elif pct >= 70:
        return "⚠️ Parcial"
    else:
        return "❌ Requiere mejora"


@st.cache_data
def agregar_columnas_cumplimiento(_df, metricas_disp):
    """Agrega columnas de cumplimiento al DataFrame"""
    df_resultado = _df.copy()
    for col in metricas_disp:
        config = METRICAS_CONFIG[col]
        col_cumplimiento = f"{col}_cumplimiento"
        if col in df_resultado.columns and col_cumplimiento not in df_resultado.columns:
            df_resultado[col_cumplimiento] = df_resultado[col].apply(
                lambda x: calcular_cumplimiento(x, config)
            )
    return df_resultado


def get_filtrado_data():
    """Obtiene los datos filtrados del session_state"""
    if "df_filtrado" not in st.session_state:
        st.error("❌ No hay datos filtrados. Regresa a la página principal.")
        st.stop()

    df = st.session_state["df_filtrado"]
    if df is None or df.empty:
        st.warning("⚠️ No hay datos con los filtros seleccionados.")
        st.stop()

    return df


def mostrar_leyenda_grafica(titulo, pregunta, interpretacion):
    st.markdown(
        f"""
    <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #2e7d32;">
        <h4 style="margin: 0; color: #1a1a1a;">📊 {titulo}</h4>
        <p style="margin: 5px 0 0 0; font-size: 0.9rem;">
            <strong>❓ ¿Qué pregunta responde?</strong> {pregunta}
        </p>
        <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: #555;">
            <strong>📖 ¿Cómo interpretarlo?</strong> {interpretacion}
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


def mostrar_interpretacion_grafica(titulo, que_muestra, como_leer, que_buscar):
    with st.container():
        st.markdown("---")
        st.markdown(f"### 📖 {titulo}")
        st.info(que_muestra)
        st.success(como_leer)
        st.warning(que_buscar)
        st.markdown("---")


def mostrar_diccionario_metricas():
    """Muestra el diccionario completo de métricas con explicaciones"""
    st.markdown("### 📊 Diccionario de Métricas - ¿Qué estamos midiendo?")

    metricas_data = [
        {
            "Métrica": "Duración del monólogo (DME_s)",
            "Qué mide": "Tiempo que el docente habla sin interrupción. Mide su capacidad de mantener la atención y fluidez.",
            "Meta": "< 3.5 segundos",
            "Interpretación": "Valores bajos indican que el docente habla en segmentos cortos, manteniendo la atención del estudiante.",
        },
        {
            "Métrica": "Porcentaje de habla (DTE_ratio)",
            "Qué mide": "Relación entre el tiempo que habla el docente y el tiempo total de la clase.",
            "Meta": "≤ 0.5 (máximo 50%)",
            "Interpretación": "Valores bajos indican que el docente no domina la conversación, permitiendo participación del estudiante.",
        },
        {
            "Métrica": "Estabilidad técnica (Jitter_Score)",
            "Qué mide": "Estabilidad y naturalidad de la voz del docente. Fluidez del discurso.",
            "Meta": "> 0.4",
            "Interpretación": "Valores altos indican una voz estable y natural, sin tartamudeos ni vacilaciones.",
        },
        {
            "Métrica": "Movimiento promedio (IMP_promedio)",
            "Qué mide": "Cantidad de movimiento corporal del docente durante la clase.",
            "Meta": "> 4.0",
            "Interpretación": "Valores altos indican un docente dinámico que usa el espacio y el movimiento para mantener la atención.",
        },
        {
            "Métrica": "Cambios de movimiento (sigma2_IM)",
            "Qué mide": "Variación y consistencia del movimiento corporal del docente.",
            "Meta": "> 8.5",
            "Interpretación": "Valores altos indican variedad en los movimientos, evitando la monotonía.",
        },
        {
            "Métrica": "Variación de la voz (Tone_CoV)",
            "Qué mide": "Variación del tono y expresividad vocal del docente.",
            "Meta": "> 0.32",
            "Interpretación": "Valores altos indican una voz expresiva que mantiene el interés del estudiante.",
        },
        {
            "Métrica": "Nivel de energía (Enthusiasm_Score)",
            "Qué mide": "Nivel de entusiasmo y energía vocal del docente.",
            "Meta": "> 0.15",
            "Interpretación": "Valores altos indican un docente energético que transmite pasión por el tema.",
        },
        {
            "Métrica": "Clase Predicha",
            "Qué mide": "Clasificación de la clase como ENTRETENIDO o ABURRIDO.",
            "Meta": "ENTRETENIDO",
            "Interpretación": "Clases clasificadas como ENTRETENIDO son las que tienen mejor desempeño en todas las métricas.",
        },
    ]

    df_metricas = pd.DataFrame(metricas_data)
    st.dataframe(
        df_metricas,
        column_config={
            "Métrica": st.column_config.TextColumn("📊 Métrica", width="medium"),
            "Qué mide": st.column_config.TextColumn("🔍 ¿Qué mide?", width="large"),
            "Meta": st.column_config.TextColumn("🎯 Meta", width="small"),
            "Interpretación": st.column_config.TextColumn(
                "💡 Interpretación", width="large"
            ),
        },
        hide_index=True,
        use_container_width=True,
    )
    st.markdown("---")


# ================================================================
# MAIN
# ================================================================


def main():
    df_filtrado = get_filtrado_data()

    st.header("📈 Análisis Profundo - 6 Gráficas Interactivas")

    # Filtro de clase
    if "Clase_Predicha" in df_filtrado.columns:
        df_filtrado["Clase_Normalizada"] = df_filtrado["Clase_Predicha"].str.upper()
        clases_disponibles = sorted(df_filtrado["Clase_Normalizada"].dropna().unique())
        if len(clases_disponibles) > 0:
            st.markdown("### 🎯 Filtrar por Clase")
            opcion_clase = st.selectbox(
                "Seleccionar clase:",
                options=["Todas"] + clases_disponibles,
                key="filtro_clase_profundidad",
            )
            if opcion_clase != "Todas":
                df_filtrado = df_filtrado[
                    df_filtrado["Clase_Normalizada"] == opcion_clase
                ]
                st.success(f"✅ Mostrando solo clases: **{opcion_clase}**")
            else:
                st.info("📊 Mostrando **todas** las clases")

    st.info(f"📊 Mostrando {len(df_filtrado)} registros con los filtros aplicados")

    # Obtener métricas disponibles
    metricas_disp = [
        col for col in METRICAS_CONFIG.keys() if col in df_filtrado.columns
    ]

    # Agregar columnas de cumplimiento
    with st.spinner("🔄 Calculando métricas de cumplimiento..."):
        df_filtrado = agregar_columnas_cumplimiento(df_filtrado, metricas_disp)

    # ================================================================
    # GRÁFICA 1: Radar Chart
    # ================================================================
    with st.expander("🕸️ Gráfica 1: Radar de Cumplimiento", expanded=True):
        mostrar_leyenda_grafica(
            "Perfil de Cumplimiento del Docente",
            "¿Qué indicadores cumple el docente según los estándares?",
            "🔹 Cada eje = % de cumplimiento. 100% = cumple la meta.",
        )

        if "nombres_apellidos" in df_filtrado.columns and metricas_disp:
            docentes = sorted(df_filtrado["nombres_apellidos"].dropna().unique())
            if len(docentes) > 0:
                docente_seleccionado = st.selectbox(
                    "Seleccionar Docente", docentes, key="radar_docente"
                )

                df_docente = df_filtrado[
                    df_filtrado["nombres_apellidos"] == docente_seleccionado
                ]

                promedios_docente = {}
                for col in metricas_disp:
                    if col in df_docente.columns:
                        promedios_docente[col] = df_docente[col].mean()
                    else:
                        promedios_docente[col] = np.nan

                datos_tabla = []
                nombres_metricas = []
                valores_cumplimiento = []

                for col in metricas_disp:
                    config = METRICAS_CONFIG[col]
                    valor = promedios_docente.get(col, np.nan)
                    if pd.isna(valor):
                        continue

                    pct = calcular_cumplimiento(valor, config)
                    estado = obtener_estado(pct)

                    if config["tipo"] == "mayor":
                        meta_text = f"> {config['meta']}"
                    elif config["tipo"] == "menor":
                        meta_text = f"< {config['meta']}"
                    elif config["tipo"] == "rango":
                        meta_text = f"{config['min']} - {config['max']}"
                    else:
                        meta_text = "-"

                    datos_tabla.append(
                        {
                            "Indicador": config["nombre"],
                            "Valor": config["formato"].format(valor),
                            "Meta": meta_text,
                            "% Cumplimiento": f"{pct:.1f}%",
                            "Estado": estado,
                        }
                    )
                    nombres_metricas.append(config["nombre"])
                    valores_cumplimiento.append(pct)

                if datos_tabla:
                    st.markdown(f"### 📊 Evaluación de {docente_seleccionado}")
                    df_tabla = pd.DataFrame(datos_tabla)
                    st.dataframe(df_tabla, hide_index=True, use_container_width=True)

                    fig_radar = go.Figure()
                    fig_radar.add_trace(
                        go.Scatterpolar(
                            r=valores_cumplimiento,
                            theta=nombres_metricas,
                            fill="toself",
                            name=docente_seleccionado,
                            line_color="#2e7d32",
                            hovertemplate="%{theta}: %{r:.1f}%<extra></extra>",
                        )
                    )
                    fig_radar.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100],
                                tickvals=[0, 25, 50, 75, 100],
                                ticktext=["0%", "25%", "50%", "75%", "100%"],
                            )
                        ),
                        title=f"Perfil de Cumplimiento de {docente_seleccionado}",
                        height=550,
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

                    mostrar_interpretacion_grafica(
                        f"Perfil de Cumplimiento de {docente_seleccionado}",
                        f"Cumple con {sum(1 for p in valores_cumplimiento if p >= 100)} de {len(valores_cumplimiento)} indicadores.",
                        "🔹 100% = cumple la meta, <70% = necesita mejora.",
                        "🎯 Busca los ejes que llegan al 100% y los que están por debajo.",
                    )

    # ================================================================
    # GRÁFICA 2: Mapa de Calor (Top 10)
    # ================================================================
    with st.expander(
        "🔥 Gráfica 2: Mapa de Calor - Top 10 Docentes vs Top 10 Programas",
        expanded=False,
    ):
        mostrar_leyenda_grafica(
            "Cumplimiento por Docente y Programa (Top 10)",
            "¿Qué docentes cumplen mejor en cada programa?",
            "🔹 Verde = alto cumplimiento, Rojo = bajo cumplimiento.",
        )

        if (
            "nombres_apellidos" in df_filtrado.columns
            and "area" in df_filtrado.columns
            and metricas_disp
        ):
            metrica_heatmap = st.selectbox(
                "Seleccionar métrica",
                options=metricas_disp,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="heatmap_metrica",
            )

            col_cumplimiento = f"{metrica_heatmap}_cumplimiento"

            df_heatmap = df_filtrado.pivot_table(
                index="nombres_apellidos",
                columns="area",
                values=col_cumplimiento,
                aggfunc="mean",
            )

            df_heatmap["promedio"] = df_heatmap.mean(axis=1)
            df_heatmap = df_heatmap.sort_values("promedio", ascending=False)
            top_docentes = df_heatmap.head(10).index
            df_heatmap = df_heatmap.loc[top_docentes]
            df_heatmap = df_heatmap.drop(columns=["promedio"])

            promedios_programas = df_heatmap.mean(axis=0).sort_values(ascending=False)
            top_programas = promedios_programas.head(10).index
            df_heatmap = df_heatmap[top_programas]

            if not df_heatmap.empty:
                fig_heatmap = px.imshow(
                    df_heatmap,
                    title=f"Top 10 Docentes vs Top 10 Programas - {METRICAS_CONFIG[metrica_heatmap]['nombre']}",
                    color_continuous_scale="RdYlGn",
                    aspect="auto",
                    text_auto=True,
                    labels={"x": "Programa", "y": "Docente", "color": "% Cumplimiento"},
                    range_color=[0, 100],
                    height=max(400, len(df_heatmap) * 30),
                )
                fig_heatmap.update_layout(
                    template="plotly_white", xaxis=dict(tickangle=45)
                )
                fig_heatmap.update_traces(
                    texttemplate="%{z:.1f}%", textfont=dict(size=10)
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

    # ================================================================
    # GRÁFICA 3: Barras Horizontales (Top 10)
    # ================================================================
    with st.expander("📊 Gráfica 3: Ranking de Programas (Top 10)", expanded=False):
        mostrar_leyenda_grafica(
            "Top 10 Programas por Cumplimiento",
            "¿Qué programas tienen mayor cumplimiento?",
            "🔹 Barras verdes = cumplen (>70%), rojas = no cumplen (<70%).",
        )

        if "area" in df_filtrado.columns and metricas_disp:
            metrica_bar_h = st.selectbox(
                "Seleccionar métrica",
                options=metricas_disp,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="bar_h_metrica",
            )
            col_cumplimiento = f"{metrica_bar_h}_cumplimiento"

            df_area = (
                df_filtrado.groupby("area")[col_cumplimiento]
                .mean()
                .reset_index()
                .dropna()
            )
            df_area = df_area.sort_values(col_cumplimiento, ascending=True).tail(10)

            if not df_area.empty:
                colores_bar = [
                    "#2e7d32" if x >= 70 else "#c62828"
                    for x in df_area[col_cumplimiento]
                ]

                fig_bar_h = go.Figure()
                fig_bar_h.add_trace(
                    go.Bar(
                        x=df_area[col_cumplimiento],
                        y=df_area["area"],
                        orientation="h",
                        marker_color=colores_bar,
                        text=df_area[col_cumplimiento].apply(lambda x: f"{x:.1f}%"),
                        textposition="outside",
                    )
                )
                fig_bar_h.add_vline(
                    x=70,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Umbral 70%",
                )
                fig_bar_h.update_layout(
                    title=f'Top 10 Programas - {METRICAS_CONFIG[metrica_bar_h]["nombre"]}',
                    template="plotly_white",
                    height=max(400, len(df_area) * 40),
                    xaxis_title="% Cumplimiento",
                    yaxis_title="Programa",
                    xaxis=dict(range=[0, 100]),
                )
                st.plotly_chart(fig_bar_h, use_container_width=True)

    # ================================================================
    # GRÁFICA 4: Barras Verticales (Top 10)
    # ================================================================
    with st.expander(
        "📊 Gráfica 4: Top 10 Programas con más Grabaciones", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Top 10 Programas con más Grabaciones",
            "¿Qué programas tienen más grabaciones?",
            "🔹 Verde = ENTRETENIDO, Rojo = ABURRIDO.",
        )

        if "area" in df_filtrado.columns and "Clase_Normalizada" in df_filtrado.columns:
            top_programas = df_filtrado["area"].value_counts().head(10).index
            df_filtrado_top = df_filtrado[df_filtrado["area"].isin(top_programas)]

            df_area_clase = (
                df_filtrado_top.groupby(["area", "Clase_Normalizada"])
                .size()
                .reset_index(name="count")
            )

            if not df_area_clase.empty:
                color_map = {"ENTRETENIDO": "#2e7d32", "ABURRIDO": "#c62828"}

                fig_bar_v = px.bar(
                    df_area_clase,
                    x="area",
                    y="count",
                    color="Clase_Normalizada",
                    color_discrete_map=color_map,
                    title="Top 10 Programas - Distribución por Clase",
                    text="count",
                    barmode="group",
                )
                fig_bar_v.update_traces(textposition="outside")
                fig_bar_v.update_layout(template="plotly_white", height=450)
                st.plotly_chart(fig_bar_v, use_container_width=True)

    # ================================================================
    # GRÁFICA 5: Desviación (Top 10)
    # ================================================================
    with st.expander("🌊 Gráfica 5: Desviación del Promedio (Top 10)", expanded=False):
        mostrar_leyenda_grafica(
            "Desviación de Top 10 Docentes",
            "¿Qué docentes están por encima o debajo del promedio?",
            "🔹 Verde = encima del promedio, Rojo = debajo del promedio.",
        )

        if "nombres_apellidos" in df_filtrado.columns and metricas_disp:
            metrica_water = st.selectbox(
                "Seleccionar métrica",
                options=metricas_disp,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="water_metrica",
            )
            col_cumplimiento = f"{metrica_water}_cumplimiento"

            df_water = (
                df_filtrado.groupby("nombres_apellidos")[col_cumplimiento]
                .mean()
                .reset_index()
                .dropna()
            )
            df_water = df_water.sort_values(col_cumplimiento, ascending=False).head(10)

            if not df_water.empty:
                promedio_general = df_water[col_cumplimiento].mean()
                df_water["desviacion"] = df_water[col_cumplimiento] - promedio_general
                df_water = df_water.sort_values("desviacion", ascending=True)

                colores_water = [
                    "#2e7d32" if x >= 0 else "#c62828" for x in df_water["desviacion"]
                ]

                fig_water = go.Figure()
                fig_water.add_trace(
                    go.Bar(
                        x=df_water["desviacion"],
                        y=df_water["nombres_apellidos"],
                        orientation="h",
                        marker_color=colores_water,
                        text=df_water["desviacion"].apply(lambda x: f"{x:+.1f}%"),
                        textposition="outside",
                    )
                )
                fig_water.add_vline(x=0, line_dash="dash", line_color="gray")
                fig_water.update_layout(
                    title=f'Top 10 Docentes - Desviación de {METRICAS_CONFIG[metrica_water]["nombre"]}',
                    template="plotly_white",
                    height=max(400, len(df_water) * 35),
                    xaxis_title="Desviación (puntos porcentuales)",
                    yaxis_title="Docente",
                )
                st.plotly_chart(fig_water, use_container_width=True)

    # ================================================================
    # GRÁFICA 6: Comparación por Clase
    # ================================================================
    with st.expander(
        "📊 Gráfica 6: Comparación de Cumplimiento por Clase", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Comparación de Cumplimiento por Clase",
            "¿Cómo se compara el cumplimiento entre ENTRETENIDO y ABURRIDO?",
            "🔹 Verde = ENTRETENIDO, Rojo = ABURRIDO.",
        )

        metricas_disponibles = [
            "DME_s",
            "DTE_ratio",
            "Enthusiasm_Score",
            "Tone_CoV",
            "sigma2_IM",
            "Jitter_Score",
            "IMP_promedio",
        ]
        metricas_existentes = [
            col for col in metricas_disponibles if col in df_filtrado.columns
        ]

        if metricas_existentes and "Clase_Normalizada" in df_filtrado.columns:
            metrica_seleccionada = st.selectbox(
                "Selecciona una métrica:",
                options=metricas_existentes,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="bar_clase_metrica",
            )
            col_cumplimiento = f"{metrica_seleccionada}_cumplimiento"

            clases_unicas = df_filtrado["Clase_Normalizada"].dropna().unique()

            if len(clases_unicas) >= 2:
                clase1 = (
                    "ENTRETENIDO"
                    if "ENTRETENIDO" in clases_unicas
                    else clases_unicas[0]
                )
                clase2 = "ABURRIDO" if "ABURRIDO" in clases_unicas else clases_unicas[1]

                df_clase1 = df_filtrado[df_filtrado["Clase_Normalizada"] == clase1]
                df_clase2 = df_filtrado[df_filtrado["Clase_Normalizada"] == clase2]

                prom_clase1 = (
                    df_clase1[col_cumplimiento].mean() if not df_clase1.empty else 0
                )
                prom_clase2 = (
                    df_clase2[col_cumplimiento].mean() if not df_clase2.empty else 0
                )

                df_barras = pd.DataFrame(
                    {
                        "Clase": [clase1, clase2],
                        "Promedio": [prom_clase1, prom_clase2],
                        "Color": ["#2e7d32", "#c62828"],
                    }
                )

                counts = [len(df_clase1), len(df_clase2)]

                fig_barras = go.Figure()
                fig_barras.add_trace(
                    go.Bar(
                        x=df_barras["Clase"],
                        y=df_barras["Promedio"],
                        text=df_barras["Promedio"].apply(lambda x: f"{x:.1f}%"),
                        textposition="outside",
                        marker=dict(color=df_barras["Color"]),
                        customdata=counts,
                    )
                )
                fig_barras.add_hline(
                    y=70,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Umbral 70%",
                )
                fig_barras.update_layout(
                    height=450,
                    template="plotly_white",
                    xaxis_title="Clase",
                    yaxis_title="% Cumplimiento",
                    yaxis=dict(range=[0, 100]),
                )
                st.plotly_chart(fig_barras, use_container_width=True)

        # ================================================================

        # GRÁFICA 7: Comparativa ENTRETENIDO vs ABURRIDO (EN PORCENTAJE DE CUMPLIMIENTO)
        # ================================================================
        with st.expander(
            "📊 Gráfica 7: Comparativa ENTRETENIDO vs ABURRIDO", expanded=False
        ):
            mostrar_leyenda_grafica(
                "Comparativa de Cumplimiento entre ENTRETENIDO y ABURRIDO",
                "¿Qué métricas tienen mayor porcentaje de cumplimiento en cada clase?",
                "🔹 Barras verdes = ENTRETENIDO | Barras rojas = ABURRIDO\n🔹 100% = cumple la meta",
            )

            if "Clase_Normalizada" in df_filtrado.columns and metricas_disp:

                # ============================================================
                # PASO 1: GENERAR COLUMNAS DE CUMPLIMIENTO
                # ============================================================
                df_temp = df_filtrado.copy()

                for col in metricas_disp:
                    col_cumplimiento = f"{col}_cumplimiento"
                    if col_cumplimiento not in df_temp.columns:
                        config = METRICAS_CONFIG[col]
                        df_temp[col_cumplimiento] = df_temp[col].apply(
                            lambda x, config=config: calcular_cumplimiento(x, config)
                        )

                # ============================================================
                # PASO 2: LISTA DE COLUMNAS DE CUMPLIMIENTO
                # ============================================================
                columnas_cumplimiento = [f"{col}_cumplimiento" for col in metricas_disp]
                columnas_existentes = [
                    col for col in columnas_cumplimiento if col in df_temp.columns
                ]

                if columnas_existentes:
                    # ============================================================
                    # PASO 3: CALCULAR PROMEDIO POR CLASE (ENTRETENIDO vs ABURRIDO)
                    # ============================================================
                    df_promedios = (
                        df_temp.groupby("Clase_Normalizada")[columnas_existentes]
                        .mean()
                        .reset_index()
                    )

                    # ============================================================
                    # PASO 4: REORGANIZAR PARA GRÁFICA
                    # ============================================================
                    df_melt = df_promedios.melt(
                        id_vars="Clase_Normalizada",
                        var_name="Columna",
                        value_name="Cumplimiento_%",
                    )

                    # ============================================================
                    # PASO 5: MAPEAR NOMBRES DE MÉTRICAS
                    # ============================================================
                    df_melt["Métrica"] = df_melt["Columna"].str.replace(
                        "_cumplimiento", ""
                    )
                    df_melt["Nombre_Métrica"] = df_melt["Métrica"].map(
                        lambda x: (
                            METRICAS_CONFIG[x]["nombre"] if x in METRICAS_CONFIG else x
                        )
                    )

                    # ============================================================
                    # PASO 6: GRÁFICA DE BARRAS
                    # ============================================================
                    fig = px.bar(
                        df_melt,
                        x="Nombre_Métrica",
                        y="Cumplimiento_%",
                        color="Clase_Normalizada",
                        barmode="group",
                        color_discrete_map={
                            "ENTRETENIDO": "#2e7d32",
                            "ABURRIDO": "#c62828",
                        },
                        title="Comparativa de Cumplimiento entre ENTRETENIDO y ABURRIDO",
                        labels={
                            "Nombre_Métrica": "Métrica",
                            "Cumplimiento_%": "Cumplimiento (%)",
                            "Clase_Normalizada": "Clase",
                        },
                        text_auto=".1f",
                        range_y=[0, 100],
                    )
                    fig.update_layout(
                        template="plotly_white", height=450, xaxis_tickangle=-45
                    )
                    fig.update_traces(textposition="outside")
                    st.plotly_chart(fig, use_container_width=True)

                    # ============================================================
                    # PASO 7: TABLA RESUMEN
                    # ============================================================
                    st.markdown("### 📋 Tabla Resumen (% de Cumplimiento)")

                    df_tabla = df_promedios.set_index(
                        "Clase_Normalizada"
                    ).T.reset_index()
                    df_tabla = df_tabla.rename(columns={"index": "Columna"})

                    # Quitar "_cumplimiento" y mapear nombres
                    df_tabla["Métrica"] = df_tabla["Columna"].str.replace(
                        "_cumplimiento", ""
                    )
                    df_tabla["Métrica"] = df_tabla["Métrica"].map(
                        lambda x: (
                            METRICAS_CONFIG[x]["nombre"] if x in METRICAS_CONFIG else x
                        )
                    )

                    # Calcular diferencia
                    df_tabla["Diferencia"] = (
                        df_tabla["ENTRETENIDO"] - df_tabla["ABURRIDO"]
                    )
                    df_tabla["Mejor"] = df_tabla.apply(
                        lambda row: (
                            "🟢 ENTRETENIDO"
                            if row["Diferencia"] > 0
                            else "🔴 ABURRIDO" if row["Diferencia"] < 0 else "⚪ Igual"
                        ),
                        axis=1,
                    )

                    # Formatear como porcentaje
                    for col in ["ENTRETENIDO", "ABURRIDO", "Diferencia"]:
                        df_tabla[col] = df_tabla[col].apply(lambda x: f"{x:.1f}%")

                    df_tabla = df_tabla.rename(
                        columns={
                            "ENTRETENIDO": "ENTRETENIDO (%)",
                            "ABURRIDO": "ABURRIDO (%)",
                            "Diferencia": "Diferencia (p.p.)",
                        }
                    )

                    st.dataframe(
                        df_tabla[
                            [
                                "Métrica",
                                "ENTRETENIDO (%)",
                                "ABURRIDO (%)",
                                "Diferencia (p.p.)",
                                "Mejor",
                            ]
                        ],
                        hide_index=True,
                        use_container_width=True,
                    )
                else:
                    st.warning("No se pudieron generar columnas de cumplimiento")

    # ================================================================
    # GRÁFICA 8: Top 10 Docentes - ENTRETENIDO vs ABURRIDO
    # ================================================================
    with st.expander(
        "🏆 Gráfica 8: Top 10 Docentes - ENTRETENIDO vs ABURRIDO", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Top 10 Docentes con más Clases ENTRETENIDO",
            "¿Qué docentes tienen más clases ENTRETENIDO?",
            "🔹 Barras verdes = ENTRETENIDO | Barras rojas = ABURRIDO\n🔹 Docentes ordenados de mejor a peor",
        )

        if (
            "nombres_apellidos" in df_filtrado.columns
            and "Clase_Normalizada" in df_filtrado.columns
        ):
            # Contar clases por docente y clase
            df_docente_clase = (
                df_filtrado.groupby(["nombres_apellidos", "Clase_Normalizada"])
                .size()
                .reset_index(name="count")
            )

            # Pivotar para tener columnas ENTRETENIDO y ABURRIDO
            df_pivot = (
                df_docente_clase.pivot(
                    index="nombres_apellidos",
                    columns="Clase_Normalizada",
                    values="count",
                )
                .fillna(0)
                .reset_index()
            )

            # Asegurar que existan ambas columnas
            for col in ["ENTRETENIDO", "ABURRIDO"]:
                if col not in df_pivot.columns:
                    df_pivot[col] = 0

            # Calcular total y porcentaje
            df_pivot["total"] = df_pivot["ENTRETENIDO"] + df_pivot["ABURRIDO"]
            df_pivot["pct_entretenido"] = (
                df_pivot["ENTRETENIDO"] / df_pivot["total"]
            ) * 100

            # Filtrar docentes con al menos 3 clases
            df_pivot = df_pivot[df_pivot["total"] >= 3]

            # Ordenar por porcentaje de ENTRETENIDO
            df_pivot = df_pivot.sort_values("pct_entretenido", ascending=False).head(10)

            if not df_pivot.empty:
                # Crear gráfica de barras apiladas
                fig = go.Figure()

                # Barras de ENTRETENIDO (verde)
                fig.add_trace(
                    go.Bar(
                        y=df_pivot["nombres_apellidos"],
                        x=df_pivot["ENTRETENIDO"],
                        name="ENTRETENIDO",
                        orientation="h",
                        marker_color="#2e7d32",
                        text=df_pivot["ENTRETENIDO"].astype(int),
                        textposition="inside",
                    )
                )

                # Barras de ABURRIDO (rojo)
                fig.add_trace(
                    go.Bar(
                        y=df_pivot["nombres_apellidos"],
                        x=df_pivot["ABURRIDO"],
                        name="ABURRIDO",
                        orientation="h",
                        marker_color="#c62828",
                        text=df_pivot["ABURRIDO"].astype(int),
                        textposition="inside",
                    )
                )

                fig.update_layout(
                    barmode="stack",
                    title="Top 10 Docentes - Clases ENTRETENIDO vs ABURRIDO",
                    template="plotly_white",
                    height=450,
                    xaxis_title="Número de Clases",
                    yaxis_title="Docente",
                    legend=dict(x=1, y=1),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Mostrar tabla con porcentajes
                st.markdown("### 📋 Resumen por Docente")
                df_show = df_pivot[
                    [
                        "nombres_apellidos",
                        "ENTRETENIDO",
                        "ABURRIDO",
                        "total",
                        "pct_entretenido",
                    ]
                ].copy()
                df_show = df_show.rename(
                    columns={
                        "nombres_apellidos": "Docente",
                        "ENTRETENIDO": "Clases ENTRETENIDO",
                        "ABURRIDO": "Clases ABURRIDO",
                        "total": "Total Clases",
                        "pct_entretenido": "% ENTRETENIDO",
                    }
                )
                df_show["% ENTRETENIDO"] = df_show["% ENTRETENIDO"].apply(
                    lambda x: f"{x:.1f}%"
                )
                st.dataframe(df_show, hide_index=True, use_container_width=True)

    # ================================================================
    # 📋 TABLA DE RECOMENDACIONES - SOLO DOCENTE SELECCIONADO (AL FINAL)
    # ================================================================
    st.write("---")
    with st.expander("📋 Tabla de recomendaciones", expanded=True):
        if (
            "nombres_apellidos" in df_filtrado.columns
            and "recomen_falencia" in df_filtrado.columns
        ):
            df_tabla = df_filtrado[["nombres_apellidos", "recomen_falencia"]].copy()

            st.subheader("📋 Tabla de Recomendaciones por Docente")

            docentes_disponibles = sorted(
                df_tabla["nombres_apellidos"].dropna().unique()
            )

            if len(docentes_disponibles) > 0:
                opcion_docente = st.selectbox(
                    "👨‍🏫 Seleccionar docente:",
                    options=docentes_disponibles,
                    key="filtro_docente_recomendaciones_final",
                )

                df_tabla = df_tabla[df_tabla["nombres_apellidos"] == opcion_docente]
                st.success(f"✅ Mostrando recomendaciones de: **{opcion_docente}**")

                st.dataframe(
                    df_tabla,
                    column_config={
                        "nombres_apellidos": "👨‍🏫 Docente",
                        "recomen_falencia": "💡 Recomendación",
                    },
                    use_container_width=True,
                    hide_index=True,
                )

                csv = df_tabla.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv,
                    file_name=f"recomendaciones_{opcion_docente}.csv",
                    mime="text/csv",
                )
            else:
                st.info("No hay docentes disponibles para mostrar recomendaciones.")
        else:
            st.warning(
                "No se encontraron las columnas 'nombres_apellidos' o 'recomen_falencia'."
            )


if __name__ == "__main__":
    main()
