"""
config.py — Mapeo Participativo de Cuencas v2.0
"""
import os, streamlit as st
from pathlib import Path

# ============================================
# SUPABASE
# ============================================
def _creds():
    u, k = "", ""
    try: u = st.secrets["supabase"]["url"]; k = st.secrets["supabase"]["key"]
    except: pass
    if not u: u = os.getenv("SUPABASE_URL", "")
    if not k: k = os.getenv("SUPABASE_ANON_KEY", os.getenv("SUPABASE_KEY", ""))
    return u, k

SUPABASE_URL, SUPABASE_KEY = _creds()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CUENCAS_SHP = DATA_DIR / "Cuencas_BNA" / "Cuencas_BNA.shp"
SUBCUENCAS_SHP = DATA_DIR / "Subcuencas_BNA" / "Subcuencas_BNA.shp"
SUBSUBCUENCAS_SHP = DATA_DIR / "SubsubcuencasBNA" / "Subsubcuencas_BNA.shp"

MAP_CENTER = [-33.45, -70.65]  # Santiago como default
MAP_ZOOM = 6
APP_NAME = "Mapeo Participativo de Cuencas"
APP_VERSION = "2.0"

# ============================================
# CATÁLOGOS
# ============================================
TIPOS_ACTOR = ["Sociedad Civil", "Público", "Privado", "Academia", "Otro"]
TIPOS_REGISTRO = ["Conflicto", "Iniciativa", "Actor", "Oportunidad"]
DIM_AGUA = ["Muy escasa", "Escasa", "Suficiente", "Abundante", "NS/NR"]
DIM_ENTORNO = ["Muy degradado", "Degradado", "En recuperación", "Conservado", "NS/NR"]
DIM_SOCIAL = ["Muy débil", "Débil", "Media", "Fuerte", "NS/NR"]
DIM_GOBERNANZA = ["Muy débil", "Débil", "Media", "Fuerte", "NS/NR"]
DIM_FINANCIAMIENTO = ["Muy difícil", "Difícil", "Medio", "Fácil", "NS/NR"]
DIM_REGENERACION = ["Bajo", "Medio", "Alto", "NS/NR"]
CONFLICTO_GRAVEDAD = ["Bajo", "Medio", "Alto", "Crítico"]
CONFLICTO_DURACION = ["Reciente", "Meses", "Años", "Crónico"]
CONFLICTO_DIALOGO = ["Nulo", "Bajo", "Medio", "Alto"]
INICIATIVA_TIPOS = ["Restauración de ribera", "Plantación/reforestación", "Protección de acuífero", "Gestión participativa", "Infraestructura hídrica", "Monitoreo ambiental", "Educación/conciencia", "Otro"]
INICIATIVA_ESTADO = ["Idea", "En marcha", "Consolidado"]
INICIATIVA_ESCALA = ["Local", "Subcuenca", "Cuenca"]
ACTOR_TIPO = ["Org formal", "Junta de vecinos", "Grupo informal", "Institución pública", "Empresa", "Otro"]
OPORTUNIDAD_VIABILIDAD = ["Bajo", "Medio", "Alto"]
OPORTUNIDAD_URGENCIA = ["Bajo", "Medio", "Alto"]
OPORTUNIDAD_BRECHAS = ["Financiamiento", "Coordinación", "Información", "Capacidades técnicas", "Apoyo institucional", "Marco legal", "Conciencia social", "Infraestructura"]
METODOS_UBICACION = ["📍 Clic en el mapa", "🏘️ Buscar por comuna", "📐 Coordenadas exactas"]

