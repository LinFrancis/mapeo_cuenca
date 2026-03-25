"""
geo_utils.py — v2.0. Cuenca detection, choropleth data, weather from Open-Meteo.
"""
import streamlit as st
from pathlib import Path
from config import CUENCAS_SHP, SUBCUENCAS_SHP, SUBSUBCUENCAS_SHP

@st.cache_resource(show_spinner="Cargando geometrías de cuencas (DGA)...")
def load_shapefiles():
    import geopandas as gpd
    result = {}
    for key, path in [("cuencas", CUENCAS_SHP), ("subcuencas", SUBCUENCAS_SHP), ("subsubcuencas", SUBSUBCUENCAS_SHP)]:
        if Path(path).exists():
            try:
                gdf = gpd.read_file(path)
                if gdf.crs and gdf.crs.to_epsg() != 4326: gdf = gdf.to_crs(epsg=4326)
                result[key] = gdf
            except Exception as e: print(f"Error {key}: {e}")
        else: result[key] = None
    return result

def _find_name_col(gdf):
    for c in ["NOM_CUEN", "NOM_CUENCA", "NOMBRE", "nombre", "Name", "NAME", "NOM_SUBE", "NOM_SUBC", "NOM_SUB", "NOM_SUBSU", "NOM_DGA"]:
        if c in gdf.columns: return c
    for c in gdf.columns:
        if c != "geometry" and gdf[c].dtype == object: return c
    return None

def identify_cuenca(lat, lon):
    from shapely.geometry import Point
    point = Point(lon, lat)
    result = {"cuenca": "No identificada", "subcuenca": "No identificada", "subsubcuenca": "No identificada"}
    shps = load_shapefiles()
    for level, key in [("cuenca", "cuencas"), ("subcuenca", "subcuencas"), ("subsubcuenca", "subsubcuencas")]:
        gdf = shps.get(key)
        if gdf is None: continue
        try:
            matches = gdf[gdf.geometry.contains(point)]
            if len(matches) > 0:
                col = _find_name_col(gdf)
                if col: result[level] = str(matches.iloc[0][col]).strip()
        except: pass
    return result

def get_geojson_simplified(level="cuencas"):
    shps = load_shapefiles()
    gdf = shps.get(level)
    if gdf is None: return None
    try:
        s = gdf.copy()
        s["geometry"] = s.geometry.simplify(0.01, preserve_topology=True)
        col = _find_name_col(s)
        if col: s["_name"] = s[col].astype(str)
        else: s["_name"] = "N/A"
        return s
    except: return None

def build_choropleth_data(level, obs_list, puntos_list):
    """Builds a dict mapping polygon name → record count for choropleth coloring."""
    pm = {p["id"]: p for p in puntos_list}
    field = {"cuencas": "cuenca", "subcuencas": "subcuenca", "subsubcuencas": "subsubcuenca"}.get(level, "cuenca")
    counts = {}
    for o in obs_list:
        p = pm.get(o.get("punto_id"))
        if p:
            name = p.get(field, "N/A")
            if name and name != "N/A": counts[name] = counts.get(name, 0) + 1
    return counts

@st.cache_data(ttl=3600, show_spinner="Consultando datos meteorológicos...")
def fetch_weather(lat, lon):
    """Fetch last 12 months of weather from Open-Meteo (free, no API key)."""
    import requests
    from datetime import datetime, timedelta
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    try:
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=America/Santiago"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json().get("daily", {})
            return {"dates": data.get("time", []), "temp_max": data.get("temperature_2m_max", []),
                    "temp_min": data.get("temperature_2m_min", []), "precip": data.get("precipitation_sum", [])}
    except: pass
    return None
