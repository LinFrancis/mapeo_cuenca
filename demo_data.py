"""
demo_data.py — v2.0 fixed. Uses REAL names from BNA shapefiles.
"""
import random
from datetime import datetime, timedelta
random.seed(42)

# REAL names from BNA shapefiles (COD_CUEN=057 Rio Maipo)
MAIPO_SUBS = {
    "Rio Maipo Alto": {
        "c": [-33.60, -70.10], "s": 0.08,
        "ss": ["Rio Maipo bajo junta Rio Negro", "Rio Maipo entre Rio Negro y Rio Volcan", "Rio Volcan", "Rio Yeso", "Rio Maipo entre Rio Volcan y Rio Colorado", "Rio Colorado antes junta Rio Olivares", "Rio Olivares"],
        "comunas": ["San José de Maipo", "Puente Alto"],
    },
    "Rio Maipo Medio": {
        "c": [-33.70, -70.55], "s": 0.08,
        "ss": ["Rio Maipo Entre Estero Colorado y Rio Clarillo", "Rio Clarillo", "Rio Maipo Entre Rio Clarillo y Estero Angostura", "Estero Angostura Antes Junta Estero Paine (I)", "Estero Paine", "Rio Maipo Entre Estero Angostura y Rio Mapocho"],
        "comunas": ["Pirque", "Puente Alto", "Buin", "Paine"],
    },
    "R.  Mapocho Alto": {
        "c": [-33.38, -70.50], "s": 0.06,
        "ss": ["Rio Molina", "Rio San Francisco", "Rio Mapocho Entre Rio San Francisco y Bajo Junta Estero Arrayan", "Rio Mapocho entre Estero Arrayan y bajo unta Estero de Las Rosas"],
        "comunas": ["Lo Barnechea", "Vitacura", "Las Condes", "Providencia"],
    },
    "Mapocho Bajo": {
        "c": [-33.42, -70.70], "s": 0.06,
        "ss": ["Rio Mapocho Entre Estero de Las Rosas y Estero Lampa y Bajo Zanjon de la Aguada", "Estero Lampa Entre Estero Colina y Rio Mapocho", "Estero Colina", "Estero Lampa Entre Estero Tiltil y Estero Colina", "Estero Tiltil", "Rio Mapocho entre Zanjon de la Aguada y Rio Maipo"],
        "comunas": ["Santiago", "Maipú", "Colina", "Ñuñoa"],
    },
    "Rio Maipo Bajo (Entre Rio Mapocho y Desembocadura)": {
        "c": [-33.65, -71.15], "s": 0.10,
        "ss": ["Rio Maipo Entre Rio Mapocho y Estero Puangue", "Estero Puangue Antes Estero Caren", "Estero Puangue Entre Estero de Los Mayos y Rio Maipo", "Rio Maipo entre Estero Puangue y bajo junta Estero Popeta", "Rio Maipo Entre Estero Popeta y Desembocadura"],
        "comunas": ["Melipilla", "Talagante"],
    },
}

# Other cuencas with REAL BNA names
OTRAS = {
    "Rio Rapel": {
        "c": [-34.20, -71.10], "s": 0.15, "sub": "Cachapoal Bajo",
        "ss": ["Cachapoal Bajo", "Rio Cachapoal Alto", "Tinguiririca Bajo"],
        "comunas": ["Rancagua", "Machalí", "San Fernando"],
    },
    "Rio Maule": {
        "c": [-35.40, -71.50], "s": 0.20, "sub": "Rio Claro",
        "ss": ["Rio Claro", "Maule Bajo", "Rio Maule Alto"],
        "comunas": ["Talca", "Linares", "Curicó"],
    },
    "Rio Bio-Bio": {
        "c": [-37.00, -72.50], "s": 0.20, "sub": "Laja Bajo",
        "ss": ["Laja Bajo", "Rio Laja Alto", "Rio Bio-Bio Bajo", "Rio Duqueco"],
        "comunas": ["Los Ángeles", "Concepción"],
    },
    "Rio Aconcagua": {
        "c": [-32.85, -70.80], "s": 0.12, "sub": "Aconcagua Alto",
        "ss": ["Aconcagua Alto", "Aconcagua Medio", "Aconcagua Bajo"],
        "comunas": ["Los Andes", "San Felipe", "Quillota"],
    },
    "Rio Elqui": {
        "c": [-29.95, -71.00], "s": 0.15, "sub": "Rio Elqui",
        "ss": ["Rio Elqui", "Q. Los Choros hasta junta Q. del Pelicano"],
        "comunas": ["La Serena", "Vicuña"],
    },
}

