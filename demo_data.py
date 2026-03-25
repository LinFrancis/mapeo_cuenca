"""
demo_data.py — Generador de datos de demostración
100 casos ficticios con relaciones cruzadas para análisis profundo.
50% concentrado en la cuenca del río Maipo.
"""

import random
import hashlib
from datetime import datetime, timedelta

random.seed(42)  # Reproducibilidad

# ============================================
# CUENCAS Y COORDENADAS
# ============================================

# Cuenca del Maipo — 50 puntos (variados dentro de la cuenca)
MAIPO_SUBCUENCAS = {
    "Río Maipo Alto": {"center": [-33.60, -70.10], "spread": 0.08,
                       "subsub": ["Volcán", "San José de Maipo", "El Yeso"]},
    "Río Mapocho":    {"center": [-33.42, -70.63], "spread": 0.06,
                       "subsub": ["Lo Barnechea", "Vitacura", "Providencia"]},
    "Río Clarillo":   {"center": [-33.72, -70.48], "spread": 0.05,
                       "subsub": ["Pirque", "Reserva Clarillo"]},
    "Río Angostura":  {"center": [-33.85, -70.72], "spread": 0.06,
                       "subsub": ["Paine", "Buin", "Linderos"]},
    "Río Maipo Bajo": {"center": [-33.65, -71.20], "spread": 0.08,
                       "subsub": ["Melipilla", "Pomaire", "San Pedro"]},
}

# Otras cuencas — 50 puntos distribuidos
OTRAS_CUENCAS = {
    "Río Rapel":       {"center": [-34.20, -71.30], "spread": 0.15,
                        "sub": "Río Cachapoal", "subsub": ["Rancagua", "Machalí", "Requínoa"]},
    "Río Maule":       {"center": [-35.40, -71.50], "spread": 0.20,
                        "sub": "Río Claro", "subsub": ["Talca", "San Clemente", "Yerbas Buenas"]},
    "Río Biobío":      {"center": [-37.00, -72.50], "spread": 0.20,
                        "sub": "Río Laja", "subsub": ["Los Ángeles", "Nacimiento", "Santa Bárbara"]},
    "Río Aconcagua":   {"center": [-32.85, -70.80], "spread": 0.12,
                        "sub": "Río Putaendo", "subsub": ["San Felipe", "Los Andes", "Putaendo"]},
    "Río Elqui":       {"center": [-29.95, -71.00], "spread": 0.15,
                        "sub": "Río Turbio", "subsub": ["Vicuña", "Paihuano", "La Serena"]},
}

# ============================================
# ACTORES FICTICIOS (redes de relaciones)
# ============================================

ACTORES_RED = [
    {"nombre": "Junta de Vigilancia Río Maipo", "tipo": "Org formal", "influencia": "Alto"},
    {"nombre": "Comité APR La Obra", "tipo": "Junta de vecinos", "influencia": "Medio"},
    {"nombre": "ONG Río Vivo", "tipo": "Org formal", "influencia": "Alto"},
    {"nombre": "Aguas Andinas S.A.", "tipo": "Empresa", "influencia": "Alto"},
    {"nombre": "Municipalidad San José de Maipo", "tipo": "Institución pública", "influencia": "Alto"},
    {"nombre": "Comunidad Ecológica Peñalolén", "tipo": "Grupo informal", "influencia": "Medio"},
    {"nombre": "Colectivo Agua que has de Beber", "tipo": "Grupo informal", "influencia": "Medio"},
    {"nombre": "DGA Región Metropolitana", "tipo": "Institución pública", "influencia": "Alto"},
    {"nombre": "Fundación Chile Sustentable", "tipo": "Org formal", "influencia": "Medio"},
    {"nombre": "Universidad de Chile - Depto Geología", "tipo": "Org formal", "influencia": "Medio"},
    {"nombre": "Cooperativa Campesina Melipilla", "tipo": "Org formal", "influencia": "Bajo"},
    {"nombre": "Minera Los Bronces (Anglo American)", "tipo": "Empresa", "influencia": "Alto"},
    {"nombre": "Consejo Regional CORE RM", "tipo": "Institución pública", "influencia": "Medio"},
    {"nombre": "Red de Monitoras Ambientales del Maipo", "tipo": "Grupo informal", "influencia": "Medio"},
    {"nombre": "Escuela Rural El Manzano", "tipo": "Otro", "influencia": "Bajo"},
]

