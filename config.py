"""
config.py — Configuración centralizada para Inteligencia Territorial
Soporta tanto st.secrets (Streamlit Cloud) como variables de entorno (local).
"""

import os
import streamlit as st
from pathlib import Path

# ============================================
# SUPABASE — lectura de credenciales
# ============================================
def get_supabase_credentials() -> tuple[str, str]:
    """
    Intenta leer credenciales en este orden:
      1. st.secrets["supabase"]["url"] / ["key"]   (Streamlit Cloud)
      2. Variables de entorno SUPABASE_URL / SUPABASE_ANON_KEY (local / .env)
    """
    url, key = "", ""

    # 1) Streamlit secrets (Cloud o local .streamlit/secrets.toml)
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except (KeyError, FileNotFoundError, AttributeError):
        pass

    # 2) Fallback a variables de entorno
    if not url:
        url = os.getenv("SUPABASE_URL", "")
    if not key:
        key = os.getenv("SUPABASE_ANON_KEY", os.getenv("SUPABASE_KEY", ""))

    return url, key


SUPABASE_URL, SUPABASE_KEY = get_supabase_credentials()

# ============================================
# RUTAS DE DATOS (shapefiles BNA)
# ============================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

CUENCAS_SHP = DATA_DIR / "Cuencas_BNA" / "Cuencas_BNA.shp"
SUBCUENCAS_SHP = DATA_DIR / "Subcuencas_BNA" / "Subcuencas_BNA.shp"
SUBSUBCUENCAS_SHP = DATA_DIR / "SubsubcuencasBNA" / "Subsubcuencas_BNA.shp"

# ============================================
# MAPA — centro en Chile
# ============================================
MAP_CENTER = [-35.6751, -71.5430]
MAP_ZOOM = 5

# ============================================
# CATÁLOGOS DEL FORMULARIO
# ============================================

TIPOS_ACTOR = [
    "Sociedad Civil",
    "Público",
    "Privado",
    "Academia",
    "Otro",
]

TIPOS_REGISTRO = ["Conflicto", "Iniciativa", "Actor", "Oportunidad"]

# Dimensiones transversales
DIM_AGUA = ["Muy escasa", "Escasa", "Suficiente", "Abundante", "NS/NR"]
DIM_ENTORNO = ["Muy degradado", "Degradado", "En recuperación", "Conservado", "NS/NR"]
DIM_SOCIAL = ["Muy débil", "Débil", "Media", "Fuerte", "NS/NR"]
DIM_GOBERNANZA = ["Muy débil", "Débil", "Media", "Fuerte", "NS/NR"]
DIM_FINANCIAMIENTO = ["Muy difícil", "Difícil", "Medio", "Fácil", "NS/NR"]
DIM_REGENERACION = ["Bajo", "Medio", "Alto", "NS/NR"]

# Módulo Conflicto
CONFLICTO_GRAVEDAD = ["Bajo", "Medio", "Alto", "Crítico"]
CONFLICTO_DURACION = ["Reciente", "Meses", "Años", "Crónico"]
CONFLICTO_DIALOGO = ["Nulo", "Bajo", "Medio", "Alto"]

# Módulo Iniciativa
INICIATIVA_TIPOS = [
    "Restauración de ribera",
    "Plantación/reforestación",
    "Protección de acuífero",
    "Gestión participativa",
    "Infraestructura hídrica",
    "Monitoreo ambiental",
    "Educación/conciencia",
    "Otro",
]
INICIATIVA_ESTADO = ["Idea", "En marcha", "Consolidado"]
INICIATIVA_ESCALA = ["Local", "Subcuenca", "Cuenca"]

# Módulo Actor
ACTOR_TIPO = [
    "Org formal",
    "Junta de vecinos",
    "Grupo informal",
    "Institución pública",
    "Empresa",
    "Otro",
]

# Módulo Oportunidad
OPORTUNIDAD_VIABILIDAD = ["Bajo", "Medio", "Alto"]
OPORTUNIDAD_URGENCIA = ["Bajo", "Medio", "Alto"]
OPORTUNIDAD_BRECHAS = [
    "Financiamiento",
    "Coordinación",
    "Información",
    "Capacidades técnicas",
    "Apoyo institucional",
    "Marco legal",
    "Conciencia social",
    "Infraestructura",
]

# ============================================
# COLORES Y EMOJIS POR TIPO
# ============================================
COLORS = {
    "Conflicto": "#EF4444",
    "Iniciativa": "#22C55E",
    "Actor": "#3B82F6",
    "Oportunidad": "#F59E0B",
}

EMOJIS = {
    "Conflicto": "🔴",
    "Iniciativa": "🟢",
    "Actor": "🔵",
    "Oportunidad": "🟡",
}

FOLIUM_COLORS = {
    "Conflicto": "red",
    "Iniciativa": "green",
    "Actor": "blue",
    "Oportunidad": "orange",
}

FOLIUM_ICONS = {
    "Conflicto": "exclamation-triangle",
    "Iniciativa": "leaf",
    "Actor": "users",
    "Oportunidad": "star",
}

# ============================================
# TEXTOS EDUCATIVOS
# ============================================
INTRO_APP = """
### ¿Qué es esta plataforma?

**Inteligencia Territorial** es una herramienta de mapeo participativo diseñada
para que comunidades, organizaciones y actores territoriales registren lo que
ocurre en las **cuencas hidrográficas de Chile**.

Cada registro se ubica geográficamente y se clasifica en una de cuatro
categorías: **conflictos** socioambientales, **iniciativas** de restauración o
gestión, **actores** territoriales relevantes, y **oportunidades** de acción.

Además, cada registro incluye **dimensiones transversales** (agua, entorno,
tejido social, gobernanza, financiamiento y potencial de regeneración) que
permiten construir un diagnóstico multidimensional del territorio.
"""

INTRO_CUENCA = """
**¿Qué es una cuenca hidrográfica?**

Es el territorio delimitado por las cumbres de cerros y montañas donde toda el
agua de lluvia escurre hacia un mismo río o lago. Chile tiene más de 100 cuencas
principales según el Banco Nacional de Aguas (BNA). Cada cuenca se subdivide en
subcuencas y subsubcuencas.

Al hacer clic en el mapa, la plataforma identifica automáticamente en qué
cuenca, subcuenca y subsubcuenca se encuentra el punto seleccionado.
"""

INTRO_DIMENSIONES = """
Las **dimensiones transversales** son 6 ejes que permiten caracterizar la
situación del territorio donde ocurre el registro:

- **💧 Agua**: Disponibilidad hídrica percibida
- **🌿 Entorno**: Estado del ecosistema natural
- **👥 Social**: Fuerza del tejido social y comunitario
- **🏛️ Gobernanza**: Calidad de la gestión institucional
- **💰 Financiamiento**: Acceso a recursos económicos
- **♻️ Regeneración**: Potencial de recuperación del territorio
"""

# ============================================
# VALIDACIONES
# ============================================
MAX_TITULO = 150
MAX_DESCRIPCION = 500
MAX_IMPORTANCIA = 300

def validate_email(email: str) -> bool:
    import re
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def validate_password(pw: str) -> tuple[bool, str]:
    if len(pw) < 6:
        return False, "Mínimo 6 caracteres"
    if len(pw) > 128:
        return False, "Máximo 128 caracteres"
    return True, ""

def validate_nombre(n: str) -> tuple[bool, str]:
    if not n or not n.strip():
        return False, "No puede estar vacío"
    if len(n) > 100:
        return False, "Máximo 100 caracteres"
    return True, ""