ACTORES = ["Junta de Vigilancia Rio Maipo", "Comite APR La Obra", "ONG Rio Vivo", "Aguas Andinas S.A.",
    "Municipalidad San Jose de Maipo", "Comunidad Ecologica Penalolen", "Colectivo Agua que has de Beber",
    "DGA Region Metropolitana", "Fundacion Chile Sustentable", "U. de Chile Depto Geologia",
    "Cooperativa Campesina Melipilla", "Minera Los Bronces", "Red Monitoras Ambientales del Maipo",
    "Consejo Regional CORE RM", "Escuela Rural El Manzano"]

CONF = [
    {"t": "Contaminacion de relaves en {z}", "d": "Relaves filtran metales pesados al estero, afectando agua de riego de agricultores.", "a": "Minera vs comunidad agricola", "g": "Critico", "dur": "Años", "dia": "Bajo"},
    {"t": "Escasez hidrica en {z}", "d": "Pozos secos hace 3 temporadas por sobreexplotacion del acuifero.", "a": "Agroindustria vs habitantes rurales", "g": "Alto", "dur": "Años", "dia": "Nulo"},
    {"t": "Vertido de aguas servidas en {z}", "d": "Planta colapsada vierte al rio. Vecinos denunciaron sin respuesta.", "a": "Empresa sanitaria vs vecinos", "g": "Alto", "dur": "Meses", "dia": "Bajo"},
    {"t": "Extraccion de aridos en {z}", "d": "Extraccion sin permisos. Erosion amenaza caminos y propiedades.", "a": "Constructora vs municipio y vecinos", "g": "Medio", "dur": "Meses", "dia": "Medio"},
    {"t": "Disputa derechos de agua en {z}", "d": "Gran fundo desvia 80% del caudal. Comunidad sin acceso.", "a": "Fundo agricola vs comunidad", "g": "Critico", "dur": "Crónico", "dia": "Bajo"},
]
INIC = [
    {"t": "Restauracion de ribera en {z}", "d": "Plantacion de especies nativas en 2km de ribera degradada.", "tipos": ["Restauración de ribera", "Plantación/reforestación"], "est": "En marcha", "esc": "Local"},
    {"t": "Monitoreo ciudadano de agua en {z}", "d": "Red de 20 puntos de monitoreo con vecinos capacitados.", "tipos": ["Monitoreo ambiental", "Educación/conciencia"], "est": "Consolidado", "esc": "Subcuenca"},
    {"t": "Mesa de gobernanza hidrica en {z}", "d": "Espacio multiactor para gestion participativa del agua.", "tipos": ["Gestión participativa"], "est": "En marcha", "esc": "Subcuenca"},
    {"t": "Cosecha de aguas lluvia en {z}", "d": "Sistemas en 45 viviendas rurales. Reduce dependencia de aljibe.", "tipos": ["Infraestructura hídrica"], "est": "Consolidado", "esc": "Local"},
]
OPOR = [
    {"t": "Fondo FPA para restauracion en {z}", "d": "Convocatoria abierta hasta $20M por proyecto.", "v": "Alto", "u": "Alto", "b": ["Financiamiento", "Capacidades técnicas"]},
    {"t": "Alianza universidad-comunidad en {z}", "d": "Asistencia tecnica gratuita para monitoreo de agua.", "v": "Alto", "u": "Medio", "b": ["Coordinación", "Información"]},
    {"t": "Plan regulador en revision en {z}", "d": "Ventana para incluir proteccion de riberas.", "v": "Medio", "u": "Alto", "b": ["Apoyo institucional", "Marco legal"]},
]

def _dims(t):
    if t == "Conflicto":
        return {"agua": random.choice(["Muy escasa","Escasa"]), "entorno": random.choice(["Muy degradado","Degradado"]),
                "social": random.choice(["Débil","Muy débil"]), "gobernanza": random.choice(["Muy débil","Débil"]),
                "financiamiento": random.choice(["Muy difícil","Difícil"]), "regeneracion": random.choice(["Bajo","Medio"])}
    elif t == "Iniciativa":
        return {"agua": random.choice(["Escasa","Suficiente"]), "entorno": random.choice(["En recuperación","Degradado"]),
                "social": random.choice(["Media","Fuerte"]), "gobernanza": random.choice(["Media","Débil"]),
                "financiamiento": random.choice(["Difícil","Medio"]), "regeneracion": random.choice(["Medio","Alto"])}
    elif t == "Actor":
        return {"agua": random.choice(["Suficiente","Escasa"]), "entorno": random.choice(["Degradado","En recuperación"]),
                "social": random.choice(["Fuerte","Media"]), "gobernanza": random.choice(["Media","Fuerte"]),
                "financiamiento": random.choice(["Medio","Difícil"]), "regeneracion": random.choice(["Medio","Alto"])}
    return {"agua": random.choice(["Escasa","Suficiente"]), "entorno": random.choice(["En recuperación","Degradado"]),
            "social": random.choice(["Media","Fuerte"]), "gobernanza": random.choice(["Débil","Media"]),
            "financiamiento": random.choice(["Medio","Difícil"]), "regeneracion": random.choice(["Alto","Medio"])}

