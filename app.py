"""
app.py — Mapeo Participativo de Cuencas v2.0
Inteligencia territorial para cuencas hidrográficas de Chile
"""
import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from config import *
from supabase_client import *

st.set_page_config(page_title=APP_NAME, page_icon="🌊", layout="wide", initial_sidebar_state="expanded")

# ===== CSS =====
st.markdown("""<style>
.block-container{padding-top:1.5rem}
.hero{background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 50%,#134E4A 100%);padding:2rem 2.5rem;border-radius:16px;color:white;margin-bottom:1.5rem;position:relative;overflow:hidden}
.hero h1{margin:0 0 .3rem;font-size:1.8rem;font-weight:700;letter-spacing:-.02em}.hero p{margin:0;opacity:.85;font-size:.95rem}
.mc{background:white;border:1px solid #E2E8F0;border-radius:12px;padding:1.2rem;text-align:center}
.mc .n{font-size:2rem;font-weight:700;line-height:1.1}.mc .l{font-size:.8rem;color:#64748B;margin-top:.3rem;text-transform:uppercase;letter-spacing:.05em}
.edu{background:linear-gradient(135deg,#EFF6FF,#F0FDF4);border-left:4px solid #2563EB;border-radius:0 12px 12px 0;padding:1.2rem 1.5rem;margin:1rem 0;font-size:.9rem;line-height:1.6}
.sb{display:inline-flex;align-items:center;gap:.5rem;background:#2563EB;color:white;padding:.35rem .9rem;border-radius:20px;font-size:.8rem;font-weight:600;margin-bottom:.6rem}
.cc{background:linear-gradient(135deg,#F0FDF4,#ECFDF5);border:1px solid #BBF7D0;border-radius:12px;padding:.8rem 1rem;margin:.4rem 0}
.cc .t{font-weight:600;color:#166534;font-size:.82rem}.cc .v{font-size:.9rem;color:#14532D;margin-top:.1rem}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#F8FAFC,#F1F5F9)}
.tb{display:inline-block;padding:.2rem .7rem;border-radius:12px;font-size:.75rem;font-weight:600}
.tc{background:#FEE2E2;color:#991B1B}.ti{background:#DCFCE7;color:#166534}.ta{background:#DBEAFE;color:#1E40AF}.to{background:#FEF3C7;color:#92400E}
.demo-b{background:linear-gradient(135deg,#FEF3C7,#FDE68A);border:2px solid #F59E0B;border-radius:12px;padding:.8rem 1.2rem;margin-bottom:1rem;font-size:.85rem}
.foot{text-align:center;padding:1.5rem 0;margin-top:3rem;border-top:1px solid #E2E8F0;font-size:.82rem;color:#94A3B8}
.foot a{color:#2563EB;text-decoration:none;font-weight:600}
.meth{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:1rem;font-size:.85rem;line-height:1.6;color:#475569}
.reg-card{background:white;border:1px solid #E2E8F0;border-radius:12px;padding:1rem 1.2rem;margin:.5rem 0}
.reg-card:hover{border-color:#2563EB}
</style>""", unsafe_allow_html=True)

# ===== STATE =====
for k, v in [("user", None), ("profile", None), ("punto_sel", None), ("cuenca_info", None),
             ("show_cuencas", False), ("demo_mode", False)]:
    if k not in st.session_state: st.session_state[k] = v

# ===== HELPERS =====
@st.cache_data
def _load_demo():
    from demo_data import generate_demo_data
    return generate_demo_data()

def get_demo_stats():
    d = _load_demo(); obs, pts = d["observaciones"], d["puntos"]
    bt = {}
    for o in obs: bt[o["tipo"]] = bt.get(o["tipo"], 0) + 1
    cs = set(p["cuenca"] for p in pts if p.get("cuenca") and p["cuenca"] != "N/A")
    dims = {d: {} for d in SCORE_MAP}
    for o in obs:
        for d in dims: v = o.get(f"dim_{d}", "NS/NR"); dims[d][v] = dims[d].get(v, 0) + 1
    return {"total": len(obs), "by_tipo": bt, "cuencas_list": sorted(cs), "cuencas_unicas": len(cs),
            "dimensiones": dims, "observaciones": obs, "puntos": pts}

def stats(): return get_demo_stats() if st.session_state.demo_mode else get_dashboard_stats()

def hero(sub=f"Inteligencia territorial para cuencas de Chile — v{APP_VERSION}"):
    st.markdown(f'<div class="hero"><h1>🌊 {APP_NAME}</h1><p>{sub}</p></div>', unsafe_allow_html=True)

def demo_banner():
    if st.session_state.demo_mode: st.markdown('<div class="demo-b">🧪 <strong>MODO DEMOSTRACIÓN</strong> — 100 registros ficticios. Los datos no se guardan.</div>', unsafe_allow_html=True)

def footer():
    st.markdown('<div class="foot"><a href="https://livlin.cl" target="_blank">livlin.cl</a> — servicios profesionales para una vida regenerativa</div>', unsafe_allow_html=True)

def show_enlaces(enl):
    """Render enlaces from a dict."""
    if not enl or not isinstance(enl, dict): return
    if enl.get("youtube"): st.markdown(f"🎥 [Video YouTube]({enl['youtube']})")
    if enl.get("perfil"): st.markdown(f"🔗 [Perfil del actor]({enl['perfil']})")
    for u in (enl.get("fotos") or []): st.markdown(f"📷 [Foto]({u})")
    for u in (enl.get("otros") or []): st.markdown(f"📎 [Enlace]({u})")

def territory_filter(obs, pts, prefix=""):
    """Shared cascading territory filter. Returns filtered (obs, pts, pm, label)."""
    pm = {p["id"]: p for p in pts}
    # Build cuenca list
    cuencas = sorted(set(p.get("cuenca", "N/A") for p in pts if p.get("cuenca") and p["cuenca"] != "N/A"))
    c1, c2, c3, c4 = st.columns(4)
    with c1: ft = st.multiselect("Tipo", TIPOS_REGISTRO, default=TIPOS_REGISTRO, key=f"{prefix}_ft")
    with c2: fc = st.selectbox("Cuenca", ["Todas"] + cuencas, key=f"{prefix}_fc")

    # Cascading subcuenca
    subs_disp = sorted(set(p.get("subcuenca", "N/A") for p in pts
                           if (fc == "Todas" or p.get("cuenca") == fc) and p.get("subcuenca") and p["subcuenca"] != "N/A"))
    with c3: fsub = st.selectbox("Subcuenca", ["Todas"] + subs_disp, key=f"{prefix}_fsub")

    # Cascading subsubcuenca
    ssubs_disp = sorted(set(p.get("subsubcuenca", "N/A") for p in pts
                            if (fc == "Todas" or p.get("cuenca") == fc)
                            and (fsub == "Todas" or p.get("subcuenca") == fsub)
                            and p.get("subsubcuenca") and p["subsubcuenca"] != "N/A"))
    with c4: fssub = st.selectbox("Subsubcuenca", ["Todas"] + ssubs_disp, key=f"{prefix}_fssub")

    # Filter
    f_obs = []
    for o in obs:
        if o["tipo"] not in ft: continue
        p = pm.get(o.get("punto_id"))
        if not p: continue
        if fc != "Todas" and p.get("cuenca") != fc: continue
        if fsub != "Todas" and p.get("subcuenca") != fsub: continue
        if fssub != "Todas" and p.get("subsubcuenca") != fssub: continue
        f_obs.append(o)

    # Build territory label
    parts = []
    if fc != "Todas": parts.append(fc)
    if fsub != "Todas": parts.append(fsub)
    if fssub != "Todas": parts.append(fssub)
    label = " → ".join(parts) if parts else "Todo el territorio"

    st.caption(f"📍 **{label}** — {len(f_obs)} registros filtrados")
    return f_obs, pts, pm, label

