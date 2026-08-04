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
# CONFIGURACIÓN DE MÉTRICAS (SIN Porcentaje_Certeza)
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
    # "Porcentaje_Certeza": {   # ELIMINADA
    #     "nombre": "Certeza",
    #     "columna": "Porcentaje_Certeza",
    #     "unidad": "%",
    #     "formato": "{:.1f}%",
    #     "tipo": "mayor",
    #     "meta": 50.0,
    #     "limite_cumple": 50,
    #     "condicion": "mayor",
    # },
}

# ================================================================
# FUNCIONES AUXILIARES PARA CÁLCULO DE CUMPLIMIENTO
# ================================================================


def calcular_cumplimiento(valor, config):
    """Calcula el porcentaje de cumplimiento según el tipo de métrica"""
    if pd.isna(valor):
        return 0.0

    tipo = config.get("tipo")
    if tipo == "mayor":
        meta = config.get("meta")
        if meta is None or meta == 0:
            return 0.0
        if valor >= meta:
            return 100.0
        else:
            return min((valor / meta) * 100, 100.0)

    elif tipo == "menor":
        meta = config.get("meta")
        if meta is None or meta == 0 or valor == 0:
            return 0.0
        if valor <= meta:
            return 100.0
        else:
            return min((meta / valor) * 100, 100.0)

    elif tipo == "rango":
        min_val = config.get("min", 0)
        max_val = config.get("max", float("inf"))
        if min_val <= valor <= max_val:
            return 100.0
        else:
            return 0.0

    else:
        return 0.0


def obtener_estado(pct):
    """Devuelve el estado según el porcentaje de cumplimiento"""
    if pct >= 100:
        return "✅ Cumple"
    elif pct >= 70:
        return "⚠️ Parcial"
    else:
        return "❌ Requiere mejora"


# ================================================================
# FUNCIÓN VERIFICAR CUMPLIMIENTO (para compatibilidad)
# ================================================================


def verificar_cumplimiento(valor, limite, condicion):
    """Función original para las gráficas 2, 3, 5, 6, 7 (ya no se usa pero se mantiene)"""
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


