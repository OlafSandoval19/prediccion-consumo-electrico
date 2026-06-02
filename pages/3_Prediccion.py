import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from utils import cargar_datos_usuario

st.set_page_config(
    page_title="Predicción de consumo",
    page_icon="🤖",
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


st.title("🤖 Predicción de consumo eléctrico")

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
    st.warning("Aún no tienes registros guardados. Primero registra datos de consumo.")
    st.stop()

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
df["tarifa_promedio_real"] = df["importe_total"] / df["consumo_kwh"]

# =========================
# Validar mínimo
# =========================
if len(df) < 3:
    st.warning(
        "Se necesitan al menos 3 registros para generar una predicción inicial. "
        "Agrega más datos históricos en la sección Registro."
    )

    st.dataframe(
        df[["anio", "bimestre", "consumo_kwh", "importe_total"]],
        use_container_width=True,
        hide_index=True
    )
    st.stop()

# =========================
# Tarifas CFE
# =========================
TARIFA_BASICA = 1.119
TARIFA_INTERMEDIA = 1.361
TARIFA_EXCEDENTE = 3.980

# Factor aproximado para pasar de subtotal energía a total de recibo.
FACTOR_RECIBO = 1.12


def calcular_importe_cfe(consumo):
    kwh_basico = min(consumo, 150)
    restante = max(consumo - 150, 0)

    kwh_intermedio = min(restante, 130)
    restante = max(restante - 130, 0)

    kwh_excedente = restante

    subtotal_basico = kwh_basico * TARIFA_BASICA
    subtotal_intermedio = kwh_intermedio * TARIFA_INTERMEDIA
    subtotal_excedente = kwh_excedente * TARIFA_EXCEDENTE

    subtotal_energia = subtotal_basico + subtotal_intermedio + subtotal_excedente
    total_estimado = subtotal_energia * FACTOR_RECIBO

    return {
        "kwh_basico": kwh_basico,
        "kwh_intermedio": kwh_intermedio,
        "kwh_excedente": kwh_excedente,
        "subtotal_basico": subtotal_basico,
        "subtotal_intermedio": subtotal_intermedio,
        "subtotal_excedente": subtotal_excedente,
        "subtotal_energia": subtotal_energia,
        "total_estimado": total_estimado
    }


def obtener_siguiente_periodo(anio_actual, periodo_actual):
    indice_actual = periodos_cfe.index(periodo_actual)

    if indice_actual == len(periodos_cfe) - 1:
        return anio_actual + 1, periodos_cfe[0]

    return anio_actual, periodos_cfe[indice_actual + 1]


def prediccion_conservadora(df_base, siguiente_anio, siguiente_periodo):
    """
    Modelo conservador para pocos recibos.
    Prioriza el cambio reciente y evita que años con consumo alto inflen demasiado.
    """

    ultimo_consumo = float(df_base["consumo_kwh"].iloc[-1])
    promedio_ultimos_2 = float(df_base["consumo_kwh"].tail(2).mean())
    promedio_ultimos_3 = float(df_base["consumo_kwh"].tail(3).mean())
    promedio_general = float(df_base["consumo_kwh"].mean())

    ultimo_anio = int(df_base["anio"].iloc[-1])
    ultimo_periodo = df_base["bimestre"].iloc[-1]

    mismo_periodo_anterior = df_base[
        (df_base["anio"] == siguiente_anio - 1) &
        (df_base["bimestre"] == siguiente_periodo)
    ]

    mismo_ultimo_periodo_anterior = df_base[
        (df_base["anio"] == ultimo_anio - 1) &
        (df_base["bimestre"] == ultimo_periodo)
    ]

    if not mismo_periodo_anterior.empty:
        consumo_estacional = float(mismo_periodo_anterior["consumo_kwh"].iloc[-1])

        if not mismo_ultimo_periodo_anterior.empty:
            consumo_equivalente_anterior = float(
                mismo_ultimo_periodo_anterior["consumo_kwh"].iloc[-1]
            )

            if consumo_equivalente_anterior > 0:
                factor_cambio = ultimo_consumo / consumo_equivalente_anterior
            else:
                factor_cambio = 1.0

            factor_suavizado = factor_cambio ** 0.70
            factor_suavizado = min(max(factor_suavizado, 0.55), 1.10)

            consumo_estacional_ajustado = consumo_estacional * factor_suavizado
        else:
            consumo_estacional_ajustado = consumo_estacional

        consumo_estimado = (
            0.35 * consumo_estacional_ajustado +
            0.35 * ultimo_consumo +
            0.20 * promedio_ultimos_2 +
            0.10 * promedio_ultimos_3
        )

        modelo_usado = "Modelo híbrido conservador ajustado"
        descripcion_modelo = (
            "La estimación usa el mismo periodo del año anterior, pero corrige el valor "
            "con el cambio reciente del usuario. Además, da mayor peso al último recibo "
            "para evitar que consumos altos antiguos eleven demasiado la predicción."
        )

    else:
        consumo_estimado = (
            0.45 * ultimo_consumo +
            0.35 * promedio_ultimos_2 +
            0.15 * promedio_ultimos_3 +
            0.05 * promedio_general
        )

        modelo_usado = "Promedio móvil conservador"
        descripcion_modelo = (
            "No se encontró el mismo periodo del año anterior. La estimación se calculó "
            "principalmente con el último consumo y los promedios recientes."
        )

    max_historico = float(df_base["consumo_kwh"].max())
    min_historico = float(df_base["consumo_kwh"].min())

    limite_superior = max_historico * 1.05
    limite_inferior = max(min_historico * 0.80, 0)

    consumo_estimado = min(consumo_estimado, limite_superior)
    consumo_estimado = max(consumo_estimado, limite_inferior)

    return float(consumo_estimado), modelo_usado, descripcion_modelo


# =========================
# Predicción principal
# =========================
ultimo = df.iloc[-1]

siguiente_anio, siguiente_periodo = obtener_siguiente_periodo(
    int(ultimo["anio"]),
    ultimo["bimestre"]
)

consumo_estimado, modelo_usado, descripcion_modelo = prediccion_conservadora(
    df,
    siguiente_anio,
    siguiente_periodo
)

detalle_estimado = calcular_importe_cfe(consumo_estimado)

subtotal_energia = detalle_estimado["subtotal_energia"]
importe_estimado = detalle_estimado["total_estimado"]

# =========================
# Resultados principales
# =========================
st.subheader("Resultado de la predicción")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Próximo periodo",
        f"{siguiente_anio} | {siguiente_periodo}"
    )