def show_cuenca_hierarchy(p):
    """Show cuenca/subcuenca/subsubcuenca badges."""
    for lb, k, icon in [("Cuenca", "cuenca", "🏔️"), ("Subcuenca", "subcuenca", "🏞️"), ("Subsubcuenca", "subsubcuenca", "💧")]:
        v = p.get(k, "N/A")
        if v and v != "N/A": st.markdown(f'<div class="cc"><div class="t">{icon} {lb}</div><div class="v">{v}</div></div>', unsafe_allow_html=True)

# ===== AUTH =====
def pantalla_auth():
    hero("Plataforma participativa de mapeo de cuencas hidrográficas de Chile")
    st.markdown(f'<div class="edu"><strong>Bienvenido/a</strong> — Las cuencas se definen según la <a href="https://dga.mop.gob.cl/administracionrecursoshidricos/mapoteca/Paginas/default.aspx" target="_blank">Dirección General de Aguas (DGA)</a>. Registra conflictos, iniciativas, actores y oportunidades organizados en cuenca → subcuenca → subsubcuenca.</div>', unsafe_allow_html=True)
    cl, cc, cr = st.columns([1, 2, 1])
    with cc:
        if st.button("🧪 Explorar en modo demostración", use_container_width=True, type="secondary"):
            st.session_state.demo_mode = True; st.session_state.user = "demo"
            st.session_state.profile = {"nombre": "Explorador/a Demo", "tipo_actor": "Sociedad Civil", "organizacion": "", "email": "demo@demo.cl"}
            st.rerun()
        st.divider()
        t1, t2 = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
        with t1:
            with st.form("login"):
                e = st.text_input("Email"); p = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Ingresar", use_container_width=True, type="primary"):
                    if e and p:
                        with st.spinner("..."): r = login_user(e, p)
                        if r["success"]: st.session_state.user = r["user_id"]; st.session_state.profile = r["profile"]; st.session_state.demo_mode = False; st.rerun()
                        else: st.error(r["error"])
        with t2:
            with st.form("signup"):
                n = st.text_input("Nombre"); es = st.text_input("Email", key="se"); ps = st.text_input("Contraseña (mín 6)", type="password", key="sp")
                ta = st.selectbox("Tipo de actor", TIPOS_ACTOR)
                if st.form_submit_button("Crear Cuenta", use_container_width=True):
                    ok, m = validate_nombre(n)
                    if not ok: st.error(m)
                    elif not validate_email(es): st.error("Email inválido")
                    else:
                        ok2, m2 = validate_password(ps)
                        if not ok2: st.error(m2)
                        else:
                            r = signup_user(es, ps, n, ta)
                            if r["success"]: st.success(r["message"])
                            else: st.error(r["error"])
    footer()

# ===== SIDEBAR =====
def sidebar():
    with st.sidebar:
        dm = st.session_state.demo_mode; tag = " 🧪" if dm else ""
        st.markdown(f'<div style="padding:.8rem;background:white;border-radius:12px;border:1px solid #E2E8F0;margin-bottom:1rem"><div style="font-weight:600">👤 {st.session_state.profile["nombre"]}{tag}</div><div style="color:#64748B;font-size:.8rem">{st.session_state.profile["tipo_actor"]}</div></div>', unsafe_allow_html=True)
        secs = ["📝 Nuevo Registro", "🔍 Explorar Registros", "🗺️ Mapa", "📊 Dashboard", "🔗 Análisis de Red", "📋 Mis Registros", "⚙️ Perfil"]
        sec = st.radio("", secs, label_visibility="collapsed")
        st.divider()
        dv = st.toggle("🧪 Modo demo", value=dm)
        if dv != dm:
            st.session_state.demo_mode = dv
            if dv: st.session_state.user = "demo"; st.session_state.profile = {"nombre": "Explorador/a Demo", "tipo_actor": "Sociedad Civil", "organizacion": "", "email": "demo@demo.cl"}
            else: st.session_state.user = None; st.session_state.profile = None
            st.rerun()
        if st.button("🚪 Salir", use_container_width=True):
            for k in ["user", "profile", "punto_sel", "cuenca_info"]: st.session_state[k] = None
            st.session_state.demo_mode = False; st.rerun()
        return sec

