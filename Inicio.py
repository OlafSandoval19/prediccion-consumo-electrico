import streamlit as st

st.set_page_config(
    page_title="Inicio | Predicción de Consumo Eléctrico",
    page_icon="⚡",
    layout="wide"
)

# =========================
# Estilos generales
# =========================
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-size: 21px !important;
    }

    .stApp {
        font-size: 21px !important;
        background-color: #ffffff;
    }

    .block-container {
    padding-top: 4.2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
    }

    .main-title {
       font-size: 44px !important;
       font-weight: 900;
       color: #1f2937;
       text-align: center;
       margin-top: 0.5rem;
       margin-bottom: 10px;
       line-height: 1.2;
    }

    .subtitle {
        font-size: 22px !important;
        color: #4b5563;
        text-align: center;
        margin-bottom: 24px;
        line-height: 1.4;
    }

    .hero-card {
        background: linear-gradient(135deg, #ecfdf5 0%, #eff6ff 100%);
        padding: 28px 32px;
        border-radius: 18px;
        border: 1px solid #d1fae5;
        box-shadow: 0px 5px 16px rgba(0,0,0,0.05);
        margin-bottom: 28px;
    }

    .hero-title {
        font-size: 28px !important;
        font-weight: 850;
        color: #111827;
        margin-bottom: 12px;
    }

    .hero-text {
        font-size: 21px !important;
        color: #374151;
        line-height: 1.55;
    }

    .section-title {
        font-size: 28px !important;
        font-weight: 850;
        color: #111827;
        margin-top: 10px;
        margin-bottom: 18px;
    }

    .step-box {
        background-color: #f9fafb;
        padding: 22px;
        border-radius: 16px;
        border-left: 7px solid #10b981;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
        min-height: 145px;
    }

    .step-title {
        font-size: 23px !important;
        font-weight: 850;
        color: #111827;
        margin-bottom: 8px;
    }

    .step-text {
        font-size: 20px !important;
        color: #4b5563;
        line-height: 1.45;
    }

    .feature-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e5e7eb;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.04);
        min-height: 110px;
    }

    .feature-label {
        font-size: 18px !important;
        color: #6b7280;
        margin-bottom: 4px;
    }

    .feature-value {
        font-size: 22px !important;
        font-weight: 800;
        color: #111827;
    }

    h1 {
        font-size: 42px !important;
        font-weight: 900 !important;
        color: #1f2937 !important;
    }

    h2 {
        font-size: 34px !important;
        font-weight: 800 !important;
        color: #1f2937 !important;
    }

    h3 {
        font-size: 28px !important;
        font-weight: 750 !important;
        color: #1f2937 !important;
    }

    p, div, span, label {
        font-size: 21px !important;
    }

    .stAlert {
        font-size: 21px !important;
    }

    .stTextInput label {
        font-size: 21px !important;
        font-weight: 700 !important;
    }

    .stTextInput input {
        font-size: 21px !important;
        height: 48px;
    }

    .stButton > button {
        font-size: 21px !important;
        font-weight: 700 !important;
        padding: 0.7rem 1.4rem;
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] * {
        font-size: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# Estado de sesión
# =========================
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if "nombre_usuario" not in st.session_state:
    st.session_state["nombre_usuario"] = ""

if "correo_usuario" not in st.session_state:
    st.session_state["correo_usuario"] = ""


# =========================
# Login
# =========================
if not st.session_state["logueado"]:

    st.markdown(
        '<div class="main-title">⚡ Predicción de Consumo Eléctrico</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Sistema web para registrar recibos CFE, analizar historial y estimar el próximo consumo eléctrico.</div>',
        unsafe_allow_html=True
    )

    col_hero_1, col_hero_2, col_hero_3 = st.columns([0.8, 1.4, 0.8])

    with col_hero_2:
        st.markdown("""
        <div class="hero-card">
            <div class="hero-title">Inicio de sesión</div>
            <div class="hero-text">
                Ingresa tu nombre y correo electrónico para crear tu historial personal de consumo.
            </div>
        </div>
        """, unsafe_allow_html=True)

        nombre = st.text_input("Nombre del usuario")
        correo = st.text_input("Correo electrónico")

        if st.button("Ingresar"):
            if nombre.strip() == "" or correo.strip() == "":
                st.warning("Por favor ingresa tu nombre y correo electrónico.")
            elif "@" not in correo or "." not in correo:
                st.warning("Ingresa un correo electrónico válido.")
            else:
                st.session_state["logueado"] = True
                st.session_state["nombre_usuario"] = nombre.strip()
                st.session_state["correo_usuario"] = correo.strip().lower()
                st.rerun()

    st.divider()

    st.markdown('<div class="section-title">¿Qué puedes hacer con esta aplicación?</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="step-box">
            <div class="step-title">🧾 Registrar recibos</div>
            <div class="step-text">
                Captura periodo, consumo en kWh e importe real pagado.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="step-box">
            <div class="step-title">📊 Consultar historial</div>
            <div class="step-text">
                Visualiza registros, gráficas de consumo y desglose por tarifa.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="step-box">
            <div class="step-title">🤖 Estimar consumo</div>
            <div class="step-text">
                Obtén una predicción conservadora del próximo periodo.
            </div>
        </div>
        """, unsafe_allow_html=True)


# =========================
# Panel principal
# =========================
else:

    st.markdown(
        '<div class="main-title">⚡ Predicción de Consumo Eléctrico</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">Panel principal de análisis y predicción de consumo eléctrico doméstico.</div>',
        unsafe_allow_html=True
    )

    st.success(
        f"Bienvenido, {st.session_state['nombre_usuario']} "
        f"({st.session_state['correo_usuario']})"
    )

    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">Sistema de predicción basado en historial CFE</div>
        <div class="hero-text">
            Esta aplicación permite registrar manualmente los datos principales de tus recibos,
            consultar tu historial de consumo y generar una estimación del próximo periodo usando
            un modelo conservador diseñado para pocos registros.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Flujo de uso recomendado</div>', unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)

    with s1:
        st.markdown("""
        <div class="step-box">
            <div class="step-title">1. Registro</div>
            <div class="step-text">
                Captura los datos de tus recibos: periodo, kWh e importe pagado.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown("""
        <div class="step-box">
            <div class="step-title">2. Historial</div>
            <div class="step-text">
                Revisa tus datos, edita registros y consulta gráficas históricas.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown("""
        <div class="step-box">
            <div class="step-title">3. Predicción</div>
            <div class="step-text">
                Estima el próximo consumo eléctrico y el posible monto del recibo.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.markdown('<div class="section-title">Características del sistema</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-label">Entrada</div>
            <div class="feature-value">Manual</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-label">Fuente</div>
            <div class="feature-value">Recibo CFE</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-label">Modelo</div>
            <div class="feature-value">Conservador</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-label">Usuarios</div>
            <div class="feature-value">Independientes</div>
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "Cada usuario trabaja con su propio historial mediante el correo electrónico registrado. "
        "Los datos no se mezclan entre usuarios."
    )

    if st.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.session_state["nombre_usuario"] = ""
        st.session_state["correo_usuario"] = ""
        st.rerun()