# ================================================================
# FUNCIONES DE VISUALIZACIÓN
# ================================================================


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
            "Métrica": "Duración del monólogo",
            "Columna": "DME_s",
            "¿Qué mide?": "Tiempo promedio que el docente habla sin interrupción. Mide la capacidad de mantener la atención del estudiante.",
            "¿Cómo se mide?": "Se calcula el promedio de los segmentos de habla continua del docente.",
            "Unidad": "segundos",
            "Meta": "< 3.5",
            "Tipo": "Menor es mejor",
        },
        {
            "Métrica": "Porcentaje de habla",
            "Columna": "DTE_ratio",
            "¿Qué mide?": "Relación entre el tiempo que habla el docente y el tiempo total de la grabación.",
            "¿Cómo se mide?": "Tiempo hablado por el docente / duración total de la grabación.",
            "Unidad": "adimensional",
            "Meta": "≤ 0.5",
            "Tipo": "Rango (0.0 - 0.5)",
        },
        {
            "Métrica": "Estabilidad técnica",
            "Columna": "Jitter_Score",
            "¿Qué mide?": "Estabilidad de la voz del docente. Mide fluidez y naturalidad del discurso.",
            "¿Cómo se mide?": "Variación de la frecuencia fundamental de la voz. Valores más altos = mayor estabilidad.",
            "Unidad": "adimensional",
            "Meta": "> 0.4",
            "Tipo": "Mayor es mejor",
        },
        {
            "Métrica": "Movimiento promedio",
            "Columna": "IMP_promedio",
            "¿Qué mide?": "Cantidad de movimiento corporal del docente. Mide dinamismo y energía en la clase.",
            "¿Cómo se mide?": "Se calcula el promedio de movimiento del docente a través de la grabación.",
            "Unidad": "adimensional",
            "Meta": "> 4.0",
            "Tipo": "Mayor es mejor",
        },
        {
            "Métrica": "Cambios de movimiento",
            "Columna": "sigma2_IM",
            "¿Qué mide?": "Variación en el movimiento corporal. Mide consistencia y ritmo del docente.",
            "¿Cómo se mide?": "Desviación estándar del movimiento a lo largo de la grabación.",
            "Unidad": "adimensional",
            "Meta": "> 8.5",
            "Tipo": "Mayor es mejor",
        },
        {
            "Métrica": "Variación de la voz",
            "Columna": "Tone_CoV",
            "¿Qué mide?": "Variación del tono de voz del docente. Mide expresividad y capacidad de mantener el interés.",
            "¿Cómo se mide?": "Coeficiente de variación del tono a lo largo de la grabación.",
            "Unidad": "adimensional",
            "Meta": "> 0.32",
            "Tipo": "Mayor es mejor",
        },
        {
            "Métrica": "Nivel de energía",
            "Columna": "Enthusiasm_Score",
            "¿Qué mide?": "Nivel de entusiasmo y energía del docente. Mide engagement con los estudiantes.",
            "¿Cómo se mide?": "Algoritmo de análisis de audio que detecta patrones de entusiasmo en la voz.",
            "Unidad": "adimensional",
            "Meta": "> 0.15",
            "Tipo": "Mayor es mejor",
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
            "Meta": st.column_config.TextColumn("Meta", width="small"),
            "Tipo": st.column_config.TextColumn("Tipo", width="medium"),
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

    # ================================================================
    # 🆕 FILTRO DE CLASE (ENTRETENIDO / ABURRIDO)
    # ================================================================
    if "Clase_Predicha" in df_filtrado.columns:
        clases_disponibles = sorted(df_filtrado["Clase_Predicha"].dropna().unique())
        if len(clases_disponibles) > 0:
            st.markdown("### 🎯 Filtrar por Clase")
            col_filtro1, col_filtro2 = st.columns([1, 3])
            with col_filtro1:
                opcion_clase = st.selectbox(
                    "Seleccionar clase:",
                    options=["Todas"] + clases_disponibles,
                    key="filtro_clase_profundidad",
                )
            if opcion_clase != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Clase_Predicha"] == opcion_clase]
                st.success(f"✅ Mostrando solo clases: **{opcion_clase}**")
            else:
                st.info("📊 Mostrando **todas** las clases")
        else:
            st.info("📊 No hay clases disponibles para filtrar.")
    else:
        st.warning("⚠️ La columna 'Clase_Predicha' no existe en los datos.")

    st.info(f"📊 Mostrando {len(df_filtrado)} registros con los filtros aplicados")

    # ================================================================
    # 📋 DICCIONARIO DE MÉTRICAS (visible por defecto)
    # ================================================================
    mostrar_tabla_metricas()

    # ================================================================
    # 📊 RESUMEN EJECUTIVO (con tarjetas de Aburridas/Entretenidas)
    # ================================================================
    st.subheader("📊 Resumen Ejecutivo")

    # ---- Contar clases (BUSCANDO EN MAYÚSCULAS) ----
    clases_counts = {}
    if "Clase_Predicha" in df_filtrado.columns:
        clases_counts = df_filtrado["Clase_Predicha"].value_counts().to_dict()
        # 🔥 CAMBIO AQUÍ: buscamos "ABURRIDO" y "ENTRETENIDO" en mayúsculas
        aburridos = clases_counts.get("ABURRIDO", 0)
        entretenidos = clases_counts.get("ENTRETENIDO", 0)
    else:
        aburridos = 0
        entretenidos = 0

    # ---- Mostrar 6 tarjetas ----
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total Grabaciones", len(df_filtrado))

    with col2:
        total_docentes = (
            df_filtrado["nombres_apellidos"].nunique()
            if "nombres_apellidos" in df_filtrado.columns
            else 0
        )
        st.metric("Total Docentes", total_docentes)

    with col3:
        total_programas = (
            df_filtrado["area"].nunique() if "area" in df_filtrado.columns else 0
        )
        st.metric("Total Programas", total_programas)

    with col4:
        total_materias = (
            df_filtrado["nom_materia"].nunique()
            if "nom_materia" in df_filtrado.columns
            else 0
        )
        st.metric("Total Materias", total_materias)

    with col5:
        st.metric("😴 Aburridas", aburridos)

    with col6:
        st.metric("🎉 Entretenidas", entretenidos)

    # ---- Continuar con el resto del código ----
    metricas_disp = [
        col for col in METRICAS_CONFIG.keys() if col in df_filtrado.columns
    ]

    # ================================================================
    # ➕ AÑADIR COLUMNAS DE CUMPLIMIENTO (en %)
    # ================================================================
    for col in metricas_disp:
        config = METRICAS_CONFIG[col]
        df_filtrado[f"{col}_cumplimiento"] = df_filtrado[col].apply(
            lambda x: calcular_cumplimiento(x, config)
        )

    # ================================================================
    # GRÁFICA 1: Radar Chart basado en CUMPLIMIENTO
    # ================================================================
    with st.expander(
        "🕸️ Gráfica 1: Radar de Cumplimiento - Perfil del Docente vs Estándares",
        expanded=True,
    ):
        mostrar_leyenda_grafica(
            "Perfil de Cumplimiento del Docente",
            "¿Qué indicadores cumple el docente según los estándares definidos? ¿Cuáles debe mejorar?",
            "🔹 Cada eje representa el **% de cumplimiento** de una métrica.\n🔹 100% = cumple o supera la meta.\n🔹 70-99% = cerca de la meta (parcial).\n🔹 <70% = necesita mejora.\n🔹 El área sombreada muestra el perfil de cumplimiento del docente.",
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

                # Calcular promedios del docente para cada métrica
                promedios_docente = {}
                for col in metricas_disp:
                    if col in df_docente.columns:
                        promedios_docente[col] = df_docente[col].mean()
                    else:
                        promedios_docente[col] = np.nan

                # Construir tabla de evaluación
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
                    # Definir meta en texto
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
                            "Tipo": config["tipo"].capitalize(),
                            "% Cumplimiento": f"{pct:.1f}%",
                            "Estado": estado,
                        }
                    )
                    nombres_metricas.append(config["nombre"])
                    valores_cumplimiento.append(pct)

                # Mostrar tabla de evaluación
                if datos_tabla:
                    st.markdown(f"### 📊 Evaluación de {docente_seleccionado}")
                    df_tabla = pd.DataFrame(datos_tabla)
                    st.dataframe(
                        df_tabla,
                        column_config={
                            "Indicador": "Indicador",
                            "Valor": "Valor",
                            "Meta": "Meta",
                            "Tipo": "Tipo",
                            "% Cumplimiento": st.column_config.TextColumn(
                                "% Cumplimiento"
                            ),
                            "Estado": st.column_config.TextColumn("Estado"),
                        },
                        hide_index=True,
                        use_container_width=True,
                    )

                    # Radar de cumplimiento
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
                            ),
                            angularaxis=dict(tickfont=dict(size=10)),
                        ),
                        title=f"Perfil de Cumplimiento de {docente_seleccionado}",
                        height=550,
                        template="plotly_white",
                        showlegend=False,
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)

                    # Interpretación
                    promedio_cumplimiento = np.mean(valores_cumplimiento)
                    max_idx = np.argmax(valores_cumplimiento)
                    min_idx = np.argmin(valores_cumplimiento)
                    fortaleza = nombres_metricas[max_idx]
                    debilidad = nombres_metricas[min_idx]
                    cumple_count = sum(1 for p in valores_cumplimiento if p >= 100)
                    total = len(valores_cumplimiento)

                    mostrar_interpretacion_grafica(
                        f"Cómo interpretar el Radar de Cumplimiento de {docente_seleccionado}",
                        f"Este radar muestra el cumplimiento de {docente_seleccionado} en {total} indicadores. "
                        f"El promedio de cumplimiento es {promedio_cumplimiento:.1f}%. "
                        f"Cumple {cumple_count} de {total} indicadores al 100%. "
                        f"Su fortaleza es {fortaleza} ({valores_cumplimiento[max_idx]:.1f}%) "
                        f"y su área de mejora es {debilidad} ({valores_cumplimiento[min_idx]:.1f}%).",
                        f"🔹 Cada eje representa un indicador.\n"
                        f"🔹 100% = cumple la meta (zona verde).\n"
                        f"🔹 70-99% = se acerca a la meta (zona amarilla).\n"
                        f"🔹 <70% = necesita mejora (zona roja).\n"
                        f"🔹 El área sombreada muestra el perfil de cumplimiento.",
                        f"🎯 Busca los ejes que llegan al 100% (cumple) y los que están por debajo (áreas de mejora). "
                        f"Presta atención a {debilidad} que tiene el menor cumplimiento.",
                    )
                else:
                    st.warning("⚠️ No hay datos de métricas para este docente.")
            else:
                st.warning("⚠️ No hay docentes en los datos filtrados.")
        else:
            st.warning("⚠️ No se encontraron las columnas necesarias para el radar.")

    # ================================================================
    # GRÁFICA 2: Mapa de Calor - Cumplimiento por Docente y Programa
    # ================================================================
    with st.expander(
        "🔥 Gráfica 2: Mapa de Calor - Cumplimiento por Docente y Programa",
        expanded=False,
    ):
        mostrar_leyenda_grafica(
            "Cumplimiento por Docente y Programa",
            "¿Qué docentes cumplen mejor los estándares en cada programa?",
            "🔹 Cada fila = un docente.\n🔹 Cada columna = un programa.\n🔹 El color indica el **% de cumplimiento** promedio de la métrica seleccionada.\n🔹 Verde = alto cumplimiento, Rojo = bajo cumplimiento.",
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

            col_cumplimiento = f"{metrica_heatmap}_cumplimiento"

            df_heatmap = df_filtrado.pivot_table(
                index="nombres_apellidos",
                columns="area",
                values=col_cumplimiento,
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
                    title=f"Mapa de Calor: % de Cumplimiento de {METRICAS_CONFIG[metrica_heatmap]['nombre']} por Docente y Programa",
                    color_continuous_scale="RdYlGn",
                    aspect="auto",
                    text_auto=True,
                    labels={
                        "x": "Programa",
                        "y": "Docente",
                        "color": "% Cumplimiento",
                    },
                    range_color=[0, 100],
                )

                height = max(400, len(df_heatmap) * 25)
                fig_heatmap.update_layout(
                    template="plotly_white",
                    height=height,
                    xaxis=dict(tickangle=45),
                    yaxis=dict(tickfont=dict(size=10)),
                )
                fig_heatmap.update_traces(
                    texttemplate="%{z:.1f}%",
                    textfont=dict(size=10, color="black"),
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

                que_muestra = f"Este mapa de calor muestra el cumplimiento de {len(df_heatmap)} docentes en {len(df_heatmap.columns)} programas, medido por {METRICAS_CONFIG[metrica_heatmap]['nombre']}. Los colores VERDES indican alto cumplimiento (≥70%) y ROJOS bajo cumplimiento (<70%)."

                if max_docente != "N/A":
                    que_muestra += f" El mejor cumplimiento es de {max_docente} en {max_programa} con {max_cell:.1f}%. El peor es {min_docente} en {min_programa} con {min_cell:.1f}%."

                if mejor_docente != "N/A":
                    que_muestra += f" {mejor_docente} es el docente con mejor promedio ({mejor_valor:.1f}%) y {peor_docente} el de menor ({peor_valor:.1f}%)."

                if mejor_programa != "N/A":
                    que_muestra += f" {mejor_programa} es el programa con mejor cumplimiento y {peor_programa} el de menor."

                como_leer = f"🔹 Cada FILA = un docente.\n🔹 Cada COLUMNA = un programa.\n🔹 COLOR:\n   🟢 Verde = alto cumplimiento (≥70%)\n   🟡 Amarillo = cumplimiento medio (40-70%)\n   🔴 Rojo = bajo cumplimiento (<40%)\n🔹 Docentes ordenados de mejor a peor promedio (arriba = mejores)."

                que_buscar = f"🎯 Busca:\n🔹 Filas VERDES completas → docentes excelentes en todo.\n🔹 Columnas VERDES completas → programas con buen cumplimiento.\n🔹 Celdas ROJAS → áreas de mejora específicas."

                if mejor_docente != "N/A":
                    que_buscar += f"\n🔹 {mejor_docente} es el mejor docente promedio."
                if peor_docente != "N/A":
                    que_buscar += f"\n🔹 {peor_docente} necesita mejorar."
                if mejor_programa != "N/A":
                    que_buscar += (
                        f"\n🔹 {mejor_programa} es el programa con mejor cumplimiento."
                    )

                mostrar_interpretacion_grafica(
                    f"Cómo interpretar el Mapa de Calor de Cumplimiento de {METRICAS_CONFIG[metrica_heatmap]['nombre']} por Docente y Programa",
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
    # GRÁFICA 3: Barras Horizontales - Ranking de Programas por Cumplimiento
    # ================================================================
    with st.expander(
        "📊 Gráfica 3: Ranking de Programas por Cumplimiento", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Ranking de Programas por Cumplimiento",
            "¿Qué programas tienen mayor porcentaje de cumplimiento en cada métrica?",
            "🔹 Cada barra representa el **% de cumplimiento promedio** de un programa.\n🔹 La línea roja marca el 70% (umbral de cumplimiento).\n🔹 Barras verdes = cumplen (>70%), rojas = no cumplen (<70%).",
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
                .sort_values(col_cumplimiento, ascending=True)
            )

            if not df_area.empty:
                cumple_count = sum(
                    1 for _, row in df_area.iterrows() if row[col_cumplimiento] >= 70
                )
                total = len(df_area)
                mejor_programa = df_area.loc[df_area[col_cumplimiento].idxmax(), "area"]
                peor_programa = df_area.loc[df_area[col_cumplimiento].idxmin(), "area"]
                promedio = df_area[col_cumplimiento].mean()

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
                    title=f"Ranking de Programas - % Cumplimiento de {METRICAS_CONFIG[metrica_bar_h]['nombre']}",
                    template="plotly_white",
                    height=max(400, len(df_area) * 40),
                    xaxis_title="% Cumplimiento",
                    yaxis_title="Programa",
                    xaxis=dict(range=[0, 100]),
                )
                st.plotly_chart(fig_bar_h, use_container_width=True, key="ranking_3")

                mostrar_interpretacion_grafica(
                    f"Cómo interpretar el Ranking de Programas por Cumplimiento en {METRICAS_CONFIG[metrica_bar_h]['nombre']}",
                    f"{cumple_count} de {total} programas ({cumple_count/total*100:.1f}%) superan el 70% de cumplimiento. El promedio general es {promedio:.1f}%. {mejor_programa} es el programa con mejor cumplimiento y {peor_programa} el peor.",
                    f"🔹 Las barras VERDES superan el 70% (cumplen).\n🔹 Las barras ROJAS están por debajo del 70% (no cumplen).\n🔹 Barras más largas = mayor cumplimiento.",
                    f"🎯 Busca qué programas están a la derecha del 70% (cumplen) y cuáles a la izquierda (no cumplen). {mejor_programa} es el programa con mejor cumplimiento.",
                )

    # ================================================================
    # GRÁFICA 4: Barras Verticales - Distribución por Programa (sin cambios, es conteo)
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
            clases_presentes = df_area_clase["Clase_Predicha"].unique()
            if len(clases_presentes) > 0:
                df_area_clase = df_area_clase[
                    df_area_clase["Clase_Predicha"].isin(clases_presentes)
                ]
            else:
                df_area_clase = pd.DataFrame()

            if not df_area_clase.empty:
                color_map = {}
                for clase in clases_presentes:
                    if clase.upper() == "ENTRETENIDO":
                        color_map[clase] = "#2e7d32"
                    elif clase.upper() == "ABURRIDO":
                        color_map[clase] = "#c62828"
                    else:
                        color_map[clase] = "#1f77b4"

                fig_bar_v = px.bar(
                    df_area_clase,
                    x="area",
                    y="count",
                    color="Clase_Predicha",
                    color_discrete_map=color_map,
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

                total_entretenido = (
                    df_area_clase[
                        df_area_clase["Clase_Predicha"].str.upper() == "ENTRETENIDO"
                    ]["count"].sum()
                    if "ENTRETENIDO" in [c.upper() for c in clases_presentes]
                    else 0
                )
                total_aburrido = (
                    df_area_clase[
                        df_area_clase["Clase_Predicha"].str.upper() == "ABURRIDO"
                    ]["count"].sum()
                    if "ABURRIDO" in [c.upper() for c in clases_presentes]
                    else 0
                )
                total = total_entretenido + total_aburrido
                pct_entretenido = (total_entretenido / total) * 100 if total > 0 else 0

                mejor_programa = "N/A"
                peor_programa = "N/A"
                if total_entretenido > 0:
                    df_entretenido = df_area_clase[
                        df_area_clase["Clase_Predicha"].str.upper() == "ENTRETENIDO"
                    ]
                    if not df_entretenido.empty:
                        mejor_programa = df_entretenido.loc[
                            df_entretenido["count"].idxmax(), "area"
                        ]
                if total_aburrido > 0:
                    df_aburrido = df_area_clase[
                        df_area_clase["Clase_Predicha"].str.upper() == "ABURRIDO"
                    ]
                    if not df_aburrido.empty:
                        peor_programa = df_aburrido.loc[
                            df_aburrido["count"].idxmax(), "area"
                        ]

                mostrar_interpretacion_grafica(
                    "Cómo interpretar la Distribución de Grabaciones por Programa",
                    f"De {total} grabaciones, {total_entretenido} ({pct_entretenido:.1f}%) son ENTRETENIDAS y {total_aburrido} ({100-pct_entretenido:.1f}%) son ABURRIDAS. {mejor_programa} tiene más clases ENTRETENIDAS. {peor_programa} tiene más clases ABURRIDAS.",
                    f"🔹 Cada barra representa un programa.\n🔹 VERDE = clases ENTRETENIDAS.\n🔹 ROJO = clases ABURRIDAS.\n🔹 Más VERDE que ROJO = programa con buena calidad.",
                    f"🎯 Busca programas con más VERDE que ROJO (buena calidad). Los programas con mucho ROJO necesitan mejorar.",
                )
            else:
                st.warning("⚠️ No hay datos de clases para mostrar.")
        else:
            st.warning("⚠️ No se encontraron las columnas 'area' o 'Clase_Predicha'.")

    # ================================================================
    # GRÁFICA 5: Desviación del Promedio de Cumplimiento
    # ================================================================
    with st.expander(
        "🌊 Gráfica 5: Desviación del Promedio de Cumplimiento", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Desviación de Docentes del Promedio de Cumplimiento",
            "¿Qué docentes están por encima o por debajo del promedio de cumplimiento?",
            "🔹 Barras verdes = por encima del promedio (mejor).\n🔹 Barras rojas = por debajo del promedio (peor).\n🔹 La línea vertical en 0 es el promedio.",
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
            if not df_water.empty:
                promedio_general = df_water[col_cumplimiento].mean()
                df_water["desviacion"] = df_water[col_cumplimiento] - promedio_general
                df_water = df_water.sort_values("desviacion", ascending=True)

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
                        text=df_water["desviacion"].apply(lambda x: f"{x:+.1f}%"),
                        textposition="outside",
                    )
                )
                fig_water.add_vline(x=0, line_dash="dash", line_color="gray")
                fig_water.update_layout(
                    title=f"Desviación del Promedio de Cumplimiento - {METRICAS_CONFIG[metrica_water]['nombre']}",
                    template="plotly_white",
                    height=max(400, len(df_water) * 35),
                    xaxis_title="Desviación (puntos porcentuales)",
                    yaxis_title="Docente",
                )
                st.plotly_chart(fig_water, use_container_width=True)

                mostrar_interpretacion_grafica(
                    f"Cómo interpretar la Desviación del Promedio de Cumplimiento en {METRICAS_CONFIG[metrica_water]['nombre']}",
                    f"El promedio de cumplimiento general es {promedio_general:.1f}%. {encima} docentes están por encima y {debajo} por debajo. {mejor['nombres_apellidos']} es el mejor con {mejor[col_cumplimiento]:.1f}% de cumplimiento. {peor['nombres_apellidos']} es el peor con {peor[col_cumplimiento]:.1f}%.",
                    f"🔹 Las barras VERDES están por ENCIMA del promedio (mejor cumplimiento).\n🔹 Las barras ROJAS están por DEBAJO del promedio (peor cumplimiento).\n🔹 La línea vertical en 0 es el PROMEDIO.",
                    f"🎯 Busca los docentes con barras más largas a la derecha (mejores) y a la izquierda (peores).",
                )
            else:
                st.warning("⚠️ No hay datos de docentes para calcular desviación.")
        else:
            st.warning("⚠️ No se encontraron columnas necesarias.")

    # ================================================================
    # GRÁFICA 7: Comparación de Cumplimiento por Clase
    # ================================================================
    with st.expander(
        "📊 Gráfica 7: Comparación de Cumplimiento por Clase", expanded=False
    ):
        mostrar_leyenda_grafica(
            "Comparación de Cumplimiento por Clase",
            "¿Cómo se compara el cumplimiento entre clases ENTRETENIDO y ABURRIDO?",
            "🔹 Cada barra representa el **% de cumplimiento promedio** de una métrica.\n🔹 🟢 Verde = ENTRETENIDO.\n🔹 🔴 Rojo = ABURRIDO.\n🔹 Barras más altas = mejor cumplimiento.",
        )

        # Lista de métricas SIN Porcentaje_Certeza
        metricas_disponibles = [
            "DME_s",
            "DTE_ratio",
            "Enthusiasm_Score",
            "Tone_CoV",
            "sigma2_IM",
            # "Porcentaje_Certeza",  # ELIMINADA
            "Jitter_Score",
            "IMP_promedio",
        ]

        metricas_existentes = [
            col for col in metricas_disponibles if col in df_filtrado.columns
        ]

        if metricas_existentes and "Clase_Predicha" in df_filtrado.columns:
            metrica_seleccionada = st.selectbox(
                "Selecciona una métrica para comparar:",
                options=metricas_existentes,
                format_func=lambda x: METRICAS_CONFIG[x]["nombre"],
                key="bar_clase_metrica",
            )
            col_cumplimiento = f"{metrica_seleccionada}_cumplimiento"

            clases_unicas = df_filtrado["Clase_Predicha"].dropna().unique()

            if len(clases_unicas) >= 2:
                clase1 = clases_unicas[0]
                clase2 = clases_unicas[1] if len(clases_unicas) > 1 else clase1

                df_clase1 = df_filtrado[df_filtrado["Clase_Predicha"] == clase1]
                df_clase2 = df_filtrado[df_filtrado["Clase_Predicha"] == clase2]

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
                        hovertemplate="<b>%{x}</b><br>% Cumplimiento: %{y:.1f}%<br>Grabaciones: %{customdata}<extra></extra>",
                        customdata=counts,
                    )
                )

                fig_barras.add_hline(
                    y=70,
                    line_dash="dash",
                    line_color="red",
                    line_width=2,
                    annotation_text="Umbral 70%",
                    annotation_position="top right",
                )

                fig_barras.update_layout(
                    height=450,
                    template="plotly_white",
                    xaxis_title="Clase",
                    yaxis_title="% Cumplimiento",
                    showlegend=False,
                    margin=dict(l=40, r=40, t=30, b=40),
                    yaxis=dict(range=[0, 100]),
                )

                st.plotly_chart(fig_barras, use_container_width=True)

                diferencia = prom_clase1 - prom_clase2
                mejor_clase = clase1 if prom_clase1 > prom_clase2 else clase2

                que_muestra = f"Este gráfico compara el cumplimiento promedio de {METRICAS_CONFIG[metrica_seleccionada]['nombre']} entre las clases {clase1} y {clase2}. La clase {clase1} tiene {prom_clase1:.1f}% de cumplimiento ({counts[0]} grabaciones) y {clase2} tiene {prom_clase2:.1f}% ({counts[1]} grabaciones). La diferencia es de {diferencia:+.1f} puntos porcentuales."

                como_leer = f"🔹 Cada barra = % de cumplimiento promedio.\n🔹 🟢 Verde = {clase1}.\n🔹 🔴 Rojo = {clase2}.\n🔹 La línea roja = umbral del 70%."

                que_buscar = f"🎯 Busca la diferencia entre las barras y qué clase supera el 70%. {mejor_clase} es la clase con mejor cumplimiento."

                mostrar_interpretacion_grafica(
                    f"Cómo interpretar la Comparación de Cumplimiento de {METRICAS_CONFIG[metrica_seleccionada]['nombre']} por Clase",
                    que_muestra,
                    como_leer,
                    que_buscar,
                )
            else:
                st.info(
                    f"⚠️ Solo hay una clase disponible: {clases_unicas[0]}. No se puede comparar."
                )
        else:
            st.warning(
                "⚠️ No hay métricas disponibles o no existe la columna 'Clase_Predicha'."
            )

    # ================================================================
    # 📋 TABLA DE RECOMENDACIONES (NUEVA)
    # ================================================================
    with st.expander("📋 Tabla de recomendaciones por docente", expanded=True):
        mostrar_tabla_recomendaciones()