# ===== REGISTRO =====
def sec_registro():
    hero("Contribuye al mapa territorial de cuencas")
    demo_banner(); dm = st.session_state.demo_mode
    if dm: st.markdown('<div class="edu">🧪 <strong>Modo exploración</strong> — Recorre el formulario completo. Los datos no se guardan.</div>', unsafe_allow_html=True)
    st.markdown(INTRO_APP)
    with st.expander("📖 Tipos de registro"):
        for tk, ti in TIPOS_EXPLICACION.items(): st.markdown(f"**{ti['emoji']} {ti['titulo']}**: {ti['larga']}")

    # PASO 1: UBICACIÓN — tres métodos
    st.markdown('<div class="sb">1 — UBICACIÓN</div>', unsafe_allow_html=True)
    with st.expander("📖 Sobre las cuencas (DGA)"): st.markdown(INTRO_CUENCA)

    metodo = st.radio("Método de ubicación", METODOS_UBICACION, horizontal=True)
    lat, lon, comuna_sel, precision = None, None, "N/A", "Aproximada"

    if metodo == "📍 Clic en el mapa":
        m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="OpenStreetMap")
        md = st_folium(m, width=None, height=400, returned_objects=["last_clicked"])
        if md and md.get("last_clicked"):
            lat, lon = md["last_clicked"]["lat"], md["last_clicked"]["lng"]
            precision = "Aproximada"

    elif metodo == "🏘️ Buscar por comuna":
        comunas_list = sorted(COMUNAS_CUENCAS.keys())
        comuna_sel = st.selectbox("Selecciona tu comuna", ["— Selecciona —"] + comunas_list)
        if comuna_sel != "— Selecciona —":
            info = COMUNAS_CUENCAS[comuna_sel]
            lat, lon = info["lat"], info["lon"]
            precision = "Aproximada"
            st.success(f"📍 {comuna_sel} → Cuenca: **{info['cuenca']}**")
            if info.get("subcuencas"):
                st.caption(f"Subcuencas asociadas: {', '.join(info['subcuencas'])}")
            st.info("💡 Opcionalmente, haz clic en el mapa para precisar la ubicación dentro de la comuna.")
            m2 = folium.Map(location=[lat, lon], zoom_start=12, tiles="OpenStreetMap")
            folium.Marker([lat, lon], popup=comuna_sel, icon=folium.Icon(color="blue")).add_to(m2)
            md2 = st_folium(m2, width=None, height=300, returned_objects=["last_clicked"])
            if md2 and md2.get("last_clicked"):
                lat, lon = md2["last_clicked"]["lat"], md2["last_clicked"]["lng"]
                st.caption(f"Ubicación refinada: {lat:.4f}, {lon:.4f}")

    elif metodo == "📐 Coordenadas exactas":
        c1, c2 = st.columns(2)
        with c1: lat = st.number_input("Latitud", value=-33.45, format="%.6f", min_value=-56.0, max_value=-17.0)
        with c2: lon = st.number_input("Longitud", value=-70.65, format="%.6f", min_value=-76.0, max_value=-66.0)
        precision = "Exacta"

    # Identificar cuenca
    ci = {"cuenca": "N/A", "subcuenca": "N/A", "subsubcuenca": "N/A"}
    if lat is not None:
        st.session_state.punto_sel = {"lat": lat, "lon": lon}
        st.metric("Lat", f"{lat:.4f}"); st.metric("Lon", f"{lon:.4f}")

        # Si viene de comuna, pre-llenar cuenca
        if metodo == "🏘️ Buscar por comuna" and comuna_sel in COMUNAS_CUENCAS:
            ci["cuenca"] = COMUNAS_CUENCAS[comuna_sel]["cuenca"]

        # Intentar detección por shapefile
        with st.spinner("Identificando cuenca..."):
            try:
                from geo_utils import identify_cuenca
                ci_geo = identify_cuenca(lat, lon)
                if ci_geo["cuenca"] != "No identificada": ci = ci_geo
            except: pass
        st.session_state.cuenca_info = ci
        show_cuenca_hierarchy(ci)

        # Weather data
        try:
            from geo_utils import fetch_weather
            wx = fetch_weather(lat, lon)
            if wx and wx.get("dates"):
                with st.expander("🌡️ Datos meteorológicos del último año (Open-Meteo)"):
                    import plotly.graph_objects as go
                    df_wx = pd.DataFrame(wx)
                    fig = go.Figure()
                    fig.add_trace(go.Bar(x=df_wx["dates"], y=df_wx["precip"], name="Precipitación (mm)", marker_color="#3B82F6", opacity=0.6))
                    fig.add_trace(go.Scatter(x=df_wx["dates"], y=df_wx["temp_max"], name="T° máx", line=dict(color="#EF4444")))
                    fig.add_trace(go.Scatter(x=df_wx["dates"], y=df_wx["temp_min"], name="T° mín", line=dict(color="#3B82F6")))
                    fig.update_layout(height=280, margin=dict(t=20, b=20), legend=dict(orientation="h", y=-0.2))
                    st.plotly_chart(fig, use_container_width=True)
                    total_rain = sum(v for v in wx["precip"] if v)
                    st.caption(f"Precipitación total 12 meses: **{total_rain:.0f} mm** · Fuente: Open-Meteo (gratuito)")
        except: pass
    else:
        st.info("👆 Selecciona una ubicación para continuar"); footer(); return

    st.divider()

    # PASO 2: TIPO
    st.markdown('<div class="sb">2 — TIPO DE REGISTRO</div>', unsafe_allow_html=True)
    tipo_r = st.radio("Tipo", TIPOS_REGISTRO, horizontal=True, label_visibility="collapsed")
    ti = TIPOS_EXPLICACION[tipo_r]
    st.markdown(f'<div class="edu"><strong>{ti["emoji"]} {ti["titulo"]}</strong>: {ti["corta"]}</div>', unsafe_allow_html=True)
    with st.expander(f"📖 ¿Qué es un registro de {tipo_r}?"): st.markdown(ti["larga"])

    st.divider()

    # PASO 3: INFO
    st.markdown('<div class="sb">3 — INFORMACIÓN</div>', unsafe_allow_html=True)
    titulo = st.text_input("📌 Título", max_chars=MAX_TITULO)
    descripcion = st.text_area("📝 Descripción", max_chars=MAX_DESCRIPCION, height=120)

    st.divider()

    # PASO 4: MÓDULO
    st.markdown(f'<div class="sb">4 — DETALLE: {tipo_r.upper()}</div>', unsafe_allow_html=True)
    mod = {}
    if tipo_r == "Conflicto":
        c1, c2, c3 = st.columns(3)
        with c1: mod["actores"] = st.text_input("Actores involucrados")
        with c2: mod["gravedad"] = st.selectbox("Gravedad", CONFLICTO_GRAVEDAD)
        with c3: mod["dialogo"] = st.selectbox("Diálogo", CONFLICTO_DIALOGO)
        mod["duracion"] = st.selectbox("Duración", CONFLICTO_DURACION)
    elif tipo_r == "Iniciativa":
        mod["tipos"] = st.multiselect("Tipos", INICIATIVA_TIPOS, max_selections=3)
        c1, c2 = st.columns(2)
        with c1: mod["estado"] = st.selectbox("Estado", INICIATIVA_ESTADO)
        with c2: mod["escala"] = st.selectbox("Escala", INICIATIVA_ESCALA)
    elif tipo_r == "Actor":
        c1, c2 = st.columns(2)
        with c1: mod["nombre"] = st.text_input("Nombre del actor")
        with c2: mod["tipo"] = st.selectbox("Tipo", ACTOR_TIPO)
    elif tipo_r == "Oportunidad":
        c1, c2 = st.columns(2)
        with c1: mod["viabilidad"] = st.selectbox("Viabilidad", OPORTUNIDAD_VIABILIDAD)
        with c2: mod["urgencia"] = st.selectbox("Urgencia", OPORTUNIDAD_URGENCIA)
        mod["brechas"] = st.multiselect("Brechas", OPORTUNIDAD_BRECHAS)

    st.divider()

    # PASO 5: DIMENSIONES
    st.markdown('<div class="sb">5 — DIMENSIONES TRANSVERSALES</div>', unsafe_allow_html=True)
    with st.expander("📖 ¿Qué son?"): st.markdown(INTRO_DIMENSIONES)
    d1, d2, d3 = st.columns(3)
    with d1: da = st.selectbox("💧 Agua", DIM_AGUA); de = st.selectbox("🌿 Entorno", DIM_ENTORNO)
    with d2: ds = st.selectbox("👥 Social", DIM_SOCIAL); dg = st.selectbox("🏛️ Gobernanza", DIM_GOBERNANZA)
    with d3: df_ = st.selectbox("💰 Financiamiento", DIM_FINANCIAMIENTO); dr = st.selectbox("♻️ Regeneración", DIM_REGENERACION)
    imp = st.text_area("🎯 Importancia", max_chars=MAX_IMPORTANCIA, height=80)

    st.divider()

    # PASO 6: ENLACES
    st.markdown('<div class="sb">6 — ENLACES Y MATERIAL</div>', unsafe_allow_html=True)
    st.caption("Opcional: agrega videos, fotos o documentos relacionados.")
    enlaces = {}
    yt = st.text_input("🎥 Video YouTube", placeholder="https://youtube.com/watch?v=...")
    if yt: enlaces["youtube"] = yt
    fotos = st.text_input("📷 URLs de fotos (separadas por coma)", placeholder="https://...")
    if fotos: enlaces["fotos"] = [u.strip() for u in fotos.split(",") if u.strip()]
    otros = st.text_input("📎 Otros enlaces", placeholder="https://documento.pdf, https://sitio.cl")
    if otros: enlaces["otros"] = [u.strip() for u in otros.split(",") if u.strip()]
    if tipo_r == "Actor":
        perfil = st.text_input("🔗 Enlace al perfil/web del actor", placeholder="https://...")
        if perfil: enlaces["perfil"] = perfil

    st.divider()

    # PASO 7: GUARDAR
    st.markdown('<div class="sb">7 — GUARDAR</div>', unsafe_allow_html=True)
    st.caption(f"📍 Precisión: **{precision}** | Cuenca: **{ci['cuenca']}** → **{ci['subcuenca']}** → **{ci['subsubcuenca']}**")

    if dm:
        if st.button("💾 Vista previa (demo)", use_container_width=True, type="primary"):
            st.success("✅ Formulario completo. En modo real se guardaría en la BD.")
            st.json({"tipo": tipo_r, "titulo": titulo, "cuenca": ci, "precision": precision, "modulo": mod, "enlaces": enlaces})
    else:
        if st.button("💾 Guardar", use_container_width=True, type="primary"):
            if not titulo or not descripcion: st.error("Completa título y descripción."); return
            with st.spinner("Guardando..."):
                pid = create_punto(st.session_state.user, lat, lon, ci["cuenca"], ci["subcuenca"], ci["subsubcuenca"], precision, comuna_sel)
                if pid:
                    oid = create_observacion(st.session_state.user, pid, tipo_r, titulo, descripcion,
                        {"agua": da, "entorno": de, "social": ds, "gobernanza": dg, "financiamiento": df_, "regeneracion": dr, "importancia_lugar": imp},
                        mod, enlaces or None)
                    if oid: st.success(f"✅ Guardado (ID: {oid})"); st.balloons(); st.session_state.punto_sel = None
    footer()

