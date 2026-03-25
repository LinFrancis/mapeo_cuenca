"""
demo_data.py — 100 casos ficticios. 50% en cuenca del Maipo.
"""
import random
from datetime import datetime, timedelta

random.seed(42)

MAIPO_SUBS = {
    "Río Maipo Alto": {"center": [-33.60, -70.10], "s": 0.08, "ss": ["Volcán", "San José de Maipo", "El Yeso"]},
    "Río Mapocho":    {"center": [-33.42, -70.63], "s": 0.06, "ss": ["Lo Barnechea", "Vitacura", "Providencia"]},
    "Río Clarillo":   {"center": [-33.72, -70.48], "s": 0.05, "ss": ["Pirque", "Reserva Clarillo"]},
    "Río Angostura":  {"center": [-33.85, -70.72], "s": 0.06, "ss": ["Paine", "Buin", "Linderos"]},
    "Río Maipo Bajo": {"center": [-33.65, -71.20], "s": 0.08, "ss": ["Melipilla", "Pomaire", "San Pedro"]},
}

OTRAS = {
    "Río Rapel":     {"center": [-34.20, -71.30], "s": 0.15, "sub": "Río Cachapoal", "ss": ["Rancagua", "Machalí", "Requínoa"]},
    "Río Maule":     {"center": [-35.40, -71.50], "s": 0.20, "sub": "Río Claro", "ss": ["Talca", "San Clemente", "Yerbas Buenas"]},
    "Río Biobío":    {"center": [-37.00, -72.50], "s": 0.20, "sub": "Río Laja", "ss": ["Los Ángeles", "Nacimiento", "Santa Bárbara"]},
    "Río Aconcagua": {"center": [-32.85, -70.80], "s": 0.12, "sub": "Río Putaendo", "ss": ["San Felipe", "Los Andes", "Putaendo"]},
    "Río Elqui":     {"center": [-29.95, -71.00], "s": 0.15, "sub": "Río Turbio", "ss": ["Vicuña", "Paihuano", "La Serena"]},
}

ACTORES = [
    "Junta de Vigilancia Río Maipo", "Comité APR La Obra", "ONG Río Vivo",
    "Aguas Andinas S.A.", "Municipalidad San José de Maipo", "Comunidad Ecológica Peñalolén",
    "Colectivo Agua que has de Beber", "DGA Región Metropolitana", "Fundación Chile Sustentable",
    "U. de Chile - Depto Geología", "Cooperativa Campesina Melipilla",
    "Minera Los Bronces (Anglo American)", "Consejo Regional CORE RM",
    "Red de Monitoras Ambientales del Maipo", "Escuela Rural El Manzano",
]

CONFLICTOS = [
    {"t": "Contaminación de relaves en estero {z}", "d": "Relaves mineros filtran metales pesados al estero, afectando agua de riego. Comunidades reportan problemas de salud y pérdida de cultivos.", "a": "Minera vs comunidad agrícola y APR", "g": "Crítico", "dur": "Años", "dia": "Bajo"},
    {"t": "Escasez hídrica en sector {z}", "d": "Pozos secos hace 3 temporadas. Sobreexplotación del acuífero por agroexportadoras deja sin agua a familias. Camiones aljibe como única fuente.", "a": "Agroindustria vs habitantes rurales", "g": "Alto", "dur": "Años", "dia": "Nulo"},
    {"t": "Vertido ilegal de aguas servidas en río {z}", "d": "Planta de tratamiento colapsada vierte al río. Olor y espuma visible. Vecinos denunciaron a la SMA sin respuesta efectiva.", "a": "Empresa sanitaria vs vecinos ribereños", "g": "Alto", "dur": "Meses", "dia": "Bajo"},
    {"t": "Extracción de áridos destruye ribera en {z}", "d": "Extracción masiva sin permisos en cauce del río. Erosión acelerada amenaza caminos y propiedades. Fiscalización inexistente.", "a": "Empresa constructora vs municipio y vecinos", "g": "Medio", "dur": "Meses", "dia": "Medio"},
    {"t": "Disputa por derechos de agua en {z}", "d": "Gran fundo desvía 80% del caudal. Comunidad local sin acceso al agua para consumo humano ni riego de subsistencia.", "a": "Fundo agrícola vs comunidad local", "g": "Crítico", "dur": "Crónico", "dia": "Bajo"},
    {"t": "Expansión urbana sobre humedal en {z}", "d": "Proyecto inmobiliario aprobado sobre humedal que es hábitat de aves migratorias. Organizaciones presentaron recurso de protección.", "a": "Inmobiliaria vs organizaciones ambientales", "g": "Medio", "dur": "Reciente", "dia": "Medio"},
]

