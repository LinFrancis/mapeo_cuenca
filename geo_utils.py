"""
geo_utils.py — Utilidades geoespaciales
Detección automática de cuenca/subcuenca/subsubcuenca a partir de coordenadas.
Usa shapefiles BNA incluidos en data/.
"""

import streamlit as st
from pathlib import Path
from config import CUENCAS_SHP, SUBCUENCAS_SHP, SUBSUBCUENCAS_SHP


@st.cache_resource(show_spinner="Cargando geometrías de cuencas...")
def load_shapefiles():
    """
    Carga los tres niveles de shapefiles y retorna los GeoDataFrames.
    Se cachea para toda la sesión del servidor.
    """
    import geopandas as gpd

    result = {"cuencas": None, "subcuencas": None, "subsubcuencas": None}

    for key, path in [
        ("cuencas", CUENCAS_SHP),
        ("subcuencas", SUBCUENCAS_SHP),
        ("subsubcuencas", SUBSUBCUENCAS_SHP),
    ]:
        if Path(path).exists():
            try:
                gdf = gpd.read_file(path)
                if gdf.crs and gdf.crs.to_epsg() != 4326:
                    gdf = gdf.to_crs(epsg=4326)
                result[key] = gdf
            except Exception as e:
                print(f"Error cargando {key}: {e}")

    return result


def identify_cuenca(lat: float, lon: float) -> dict:
    """
    Dado un punto (lat, lon), identifica en qué cuenca, subcuenca y
    subsubcuenca cae.

    Returns:
        dict con keys: cuenca, subcuenca, subsubcuenca
              (cada una es el nombre o "No identificada")
    """
    from shapely.geometry import Point

    point = Point(lon, lat)  # shapely usa (x=lon, y=lat)
    result = {
        "cuenca": "No identificada",
        "subcuenca": "No identificada",
        "subsubcuenca": "No identificada",
    }

    shps = load_shapefiles()

    # Buscar nombre de columna probable para el nombre de la cuenca
    name_cols = ["NOM_CUEN", "NOM_CUENCA", "NOMBRE", "nombre", "Name", "NAME",
                 "NOM_SUBE", "NOM_SUBC", "NOM_SUB", "NOM_SUBSU", "NOM_DGA"]

    for level, gdf_key in [("cuenca", "cuencas"), ("subcuenca", "subcuencas"),
                            ("subsubcuenca", "subsubcuencas")]:
        gdf = shps.get(gdf_key)
        if gdf is None:
            continue

        try:
            # Buscar qué polígono contiene el punto
            mask = gdf.geometry.contains(point)
            matches = gdf[mask]

            if len(matches) > 0:
                row = matches.iloc[0]
                # Intentar encontrar la columna con el nombre
                found = False
                for col in name_cols:
                    if col in row.index and row[col]:
                        result[level] = str(row[col]).strip()
                        found = True
                        break
                if not found:
                    # Usar la primera columna de texto que no sea geometry
                    for col in row.index:
                        if col != "geometry" and isinstance(row[col], str) and row[col].strip():
                            result[level] = row[col].strip()
                            break
        except Exception as e:
            print(f"Error en {level}: {e}")

    return result


def get_cuencas_geojson():
    """Retorna GeoJSON simplificado de cuencas para overlay en mapa."""
    shps = load_shapefiles()
    gdf = shps.get("cuencas")
    if gdf is None:
        return None
    try:
        # Simplificar geometría para rendimiento
        simplified = gdf.copy()
        simplified["geometry"] = simplified.geometry.simplify(0.01, preserve_topology=True)
        return simplified
    except Exception:
        return None