def mostrar_tabla_recomendaciones():
    """
    Muestra una tabla con las columnas 'nombres_apellidos' y 'recomen_falencia'
    a partir de los datos filtrados en session_state. Incluye botón de descarga CSV.
    """
    # Obtener los datos ya filtrados (desde el sidebar)
    df = get_filtrado_data()

    # Verificar que existan las columnas necesarias
    columnas_requeridas = ["nombres_apellidos", "recomen_falencia"]
    for col in columnas_requeridas:
        if col not in df.columns:
            st.error(f"❌ La columna '{col}' no existe en los datos filtrados.")
            return

    # Crear el DataFrame con solo esas dos columnas
    df_tabla = df[columnas_requeridas].copy()

    # Mostrar el título y cantidad de registros
    st.subheader("📋 Tabla de Recomendaciones por Docente")
    st.info(f"📊 Mostrando {len(df_tabla)} registros con los filtros aplicados")

    # Mostrar la tabla interactiva
    st.dataframe(
        df_tabla,
        column_config={
            "nombres_apellidos": "Docente",
            "recomen_falencia": "Recomendación",
        },
        use_container_width=True,
        hide_index=True,
    )

    # Botón para descargar CSV (para imprimir o guardar)
    csv = df_tabla.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar CSV (para imprimir)",
        data=csv,
        file_name="recomendaciones_docentes.csv",
        mime="text/csv",
        help="Descarga el archivo CSV que puedes abrir en Excel o imprimir.",
    )


# ================================================================
# EJECUCIÓN
# ================================================================

if __name__ == "__main__":
    main()
