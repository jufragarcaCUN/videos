from pathlib import Path
import os
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Académico | CUN",
    page_icon="🎓",
    layout="wide",
)

# Estilos CSS
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            background-color: #1a5276 !important;
        }
        [data-testid="stSidebar"] * {
            color: white !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)


def mostrar_archivos_en_sidebar(ruta_carpeta):
    """Muestra el contenido de la carpeta en un desplegable dentro del Sidebar."""
    try:
        if os.path.exists(ruta_carpeta):
            elementos = os.listdir(ruta_carpeta)
            with st.sidebar.expander("📂 Archivos en el directorio", expanded=False):
                for elem in elementos:
                    # Ignorar archivos temporales de Excel
                    if elem.startswith("~$"):
                        continue

                    ruta_completa = os.path.join(ruta_carpeta, elem)
                    if os.path.isfile(ruta_completa):
                        st.text(f"📄 {elem}")
                    elif os.path.isdir(ruta_completa):
                        st.text(f"📁 {elem}")
    except Exception as e:
        st.sidebar.error(f"Error al listar carpeta: {e}")


@st.cache_data
def load_data():
    try:
        # Corrección del nombre del archivo a 'exel_salida.xlsx'
        excel_path = Path(__file__).parent / "exel_entrada.xlsx"

        if not excel_path.exists():
            st.error(f"❌ No se encontró el archivo Excel en: {excel_path}")
            return None

        df = pd.read_excel(excel_path)

        multi_value_cols = [
            "grupo",
            "nom_materia",
            "creditos",
            "capacidad",
            "num_inscritos",
            "porcentaje_ocupacion_aula",
            "cod_periodo_grupo",
        ]
        for col in multi_value_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.split("|").str[0]
                if col in [
                    "creditos",
                    "capacidad",
                    "num_inscritos",
                    "porcentaje_ocupacion_aula",
                ]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

        date_columns = ["fecha", "fec_contrato", "fec_fin"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        numeric_columns = [
            "pro_evaluacion_autoevaluacion_docente",
            "pro_evaluacion_evaluacion_por_estudiantes",
            "num_encuestas_evaluacion_por_estudiantes",
            "sigma2_IM",
            "Porcentaje_Certeza",
            "Jitter_Score",
            "IMP_promedio",
            "CPM",
            "DME_s",
            "DTE_ratio",
            "Enthusiasm_Score",
            "Tone_CoV",
            "capacidad",
            "num_inscritos",
            "creditos",
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.replace(["NULL", "null", "NaN", "", " "], np.nan)

        if "CPM" in df.columns:
            df["CPM"] = df["CPM"] / 1000

        return df

    except Exception as e:
        st.error(f"❌ Error al cargar los datos: {str(e)}")
        return None


def render_sidebar_filters(df):
    """Renderiza los filtros dentro del sidebar independientemente de la página."""
    st.sidebar.markdown("### 🎛️ Filtros Globales")
    filters_sidebar = {}

    for col, label in [
        ("area", "📚 Programa"),
        ("nombres_apellidos", "👨‍🏫 Docente"),
        ("nom_materia", "📖 Materia"),
    ]:
        if col in df.columns:
            options = ["Todos"] + sorted(df[col].dropna().unique().tolist())
            selected = st.sidebar.multiselect(
                label,
                options=options,
                default=["Todos"],
                key=f"global_sidebar_{col}",
            )
            if "Todos" not in selected and selected:
                filters_sidebar[col] = selected

    # Aplicar Filtros
    df_filtrado = df.copy()
    for col, value in filters_sidebar.items():
        if value and "Todos" not in value and col in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado[col].isin(value)]

    # Guardar en Session State
    st.session_state["df_filtrado"] = df_filtrado


def main():
    # Muestra los archivos en el menú lateral de Streamlit
    ruta = Path(__file__).parent
    mostrar_archivos_en_sidebar(ruta)

    df = load_data()
    if df is None:
        st.stop()

    # 1. Definir páginas de la navegación
    p_presentacion = st.Page("pages/1_presentacion.py", title="Presentación", icon="🎓")
    p_general = st.Page("pages/2_general.py", title="Análisis General", icon="📈")
    p_profundidad = st.Page("pages/3_profundidad.py", title="profundidad", icon="📈")

    pg = st.navigation({"Informes": [p_presentacion, p_general, p_profundidad]})

    # 2. Renderizar Filtros
    render_sidebar_filters(df)

    # 3. Ejecutar la vista de la página actual
    pg.run()


if __name__ == "__main__":
    main()