COLORS = {"Conflicto": "#EF4444", "Iniciativa": "#22C55E", "Actor": "#3B82F6", "Oportunidad": "#F59E0B"}
EMOJIS = {"Conflicto": "🔴", "Iniciativa": "🟢", "Actor": "🔵", "Oportunidad": "🟡"}
FOLIUM_COLORS = {"Conflicto": "red", "Iniciativa": "green", "Actor": "blue", "Oportunidad": "orange"}
FOLIUM_ICONS = {"Conflicto": "exclamation-triangle", "Iniciativa": "leaf", "Actor": "users", "Oportunidad": "star"}

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
# COMUNAS → CUENCAS (principales)
# ============================================
COMUNAS_CUENCAS = {
    # Región Metropolitana → Río Maipo
    "Santiago": {"lat": -33.45, "lon": -70.65, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto", "Rio Maipo Alto"]},
    "Providencia": {"lat": -33.42, "lon": -70.61, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto"]},
    "Las Condes": {"lat": -33.41, "lon": -70.57, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto"]},
    "Lo Barnechea": {"lat": -33.35, "lon": -70.51, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto"]},
    "Vitacura": {"lat": -33.39, "lon": -70.58, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto"]},
    "Ñuñoa": {"lat": -33.46, "lon": -70.60, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto"]},
    "La Reina": {"lat": -33.44, "lon": -70.54, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto"]},
    "Peñalolén": {"lat": -33.49, "lon": -70.53, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto"]},
    "La Florida": {"lat": -33.52, "lon": -70.59, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto", "Rio Maipo Alto"]},
    "Puente Alto": {"lat": -33.61, "lon": -70.57, "cuenca": "Rio Maipo", "subcuencas": ["Rio Maipo Alto"]},
    "San José de Maipo": {"lat": -33.64, "lon": -70.35, "cuenca": "Rio Maipo", "subcuencas": ["Rio Maipo Alto"]},
    "Pirque": {"lat": -33.67, "lon": -70.50, "cuenca": "Rio Maipo", "subcuencas": ["Rio Maipo Medio"]},
    "San Bernardo": {"lat": -33.59, "lon": -70.70, "cuenca": "Rio Maipo", "subcuencas": ["Rio Maipo Bajo (Entre Rio Mapocho y Desembocadura)"]},
    "Buin": {"lat": -33.73, "lon": -70.74, "cuenca": "Rio Maipo", "subcuencas": ["Rio Maipo Medio"]},
    "Paine": {"lat": -33.81, "lon": -70.74, "cuenca": "Rio Maipo", "subcuencas": ["Rio Maipo Medio"]},
    "Melipilla": {"lat": -33.70, "lon": -71.21, "cuenca": "Rio Maipo", "subcuencas": ["Rio Maipo Bajo (Entre Rio Mapocho y Desembocadura)"]},
    "Talagante": {"lat": -33.66, "lon": -70.93, "cuenca": "Rio Maipo", "subcuencas": ["Rio Maipo Bajo (Entre Rio Mapocho y Desembocadura)"]},
    "Maipú": {"lat": -33.51, "lon": -70.76, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto", "Rio Maipo Bajo (Entre Rio Mapocho y Desembocadura)"]},
    "Colina": {"lat": -33.20, "lon": -70.67, "cuenca": "Rio Maipo", "subcuencas": ["R.  Mapocho Alto"]},
    # Valparaíso → Río Aconcagua
    "Los Andes": {"lat": -32.83, "lon": -70.60, "cuenca": "Rio Aconcagua", "subcuencas": ["Aconcagua Alto", "Aconcagua Alto"]},
    "San Felipe": {"lat": -32.75, "lon": -70.73, "cuenca": "Rio Aconcagua", "subcuencas": ["Aconcagua Alto", "Rio Aconcagua"]},
    "Quillota": {"lat": -32.88, "lon": -71.25, "cuenca": "Rio Aconcagua", "subcuencas": ["Aconcagua Bajo"]},
    # O'Higgins → Río Rapel
    "Rancagua": {"lat": -34.17, "lon": -70.74, "cuenca": "Rio Rapel", "subcuencas": ["Rio Cachapoal Alto (Hasta bajo junta Rio Claro)"]},
    "Machalí": {"lat": -34.18, "lon": -70.65, "cuenca": "Rio Rapel", "subcuencas": ["Rio Cachapoal Alto (Hasta bajo junta Rio Claro)"]},
    "Requínoa": {"lat": -34.30, "lon": -70.82, "cuenca": "Rio Rapel", "subcuencas": ["Rio Cachapoal Alto (Hasta bajo junta Rio Claro)"]},
    "San Fernando": {"lat": -34.58, "lon": -71.00, "cuenca": "Rio Rapel", "subcuencas": ["Tinguiririca Bajo"]},
    # Maule → Río Maule
    "Talca": {"lat": -35.43, "lon": -71.66, "cuenca": "Rio Maule", "subcuencas": ["Rio Claro", "Rio Maule"]},
    "Curicó": {"lat": -34.98, "lon": -71.24, "cuenca": "Rio Maule", "subcuencas": ["Rio Claro", "Rio Claro"]},
    "Linares": {"lat": -35.85, "lon": -71.60, "cuenca": "Rio Maule", "subcuencas": ["Rio Maule entre Rio Loncomilla y Rio Claro"]},
    # Biobío
    "Los Ángeles": {"lat": -37.47, "lon": -72.35, "cuenca": "Rio Bio-Bio", "subcuencas": ["Laja Bajo", "Rio Bio-Bio"]},
    "Concepción": {"lat": -36.83, "lon": -73.05, "cuenca": "Rio Bio-Bio", "subcuencas": ["Rio Bio-Bio Bajo"]},
    "Chillán": {"lat": -36.63, "lon": -72.10, "cuenca": "Rio Itata", "subcuencas": ["Rio Itata"]},
    # Coquimbo
    "La Serena": {"lat": -29.90, "lon": -71.25, "cuenca": "Rio Elqui", "subcuencas": ["Rio Elqui"]},
    "Vicuña": {"lat": -30.03, "lon": -70.71, "cuenca": "Rio Elqui", "subcuencas": ["Rio Elqui"]},
    "Ovalle": {"lat": -30.60, "lon": -71.20, "cuenca": "Rio Limari", "subcuencas": ["Rio Limari"]},
    # Araucanía
    "Temuco": {"lat": -38.74, "lon": -72.60, "cuenca": "Rio Imperial", "subcuencas": ["Rio Cautin"]},
    # Los Ríos
    "Valdivia": {"lat": -39.81, "lon": -73.24, "cuenca": "Rio Valdivia", "subcuencas": ["Rio Calle-Calle"]},
}

# ============================================
# TEXTOS
# ============================================
INTRO_APP = f"""
### {APP_NAME}

Herramienta de **inteligencia territorial** que permite a comunidades, organizaciones
y actores territoriales registrar lo que ocurre en las cuencas hidrográficas de Chile.

La delimitación de cuencas proviene de la **Dirección General de Aguas (DGA)** del
Ministerio de Obras Públicas, disponible en su
[Mapoteca Digital](https://dga.mop.gob.cl/administracionrecursoshidricos/mapoteca/Paginas/default.aspx).

Cada registro se organiza territorialmente en tres niveles:
**cuenca → subcuenca → subsubcuenca**, permitiendo análisis desde lo macro hasta
la unidad territorial mínima.
"""

INTRO_CUENCA = """
**¿Qué es una cuenca hidrográfica?**

Es el territorio delimitado por las cumbres donde toda el agua escurre hacia un
mismo río o lago. La DGA define tres niveles jerárquicos:

- **Cuenca**: La unidad mayor (ej: Río Maipo)
- **Subcuenca**: División intermedia (ej: Río Mapocho, Río Clarillo)
- **Subsubcuenca**: La unidad territorial mínima de análisis

Esta jerarquía permite entender la diversidad interna de cada cuenca y analizar
problemas y oportunidades a la escala correcta.
"""

INTRO_DIMENSIONES = """
Las **dimensiones transversales** son 6 ejes que caracterizan el territorio donde
ocurre cada registro. Son evaluaciones cualitativas basadas en la percepción de
quien conoce el lugar:

- **💧 Agua**: Disponibilidad hídrica percibida
- **🌿 Entorno**: Estado del ecosistema natural
- **👥 Social**: Fuerza del tejido social y comunitario
- **🏛️ Gobernanza**: Calidad de la gestión institucional
- **💰 Financiamiento**: Acceso a recursos económicos
- **♻️ Regeneración**: Potencial de recuperación del territorio

Al agregar las respuestas de muchos participantes, emergen patrones que ningún
registro individual podría revelar.
"""

TIPOS_EXPLICACION = {
    "Conflicto": {
        "emoji": "🔴", "titulo": "Conflicto Socioambiental",
        "corta": "Situaciones de tensión, daño o disputa que afectan al territorio.",
        "larga": """Un **conflicto** registra tensiones, daños ambientales o disputas entre actores.
**Campos**: Actores involucrados, gravedad (Bajo→Crítico), duración, estado del diálogo.
**¿Cuándo?** Al identificar contaminación, disputas por agua, expansión urbana sobre ecosistemas, etc.""",
    },
    "Iniciativa": {
        "emoji": "🟢", "titulo": "Iniciativa Territorial",
        "corta": "Acciones positivas de restauración, gestión del agua o cuidado del territorio.",
        "larga": """Una **iniciativa** registra acciones que buscan mejorar el territorio.
**Campos**: Tipos (restauración, monitoreo, etc.), estado (Idea→Consolidado), escala territorial.
**¿Cuándo?** Al conocer proyectos comunitarios, programas públicos, acciones colectivas.""",
    },
    "Actor": {
        "emoji": "🔵", "titulo": "Actor Territorial",
        "corta": "Organizaciones o personas relevantes en la gobernanza del territorio.",
        "larga": """Un **actor** mapea organizaciones, instituciones o grupos con influencia territorial.
**Campos**: Nombre, tipo de organización, enlaces a perfiles y sitios web.
**¿Cuándo?** Al identificar organizaciones clave en la gestión del agua o las dinámicas sociales.""",
    },
    "Oportunidad": {
        "emoji": "🟡", "titulo": "Oportunidad de Acción",
        "corta": "Ventanas de acción, financiamiento o articulación territorial.",
        "larga": """Una **oportunidad** registra situaciones favorables para actuar.
**Campos**: Viabilidad, urgencia, brechas a superar (financiamiento, coordinación, etc.).
**¿Cuándo?** Al detectar fondos disponibles, alianzas posibles, cambios normativos favorables.""",
    },
}

MAX_TITULO = 150
MAX_DESCRIPCION = 500
MAX_IMPORTANCIA = 300

def validate_email(e):
    import re; return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', e) is not None
def validate_password(p):
    if len(p) < 6: return False, "Mínimo 6 caracteres"
    return True, ""
def validate_nombre(n):
    if not n or not n.strip(): return False, "No puede estar vacío"
    return True, ""
