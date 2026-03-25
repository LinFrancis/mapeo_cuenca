"""
app.py — Inteligencia Territorial
Plataforma de mapeo participativo de cuencas hidrográficas de Chile
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from config import *
from supabase_client import *

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Inteligencia Territorial",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================
# CSS
# ============================================
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; }
    .hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #134E4A 100%);
        padding: 2rem 2.5rem; border-radius: 16px; color: white; margin-bottom: 1.5rem;
        position: relative; overflow: hidden;
    }
    .hero::before {
        content: ''; position: absolute; top: -50%; right: -20%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero h1 { margin: 0 0 0.3rem 0; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.02em; }
    .hero p  { margin: 0; opacity: 0.85; font-size: 0.95rem; }
    .metric-card {
        background: white; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 1.2rem; text-align: center; transition: transform 0.15s;
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
    .metric-card .number { font-size: 2rem; font-weight: 700; line-height: 1.1; }
    .metric-card .label  { font-size: 0.8rem; color: #64748B; margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .edu-box {
        background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%);
        border-left: 4px solid #2563EB; border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.5rem; margin: 1rem 0; font-size: 0.9rem; line-height: 1.6;
    }
    .step-badge {
        display: inline-flex; align-items: center; gap: 0.5rem;
        background: #2563EB; color: white; padding: 0.35rem 0.9rem;
        border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.6rem;
    }
    .cuenca-card {
        background: linear-gradient(135deg, #F0FDF4, #ECFDF5);
        border: 1px solid #BBF7D0; border-radius: 12px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    }
    .cuenca-card .title { font-weight: 600; color: #166534; font-size: 0.85rem; }
    .cuenca-card .value { font-size: 0.95rem; color: #14532D; margin-top: 0.2rem; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%); }
    .tipo-badge { display: inline-block; padding: 0.2rem 0.7rem; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
    .tipo-conflicto  { background: #FEE2E2; color: #991B1B; }
    .tipo-iniciativa  { background: #DCFCE7; color: #166534; }
    .tipo-actor       { background: #DBEAFE; color: #1E40AF; }
    .tipo-oportunidad { background: #FEF3C7; color: #92400E; }
    .demo-banner {
        background: linear-gradient(135deg, #FEF3C7, #FDE68A); border: 2px solid #F59E0B;
        border-radius: 12px; padding: 0.8rem 1.2rem; margin-bottom: 1rem;
        display: flex; align-items: center; gap: 0.5rem; font-size: 0.85rem;
    }
    .footer-livlin {
        text-align: center; padding: 1.5rem 0; margin-top: 3rem;
        border-top: 1px solid #E2E8F0; font-size: 0.8rem; color: #94A3B8;
    }
    .footer-livlin a { color: #2563EB; text-decoration: none; font-weight: 500; }
    .footer-livlin a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)


# ============================================
# SESSION STATE
# ============================================
for key, default in [
    ("user", None), ("profile", None), ("punto_seleccionado", None),
    ("registro_temp", {}), ("cuenca_info", None),
    ("show_cuencas_layer", False), ("demo_mode", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ============================================
# DEMO DATA HELPERS
# ============================================
@st.cache_data
def _load_demo():
    from demo_data import generate_demo_data
    return generate_demo_data()


def get_demo_stats():
    """Construye stats idénticas a get_dashboard_stats pero con datos demo."""
    data = _load_demo()
    obs = data["observaciones"]
    puntos = data["puntos"]

    by_tipo = {}
    for o in obs:
        t = o["tipo"]
        by_tipo[t] = by_tipo.get(t, 0) + 1

    cuencas = set()
    for p in puntos:
        c = p.get("cuenca", "N/A")
        if c and c != "N/A":
            cuencas.add(c)

    dims = {d: {} for d in ["agua", "entorno", "social", "gobernanza", "financiamiento", "regeneracion"]}
    for o in obs:
        for d in dims:
            val = o.get(f"dim_{d}", "NS/NR")
            dims[d][val] = dims[d].get(val, 0) + 1

    return {
        "total": len(obs), "total_puntos": len(puntos),
        "by_tipo": by_tipo, "cuencas_unicas": len(cuencas),
        "cuencas_list": sorted(cuencas), "dimensiones": dims,
        "observaciones": obs, "puntos": puntos,
    }


# ============================================
# HELPERS
# ============================================
def render_hero(subtitle="Mapeando cuencas, construyendo territorio"):
    st.markdown(f"""
    <div class="hero">
        <h1>🌊 Inteligencia Territorial</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_demo_banner():
    if st.session_state.demo_mode:
        st.markdown("""
        <div class="demo-banner">
            <strong>🧪 MODO DEMOSTRACIÓN</strong> — Datos ficticios (100 registros).
            Para ver datos reales, desactiva el modo demo en el sidebar.
        </div>
        """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="footer-livlin">
        ¿Quieres llevar esta plataforma al siguiente nivel? Conversemos →
        <a href="https://livlin.cl" target="_blank">livlin.cl</a><br>
        <span style="font-size:0.7rem; color:#CBD5E1;">Desarrollo de aplicaciones territoriales · Inteligencia de datos · Gobernanza digital</span>
    </div>
    """, unsafe_allow_html=True)


def get_active_stats():
    """Retorna stats de demo o reales según el modo activo."""
    if st.session_state.demo_mode:
        return get_demo_stats()
    return get_dashboard_stats()


# ============================================
# AUTH SCREEN
# ============================================
def pantalla_auth():
    render_hero("Plataforma de mapeo territorial participativo para cuencas de Chile")

    st.markdown("""
    <div class="edu-box">
        <strong>Bienvenido/a</strong> — Esta plataforma permite a comunidades, organizaciones y
        actores territoriales registrar conflictos, iniciativas, actores y oportunidades en las
        cuencas hidrográficas de Chile. Cada punto se ubica geográficamente y se enriquece con
        dimensiones transversales para construir un diagnóstico colectivo del territorio.
    </div>
    """, unsafe_allow_html=True)

    # Demo access
    st.markdown("---")
    col_demo_l, col_demo, col_demo_r = st.columns([1, 2, 1])
    with col_demo:
        st.markdown("#### 🧪 Acceso rápido de demostración")
        st.caption("Explora la plataforma con 100 registros ficticios sin necesidad de crear cuenta.")
        if st.button("Entrar en modo demostración", use_container_width=True, type="secondary"):
            st.session_state.demo_mode = True
            st.session_state.user = "demo"
            st.session_state.profile = {
                "nombre": "Usuario Demo",
                "tipo_actor": "Sociedad Civil",
                "organizacion": "Explorador/a",
                "email": "demo@demo.cl",
            }
            st.rerun()
    st.markdown("---")

    col_l, col_form, col_r = st.columns([1, 2, 1])
    with col_form:
        tab_login, tab_signup = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])

        with tab_login:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Contraseña", type="password")
                submitted = st.form_submit_button("Ingresar", use_container_width=True, type="primary")
                if submitted:
                    if not email or not password:
                        st.error("Completa email y contraseña")
                    else:
                        with st.spinner("Validando..."):
                            result = login_user(email, password)
                            if result["success"]:
                                st.session_state.user = result["user_id"]
                                st.session_state.profile = result["profile"]
                                st.session_state.demo_mode = False
                                st.rerun()
                            else:
                                st.error(result["error"])

        with tab_signup:
            with st.form("signup_form"):
                nombre = st.text_input("Nombre completo")
                email_s = st.text_input("Email", key="signup_email")
                password_s = st.text_input("Contraseña (mín. 6 caracteres)", type="password", key="signup_pass")
                tipo_actor = st.selectbox("Tipo de actor", TIPOS_ACTOR)
                st.markdown("""
                <div style="font-size:0.8rem; color:#64748B; margin:0.5rem 0;">
                    <strong>Tipo de actor</strong>: indica desde qué perspectiva participas.
                </div>
                """, unsafe_allow_html=True)
                submitted_s = st.form_submit_button("Crear Cuenta", use_container_width=True)
                if submitted_s:
                    ok_n, msg_n = validate_nombre(nombre)
                    if not ok_n:
                        st.error(msg_n)
                    elif not validate_email(email_s):
                        st.error("Email inválido")
                    else:
                        ok_p, msg_p = validate_password(password_s)
                        if not ok_p:
                            st.error(msg_p)
                        else:
                            with st.spinner("Creando cuenta..."):
                                result = signup_user(email_s, password_s, nombre, tipo_actor)
                                if result["success"]:
                                    st.success(result["message"])
                                    st.info("Ahora puedes iniciar sesión.")
                                else:
                                    st.error(result["error"])

    render_footer()


# ============================================
# SIDEBAR
# ============================================
def render_sidebar():
    with st.sidebar:
        is_demo = st.session_state.demo_mode
        badge = " 🧪" if is_demo else ""
        st.markdown(f"""
        <div style="padding:1rem; background:white; border-radius:12px; border:1px solid #E2E8F0; margin-bottom:1rem;">
            <div style="font-weight:600; font-size:1rem;">👤 {st.session_state.profile['nombre']}{badge}</div>
            <div style="color:#64748B; font-size:0.8rem; margin-top:0.2rem;">
                {st.session_state.profile['tipo_actor']}
                {(' · ' + st.session_state.profile['organizacion']) if st.session_state.profile.get('organizacion') else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if is_demo:
            secciones = ["🗺️ Mapa Global", "📊 Dashboard", "🔗 Análisis de Red"]
        else:
            secciones = ["📝 Nuevo Registro", "🗺️ Mapa Global", "📊 Dashboard", "🔗 Análisis de Red", "📋 Mis Registros", "⚙️ Perfil"]

        seccion = st.radio("Navegación", secciones, label_visibility="collapsed")

        st.divider()

        # Demo toggle
        demo_val = st.toggle("🧪 Modo demostración", value=st.session_state.demo_mode)
        if demo_val != st.session_state.demo_mode:
            st.session_state.demo_mode = demo_val
            if demo_val:
                st.session_state.user = "demo"
                st.session_state.profile = {
                    "nombre": "Usuario Demo", "tipo_actor": "Sociedad Civil",
                    "organizacion": "Explorador/a", "email": "demo@demo.cl",
                }
            else:
                st.session_state.user = None
                st.session_state.profile = None
            st.rerun()

        with st.expander("ℹ️ ¿Cómo usar esta plataforma?", expanded=False):
            st.markdown("""
            **Nuevo Registro**: Clic en mapa → formulario → guardar.

            **Mapa Global**: Todos los registros con filtros.

            **Dashboard**: Gráficos y diagnóstico multidimensional.

            **Análisis de Red**: Conexiones entre actores, conflictos e iniciativas.

            **Mis Registros**: Tus aportes personales.
            """)

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for k in ["user", "profile", "punto_seleccionado", "registro_temp", "cuenca_info"]:
                st.session_state[k] = None if k != "registro_temp" else {}
            st.session_state.demo_mode = False
            st.rerun()

        return seccion


# ============================================
# NUEVO REGISTRO
# ============================================
def seccion_nuevo_registro():
    render_hero("Contribuye al mapa territorial de tu cuenca")
    if st.session_state.demo_mode:
        st.warning("El modo demo es solo lectura. Desactívalo para crear registros reales.")
        return

    st.markdown(INTRO_APP, unsafe_allow_html=True)

    # PASO 1
    st.markdown('<div class="step-badge">1 — UBICACIÓN</div>', unsafe_allow_html=True)
    st.markdown("Haz **clic en el mapa** para seleccionar la ubicación.")
    st.markdown(f'<div class="edu-box">{INTRO_CUENCA}</div>', unsafe_allow_html=True)

    col_map, col_info = st.columns([3, 1])
    with col_map:
        m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="OpenStreetMap")
        try:
            from geo_utils import get_cuencas_geojson
            cuencas_gdf = get_cuencas_geojson()
            if cuencas_gdf is not None and st.session_state.get("show_cuencas_layer"):
                folium.GeoJson(cuencas_gdf.to_json(), style_function=lambda x: {
                    "fillColor": "#3B82F6", "color": "#1E40AF", "weight": 1, "fillOpacity": 0.08,
                }).add_to(m)
        except Exception:
            pass
        map_data = st_folium(m, width=None, height=450, returned_objects=["last_clicked"])

    with col_info:
        st.session_state.show_cuencas_layer = st.toggle("Mostrar cuencas BNA", value=st.session_state.get("show_cuencas_layer", False))
        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]
            st.session_state.punto_seleccionado = {"lat": lat, "lon": lon}
            st.success("📍 Punto seleccionado")
            st.metric("Latitud", f"{lat:.4f}")
            st.metric("Longitud", f"{lon:.4f}")
            with st.spinner("Identificando cuenca..."):
                try:
                    from geo_utils import identify_cuenca
                    ci = identify_cuenca(lat, lon)
                    st.session_state.cuenca_info = ci
                    for level, label in [("cuenca", "🏔️ Cuenca"), ("subcuenca", "🏞️ Subcuenca"), ("subsubcuenca", "💧 Subsubcuenca")]:
                        val = ci[level]
                        color = "#166534" if val != "No identificada" else "#92400E"
                        st.markdown(f'<div class="cuenca-card"><div class="title">{label}</div><div class="value" style="color:{color}">{val}</div></div>', unsafe_allow_html=True)
                except Exception:
                    st.session_state.cuenca_info = {"cuenca": "N/A", "subcuenca": "N/A", "subsubcuenca": "N/A"}
        else:
            st.info("👆 Haz clic en el mapa")

    if not st.session_state.punto_seleccionado:
        return

    st.divider()

    # PASO 2
    st.markdown('<div class="step-badge">2 — TIPO DE REGISTRO</div>', unsafe_allow_html=True)
    tipos_desc = {
        "Conflicto": "Situaciones de tensión o daño socioambiental.",
        "Iniciativa": "Acciones positivas de restauración o gestión.",
        "Actor": "Personas u organizaciones relevantes en el territorio.",
        "Oportunidad": "Ventanas de acción o financiamiento.",
    }
    tipo_registro = st.radio("Tipo", TIPOS_REGISTRO, horizontal=True, label_visibility="collapsed")
    st.markdown(f'<div class="edu-box"><strong>{EMOJIS[tipo_registro]} {tipo_registro}</strong>: {tipos_desc[tipo_registro]}</div>', unsafe_allow_html=True)

    st.divider()

    # PASO 3
    st.markdown('<div class="step-badge">3 — INFORMACIÓN GENERAL</div>', unsafe_allow_html=True)
    titulo = st.text_input("📌 Título", max_chars=MAX_TITULO, placeholder="Ej: Sequía en río Maule")
    descripcion = st.text_area("📝 Descripción", max_chars=MAX_DESCRIPCION, placeholder="Contexto territorial...", height=120)

    st.divider()

    # PASO 4
    st.markdown(f'<div class="step-badge">4 — DETALLE: {tipo_registro.upper()}</div>', unsafe_allow_html=True)
    modulo = {}
    if tipo_registro == "Conflicto":
        c1, c2, c3 = st.columns(3)
        with c1: modulo["actores"] = st.text_input("Actores involucrados")
        with c2: modulo["gravedad"] = st.selectbox("Gravedad", CONFLICTO_GRAVEDAD)
        with c3: modulo["dialogo"] = st.selectbox("Diálogo", CONFLICTO_DIALOGO)
        modulo["duracion"] = st.selectbox("Duración", CONFLICTO_DURACION)
    elif tipo_registro == "Iniciativa":
        modulo["tipos"] = st.multiselect("Tipos", INICIATIVA_TIPOS, max_selections=3)
        c1, c2 = st.columns(2)
        with c1: modulo["estado"] = st.selectbox("Estado", INICIATIVA_ESTADO)
        with c2: modulo["escala"] = st.selectbox("Escala", INICIATIVA_ESCALA)
    elif tipo_registro == "Actor":
        c1, c2 = st.columns(2)
        with c1: modulo["nombre"] = st.text_input("Nombre")
        with c2: modulo["tipo"] = st.selectbox("Tipo", ACTOR_TIPO)
    elif tipo_registro == "Oportunidad":
        c1, c2 = st.columns(2)
        with c1: modulo["viabilidad"] = st.selectbox("Viabilidad", OPORTUNIDAD_VIABILIDAD)
        with c2: modulo["urgencia"] = st.selectbox("Urgencia", OPORTUNIDAD_URGENCIA)
        modulo["brechas"] = st.multiselect("Brechas", OPORTUNIDAD_BRECHAS)

    st.divider()

    # PASO 5
    st.markdown('<div class="step-badge">5 — DIMENSIONES TRANSVERSALES</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="edu-box">{INTRO_DIMENSIONES}</div>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1:
        dim_agua = st.selectbox("💧 Agua", DIM_AGUA)
        dim_entorno = st.selectbox("🌿 Entorno", DIM_ENTORNO)
    with d2:
        dim_social = st.selectbox("👥 Social", DIM_SOCIAL)
        dim_gobernanza = st.selectbox("🏛️ Gobernanza", DIM_GOBERNANZA)
    with d3:
        dim_financ = st.selectbox("💰 Financiamiento", DIM_FINANCIAMIENTO)
        dim_regen = st.selectbox("♻️ Regeneración", DIM_REGENERACION)
    importancia = st.text_area("🎯 ¿Por qué es importante?", max_chars=MAX_IMPORTANCIA, height=80)

    st.divider()

    # PASO 6
    st.markdown('<div class="step-badge">6 — GUARDAR</div>', unsafe_allow_html=True)
    if st.button("💾 Guardar Registro", use_container_width=True, type="primary"):
        if not titulo or not descripcion:
            st.error("Completa título y descripción.")
            return
        ci = st.session_state.cuenca_info or {"cuenca": "N/A", "subcuenca": "N/A", "subsubcuenca": "N/A"}
        p = st.session_state.punto_seleccionado
        with st.spinner("Guardando..."):
            punto_id = create_punto(st.session_state.user, p["lat"], p["lon"], ci["cuenca"], ci["subcuenca"], ci["subsubcuenca"])
            if punto_id:
                obs_id = create_observacion(st.session_state.user, punto_id, tipo_registro, titulo, descripcion,
                    {"agua": dim_agua, "entorno": dim_entorno, "social": dim_social,
                     "gobernanza": dim_gobernanza, "financiamiento": dim_financ,
                     "regeneracion": dim_regen, "importancia_lugar": importancia}, modulo)
                if obs_id:
                    st.success(f"✅ Registro guardado (ID: {obs_id})")
                    st.balloons()
                    st.session_state.punto_seleccionado = None
                    st.session_state.cuenca_info = None


# ============================================
# MAPA GLOBAL
# ============================================
def seccion_mapa_global():
    render_hero("Visualiza todos los registros territoriales")
    render_demo_banner()

    st.markdown("""
    <div class="edu-box">
        Cada marcador representa un registro: <strong style="color:#EF4444">rojo</strong> = conflicto,
        <strong style="color:#22C55E">verde</strong> = iniciativa,
        <strong style="color:#3B82F6">azul</strong> = actor,
        <strong style="color:#F59E0B">naranja</strong> = oportunidad.
    </div>
    """, unsafe_allow_html=True)

    stats = get_active_stats()
    if not stats or stats.get("total", 0) == 0:
        st.info("No hay datos disponibles.")
        return

    obs = stats["observaciones"]
    puntos = stats["puntos"]
    puntos_map = {p["id"]: p for p in puntos}

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_tipos = st.multiselect("Filtrar por tipo", TIPOS_REGISTRO, default=TIPOS_REGISTRO)
    with col_f2:
        filtro_cuenca = st.selectbox("Filtrar por cuenca", ["Todas"] + stats.get("cuencas_list", []))

    filtered = []
    for o in obs:
        if o["tipo"] not in filtro_tipos:
            continue
        p = puntos_map.get(o["punto_id"])
        if not p:
            continue
        if filtro_cuenca != "Todas" and p.get("cuenca") != filtro_cuenca:
            continue
        filtered.append((o, p))

    st.caption(f"Mostrando **{len(filtered)}** registros")

    m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="CartoDB positron")
    for o, p in filtered:
        tipo = o["tipo"]
        popup_html = f"""
        <div style="max-width:260px; font-family:sans-serif;">
            <strong>{o['titulo']}</strong><br>
            <span style="color:{COLORS[tipo]}; font-weight:600;">{EMOJIS[tipo]} {tipo}</span><br>
            <small>{o.get('descripcion', '')[:150]}...</small><br>
            <small style="color:#888;">📍 {p.get('cuenca', 'N/A')} → {p.get('subcuenca', '')}</small>
        </div>"""
        folium.Marker(
            location=[p["lat"], p["lon"]],
            popup=folium.Popup(popup_html, max_width=280),
            icon=folium.Icon(color=FOLIUM_COLORS.get(tipo, "gray"), icon=FOLIUM_ICONS.get(tipo, "info-sign"), prefix="fa"),
        ).add_to(m)

    st_folium(m, width=None, height=550, returned_objects=[])
    render_footer()