INICIATIVAS_TPL = [
    {"t": "Restauración de ribera en {z}", "d": "Proyecto comunitario de plantación de especies nativas (quillay, peumo, boldo) en 2km de ribera degradada. 150 voluntarios.", "tipos": ["Restauración de ribera", "Plantación/reforestación"], "est": "En marcha", "esc": "Local"},
    {"t": "Monitoreo ciudadano de agua en {z}", "d": "Red de 20 puntos de monitoreo con vecinos capacitados. Miden pH, conductividad, oxígeno disuelto y coliformes mensualmente.", "tipos": ["Monitoreo ambiental", "Educación/conciencia"], "est": "Consolidado", "esc": "Subcuenca"},
    {"t": "Mesa de gobernanza hídrica en {z}", "d": "Espacio multiactor: APRs, municipio, DGA, agricultores y sociedad civil gestionan el agua de la subcuenca de forma participativa.", "tipos": ["Gestión participativa"], "est": "En marcha", "esc": "Subcuenca"},
    {"t": "Cosecha de aguas lluvia en {z}", "d": "Sistemas de cosecha de lluvia en 45 viviendas rurales. Capacitación a familias. Reduce dependencia de camiones aljibe un 60%.", "tipos": ["Infraestructura hídrica", "Educación/conciencia"], "est": "Consolidado", "esc": "Local"},
    {"t": "Escuela del agua para niños en {z}", "d": "Programa educativo en 5 escuelas rurales sobre ciclo del agua y cuencas. Incluye salidas a terreno y huertos escolares.", "tipos": ["Educación/conciencia"], "est": "En marcha", "esc": "Local"},
    {"t": "Protección comunitaria de acuífero en {z}", "d": "Comunidad logró declaratoria de zona de restricción para nuevas extracciones. Monitorean niveles freáticos con apoyo universitario.", "tipos": ["Protección de acuífero", "Monitoreo ambiental"], "est": "Consolidado", "esc": "Cuenca"},
]

OPORTUNIDADES_TPL = [
    {"t": "Fondo FPA para restauración en {z}", "d": "Convocatoria abierta del Fondo de Protección Ambiental. Hasta $20M por proyecto. Cierre en 60 días.", "v": "Alto", "u": "Alto", "b": ["Financiamiento", "Capacidades técnicas"]},
    {"t": "Alianza universidad-comunidad en {z}", "d": "Depto de ingeniería ambiental ofrece asistencia técnica gratuita para red de monitoreo de calidad de agua.", "v": "Alto", "u": "Medio", "b": ["Coordinación", "Información"]},
    {"t": "Plan regulador en revisión en {z}", "d": "Municipio abrió proceso de actualización. Ventana para incluir fajas de protección de riberas y humedales.", "v": "Medio", "u": "Alto", "b": ["Apoyo institucional", "Marco legal"]},
    {"t": "Programa INDAP de riego eficiente en {z}", "d": "Subsidio de reconversión de riego tendido a goteo. Cubre 70% de inversión. Requiere organización colectiva.", "v": "Alto", "u": "Medio", "b": ["Financiamiento", "Coordinación"]},
]

def _dims(tipo):
    if tipo == "Conflicto":
        return {"agua": random.choice(["Muy escasa", "Escasa", "Escasa"]),
                "entorno": random.choice(["Muy degradado", "Degradado", "Degradado"]),
                "social": random.choice(["Débil", "Media", "Muy débil"]),
                "gobernanza": random.choice(["Muy débil", "Débil", "Débil"]),
                "financiamiento": random.choice(["Muy difícil", "Difícil"]),
                "regeneracion": random.choice(["Bajo", "Bajo", "Medio"])}
    elif tipo == "Iniciativa":
        return {"agua": random.choice(["Escasa", "Suficiente"]),
                "entorno": random.choice(["En recuperación", "Degradado", "En recuperación"]),
                "social": random.choice(["Media", "Fuerte", "Media"]),
                "gobernanza": random.choice(["Media", "Débil", "Media"]),
                "financiamiento": random.choice(["Difícil", "Medio"]),
                "regeneracion": random.choice(["Medio", "Alto", "Medio"])}
    elif tipo == "Actor":
        return {"agua": random.choice(["Suficiente", "Escasa"]),
                "entorno": random.choice(["Degradado", "En recuperación", "Conservado"]),
                "social": random.choice(["Fuerte", "Media"]),
                "gobernanza": random.choice(["Media", "Fuerte"]),
                "financiamiento": random.choice(["Medio", "Difícil"]),
                "regeneracion": random.choice(["Medio", "Alto"])}
    else:
        return {"agua": random.choice(["Escasa", "Suficiente"]),
                "entorno": random.choice(["En recuperación", "Degradado"]),
                "social": random.choice(["Media", "Fuerte"]),
                "gobernanza": random.choice(["Débil", "Media"]),
                "financiamiento": random.choice(["Medio", "Difícil"]),
                "regeneracion": random.choice(["Alto", "Medio"])}

