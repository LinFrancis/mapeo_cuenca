# 🌊 Inteligencia Territorial

Plataforma de **mapeo territorial participativo** para cuencas hidrográficas de Chile.

Permite a comunidades, organizaciones y actores territoriales registrar **conflictos**, **iniciativas**, **actores** y **oportunidades** geolocalizados en cuencas, subcuencas y subsubcuencas del país, construyendo un diagnóstico colectivo multidimensional.

## Características

- **Mapeo participativo**: Registro geolocalizado con clic en mapa interactivo
- **Detección automática de cuenca**: Al hacer clic, identifica cuenca/subcuenca/subsubcuenca usando shapefiles BNA
- **4 tipos de registro**: Conflicto, Iniciativa, Actor, Oportunidad — cada uno con campos específicos
- **6 dimensiones transversales**: Agua, entorno, social, gobernanza, financiamiento, regeneración
- **Dashboard analítico**: Gráficos, radar de dimensiones, tabla por cuenca, timeline
- **Mapa global**: Todos los registros con filtros por tipo y cuenca
- **Educativo y autoexplicativo**: Textos contextuales que guían al usuario

## Stack

| Componente | Tecnología |
|---|---|
| Frontend | Streamlit |
| Backend/Auth/DB | Supabase (PostgreSQL + Auth) |
| Mapas | Folium + streamlit-folium |
| Gráficos | Plotly |
| Geodatos | GeoPandas + Shapely |
| Shapefiles | BNA (Banco Nacional de Aguas, Chile) |

## Deploy en Streamlit Cloud

### 1. Repositorio

Sube estos archivos a GitHub:
```
app.py
config.py
supabase_client.py
geo_utils.py
requirements.txt
packages.txt
.streamlit/config.toml
data/
  Cuencas_BNA/
  Subcuencas_BNA/
  SubsubcuencasBNA/
```

### 2. Supabase

- Crea un proyecto en [supabase.com](https://supabase.com)
- Ejecuta `SCHEMA_SUPABASE_COMPLETO.sql` en el SQL Editor
- Copia la URL y la publishable key (o anon key)

### 3. Secrets en Streamlit Cloud

En **App Settings → Secrets**, pega:

```toml
[supabase]
url = "https://TU-PROYECTO.supabase.co"
key = "sb_publishable_TU_KEY"
```

### 4. Deploy

Conecta el repo de GitHub en [share.streamlit.io](https://share.streamlit.io) y despliega.

## Desarrollo Local

```bash
# Clonar
git clone <tu-repo>
cd inteligencia-territorial

# Entorno virtual
python -m venv venv
source venv/bin/activate

# Dependencias
pip install -r requirements.txt

# Secrets locales
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml
# Edita .streamlit/secrets.toml con tus credenciales

# Ejecutar
streamlit run app.py
```

## Estructura de archivos

```
├── app.py                 # Aplicación principal Streamlit
├── config.py              # Configuración, catálogos, textos educativos
├── supabase_client.py     # Cliente Supabase (auth, CRUD, stats)
├── geo_utils.py           # Detección de cuenca con shapefiles
├── requirements.txt       # Dependencias Python
├── packages.txt           # Dependencias del sistema (para Streamlit Cloud)
├── secrets.toml.example   # Template de secrets
├── SCHEMA_SUPABASE_COMPLETO.sql  # Schema de la base de datos
├── .streamlit/
│   └── config.toml        # Tema y configuración de Streamlit
└── data/
    ├── Cuencas_BNA/       # Shapefiles de cuencas
    ├── Subcuencas_BNA/    # Shapefiles de subcuencas
    └── SubsubcuencasBNA/  # Shapefiles de subsubcuencas
```

## Licencia

Proyecto de código abierto para la gobernanza territorial participativa en Chile.