with col2:
    st.metric(
        "Consumo estimado",
        f"{consumo_estimado:.1f} kWh"
    )

with col3:
    st.metric(
        "Recibo estimado",
        f"${importe_estimado:,.2f} MXN"
    )

st.success(f"Modelo utilizado: {modelo_usado}")
st.info(descripcion_modelo)

st.caption(
    "La predicción se calcula únicamente con los registros del usuario activo. "
    "No se mezclan datos entre usuarios."
)

st.divider()

# =========================
# Comparación con último recibo
# =========================
st.subheader("Comparación con el último recibo")

ultimo_consumo = float(df["consumo_kwh"].iloc[-1])
ultimo_importe = float(df["importe_total"].iloc[-1])

diferencia_consumo = consumo_estimado - ultimo_consumo
porcentaje_cambio = (diferencia_consumo / ultimo_consumo) * 100 if ultimo_consumo > 0 else 0

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Último consumo", f"{ultimo_consumo:.1f} kWh")

with c2:
    st.metric(
        "Diferencia estimada",
        f"{diferencia_consumo:.1f} kWh",
        f"{porcentaje_cambio:.1f}%"
    )

with c3:
    st.metric("Último importe", f"${ultimo_importe:,.2f} MXN")

if porcentaje_cambio > 10:
    st.warning(
        f"El consumo estimado aumenta aproximadamente {porcentaje_cambio:.1f}% "
        "respecto al último periodo registrado."
    )
