import streamlit as st
import pandas as pd
import plotly.express as px
from utils import cargar_datos_usuario, eliminar_registro, actualizar_registro

st.set_page_config(
    page_title="Historial de consumo",
    page_icon="📊",
    layout="wide"
)

# =========================
# Estilos generales
# =========================
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 22px !important;
    }

    .stApp {
        font-size: 22px !important;
    }

    h1 {
        font-size: 48px !important;
        font-weight: 900 !important;
        color: #1f2937 !important;
    }

    h2 {
        font-size: 38px !important;
        font-weight: 800 !important;
        color: #1f2937 !important;
    }

    h3 {
        font-size: 32px !important;
        font-weight: 750 !important;
        color: #1f2937 !important;
    }

    p, div, span, label {
        font-size: 22px !important;
    }

    .stAlert {
        font-size: 22px !important;
    }

    .stMetric label {
        font-size: 22px !important;
        font-weight: 700 !important;
    }

    .stMetric div {
        font-size: 32px !important;
        font-weight: 800 !important;
    }

    .stDataFrame {
        font-size: 20px !important;
    }

    .stSelectbox label,
    .stNumberInput label,
    .stRadio label {
        font-size: 22px !important;
        font-weight: 700 !important;
    }

    .stSelectbox div,
    .stNumberInput input {
        font-size: 22px !important;
    }

    .stButton > button {
        font-size: 22px !important;
        font-weight: 700 !important;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] * {
        font-size: 21px !important;
    }

    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# Estilo para gráficas Plotly
# =========================
def aplicar_estilo_grafica(fig, titulo_x, titulo_y):
    fig.update_layout(
        template="plotly_white",
        title=dict(
            font=dict(size=28),
            x=0.02,
            xanchor="left"
        ),
        font=dict(size=20),
        xaxis_title=titulo_x,
        yaxis_title=titulo_y,
        xaxis=dict(
            tickangle=-30,
            showgrid=False,
            tickfont=dict(size=16)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.08)",
            tickfont=dict(size=16)
        ),
        legend=dict(
            title="",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=80, b=80),
        height=520
    )

    return fig


st.title("📊 Historial de consumo eléctrico")

# =========================
# Validar sesión
# =========================
if "logueado" not in st.session_state or not st.session_state["logueado"]:
    st.warning("Primero inicia sesión desde la página principal.")
    st.stop()

correo = st.session_state["correo_usuario"]
nombre = st.session_state["nombre_usuario"]

st.info(f"Usuario activo: {nombre} ({correo})")

# =========================
# Cargar datos
# =========================
df = cargar_datos_usuario(correo)

if df.empty:
    st.warning("Aún no tienes registros guardados.")
    st.stop()

# Guardar índice real del CSV antes de ordenar
df["registro_id"] = df.index

# =========================
# Orden de periodos CFE
# =========================
orden_periodos = {
    "05 NOV - 07 ENE": 1,
    "07 ENE - 06 MAR": 2,
    "06 MAR - 07 MAY": 3,
    "07 MAY - 07 JUL": 4,
    "07 JUL - 04 SEP": 5,
    "04 SEP - 05 NOV": 6
}

periodos_cfe = [
    "05 NOV - 07 ENE",
    "07 ENE - 06 MAR",
    "06 MAR - 07 MAY",
    "07 MAY - 07 JUL",
    "07 JUL - 04 SEP",
    "04 SEP - 05 NOV"
]

df["orden_periodo"] = df["bimestre"].map(orden_periodos)
df = df.sort_values(by=["anio", "orden_periodo"]).reset_index(drop=True)

df["periodo_completo"] = df["anio"].astype(str) + " | " + df["bimestre"]
df["tarifa_promedio"] = df["importe_total"] / df["consumo_kwh"]

# =========================
# Resumen general
# =========================
st.subheader("Resumen general")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Registros", len(df))

with col2:
    st.metric("Consumo promedio", f"{df['consumo_kwh'].mean():.1f} kWh")

with col3:
    st.metric("Importe promedio", f"${df['importe_total'].mean():,.2f}")

with col4:
    st.metric("Tarifa promedio", f"${df['tarifa_promedio'].mean():.2f}/kWh")

