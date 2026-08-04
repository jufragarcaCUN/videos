"""
Dashboard - Presentación
Página de introducción y explicación del dashboard
"""

import warnings
import streamlit as st

warnings.filterwarnings("ignore")


# ==================== MAIN ====================
def main(df_filtrado=None):
    st.header("🎓 Bienvenido al Dashboard de Análisis Académico")

    st.markdown(
        """
    <div style="background: linear-gradient(135deg, #1a5276, #2e86c1); 
                padding: 30px; 
                border-radius: 15px; 
                text-align: center; 
                color: white;
                margin-bottom: 30px;">
        <h2 style="margin: 0;">📊 Inteligencia Académica CUN</h2>
        <p style="margin: 10px 0 0 0; font-size: 1.1rem;">
            Analizando la calidad de las grabaciones académicas a través de métricas avanzadas
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ====================================================================
    # DICCIONARIO DE MÉTRICAS (MODELOS)
    # ====================================================================
    with st.expander(
        "📊 Diccionario de Métricas - ¿Qué mide cada modelo?", expanded=True
    ):
        st.markdown("""
        ### 📋 Cada métrica mide un aspecto diferente de la clase:

        ---

        **📌 DME_s - Duración del Monólogo**  
        *"¿El profesor habla mucho tiempo seguido sin pausar?"*  
        Mide el **tiempo continuo máximo de voz activa sin pausas**.  
        • **Rango:** 0.0 a 120.0+ segundos  
        🟢 **Bueno:** < 3.5   
        🔴 **Malo:** > 3.5 

        ---

        **📌 DTE_ratio - Porcentaje de habla**  
        *"¿Cuánto espacio de la clase ocupa la voz del docente?"*  
        Mide la **proporción del tiempo total del video con voz activa**.  
        • **Rango:** 0.0 a 1.0 (0% a 100%)  
        🟢 **Bueno:** ≤ 0.50 (clase interactiva, da tiempo a preguntas o práctica)  
        🔴 **Malo:** > 0.50 (clase predominantemente expositiva)

        ---

        **📌 Tone_CoV - Variación de la voz (Modulación)**  
        *"¿La voz del profesor es monótona o expresiva?"*  
        Mide el **coeficiente de variación del tono de voz (pitch)**.  
        • **Rango:** 0.0 a 1.0  
        🟢 **Bueno:** > 0.32 (voz dinámica, buena modulación y énfasis)  
        🔴 **Malo:** < 0.32 (voz plana, monótona)

        ---

        **📌 Enthusiasm_Score - Nivel de energía**  
        *"¿Con qué fuerza e intensidad habla el docente?"*  
        Mide el **rango dinámico e intensidad acústica en la voz**.  
        • **Rango:** 0.0 a 1.0  
        🟢 **Bueno:** > 0.15 (clase energética, voz entusiasta)  
        🔴 **Malo:** < 0.15 (falta de energía, voz baja o cansada)

        ---

        **📌 IMP_promedio - Movimiento promedio**  
        *"¿El profesor se mueve o gesticula en pantalla?"*  
        Mide la **cantidad de movimiento corporal o cambios en encuadre**.  
        • **Rango:** 0.0 a 10.0+  
        🟢 **Bueno:** > 4.0 (movimiento activo y gesticulación)  
        🔴 **Malo:** < 4.0 (docente estático frente a la cámara)

        ---

        **📌 sigma2_IM - Cambios de ritmo de movimiento**  
        *"¿Los movimientos varían entre pausa y dinamismo?"*  
        Mide la **variabilidad temporal de la cantidad de movimiento**.  
        • **Rango:** 0.0 a 20.0+  
        🟢 **Bueno:** > 8.5 (ritmo cambiante, pausa y dinamismo natural)  
        🔴 **Malo:** < 8.5 (movimiento rígido o monótono)

        ---

        **📌 Jitter_Score - Estabilidad técnica**  
        *"¿El video se reproduce de forma fluida?"*  
        Mide la **ausencia de tirones, saltos de cuadro o inestabilidad gráfica**.  
        • **Rango:** 0.0 a 1.0  
        🟢 **Bueno:** > 0.4 (grabación limpia y estable)  
        🔴 **Malo:** < 0.4 (video inestable, dificulta la visualización)

        ---
        """)

    # ====================================================================
    # GUÍA DE INTERPRETACIÓN DE GRÁFICOS
    # ====================================================================
    with st.expander("📈 ¿Cómo interpretar los gráficos?", expanded=True):
        st.markdown("""
        ### 🎯 Cada gráfico en el dashboard responde preguntas específicas:

        ---

        **📊 Visión General**  
        *"¿Cómo se comparan los docentes, áreas y materias en cada métrica?"*  
        - **Barras verticales** = valor promedio de cada elemento (docente/área/materia)
        - **Línea roja** = límite de cumplimiento (bueno/malo)
        - **Color de las barras**: 
          - 🟢 Verde = cumple con el límite
          - 🔴 Rojo = no cumple con el límite

        ---

        **📈 Análisis Profundo**  
        *"¿Qué patrones existen en los datos? ¿Qué métricas afectan la clasificación?"*  
        - **Tablero de Cumplimiento**: cards con el resumen de cuántos cumplen por métrica
        - **Heatmap**: mapa de calor verde/rojo mostrando patrones de cumplimiento
        - **Top Performers**: lista de los mejores en cada métrica
        - **Perfil de Docentes**: barras que muestran el desempeño de cada docente
        - **Distribución de Clases**: compara ENTRETENIDO vs ABURRIDO
        - **Correlación**: muestra qué métrica predice mejor la clasificación

        ---

        **📖 Presentación**  
        *"¿Qué estamos evaluando y cómo?"*  
        - Explicación de cada métrica
        - Guía de interpretación de gráficos
        - Resumen del dashboard
        """)

    # ====================================================================
    # GUÍA DE NAVEGACIÓN
    # ====================================================================
    with st.expander("🧭 ¿Cómo navegar el dashboard?", expanded=True):
        st.markdown("""
        ### 📌 Pestañas disponibles:

        | Pestaña | ¿Qué encontrarás? | ¿Para qué sirve? |
        |---------|-------------------|------------------|
        | **📖 Presentación** | Explicación de métricas y guía de uso | Entender qué estamos evaluando |
        | **📊 Visión General** | Gráficas de barras por docente, área y materia | Comparar rápidamente el desempeño |
        | **📈 Análisis Profundo** | Análisis detallado, cumplimiento, heatmap, top performers | Identificar patrones y oportunidades de mejora |
        | **📋 Verificación** | Datos crudos del Excel | Validar que los datos cargaron correctamente |

        ### 🎯 Filtros disponibles:

        | Filtro | Ubicación | ¿Qué hace? |
        |--------|-----------|------------|
        | **📚 Área** | Sidebar izquierdo | Filtra por área académica |
        | **👨‍🏫 Docente** | Sidebar izquierdo | Filtra por docente específico |
        | **📖 Materia** | Sidebar izquierdo | Filtra por materia específica |
        | **🎯 Clase Predicha** | Cuerpo de la página | Filtra por ENTRETENIDO/ABURRIDO |
        | **👔 Estado Docente** | Cuerpo de la página | Filtra por estado del docente |
        """)

    # ====================================================================
    # SOBRE EL DASHBOARD
    # ====================================================================
    with st.expander("👥 Sobre este dashboard", expanded=False):
        st.markdown("""
        ### Dashboard Estratégico de Grabaciones Académicas

        **Desarrollado por:** Inteligencia Académica CUN  
        **Versión:** 1.1  
        **Última actualización:** 2026

        ### Tecnologías utilizadas:
        - 🐍 Python + Streamlit
        - 📊 Plotly para visualizaciones
        - 🤖 Machine Learning para clasificación
        - 🎯 Scikit-learn para modelos

        ### Objetivo:
        *"Transformar datos en insights accionables para mejorar la calidad académica."*
        """)


if __name__ == "__main__":
    main()
