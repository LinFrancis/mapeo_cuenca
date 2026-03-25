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

st.set_page_config(page_title="Inteligencia Territorial", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# ============================================
# CSS
# ============================================
st.markdown("""<style>
.block-container{padding-top:1.5rem}
.hero{background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 50%,#134E4A 100%);padding:2rem 2.5rem;border-radius:16px;color:white;margin-bottom:1.5rem;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:-50%;right:-20%;width:400px;height:400px;background:radial-gradient(circle,rgba(56,189,248,.12) 0%,transparent 70%);pointer-events:none}
.hero h1{margin:0 0 .3rem;font-size:1.8rem;font-weight:700;letter-spacing:-.02em}
.hero p{margin:0;opacity:.85;font-size:.95rem}
.mc{background:white;border:1px solid #E2E8F0;border-radius:12px;padding:1.2rem;text-align:center;transition:transform .15s}
.mc:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,.06)}
.mc .n{font-size:2rem;font-weight:700;line-height:1.1}
.mc .l{font-size:.8rem;color:#64748B;margin-top:.3rem;text-transform:uppercase;letter-spacing:.05em}
.edu{background:linear-gradient(135deg,#EFF6FF,#F0FDF4);border-left:4px solid #2563EB;border-radius:0 12px 12px 0;padding:1.2rem 1.5rem;margin:1rem 0;font-size:.9rem;line-height:1.6}
.sb{display:inline-flex;align-items:center;gap:.5rem;background:#2563EB;color:white;padding:.35rem .9rem;border-radius:20px;font-size:.8rem;font-weight:600;margin-bottom:.6rem}
.cc{background:linear-gradient(135deg,#F0FDF4,#ECFDF5);border:1px solid #BBF7D0;border-radius:12px;padding:1rem 1.2rem;margin:.5rem 0}
.cc .t{font-weight:600;color:#166534;font-size:.85rem}
.cc .v{font-size:.95rem;color:#14532D;margin-top:.2rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#F8FAFC,#F1F5F9)}
.tb{display:inline-block;padding:.2rem .7rem;border-radius:12px;font-size:.75rem;font-weight:600}
.tc{background:#FEE2E2;color:#991B1B}.ti{background:#DCFCE7;color:#166534}
.ta{background:#DBEAFE;color:#1E40AF}.to{background:#FEF3C7;color:#92400E}
.demo-b{background:linear-gradient(135deg,#FEF3C7,#FDE68A);border:2px solid #F59E0B;border-radius:12px;padding:.8rem 1.2rem;margin-bottom:1rem;display:flex;align-items:center;gap:.5rem;font-size:.85rem}
.foot{text-align:center;padding:1.5rem 0;margin-top:3rem;border-top:1px solid #E2E8F0;font-size:.82rem;color:#94A3B8}
.foot a{color:#2563EB;text-decoration:none;font-weight:600}
.foot a:hover{text-decoration:underline}
.meth{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:1rem;font-size:.85rem;line-height:1.6;color:#475569}
</style>""", unsafe_allow_html=True)

# ============================================
# STATE
# ============================================
for k, v in [("user", None), ("profile", None), ("punto_seleccionado", None),
             ("registro_temp", {}), ("cuenca_info", None), ("show_cuencas_layer", False), ("demo_mode", False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================
# HELPERS
# ============================================
@st.cache_data
def _load_demo():
    from demo_data import generate_demo_data
    return generate_demo_data()

def get_demo_stats():
    data = _load_demo()
    obs, puntos = data["observaciones"], data["puntos"]
    by_tipo = {}
    for o in obs: by_tipo[o["tipo"]] = by_tipo.get(o["tipo"], 0) + 1
    cuencas = set(p["cuenca"] for p in puntos if p.get("cuenca") and p["cuenca"] != "N/A")
    dims = {d: {} for d in ["agua", "entorno", "social", "gobernanza", "financiamiento", "regeneracion"]}
    for o in obs:
        for d in dims:
            val = o.get(f"dim_{d}", "NS/NR")
            dims[d][val] = dims[d].get(val, 0) + 1
    return {"total": len(obs), "total_puntos": len(puntos), "by_tipo": by_tipo,
            "cuencas_unicas": len(cuencas), "cuencas_list": sorted(cuencas),
            "dimensiones": dims, "observaciones": obs, "puntos": puntos}

def get_active_stats():
    return get_demo_stats() if st.session_state.demo_mode else get_dashboard_stats()

def hero(sub="Mapeando cuencas, construyendo territorio"):
    st.markdown(f'<div class="hero"><h1>🌊 Inteligencia Territorial</h1><p>{sub}</p></div>', unsafe_allow_html=True)

def demo_banner():
    if st.session_state.demo_mode:
        st.markdown('<div class="demo-b"><strong>🧪 MODO DEMOSTRACIÓN</strong> — 100 registros ficticios para explorar la plataforma completa.</div>', unsafe_allow_html=True)

def footer():
    st.markdown("""<div class="foot">
        <a href="https://livlin.cl" target="_blank">livlin.cl</a> — servicios profesionales para una vida regenerativa
    </div>""", unsafe_allow_html=True)

SCORE_MAP = {
    "agua": {"Muy escasa": 1, "Escasa": 2, "Suficiente": 3, "Abundante": 4},
    "entorno": {"Muy degradado": 1, "Degradado": 2, "En recuperación": 3, "Conservado": 4},
    "social": {"Muy débil": 1, "Débil": 2, "Media": 3, "Fuerte": 4},
    "gobernanza": {"Muy débil": 1, "Débil": 2, "Media": 3, "Fuerte": 4},
    "financiamiento": {"Muy difícil": 1, "Difícil": 2, "Medio": 3, "Fácil": 4},
    "regeneracion": {"Bajo": 1, "Medio": 2, "Alto": 3},
}
DIM_LABELS = {"agua": "💧 Agua", "entorno": "🌿 Entorno", "social": "👥 Social",
              "gobernanza": "🏛️ Gobernanza", "financiamiento": "💰 Financ.", "regeneracion": "♻️ Regen."}

# ============================================
# AUTH
# ============================================
def pantalla_auth():
    hero("Plataforma de mapeo territorial participativo para cuencas de Chile")
    st.markdown('<div class="edu"><strong>Bienvenido/a</strong> — Registra conflictos, iniciativas, actores y oportunidades geolocalizados en las cuencas de Chile. Construye un diagnóstico colectivo del territorio.</div>', unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("#### 🧪 Explorar sin cuenta")
        st.caption("Conoce toda la plataforma con 100 registros de demostración.")
        if st.button("Entrar en modo demostración", use_container_width=True, type="secondary"):
            st.session_state.demo_mode = True
            st.session_state.user = "demo"
            st.session_state.profile = {"nombre": "Explorador/a Demo", "tipo_actor": "Sociedad Civil", "organizacion": "", "email": "demo@demo.cl"}
            st.rerun()
        st.divider()
        tab_login, tab_signup = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
        with tab_login:
            with st.form("login"):
                email = st.text_input("Email")
                pw = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Ingresar", use_container_width=True, type="primary"):
                    if not email or not pw:
                        st.error("Completa ambos campos")
                    else:
                        with st.spinner("Validando..."):
                            r = login_user(email, pw)
                            if r["success"]:
                                st.session_state.user = r["user_id"]
                                st.session_state.profile = r["profile"]
                                st.session_state.demo_mode = False
                                st.rerun()
                            else:
                                st.error(r["error"])
        with tab_signup:
            with st.form("signup"):
                nombre = st.text_input("Nombre completo")
                email_s = st.text_input("Email", key="se")
                pw_s = st.text_input("Contraseña (mín 6)", type="password", key="sp")
                tipo = st.selectbox("Tipo de actor", TIPOS_ACTOR)
                st.caption("El tipo de actor indica desde qué perspectiva participas en el territorio.")
                if st.form_submit_button("Crear Cuenta", use_container_width=True):
                    ok, msg = validate_nombre(nombre)
                    if not ok: st.error(msg)
                    elif not validate_email(email_s): st.error("Email inválido")
                    else:
                        ok2, msg2 = validate_password(pw_s)
                        if not ok2: st.error(msg2)
                        else:
                            with st.spinner("Creando cuenta..."):
                                r = signup_user(email_s, pw_s, nombre, tipo)
                                if r["success"]: st.success(r["message"])
                                else: st.error(r["error"])
    footer()

# ============================================
# SIDEBAR
# ============================================
def render_sidebar():
    with st.sidebar:
        is_demo = st.session_state.demo_mode
        tag = " 🧪" if is_demo else ""
        st.markdown(f'<div style="padding:1rem;background:white;border-radius:12px;border:1px solid #E2E8F0;margin-bottom:1rem"><div style="font-weight:600">👤 {st.session_state.profile["nombre"]}{tag}</div><div style="color:#64748B;font-size:.8rem;margin-top:.2rem">{st.session_state.profile["tipo_actor"]}</div></div>', unsafe_allow_html=True)

        secs = ["📝 Nuevo Registro", "🗺️ Mapa Global", "📊 Dashboard", "🔗 Análisis de Red", "📋 Mis Registros", "⚙️ Perfil"]
        sec = st.radio("Navegación", secs, label_visibility="collapsed")

        st.divider()
        dv = st.toggle("🧪 Modo demostración", value=is_demo)
        if dv != is_demo:
            st.session_state.demo_mode = dv
            if dv:
                st.session_state.user = "demo"
                st.session_state.profile = {"nombre": "Explorador/a Demo", "tipo_actor": "Sociedad Civil", "organizacion": "", "email": "demo@demo.cl"}
            else:
                st.session_state.user = None
                st.session_state.profile = None
            st.rerun()

        with st.expander("ℹ️ Guía rápida"):
            st.markdown("**Nuevo Registro**: Clic en mapa → formulario → guardar.\n\n**Mapa Global**: Todos los registros con filtros.\n\n**Dashboard**: Diagnóstico multidimensional.\n\n**Análisis de Red**: Conexiones entre registros.\n\n**Mis Registros**: Tus aportes.")

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for k in ["user", "profile", "punto_seleccionado", "registro_temp", "cuenca_info"]:
                st.session_state[k] = None if k != "registro_temp" else {}
            st.session_state.demo_mode = False
            st.rerun()
        return sec

# ============================================
# NUEVO REGISTRO (funciona en demo también)
# ============================================
def seccion_registro():
    hero("Contribuye al mapa territorial")
    demo_banner()
    is_demo = st.session_state.demo_mode

    if is_demo:
        st.markdown('<div class="edu">🧪 <strong>Modo exploración</strong> — Puedes recorrer todo el formulario para conocer qué información se recopila. Los datos no se guardan en la base de datos.</div>', unsafe_allow_html=True)

    st.markdown(INTRO_APP, unsafe_allow_html=True)

    # Tipos de registro — explicación completa
    with st.expander("📖 ¿Qué tipos de registro existen? (clic para expandir)"):
        for tipo_key, info in TIPOS_EXPLICACION.items():
            st.markdown(f"#### {info['emoji']} {info['titulo']}")
            st.markdown(info["desc_larga"])
            st.divider()

    # PASO 1
    st.markdown('<div class="sb">1 — UBICACIÓN</div>', unsafe_allow_html=True)
    st.markdown("Haz **clic en el mapa** para seleccionar la ubicación del registro.")

    with st.expander("📖 ¿Qué es una cuenca hidrográfica?"):
        st.markdown(INTRO_CUENCA)

    col_m, col_i = st.columns([3, 1])
    with col_m:
        m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="OpenStreetMap")
        try:
            from geo_utils import get_cuencas_geojson
            g = get_cuencas_geojson()
            if g is not None and st.session_state.show_cuencas_layer:
                folium.GeoJson(g.to_json(), style_function=lambda x: {"fillColor": "#3B82F6", "color": "#1E40AF", "weight": 1, "fillOpacity": 0.08}).add_to(m)
        except Exception: pass
        md = st_folium(m, width=None, height=450, returned_objects=["last_clicked"])
    with col_i:
        st.session_state.show_cuencas_layer = st.toggle("Cuencas BNA", value=st.session_state.show_cuencas_layer)
        if md and md.get("last_clicked"):
            lat, lon = md["last_clicked"]["lat"], md["last_clicked"]["lng"]
            st.session_state.punto_seleccionado = {"lat": lat, "lon": lon}
            st.success("📍 Seleccionado")
            st.metric("Lat", f"{lat:.4f}")
            st.metric("Lon", f"{lon:.4f}")
            with st.spinner("Identificando cuenca..."):
                try:
                    from geo_utils import identify_cuenca
                    ci = identify_cuenca(lat, lon)
                    st.session_state.cuenca_info = ci
                    for lv, lb in [("cuenca", "🏔️ Cuenca"), ("subcuenca", "🏞️ Subcuenca"), ("subsubcuenca", "💧 Subsubcuenca")]:
                        v = ci[lv]
                        c = "#166534" if v != "No identificada" else "#92400E"
                        st.markdown(f'<div class="cc"><div class="t">{lb}</div><div class="v" style="color:{c}">{v}</div></div>', unsafe_allow_html=True)
                except Exception:
                    st.session_state.cuenca_info = {"cuenca": "N/A", "subcuenca": "N/A", "subsubcuenca": "N/A"}
        else:
            st.info("👆 Clic en el mapa")

    if not st.session_state.punto_seleccionado:
        footer()
        return

    st.divider()

    # PASO 2
    st.markdown('<div class="sb">2 — TIPO DE REGISTRO</div>', unsafe_allow_html=True)
    tipo_r = st.radio("Tipo", TIPOS_REGISTRO, horizontal=True, label_visibility="collapsed")
    info_t = TIPOS_EXPLICACION[tipo_r]
    st.markdown(f'<div class="edu"><strong>{info_t["emoji"]} {info_t["titulo"]}</strong>: {info_t["desc_corta"]}</div>', unsafe_allow_html=True)

    with st.expander(f"📖 ¿Qué significa registrar un {tipo_r}?"):
        st.markdown(info_t["desc_larga"])

    st.divider()

    # PASO 3
    st.markdown('<div class="sb">3 — INFORMACIÓN GENERAL</div>', unsafe_allow_html=True)
    titulo = st.text_input("📌 Título", max_chars=MAX_TITULO, placeholder="Ej: Sequía en río Maule, Comité APR zona alta")
    descripcion = st.text_area("📝 Descripción detallada", max_chars=MAX_DESCRIPCION, placeholder="Describe la situación, quiénes participan, desde cuándo ocurre, qué efectos tiene...", height=120)

    st.divider()

    # PASO 4
    st.markdown(f'<div class="sb">4 — DETALLE: {tipo_r.upper()}</div>', unsafe_allow_html=True)
    modulo = {}
    if tipo_r == "Conflicto":
        c1, c2, c3 = st.columns(3)
        with c1: modulo["actores"] = st.text_input("Actores involucrados", placeholder="Ej: Minera vs comunidad")
        with c2: modulo["gravedad"] = st.selectbox("Gravedad", CONFLICTO_GRAVEDAD, help="Bajo=molestia menor, Crítico=daño severo e irreversible")
        with c3: modulo["dialogo"] = st.selectbox("Estado del diálogo", CONFLICTO_DIALOGO, help="Nulo=sin comunicación, Alto=negociación activa")
        modulo["duracion"] = st.selectbox("Duración", CONFLICTO_DURACION, help="¿Hace cuánto existe este conflicto?")
    elif tipo_r == "Iniciativa":
        modulo["tipos"] = st.multiselect("Tipos de iniciativa", INICIATIVA_TIPOS, max_selections=3, help="Selecciona hasta 3 categorías")
        c1, c2 = st.columns(2)
        with c1: modulo["estado"] = st.selectbox("Estado actual", INICIATIVA_ESTADO, help="Idea=propuesta, En marcha=ejecutándose, Consolidado=funcionando")
        with c2: modulo["escala"] = st.selectbox("Escala territorial", INICIATIVA_ESCALA, help="¿Qué alcance geográfico tiene?")
    elif tipo_r == "Actor":
        c1, c2 = st.columns(2)
        with c1: modulo["nombre"] = st.text_input("Nombre del actor/organización")
        with c2: modulo["tipo"] = st.selectbox("Tipo de organización", ACTOR_TIPO)
    elif tipo_r == "Oportunidad":
        c1, c2 = st.columns(2)
        with c1: modulo["viabilidad"] = st.selectbox("Viabilidad", OPORTUNIDAD_VIABILIDAD, help="¿Qué tan factible es?")
        with c2: modulo["urgencia"] = st.selectbox("Urgencia", OPORTUNIDAD_URGENCIA, help="¿Cuánto tiempo queda para actuar?")
        modulo["brechas"] = st.multiselect("Brechas a superar", OPORTUNIDAD_BRECHAS, help="¿Qué obstáculos hay?")

    st.divider()

    # PASO 5
    st.markdown('<div class="sb">5 — DIMENSIONES TRANSVERSALES</div>', unsafe_allow_html=True)

    with st.expander("📖 ¿Qué son las dimensiones transversales?"):
        st.markdown(INTRO_DIMENSIONES)
        st.markdown("""
**¿Cómo responder?** Usa tu percepción y conocimiento del lugar. No se trata de
datos exactos, sino de la evaluación cualitativa de quien conoce el territorio.
Cada dimensión tiene una escala de 4 niveles (de peor a mejor) más la opción
NS/NR (no sabe / no responde).

**¿Para qué sirven?** Permiten construir un **radar territorial** que muestra
fortalezas y debilidades de cada zona. Al agregar las respuestas de muchos
participantes, emergen patrones que ningún registro individual podría revelar.
""")

    d1, d2, d3 = st.columns(3)
    with d1:
        da = st.selectbox("💧 Disponibilidad de agua", DIM_AGUA, help="Percepción de la disponibilidad hídrica en la zona")
        de = st.selectbox("🌿 Estado del entorno", DIM_ENTORNO, help="Condición del ecosistema natural circundante")
    with d2:
        ds = st.selectbox("👥 Tejido social", DIM_SOCIAL, help="Fuerza de la organización comunitaria")
        dg = st.selectbox("🏛️ Gobernanza", DIM_GOBERNANZA, help="Calidad de la gestión institucional")
    with d3:
        df = st.selectbox("💰 Financiamiento", DIM_FINANCIAMIENTO, help="Acceso a recursos económicos")
        dr = st.selectbox("♻️ Regeneración", DIM_REGENERACION, help="Potencial de recuperación del territorio")
    imp = st.text_area("🎯 ¿Por qué es importante este lugar?", max_chars=MAX_IMPORTANCIA, height=80)

    st.divider()

    # PASO 6
    st.markdown('<div class="sb">6 — GUARDAR</div>', unsafe_allow_html=True)
    if is_demo:
        if st.button("💾 Vista previa (modo demo — no guarda)", use_container_width=True, type="primary"):
            st.success("✅ ¡Formulario completado correctamente! En modo real, este registro se guardaría en la base de datos.")
            st.info(f"**Resumen**: {tipo_r} — \"{titulo or '(sin título)'}\" en {st.session_state.cuenca_info.get('cuenca', 'N/A') if st.session_state.cuenca_info else 'N/A'}")
            st.json({"tipo": tipo_r, "titulo": titulo, "modulo": modulo, "dimensiones": {"agua": da, "entorno": de, "social": ds, "gobernanza": dg, "financiamiento": df, "regeneracion": dr}})
    else:
        if st.button("💾 Guardar Registro", use_container_width=True, type="primary"):
            if not titulo or not descripcion:
                st.error("Completa título y descripción.")
                return
            ci = st.session_state.cuenca_info or {"cuenca": "N/A", "subcuenca": "N/A", "subsubcuenca": "N/A"}
            p = st.session_state.punto_seleccionado
            with st.spinner("Guardando..."):
                pid = create_punto(st.session_state.user, p["lat"], p["lon"], ci["cuenca"], ci["subcuenca"], ci["subsubcuenca"])
                if pid:
                    oid = create_observacion(st.session_state.user, pid, tipo_r, titulo, descripcion,
                        {"agua": da, "entorno": de, "social": ds, "gobernanza": dg, "financiamiento": df, "regeneracion": dr, "importancia_lugar": imp}, modulo)
                    if oid:
                        st.success(f"✅ Registro guardado (ID: {oid})")
                        st.balloons()
                        st.session_state.punto_seleccionado = None
    footer()

# ============================================
# MAPA GLOBAL
# ============================================
def seccion_mapa():
    hero("Visualiza todos los registros territoriales")
    demo_banner()

    st.markdown('<div class="edu">Cada marcador representa un registro: <strong style="color:#EF4444">rojo</strong>=conflicto, <strong style="color:#22C55E">verde</strong>=iniciativa, <strong style="color:#3B82F6">azul</strong>=actor, <strong style="color:#F59E0B">naranja</strong>=oportunidad.</div>', unsafe_allow_html=True)

    with st.expander("📖 ¿Cómo interpretar el mapa?"):
        st.markdown("""
**Concentración de marcadores**: Muchos marcadores juntos indican zonas de alta actividad territorial.

**Balance de colores**: Una zona con solo marcadores rojos (conflictos) sin verdes (iniciativas) sugiere
que no hay respuesta organizada. Zonas con ambos colores muestran capacidad de reacción.

**Distribución geográfica**: Los registros tienden a concentrarse en zonas habitadas de las cuencas.
Las zonas sin marcadores pueden indicar falta de participantes, no ausencia de situaciones.
""")

    stats = get_active_stats()
    if not stats or stats.get("total", 0) == 0:
        st.info("Sin datos."); return

    obs, puntos = stats["observaciones"], stats["puntos"]
    pm = {p["id"]: p for p in puntos}
    c1, c2 = st.columns(2)
    with c1: ft = st.multiselect("Tipo", TIPOS_REGISTRO, default=TIPOS_REGISTRO)
    with c2: fc = st.selectbox("Cuenca", ["Todas"] + stats.get("cuencas_list", []))

    filtered = [(o, pm[o["punto_id"]]) for o in obs if o["tipo"] in ft and o["punto_id"] in pm and (fc == "Todas" or pm[o["punto_id"]].get("cuenca") == fc)]
    st.caption(f"**{len(filtered)}** registros")

    m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="CartoDB positron")
    for o, p in filtered:
        t = o["tipo"]
        popup = f'<div style="max-width:260px;font-family:sans-serif"><strong>{o["titulo"]}</strong><br><span style="color:{COLORS[t]};font-weight:600">{EMOJIS[t]} {t}</span><br><small>{o.get("descripcion","")[:150]}...</small><br><small style="color:#888">📍 {p.get("cuenca","N/A")} → {p.get("subcuenca","")}</small></div>'
        folium.Marker([p["lat"], p["lon"]], popup=folium.Popup(popup, max_width=280),
                      icon=folium.Icon(color=FOLIUM_COLORS.get(t, "gray"), icon=FOLIUM_ICONS.get(t, "info-sign"), prefix="fa")).add_to(m)
    st_folium(m, width=None, height=550, returned_objects=[])
    footer()

# ============================================
# DASHBOARD
# ============================================
def seccion_dashboard():
    hero("Diagnóstico territorial colectivo")
    demo_banner()

    st.markdown('<div class="edu">El dashboard agrega los registros de todos los participantes para mostrar una <strong>radiografía del territorio</strong>. Las dimensiones revelan patrones: dónde falta agua, dónde la gobernanza es débil, dónde hay potencial de regeneración.</div>', unsafe_allow_html=True)

    stats = get_active_stats()
    if not stats or stats.get("total", 0) == 0:
        st.info("Sin registros."); return

    bt = stats.get("by_tipo", {})
    cols = st.columns(5)
    for col, (n, l, c) in zip(cols, [(stats["total"], "Total", "#1E293B"),
        (bt.get("Conflicto", 0), "Conflictos", COLORS["Conflicto"]),
        (bt.get("Iniciativa", 0), "Iniciativas", COLORS["Iniciativa"]),
        (bt.get("Actor", 0), "Actores", COLORS["Actor"]),
        (bt.get("Oportunidad", 0), "Oportunidades", COLORS["Oportunidad"])]):
        col.markdown(f'<div class="mc"><div class="n" style="color:{c}">{n}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribución por tipo")
        with st.expander("📐 Metodología"):
            st.markdown('<div class="meth">Gráfico de torta con hueco (donut chart). Cada segmento representa la proporción de registros por tipo. Un predominio de conflictos indica un territorio en tensión; un predominio de iniciativas sugiere capacidad de acción comunitaria.</div>', unsafe_allow_html=True)
        fig = px.pie(names=list(bt.keys()), values=list(bt.values()), color=list(bt.keys()), color_discrete_map=COLORS, hole=0.45)
        fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=320, legend=dict(orientation="h", yanchor="bottom", y=-0.15))
        fig.update_traces(textinfo="percent+label", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Radar de dimensiones")
        with st.expander("📐 Metodología"):
            st.markdown('<div class="meth"><strong>Construcción</strong>: Cada dimensión tiene una escala ordinal (1-4). Se calcula el promedio ponderado por frecuencia y se normaliza a 0-100%. El radar muestra el perfil multidimensional del territorio.<br><br><strong>Interpretación</strong>: Valores bajos (cerca del centro) = dimensiones críticas. Valores altos (cerca del borde) = fortalezas. Un radar "aplastado" en una dirección indica un desequilibrio sistémico. Lo ideal es un polígono expandido y equilibrado.</div>', unsafe_allow_html=True)

        dims = stats.get("dimensiones", {})
        rv, rl = [], []
        for d, label in DIM_LABELS.items():
            vals = dims.get(d, {})
            sm = SCORE_MAP.get(d, {})
            ts, tc = 0, 0
            for val, cnt in vals.items():
                s = sm.get(val, 0)
                if s > 0: ts += s * cnt; tc += cnt
            avg = (ts / tc) if tc > 0 else 0
            mx = max(sm.values()) if sm else 4
            rv.append(round((avg / mx) * 100, 1)); rl.append(label)
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=rv + [rv[0]], theta=rl + [rl[0]], fill="toself", fillcolor="rgba(37,99,235,.15)", line=dict(color="#2563EB", width=2)))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)), margin=dict(t=30, b=30, l=60, r=60), height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Row 2 — stacked bar by cuenca
    st.divider()
    st.subheader("Registros por cuenca")
    with st.expander("📐 Metodología"):
        st.markdown('<div class="meth">Gráfico de barras apiladas. Cada barra representa una cuenca; los segmentos de color representan los tipos de registro. Permite comparar la intensidad y composición de la actividad territorial entre cuencas.</div>', unsafe_allow_html=True)

    obs, puntos = stats["observaciones"], stats["puntos"]
    pm = {p["id"]: p for p in puntos}
    cd = {}
    for o in obs:
        p = pm.get(o["punto_id"])
        if p:
            c = p.get("cuenca", "N/A")
            if c != "N/A":
                cd.setdefault(c, {}).setdefault(o["tipo"], 0)
                cd[c][o["tipo"]] += 1
    if cd:
        rows = [{"Cuenca": c, "Tipo": t, "Cantidad": n} for c, ts in cd.items() for t, n in ts.items() if n > 0]
        fig = px.bar(pd.DataFrame(rows), x="Cuenca", y="Cantidad", color="Tipo", color_discrete_map=COLORS, barmode="stack")
        fig.update_layout(margin=dict(t=20, b=20), height=350, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    # Row 3 — heatmap
    st.divider()
    st.subheader("Heatmap de dimensiones por cuenca")
    with st.expander("📐 Metodología"):
        st.markdown('<div class="meth"><strong>Construcción</strong>: Para cada par (cuenca, dimensión), se promedian los scores numéricos de todos los registros y se normalizan a porcentaje (0-100%).<br><br><strong>Interpretación</strong>: Colores cálidos (rojo) = valores bajos/críticos. Colores fríos (verde) = valores altos/favorables. Columnas enteras en rojo revelan una dimensión débil en todo el territorio. Filas en rojo revelan cuencas en estado crítico integral.</div>', unsafe_allow_html=True)

    cdims = {}
    for o in obs:
        p = pm.get(o["punto_id"])
        if not p: continue
        c = p.get("cuenca", "N/A")
        if c == "N/A": continue
        cdims.setdefault(c, {d: [] for d in SCORE_MAP})
        for d, sm in SCORE_MAP.items():
            s = sm.get(o.get(f"dim_{d}", ""), 0)
            if s > 0: cdims[c][d].append(s)
    if cdims:
        hrows = []
        for c, dd in cdims.items():
            row = {"Cuenca": c}
            for d, lb in DIM_LABELS.items():
                vs = dd.get(d, [])
                mx = max(SCORE_MAP[d].values())
                row[lb] = round((sum(vs) / len(vs) / mx * 100), 0) if vs else 0
            hrows.append(row)
        dh = pd.DataFrame(hrows).set_index("Cuenca")
        fig = px.imshow(dh, aspect="auto", color_continuous_scale=["#EF4444", "#FCD34D", "#22C55E"], labels=dict(color="Score %"))
        fig.update_layout(margin=dict(t=20, b=20), height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Timeline
    st.divider()
    st.subheader("Actividad reciente")
    for o in obs[:12]:
        t = o["tipo"]
        f = o.get("created_at", "")[:10]
        st.markdown(f'<div style="display:flex;align-items:center;gap:.8rem;padding:.5rem 0;border-bottom:1px solid #F1F5F9"><span class="tb t{t[0].lower()}">{EMOJIS[t]} {t}</span><span style="flex:1;font-size:.9rem"><strong>{o["titulo"]}</strong></span><span style="color:#94A3B8;font-size:.8rem">{f}</span></div>', unsafe_allow_html=True)
    footer()

# ============================================
# RED
# ============================================
def seccion_red():
    hero("Análisis de conexiones territoriales")
    demo_banner()

    st.markdown('<div class="edu"><strong>¿Por qué analizar las conexiones?</strong> Los conflictos, iniciativas, actores y oportunidades no son independientes: un conflicto puede estar vinculado a una iniciativa que involucra a un actor y abre una oportunidad. Este análisis revela <strong>relaciones ocultas</strong> entre registros.</div>', unsafe_allow_html=True)

    stats = get_active_stats()
    if not stats or stats.get("total", 0) < 5:
        st.info("Se necesitan al menos 5 registros."); return

    obs, puntos = stats["observaciones"], stats["puntos"]
    pm = {p["id"]: p for p in puntos}

    # 1. Co-ocurrencia
    st.subheader("🗺️ Co-ocurrencia territorial")
    with st.expander("📐 Metodología"):
        st.markdown('<div class="meth"><strong>Construcción</strong>: Para cada subcuenca, se registra qué tipos de registro están presentes. La celda (i,j) de la matriz cuenta en cuántas subcuencas coexisten los tipos i y j.<br><br><strong>Interpretación</strong>: Una alta co-ocurrencia Conflicto-Iniciativa indica que las comunidades están respondiendo activamente a los problemas. Conflicto-Oportunidad alta sugiere que hay ventanas para intervenir donde hay tensión. Valores bajos en la diagonal indican pocos registros de ese tipo.</div>', unsafe_allow_html=True)

    sub_t = {}
    for o in obs:
        p = pm.get(o["punto_id"])
        if not p: continue
        s = p.get("subcuenca", "N/A")
        if s != "N/A": sub_t.setdefault(s, []).append(o["tipo"])
    tl = ["Conflicto", "Iniciativa", "Actor", "Oportunidad"]
    cooc = pd.DataFrame(0, index=tl, columns=tl)
    for ts in sub_t.values():
        for t1 in tl:
            for t2 in tl:
                if t1 in ts and t2 in ts: cooc.loc[t1, t2] += 1
    fig = px.imshow(cooc, text_auto=True, color_continuous_scale=["#F8FAFC", "#2563EB"], labels=dict(color="Subcuencas"))
    fig.update_layout(margin=dict(t=20, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # 2. Actores
    st.subheader("👥 Red de actores")
    with st.expander("📐 Metodología"):
        st.markdown('<div class="meth"><strong>Construcción</strong>: Se extraen nombres de actores de los campos actor_nombre y conflicto_actores_involucrados. Se cuentan menciones y subcuencas donde aparecen.<br><br><strong>Interpretación</strong>: Actores grandes y altos = muy mencionados. Actores a la derecha = presentes en muchas subcuencas (articuladores). "Multi-cuenca" (rojo) = actores que trascienden una sola cuenca — son nodos clave de la red territorial.</div>', unsafe_allow_html=True)

    am = {}
    for o in obs:
        p = pm.get(o["punto_id"])
        sub = p.get("subcuenca", "N/A") if p else "N/A"
        names = []
        if o.get("actor_nombre"): names.append(o["actor_nombre"])
        if o.get("conflicto_actores_involucrados"):
            names.extend([x.strip() for x in o["conflicto_actores_involucrados"].replace(" vs ", "|").replace(" y ", "|").split("|") if x.strip()])
        for n in names:
            am.setdefault(n, {"count": 0, "subs": set(), "tipos": set(), "cuencas": set()})
            am[n]["count"] += 1; am[n]["subs"].add(sub); am[n]["tipos"].add(o["tipo"])
            if p: am[n]["cuencas"].add(p.get("cuenca", "N/A"))
    if am:
        ar = [{"Actor": n, "Menciones": d["count"], "Subcuencas": len(d["subs"]),
               "Cuencas": ", ".join(sorted(d["cuencas"])), "Tipos": ", ".join(sorted(d["tipos"])),
               "Alcance": "🔴 Multi-cuenca" if len(d["cuencas"]) > 1 else "🟢 Local"}
              for n, d in sorted(am.items(), key=lambda x: -x[1]["count"])]
        df = pd.DataFrame(ar)
        fig = px.scatter(df, x="Subcuencas", y="Menciones", size="Menciones", color="Alcance", text="Actor",
                        color_discrete_map={"🔴 Multi-cuenca": "#EF4444", "🟢 Local": "#22C55E"})
        fig.update_traces(textposition="top center", textfont_size=9)
        fig.update_layout(margin=dict(t=20, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📋 Tabla de actores"):
            st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # 3. Conflicto → Respuesta
    st.subheader("⚡ Balance conflicto → respuesta")
    with st.expander("📐 Metodología"):
        st.markdown('<div class="meth"><strong>Construcción</strong>: Para cada subcuenca se cuenta el número de conflictos (C) e iniciativas (I). El ratio I/C mide la capacidad de respuesta.<br><br><strong>Interpretación</strong>: Puntos sobre la línea diagonal (ratio>1) = respuesta activa. Puntos bajo la diagonal = brecha de respuesta. Puntos en el eje X con Y=0 = conflictos sin ninguna iniciativa. El tamaño del punto refleja las oportunidades detectadas.</div>', unsafe_allow_html=True)

    sb = {}
    for o in obs:
        p = pm.get(o["punto_id"])
        if not p: continue
        s = p.get("subcuenca", "N/A")
        if s == "N/A": continue
        sb.setdefault(s, {"Conflicto": 0, "Iniciativa": 0, "Oportunidad": 0, "cuenca": p.get("cuenca", "")})
        sb[s][o["tipo"]] = sb[s].get(o["tipo"], 0) + 1
    if sb:
        br = [{"Subcuenca": s, "Cuenca": d["cuenca"], "Conflictos": d["Conflicto"], "Iniciativas": d["Iniciativa"],
               "Oportunidades": max(d["Oportunidad"], 1),
               "Ratio": round(d["Iniciativa"] / d["Conflicto"], 2) if d["Conflicto"] > 0 else (9 if d["Iniciativa"] > 0 else 0),
               "Estado": "✅ Activa" if (d["Iniciativa"] / d["Conflicto"] if d["Conflicto"] > 0 else 9) >= 1 else ("⚠️ Brecha" if d["Iniciativa"] > 0 else "🔴 Sin respuesta")}
              for s, d in sb.items()]
        dfb = pd.DataFrame(br).sort_values("Conflictos", ascending=False)
        fig = px.scatter(dfb, x="Conflictos", y="Iniciativas", size="Oportunidades", color="Estado", hover_name="Subcuenca",
                        color_discrete_map={"✅ Activa": "#22C55E", "⚠️ Brecha": "#F59E0B", "🔴 Sin respuesta": "#EF4444"})
        mx = max(dfb["Conflictos"].max(), dfb["Iniciativas"].max(), 1)
        fig.add_trace(go.Scatter(x=[0, mx], y=[0, mx], mode="lines", line=dict(dash="dash", color="#94A3B8"), name="Equilibrio 1:1"))
        fig.update_layout(margin=dict(t=20, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("📋 Tabla de balance"):
            st.dataframe(dfb, use_container_width=True, hide_index=True)

    st.divider()

    # 4. Brechas
    st.subheader("🎯 Brechas prioritarias")
    with st.expander("📐 Metodología"):
        st.markdown('<div class="meth"><strong>Construcción</strong>: Se cuentan las menciones de cada tipo de brecha en los registros de oportunidades. Cada oportunidad puede mencionar múltiples brechas.<br><br><strong>Interpretación</strong>: Las brechas más frecuentes son los cuellos de botella del territorio. Si "Financiamiento" lidera, falta dinero. Si "Coordinación" lidera, hay actores pero no trabajan juntos. Esto orienta las prioridades de acción.</div>', unsafe_allow_html=True)

    bc = {}
    for o in obs:
        if o["tipo"] == "Oportunidad":
            for b in (o.get("oportunidad_brechas") or []):
                bc[b] = bc.get(b, 0) + 1
    if bc:
        dfbr = pd.DataFrame([{"Brecha": k, "Menciones": v} for k, v in sorted(bc.items(), key=lambda x: -x[1])])
        fig = px.bar(dfbr, x="Menciones", y="Brecha", orientation="h", color="Menciones", color_continuous_scale=["#FDE68A", "#EF4444"])
        fig.update_layout(margin=dict(t=20, b=20, l=10), height=300, showlegend=False, yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)
    footer()

# ============================================
# MIS REGISTROS
# ============================================
def seccion_registros():
    hero("Tus aportes al mapa territorial")
    if st.session_state.demo_mode:
        st.info("En modo demo los registros son ficticios compartidos. Crea una cuenta para tener registros propios.")
        footer(); return
    mis = get_observaciones_by_user(st.session_state.user)
    if not mis:
        st.info("No has creado registros. Ve a **Nuevo Registro**."); footer(); return
    st.write(f"**{len(mis)}** registros.")
    for o in mis:
        t = o["tipo"]; f = o.get("created_at", "")[:10]
        with st.expander(f"{EMOJIS[t]} **{o['titulo']}** — {t} · {f}"):
            st.write(o.get("descripcion", ""))
            cs = st.columns(6)
            for col, (e, k) in zip(cs, [("💧", "dim_agua"), ("🌿", "dim_entorno"), ("👥", "dim_social"),
                                         ("🏛️", "dim_gobernanza"), ("💰", "dim_financiamiento"), ("♻️", "dim_regeneracion")]):
                col.caption(e); col.write(o.get(k, "NS/NR"))
            if st.button("🗑️ Eliminar", key=f"d_{o['id']}"):
                if delete_observacion(o["id"], st.session_state.user): st.success("Eliminado"); st.rerun()
    footer()

# ============================================
# PERFIL
# ============================================
def seccion_perfil():
    hero("Tu información")
    if st.session_state.demo_mode:
        st.info("Perfil no editable en modo demo."); footer(); return
    pr = st.session_state.profile
    with st.form("pf"):
        n = st.text_input("Nombre", value=pr.get("nombre", ""))
        st.text_input("Email", value=pr.get("email", ""), disabled=True)
        org = st.text_input("Organización", value=pr.get("organizacion", "") or "")
        ta = st.selectbox("Tipo", TIPOS_ACTOR, index=TIPOS_ACTOR.index(pr["tipo_actor"]) if pr.get("tipo_actor") in TIPOS_ACTOR else 0)
        if st.form_submit_button("💾 Guardar", use_container_width=True):
            if update_user_profile(st.session_state.user, {"nombre": n, "organizacion": org, "tipo_actor": ta}):
                st.session_state.profile.update({"nombre": n, "organizacion": org, "tipo_actor": ta})
                st.success("✅ Actualizado")
    footer()

# ============================================
# MAIN
# ============================================
def main():
    # Sin credenciales → ofrecer demo
    if not SUPABASE_URL or not SUPABASE_KEY:
        hero("Configuración pendiente")
        st.warning("Credenciales de Supabase no configuradas.")
        if st.button("🧪 Explorar en modo demostración", type="primary"):
            st.session_state.demo_mode = True
            st.session_state.user = "demo"
            st.session_state.profile = {"nombre": "Explorador/a Demo", "tipo_actor": "Sociedad Civil", "organizacion": "", "email": "demo@demo.cl"}
            st.rerun()
        footer(); return

    if not st.session_state.user:
        conn = test_connection()
        if not conn:
            hero("Sin conexión")
            st.warning("No se pudo conectar a Supabase.")
            if st.button("🧪 Explorar con datos de demostración", type="primary"):
                st.session_state.demo_mode = True
                st.session_state.user = "demo"
                st.session_state.profile = {"nombre": "Explorador/a Demo", "tipo_actor": "Sociedad Civil", "organizacion": "", "email": "demo@demo.cl"}
                st.rerun()
            footer(); return
        pantalla_auth(); return

    sec = render_sidebar()
    {"📝 Nuevo Registro": seccion_registro, "🗺️ Mapa Global": seccion_mapa, "📊 Dashboard": seccion_dashboard,
     "🔗 Análisis de Red": seccion_red, "📋 Mis Registros": seccion_registros, "⚙️ Perfil": seccion_perfil}.get(sec, seccion_registro)()

if __name__ == "__main__":
    main()
