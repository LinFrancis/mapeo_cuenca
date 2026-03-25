# 🌊 Mapeo Participativo de Cuencas v2.0

Herramienta de **inteligencia territorial** para cuencas hidrográficas de Chile. Las cuencas se definen según la [Dirección General de Aguas (DGA)](https://dga.mop.gob.cl/administracionrecursoshidricos/mapoteca/Paginas/default.aspx).

## Novedades v2.0

- **🔍 Explorador de registros** — Buscador con filtros cascada: cuenca → subcuenca → subsubcuenca
- **📍 Tres métodos de ubicación** — Clic en mapa, buscar por comuna, o coordenadas exactas
- **🗺️ Mapas coropléticos** — Cuencas pintadas por densidad de registros (3 niveles)
- **🌡️ Datos meteorológicos** — Temperatura y precipitación del último año (Open-Meteo, gratis)
- **🔗 Enlaces multimedia** — YouTube, fotos, documentos, perfiles de actores
- **📐 Metodología** — Cada gráfico tiene un expander explicando construcción e interpretación
- **🧪 Demo completo** — 100 registros ficticios con formulario navegable

## Deploy

### 1. Supabase
```
1. Crear proyecto en supabase.com
2. SQL Editor → ejecutar SCHEMA_SUPABASE_COMPLETO.sql
3. SQL Editor → ejecutar MIGRATION_V2.sql
4. Authentication → Settings → Email → desactivar "Confirm email"
```

### 2. Streamlit Cloud
```
1. Subir repo a GitHub
2. App Settings → Secrets:
   [supabase]
   url = "https://TU-PROYECTO.supabase.co"
   key = "sb_publishable_TU_KEY"
3. Deploy
```

## Archivos
| Archivo | Descripción |
|---|---|
| `app.py` | App principal v2.0 |
| `config.py` | Config, catálogos, comunas→cuencas, textos |
| `supabase_client.py` | Cliente DB (signup via trigger) |
| `geo_utils.py` | Cuencas, coropléticos, weather |
| `demo_data.py` | 100 casos con enlaces y comunas |
| `MIGRATION_V2.sql` | **Ejecutar en Supabase** |

---
[livlin.cl](https://livlin.cl) — servicios profesionales para una vida regenerativa
