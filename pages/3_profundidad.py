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
# 🔥 OBTENER DATOS FILTRADOS DEL SESSION_STATE
# ================================================================


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


# ================================================================
# CONFIGURACIÓN
# ================================================================

METRICAS_CONFIG = {
    "CPM": {
        "nombre": "Cortes o interrupciones",
        "columna": "CPM",
        "unidad": "cortes/min",
        "limite_cumple": 18.0,
        "condicion": "mayor",
        "formato": "{:.1f}",
    },
    "DME_s": {
        "nombre": "Duración del monólogo",
        "columna": "DME_s",
        "unidad": "segundos",
        "limite_cumple": 3.5,
        "condicion": "menor",
        "formato": "{:.1f}s",
    },
    "DTE_ratio": {
        "nombre": "Porcentaje de habla",
        "columna": "DTE_ratio",
        "unidad": "",
        "limite_cumple": 0.50,
        "condicion": "menor_igual",
        "formato": "{:.3f}",
    },
    "Jitter_Score": {
        "nombre": "Estabilidad técnica",
        "columna": "Jitter_Score",
        "unidad": "",
        "limite_cumple": 0.4,
        "condicion": "mayor",
        "formato": "{:.3f}",
    },
    "IMP_promedio": {
        "nombre": "Movimiento promedio",
        "columna": "IMP_promedio",
        "unidad": "",
        "limite_cumple": 4.0,
        "condicion": "mayor",
        "formato": "{:.3f}",
    },
    "sigma2_IM": {
        "nombre": "Cambios de movimiento",
        "columna": "sigma2_IM",
        "unidad": "",
        "limite_cumple": 8.5,
        "condicion": "mayor",
        "formato": "{:.3f}",
    },
    "Tone_CoV": {
        "nombre": "Variación de la voz",
        "columna": "Tone_CoV",
        "unidad": "",
        "limite_cumple": 0.32,
        "condicion": "mayor",
        "formato": "{:.3f}",
    },
    "Enthusiasm_Score": {
        "nombre": "Nivel de energía",
        "columna": "Enthusiasm_Score",
        "unidad": "",
        "limite_cumple": 0.15,
        "condicion": "mayor",
        "formato": "{:.3f}",
    },
    "Porcentaje_Certeza": {
        "nombre": "Certeza",
        "columna": "Porcentaje_Certeza",
        "unidad": "%",
        "limite_cumple": 50,
        "condicion": "mayor",
        "formato": "{:.1f}%",
    },
}

# ================================================================
# FUNCIONES
# ================================================================


def verificar_cumplimiento(valor, limite, condicion):
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

        with st.container():
            st.markdown("#### 🔍 ¿Qué muestra esta gráfica?")
            st.info(que_muestra)

        with st.container():
            st.markdown("#### 📊 ¿Cómo se lee?")
            st.success(como_leer)

        with st.container():
            st.markdown("#### 🎯 ¿Qué debes buscar?")
            st.warning(que_buscar)

        st.markdown("---")


