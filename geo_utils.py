"""
geo_utils.py — v2.0 fixed.
BNA shapefiles: NOM_CUEN (cuencas), NOM_SUBC (subcuencas), NOM_SSUBC (subsubcuencas).
"""
import streamlit as st
from pathlib import Path
from config import CUENCAS_SHP, SUBCUENCAS_SHP, SUBSUBCUENCAS_SHP

NAME_COLS = {"cuencas": "NOM_CUEN", "subcuencas": "NOM_SUBC", "subsubcuencas": "NOM_SSUBC"}

@st.cache_resource(show_spinner="Cargando geometrías de cuencas (DGA)...")
def load_shapefiles():
    import geopandas as gpd
    result = {}
    for key, path in [("cuencas", CUENCAS_SHP), ("subcuencas", SUBCUENCAS_SHP), ("subsubcuencas", SUBSUBCUENCAS_SHP)]:
        if Path(path).exists():
            try:
                gdf = gpd.read_file(str(path))
                if gdf.crs and gdf.crs.to_epsg() != 4326: gdf = gdf.to_crs(epsg=4326)
                result[key] = gdf
            except Exception as e: print(f"Error {key}: {e}"); result[key] = None
        else: result[key] = None
    return result

def identify_cuenca(lat, lon):
    from shapely.geometry import Point
    point = Point(lon, lat)
    r = {"cuenca": "No identificada", "subcuenca": "No identificada", "subsubcuenca": "No identificada"}
    shps = load_shapefiles()
    for level, key in [("cuenca", "cuencas"), ("subcuenca", "subcuencas"), ("subsubcuenca", "subsubcuencas")]:
        gdf = shps.get(key)
        if gdf is None: continue
        try:
            m = gdf[gdf.geometry.contains(point)]
            if len(m) > 0:
                col = NAME_COLS.get(key)
                if col and col in m.columns: r[level] = str(m.iloc[0][col]).strip()
        except: pass
    return r

def get_geojson_simplified(level="cuencas"):
    shps = load_shapefiles()
    gdf = shps.get(level)
    if gdf is None: return None
    try:
        s = gdf.copy()
        s["geometry"] = s.geometry.simplify(0.01, preserve_topology=True)
        col = NAME_COLS.get(level)
        if col and col in s.columns: s["_name"] = s[col].astype(str).str.strip()
        else: s["_name"] = "N/A"
        return s
    except: return None

def build_choropleth_data(level, obs_list, puntos_list):
    pm = {p["id"]: p for p in puntos_list}
    field = {"cuencas": "cuenca", "subcuencas": "subcuenca", "subsubcuencas": "subsubcuenca"}.get(level, "cuenca")
    counts = {}
    for o in obs_list:
        p = pm.get(o.get("punto_id"))
        if p:
            n = p.get(field, "N/A")
            if n and n != "N/A": counts[n] = counts.get(n, 0) + 1
    return counts

@st.cache_data(ttl=3600, show_spinner="Datos meteorológicos...")
def fetch_weather(lat, lon):
    import requests
    from datetime import datetime, timedelta
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    try:
        r = requests.get(f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=America/Santiago", timeout=10)
        if r.status_code == 200:
            d = r.json().get("daily", {})
            return {"dates": d.get("time", []), "temp_max": d.get("temperature_2m_max", []),
                    "temp_min": d.get("temperature_2m_min", []), "precip": d.get("precipitation_sum", [])}
    except: pass
    return None