elif porcentaje_cambio < -10:
    st.success(
        f"El consumo estimado disminuye aproximadamente {abs(porcentaje_cambio):.1f}% "
        "respecto al último periodo registrado."
    )
else:
    st.info(
        "El consumo estimado se mantiene relativamente estable respecto al último periodo."
    )

if consumo_estimado > 280:
    st.warning(
        "El consumo estimado entra en zona de excedente. "
        "Esto puede elevar el costo del recibo."
    )
else:
    st.success(
        "El consumo estimado se mantiene dentro de los bloques básico/intermedio."
    )

st.divider()

# =========================
# Estimación económica
# =========================
st.subheader("Estimación económica del próximo recibo")

e1, e2 = st.columns(2)

with e1:
    st.metric(
        "Recibo estimado",
        f"${importe_estimado:,.2f} MXN"
    )
    st.write(
        "Este valor se calcula con el subtotal de energía por bloques CFE "
        "más un factor moderado de cargos adicionales."
    )

with e2:
    st.metric(
        "Subtotal de energía",
        f"${subtotal_energia:,.2f} MXN"
    )
    st.write(
        f"Factor aplicado para cargos adicionales: **{FACTOR_RECIBO:.2f}**"
    )

st.warning(
    "El recibo real puede variar por IVA, subsidios, ajustes, adeudos o cargos locales. "
    "Esta estimación busca ser práctica y conservadora."
)

st.divider()

# =========================
# Desglose por tarifa CFE
# =========================
st.subheader("Desglose estimado por tarifa CFE")

d1, d2, d3, d4 = st.columns(4)

with d1:
    st.metric("Básico", f"{detalle_estimado['kwh_basico']:.1f} kWh")
    st.write(f"Tarifa: ${TARIFA_BASICA:.3f}/kWh")
    st.write(f"Subtotal: ${detalle_estimado['subtotal_basico']:,.2f}")

with d2:
    st.metric("Intermedio", f"{detalle_estimado['kwh_intermedio']:.1f} kWh")
    st.write(f"Tarifa: ${TARIFA_INTERMEDIA:.3f}/kWh")
    st.write(f"Subtotal: ${detalle_estimado['subtotal_intermedio']:,.2f}")

with d3:
    st.metric("Excedente", f"{detalle_estimado['kwh_excedente']:.1f} kWh")
    st.write(f"Tarifa: ${TARIFA_EXCEDENTE:.3f}/kWh")
    st.write(f"Subtotal: ${detalle_estimado['subtotal_excedente']:,.2f}")

with d4:
    st.metric("Subtotal energía", f"${subtotal_energia:,.2f}")

st.divider()

# =========================
# Confiabilidad de la estimación
# =========================
st.subheader("Confiabilidad de la estimación")

n_registros = len(df)
variabilidad = float(df["consumo_kwh"].std())
promedio_consumo = float(df["consumo_kwh"].mean())

coef_variacion = variabilidad / promedio_consumo if promedio_consumo > 0 else 0

if n_registros >= 9 and coef_variacion <= 0.35:
    nivel_confianza = "Alta"
    margen_consumo = 0.08
    margen_recibo = 0.07
elif n_registros >= 6 and coef_variacion <= 0.55:
    nivel_confianza = "Media"
    margen_consumo = 0.10
    margen_recibo = 0.09
else:
    nivel_confianza = "Baja"
    margen_consumo = 0.15
    margen_recibo = 0.12

consumo_min = consumo_estimado * (1 - margen_consumo)
consumo_max = consumo_estimado * (1 + margen_consumo)

recibo_min = importe_estimado * (1 - margen_recibo)
recibo_max = importe_estimado * (1 + margen_recibo)

r1, r2, r3 = st.columns(3)

with r1:
    st.metric("Nivel de confianza", nivel_confianza)

with r2:
    st.metric(
        "Rango estimado de consumo",
        f"{consumo_min:.0f} - {consumo_max:.0f} kWh"
    )

