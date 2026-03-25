"""
config.py — Configuración centralizada
"""

import os
import streamlit as st
from pathlib import Path

# ============================================
# SUPABASE
# ============================================
def get_supabase_credentials():
    url, key = "", ""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except (KeyError, FileNotFoundError, AttributeError):
        pass
    if not url:
        url = os.getenv("SUPABASE_URL", "")
    if not key:
        key = os.getenv("SUPABASE_ANON_KEY", os.getenv("SUPABASE_KEY", ""))
    return url, key

SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()

# ============================================
# RUTAS
# ============================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CUENCAS_SHP = DATA_DIR / "Cuencas_BNA" / "Cuencas_BNA.shp"
SUBCUENCAS_SHP = DATA_DIR / "Subcuencas_BNA" / "Subcuencas_BNA.shp"
SUBSUBCUENCAS_SHP = DATA_DIR / "SubsubcuencasBNA" / "Subsubcuencas_BNA.shp"

MAP_CENTER = [-35.6751, -71.5430]
MAP_ZOOM = 5

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

INICIATIVA_TIPOS = [
    "Restauración de ribera", "Plantación/reforestación", "Protección de acuífero",
    "Gestión participativa", "Infraestructura hídrica", "Monitoreo ambiental",
    "Educación/conciencia", "Otro",
]
INICIATIVA_ESTADO = ["Idea", "En marcha", "Consolidado"]
INICIATIVA_ESCALA = ["Local", "Subcuenca", "Cuenca"]

ACTOR_TIPO = ["Org formal", "Junta de vecinos", "Grupo informal", "Institución pública", "Empresa", "Otro"]

OPORTUNIDAD_VIABILIDAD = ["Bajo", "Medio", "Alto"]
OPORTUNIDAD_URGENCIA = ["Bajo", "Medio", "Alto"]
OPORTUNIDAD_BRECHAS = [
    "Financiamiento", "Coordinación", "Información", "Capacidades técnicas",
    "Apoyo institucional", "Marco legal", "Conciencia social", "Infraestructura",
]

COLORS = {"Conflicto": "#EF4444", "Iniciativa": "#22C55E", "Actor": "#3B82F6", "Oportunidad": "#F59E0B"}
EMOJIS = {"Conflicto": "🔴", "Iniciativa": "🟢", "Actor": "🔵", "Oportunidad": "🟡"}
FOLIUM_COLORS = {"Conflicto": "red", "Iniciativa": "green", "Actor": "blue", "Oportunidad": "orange"}
FOLIUM_ICONS = {"Conflicto": "exclamation-triangle", "Iniciativa": "leaf", "Actor": "users", "Oportunidad": "star"}

# ============================================
# TEXTOS EDUCATIVOS
# ============================================
INTRO_APP = """
### ¿Qué es esta plataforma?

**Inteligencia Territorial** es una herramienta de mapeo participativo diseñada
para que comunidades, organizaciones y actores territoriales registren lo que
ocurre en las **cuencas hidrográficas de Chile**.

Cada registro se ubica geográficamente y se clasifica en una de cuatro
categorías, y se enriquece con **dimensiones transversales** que permiten
construir un diagnóstico multidimensional del territorio.
"""

INTRO_CUENCA = """
**¿Qué es una cuenca hidrográfica?**
Es el territorio delimitado por las cumbres donde toda el agua escurre hacia
un mismo río o lago. Chile tiene más de 100 cuencas principales según el BNA.
Al hacer clic en el mapa, la plataforma identifica automáticamente cuenca,
subcuenca y subsubcuenca.
"""

INTRO_DIMENSIONES = """
Las **dimensiones transversales** son 6 ejes que caracterizan el territorio:

- **💧 Agua**: Disponibilidad hídrica percibida en la zona
- **🌿 Entorno**: Estado del ecosistema natural circundante
- **👥 Social**: Fuerza del tejido social y comunitario
- **🏛️ Gobernanza**: Calidad de la gestión institucional del territorio
- **💰 Financiamiento**: Acceso a recursos económicos para acciones territoriales
- **♻️ Regeneración**: Potencial de recuperación ecológica y social
"""