st.divider()

# =========================
# Tabla de registros
# =========================
st.subheader("Tabla de registros")

columnas_mostrar = [
    "registro_id",
    "anio",
    "bimestre",
    "consumo_kwh",
    "importe_total",
    "kwh_basico",
    "kwh_intermedio",
    "kwh_excedente",
    "tarifa_promedio"
]

df_tabla = df[columnas_mostrar].copy()

df_tabla = df_tabla.rename(columns={
    "registro_id": "ID",
    "anio": "Año",
    "bimestre": "Periodo",
    "consumo_kwh": "Consumo (kWh)",
    "importe_total": "Importe ($)",
    "kwh_basico": "Básico (kWh)",
    "kwh_intermedio": "Intermedio (kWh)",
    "kwh_excedente": "Excedente (kWh)",
    "tarifa_promedio": "Tarifa promedio ($/kWh)"
})

# Formato visual de tabla
df_tabla["Consumo (kWh)"] = df_tabla["Consumo (kWh)"].map(lambda x: f"{x:.0f}")
df_tabla["Importe ($)"] = df_tabla["Importe ($)"].map(lambda x: f"${x:,.2f}")
df_tabla["Básico (kWh)"] = df_tabla["Básico (kWh)"].map(lambda x: f"{x:.0f}")
df_tabla["Intermedio (kWh)"] = df_tabla["Intermedio (kWh)"].map(lambda x: f"{x:.0f}")
df_tabla["Excedente (kWh)"] = df_tabla["Excedente (kWh)"].map(lambda x: f"{x:.0f}")
df_tabla["Tarifa promedio ($/kWh)"] = df_tabla["Tarifa promedio ($/kWh)"].map(lambda x: f"${x:.2f}")

st.dataframe(
    df_tabla,
    use_container_width=True,
    hide_index=True,
    height=360
)

st.divider()

# =========================
# Modificar o eliminar registro
# =========================
st.subheader("Modificar o eliminar registro")

opciones = [
    f"ID {row['registro_id']} | {row['anio']} | {row['bimestre']} | "
    f"{row['consumo_kwh']} kWh | ${row['importe_total']}"
    for _, row in df.iterrows()
]

seleccion = st.selectbox("Selecciona un registro", opciones)

registro_id = int(seleccion.split("|")[0].replace("ID", "").strip())
registro = df[df["registro_id"] == registro_id].iloc[0]

accion = st.radio(
    "Acción",
    ["Editar", "Eliminar"],
    horizontal=True
)

if accion == "Eliminar":
    st.warning("Esta acción eliminará permanentemente el registro seleccionado.")

    st.write(
        f"Registro seleccionado: **{registro['anio']} | {registro['bimestre']} | "
        f"{registro['consumo_kwh']} kWh | ${registro['importe_total']}**"
    )

    if st.button("Eliminar registro"):
        eliminar_registro(registro_id)
        st.success("Registro eliminado correctamente.")
        st.rerun()

