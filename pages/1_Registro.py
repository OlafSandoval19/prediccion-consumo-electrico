import streamlit as st
from utils import guardar_registro

st.set_page_config(
    page_title="Registro de consumo",
    page_icon="🧾",
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

    .stSelectbox label,
    .stNumberInput label {
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

st.title("🧾 Registro de consumo eléctrico")

# =========================
# Validar sesión
# =========================
if "logueado" not in st.session_state or not st.session_state["logueado"]:
    st.warning("Primero inicia sesión desde la página principal.")
    st.stop()

st.info(
    f"Usuario activo: {st.session_state['nombre_usuario']} "
    f"({st.session_state['correo_usuario']})"
)

# =========================
# Datos del recibo
# =========================
st.subheader("Datos del recibo CFE")

col1, col2 = st.columns(2)

with col1:
    anio = st.number_input(
        "Año",
        min_value=2020,
        max_value=2035,
        value=2026,
        step=1
    )

with col2:
    periodo = st.selectbox(
        "Periodo del recibo",
        [
            "05 NOV - 07 ENE",
            "07 ENE - 06 MAR",
            "06 MAR - 07 MAY",
            "07 MAY - 07 JUL",
            "07 JUL - 04 SEP",
            "04 SEP - 05 NOV"
        ]
    )

col3, col4 = st.columns(2)

with col3:
    consumo_kwh = st.number_input(
        "Consumo total del periodo (kWh)",
        min_value=0.0,
        step=1.0
    )

with col4:
    importe_total = st.number_input(
        "Importe real pagado en el recibo ($ MXN)",
        min_value=0.0,
        step=1.0
    )

st.divider()

# =========================
# Cálculo automático de tarifa CFE
# =========================
TARIFA_BASICA = 1.119
TARIFA_INTERMEDIA = 1.361
TARIFA_EXCEDENTE = 3.980


def calcular_tarifa_cfe(consumo):
    kwh_basico = min(consumo, 150)
    restante = max(consumo - 150, 0)

    kwh_intermedio = min(restante, 130)
    restante = max(restante - 130, 0)

    kwh_excedente = restante

    subtotal_basico = kwh_basico * TARIFA_BASICA
    subtotal_intermedio = kwh_intermedio * TARIFA_INTERMEDIA
    subtotal_excedente = kwh_excedente * TARIFA_EXCEDENTE

    subtotal_calculado = (
        subtotal_basico
        + subtotal_intermedio
        + subtotal_excedente
    )

    return {
        "kwh_basico": kwh_basico,
        "precio_basico": TARIFA_BASICA,
        "subtotal_basico": subtotal_basico,
        "kwh_intermedio": kwh_intermedio,
        "precio_intermedio": TARIFA_INTERMEDIA,
        "subtotal_intermedio": subtotal_intermedio,
        "kwh_excedente": kwh_excedente,
        "precio_excedente": TARIFA_EXCEDENTE,
        "subtotal_excedente": subtotal_excedente,
        "subtotal_calculado": subtotal_calculado
    }


detalle_tarifa = calcular_tarifa_cfe(consumo_kwh)

st.subheader("Detalle automático de tarifa CFE")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Básico", f"{detalle_tarifa['kwh_basico']:.0f} kWh")
    st.write(f"Precio: ${detalle_tarifa['precio_basico']:.3f}/kWh")
    st.write(f"Subtotal: ${detalle_tarifa['subtotal_basico']:.2f}")

with c2:
    st.metric("Intermedio", f"{detalle_tarifa['kwh_intermedio']:.0f} kWh")
    st.write(f"Precio: ${detalle_tarifa['precio_intermedio']:.3f}/kWh")
    st.write(f"Subtotal: ${detalle_tarifa['subtotal_intermedio']:.2f}")

with c3:
    st.metric("Excedente", f"{detalle_tarifa['kwh_excedente']:.0f} kWh")
    st.write(f"Precio: ${detalle_tarifa['precio_excedente']:.3f}/kWh")
    st.write(f"Subtotal: ${detalle_tarifa['subtotal_excedente']:.2f}")

with c4:
    st.metric("Subtotal calculado", f"${detalle_tarifa['subtotal_calculado']:.2f}")

# =========================
# Comparación con importe real
# =========================
if consumo_kwh > 0 and importe_total > 0:
    diferencia = importe_total - detalle_tarifa["subtotal_calculado"]
    porcentaje_dif = abs(diferencia) / importe_total * 100

    st.info(
        f"Importe capturado: ${importe_total:.2f} MXN | "
        f"Subtotal por energía calculado: ${detalle_tarifa['subtotal_calculado']:.2f} MXN | "
        f"Diferencia: ${diferencia:.2f} MXN"
    )

    if porcentaje_dif > 35:
        st.warning(
            "El importe capturado es muy diferente al subtotal calculado. "
            "Revisa si el importe corresponde al mismo periodo y consumo."
        )

st.divider()

# =========================
# Guardar registro
# =========================
if st.button("Guardar registro"):
    if consumo_kwh <= 0:
        st.warning("Ingresa un consumo válido en kWh.")
    elif importe_total <= 0:
        st.warning("Ingresa un importe válido del recibo.")
    else:
        registro = {
            "nombre_usuario": st.session_state["nombre_usuario"],
            "correo_usuario": st.session_state["correo_usuario"],
            "anio": int(anio),
            "bimestre": periodo,
            "consumo_kwh": consumo_kwh,
            "importe_total": importe_total,

            "kwh_basico": detalle_tarifa["kwh_basico"],
            "precio_basico": detalle_tarifa["precio_basico"],

            "kwh_intermedio": detalle_tarifa["kwh_intermedio"],
            "precio_intermedio": detalle_tarifa["precio_intermedio"],

            "kwh_excedente": detalle_tarifa["kwh_excedente"],
            "precio_excedente": detalle_tarifa["precio_excedente"]
        }

        guardar_registro(registro)
        st.success("Registro guardado correctamente.")