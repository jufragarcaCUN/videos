"""
Dashboard - Verificación
Página para verificar los datos del Excel
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")


# ==================== FUNCIÓN DE CARGA ====================
@st.cache_data
def load_data_excel():
    try:
        Excel = r"C:\Users\juan_garnicac\Documents\ProyectosVisual\Videos\presentaciones\tabla_23_julio.xlsx"

        if not Path(Excel).exists():
            st.error(f"❌ No se encontró el archivo Excel")
            return None

        # LEER EL EXCEL
        df = pd.read_excel(Excel)

        # 🔥 SOLO DIVIDIR CPM ENTRE 1000
        if "CPM" in df.columns:
            df["CPM"] = pd.to_numeric(df["CPM"], errors="coerce") / 1000

        return df

    except Exception as e:
        st.error(f"❌ Error al cargar datos: {str(e)}")
        return None


# ==================== MAIN ====================
def main(df_filtrado=None):
    st.header("📋 Verificación de Datos")

    # Cargar datos
    df = load_data_excel()
    if df is None:
        st.stop()

    st.info("📊 Mostrando el Excel con CPM dividido entre 1000")

    # ====================================================================
    # KPIS
    # ====================================================================
    st.markdown("---")
    st.subheader("📊 Resumen del Excel")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Registros", len(df))
    with col2:
        st.metric("Total Columnas", len(df.columns))
    with col3:
        st.metric(
            "Total Docentes",
            (
                df["nombres_apellidos"].nunique()
                if "nombres_apellidos" in df.columns
                else 0
            ),
        )
    with col4:
        st.metric("Total Áreas", df["area"].nunique() if "area" in df.columns else 0)

    # ====================================================================
    # VER COLUMNA CPM
    # ====================================================================
    st.markdown("---")
    st.subheader("🔍 Columna CPM - Dividida entre 1000")

    if "CPM" in df.columns:
        with st.expander("📊 CPM - Valores", expanded=True):
            datos_col = df["CPM"].dropna()

            if not datos_col.empty:
                st.dataframe(
                    pd.DataFrame(
                        {"Fila": datos_col.index + 1, "CPM": datos_col.values}
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.warning("⚠️ No hay datos en CPM")

    # ====================================================================
    # VER TODOS LOS DATOS
    # ====================================================================
    st.markdown("---")
    st.subheader("📋 Datos Completos")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    # ====================================================================
    # EXPORTAR DATOS
    # ====================================================================
    st.markdown("---")
    st.subheader("📥 Exportar Datos")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name="datos_cpm_dividido.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
