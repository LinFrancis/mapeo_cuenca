"""
demo_data.py — v2.0. 100 casos con enlaces, comunas, precisión.
"""
import random
from datetime import datetime, timedelta
random.seed(42)

MAIPO_SUBS = {
    "Río Maipo Alto": {"c": [-33.60, -70.10], "s": 0.08, "ss": ["Volcán", "San José de Maipo", "El Yeso"], "comunas": ["San José de Maipo", "Puente Alto"]},
    "Río Mapocho": {"c": [-33.42, -70.63], "s": 0.06, "ss": ["Lo Barnechea", "Vitacura", "Providencia"], "comunas": ["Lo Barnechea", "Vitacura", "Providencia", "Santiago"]},
    "Río Clarillo": {"c": [-33.72, -70.48], "s": 0.05, "ss": ["Pirque", "Reserva Clarillo"], "comunas": ["Pirque"]},
    "Río Angostura": {"c": [-33.85, -70.72], "s": 0.06, "ss": ["Paine", "Buin", "Linderos"], "comunas": ["Paine", "Buin"]},
    "Río Maipo Bajo": {"c": [-33.65, -71.20], "s": 0.08, "ss": ["Melipilla", "Pomaire", "San Pedro"], "comunas": ["Melipilla", "Talagante"]},
}
OTRAS = {
    "Río Rapel": {"c": [-34.20, -71.30], "s": 0.15, "sub": "Río Cachapoal", "ss": ["Rancagua", "Machalí", "Requínoa"], "comunas": ["Rancagua", "Machalí"]},
    "Río Maule": {"c": [-35.40, -71.50], "s": 0.20, "sub": "Río Claro", "ss": ["Talca", "San Clemente", "Yerbas Buenas"], "comunas": ["Talca", "Linares"]},
    "Río Biobío": {"c": [-37.00, -72.50], "s": 0.20, "sub": "Río Laja", "ss": ["Los Ángeles", "Nacimiento", "Sta. Bárbara"], "comunas": ["Los Ángeles", "Concepción"]},
    "Río Aconcagua": {"c": [-32.85, -70.80], "s": 0.12, "sub": "Río Putaendo", "ss": ["San Felipe", "Los Andes", "Putaendo"], "comunas": ["Los Andes", "San Felipe"]},
    "Río Elqui": {"c": [-29.95, -71.00], "s": 0.15, "sub": "Río Turbio", "ss": ["Vicuña", "Paihuano", "La Serena"], "comunas": ["La Serena", "Vicuña"]},
}
ACTORES = ["Junta de Vigilancia Río Maipo", "Comité APR La Obra", "ONG Río Vivo", "Aguas Andinas S.A.",
    "Municipalidad San José de Maipo", "Comunidad Ecológica Peñalolén", "Colectivo Agua que has de Beber",
    "DGA Región Metropolitana", "Fundación Chile Sustentable", "U. de Chile - Depto Geología",
    "Cooperativa Campesina Melipilla", "Minera Los Bronces", "Red Monitoras Ambientales del Maipo",
    "Consejo Regional CORE RM", "Escuela Rural El Manzano"]