# ===== EXPLORAR REGISTROS =====
def sec_explorar():
    hero("Explorar registros territoriales")
    demo_banner()
    st.markdown('<div class="edu">Busca y filtra registros por tipo, cuenca y texto libre. Explora el detalle de cada registro incluyendo dimensiones, enlaces y ubicación jerárquica.</div>', unsafe_allow_html=True)

    s = stats()
    if not s or s.get("total", 0) == 0: st.info("Sin registros."); return
    obs, pts = s["observaciones"], s["puntos"]
    pm = {p["id"]: p for p in pts}

    # Filtros
    c1, c2, c3 = st.columns(3)
    with c1: ft = st.multiselect("Tipo", TIPOS_REGISTRO, default=TIPOS_REGISTRO)
    with c2:
        cuencas = ["Todas"] + s.get("cuencas_list", [])
        fc = st.selectbox("Cuenca", cuencas)
    with c3: busqueda = st.text_input("🔍 Buscar en título o descripción")

    # Subcuenca filter (cascading)
    subcuencas_disponibles = set()
    for p in pts:
        if (fc == "Todas" or p.get("cuenca") == fc) and p.get("subcuenca") and p["subcuenca"] != "N/A":
            subcuencas_disponibles.add(p["subcuenca"])
    if subcuencas_disponibles:
        fsub = st.selectbox("Subcuenca", ["Todas"] + sorted(subcuencas_disponibles))
    else:
        fsub = "Todas"

    # Subsubcuenca filter
    subsub_disponibles = set()
    for p in pts:
        if (fc == "Todas" or p.get("cuenca") == fc) and (fsub == "Todas" or p.get("subcuenca") == fsub):
            if p.get("subsubcuenca") and p["subsubcuenca"] != "N/A":
                subsub_disponibles.add(p["subsubcuenca"])
    if subsub_disponibles:
        fssub = st.selectbox("Subsubcuenca", ["Todas"] + sorted(subsub_disponibles))
    else:
        fssub = "Todas"

    # Apply filters
    filtered = []
    bq = busqueda.lower().strip() if busqueda else ""
    for o in obs:
        if o["tipo"] not in ft: continue
        p = pm.get(o["punto_id"])
        if not p: continue
        if fc != "Todas" and p.get("cuenca") != fc: continue
        if fsub != "Todas" and p.get("subcuenca") != fsub: continue
        if fssub != "Todas" and p.get("subsubcuenca") != fssub: continue
        if bq and bq not in (o.get("titulo", "") + " " + o.get("descripcion", "")).lower(): continue
        filtered.append((o, p))

    st.caption(f"**{len(filtered)}** registros encontrados")

    # Results
    for o, p in filtered:
        t = o["tipo"]; f = o.get("created_at", "")[:10]
        with st.expander(f"{EMOJIS[t]} **{o['titulo']}** — {t} · {f} · 📍 {p.get('subsubcuenca', 'N/A')}"):
            st.write(o.get("descripcion", ""))

            # Cuenca hierarchy
            st.markdown("**📍 Ubicación territorial:**")
            show_cuenca_hierarchy(p)
            if p.get("comuna_nombre") and p["comuna_nombre"] != "N/A":
                st.caption(f"Comuna: {p['comuna_nombre']} | Precisión: {p.get('precision_ubicacion', 'N/A')}")

            # Module specific
            st.markdown("**📋 Detalle específico:**")
            if t == "Conflicto":
                if o.get("conflicto_actores_involucrados"): st.write(f"Actores: {o['conflicto_actores_involucrados']}")
                cols = st.columns(3)
                cols[0].metric("Gravedad", o.get("conflicto_gravedad", "N/A"))
                cols[1].metric("Duración", o.get("conflicto_duracion", "N/A"))
                cols[2].metric("Diálogo", o.get("conflicto_dialogo", "N/A"))
            elif t == "Iniciativa":
                if o.get("iniciativa_tipos"): st.write(f"Tipos: {', '.join(o['iniciativa_tipos']) if isinstance(o['iniciativa_tipos'], list) else o['iniciativa_tipos']}")
                c1, c2 = st.columns(2)
                c1.metric("Estado", o.get("iniciativa_estado", "N/A"))
                c2.metric("Escala", o.get("iniciativa_escala", "N/A"))
            elif t == "Actor":
                if o.get("actor_nombre"): st.write(f"**{o['actor_nombre']}** ({o.get('actor_tipo', 'N/A')})")
            elif t == "Oportunidad":
                c1, c2 = st.columns(2)
                c1.metric("Viabilidad", o.get("oportunidad_viabilidad", "N/A"))
                c2.metric("Urgencia", o.get("oportunidad_urgencia", "N/A"))
                if o.get("oportunidad_brechas"):
                    brechas = o["oportunidad_brechas"] if isinstance(o["oportunidad_brechas"], list) else [o["oportunidad_brechas"]]
                    st.write(f"Brechas: {', '.join(brechas)}")

            # Dimensions
            st.markdown("**📊 Dimensiones:**")
            cols = st.columns(6)
            for col, (emoji, k) in zip(cols, [("💧", "dim_agua"), ("🌿", "dim_entorno"), ("👥", "dim_social"),
                                               ("🏛️", "dim_gobernanza"), ("💰", "dim_financiamiento"), ("♻️", "dim_regeneracion")]):
                col.caption(emoji); col.write(o.get(k, "NS/NR"))
            if o.get("dim_importancia_lugar"): st.caption(f"🎯 {o['dim_importancia_lugar']}")

            # Enlaces
            enl = o.get("enlaces")
            if enl:
                st.markdown("**🔗 Enlaces:**")
                show_enlaces(enl if isinstance(enl, dict) else {})
    footer()