def mostrar_tabla_metricas():
    """Muestra la tabla de métricas con definiciones, cómo se miden y rangos"""

    st.markdown("### 📋 Diccionario de Métricas")
    st.markdown(
        """
    <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #2e7d32;">
        <p style="margin: 0; font-size: 0.9rem;">
            <strong>📖 ¿Qué significan estas métricas?</strong> Estas métricas evalúan la calidad de las grabaciones de clase.
            Cada métrica mide un aspecto diferente del desempeño del docente: fluidez, energía, movimiento, estabilidad vocal, etc.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    data = [
        {
            "Métrica": "Cortes o interrupciones",
            "Columna": "CPM",
            "¿Qué mide?": "Número de cortes o interrupciones en el audio por minuto. Mide la fluidez del discurso del docente.",
            "¿Cómo se mide?": "Se cuentan los cortes en el audio y se dividen por la duración total en minutos.",
            "Unidad": "cortes/min",
            "✅ Buena": "> 18.0",
            "⚠️ Regular": "12.60 - 18.0",
            "❌ Mala": "< 12.60",
        },
        {
            "Métrica": "Duración del monólogo",
            "Columna": "DME_s",
            "¿Qué mide?": "Tiempo promedio que el docente habla sin interrupción. Mide la capacidad de mantener la atención del estudiante.",
            "¿Cómo se mide?": "Se calcula el promedio de los segmentos de habla continua del docente.",
            "Unidad": "segundos",
            "✅ Buena": "< 3.5",
            "⚠️ Regular": "3.5 - 4.55",
            "❌ Mala": "> 4.55",
        },
        {
            "Métrica": "Porcentaje de habla",
            "Columna": "DTE_ratio",
            "¿Qué mide?": "Relación entre el tiempo que habla el docente y el tiempo total de la grabación.",
            "¿Cómo se mide?": "Tiempo hablado por el docente / duración total de la grabación.",
            "Unidad": "adimensional",
            "✅ Buena": "≤ 0.5",
            "⚠️ Regular": "0.5 - 0.65",
            "❌ Mala": "> 0.65",
        },
        {
            "Métrica": "Estabilidad técnica",
            "Columna": "Jitter_Score",
            "¿Qué mide?": "Estabilidad de la voz del docente. Mide fluidez y naturalidad del discurso.",
            "¿Cómo se mide?": "Variación de la frecuencia fundamental de la voz. Valores más altos = mayor estabilidad.",
            "Unidad": "adimensional",
            "✅ Buena": "> 0.4",
            "⚠️ Regular": "0.28 - 0.4",
            "❌ Mala": "< 0.28",
        },
        {
            "Métrica": "Movimiento promedio",
            "Columna": "IMP_promedio",
            "¿Qué mide?": "Cantidad de movimiento corporal del docente. Mide dinamismo y energía en la clase.",
            "¿Cómo se mide?": "Se calcula el promedio de movimiento del docente a través de la grabación.",
            "Unidad": "adimensional",
            "✅ Buena": "> 4.0",
            "⚠️ Regular": "2.80 - 4.0",
            "❌ Mala": "< 2.80",
        },
        {
            "Métrica": "Cambios de movimiento",
            "Columna": "sigma2_IM",
            "¿Qué mide?": "Variación en el movimiento corporal. Mide consistencia y ritmo del docente.",
            "¿Cómo se mide?": "Desviación estándar del movimiento a lo largo de la grabación.",
            "Unidad": "adimensional",
            "✅ Buena": "> 8.5",
            "⚠️ Regular": "5.95 - 8.5",
            "❌ Mala": "< 5.95",
        },
        {
            "Métrica": "Variación de la voz",
            "Columna": "Tone_CoV",
            "¿Qué mide?": "Variación del tono de voz del docente. Mide expresividad y capacidad de mantener el interés.",
            "¿Cómo se mide?": "Coeficiente de variación del tono a lo largo de la grabación.",
            "Unidad": "adimensional",
            "✅ Buena": "> 0.32",
            "⚠️ Regular": "0.22 - 0.32",
            "❌ Mala": "< 0.22",
        },
        {
            "Métrica": "Nivel de energía",
            "Columna": "Enthusiasm_Score",
            "¿Qué mide?": "Nivel de entusiasmo y energía del docente. Mide engagement con los estudiantes.",
            "¿Cómo se mide?": "Algoritmo de análisis de audio que detecta patrones de entusiasmo en la voz.",
            "Unidad": "adimensional",
            "✅ Buena": "> 0.15",
            "⚠️ Regular": "0.10 - 0.15",
            "❌ Mala": "< 0.10",
        },
        {
            "Métrica": "Certeza",
            "Columna": "Porcentaje_Certeza",
            "¿Qué mide?": "Confianza en la clasificación de la grabación. Mide claridad en la transmisión del contenido.",
            "¿Cómo se mide?": "Porcentaje de certeza del modelo de clasificación al evaluar la grabación.",
            "Unidad": "%",
            "✅ Buena": "> 50",
            "⚠️ Regular": "35.00 - 50",
            "❌ Mala": "< 35.00",
        },
    ]

    df_metricas = pd.DataFrame(data)

    st.dataframe(
        df_metricas,
        column_config={
            "Métrica": st.column_config.TextColumn("Métrica", width="medium"),
            "Columna": st.column_config.TextColumn("Columna", width="small"),
            "¿Qué mide?": st.column_config.TextColumn("¿Qué mide?", width="large"),
            "¿Cómo se mide?": st.column_config.TextColumn(
                "¿Cómo se mide?", width="large"
            ),
            "Unidad": st.column_config.TextColumn("Unidad", width="small"),
            "✅ Buena": st.column_config.TextColumn("✅ Buena", width="small"),
            "⚠️ Regular": st.column_config.TextColumn("⚠️ Regular", width="small"),
            "❌ Mala": st.column_config.TextColumn("❌ Mala", width="small"),
        },
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("---")
    df_metricas = pd.DataFrame(data)

    st.dataframe(
        df_metricas,
        column_config={
            "Métrica": "Métrica",
            "Columna": "Columna",
            "Unidad": "Unidad",
            "✅ Buena": st.column_config.TextColumn("✅ Buena"),
            "⚠️ Regular": st.column_config.TextColumn("⚠️ Regular"),
            "❌ Mala": st.column_config.TextColumn("❌ Mala"),
        },
        hide_index=True,
        use_container_width=True,
    )

    st.markdown("---")


# ================================================================
# MAIN
# ================================================================


def main():
    """Función principal que muestra todas las gráficas"""

    df_filtrado = get_filtrado_data()

    st.header("📈 Análisis Profundo - 6 Gráficas Interactivas")
    st.info(f"📊 Mostrando {len(df_filtrado)} registros con los filtros aplicados")

    mostrar_tabla_metricas()

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
            "Total Programas",
            df_filtrado["area"].nunique() if "area" in df_filtrado.columns else 0,
        )
    with col4:
        st.metric(
            "Total Materias",
            (
                df_filtrado["nom_materia"].nunique()
                if "nom_materia" in df_filtrado.columns
                else 0
            ),
        )

    metricas_disp = [
        col for col in METRICAS_CONFIG.keys() if col in df_filtrado.columns
    ]

    # ================================================================
    # GRÁFICA 1: Radar Chart
    # ================================================================
    with st.expander(
        "🕸️ Gráfica 1: Radar Chart - Perfil Multidimensional del Docente", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Perfil Multidimensional del Docente",
            "¿Cuál es el perfil completo de un docente en todas las métricas?",
            "🔹 Cada eje representa una métrica diferente.\n🔹 El área sombreada muestra el desempeño del docente.\n🔹 Mientras más cerca del borde, mejor desempeño.",
        )

        if "nombres_apellidos" in df_filtrado.columns and metricas_disp:
            docentes_radar = sorted(df_filtrado["nombres_apellidos"].dropna().unique())
            if len(docentes_radar) > 0:
                docente_radar = st.selectbox(
                    "Seleccionar Docente", docentes_radar, key="radar_docente"
                )
                df_radar = df_filtrado[
                    df_filtrado["nombres_apellidos"] == docente_radar
                ]
                metricas_radar = [
                    col for col in metricas_disp if col in df_radar.columns
                ]

                if not df_radar.empty and len(metricas_radar) > 2:
                    valores = []
                    nombres_metricas = []
                    for col in metricas_radar:
                        media = df_radar[col].mean()
                        min_val = df_filtrado[col].min()
                        max_val = df_filtrado[col].max()
                        norm = (
                            ((media - min_val) / (max_val - min_val)) * 100
                            if max_val > min_val
                            else 50
                        )
                        valores.append(norm)
                        nombres_metricas.append(METRICAS_CONFIG[col]["nombre"])

                    area_promedio = np.mean(valores)

                    fig_radar = go.Figure()
                    fig_radar.add_trace(
                        go.Scatterpolar(
                            r=valores,
                            theta=nombres_metricas,
                            fill="toself",
                            name=docente_radar,
                            line_color="#2e7d32",
                        )
                    )
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        title=f"Perfil de {docente_radar}",
                        height=500,
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

                    max_idx = np.argmax(valores)
                    min_idx = np.argmin(valores)
                    fortaleza = nombres_metricas[max_idx]
                    debilidad = nombres_metricas[min_idx]

                    mostrar_interpretacion_grafica(
                        f"Cómo interpretar el Radar Chart de {docente_radar}",
                        f"Este gráfico muestra el perfil completo de {docente_radar} en {len(metricas_radar)} métricas. El área promedio es de {area_promedio:.1f}%. Su fortaleza es {fortaleza} ({valores[max_idx]:.1f}%) y su área de mejora es {debilidad} ({valores[min_idx]:.1f}%).",
                        f"🔹 Cada eje va de 0% (centro) a 100% (borde).\n🔹 Mientras más cerca del borde, mejor desempeño en esa métrica.\n🔹 La forma del área muestra las fortalezas y debilidades.",
                        f"🎯 Busca los ejes más largos (fortalezas) y los más cortos (debilidades).",
                    )

    # ================================================================
    # GRÁFICA 2: Mapa de Calor - Desempeño Docente por Programa
    # ================================================================
    with st.expander(
        "🔥 Gráfica 2: Mapa de Calor - Desempeño Docente por Programa", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Desempeño Docente por Programa",
            "¿Cómo se desempeña cada docente en su programa? ¿Qué programas y docentes destacan?",
            "🔹 Cada fila = un docente.\n🔹 Cada columna = un programa.\n🔹 El color indica el desempeño (métrica seleccionada).\n🔹 Verde = alto desempeño, Rojo = bajo desempeño.",
        )

        if (
            "nombres_apellidos" in df_filtrado.columns
            and "area" in df_filtrado.columns
            and metricas_disp
        ):

            metrica_heatmap = st.selectbox(
                "Seleccionar métrica para el mapa de calor",
                options=metricas_disp,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="heatmap_metrica",
            )

            df_heatmap = df_filtrado.pivot_table(
                index="nombres_apellidos",
                columns="area",
                values=metrica_heatmap,
                aggfunc="mean",
            )

            docentes_count = df_filtrado.groupby("nombres_apellidos").size()
            docentes_validos = docentes_count[docentes_count >= 1].index
            df_heatmap = df_heatmap.loc[df_heatmap.index.isin(docentes_validos)]

            programas_count = df_filtrado.groupby("area").size()
            programas_validos = programas_count[programas_count >= 1].index
            df_heatmap = df_heatmap[
                df_heatmap.columns[df_heatmap.columns.isin(programas_validos)]
            ]

            if (
                not df_heatmap.empty
                and len(df_heatmap) > 0
                and len(df_heatmap.columns) > 0
            ):

                df_heatmap["promedio"] = df_heatmap.mean(axis=1)
                df_heatmap = df_heatmap.sort_values("promedio", ascending=False)
                df_heatmap = df_heatmap.drop(columns=["promedio"])

                fig_heatmap = px.imshow(
                    df_heatmap,
                    title=f"Mapa de Calor: {METRICAS_CONFIG[metrica_heatmap]['nombre']} por Docente y Programa",
                    color_continuous_scale="RdYlGn",
                    aspect="auto",
                    text_auto=True,
                    labels={
                        "x": "Programa",
                        "y": "Docente",
                        "color": METRICAS_CONFIG[metrica_heatmap]["nombre"],
                    },
                )

                height = max(400, len(df_heatmap) * 25)
                fig_heatmap.update_layout(
                    template="plotly_white",
                    height=height,
                    xaxis=dict(tickangle=45),
                    yaxis=dict(tickfont=dict(size=10)),
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)

                promedios = df_heatmap.mean(axis=1).sort_values(ascending=False)
                mejor_docente = promedios.index[0] if len(promedios) > 0 else "N/A"
                peor_docente = promedios.index[-1] if len(promedios) > 0 else "N/A"
                mejor_valor = promedios.iloc[0] if len(promedios) > 0 else 0
                peor_valor = promedios.iloc[-1] if len(promedios) > 0 else 0

                promedios_programa = df_heatmap.mean(axis=0).sort_values(
                    ascending=False
                )
                mejor_programa = (
                    promedios_programa.index[0]
                    if len(promedios_programa) > 0
                    else "N/A"
                )
                peor_programa = (
                    promedios_programa.index[-1]
                    if len(promedios_programa) > 0
                    else "N/A"
                )

                if not df_heatmap.empty:
                    max_cell = df_heatmap.max().max()
                    min_cell = df_heatmap.min().min()
                    max_docente = df_heatmap.stack().idxmax()[0]
                    max_programa = df_heatmap.stack().idxmax()[1]
                    min_docente = df_heatmap.stack().idxmin()[0]
                    min_programa = df_heatmap.stack().idxmin()[1]
                else:
                    max_cell = min_cell = 0
                    max_docente = max_programa = min_docente = min_programa = "N/A"

                que_muestra = f"Este mapa de calor muestra el desempeño de {len(df_heatmap)} docentes en {len(df_heatmap.columns)} programas, medido por {METRICAS_CONFIG[metrica_heatmap]['nombre']}. Los colores VERDES indican alto desempeño y ROJOS bajo desempeño."

                if max_docente != "N/A":
                    que_muestra += f" El mejor desempeño es de {max_docente} en {max_programa} con {max_cell:.2f}. El peor es {min_docente} en {min_programa} con {min_cell:.2f}."

                if mejor_docente != "N/A":
                    que_muestra += f" {mejor_docente} es el docente con mejor promedio ({mejor_valor:.2f}) y {peor_docente} el de menor ({peor_valor:.2f})."

                if mejor_programa != "N/A":
                    que_muestra += f" {mejor_programa} es el programa con mejor desempeño y {peor_programa} el de menor."

                como_leer = f"🔹 Cada FILA = un docente.\n🔹 Cada COLUMNA = un programa.\n🔹 COLOR:\n   🟢 Verde = alto {METRICAS_CONFIG[metrica_heatmap]['nombre']}\n   🟡 Amarillo = promedio\n   🔴 Rojo = bajo {METRICAS_CONFIG[metrica_heatmap]['nombre']}\n🔹 Docentes ordenados de mejor a peor promedio (arriba = mejores)."

                que_buscar = f"🎯 Busca:\n🔹 Filas VERDES completas → docentes excelentes en todo.\n🔹 Columnas VERDES completas → programas con buen desempeño.\n🔹 Celdas ROJAS → puntos de mejora específicos."

                if mejor_docente != "N/A":
                    que_buscar += f"\n🔹 {mejor_docente} es el mejor docente promedio."
                if peor_docente != "N/A":
                    que_buscar += f"\n🔹 {peor_docente} necesita mejorar."
                if mejor_programa != "N/A":
                    que_buscar += (
                        f"\n🔹 {mejor_programa} es el programa con mejor desempeño."
                    )

                mostrar_interpretacion_grafica(
                    f"Cómo interpretar el Mapa de Calor de {METRICAS_CONFIG[metrica_heatmap]['nombre']} por Docente y Programa",
                    que_muestra,
                    como_leer,
                    que_buscar,
                )

            else:
                st.warning(
                    "⚠️ No hay suficientes datos para generar el mapa de calor. Se necesitan al menos 1 docente y 1 programa con datos."
                )
        else:
            st.warning(
                "⚠️ No se encontraron las columnas necesarias: 'nombres_apellidos', 'area' o métricas disponibles."
            )

    # ================================================================
    # GRÁFICA 3: Barras Horizontales - Ranking por Programa
    # ================================================================
    with st.expander(
        "📊 Gráfica 3: Barras Horizontales - Ranking por Programa", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Ranking de Programas",
            "¿Qué programas tienen mejor desempeño en cada métrica?",
            "🔹 Cada barra representa el promedio de un programa.\n🔹 La línea roja marca el límite de cumplimiento.\n🔹 Barras verdes = cumplen, rojas = no cumplen.",
        )

        if "area" in df_filtrado.columns and metricas_disp:
            metrica_bar_h = st.selectbox(
                "Seleccionar métrica",
                options=metricas_disp,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="bar_h_metrica",
            )
            df_area = (
                df_filtrado.groupby("area")[metrica_bar_h]
                .mean()
                .reset_index()
                .dropna()
                .sort_values(metrica_bar_h, ascending=True)
            )

            if not df_area.empty:
                cumple_count = sum(
                    1
                    for _, row in df_area.iterrows()
                    if verificar_cumplimiento(
                        row[metrica_bar_h],
                        METRICAS_CONFIG[metrica_bar_h]["limite_cumple"],
                        METRICAS_CONFIG[metrica_bar_h]["condicion"],
                    )
                )
                total = len(df_area)
                mejor_programa = df_area.loc[df_area[metrica_bar_h].idxmax(), "area"]
                peor_programa = df_area.loc[df_area[metrica_bar_h].idxmin(), "area"]
                promedio = df_area[metrica_bar_h].mean()
                limite = METRICAS_CONFIG[metrica_bar_h]["limite_cumple"]

                colores_bar = []
                for _, row in df_area.iterrows():
                    cumple = verificar_cumplimiento(
                        row[metrica_bar_h],
                        METRICAS_CONFIG[metrica_bar_h]["limite_cumple"],
                        METRICAS_CONFIG[metrica_bar_h]["condicion"],
                    )
                    colores_bar.append("#2e7d32" if cumple else "#c62828")

                fig_bar_h = go.Figure()
                fig_bar_h.add_trace(
                    go.Bar(
                        x=df_area[metrica_bar_h],
                        y=df_area["area"],
                        orientation="h",
                        marker_color=colores_bar,
                        text=df_area[metrica_bar_h].apply(
                            lambda x: METRICAS_CONFIG[metrica_bar_h]["formato"].format(
                                x
                            )
                        ),
                        textposition="outside",
                    )
                )
                fig_bar_h.add_vline(
                    x=limite,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Límite: {limite}",
                )
                fig_bar_h.update_layout(
                    title=f"Ranking de Programas - {METRICAS_CONFIG[metrica_bar_h]['nombre']}",
                    template="plotly_white",
                    height=max(400, len(df_area) * 40),
                    xaxis_title=METRICAS_CONFIG[metrica_bar_h]["nombre"],
                    yaxis_title="Programa",
                )
                st.plotly_chart(fig_bar_h, use_container_width=True)

                mostrar_interpretacion_grafica(
                    f"Cómo interpretar el Ranking de Programas en {METRICAS_CONFIG[metrica_bar_h]['nombre']}",
                    f"{cumple_count} de {total} programas ({cumple_count/total*100:.1f}%) cumplen con el estándar. El promedio general es {METRICAS_CONFIG[metrica_bar_h]['formato'].format(promedio)}. {mejor_programa} es el programa con mejor desempeño y {peor_programa} el peor.",
                    f"🔹 Las barras VERDES cumplen con el estándar (a la derecha de la línea roja).\n🔹 Las barras ROJAS NO cumplen (a la izquierda).\n🔹 Barras más largas = mejor desempeño.",
                    f"🎯 Busca qué programas están a la derecha de la línea roja (cumplen) y cuáles a la izquierda (no cumplen). {mejor_programa} es el programa con mejor desempeño.",
                )

    # ================================================================
    # GRÁFICA 4: Barras Verticales - Distribución por Programa
    # ================================================================
    with st.expander(
        "📊 Gráfica 4: Barras Verticales - Distribución por Programa", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Distribución de Grabaciones por Programa",
            "¿Qué programas tienen más grabaciones y cómo se distribuyen?",
            "🔹 Cada barra representa un programa.\n🔹 El color muestra la clase (Verde=ENTRETENIDO, Rojo=ABURRIDO).\n🔹 Altura de barra = cantidad de grabaciones.",
        )

        if "area" in df_filtrado.columns and "Clase_Predicha" in df_filtrado.columns:
            df_area_clase = (
                df_filtrado.groupby(["area", "Clase_Predicha"])
                .size()
                .reset_index(name="count")
            )
            df_area_clase = df_area_clase[
                df_area_clase["Clase_Predicha"].isin(["ENTRETENIDO", "ABURRIDO"])
            ]

            if not df_area_clase.empty:
                fig_bar_v = px.bar(
                    df_area_clase,
                    x="area",
                    y="count",
                    color="Clase_Predicha",
                    color_discrete_map={
                        "ENTRETENIDO": "#2e7d32",
                        "ABURRIDO": "#c62828",
                    },
                    title="Distribución de Grabaciones por Programa y Clase",
                    text="count",
                    barmode="group",
                )
                fig_bar_v.update_traces(textposition="outside")
                fig_bar_v.update_layout(
                    template="plotly_white",
                    height=450,
                    xaxis_title="Programa",
                    yaxis_title="Número de Grabaciones",
                )
                st.plotly_chart(fig_bar_v, use_container_width=True)

                total_entretenido = df_area_clase[
                    df_area_clase["Clase_Predicha"] == "ENTRETENIDO"
                ]["count"].sum()
                total_aburrido = df_area_clase[
                    df_area_clase["Clase_Predicha"] == "ABURRIDO"
                ]["count"].sum()
                total = total_entretenido + total_aburrido
                pct_entretenido = (total_entretenido / total) * 100 if total > 0 else 0

                mejor_programa = (
                    df_area_clase[df_area_clase["Clase_Predicha"] == "ENTRETENIDO"].loc[
                        df_area_clase[df_area_clase["Clase_Predicha"] == "ENTRETENIDO"][
                            "count"
                        ].idxmax(),
                        "area",
                    ]
                    if total_entretenido > 0
                    else "N/A"
                )
                peor_programa = (
                    df_area_clase[df_area_clase["Clase_Predicha"] == "ABURRIDO"].loc[
                        df_area_clase[df_area_clase["Clase_Predicha"] == "ABURRIDO"][
                            "count"
                        ].idxmax(),
                        "area",
                    ]
                    if total_aburrido > 0
                    else "N/A"
                )

                mostrar_interpretacion_grafica(
                    "Cómo interpretar la Distribución de Grabaciones por Programa",
                    f"De {total} grabaciones, {total_entretenido} ({pct_entretenido:.1f}%) son ENTRETENIDAS y {total_aburrido} ({100-pct_entretenido:.1f}%) son ABURRIDAS. {mejor_programa} tiene más clases ENTRETENIDAS. {peor_programa} tiene más clases ABURRIDAS.",
                    f"🔹 Cada barra representa un programa.\n🔹 VERDE = clases ENTRETENIDAS.\n🔹 ROJO = clases ABURRIDAS.\n🔹 Más VERDE que ROJO = programa con buena calidad.",
                    f"🎯 Busca programas con más VERDE que ROJO (buena calidad). Los programas con mucho ROJO necesitan mejorar.",
                )

    # ================================================================
    # GRÁFICA 5: Barras Horizontales - Desviación del Promedio
    # ================================================================
    with st.expander(
        "🌊 Gráfica 5: Barras Horizontales - Desviación del Promedio", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Desviación de Docentes del Promedio",
            "¿Qué docentes están por encima o por debajo del promedio?",
            "🔹 Barras verdes = por encima del promedio (mejor).\n🔹 Barras rojas = por debajo del promedio (peor).\n🔹 La línea vertical en 0 es el promedio.",
        )

        if "nombres_apellidos" in df_filtrado.columns and metricas_disp:
            metrica_water = st.selectbox(
                "Seleccionar métrica",
                options=metricas_disp,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="water_metrica",
            )
            df_water = (
                df_filtrado.groupby("nombres_apellidos")[metrica_water]
                .mean()
                .reset_index()
                .dropna()
            )
            promedio_general = df_filtrado[metrica_water].mean()
            df_water["desviacion"] = df_water[metrica_water] - promedio_general
            df_water = df_water.sort_values("desviacion", ascending=True)

            if not df_water.empty:
                mejor = df_water.loc[df_water["desviacion"].idxmax()]
                peor = df_water.loc[df_water["desviacion"].idxmin()]
                encima = len(df_water[df_water["desviacion"] > 0])
                debajo = len(df_water[df_water["desviacion"] < 0])

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
                        text=df_water["desviacion"].apply(lambda x: f"{x:+.2f}"),
                        textposition="outside",
                    )
                )
                fig_water.add_vline(x=0, line_dash="dash", line_color="gray")
                fig_water.update_layout(
                    title=f"Desviación del Promedio - {METRICAS_CONFIG[metrica_water]['nombre']}",
                    template="plotly_white",
                    height=max(400, len(df_water) * 35),
                    xaxis_title=f"Desviación ({METRICAS_CONFIG[metrica_water]['unidad']})",
                    yaxis_title="Docente",
                )
                st.plotly_chart(fig_water, use_container_width=True)

                mostrar_interpretacion_grafica(
                    f"Cómo interpretar la Desviación del Promedio en {METRICAS_CONFIG[metrica_water]['nombre']}",
                    f"El promedio general es {METRICAS_CONFIG[metrica_water]['formato'].format(promedio_general)}. {encima} docentes están por encima y {debajo} por debajo. {mejor['nombres_apellidos']} es el mejor con {METRICAS_CONFIG[metrica_water]['formato'].format(mejor[metrica_water])}. {peor['nombres_apellidos']} es el peor con {METRICAS_CONFIG[metrica_water]['formato'].format(peor[metrica_water])}.",
                    f"🔹 Las barras VERDES están por ENCIMA del promedio (mejor desempeño).\n🔹 Las barras ROJAS están por DEBAJO del promedio (peor desempeño).\n🔹 La línea vertical en 0 es el PROMEDIO.",
                    f"🎯 Busca los docentes con barras más largas a la derecha (mejores) y a la izquierda (peores).",
                )

    # ================================================================
    # GRÁFICA 6: Lollipop Chart - Ranking por Programa
    # ================================================================
    with st.expander(
        "🍭 Gráfica 6: Lollipop Chart - Ranking por Programa", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Ranking por Programa",
            "¿Qué programas tienen mejor desempeño en cada métrica?",
            "🔹 Cada 'lollipop' (paleta) muestra un programa.\n🔹 La línea conecta el valor con el programa.\n🔹 La línea roja marca el límite de cumplimiento.\n🔹 Programas verdes = cumplen, rojas = no cumplen.",
        )

        if "area" in df_filtrado.columns and metricas_disp:
            metrica_lollipop = st.selectbox(
                "Seleccionar métrica",
                options=metricas_disp,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="lollipop_metrica_area",
            )
            df_lollipop = (
                df_filtrado.groupby("area")[metrica_lollipop]
                .mean()
                .reset_index()
                .dropna()
                .sort_values(metrica_lollipop, ascending=True)
            )

            if not df_lollipop.empty:
                mejor_programa = df_lollipop.loc[df_lollipop[metrica_lollipop].idxmax()]
                peor_programa = df_lollipop.loc[df_lollipop[metrica_lollipop].idxmin()]
                cumple_count = sum(
                    1
                    for _, row in df_lollipop.iterrows()
                    if verificar_cumplimiento(
                        row[metrica_lollipop],
                        METRICAS_CONFIG[metrica_lollipop]["limite_cumple"],
                        METRICAS_CONFIG[metrica_lollipop]["condicion"],
                    )
                )
                total = len(df_lollipop)
                limite = METRICAS_CONFIG[metrica_lollipop]["limite_cumple"]

                colores_lollipop = []
                for _, row in df_lollipop.iterrows():
                    cumple = verificar_cumplimiento(
                        row[metrica_lollipop],
                        METRICAS_CONFIG[metrica_lollipop]["limite_cumple"],
                        METRICAS_CONFIG[metrica_lollipop]["condicion"],
                    )
                    colores_lollipop.append("#2e7d32" if cumple else "#c62828")

                fig_lollipop = go.Figure()
                fig_lollipop.add_trace(
                    go.Scatter(
                        x=df_lollipop[metrica_lollipop],
                        y=df_lollipop["area"],
                        mode="markers",
                        marker=dict(size=15, color=colores_lollipop),
                        name="Promedio",
                        text=df_lollipop[metrica_lollipop].apply(
                            lambda x: METRICAS_CONFIG[metrica_lollipop][
                                "formato"
                            ].format(x)
                        ),
                        textposition="middle right",
                    )
                )
                fig_lollipop.add_trace(
                    go.Scatter(
                        x=df_lollipop[metrica_lollipop],
                        y=df_lollipop["area"],
                        mode="lines",
                        line=dict(color="gray", width=1),
                        showlegend=False,
                    )
                )
                fig_lollipop.add_vline(
                    x=limite,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Límite: {limite}",
                )
                fig_lollipop.update_layout(
                    title=f"Ranking por Programa - {METRICAS_CONFIG[metrica_lollipop]['nombre']}",
                    template="plotly_white",
                    height=max(400, len(df_lollipop) * 35),
                    xaxis_title=METRICAS_CONFIG[metrica_lollipop]["nombre"],
                    yaxis_title="Programa",
                )
                st.plotly_chart(fig_lollipop, use_container_width=True)

                mostrar_interpretacion_grafica(
                    f"Cómo interpretar el Ranking por Programa en {METRICAS_CONFIG[metrica_lollipop]['nombre']}",
                    f"{cumple_count} de {total} programas ({cumple_count/total*100:.1f}%) cumplen con el estándar ({limite}). {mejor_programa['area']} es la #1 con {METRICAS_CONFIG[metrica_lollipop]['formato'].format(mejor_programa[metrica_lollipop])}. {peor_programa['area']} tiene el valor más bajo.",
                    f"🔹 Los círculos VERDES cumplen con el estándar.\n🔹 Los círculos ROJOS NO cumplen.\n🔹 Los programas más a la DERECHA tienen mejor desempeño.\n🔹 La línea ROJA es el límite de cumplimiento.",
                    f"🎯 Busca qué programas están a la derecha de la línea roja (cumplen) y cuáles a la izquierda (no cumplen).",
                )

    # ================================================================
    # GRÁFICA 7: Barras - Comparación de Métricas por Clase
    # ================================================================
    with st.expander("📊 Gráfica 7: Comparación de Métricas por Clase", expanded=False):
        mostrar_leyenda_grafica(
            "Comparación de Métricas por Clase",
            "¿Cómo se comparan las métricas entre clases ENTRETENIDO y ABURRIDO?",
            "🔹 Cada barra representa el promedio de una métrica.\n🔹 🟢 Verde = ENTRETENIDO (buena calidad).\n🔹 🔴 Rojo = ABURRIDO (mala calidad).\n🔹 Barras más altas = mejor desempeño.",
        )

        metricas_disponibles = [
            "CPM",
            "DME_s",
            "DTE_ratio",
            "Enthusiasm_Score",
            "Tone_CoV",
            "sigma2_IM",
            "Porcentaje_Certeza",
            "Jitter_Score",
            "IMP_promedio",
        ]

        metricas_existentes = [
            col for col in metricas_disponibles if col in df_filtrado.columns
        ]

        if metricas_existentes:
            metrica_seleccionada = st.selectbox(
                "Selecciona una métrica para comparar:",
                options=metricas_existentes,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="bar_clase_metrica",
            )

            df_entretenido = df_filtrado[df_filtrado["Clase_Predicha"] == "ENTRETENIDO"]
            df_aburrido = df_filtrado[df_filtrado["Clase_Predicha"] == "ABURRIDO"]

            prom_entretenido = (
                df_entretenido[metrica_seleccionada].mean()
                if not df_entretenido.empty
                else 0
            )
            prom_aburrido = (
                df_aburrido[metrica_seleccionada].mean() if not df_aburrido.empty else 0
            )

            df_barras = pd.DataFrame(
                {
                    "Clase": ["ENTRETENIDO", "ABURRIDO"],
                    "Promedio": [prom_entretenido, prom_aburrido],
                    "Color": ["#2e7d32", "#c62828"],
                }
            )

            count_entretenido = len(df_entretenido)
            count_aburrido = len(df_aburrido)

            fig_barras = go.Figure()
            fig_barras.add_trace(
                go.Bar(
                    x=df_barras["Clase"],
                    y=df_barras["Promedio"],
                    text=df_barras["Promedio"].apply(lambda x: f"{x:.3f}"),
                    textposition="outside",
                    marker=dict(color=df_barras["Color"]),
                    hovertemplate="<b>%{x}</b><br>Promedio: %{y:.3f}<br>Grabaciones: %{customdata}<extra></extra>",
                    customdata=[count_entretenido, count_aburrido],
                )
            )

            limite = METRICAS_CONFIG[metrica_seleccionada].get("limite_cumple")
            if limite is not None:
                condicion = METRICAS_CONFIG[metrica_seleccionada].get("condicion")
                if condicion == "mayor":
                    fig_barras.add_hline(
                        y=limite,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Límite: {limite}",
                        annotation_position="top right",
                    )
                elif condicion == "menor":
                    fig_barras.add_hline(
                        y=limite,
                        line_dash="dash",
                        line_color="red",
                        annotation_text=f"Límite: {limite}",
                        annotation_position="bottom right",
                    )

            fig_barras.update_layout(
                height=450,
                template="plotly_white",
                xaxis_title="Clase",
                yaxis_title=METRICAS_CONFIG[metrica_seleccionada]["nombre"],
                showlegend=False,
                margin=dict(l=40, r=40, t=30, b=40),
            )

            st.plotly_chart(fig_barras, use_container_width=True)

            diferencia = prom_entretenido - prom_aburrido
            mejor_clase = (
                "ENTRETENIDO" if prom_entretenido > prom_aburrido else "ABURRIDO"
            )
            condicion = METRICAS_CONFIG[metrica_seleccionada]["condicion"]

            if condicion == "mayor" or condicion == "mayor_igual":
                mejor_texto = "mejor (mayor es mejor)"
            elif condicion == "menor" or condicion == "menor_igual":
                mejor_texto = "mejor (menor es mejor)"
            else:
                mejor_texto = "mejor"

            que_muestra = f"Este gráfico compara el promedio de {METRICAS_CONFIG[metrica_seleccionada]['nombre']} entre clases ENTRETENIDO y ABURRIDO. Los ENTRETENIDOS tienen un promedio de {prom_entretenido:.3f} ({count_entretenido} grabaciones) y los ABURRIDOS de {prom_aburrido:.3f} ({count_aburrido} grabaciones). La diferencia es de {diferencia:+.3f}."

            if diferencia > 0:
                que_muestra += (
                    f" Los ENTRETENIDOS tienen mejor desempeño en esta métrica."
                )
            else:
                que_muestra += f" Los ABURRIDOS tienen mejor desempeño en esta métrica."

            como_leer = f"🔹 Cada barra = promedio de la métrica.\n🔹 🟢 Verde = ENTRETENIDO.\n🔹 🔴 Rojo = ABURRIDO.\n🔹 La línea roja = límite de cumplimiento (si existe).\n🔹 Barras más altas = mejor desempeño (para métricas donde 'mayor es mejor')."

            que_buscar = f"🎯 Busca:\n🔹 La diferencia entre las dos barras.\n🔹 Qué clase está por encima del límite (línea roja).\n🔹 {mejor_clase} es la clase con {mejor_texto}."

            mostrar_interpretacion_grafica(
                f"Cómo interpretar la Comparación de {METRICAS_CONFIG[metrica_seleccionada]['nombre']} por Clase",
                que_muestra,
                como_leer,
                que_buscar,
            )
        else:
            st.warning("⚠️ No hay métricas disponibles para comparar.")


# ================================================================
# EJECUCIÓN
# ================================================================

if __name__ == "__main__":
    main()