CONF = [
    {"t": "Contaminación de relaves en {z}", "d": "Relaves filtran metales pesados al estero, afectando agua de riego.", "a": "Minera vs comunidad agrícola", "g": "Crítico", "dur": "Años", "dia": "Bajo"},
    {"t": "Escasez hídrica en {z}", "d": "Pozos secos hace 3 temporadas por sobreexplotación del acuífero.", "a": "Agroindustria vs habitantes rurales", "g": "Alto", "dur": "Años", "dia": "Nulo"},
    {"t": "Vertido de aguas servidas en {z}", "d": "Planta colapsada vierte al río. Vecinos denunciaron sin respuesta.", "a": "Empresa sanitaria vs vecinos", "g": "Alto", "dur": "Meses", "dia": "Bajo"},
    {"t": "Extracción de áridos en ribera de {z}", "d": "Extracción sin permisos. Erosión amenaza caminos.", "a": "Constructora vs municipio y vecinos", "g": "Medio", "dur": "Meses", "dia": "Medio"},
    {"t": "Disputa derechos de agua en {z}", "d": "Fundo desvía 80% del caudal. Comunidad sin acceso.", "a": "Fundo agrícola vs comunidad", "g": "Crítico", "dur": "Crónico", "dia": "Bajo"},
]
INIC = [
    {"t": "Restauración de ribera en {z}", "d": "Plantación de especies nativas en 2km de ribera degradada.", "tipos": ["Restauración de ribera", "Plantación/reforestación"], "est": "En marcha", "esc": "Local"},
    {"t": "Monitoreo ciudadano de agua en {z}", "d": "Red de 20 puntos de monitoreo con vecinos capacitados.", "tipos": ["Monitoreo ambiental", "Educación/conciencia"], "est": "Consolidado", "esc": "Subcuenca"},
    {"t": "Mesa de gobernanza hídrica en {z}", "d": "Espacio multiactor para gestión participativa del agua.", "tipos": ["Gestión participativa"], "est": "En marcha", "esc": "Subcuenca"},
    {"t": "Cosecha de aguas lluvia en {z}", "d": "Sistemas en 45 viviendas rurales. Reduce dependencia de aljibe 60%.", "tipos": ["Infraestructura hídrica"], "est": "Consolidado", "esc": "Local"},
]
OPOR = [
    {"t": "Fondo FPA para restauración en {z}", "d": "Convocatoria abierta. Hasta $20M por proyecto.", "v": "Alto", "u": "Alto", "b": ["Financiamiento", "Capacidades técnicas"]},
    {"t": "Alianza universidad-comunidad en {z}", "d": "Asistencia técnica gratuita para monitoreo de agua.", "v": "Alto", "u": "Medio", "b": ["Coordinación", "Información"]},
    {"t": "Plan regulador en revisión en {z}", "d": "Ventana para incluir protección de riberas.", "v": "Medio", "u": "Alto", "b": ["Apoyo institucional", "Marco legal"]},
]

def _dims(tipo):
    if tipo == "Conflicto":
        return {"agua": random.choice(["Muy escasa", "Escasa"]), "entorno": random.choice(["Muy degradado", "Degradado"]),
                "social": random.choice(["Débil", "Muy débil"]), "gobernanza": random.choice(["Muy débil", "Débil"]),
                "financiamiento": random.choice(["Muy difícil", "Difícil"]), "regeneracion": random.choice(["Bajo", "Medio"])}
    elif tipo == "Iniciativa":
        return {"agua": random.choice(["Escasa", "Suficiente"]), "entorno": random.choice(["En recuperación", "Degradado"]),
                "social": random.choice(["Media", "Fuerte"]), "gobernanza": random.choice(["Media", "Débil"]),
                "financiamiento": random.choice(["Difícil", "Medio"]), "regeneracion": random.choice(["Medio", "Alto"])}
    elif tipo == "Actor":
        return {"agua": random.choice(["Suficiente", "Escasa"]), "entorno": random.choice(["Degradado", "En recuperación"]),
                "social": random.choice(["Fuerte", "Media"]), "gobernanza": random.choice(["Media", "Fuerte"]),
                "financiamiento": random.choice(["Medio", "Difícil"]), "regeneracion": random.choice(["Medio", "Alto"])}
    else:
        return {"agua": random.choice(["Escasa", "Suficiente"]), "entorno": random.choice(["En recuperación", "Degradado"]),
                "social": random.choice(["Media", "Fuerte"]), "gobernanza": random.choice(["Débil", "Media"]),
                "financiamiento": random.choice(["Medio", "Difícil"]), "regeneracion": random.choice(["Alto", "Medio"])}

def _enlaces(tipo):
    e = {}
    if random.random() > 0.5: e["youtube"] = f"https://youtube.com/watch?v=demo{random.randint(100,999)}"
    if random.random() > 0.6: e["fotos"] = [f"https://ejemplo.cl/foto{random.randint(1,50)}.jpg"]
    if random.random() > 0.7: e["otros"] = [f"https://ejemplo.cl/doc{random.randint(1,20)}.pdf"]
    if tipo == "Actor" and random.random() > 0.4: e["perfil"] = f"https://ejemplo.cl/actor{random.randint(1,15)}"
    return e