# ===== MAPA =====
def sec_mapa():
    hero("Mapa territorial de cuencas")
    demo_banner()
    st.markdown('<div class="edu">Visualiza registros como marcadores, mapa de calor o <strong>mapa coroplético</strong> pintando cuencas por densidad. Selecciona el nivel territorial: cuenca, subcuenca o subsubcuenca.</div>', unsafe_allow_html=True)

    s = stats()
    if not s or s.get("total", 0) == 0: st.info("Sin datos."); return
    obs, pts = s["observaciones"], s["puntos"]
    pm = {p["id"]: p for p in pts}

    c1, c2 = st.columns(2)
    with c1: ft = st.multiselect("Tipo", TIPOS_REGISTRO, default=TIPOS_REGISTRO, key="mft")
    with c2: fc = st.selectbox("Cuenca", ["Todas"] + s.get("cuencas_list", []), key="mfc")

    # Level selector (applies to ALL views)
    nivel = st.radio("Nivel territorial", ["Cuencas", "Subcuencas", "Subsubcuencas"], horizontal=True, key="mniv")
    vista = st.radio("Vista del mapa", ["📍 Marcadores", "🎨 Mapa de calor", "🗺️ Coroplético (capas de color)"], horizontal=True)

    filtered = [(o, pm[o["punto_id"]]) for o in obs if o["tipo"] in ft and o["punto_id"] in pm and (fc == "Todas" or pm[o["punto_id"]].get("cuenca") == fc)]
    st.caption(f"**{len(filtered)}** registros")

    m = folium.Map(location=MAP_CENTER, zoom_start=MAP_ZOOM, tiles="CartoDB positron")

    # Try to load choropleth layer (used by coropletico and optionally as overlay)
    nivel_key = nivel.lower()
    gdf_layer = None
    try:
        from geo_utils import get_geojson_simplified, build_choropleth_data
        gdf_layer = get_geojson_simplified(nivel_key)
    except Exception:
        pass

    if vista == "📍 Marcadores":
        # Optionally show cuenca boundaries as light overlay
        if gdf_layer is not None:
            folium.GeoJson(
                gdf_layer.to_json(),
                style_function=lambda x: {"fillColor": "transparent", "color": "#94A3B8", "weight": 0.8, "fillOpacity": 0},
                tooltip=folium.GeoJsonTooltip(fields=["_name"], aliases=[nivel[:-1]]),
            ).add_to(m)
        for o, p in filtered:
            t = o["tipo"]
            popup = f'<div style="max-width:260px;font-family:sans-serif"><strong>{o["titulo"]}</strong><br><span style="color:{COLORS[t]};font-weight:600">{EMOJIS[t]} {t}</span><br><small>📍 {p.get("cuenca","N/A")} → {p.get("subcuenca","")} → {p.get("subsubcuenca","")}</small></div>'
            folium.Marker([p["lat"], p["lon"]], popup=folium.Popup(popup, max_width=280),
                          icon=folium.Icon(color=FOLIUM_COLORS.get(t, "gray"), icon=FOLIUM_ICONS.get(t, "info-sign"), prefix="fa")).add_to(m)

    elif vista == "🎨 Mapa de calor":
        # Show boundaries + heatmap
        if gdf_layer is not None:
            folium.GeoJson(
                gdf_layer.to_json(),
                style_function=lambda x: {"fillColor": "transparent", "color": "#94A3B8", "weight": 0.8, "fillOpacity": 0},
                tooltip=folium.GeoJsonTooltip(fields=["_name"], aliases=[nivel[:-1]]),
            ).add_to(m)
        heat_data = [[p["lat"], p["lon"]] for _, p in filtered]
        if heat_data: HeatMap(heat_data, radius=20, blur=15, max_zoom=10).add_to(m)

    elif "Coroplético" in vista:
        if gdf_layer is not None:
            counts = build_choropleth_data(nivel_key, [o for o, _ in filtered], pts)
            gdf_layer["registros"] = gdf_layer["_name"].map(counts).fillna(0).astype(int)
            max_c = int(gdf_layer["registros"].max()) if gdf_layer["registros"].max() > 0 else 1

            import branca.colormap as cm
            colormap = cm.LinearColormap(["#F0F4F8", "#FCD34D", "#EF4444"], vmin=0, vmax=max_c, caption=f"Registros por {nivel[:-1].lower()}")

            def style_fn(feat, _cm=colormap):
                n = feat["properties"].get("registros", 0)
                return {"fillColor": _cm(n), "color": "#64748B", "weight": 0.8,
                        "fillOpacity": 0.65 if n > 0 else 0.08}

            folium.GeoJson(
                gdf_layer.to_json(),
                style_function=style_fn,
                tooltip=folium.GeoJsonTooltip(fields=["_name", "registros"], aliases=[nivel[:-1], "Registros"]),
            ).add_to(m)
            colormap.add_to(m)

            # Summary table
            with st.expander(f"📋 Tabla: registros por {nivel[:-1].lower()}"):
                df_counts = gdf_layer[gdf_layer["registros"] > 0][["_name", "registros"]].sort_values("registros", ascending=False).rename(columns={"_name": nivel[:-1], "registros": "Registros"})
                if len(df_counts) > 0:
                    st.dataframe(df_counts, use_container_width=True, hide_index=True)
                else:
                    st.caption("No hay registros en este nivel.")
        else:
            st.warning(f"Shapefiles de {nivel.lower()} no disponibles. Verifica que la carpeta data/ contenga los archivos .shp de la DGA.")

    with st.expander("📐 Metodología del mapa"):
        st.markdown('<div class="meth"><strong>Marcadores</strong>: Cada pin = un registro. Color = tipo.<br><strong>Mapa de calor</strong>: Densidad de registros. Rojo = alta concentración.<br><strong>Coroplético</strong>: Polígonos de la DGA pintados según cantidad de registros. Más oscuro = más registros. Funciona a nivel de cuenca, subcuenca y subsubcuenca.<br><br>Los límites de cuencas provienen de la <a href="https://dga.mop.gob.cl/administracionrecursoshidricos/mapoteca/Paginas/default.aspx">Mapoteca Digital de la DGA</a>.</div>', unsafe_allow_html=True)

    st_folium(m, width=None, height=550, returned_objects=[])
    footer()