# ============================================
# DASHBOARD
# ============================================
def seccion_dashboard():
    render_hero("Diagnóstico territorial colectivo")
    render_demo_banner()

    st.markdown("""
    <div class="edu-box">
        El dashboard agrega los registros de todos los participantes para mostrar una
        <strong>radiografía del territorio</strong>. Las dimensiones transversales revelan
        patrones: dónde falta agua, dónde la gobernanza es débil, dónde hay potencial
        de regeneración.
    </div>
    """, unsafe_allow_html=True)

    stats = get_active_stats()
    if not stats or stats.get("total", 0) == 0:
        st.info("Aún no hay registros.")
        return

    by_tipo = stats.get("by_tipo", {})

    # Métricas
    cols = st.columns(5)
    metrics = [
        (stats['total'], "Total", "#1E293B"),
        (by_tipo.get('Conflicto', 0), "Conflictos", COLORS["Conflicto"]),
        (by_tipo.get('Iniciativa', 0), "Iniciativas", COLORS["Iniciativa"]),
        (by_tipo.get('Actor', 0), "Actores", COLORS["Actor"]),
        (by_tipo.get('Oportunidad', 0), "Oportunidades", COLORS["Oportunidad"]),
    ]
    for col, (num, label, color) in zip(cols, metrics):
        col.markdown(f'<div class="metric-card"><div class="number" style="color:{color}">{num}</div><div class="label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts row 1
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución por tipo")
        fig = px.pie(names=list(by_tipo.keys()), values=list(by_tipo.values()),
                     color=list(by_tipo.keys()), color_discrete_map=COLORS, hole=0.45)
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320,
                         legend=dict(orientation="h", yanchor="bottom", y=-0.15))
        fig.update_traces(textinfo="percent+label", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Radar de dimensiones")
        dims = stats.get("dimensiones", {})
        score_map = {
            "agua": {"Muy escasa": 1, "Escasa": 2, "Suficiente": 3, "Abundante": 4},
            "entorno": {"Muy degradado": 1, "Degradado": 2, "En recuperación": 3, "Conservado": 4},
            "social": {"Muy débil": 1, "Débil": 2, "Media": 3, "Fuerte": 4},
            "gobernanza": {"Muy débil": 1, "Débil": 2, "Media": 3, "Fuerte": 4},
            "financiamiento": {"Muy difícil": 1, "Difícil": 2, "Medio": 3, "Fácil": 4},
            "regeneracion": {"Bajo": 1, "Medio": 2, "Alto": 3},
        }
        dim_labels = {"agua": "💧 Agua", "entorno": "🌿 Entorno", "social": "👥 Social",
                     "gobernanza": "🏛️ Gobernanza", "financiamiento": "💰 Financ.", "regeneracion": "♻️ Regen."}
        radar_vals, radar_labels = [], []
        for d, label in dim_labels.items():
            vals = dims.get(d, {})
            smap = score_map.get(d, {})
            total_s, total_c = 0, 0
            for val, count in vals.items():
                s = smap.get(val, 0)
                if s > 0:
                    total_s += s * count
                    total_c += count
            avg = (total_s / total_c) if total_c > 0 else 0
            mx = max(smap.values()) if smap else 4
            radar_vals.append(round((avg / mx) * 100, 1))
            radar_labels.append(label)

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=radar_vals + [radar_vals[0]], theta=radar_labels + [radar_labels[0]],
                                       fill="toself", fillcolor="rgba(37,99,235,0.15)", line=dict(color="#2563EB", width=2)))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)),
                         margin=dict(t=30, b=30, l=60, r=60), height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Charts row 2 — by cuenca
    st.divider()
    st.subheader("Distribución por cuenca")

    puntos = stats["puntos"]
    obs = stats["observaciones"]
    puntos_map = {p["id"]: p for p in puntos}

    cuenca_data = {}
    for o in obs:
        p = puntos_map.get(o["punto_id"])
        if p:
            c = p.get("cuenca", "N/A")
            if c and c != "N/A":
                if c not in cuenca_data:
                    cuenca_data[c] = {"Conflicto": 0, "Iniciativa": 0, "Actor": 0, "Oportunidad": 0}
                cuenca_data[c][o["tipo"]] = cuenca_data[c].get(o["tipo"], 0) + 1

    if cuenca_data:
        rows = []
        for cuenca, tipos in cuenca_data.items():
            for tipo, count in tipos.items():
                if count > 0:
                    rows.append({"Cuenca": cuenca, "Tipo": tipo, "Cantidad": count})
        df_bar = pd.DataFrame(rows)
        fig = px.bar(df_bar, x="Cuenca", y="Cantidad", color="Tipo", color_discrete_map=COLORS,
                     barmode="stack")
        fig.update_layout(margin=dict(t=20, b=20), height=350, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    # Dimensiones por cuenca (heatmap)
    st.divider()
    st.subheader("Dimensiones por cuenca")
    st.caption("Promedio normalizado (0-100) de cada dimensión por cuenca. Rojo = más crítico.")

    cuenca_dims = {}
    for o in obs:
        p = puntos_map.get(o["punto_id"])
        if not p:
            continue
        c = p.get("cuenca", "N/A")
        if c == "N/A":
            continue
        if c not in cuenca_dims:
            cuenca_dims[c] = {d: [] for d in score_map}
        for d, smap in score_map.items():
            val = o.get(f"dim_{d}", "NS/NR")
            s = smap.get(val, 0)
            if s > 0:
                cuenca_dims[c][d].append(s)

    if cuenca_dims:
        heatmap_rows = []
        for c, dims_data in cuenca_dims.items():
            row = {"Cuenca": c}
            for d, label in dim_labels.items():
                vals = dims_data.get(d, [])
                mx = max(score_map[d].values()) if score_map.get(d) else 4
                avg = (sum(vals) / len(vals) / mx * 100) if vals else 0
                row[label] = round(avg, 0)
            heatmap_rows.append(row)
        df_heat = pd.DataFrame(heatmap_rows).set_index("Cuenca")

        fig = px.imshow(df_heat, aspect="auto",
                        color_continuous_scale=["#EF4444", "#FCD34D", "#22C55E"],
                        labels=dict(color="Score %"))
        fig.update_layout(margin=dict(t=20, b=20), height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Timeline
    st.divider()
    st.subheader("Actividad reciente")
    for o in obs[:12]:
        tipo = o["tipo"]
        fecha = o.get("created_at", "")[:10]
        badge = f"tipo-{tipo.lower()}"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.8rem; padding:0.5rem 0; border-bottom:1px solid #F1F5F9;">
            <span class="tipo-badge {badge}">{EMOJIS[tipo]} {tipo}</span>
            <span style="flex:1; font-size:0.9rem;"><strong>{o['titulo']}</strong></span>
            <span style="color:#94A3B8; font-size:0.8rem;">{fecha}</span>
        </div>""", unsafe_allow_html=True)

    render_footer()


# ============================================
# ANÁLISIS DE RED
# ============================================
def seccion_analisis_red():
    render_hero("Análisis de conexiones territoriales")
    render_demo_banner()

    st.markdown("""
    <div class="edu-box">
        <strong>¿Por qué analizar las conexiones?</strong> Los conflictos, iniciativas, actores y oportunidades
        de un territorio no son independientes: un conflicto por agua puede estar vinculado a una iniciativa
        de monitoreo, que a su vez involucra a un actor comunitario y abre una oportunidad de financiamiento.
        Este análisis revela esas <strong>relaciones ocultas</strong> entre registros que comparten
        ubicación, cuenca o actores.
    </div>
    """, unsafe_allow_html=True)

    stats = get_active_stats()
    if not stats or stats.get("total", 0) < 5:
        st.info("Se necesitan al menos 5 registros para el análisis de red.")
        return

    obs = stats["observaciones"]
    puntos = stats["puntos"]
    puntos_map = {p["id"]: p for p in puntos}

    # ---- 1. MATRIZ DE CO-OCURRENCIA POR SUBCUENCA ----
    st.subheader("🗺️ Co-ocurrencia territorial")
    st.caption("¿Qué tipos de registro aparecen juntos en las mismas subcuencas? Una alta co-ocurrencia de conflictos e iniciativas sugiere que la comunidad está respondiendo activamente.")

    sub_tipos = {}
    for o in obs:
        p = puntos_map.get(o["punto_id"])
        if not p:
            continue
        sub = p.get("subcuenca", "N/A")
        if sub == "N/A":
            continue
        if sub not in sub_tipos:
            sub_tipos[sub] = []
        sub_tipos[sub].append(o["tipo"])

    # Construir matriz
    tipos_list = ["Conflicto", "Iniciativa", "Actor", "Oportunidad"]
    cooc = pd.DataFrame(0, index=tipos_list, columns=tipos_list)
    for sub, tipos in sub_tipos.items():
        for t1 in tipos_list:
            for t2 in tipos_list:
                if t1 in tipos and t2 in tipos:
                    cooc.loc[t1, t2] += 1

    fig = px.imshow(cooc, text_auto=True, color_continuous_scale=["#F8FAFC", "#2563EB"],
                    labels=dict(color="Subcuencas"))
    fig.update_layout(margin=dict(t=20, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ---- 2. ACTORES Y SUS CONEXIONES ----
    st.subheader("👥 Red de actores")
    st.caption("Actores mencionados en conflictos e iniciativas. El tamaño indica frecuencia de mención. Actores que aparecen en múltiples subcuencas son nodos articuladores del territorio.")

    actor_mentions = {}
    for o in obs:
        p = puntos_map.get(o["punto_id"])
        sub = p.get("subcuenca", "N/A") if p else "N/A"

        names = []
        if o.get("actor_nombre"):
            names.append(o["actor_nombre"])
        if o.get("conflicto_actores_involucrados"):
            # Extraer nombres de la cadena "X vs Y"
            parts = o["conflicto_actores_involucrados"].replace(" vs ", "|").replace(" y ", "|").split("|")
            names.extend([p.strip() for p in parts if p.strip()])

        for name in names:
            if name not in actor_mentions:
                actor_mentions[name] = {"count": 0, "subcuencas": set(), "tipos": set(), "cuencas": set()}
            actor_mentions[name]["count"] += 1
            actor_mentions[name]["subcuencas"].add(sub)
            actor_mentions[name]["tipos"].add(o["tipo"])
            if p:
                actor_mentions[name]["cuencas"].add(p.get("cuenca", "N/A"))

    if actor_mentions:
        actor_rows = []
        for name, data in sorted(actor_mentions.items(), key=lambda x: -x[1]["count"]):
            actor_rows.append({
                "Actor": name,
                "Menciones": data["count"],
                "Subcuencas": len(data["subcuencas"]),
                "Cuencas": ", ".join(sorted(data["cuencas"])),
                "Tipos vinculados": ", ".join(sorted(data["tipos"])),
                "Alcance": "🔴 Multi-cuenca" if len(data["cuencas"]) > 1 else "🟢 Local",
            })
        df_actors = pd.DataFrame(actor_rows)

        # Bubble chart
        fig = px.scatter(df_actors, x="Subcuencas", y="Menciones", size="Menciones",
                        color="Alcance", text="Actor",
                        color_discrete_map={"🔴 Multi-cuenca": "#EF4444", "🟢 Local": "#22C55E"})
        fig.update_traces(textposition="top center", textfont_size=10)
        fig.update_layout(margin=dict(t=20, b=20), height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Tabla completa de actores"):
            st.dataframe(df_actors, use_container_width=True, hide_index=True)

    st.divider()

    # ---- 3. CONFLICTO ↔ RESPUESTA ----
    st.subheader("⚡ Mapa conflicto → respuesta")
    st.caption("¿Las subcuencas con más conflictos también tienen más iniciativas? Un ratio alto de iniciativas/conflictos indica capacidad de respuesta comunitaria.")

    sub_balance = {}
    for o in obs:
        p = puntos_map.get(o["punto_id"])
        if not p:
            continue
        sub = p.get("subcuenca", "N/A")
        if sub == "N/A":
            continue
        if sub not in sub_balance:
            sub_balance[sub] = {"Conflicto": 0, "Iniciativa": 0, "Oportunidad": 0, "Actor": 0,
                                "cuenca": p.get("cuenca", "")}
        sub_balance[sub][o["tipo"]] += 1

    if sub_balance:
        balance_rows = []
        for sub, data in sub_balance.items():
            conf = data["Conflicto"]
            ini = data["Iniciativa"]
            ratio = round(ini / conf, 2) if conf > 0 else (999 if ini > 0 else 0)
            balance_rows.append({
                "Subcuenca": sub,
                "Cuenca": data["cuenca"],
                "Conflictos": conf,
                "Iniciativas": ini,
                "Oportunidades": data["Oportunidad"],
                "Ratio I/C": ratio,
                "Estado": "✅ Respuesta activa" if ratio >= 1 else ("⚠️ Brecha" if ratio > 0 else "🔴 Sin respuesta"),
            })
        df_balance = pd.DataFrame(balance_rows).sort_values("Conflictos", ascending=False)

        fig = px.scatter(df_balance, x="Conflictos", y="Iniciativas", size="Oportunidades",
                        color="Estado", hover_name="Subcuenca",
                        color_discrete_map={"✅ Respuesta activa": "#22C55E", "⚠️ Brecha": "#F59E0B", "🔴 Sin respuesta": "#EF4444"})
        # Línea de equilibrio
        max_val = max(df_balance["Conflictos"].max(), df_balance["Iniciativas"].max(), 1)
        fig.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val], mode="lines",
                                 line=dict(dash="dash", color="#94A3B8"), name="Equilibrio 1:1", showlegend=True))
        fig.update_layout(margin=dict(t=20, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("📋 Tabla de balance por subcuenca"):
            st.dataframe(df_balance, use_container_width=True, hide_index=True)

    st.divider()

    # ---- 4. BRECHAS Y OPORTUNIDADES ----
    st.subheader("🎯 Mapa de brechas")
    st.caption("Las brechas más mencionadas en las oportunidades señalan dónde hay que concentrar esfuerzos.")

    brechas_count = {}
    for o in obs:
        if o["tipo"] == "Oportunidad":
            brechas = o.get("oportunidad_brechas", [])
            if isinstance(brechas, list):
                for b in brechas:
                    brechas_count[b] = brechas_count.get(b, 0) + 1

    if brechas_count:
        df_brechas = pd.DataFrame([
            {"Brecha": k, "Menciones": v}
            for k, v in sorted(brechas_count.items(), key=lambda x: -x[1])
        ])
        fig = px.bar(df_brechas, x="Menciones", y="Brecha", orientation="h",
                     color="Menciones", color_continuous_scale=["#FDE68A", "#EF4444"])
        fig.update_layout(margin=dict(t=20, b=20, l=10), height=300, showlegend=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    render_footer()


# ============================================
# MIS REGISTROS
# ============================================
def seccion_mis_registros():
    render_hero("Tus aportes al mapa territorial")
    if st.session_state.demo_mode:
        st.info("En modo demo no hay registros personales.")
        return

    mis_obs = get_observaciones_by_user(st.session_state.user)
    if not mis_obs:
        st.info("No has creado registros aún. Ve a **Nuevo Registro**.")
        return

    st.write(f"Has contribuido con **{len(mis_obs)}** registros.")
    for obs_item in mis_obs:
        tipo = obs_item["tipo"]
        fecha = obs_item.get("created_at", "")[:10]
        with st.expander(f"{EMOJIS[tipo]} **{obs_item['titulo']}** — {tipo} · {fecha}"):
            st.write(obs_item.get("descripcion", ""))
            dims_display = {"💧": obs_item.get("dim_agua"), "🌿": obs_item.get("dim_entorno"),
                           "👥": obs_item.get("dim_social"), "🏛️": obs_item.get("dim_gobernanza"),
                           "💰": obs_item.get("dim_financiamiento"), "♻️": obs_item.get("dim_regeneracion")}
            cols = st.columns(6)
            for col, (emoji, val) in zip(cols, dims_display.items()):
                col.caption(emoji)
                col.write(val or "NS/NR")
            if st.button(f"🗑️ Eliminar", key=f"del_{obs_item['id']}"):
                if delete_observacion(obs_item["id"], st.session_state.user):
                    st.success("Eliminado")
                    st.rerun()

    render_footer()


# ============================================
# PERFIL
# ============================================
def seccion_perfil():
    render_hero("Tu información de participante")
    if st.session_state.demo_mode:
        st.info("Perfil no editable en modo demo.")
        return
    profile = st.session_state.profile
    with st.form("profile_form"):
        nombre = st.text_input("Nombre", value=profile.get("nombre", ""))
        st.text_input("Email", value=profile.get("email", ""), disabled=True)
        organizacion = st.text_input("Organización", value=profile.get("organizacion", "") or "")
        tipo_actor = st.selectbox("Tipo de actor", TIPOS_ACTOR,
                                  index=TIPOS_ACTOR.index(profile["tipo_actor"]) if profile.get("tipo_actor") in TIPOS_ACTOR else 0)
        if st.form_submit_button("💾 Guardar", use_container_width=True):
            if update_user_profile(st.session_state.user, {"nombre": nombre, "organizacion": organizacion, "tipo_actor": tipo_actor}):
                st.session_state.profile.update({"nombre": nombre, "organizacion": organizacion, "tipo_actor": tipo_actor})
                st.success("✅ Actualizado")

    render_footer()


# ============================================
# MAIN
# ============================================
def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        render_hero("Error de configuración")
        st.error("**No se encontraron las credenciales de Supabase.** Configura los secrets.")
        st.markdown("---")
        st.markdown("#### 🧪 ¿Solo quieres explorar?")
        if st.button("Entrar en modo demostración", type="primary"):
            st.session_state.demo_mode = True
            st.session_state.user = "demo"
            st.session_state.profile = {"nombre": "Usuario Demo", "tipo_actor": "Sociedad Civil", "organizacion": "Explorador/a", "email": "demo@demo.cl"}
            st.rerun()
        render_footer()
        return

    conn_ok = test_connection()

    if not st.session_state.user:
        if not conn_ok:
            render_hero("Sin conexión a Supabase")
            st.warning("No se pudo conectar a la base de datos. Puedes explorar con datos de demostración.")
            if st.button("Entrar en modo demostración", type="primary"):
                st.session_state.demo_mode = True
                st.session_state.user = "demo"
                st.session_state.profile = {"nombre": "Usuario Demo", "tipo_actor": "Sociedad Civil", "organizacion": "Explorador/a", "email": "demo@demo.cl"}
                st.rerun()
            render_footer()
            return
        pantalla_auth()
        return

    seccion = render_sidebar()

    if seccion == "📝 Nuevo Registro":
        seccion_nuevo_registro()
    elif seccion == "🗺️ Mapa Global":
        seccion_mapa_global()
    elif seccion == "📊 Dashboard":
        seccion_dashboard()
    elif seccion == "🔗 Análisis de Red":
        seccion_analisis_red()
    elif seccion == "📋 Mis Registros":
        seccion_mis_registros()
    elif seccion == "⚙️ Perfil":
        seccion_perfil()


if __name__ == "__main__":
    main()