def _make(i, cuenca, sub, subsub, lat, lon, comuna, prec):
    _id = 9000 + i
    fecha = (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
    r = random.random()
    if r < 0.28:
        tipo, tpl = "Conflicto", random.choice(CONF)
        mod = {"actores": tpl["a"], "gravedad": tpl["g"], "duracion": tpl["dur"], "dialogo": tpl["dia"]}
        titulo, desc = tpl["t"].replace("{z}", subsub), tpl["d"]
    elif r < 0.58:
        tipo, tpl = "Iniciativa", random.choice(INIC)
        mod = {"tipos": tpl["tipos"], "estado": tpl["est"], "escala": tpl["esc"]}
        titulo, desc = tpl["t"].replace("{z}", subsub), tpl["d"]
    elif r < 0.78:
        tipo, tpl = "Oportunidad", random.choice(OPOR)
        mod = {"viabilidad": tpl["v"], "urgencia": tpl["u"], "brechas": tpl["b"]}
        titulo, desc = tpl["t"].replace("{z}", subsub), tpl["d"]
    else:
        tipo = "Actor"; a = random.choice(ACTORES)
        mod = {"nombre": a, "tipo": random.choice(["Org formal", "Junta de vecinos", "Grupo informal", "Institución pública", "Empresa"])}
        titulo = f"{a} — {subsub}"; desc = f"Actor activo en {subsub}, cuenca {cuenca}."

    dims = _dims(tipo); enl = _enlaces(tipo)
    punto = {"id": _id, "lat": round(lat, 6), "lon": round(lon, 6), "cuenca": cuenca, "subcuenca": sub,
             "subsubcuenca": subsub, "comuna_nombre": comuna, "precision_ubicacion": prec, "created_at": fecha}
    obs = {"id": _id, "punto_id": _id, "tipo": tipo, "titulo": titulo, "descripcion": desc,
           "created_at": fecha, "modulo": mod, "enlaces": enl,
           **{f"dim_{k}": v for k, v in dims.items()},
           "dim_importancia_lugar": f"Sector {subsub}, subcuenca {sub}, cuenca {cuenca}."}
    if tipo == "Conflicto": obs.update({"conflicto_actores_involucrados": mod.get("actores"), "conflicto_gravedad": mod.get("gravedad"), "conflicto_duracion": mod.get("duracion"), "conflicto_dialogo": mod.get("dialogo")})
    elif tipo == "Iniciativa": obs.update({"iniciativa_tipos": mod.get("tipos"), "iniciativa_estado": mod.get("estado"), "iniciativa_escala": mod.get("escala")})
    elif tipo == "Actor": obs.update({"actor_nombre": mod.get("nombre"), "actor_tipo": mod.get("tipo")})
    elif tipo == "Oportunidad": obs.update({"oportunidad_viabilidad": mod.get("viabilidad"), "oportunidad_urgencia": mod.get("urgencia"), "oportunidad_brechas": mod.get("brechas")})
    return punto, obs

def generate_demo_data():
    regs = []; subs = list(MAIPO_SUBS.items())
    for i in range(50):
        sn, sd = subs[i % len(subs)]; ss = random.choice(sd["ss"]); com = random.choice(sd["comunas"])
        lat = sd["c"][0] + random.uniform(-sd["s"], sd["s"]); lon = sd["c"][1] + random.uniform(-sd["s"], sd["s"])
        prec = random.choice(["Exacta", "Aproximada", "Aproximada"])
        regs.append(_make(i, "Río Maipo", sn, ss, lat, lon, com, prec))
    otras = list(OTRAS.items())
    for i in range(50):
        cn, cd = otras[i % len(otras)]; ss = random.choice(cd["ss"]); com = random.choice(cd["comunas"])
        lat = cd["c"][0] + random.uniform(-cd["s"], cd["s"]); lon = cd["c"][1] + random.uniform(-cd["s"], cd["s"])
        prec = random.choice(["Exacta", "Aproximada", "Aproximada"])
        regs.append(_make(50+i, cn, cd.get("sub", cn), ss, lat, lon, com, prec))
    return {"puntos": [r[0] for r in regs], "observaciones": [r[1] for r in regs]}