# ============================================
# TEMPLATES DE REGISTROS
# ============================================

CONFLICTOS = [
    {"titulo": "Contaminación de relaves en estero {subsub}",
     "desc": "Relaves mineros históricos filtran metales pesados al estero, afectando agua de riego de pequeños agricultores. Comunidades reportan problemas de salud.",
     "actores": "Minera vs comunidad agrícola y APR",
     "gravedad": "Crítico", "duracion": "Años", "dialogo": "Bajo"},
    {"titulo": "Escasez hídrica en sector {subsub}",
     "desc": "Pozos secos desde hace 3 temporadas. La sobreexplotación del acuífero por agroexportadoras deja sin agua a las familias. Camiones aljibe como única fuente.",
     "actores": "Agroindustria vs habitantes rurales",
     "gravedad": "Alto", "duracion": "Años", "dialogo": "Nulo"},
    {"titulo": "Vertido ilegal de aguas servidas en río {subsub}",
     "desc": "Planta de tratamiento colapsada vierte directamente al río. Olor y espuma visible. Vecinos han denunciado a la SMA sin respuesta.",
     "actores": "Empresa sanitaria vs vecinos ribereños",
     "gravedad": "Alto", "duracion": "Meses", "dialogo": "Bajo"},
    {"titulo": "Extracción de áridos destruye ribera en {subsub}",
     "desc": "Extracción masiva de áridos sin permisos en cauce del río. Erosión acelerada amenaza caminos y propiedades aledañas. Fiscalización inexistente.",
     "actores": "Empresa constructora vs municipio y vecinos",
     "gravedad": "Medio", "duracion": "Meses", "dialogo": "Medio"},
    {"titulo": "Conflicto por derechos de agua en {subsub}",
     "desc": "Disputa legal entre gran fundo y comunidad indígena por derechos de aprovechamiento. El fundo desvía el 80% del caudal disponible.",
     "actores": "Fundo agrícola vs comunidad local",
     "gravedad": "Crítico", "duracion": "Crónico", "dialogo": "Bajo"},
    {"titulo": "Expansión urbana sobre humedal en {subsub}",
     "desc": "Proyecto inmobiliario aprobado sobre humedal urbano que es hábitat de aves migratorias. Organizaciones ambientales presentaron recurso de protección.",
     "actores": "Inmobiliaria vs organizaciones ambientales",
     "gravedad": "Medio", "duracion": "Reciente", "dialogo": "Medio"},
]

INICIATIVAS = [
    {"titulo": "Restauración de ribera en {subsub}",
     "desc": "Proyecto comunitario de plantación de especies nativas (quillay, peumo, boldo) en 2km de ribera degradada. 150 voluntarios en 6 jornadas.",
     "tipos": ["Restauración de ribera", "Plantación/reforestación"],
     "estado": "En marcha", "escala": "Local"},
    {"titulo": "Monitoreo ciudadano de calidad de agua en {subsub}",
     "desc": "Red de 20 puntos de monitoreo operados por vecinos capacitados. Miden pH, conductividad, oxígeno disuelto y coliformes mensualmente.",
     "tipos": ["Monitoreo ambiental", "Educación/conciencia"],
     "estado": "Consolidado", "escala": "Subcuenca"},
    {"titulo": "Mesa de gobernanza hídrica participativa",
     "desc": "Espacio multiactor donde se reúnen APRs, municipio, DGA, agricultores y sociedad civil para gestionar el agua de la subcuenca.",
     "tipos": ["Gestión participativa"],
     "estado": "En marcha", "escala": "Subcuenca"},
    {"titulo": "Cosecha de aguas lluvia en {subsub}",
     "desc": "Instalación de sistemas de cosecha de lluvia en 45 viviendas rurales. Capacitación a familias en mantención y uso. Reduce dependencia de camiones aljibe.",
     "tipos": ["Infraestructura hídrica", "Educación/conciencia"],
     "estado": "Consolidado", "escala": "Local"},
    {"titulo": "Escuela del agua para niños en {subsub}",
     "desc": "Programa educativo en 5 escuelas rurales sobre ciclo del agua, cuencas y cuidado del recurso. Incluye salidas a terreno y huertos escolares.",
     "tipos": ["Educación/conciencia"],
     "estado": "En marcha", "escala": "Local"},
    {"titulo": "Protección comunitaria de acuífero en {subsub}",
     "desc": "Comunidad organizada logró declaratoria de zona de restricción para nuevas extracciones. Monitorean niveles freáticos con apoyo universitario.",
     "tipos": ["Protección de acuífero", "Monitoreo ambiental"],
     "estado": "Consolidado", "escala": "Cuenca"},
]