else:
    st.write("Edita los campos necesarios:")

    col1, col2 = st.columns(2)

    with col1:
        nuevo_anio = st.number_input(
            "Año",
            min_value=2020,
            max_value=2035,
            value=int(registro["anio"]),
            step=1
        )

    with col2:
        nuevo_periodo = st.selectbox(
            "Periodo del recibo",
            periodos_cfe,
            index=periodos_cfe.index(registro["bimestre"])
        )

    col3, col4 = st.columns(2)

    with col3:
        nuevo_consumo = st.number_input(
            "Consumo total del periodo (kWh)",
            min_value=0.0,
            value=float(registro["consumo_kwh"]),
            step=1.0
        )

    with col4:
        nuevo_importe = st.number_input(
            "Importe real pagado en el recibo ($ MXN)",
            min_value=0.0,
            value=float(registro["importe_total"]),
            step=1.0
        )

    # =========================
    # Recalcular tarifa CFE
    # =========================
    TARIFA_BASICA = 1.119
    TARIFA_INTERMEDIA = 1.361
    TARIFA_EXCEDENTE = 3.980

    kwh_basico = min(nuevo_consumo, 150)
    restante = max(nuevo_consumo - 150, 0)

    kwh_intermedio = min(restante, 130)
    restante = max(restante - 130, 0)

    kwh_excedente = restante

    subtotal_basico = kwh_basico * TARIFA_BASICA
    subtotal_intermedio = kwh_intermedio * TARIFA_INTERMEDIA
    subtotal_excedente = kwh_excedente * TARIFA_EXCEDENTE
    subtotal_calculado = subtotal_basico + subtotal_intermedio + subtotal_excedente

    st.info(
        f"Nuevo desglose automático: "
        f"Básico {kwh_basico:.0f} kWh, "
        f"Intermedio {kwh_intermedio:.0f} kWh, "
        f"Excedente {kwh_excedente:.0f} kWh. "
        f"Subtotal calculado: ${subtotal_calculado:.2f}"
    )

    if nuevo_consumo > 0 and nuevo_importe > 0:
        diferencia = nuevo_importe - subtotal_calculado
        porcentaje_dif = abs(diferencia) / nuevo_importe * 100

        st.write(
            f"Importe capturado: **${nuevo_importe:.2f} MXN** | "
            f"Subtotal por energía calculado: **${subtotal_calculado:.2f} MXN** | "
            f"Diferencia: **${diferencia:.2f} MXN**"
        )

        if porcentaje_dif > 35:
            st.warning(
                "El importe capturado es muy diferente al subtotal calculado. "
                "Revisa si el importe corresponde al mismo periodo y consumo."
            )

    if st.button("Guardar cambios"):
        if nuevo_consumo <= 0:
            st.warning("El consumo debe ser mayor a cero.")
        elif nuevo_importe <= 0:
            st.warning("El importe debe ser mayor a cero.")
        else:
            datos_actualizados = {
                "anio": int(nuevo_anio),
                "bimestre": nuevo_periodo,
                "consumo_kwh": nuevo_consumo,
                "importe_total": nuevo_importe,
                "kwh_basico": kwh_basico,
                "precio_basico": TARIFA_BASICA,
                "kwh_intermedio": kwh_intermedio,
                "precio_intermedio": TARIFA_INTERMEDIA,
                "kwh_excedente": kwh_excedente,
                "precio_excedente": TARIFA_EXCEDENTE
            }

            actualizar_registro(registro_id, datos_actualizados)
            st.success("Registro actualizado correctamente.")
            st.rerun()

st.divider()

# =========================
# Gráfica de consumo
# =========================
st.subheader("Consumo histórico")

fig_consumo = px.line(
    df,
    x="periodo_completo",
    y="consumo_kwh",
    markers=True,
    text=df["consumo_kwh"].round(0),
    title="Consumo eléctrico por periodo"
)

fig_consumo.update_traces(
    textposition="top center",
    marker=dict(size=11),
    line=dict(width=4),
    hovertemplate="<b>Periodo:</b> %{x}<br><b>Consumo:</b> %{y:.0f} kWh<extra></extra>"
)

fig_consumo = aplicar_estilo_grafica(
    fig_consumo,
    "Periodo",
    "Consumo (kWh)"
)

st.plotly_chart(fig_consumo, use_container_width=True)

# =========================
# Gráfica de importe
# =========================
st.subheader("Importe histórico")

fig_importe = px.bar(
    df,
    x="periodo_completo",
    y="importe_total",
    text=df["importe_total"].round(0),
    title="Importe del recibo por periodo"
)

fig_importe.update_traces(
    texttemplate="$%{text:,.0f}",
    textposition="outside",
    hovertemplate="<b>Periodo:</b> %{x}<br><b>Importe:</b> $%{y:,.2f} MXN<extra></extra>"
)

fig_importe.update_layout(
    template="plotly_white",
    title=dict(
        font=dict(size=28),
        x=0.02,
        xanchor="left"
    ),
    font=dict(size=20),
    xaxis_title="Periodo",
    yaxis_title="Importe ($ MXN)",
    xaxis=dict(
        tickangle=-30,
        showgrid=False,
        tickfont=dict(size=16)
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor="rgba(0,0,0,0.08)",
        tickfont=dict(size=16)
    ),
    margin=dict(l=40, r=40, t=80, b=80),
    height=520
)

st.plotly_chart(fig_importe, use_container_width=True)