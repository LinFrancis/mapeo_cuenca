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
# CSS PERSONALIZADO
# ============================================
st.markdown("""
<style>
    /* Tipografía y espaciado general */
    .block-container { padding-top: 1.5rem; }

    /* Header hero */
    .hero {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #134E4A 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .hero::before {
        content: '';
        position: absolute;
        top: -50%; right: -20%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
        pointer-events: none;
    }
    .hero h1 { margin: 0 0 0.3rem 0; font-size: 1.8rem; font-weight: 700; letter-spacing: -0.02em; }
    .hero p  { margin: 0; opacity: 0.85; font-size: 0.95rem; }

    /* Tarjetas de métricas */
    .metric-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        transition: transform 0.15s;
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
    .metric-card .number { font-size: 2rem; font-weight: 700; line-height: 1.1; }
    .metric-card .label  { font-size: 0.8rem; color: #64748B; margin-top: 0.3rem; text-transform: uppercase; letter-spacing: 0.05em; }

    /* Info boxes educativas */
    .edu-box {
        background: linear-gradient(135deg, #EFF6FF 0%, #F0FDF4 100%);
        border-left: 4px solid #2563EB;
        border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* Step indicator */
    .step-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: #2563EB;
        color: white;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
    }

    /* Cuenca info card */
    .cuenca-card {
        background: linear-gradient(135deg, #F0FDF4, #ECFDF5);
        border: 1px solid #BBF7D0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
    }
    .cuenca-card .title { font-weight: 600; color: #166534; font-size: 0.85rem; }
    .cuenca-card .value { font-size: 0.95rem; color: #14532D; margin-top: 0.2rem; }

    /* Auth container */
    .auth-container {
        max-width: 480px;
        margin: 2rem auto;
        padding: 2rem;
        background: white;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F8FAFC 0%, #F1F5F9 100%);
    }

    /* Reduce spacing in forms */
    .stSelectbox, .stTextInput, .stTextArea { margin-bottom: 0.3rem; }

    /* Tipo badges */
    .tipo-badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .tipo-conflicto  { background: #FEE2E2; color: #991B1B; }
    .tipo-iniciativa  { background: #DCFCE7; color: #166534; }
    .tipo-actor       { background: #DBEAFE; color: #1E40AF; }
    .tipo-oportunidad { background: #FEF3C7; color: #92400E; }
</style>
""", unsafe_allow_html=True)