OPORTUNIDADES = [
    {"titulo": "Fondo FPA disponible para restauración en {subsub}",
     "desc": "Convocatoria abierta del Fondo de Protección Ambiental para proyectos de restauración ecológica. Hasta $20M por proyecto. Cierre en 60 días.",
     "viabilidad": "Alto", "urgencia": "Alto", "brechas": ["Financiamiento", "Capacidades técnicas"]},
    {"titulo": "Alianza universidad-comunidad para monitoreo en {subsub}",
     "desc": "Departamento de ingeniería ambiental ofrece asistencia técnica gratuita para implementar red de monitoreo de calidad de agua.",
     "viabilidad": "Alto", "urgencia": "Medio", "brechas": ["Coordinación", "Información"]},
    {"titulo": "Plan regulador en revisión permite proteger riberas en {subsub}",
     "desc": "Municipio abrió proceso de actualización del plan regulador. Es la ventana para incluir fajas de protección de riberas y humedales.",
     "viabilidad": "Medio", "urgencia": "Alto", "brechas": ["Apoyo institucional", "Marco legal"]},
    {"titulo": "Programa INDAP de riego eficiente en {subsub}",
     "desc": "Subsidio de reconversión de riego tendido a goteo para pequeños agricultores. Cubre 70% de la inversión. Requiere organización colectiva.",
     "viabilidad": "Alto", "urgencia": "Medio", "brechas": ["Financiamiento", "Coordinación"]},
]

# ============================================
# DIMENSIONES PONDERADAS (no aleatorias — cuentan una historia)
# ============================================

def dims_for_tipo(tipo, cuenca):
    """Genera dimensiones coherentes según tipo y cuenca."""
    is_maipo = cuenca == "Río Maipo"

    if tipo == "Conflicto":
        # Conflictos en zonas más degradadas
        return {
            "agua": random.choice(["Muy escasa", "Escasa", "Escasa"]),
            "entorno": random.choice(["Muy degradado", "Degradado", "Degradado"]),
            "social": random.choice(["Débil", "Media", "Muy débil"]),
            "gobernanza": random.choice(["Muy débil", "Débil", "Débil"]),
            "financiamiento": random.choice(["Muy difícil", "Difícil"]),
            "regeneracion": random.choice(["Bajo", "Bajo", "Medio"]),
        }
    elif tipo == "Iniciativa":
        # Iniciativas en zonas con algo de organización
        return {
            "agua": random.choice(["Escasa", "Suficiente", "Escasa"]),
            "entorno": random.choice(["En recuperación", "Degradado", "En recuperación"]),
            "social": random.choice(["Media", "Fuerte", "Media"]),
            "gobernanza": random.choice(["Media", "Débil", "Media"]),
            "financiamiento": random.choice(["Difícil", "Medio", "Difícil"]),
            "regeneracion": random.choice(["Medio", "Alto", "Medio"]),
        }
    elif tipo == "Actor":
        return {
            "agua": random.choice(["Suficiente", "Escasa", "Suficiente"]),
            "entorno": random.choice(["Degradado", "En recuperación", "Conservado"]),
            "social": random.choice(["Fuerte", "Media", "Fuerte"]),
            "gobernanza": random.choice(["Media", "Fuerte", "Media"]),
            "financiamiento": random.choice(["Medio", "Difícil", "Medio"]),
            "regeneracion": random.choice(["Medio", "Alto"]),
        }
    else:  # Oportunidad
        return {
            "agua": random.choice(["Escasa", "Suficiente"]),
            "entorno": random.choice(["En recuperación", "Degradado"]),
            "social": random.choice(["Media", "Fuerte"]),
            "gobernanza": random.choice(["Débil", "Media"]),
            "financiamiento": random.choice(["Medio", "Difícil"]),
            "regeneracion": random.choice(["Alto", "Medio", "Alto"]),
        }


