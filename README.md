# 🌊 Inteligencia Territorial

Plataforma de **mapeo territorial participativo** para cuencas hidrográficas de Chile.

## Características

- **Mapeo participativo** con detección automática de cuenca/subcuenca
- **4 tipos de registro**: Conflicto, Iniciativa, Actor, Oportunidad
- **6 dimensiones transversales**: Agua, entorno, social, gobernanza, financiamiento, regeneración
- **Dashboard analítico**: Radar, heatmap por cuenca, gráficos de distribución
- **Análisis de red**: Co-ocurrencia, red de actores, balance conflicto→respuesta, brechas
- **Modo demostración**: 100 registros ficticios (50% cuenca del Maipo) para explorar sin cuenta
- **Contenido educativo**: Explicaciones de cada módulo, metodología de indicadores

## Deploy rápido

### 1. Supabase
- Crea proyecto en [supabase.com](https://supabase.com)
- Ejecuta `SCHEMA_SUPABASE_COMPLETO.sql` en SQL Editor
- **Ejecuta `FIX_SIGNUP.sql`** en SQL Editor (crea trigger para signup automático)
- En Authentication → Settings → Email: desactiva "Confirm email" (para desarrollo)

### 2. Streamlit Cloud
- Sube repo a GitHub
- En App Settings → Secrets:
```toml
[supabase]
url = "https://TU-PROYECTO.supabase.co"
key = "sb_publishable_TU_KEY"
```

## Archivos

| Archivo | Descripción |
|---|---|
| `app.py` | Aplicación principal |
| `config.py` | Configuración, catálogos, textos educativos |
| `supabase_client.py` | Cliente Supabase (auth con trigger, CRUD) |
| `geo_utils.py` | Detección de cuenca con shapefiles |
| `demo_data.py` | Generador de 100 casos ficticios |
| `FIX_SIGNUP.sql` | **Ejecutar en Supabase** — trigger + policies |
| `packages.txt` | Deps del sistema para Streamlit Cloud |

---

[livlin.cl](https://livlin.cl) — servicios profesionales para una vida regenerativa