# ===== DASHBOARD =====
def sec_dashboard():
    hero("Diagnóstico territorial colectivo")
    demo_banner()
    st.markdown('<div class="edu">Filtra por cuenca, subcuenca o subsubcuenca para ver el diagnóstico de <strong>tu territorio específico</strong>. Las cuencas se definen según la <a href="https://dga.mop.gob.cl/administracionrecursoshidricos/mapoteca/Paginas/default.aspx" target="_blank">DGA</a>.</div>', unsafe_allow_html=True)

    s = stats()
    if not s or s.get("total", 0) == 0: st.info("Sin datos."); return

    # FILTROS TERRITORIALES
    obs_f, pts, pm, territory_label = territory_filter(s["observaciones"], s["puntos"], prefix="dash")

    if len(obs_f) == 0:
        st.info("No hay registros para los filtros seleccionados."); footer(); return

    # Recalculate stats from filtered data
    bt = {}
    for o in obs_f: bt[o["tipo"]] = bt.get(o["tipo"], 0) + 1

    # Metrics
    cols = st.columns(5)
    for col, (n, l, c) in zip(cols, [(len(obs_f), "Total", "#1E293B"), (bt.get("Conflicto", 0), "Conflictos", COLORS["Conflicto"]),
        (bt.get("Iniciativa", 0), "Iniciativas", COLORS["Iniciativa"]), (bt.get("Actor", 0), "Actores", COLORS["Actor"]),
        (bt.get("Oportunidad", 0), "Oportunidades", COLORS["Oportunidad"])]):
        col.markdown(f'<div class="mc"><div class="n" style="color:{c}">{n}</div><div class="l">{l}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Distribución por tipo")
        with st.expander("📐 Metodología: Distribución por tipo"):
            st.markdown("""<div class="meth">
<strong>¿Qué muestra?</strong> La proporción de cada tipo de registro sobre el total filtrado.<br><br>
<strong>¿Cómo se construye?</strong> Se cuenta el número de registros por tipo dentro del filtro territorial seleccionado.<br><br>
<strong>¿Cómo interpretarlo?</strong><br>
• <strong>Predominio de conflictos (rojo > 40%)</strong>: Territorio en tensión.<br>
• <strong>Predominio de iniciativas (verde > 40%)</strong>: Capacidad de acción comunitaria.<br>
• <strong>Distribución equilibrada</strong>: Señal saludable — problemas identificados con respuestas activas.<br>
• <strong>Pocos actores (azul < 10%)</strong>: Falta mapear la red de actores, lo que dificulta la coordinación.
</div>""", unsafe_allow_html=True)
        if bt:
            fig = px.pie(names=list(bt.keys()), values=list(bt.values()), color=list(bt.keys()), color_discrete_map=COLORS, hole=0.45)
            fig.update_layout(margin=dict(t=20, b=20), height=320, legend=dict(orientation="h", y=-0.15))
            fig.update_traces(textinfo="percent+label", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Radar de dimensiones")
        with st.expander("📐 Metodología: Radar de dimensiones"):
            st.markdown("""<div class="meth">
<strong>¿Qué muestra?</strong> El perfil multidimensional del territorio filtrado en 6 ejes.<br><br>
<strong>¿Cómo se construye?</strong> Promedio ponderado de cada dimensión normalizado a 0-100%.<br><br>
<strong>¿Cómo interpretarlo?</strong><br>
• <strong>Cerca del centro (< 30%)</strong>: Dimensiones críticas.<br>
• <strong>Cerca del borde (> 70%)</strong>: Fortalezas del territorio.<br>
• <strong>Radar aplastado</strong>: Desequilibrio sistémico.<br>
• <strong>Uniformemente bajo</strong>: Crisis integral. <strong>Uniformemente alto</strong>: Territorio resiliente.
</div>""", unsafe_allow_html=True)
        rv, rl = [], []
        for d, lb in DIM_LABELS.items():
            sm = SCORE_MAP.get(d, {}); ts, tc = 0, 0
            for o in obs_f:
                sc = sm.get(o.get(f"dim_{d}", ""), 0)
                if sc > 0: ts += sc; tc += 1
            avg = (ts / tc) if tc > 0 else 0; mx = max(sm.values()) if sm else 4
            rv.append(round((avg / mx) * 100, 1)); rl.append(lb)
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=rv + [rv[0]], theta=rl + [rl[0]], fill="toself", fillcolor="rgba(37,99,235,.15)", line=dict(color="#2563EB", width=2)))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], showticklabels=False)), margin=dict(t=30, b=30, l=60, r=60), height=320, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Stacked bar by subcuenca (within filtered territory)
    st.divider(); st.subheader("Registros por subcuenca")
    with st.expander("📐 Metodología: Registros por subcuenca"):
        st.markdown("""<div class="meth">
<strong>¿Qué muestra?</strong> La composición de registros desglosada por subcuenca dentro del filtro seleccionado.<br><br>
<strong>¿Cómo interpretarlo?</strong><br>
• <strong>Barras predominantemente rojas</strong>: Subcuencas en conflicto sin respuesta organizada.<br>
• <strong>Barras con variedad de colores</strong>: Ecosistemas de gobernanza más desarrollados.<br>
• <strong>Subcuencas sin barra</strong>: Puede indicar falta de participantes, no ausencia de problemas.
</div>""", unsafe_allow_html=True)
    cd = {}
    for o in obs_f:
        p = pm.get(o["punto_id"])
        if p:
            sub = p.get("subcuenca", "N/A")
            if sub != "N/A": cd.setdefault(sub, {}).setdefault(o["tipo"], 0); cd[sub][o["tipo"]] += 1
    if cd:
        rows = [{"Subcuenca": c, "Tipo": t, "Cantidad": n} for c, ts in cd.items() for t, n in ts.items() if n > 0]
        fig = px.bar(pd.DataFrame(rows), x="Subcuenca", y="Cantidad", color="Tipo", color_discrete_map=COLORS, barmode="stack")
        fig.update_layout(margin=dict(t=20, b=20), height=350, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    # Heatmap dimensions by subcuenca
    st.divider(); st.subheader("Dimensiones por subcuenca")
    with st.expander("📐 Metodología: Heatmap de dimensiones"):
        st.markdown("""<div class="meth">
<strong>¿Qué muestra?</strong> Matriz subcuenca × dimensión. Cada celda = score promedio normalizado (0-100%).<br><br>
<strong>¿Cómo interpretarlo?</strong><br>
• <strong>Rojo (< 40%)</strong>: Dimensión crítica. <strong>Verde (> 60%)</strong>: Fortaleza.<br>
• <strong>Columna entera roja</strong>: Dimensión débil en todo el territorio (problema estructural).<br>
• <strong>Fila entera roja</strong>: Subcuenca en estado crítico integral.
</div>""", unsafe_allow_html=True)
    cdims = {}
    for o in obs_f:
        p = pm.get(o["punto_id"])
        if not p: continue
        sub = p.get("subcuenca", "N/A")
        if sub == "N/A": continue
        cdims.setdefault(sub, {d: [] for d in SCORE_MAP})
        for d, sm in SCORE_MAP.items():
            sc = sm.get(o.get(f"dim_{d}", ""), 0)
            if sc > 0: cdims[sub][d].append(sc)
    if cdims:
        hr = []
        for c, dd in cdims.items():
            row = {"Subcuenca": c}
            for d, lb in DIM_LABELS.items():
                vs = dd.get(d, []); mx = max(SCORE_MAP[d].values()) if SCORE_MAP.get(d) else 4
                row[lb] = round((sum(vs) / len(vs) / mx * 100), 0) if vs else 0
            hr.append(row)
        dh = pd.DataFrame(hr).set_index("Subcuenca")
        fig = px.imshow(dh, aspect="auto", color_continuous_scale=["#EF4444", "#FCD34D", "#22C55E"], labels=dict(color="Score %"))
        fig.update_layout(margin=dict(t=20, b=20), height=max(200, len(hr) * 40 + 80))
        st.plotly_chart(fig, use_container_width=True)

    # Timeline
    st.divider(); st.subheader("Actividad reciente")
    for o in obs_f[:12]:
        t = o["tipo"]; f = o.get("created_at", "")[:10]
        st.markdown(f'<div style="display:flex;align-items:center;gap:.8rem;padding:.5rem 0;border-bottom:1px solid #F1F5F9"><span class="tb t{t[0].lower()}">{EMOJIS[t]} {t}</span><span style="flex:1;font-size:.9rem"><strong>{o["titulo"]}</strong></span><span style="color:#94A3B8;font-size:.8rem">{f}</span></div>', unsafe_allow_html=True)
    footer()

# ===== RED =====
def sec_red():
    hero("Análisis de conexiones territoriales")
    demo_banner()
    st.markdown('<div class="edu">Filtra por cuenca, subcuenca o subsubcuenca para analizar las conexiones de <strong>tu territorio</strong>. Los registros no son independientes — este análisis revela relaciones ocultas.</div>', unsafe_allow_html=True)
    s = stats()
    if not s or s.get("total", 0) < 5: st.info("Se necesitan al menos 5 registros."); return

    # FILTROS TERRITORIALES
    obs_f, pts, pm, territory_label = territory_filter(s["observaciones"], s["puntos"], prefix="red")

    if len(obs_f) < 3:
        st.info(f"Solo {len(obs_f)} registros en {territory_label}. Se necesitan al menos 3 para el análisis."); footer(); return

    # Co-ocurrencia
    st.subheader("🗺️ Co-ocurrencia por subsubcuenca")
    with st.expander("📐 Metodología: Matriz de co-ocurrencia"):
        st.markdown("""<div class="meth">
<strong>¿Qué muestra?</strong> En cuántas subsubcuencas coexisten distintos tipos de registro dentro del territorio filtrado.<br><br>
<strong>¿Cómo interpretarlo?</strong><br>
• <strong>Alta co-ocurrencia Conflicto-Iniciativa</strong>: Comunidades respondiendo activamente.<br>
• <strong>Alta co-ocurrencia Conflicto-Oportunidad</strong>: Ventanas de acción donde hay tensión.<br>
• <strong>Baja co-ocurrencia Conflicto-Actor</strong>: Desconexión entre gobernanza y realidad territorial.
</div>""", unsafe_allow_html=True)
    sub_t = {}
    for o in obs_f:
        p = pm.get(o["punto_id"])
        if p and p.get("subsubcuenca", "N/A") != "N/A": sub_t.setdefault(p["subsubcuenca"], []).append(o["tipo"])
    tl = TIPOS_REGISTRO; cooc = pd.DataFrame(0, index=tl, columns=tl)
    for ts in sub_t.values():
        for t1 in tl:
            for t2 in tl:
                if t1 in ts and t2 in ts: cooc.loc[t1, t2] += 1
    fig = px.imshow(cooc, text_auto=True, color_continuous_scale=["#F8FAFC", "#2563EB"])
    fig.update_layout(margin=dict(t=20, b=20), height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Actores
    st.subheader("👥 Red de actores")
    with st.expander("📐 Metodología: Red de actores"):
        st.markdown("""<div class="meth">
<strong>¿Qué muestra?</strong> Actores mencionados en los registros filtrados. Tamaño = frecuencia. Color rojo = presencia en múltiples cuencas.<br><br>
<strong>Para la gobernanza</strong>: Los actores multi-cuenca son aliados estratégicos para iniciativas regionales. Los actores locales con presencia en zonas de conflicto son voces que necesitan ser escuchadas.
</div>""", unsafe_allow_html=True)
    am = {}
    for o in obs_f:
        p = pm.get(o["punto_id"]); sub = p.get("subcuenca", "N/A") if p else "N/A"
        names = []
        if o.get("actor_nombre"): names.append(o["actor_nombre"])
        if o.get("conflicto_actores_involucrados"): names.extend([x.strip() for x in o["conflicto_actores_involucrados"].replace(" vs ", "|").replace(" y ", "|").split("|") if x.strip()])
        for n in names:
            am.setdefault(n, {"c": 0, "subs": set(), "cuencas": set()})
            am[n]["c"] += 1; am[n]["subs"].add(sub)
            if p: am[n]["cuencas"].add(p.get("cuenca", "N/A"))
    if am:
        ar = [{"Actor": n, "Menciones": d["c"], "Subcuencas": len(d["subs"]),
               "Alcance": "🔴 Multi-cuenca" if len(d["cuencas"]) > 1 else "🟢 Local"}
              for n, d in sorted(am.items(), key=lambda x: -x[1]["c"])]
        fig = px.scatter(pd.DataFrame(ar), x="Subcuencas", y="Menciones", size="Menciones", color="Alcance", text="Actor",
                        color_discrete_map={"🔴 Multi-cuenca": "#EF4444", "🟢 Local": "#22C55E"})
        fig.update_traces(textposition="top center", textfont_size=9)
        fig.update_layout(margin=dict(t=20, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Conflicto → respuesta
    st.subheader("⚡ Balance conflicto → respuesta por subcuenca")
    with st.expander("📐 Metodología: Balance conflicto → respuesta"):
        st.markdown("""<div class="meth">
<strong>¿Qué muestra?</strong> Relación conflictos vs iniciativas en cada subcuenca del territorio filtrado.<br><br>
<strong>¿Cómo interpretarlo?</strong><br>
• <strong>Sobre la diagonal (✅)</strong>: Respuesta activa. <strong>Bajo la diagonal (⚠️)</strong>: Brecha.<br>
• <strong>Puntos grandes</strong>: Muchas oportunidades detectadas — potencial de acción.<br>
• <strong>Uso estratégico</strong>: Subcuencas bajo la diagonal con puntos grandes son las de mayor potencial de impacto.
</div>""", unsafe_allow_html=True)
    sb = {}
    for o in obs_f:
        p = pm.get(o["punto_id"])
        if p and p.get("subcuenca", "N/A") != "N/A":
            sb.setdefault(p["subcuenca"], {"Conflicto": 0, "Iniciativa": 0, "Oportunidad": 0})
            sb[p["subcuenca"]][o["tipo"]] = sb[p["subcuenca"]].get(o["tipo"], 0) + 1
    if sb:
        br = [{"Subcuenca": sc, "Conflictos": d["Conflicto"], "Iniciativas": d["Iniciativa"], "Oportunidades": max(d["Oportunidad"], 1),
               "Estado": "✅" if (d["Iniciativa"] / d["Conflicto"] if d["Conflicto"] > 0 else 9) >= 1 else "⚠️"} for sc, d in sb.items()]
        dfb = pd.DataFrame(br)
        fig = px.scatter(dfb, x="Conflictos", y="Iniciativas", size="Oportunidades", color="Estado", hover_name="Subcuenca",
                        color_discrete_map={"✅": "#22C55E", "⚠️": "#EF4444"})
        mx = max(dfb["Conflictos"].max(), dfb["Iniciativas"].max(), 1)
        fig.add_trace(go.Scatter(x=[0, mx], y=[0, mx], mode="lines", line=dict(dash="dash", color="#94A3B8"), name="1:1"))
        fig.update_layout(margin=dict(t=20, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)
    footer()

# ===== MIS REGISTROS =====
def sec_mis():
    hero("Tus aportes")
    if st.session_state.demo_mode: st.info("Crea una cuenta para tener registros propios."); footer(); return
    mis = get_observaciones_by_user(st.session_state.user)
    if not mis: st.info("Sin registros. Ve a **Nuevo Registro**."); footer(); return
    for o in mis:
        t = o["tipo"]; f = o.get("created_at", "")[:10]
        with st.expander(f"{EMOJIS[t]} {o['titulo']} — {t} · {f}"):
            st.write(o.get("descripcion", ""))
            if st.button("🗑️ Eliminar", key=f"d_{o['id']}"):
                if delete_observacion(o["id"], st.session_state.user): st.success("Eliminado"); st.rerun()
    footer()

# ===== PERFIL =====
def sec_perfil():
    hero("Tu información")
    if st.session_state.demo_mode: st.info("No editable en demo."); footer(); return
    pr = st.session_state.profile
    with st.form("pf"):
        n = st.text_input("Nombre", value=pr.get("nombre", ""))
        org = st.text_input("Organización", value=pr.get("organizacion", "") or "")
        ta = st.selectbox("Tipo", TIPOS_ACTOR, index=TIPOS_ACTOR.index(pr["tipo_actor"]) if pr.get("tipo_actor") in TIPOS_ACTOR else 0)
        if st.form_submit_button("💾 Guardar", use_container_width=True):
            if update_user_profile(st.session_state.user, {"nombre": n, "organizacion": org, "tipo_actor": ta}):
                st.session_state.profile.update({"nombre": n, "organizacion": org, "tipo_actor": ta}); st.success("✅")
    footer()

# ===== MAIN =====
def main():
    if not SUPABASE_URL or not SUPABASE_KEY:
        hero("Configuración pendiente")
        st.warning("Credenciales no configuradas.")
        if st.button("🧪 Modo demostración", type="primary"):
            st.session_state.demo_mode = True; st.session_state.user = "demo"
            st.session_state.profile = {"nombre": "Explorador/a Demo", "tipo_actor": "Sociedad Civil", "organizacion": "", "email": "demo@demo.cl"}
            st.rerun()
        footer(); return
    if not st.session_state.user:
        if not test_connection():
            hero("Sin conexión")
            if st.button("🧪 Modo demostración", type="primary"):
                st.session_state.demo_mode = True; st.session_state.user = "demo"
                st.session_state.profile = {"nombre": "Explorador/a Demo", "tipo_actor": "Sociedad Civil", "organizacion": "", "email": "demo@demo.cl"}
                st.rerun()
            footer(); return
        pantalla_auth(); return
    sec = sidebar()
    {"📝 Nuevo Registro": sec_registro, "🔍 Explorar Registros": sec_explorar, "🗺️ Mapa": sec_mapa,
     "📊 Dashboard": sec_dashboard, "🔗 Análisis de Red": sec_red, "📋 Mis Registros": sec_mis, "⚙️ Perfil": sec_perfil}.get(sec, sec_registro)()

if __name__ == "__main__":
    main()