# ============================================
# GENERAR LOS 100 CASOS
# ============================================

def generate_demo_data():
    """
    Genera 100 registros ficticios con estructura completa.
    Retorna dict con 'puntos' y 'observaciones' listos para inyectar.
    """
    registros = []  # (punto_dict, obs_dict)
    _id_counter = 9000  # IDs ficticios que no chocan con los reales

    # ---- 50 CASOS EN CUENCA DEL MAIPO ----
    maipo_subs = list(MAIPO_SUBCUENCAS.items())

    for i in range(50):
        sub_name, sub_data = maipo_subs[i % len(maipo_subs)]
        subsub = random.choice(sub_data["subsub"])

        lat = sub_data["center"][0] + random.uniform(-sub_data["spread"], sub_data["spread"])
        lon = sub_data["center"][1] + random.uniform(-sub_data["spread"], sub_data["spread"])

        # Distribuir tipos: ~30% conflicto, ~30% iniciativa, ~20% oportunidad, ~20% actor
        r = random.random()
        if r < 0.30:
            tipo = "Conflicto"
            tpl = random.choice(CONFLICTOS)
            modulo = {
                "actores": tpl["actores"],
                "gravedad": tpl["gravedad"],
                "duracion": tpl["duracion"],
                "dialogo": tpl["dialogo"],
            }
        elif r < 0.60:
            tipo = "Iniciativa"
            tpl = random.choice(INICIATIVAS)
            modulo = {"tipos": tpl["tipos"], "estado": tpl["estado"], "escala": tpl["escala"]}
        elif r < 0.80:
            tipo = "Oportunidad"
            tpl = random.choice(OPORTUNIDADES)
            modulo = {"viabilidad": tpl["viabilidad"], "urgencia": tpl["urgencia"],
                      "brechas": tpl["brechas"]}
        else:
            tipo = "Actor"
            actor = random.choice(ACTORES_RED)
            tpl = {"titulo": f"{actor['nombre']} — presencia en {subsub}",
                   "desc": f"Actor territorial activo en la zona de {subsub}. "
                           f"Tipo: {actor['tipo']}. Nivel de influencia: {actor['influencia']}."}
            modulo = {"nombre": actor["nombre"], "tipo": actor["tipo"]}

        dims = dims_for_tipo(tipo, "Río Maipo")
        fecha = datetime.now() - timedelta(days=random.randint(1, 365))

        _id_counter += 1
        punto = {
            "id": _id_counter,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "cuenca": "Río Maipo",
            "subcuenca": sub_name,
            "subsubcuenca": subsub,
            "created_at": fecha.isoformat(),
        }
        obs = {
            "id": _id_counter,
            "punto_id": _id_counter,
            "tipo": tipo,
            "titulo": tpl["titulo"].replace("{subsub}", subsub),
            "descripcion": tpl["desc"].replace("{subsub}", subsub),
            "created_at": fecha.isoformat(),
            "modulo": modulo,
            **{f"dim_{k}": v for k, v in dims.items()},
            "dim_importancia_lugar": f"Zona clave en la subcuenca {sub_name}, sector {subsub}.",
        }
        # Agregar campos del módulo al obs directamente
        if tipo == "Conflicto":
            obs["conflicto_actores_involucrados"] = modulo.get("actores", "")
            obs["conflicto_gravedad"] = modulo.get("gravedad")
            obs["conflicto_duracion"] = modulo.get("duracion")
            obs["conflicto_dialogo"] = modulo.get("dialogo")
        elif tipo == "Iniciativa":
            obs["iniciativa_tipos"] = modulo.get("tipos", [])
            obs["iniciativa_estado"] = modulo.get("estado")
            obs["iniciativa_escala"] = modulo.get("escala")
        elif tipo == "Actor":
            obs["actor_nombre"] = modulo.get("nombre")
            obs["actor_tipo"] = modulo.get("tipo")
        elif tipo == "Oportunidad":
            obs["oportunidad_viabilidad"] = modulo.get("viabilidad")
            obs["oportunidad_urgencia"] = modulo.get("urgencia")
            obs["oportunidad_brechas"] = modulo.get("brechas", [])

        registros.append((punto, obs))

    # ---- 50 CASOS EN OTRAS CUENCAS ----
    otras = list(OTRAS_CUENCAS.items())

    for i in range(50):
        cuenca_name, cuenca_data = otras[i % len(otras)]
        subsub = random.choice(cuenca_data["subsub"])

        lat = cuenca_data["center"][0] + random.uniform(-cuenca_data["spread"], cuenca_data["spread"])
        lon = cuenca_data["center"][1] + random.uniform(-cuenca_data["spread"], cuenca_data["spread"])

        r = random.random()
        if r < 0.30:
            tipo = "Conflicto"
            tpl = random.choice(CONFLICTOS)
            modulo = {"actores": tpl["actores"], "gravedad": tpl["gravedad"],
                      "duracion": tpl["duracion"], "dialogo": tpl["dialogo"]}
        elif r < 0.60:
            tipo = "Iniciativa"
            tpl = random.choice(INICIATIVAS)
            modulo = {"tipos": tpl["tipos"], "estado": tpl["estado"], "escala": tpl["escala"]}
        elif r < 0.80:
            tipo = "Oportunidad"
            tpl = random.choice(OPORTUNIDADES)
            modulo = {"viabilidad": tpl["viabilidad"], "urgencia": tpl["urgencia"],
                      "brechas": tpl["brechas"]}
        else:
            tipo = "Actor"
            actor = random.choice(ACTORES_RED[:5])
            tpl = {"titulo": f"Presencia de {actor['nombre']} en {subsub}",
                   "desc": f"Actor territorial con actividad en {subsub}, cuenca {cuenca_name}."}
            modulo = {"nombre": actor["nombre"], "tipo": actor["tipo"]}

        dims = dims_for_tipo(tipo, cuenca_name)
        fecha = datetime.now() - timedelta(days=random.randint(1, 365))

        _id_counter += 1
        punto = {
            "id": _id_counter,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "cuenca": cuenca_name,
            "subcuenca": cuenca_data.get("sub", cuenca_name),
            "subsubcuenca": subsub,
            "created_at": fecha.isoformat(),
        }
        obs = {
            "id": _id_counter,
            "punto_id": _id_counter,
            "tipo": tipo,
            "titulo": tpl["titulo"].replace("{subsub}", subsub),
            "descripcion": tpl["desc"].replace("{subsub}", subsub),
            "created_at": fecha.isoformat(),
            "modulo": modulo,
            **{f"dim_{k}": v for k, v in dims.items()},
            "dim_importancia_lugar": f"Sector {subsub} en cuenca {cuenca_name}.",
        }
        if tipo == "Conflicto":
            obs["conflicto_actores_involucrados"] = modulo.get("actores", "")
            obs["conflicto_gravedad"] = modulo.get("gravedad")
            obs["conflicto_duracion"] = modulo.get("duracion")
            obs["conflicto_dialogo"] = modulo.get("dialogo")
        elif tipo == "Iniciativa":
            obs["iniciativa_tipos"] = modulo.get("tipos", [])
            obs["iniciativa_estado"] = modulo.get("estado")
            obs["iniciativa_escala"] = modulo.get("escala")
        elif tipo == "Actor":
            obs["actor_nombre"] = modulo.get("nombre")
            obs["actor_tipo"] = modulo.get("tipo")
        elif tipo == "Oportunidad":
            obs["oportunidad_viabilidad"] = modulo.get("viabilidad")
            obs["oportunidad_urgencia"] = modulo.get("urgencia")
            obs["oportunidad_brechas"] = modulo.get("brechas", [])

        registros.append((punto, obs))

    puntos = [r[0] for r in registros]
    observaciones = [r[1] for r in registros]

    return {"puntos": puntos, "observaciones": observaciones}