def _make(i, cuenca, sub, subsub, lat, lon):
    _id = 9000 + i
    fecha = (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat()
    r = random.random()
    if r < 0.28:
        tipo = "Conflicto"
        tpl = random.choice(CONFLICTOS)
        mod = {"actores": tpl["a"], "gravedad": tpl["g"], "duracion": tpl["dur"], "dialogo": tpl["dia"]}
        titulo, desc = tpl["t"].replace("{z}", subsub), tpl["d"]
    elif r < 0.58:
        tipo = "Iniciativa"
        tpl = random.choice(INICIATIVAS_TPL)
        mod = {"tipos": tpl["tipos"], "estado": tpl["est"], "escala": tpl["esc"]}
        titulo, desc = tpl["t"].replace("{z}", subsub), tpl["d"]
    elif r < 0.78:
        tipo = "Oportunidad"
        tpl = random.choice(OPORTUNIDADES_TPL)
        mod = {"viabilidad": tpl["v"], "urgencia": tpl["u"], "brechas": tpl["b"]}
        titulo, desc = tpl["t"].replace("{z}", subsub), tpl["d"]
    else:
        tipo = "Actor"
        a = random.choice(ACTORES)
        mod = {"nombre": a, "tipo": random.choice(["Org formal", "Junta de vecinos", "Grupo informal", "Institución pública", "Empresa"])}
        titulo = f"{a} — presencia en {subsub}"
        desc = f"Actor territorial activo en {subsub}, cuenca {cuenca}. Participa en gestión del agua y coordinación con otras organizaciones."

    dims = _dims(tipo)
    punto = {"id": _id, "lat": round(lat, 6), "lon": round(lon, 6),
             "cuenca": cuenca, "subcuenca": sub, "subsubcuenca": subsub, "created_at": fecha}
    obs = {"id": _id, "punto_id": _id, "tipo": tipo, "titulo": titulo, "descripcion": desc,
           "created_at": fecha, "modulo": mod,
           **{f"dim_{k}": v for k, v in dims.items()},
           "dim_importancia_lugar": f"Sector {subsub}, subcuenca {sub}, cuenca {cuenca}."}
    if tipo == "Conflicto":
        obs.update({"conflicto_actores_involucrados": mod["actores"], "conflicto_gravedad": mod["gravedad"],
                    "conflicto_duracion": mod["duracion"], "conflicto_dialogo": mod["dialogo"]})
    elif tipo == "Iniciativa":
        obs.update({"iniciativa_tipos": mod["tipos"], "iniciativa_estado": mod["estado"], "iniciativa_escala": mod["escala"]})
    elif tipo == "Actor":
        obs.update({"actor_nombre": mod["nombre"], "actor_tipo": mod["tipo"]})
    elif tipo == "Oportunidad":
        obs.update({"oportunidad_viabilidad": mod["viabilidad"], "oportunidad_urgencia": mod["urgencia"],
                    "oportunidad_brechas": mod["brechas"]})
    return punto, obs

def generate_demo_data():
    registros = []
    subs = list(MAIPO_SUBS.items())
    for i in range(50):
        sn, sd = subs[i % len(subs)]
        ss = random.choice(sd["ss"])
        lat = sd["center"][0] + random.uniform(-sd["s"], sd["s"])
        lon = sd["center"][1] + random.uniform(-sd["s"], sd["s"])
        registros.append(_make(i, "Río Maipo", sn, ss, lat, lon))
    otras = list(OTRAS.items())
    for i in range(50):
        cn, cd = otras[i % len(otras)]
        ss = random.choice(cd["ss"])
        lat = cd["center"][0] + random.uniform(-cd["s"], cd["s"])
        lon = cd["center"][1] + random.uniform(-cd["s"], cd["s"])
        registros.append(_make(50 + i, cn, cd.get("sub", cn), ss, lat, lon))
    return {"puntos": [r[0] for r in registros], "observaciones": [r[1] for r in registros]}