with r3:
    st.metric(
        "Rango estimado del recibo",
        f"${recibo_min:,.0f} - ${recibo_max:,.0f} MXN"
    )

st.info(
    "Este rango considera la cantidad de recibos disponibles y la variación histórica "
    "del consumo. Con más registros, la estimación puede volverse más estable."
)

st.divider()

# =========================
# Gráfica histórico + predicción
# =========================
st.subheader("Consumo histórico y predicción")

df_grafica = df[["periodo_completo", "consumo_kwh"]].copy()
df_grafica["Tipo"] = "Histórico"

nuevo_punto = pd.DataFrame([{
    "periodo_completo": f"{siguiente_anio} | {siguiente_periodo}",
    "consumo_kwh": consumo_estimado,
    "Tipo": "Predicción"
}])

df_grafica = pd.concat([df_grafica, nuevo_punto], ignore_index=True)

fig_consumo = px.line(
    df_grafica,
    x="periodo_completo",
    y="consumo_kwh",
    markers=True,
    color="Tipo",
    text=df_grafica["consumo_kwh"].round(0),
    title="Consumo histórico y próximo periodo estimado"
)

fig_consumo.update_traces(
    textposition="top center",
    marker=dict(size=11),
    line=dict(width=4),
    hovertemplate="<b>Periodo:</b> %{x}<br><b>Consumo:</b> %{y:.1f} kWh<extra></extra>"
)

fig_consumo = aplicar_estilo_grafica(
    fig_consumo,
    "Periodo",
    "Consumo (kWh)"
)

st.plotly_chart(fig_consumo, use_container_width=True)

# =========================
# Gráfica importe histórico + estimado
# =========================
st.subheader("Importe histórico y recibo estimado")

df_importe = df[["periodo_completo", "importe_total"]].copy()
df_importe["Tipo"] = "Histórico"

nuevo_importe = pd.DataFrame([{
    "periodo_completo": f"{siguiente_anio} | {siguiente_periodo}",
    "importe_total": importe_estimado,
    "Tipo": "Predicción"
}])

df_importe = pd.concat([df_importe, nuevo_importe], ignore_index=True)

fig_importe = px.bar(
    df_importe,
    x="periodo_completo",
    y="importe_total",
    color="Tipo",
    text=df_importe["importe_total"].round(0),
    title="Importe histórico y recibo estimado"
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

st.plotly_chart(fig_importe, use_container_width=True)

# =========================
# Tabla de datos usados
# =========================
st.subheader("Datos utilizados para la predicción")

tabla = df[[
    "anio",
    "bimestre",
    "consumo_kwh",
    "importe_total",
    "kwh_basico",
    "kwh_intermedio",
    "kwh_excedente",
    "tarifa_promedio_real"
]].copy()

tabla = tabla.rename(columns={
    "anio": "Año",
    "bimestre": "Periodo",
    "consumo_kwh": "Consumo (kWh)",
    "importe_total": "Importe real ($)",
    "kwh_basico": "Básico (kWh)",
    "kwh_intermedio": "Intermedio (kWh)",
    "kwh_excedente": "Excedente (kWh)",
    "tarifa_promedio_real": "Tarifa promedio real ($/kWh)"
})

# Formato visual de tabla
tabla["Consumo (kWh)"] = tabla["Consumo (kWh)"].map(lambda x: f"{x:.0f}")
tabla["Importe real ($)"] = tabla["Importe real ($)"].map(lambda x: f"${x:,.2f}")
tabla["Básico (kWh)"] = tabla["Básico (kWh)"].map(lambda x: f"{x:.0f}")
tabla["Intermedio (kWh)"] = tabla["Intermedio (kWh)"].map(lambda x: f"{x:.0f}")
tabla["Excedente (kWh)"] = tabla["Excedente (kWh)"].map(lambda x: f"{x:.0f}")
tabla["Tarifa promedio real ($/kWh)"] = tabla["Tarifa promedio real ($/kWh)"].map(lambda x: f"${x:.2f}")

st.dataframe(
    tabla,
    use_container_width=True,
    hide_index=True,
    height=360
)