def _enl(t):
    e = {}
    if random.random() > 0.5: e["youtube"] = f"https://youtube.com/watch?v=demo{random.randint(100,999)}"
    if random.random() > 0.6: e["fotos"] = [f"https://ejemplo.cl/foto{random.randint(1,50)}.jpg"]
    if t == "Actor" and random.random() > 0.4: e["perfil"] = f"https://ejemplo.cl/actor{random.randint(1,15)}"
    return e

def _make(i, cuenca, sub, subsub, lat, lon, comuna, prec):
    _id = 9000 + i; fecha = (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
    r = random.random()
    if r < 0.28:
        tipo, tpl = "Conflicto", random.choice(CONF)
        mod = {"actores": tpl["a"], "gravedad": tpl["g"], "duracion": tpl["dur"], "dialogo": tpl["dia"]}
        ti, de = tpl["t"].replace("{z}", subsub[:40]), tpl["d"]
    elif r < 0.58:
        tipo, tpl = "Iniciativa", random.choice(INIC)
        mod = {"tipos": tpl["tipos"], "estado": tpl["est"], "escala": tpl["esc"]}
        ti, de = tpl["t"].replace("{z}", subsub[:40]), tpl["d"]
    elif r < 0.78:
        tipo, tpl = "Oportunidad", random.choice(OPOR)
        mod = {"viabilidad": tpl["v"], "urgencia": tpl["u"], "brechas": tpl["b"]}
        ti, de = tpl["t"].replace("{z}", subsub[:40]), tpl["d"]
    else:
        tipo = "Actor"; a = random.choice(ACTORES)
        mod = {"nombre": a, "tipo": random.choice(["Org formal","Junta de vecinos","Grupo informal","Institución pública","Empresa"])}
        ti = f"{a} en {subsub[:30]}"; de = f"Actor territorial activo en {subsub}, cuenca {cuenca}."
    dims = _dims(tipo); enl = _enl(tipo)
    punto = {"id": _id, "lat": round(lat, 6), "lon": round(lon, 6), "cuenca": cuenca, "subcuenca": sub,
             "subsubcuenca": subsub, "comuna_nombre": comuna, "precision_ubicacion": prec, "created_at": fecha}
    obs = {"id": _id, "punto_id": _id, "tipo": tipo, "titulo": ti, "descripcion": de,
           "created_at": fecha, "modulo": mod, "enlaces": enl,
           **{f"dim_{k}": v for k, v in dims.items()}, "dim_importancia_lugar": f"Sector {subsub}, {sub}, {cuenca}."}
    if tipo == "Conflicto": obs.update({"conflicto_actores_involucrados": mod["actores"], "conflicto_gravedad": mod["gravedad"], "conflicto_duracion": mod["duracion"], "conflicto_dialogo": mod["dialogo"]})
    elif tipo == "Iniciativa": obs.update({"iniciativa_tipos": mod["tipos"], "iniciativa_estado": mod["estado"], "iniciativa_escala": mod["escala"]})
    elif tipo == "Actor": obs.update({"actor_nombre": mod["nombre"], "actor_tipo": mod["tipo"]})
    elif tipo == "Oportunidad": obs.update({"oportunidad_viabilidad": mod["viabilidad"], "oportunidad_urgencia": mod["urgencia"], "oportunidad_brechas": mod["brechas"]})
    return punto, obs

def generate_demo_data():
    regs = []; subs = list(MAIPO_SUBS.items())
    for i in range(50):
        sn, sd = subs[i % len(subs)]; ss = random.choice(sd["ss"]); com = random.choice(sd["comunas"])
        lat = sd["c"][0] + random.uniform(-sd["s"], sd["s"]); lon = sd["c"][1] + random.uniform(-sd["s"], sd["s"])
        regs.append(_make(i, "Rio Maipo", sn, ss, lat, lon, com, random.choice(["Exacta","Aproximada","Aproximada"])))
    otras = list(OTRAS.items())
    for i in range(50):
        cn, cd = otras[i % len(otras)]; ss = random.choice(cd["ss"]); com = random.choice(cd["comunas"])
        lat = cd["c"][0] + random.uniform(-cd["s"], cd["s"]); lon = cd["c"][1] + random.uniform(-cd["s"], cd["s"])
        regs.append(_make(50+i, cn, cd.get("sub", cn), ss, lat, lon, com, random.choice(["Exacta","Aproximada","Aproximada"])))
    return {"puntos": [r[0] for r in regs], "observaciones": [r[1] for r in regs]}