TIPOS_EXPLICACION = {
    "Conflicto": {
        "emoji": "🔴",
        "titulo": "Conflicto Socioambiental",
        "desc_corta": "Situaciones de tensión, daño o disputa que afectan al territorio o sus comunidades.",
        "desc_larga": """
Un **conflicto** registra situaciones donde existen tensiones, daños ambientales
o disputas entre actores del territorio. Pueden ser por uso del agua, contaminación,
expansión urbana, extracción de recursos, entre otros.

**Campos específicos:**
- **Actores involucrados**: Quiénes están en disputa (ej: "Empresa minera vs comunidad agrícola")
- **Gravedad**: De Bajo a Crítico — indica el nivel de daño actual o potencial
- **Duración**: Desde Reciente hasta Crónico — cuánto tiempo lleva activo
- **Estado del diálogo**: De Nulo a Alto — si hay comunicación entre las partes

**¿Cuándo registrar un conflicto?** Cuando identificas una situación de daño
ambiental, disputa por recursos naturales, contaminación, o tensión entre actores
del territorio que afecta la calidad de vida o el ecosistema.
""",
    },
    "Iniciativa": {
        "emoji": "🟢",
        "titulo": "Iniciativa Territorial",
        "desc_corta": "Acciones positivas de restauración, gestión del agua o cuidado del territorio.",
        "desc_larga": """
Una **iniciativa** registra acciones concretas que buscan mejorar el territorio:
restauración ecológica, gestión del agua, monitoreo ambiental, educación, etc.

**Campos específicos:**
- **Tipos de iniciativa**: Categorías como restauración de ribera, monitoreo, gestión participativa
- **Estado**: Idea (propuesta), En marcha (ejecutándose), Consolidado (funcionando establemente)
- **Escala**: Local, Subcuenca o Cuenca — el alcance territorial de la iniciativa

**¿Cuándo registrar una iniciativa?** Cuando conoces una acción positiva en el
territorio: un proyecto comunitario, un programa público, una acción colectiva
que busca mejorar las condiciones ambientales o sociales.
""",
    },
    "Actor": {
        "emoji": "🔵",
        "titulo": "Actor Territorial",
        "desc_corta": "Personas, organizaciones o instituciones relevantes en la gobernanza del territorio.",
        "desc_larga": """
Un **actor** registra a las organizaciones, instituciones o grupos que tienen
un rol relevante en el territorio — ya sea positivo, negativo o neutro.

**Campos específicos:**
- **Nombre**: Identificación del actor u organización
- **Tipo**: Org formal, junta de vecinos, grupo informal, institución pública, empresa, otro

**¿Cuándo registrar un actor?** Cuando identificas una organización o grupo que
tiene influencia en las decisiones territoriales, la gestión del agua, o las
dinámicas sociales de la cuenca. Mapear los actores permite entender las redes
de poder y colaboración del territorio.
""",
    },
    "Oportunidad": {
        "emoji": "🟡",
        "titulo": "Oportunidad de Acción",
        "desc_corta": "Ventanas de acción, financiamiento o articulación para mejorar el territorio.",
        "desc_larga": """
Una **oportunidad** registra situaciones favorables para actuar: fondos disponibles,
ventanas políticas, alianzas posibles, proyectos potenciales.

**Campos específicos:**
- **Viabilidad**: Bajo, Medio, Alto — qué tan factible es aprovechar esta oportunidad
- **Urgencia**: Bajo, Medio, Alto — cuánto tiempo queda antes de que se cierre la ventana
- **Brechas**: Qué obstáculos hay que superar (financiamiento, coordinación, información, etc.)

**¿Cuándo registrar una oportunidad?** Cuando detectas una posibilidad concreta
de acción: un fondo concursable, una alianza posible, un cambio normativo favorable,
un proyecto que podría replicarse.
""",
    },
}

# ============================================
# VALIDACIONES
# ============================================
MAX_TITULO = 150
MAX_DESCRIPCION = 500
MAX_IMPORTANCIA = 300

def validate_email(email):
    import re
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def validate_password(pw):
    if len(pw) < 6: return False, "Mínimo 6 caracteres"
    if len(pw) > 128: return False, "Máximo 128 caracteres"
    return True, ""

def validate_nombre(n):
    if not n or not n.strip(): return False, "No puede estar vacío"
    if len(n) > 100: return False, "Máximo 100 caracteres"
    return True, ""