# ============================================
# SESSION STATE DEFAULTS
# ============================================
for key, default in [
    ("user", None),
    ("profile", None),
    ("punto_seleccionado", None),
    ("registro_temp", {}),
    ("cuenca_info", None),
    ("show_cuencas_layer", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ============================================
# HELPER: HERO BANNER
# ============================================
def render_hero(subtitle="Mapeando cuencas, construyendo territorio"):
    st.markdown(f"""
    <div class="hero">
        <h1>🌊 Inteligencia Territorial</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================
# PANTALLA DE AUTENTICACIÓN
# ============================================
def pantalla_auth():
    render_hero("Plataforma de mapeo territorial participativo para cuencas de Chile")

    # Explicación educativa
    st.markdown("""
    <div class="edu-box">
        <strong>Bienvenido/a</strong> — Esta plataforma permite a comunidades, organizaciones y
        actores territoriales registrar conflictos, iniciativas, actores y oportunidades en las
        cuencas hidrográficas de Chile. Cada punto se ubica geográficamente y se enriquece con
        dimensiones transversales para construir un diagnóstico colectivo del territorio.
    </div>
    """, unsafe_allow_html=True)

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
                    <strong>¿Qué es el tipo de actor?</strong> Indica desde qué perspectiva
                    participas: sociedad civil, sector público, privado, academia u otro.
                    Esto ayuda a entender la diversidad de voces en el territorio.
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


# ============================================
# SIDEBAR
# ============================================
def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:1rem; background:white; border-radius:12px; border:1px solid #E2E8F0; margin-bottom:1rem;">
            <div style="font-weight:600; font-size:1rem;">👤 {st.session_state.profile['nombre']}</div>
            <div style="color:#64748B; font-size:0.8rem; margin-top:0.2rem;">
                {st.session_state.profile['tipo_actor']}
                {(' · ' + st.session_state.profile['organizacion']) if st.session_state.profile.get('organizacion') else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)

        seccion = st.radio(
            "Navegación",
            ["📝 Nuevo Registro", "🗺️ Mapa Global", "📊 Dashboard", "📋 Mis Registros", "⚙️ Perfil"],
            label_visibility="collapsed",
        )

        st.divider()

        # Ayuda contextual
        with st.expander("ℹ️ ¿Cómo usar esta plataforma?", expanded=False):
            st.markdown("""
            **1. Nuevo Registro**: Haz clic en el mapa para ubicar un punto,
            luego completa el formulario con la información territorial.

            **2. Mapa Global**: Visualiza todos los registros de la comunidad
            en un mapa interactivo con filtros por tipo y cuenca.

            **3. Dashboard**: Estadísticas y gráficos del estado del territorio
            según los registros de todos los participantes.

            **4. Mis Registros**: Lista de tus aportes con opción de eliminar.

            **5. Perfil**: Actualiza tu información personal.
            """)

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for k in ["user", "profile", "punto_seleccionado", "registro_temp", "cuenca_info"]:
                st.session_state[k] = None if k != "registro_temp" else {}
            st.rerun()

        return seccion


# ============================================
# SECCIÓN: NUEVO REGISTRO
# ============================================
def seccion_nuevo_registro():
    render_hero("Contribuye al mapa territorial de tu cuenca")

    st.markdown(INTRO_APP, unsafe_allow_html=True)

    # ---- PASO 1: UBICACIÓN ----
    st.markdown('<div class="step-badge">1 — UBICACIÓN</div>', unsafe_allow_html=True)
    st.markdown("Haz **clic en el mapa** para seleccionar la ubicación del registro.")

    st.markdown(f"""
    <div class="edu-box">
        {INTRO_CUENCA}
    </div>
    """, unsafe_allow_html=True)

    col_map, col_info = st.columns([3, 1])

    with col_map:
        m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="OpenStreetMap")

        # Agregar capa de cuencas si está disponible
        try:
            from geo_utils import get_cuencas_geojson
            cuencas_gdf = get_cuencas_geojson()
            if cuencas_gdf is not None and st.session_state.get("show_cuencas_layer"):
                folium.GeoJson(
                    cuencas_gdf.to_json(),
                    style_function=lambda x: {
                        "fillColor": "#3B82F6",
                        "color": "#1E40AF",
                        "weight": 1,
                        "fillOpacity": 0.08,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=cuencas_gdf.columns.drop("geometry").tolist()[:2],
                        aliases=["Cuenca", "Código"][:2],
                    ),
                ).add_to(m)
        except ImportError:
            pass
        except Exception:
            pass

        map_data = st_folium(m, width=None, height=450, returned_objects=["last_clicked"])

    with col_info:
        # Toggle cuencas layer
        st.session_state.show_cuencas_layer = st.toggle(
            "Mostrar cuencas BNA", value=st.session_state.get("show_cuencas_layer", False)
        )

        if map_data and map_data.get("last_clicked"):
            lat = map_data["last_clicked"]["lat"]
            lon = map_data["last_clicked"]["lng"]
            st.session_state.punto_seleccionado = {"lat": lat, "lon": lon}

            st.success("📍 Punto seleccionado")
            st.metric("Latitud", f"{lat:.4f}")
            st.metric("Longitud", f"{lon:.4f}")

            # Detección automática de cuenca
            with st.spinner("Identificando cuenca..."):
                try:
                    from geo_utils import identify_cuenca
                    cuenca_info = identify_cuenca(lat, lon)
                    st.session_state.cuenca_info = cuenca_info

                    for level, label in [("cuenca", "🏔️ Cuenca"), ("subcuenca", "🏞️ Subcuenca"),
                                         ("subsubcuenca", "💧 Subsubcuenca")]:
                        val = cuenca_info[level]
                        color = "#166534" if val != "No identificada" else "#92400E"
                        st.markdown(f"""
                        <div class="cuenca-card">
                            <div class="title">{label}</div>
                            <div class="value" style="color:{color}">{val}</div>
                        </div>
                        """, unsafe_allow_html=True)
                except ImportError:
                    st.session_state.cuenca_info = {
                        "cuenca": "N/A", "subcuenca": "N/A", "subsubcuenca": "N/A"
                    }
                    st.info("Shapefiles no disponibles — geopandas no instalado")
                except Exception as e:
                    st.session_state.cuenca_info = {
                        "cuenca": "N/A", "subcuenca": "N/A", "subsubcuenca": "N/A"
                    }
        else:
            st.info("👆 Haz clic en el mapa para comenzar")

    # Si no hay punto seleccionado, no mostrar el resto
    if not st.session_state.punto_seleccionado:
        return

    st.divider()

    # ---- PASO 2: TIPO ----
    st.markdown('<div class="step-badge">2 — TIPO DE REGISTRO</div>', unsafe_allow_html=True)

    tipo_cols = st.columns(4)
    tipos_desc = {
        "Conflicto": "Situaciones de tensión o daño socioambiental que afectan al territorio o sus comunidades.",
        "Iniciativa": "Acciones positivas de restauración, gestión del agua o cuidado del territorio.",
        "Actor": "Personas, organizaciones o instituciones relevantes en la gobernanza territorial.",
        "Oportunidad": "Ventanas de acción, financiamiento o articulación para mejorar el territorio.",
    }

    tipo_registro = st.radio(
        "Tipo",
        TIPOS_REGISTRO,
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown(f"""
    <div class="edu-box">
        <strong>{EMOJIS[tipo_registro]} {tipo_registro}</strong>: {tipos_desc[tipo_registro]}
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ---- PASO 3: INFORMACIÓN ----
    st.markdown('<div class="step-badge">3 — INFORMACIÓN GENERAL</div>', unsafe_allow_html=True)

    titulo = st.text_input("📌 Título del registro", max_chars=MAX_TITULO,
                           placeholder="Ej: Sequía en río Maule, Comité de agua potable rural")
    descripcion = st.text_area("📝 Descripción", max_chars=MAX_DESCRIPCION,
                               placeholder="Describe la situación, actores involucrados, contexto territorial...",
                               height=120)

    st.divider()

    # ---- PASO 4: MÓDULO ESPECÍFICO ----
    st.markdown(f'<div class="step-badge">4 — DETALLE: {tipo_registro.upper()}</div>', unsafe_allow_html=True)

    modulo = {}

    if tipo_registro == "Conflicto":
        c1, c2, c3 = st.columns(3)
        with c1:
            modulo["actores"] = st.text_input("Actores involucrados",
                                              placeholder="Ej: Empresa minera vs comunidad")
        with c2:
            modulo["gravedad"] = st.selectbox("Gravedad", CONFLICTO_GRAVEDAD)
        with c3:
            modulo["dialogo"] = st.selectbox("Estado del diálogo", CONFLICTO_DIALOGO)
        modulo["duracion"] = st.selectbox("Duración del conflicto", CONFLICTO_DURACION)

    elif tipo_registro == "Iniciativa":
        modulo["tipos"] = st.multiselect("Tipos de iniciativa", INICIATIVA_TIPOS, max_selections=3)
        c1, c2 = st.columns(2)
        with c1:
            modulo["estado"] = st.selectbox("Estado actual", INICIATIVA_ESTADO)
        with c2:
            modulo["escala"] = st.selectbox("Escala territorial", INICIATIVA_ESCALA)

    elif tipo_registro == "Actor":
        c1, c2 = st.columns(2)
        with c1:
            modulo["nombre"] = st.text_input("Nombre del actor/organización")
        with c2:
            modulo["tipo"] = st.selectbox("Tipo de actor", ACTOR_TIPO)

    elif tipo_registro == "Oportunidad":
        c1, c2 = st.columns(2)
        with c1:
            modulo["viabilidad"] = st.selectbox("Viabilidad", OPORTUNIDAD_VIABILIDAD)
        with c2:
            modulo["urgencia"] = st.selectbox("Urgencia", OPORTUNIDAD_URGENCIA)
        modulo["brechas"] = st.multiselect("Brechas a superar", OPORTUNIDAD_BRECHAS)

    st.divider()

    # ---- PASO 5: DIMENSIONES ----
    st.markdown('<div class="step-badge">5 — DIMENSIONES TRANSVERSALES</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="edu-box">
        {INTRO_DIMENSIONES}
    </div>
    """, unsafe_allow_html=True)

    d1, d2, d3 = st.columns(3)
    with d1:
        dim_agua = st.selectbox("💧 Disponibilidad de agua", DIM_AGUA)
        dim_entorno = st.selectbox("🌿 Estado del entorno", DIM_ENTORNO)
    with d2:
        dim_social = st.selectbox("👥 Tejido social", DIM_SOCIAL)
        dim_gobernanza = st.selectbox("🏛️ Gobernanza", DIM_GOBERNANZA)
    with d3:
        dim_financ = st.selectbox("💰 Financiamiento", DIM_FINANCIAMIENTO)
        dim_regen = st.selectbox("♻️ Potencial de regeneración", DIM_REGENERACION)

    importancia = st.text_area("🎯 ¿Por qué es importante este lugar?",
                               max_chars=MAX_IMPORTANCIA, height=80,
                               placeholder="Explica brevemente la relevancia territorial de este registro...")

    st.divider()

    # ---- PASO 6: GUARDAR ----
    st.markdown('<div class="step-badge">6 — GUARDAR</div>', unsafe_allow_html=True)

    if st.button("💾 Guardar Registro", use_container_width=True, type="primary"):
        if not titulo or not descripcion:
            st.error("Completa al menos el título y la descripción.")
            return

        ci = st.session_state.cuenca_info or {"cuenca": "N/A", "subcuenca": "N/A", "subsubcuenca": "N/A"}
        punto = st.session_state.punto_seleccionado

        with st.spinner("Guardando registro..."):
            punto_id = create_punto(
                st.session_state.user,
                punto["lat"], punto["lon"],
                ci["cuenca"], ci["subcuenca"], ci["subsubcuenca"],
            )

            if punto_id:
                obs_id = create_observacion(
                    st.session_state.user, punto_id, tipo_registro,
                    titulo, descripcion,
                    {
                        "agua": dim_agua,
                        "entorno": dim_entorno,
                        "social": dim_social,
                        "gobernanza": dim_gobernanza,
                        "financiamiento": dim_financ,
                        "regeneracion": dim_regen,
                        "importancia_lugar": importancia,
                    },
                    modulo,
                )
                if obs_id:
                    st.success(f"✅ Registro guardado exitosamente (ID: {obs_id})")
                    st.balloons()
                    st.session_state.punto_seleccionado = None
                    st.session_state.cuenca_info = None
                else:
                    st.error("Error al guardar la observación")
            else:
                st.error("Error al guardar el punto geográfico")


# ============================================
# SECCIÓN: MAPA GLOBAL
# ============================================
def seccion_mapa_global():
    render_hero("Visualiza todos los registros territoriales")

    st.markdown("""
    <div class="edu-box">
        Este mapa muestra <strong>todos los registros</strong> creados por la comunidad.
        Cada marcador representa un registro territorial: <strong style="color:#EF4444">rojo</strong> = conflicto,
        <strong style="color:#22C55E">verde</strong> = iniciativa,
        <strong style="color:#3B82F6">azul</strong> = actor,
        <strong style="color:#F59E0B">naranja</strong> = oportunidad.
        Usa los filtros para explorar por tipo o cuenca.
    </div>
    """, unsafe_allow_html=True)

    stats = get_dashboard_stats()
    if not stats:
        st.info("No hay datos disponibles todavía.")
        return

    obs = stats.get("observaciones", [])
    puntos = stats.get("puntos", [])
    puntos_map = {p["id"]: p for p in puntos}

    # Filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        filtro_tipos = st.multiselect("Filtrar por tipo", TIPOS_REGISTRO, default=TIPOS_REGISTRO)
    with col_f2:
        cuencas_list = ["Todas"] + stats.get("cuencas_list", [])
        filtro_cuenca = st.selectbox("Filtrar por cuenca", cuencas_list)

    # Filtrar observaciones
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

    # Construir mapa
    m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="CartoDB positron")

    for o, p in filtered:
        tipo = o["tipo"]
        popup_html = f"""
        <div style="max-width:250px; font-family:sans-serif;">
            <strong>{o['titulo']}</strong><br>
            <span style="color:{COLORS[tipo]}; font-weight:600;">{EMOJIS[tipo]} {tipo}</span><br>
            <small>{o.get('descripcion', '')[:120]}...</small><br>
            <small style="color:#888;">📍 {p.get('cuenca', 'N/A')}</small>
        </div>
        """
        folium.Marker(
            location=[p["lat"], p["lon"]],
            popup=folium.Popup(popup_html, max_width=280),
            icon=folium.Icon(
                color=FOLIUM_COLORS.get(tipo, "gray"),
                icon=FOLIUM_ICONS.get(tipo, "info-sign"),
                prefix="fa",
            ),
        ).add_to(m)

    st_folium(m, width=None, height=550, returned_objects=[])


# ============================================
# SECCIÓN: DASHBOARD
# ============================================
def seccion_dashboard():
    render_hero("Diagnóstico territorial colectivo")

    st.markdown("""
    <div class="edu-box">
        El dashboard agrega los registros de todos los participantes para mostrar
        una <strong>radiografía del territorio</strong>. Las dimensiones transversales
        revelan patrones: dónde falta agua, dónde la gobernanza es débil, dónde hay
        potencial de regeneración. Este diagnóstico colectivo es la base para la
        acción territorial coordinada.
    </div>
    """, unsafe_allow_html=True)

    stats = get_dashboard_stats()
    if not stats or stats.get("total", 0) == 0:
        st.info("Aún no hay registros. Sé el primero en contribuir desde **Nuevo Registro**.")
        return

    # Métricas principales
    by_tipo = stats.get("by_tipo", {})
    cols = st.columns(5)

    metrics = [
        (f"{stats['total']}", "Total registros", "#1E293B"),
        (f"{by_tipo.get('Conflicto', 0)}", "Conflictos", COLORS["Conflicto"]),
        (f"{by_tipo.get('Iniciativa', 0)}", "Iniciativas", COLORS["Iniciativa"]),
        (f"{by_tipo.get('Actor', 0)}", "Actores", COLORS["Actor"]),
        (f"{by_tipo.get('Oportunidad', 0)}", "Oportunidades", COLORS["Oportunidad"]),
    ]

    for col, (num, label, color) in zip(cols, metrics):
        col.markdown(f"""
        <div class="metric-card">
            <div class="number" style="color:{color}">{num}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráficos
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Distribución por tipo")
        if by_tipo:
            fig = px.pie(
                names=list(by_tipo.keys()),
                values=list(by_tipo.values()),
                color=list(by_tipo.keys()),
                color_discrete_map=COLORS,
                hole=0.45,
            )
            fig.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                height=320,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.15),
                font=dict(family="sans-serif"),
            )
            fig.update_traces(textinfo="percent+label", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.subheader("Dimensiones transversales")
        dims = stats.get("dimensiones", {})
        if dims:
            dim_labels = {
                "agua": "💧 Agua",
                "entorno": "🌿 Entorno",
                "social": "👥 Social",
                "gobernanza": "🏛️ Gobernanza",
                "financiamiento": "💰 Financ.",
                "regeneracion": "♻️ Regen.",
            }
            # Calcular score promedio (simplificado: mapear valores a números)
            score_map = {
                "agua": {"Muy escasa": 1, "Escasa": 2, "Suficiente": 3, "Abundante": 4},
                "entorno": {"Muy degradado": 1, "Degradado": 2, "En recuperación": 3, "Conservado": 4},
                "social": {"Muy débil": 1, "Débil": 2, "Media": 3, "Fuerte": 4},
                "gobernanza": {"Muy débil": 1, "Débil": 2, "Media": 3, "Fuerte": 4},
                "financiamiento": {"Muy difícil": 1, "Difícil": 2, "Medio": 3, "Fácil": 4},
                "regeneracion": {"Bajo": 1, "Medio": 2, "Alto": 3},
            }

            radar_vals = []
            radar_labels = []
            for d, label in dim_labels.items():
                vals = dims.get(d, {})
                smap = score_map.get(d, {})
                total_score = 0
                total_count = 0
                for val, count in vals.items():
                    s = smap.get(val, 0)
                    if s > 0:
                        total_score += s * count
                        total_count += count
                avg = (total_score / total_count) if total_count > 0 else 0
                max_val = max(smap.values()) if smap else 4
                normalized = (avg / max_val) * 100  # normalizar a 0-100
                radar_vals.append(round(normalized, 1))
                radar_labels.append(label)

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=radar_vals + [radar_vals[0]],
                theta=radar_labels + [radar_labels[0]],
                fill="toself",
                fillcolor="rgba(37,99,235,0.15)",
                line=dict(color="#2563EB", width=2),
                name="Promedio territorial",
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100], showticklabels=False),
                ),
                margin=dict(t=30, b=30, l=60, r=60),
                height=320,
                showlegend=False,
                font=dict(family="sans-serif"),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Información por cuenca
    if stats.get("cuencas_unicas", 0) > 0:
        st.divider()
        st.subheader("Registros por cuenca")

        cuenca_counts = {}
        puntos = stats.get("puntos", [])
        obs = stats.get("observaciones", [])
        puntos_map = {p["id"]: p for p in puntos}
        for o in obs:
            p = puntos_map.get(o["punto_id"])
            if p:
                c = p.get("cuenca", "N/A")
                if c and c != "N/A":
                    if c not in cuenca_counts:
                        cuenca_counts[c] = {"Conflicto": 0, "Iniciativa": 0, "Actor": 0, "Oportunidad": 0}
                    cuenca_counts[c][o["tipo"]] = cuenca_counts[c].get(o["tipo"], 0) + 1

        if cuenca_counts:
            rows = []
            for cuenca, tipos in cuenca_counts.items():
                rows.append({
                    "Cuenca": cuenca,
                    "🔴 Conflictos": tipos.get("Conflicto", 0),
                    "🟢 Iniciativas": tipos.get("Iniciativa", 0),
                    "🔵 Actores": tipos.get("Actor", 0),
                    "🟡 Oportunidades": tipos.get("Oportunidad", 0),
                    "Total": sum(tipos.values()),
                })
            df = pd.DataFrame(rows).sort_values("Total", ascending=False)
            st.dataframe(df, use_container_width=True, hide_index=True)

    # Timeline
    st.divider()
    st.subheader("Actividad reciente")
    obs = stats.get("observaciones", [])[:10]
    for o in obs:
        tipo = o["tipo"]
        fecha = o.get("created_at", "")[:10]
        badge_class = f"tipo-{tipo.lower()}"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:0.8rem; padding:0.5rem 0; border-bottom:1px solid #F1F5F9;">
            <span class="tipo-badge {badge_class}">{EMOJIS[tipo]} {tipo}</span>
            <span style="flex:1; font-size:0.9rem;"><strong>{o['titulo']}</strong></span>
            <span style="color:#94A3B8; font-size:0.8rem;">{fecha}</span>
        </div>
        """, unsafe_allow_html=True)


# ============================================
# SECCIÓN: MIS REGISTROS
# ============================================
def seccion_mis_registros():
    render_hero("Tus aportes al mapa territorial")

    mis_obs = get_observaciones_by_user(st.session_state.user)

    if not mis_obs:
        st.info("No has creado registros aún. Ve a **Nuevo Registro** para comenzar.")
        return

    st.write(f"Has contribuido con **{len(mis_obs)}** registros.")

    for obs in mis_obs:
        tipo = obs["tipo"]
        fecha = obs.get("created_at", "")[:10]

        with st.expander(f"{EMOJIS[tipo]} **{obs['titulo']}** — {tipo} · {fecha}"):
            st.write(obs.get("descripcion", ""))

            # Dimensiones
            dims_display = {
                "💧 Agua": obs.get("dim_agua"),
                "🌿 Entorno": obs.get("dim_entorno"),
                "👥 Social": obs.get("dim_social"),
                "🏛️ Gobernanza": obs.get("dim_gobernanza"),
                "💰 Financ.": obs.get("dim_financiamiento"),
                "♻️ Regen.": obs.get("dim_regeneracion"),
            }
            cols = st.columns(6)
            for col, (label, val) in zip(cols, dims_display.items()):
                col.caption(label)
                col.write(val or "NS/NR")

            if obs.get("dim_importancia_lugar"):
                st.caption("🎯 Importancia")
                st.write(obs["dim_importancia_lugar"])

            # Botón eliminar
            if st.button(f"🗑️ Eliminar", key=f"del_{obs['id']}"):
                if delete_observacion(obs["id"], st.session_state.user):
                    st.success("Registro eliminado")
                    st.rerun()
                else:
                    st.error("No se pudo eliminar")


# ============================================
# SECCIÓN: PERFIL
# ============================================
def seccion_perfil():
    render_hero("Tu información de participante")

    profile = st.session_state.profile

    with st.form("profile_form"):
        nombre = st.text_input("Nombre", value=profile.get("nombre", ""))
        st.text_input("Email", value=profile.get("email", ""), disabled=True)
        organizacion = st.text_input("Organización", value=profile.get("organizacion", "") or "")
        tipo_actor = st.selectbox(
            "Tipo de actor",
            TIPOS_ACTOR,
            index=TIPOS_ACTOR.index(profile["tipo_actor"]) if profile.get("tipo_actor") in TIPOS_ACTOR else 0,
        )

        if st.form_submit_button("💾 Guardar Cambios", use_container_width=True):
            if update_user_profile(st.session_state.user, {
                "nombre": nombre,
                "organizacion": organizacion,
                "tipo_actor": tipo_actor,
            }):
                st.session_state.profile["nombre"] = nombre
                st.session_state.profile["organizacion"] = organizacion
                st.session_state.profile["tipo_actor"] = tipo_actor
                st.success("✅ Perfil actualizado")
            else:
                st.error("Error al actualizar")


# ============================================
# MAIN
# ============================================
def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        render_hero("Error de configuración")
        st.error("""
        **No se encontraron las credenciales de Supabase.**

        Asegúrate de configurar los secrets en Streamlit Cloud:

        ```toml
        [supabase]
        url = "https://TU-PROYECTO.supabase.co"
        key = "sb_publishable_TU_KEY_AQUI"
        ```

        Ve a **App Settings → Secrets** en Streamlit Cloud y pega tus credenciales.
        """)
        return

    if not test_connection():
        render_hero("Error de conexión")
        st.error("""
        **No se pudo conectar a Supabase.** Verifica que:
        1. La URL y la key son correctas
        2. Las tablas del schema están creadas
        3. El proyecto de Supabase está activo (no pausado)
        """)
        return

    if not st.session_state.user:
        pantalla_auth()
        return

    seccion = render_sidebar()

    if seccion == "📝 Nuevo Registro":
        seccion_nuevo_registro()
    elif seccion == "🗺️ Mapa Global":
        seccion_mapa_global()
    elif seccion == "📊 Dashboard":
        seccion_dashboard()
    elif seccion == "📋 Mis Registros":
        seccion_mis_registros()
    elif seccion == "⚙️ Perfil":
        seccion_perfil()


if __name__ == "__main__":
    main()
