-- ============================================
-- SCHEMA: Inteligencia Territorial V4
-- Base de datos: PostgreSQL (Supabase)
-- Ejecutar en: SQL Editor de Supabase
-- ============================================

-- ============================================
-- 1. TABLA: users_profiles
-- ============================================
CREATE TABLE public.users_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
  
  -- Datos personales
  nombre TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  
  -- Perfil territorial
  organizacion TEXT,
  rol TEXT,
  tipo_actor TEXT NOT NULL DEFAULT 'Otro' CHECK (
    tipo_actor IN ('Sociedad Civil', 'Público', 'Privado', 'Academia', 'Otro')
  ),
  
  -- Contacto
  telefono TEXT,
  region_interes TEXT,
  
  -- Auditoría
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT nombre_not_empty CHECK (LENGTH(TRIM(nombre)) > 0),
  CONSTRAINT email_not_empty CHECK (LENGTH(TRIM(email)) > 0)
);

-- Índices
CREATE INDEX idx_users_email ON public.users_profiles(email);
CREATE INDEX idx_users_tipo_actor ON public.users_profiles(tipo_actor);

-- Row Level Security
ALTER TABLE public.users_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" 
  ON public.users_profiles 
  FOR SELECT 
  USING (auth_user_id = auth.uid());

CREATE POLICY "Users can update own profile" 
  ON public.users_profiles 
  FOR UPDATE 
  USING (auth_user_id = auth.uid());

CREATE POLICY "New users can insert own profile"
  ON public.users_profiles
  FOR INSERT
  WITH CHECK (auth_user_id = auth.uid());


-- ============================================
-- 2. TABLA: puntos (Ubicaciones geográficas)
-- ============================================
CREATE TABLE public.puntos (
  id BIGSERIAL PRIMARY KEY,
  
  -- Ubicación (WGS84 - EPSG:4326)
  lat DECIMAL(10, 8) NOT NULL,
  lon DECIMAL(11, 8) NOT NULL,
  
  -- Geografía BNA
  cuenca TEXT DEFAULT 'N/A',
  subcuenca TEXT DEFAULT 'N/A',
  subsubcuenca TEXT DEFAULT 'N/A',
  gauge_id TEXT DEFAULT 'N/A',
  
  -- Metadatos
  precision_ubicacion TEXT DEFAULT 'Aproximada' CHECK (
    precision_ubicacion IN ('Exacta', 'Aproximada')
  ),
  comuna_nombre TEXT DEFAULT 'N/A',
  region_nombre TEXT DEFAULT 'N/A',
  
  -- Auditoría
  created_by UUID REFERENCES public.users_profiles(auth_user_id) ON DELETE SET NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  
  -- Geometría (PostGIS)
  geom GEOMETRY(POINT, 4326) GENERATED ALWAYS AS 
    (ST_SetSRID(ST_MakePoint(lon, lat), 4326)) STORED,
  
  CONSTRAINT valid_lat CHECK (lat >= -90 AND lat <= 90),
  CONSTRAINT valid_lon CHECK (lon >= -180 AND lon <= 180)
);

-- Índices
CREATE INDEX idx_puntos_geom ON public.puntos USING GIST(geom);
CREATE INDEX idx_puntos_cuenca ON public.puntos(cuenca);
CREATE INDEX idx_puntos_subcuenca ON public.puntos(subcuenca);
CREATE INDEX idx_puntos_created_by ON public.puntos(created_by);
CREATE INDEX idx_puntos_created_at ON public.puntos(created_at DESC);

-- Row Level Security
ALTER TABLE public.puntos ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view all puntos" 
  ON public.puntos 
  FOR SELECT 
  USING (TRUE);

CREATE POLICY "Authenticated users can create puntos" 
  ON public.puntos 
  FOR INSERT 
  WITH CHECK (auth.uid() IS NOT NULL AND created_by = auth.uid());

CREATE POLICY "Users can update own puntos" 
  ON public.puntos 
  FOR UPDATE 
  USING (created_by = auth.uid());


-- ============================================
-- 3. TABLA: observaciones (Registros territoriales)
-- ============================================
CREATE TABLE public.observaciones (
  id BIGSERIAL PRIMARY KEY,
  
  -- Referencias
  punto_id BIGINT NOT NULL REFERENCES public.puntos(id) ON DELETE CASCADE,
  autor_id UUID NOT NULL REFERENCES public.users_profiles(auth_user_id) ON DELETE SET NULL,
  
  -- Registro principal
  tipo TEXT NOT NULL CHECK (tipo IN ('Conflicto', 'Iniciativa', 'Actor', 'Oportunidad')),
  titulo TEXT NOT NULL,
  descripcion TEXT NOT NULL,
  
  -- ============================================
  -- MÓDULO A: CONFLICTO
  -- ============================================
  conflicto_actores_involucrados TEXT,
  conflicto_gravedad TEXT CHECK (
    conflicto_gravedad IS NULL OR 
    conflicto_gravedad IN ('Bajo', 'Medio', 'Alto', 'Crítico')
  ),
  conflicto_duracion TEXT CHECK (
    conflicto_duracion IS NULL OR 
    conflicto_duracion IN ('Reciente', 'Meses', 'Años', 'Crónico')
  ),
  conflicto_dialogo TEXT CHECK (
    conflicto_dialogo IS NULL OR 
    conflicto_dialogo IN ('Nulo', 'Bajo', 'Medio', 'Alto')
  ),
  
  -- ============================================
  -- MÓDULO B: INICIATIVA
  -- ============================================
  iniciativa_tipos TEXT[],
  iniciativa_estado TEXT CHECK (
    iniciativa_estado IS NULL OR 
    iniciativa_estado IN ('Idea', 'En marcha', 'Consolidado')
  ),
  iniciativa_escala TEXT CHECK (
    iniciativa_escala IS NULL OR 
    iniciativa_escala IN ('Local', 'Subcuenca', 'Cuenca')
  ),
  iniciativa_aporte_naturaleza TEXT CHECK (
    iniciativa_aporte_naturaleza IS NULL OR 
    iniciativa_aporte_naturaleza IN ('Bajo', 'Medio', 'Alto')
  ),
  iniciativa_potencial_replica TEXT CHECK (
    iniciativa_potencial_replica IS NULL OR 
    iniciativa_potencial_replica IN ('Bajo', 'Medio', 'Alto')
  ),
  
  -- ============================================
  -- MÓDULO C: ACTOR / COMUNIDAD
  -- ============================================
  actor_nombre TEXT,
  actor_tipo TEXT CHECK (
    actor_tipo IS NULL OR 
    actor_tipo IN ('Org formal', 'Junta de vecinos', 'Grupo informal', 'Institución pública', 'Empresa', 'Otro')
  ),
  actor_influencia TEXT CHECK (
    actor_influencia IS NULL OR 
    actor_influencia IN ('Bajo', 'Medio', 'Alto')
  ),
  actor_organizacion_interna TEXT CHECK (
    actor_organizacion_interna IS NULL OR 
    actor_organizacion_interna IN ('Débil', 'Medio', 'Fuerte')
  ),
  actor_colaboracion TEXT CHECK (
    actor_colaboracion IS NULL OR 
    actor_colaboracion IN ('Bajo', 'Medio', 'Alto')
  ),
  
  -- ============================================
  -- MÓDULO D: OPORTUNIDAD
  -- ============================================
  oportunidad_responde_conflicto BIGINT REFERENCES public.observaciones(id) ON DELETE SET NULL,
  oportunidad_viabilidad TEXT CHECK (
    oportunidad_viabilidad IS NULL OR 
    oportunidad_viabilidad IN ('Bajo', 'Medio', 'Alto')
  ),
  oportunidad_urgencia TEXT CHECK (
    oportunidad_urgencia IS NULL OR 
    oportunidad_urgencia IN ('Bajo', 'Medio', 'Alto')
  ),
  oportunidad_brechas TEXT[],
  oportunidad_logros TEXT,
  
  -- ============================================
  -- DIMENSIONES TRANSVERSALES (Todos los registros)
  -- ============================================
  dim_agua TEXT NOT NULL DEFAULT 'NS/NR' CHECK (
    dim_agua IN ('Muy escasa', 'Escasa', 'Suficiente', 'Abundante', 'NS/NR')
  ),
  dim_entorno TEXT NOT NULL DEFAULT 'NS/NR' CHECK (
    dim_entorno IN ('Muy degradado', 'Degradado', 'En recuperación', 'Conservado', 'NS/NR')
  ),
  dim_social TEXT NOT NULL DEFAULT 'NS/NR' CHECK (
    dim_social IN ('Muy débil', 'Débil', 'Media', 'Fuerte', 'NS/NR')
  ),
  dim_gobernanza TEXT NOT NULL DEFAULT 'NS/NR' CHECK (
    dim_gobernanza IN ('Muy débil', 'Débil', 'Media', 'Fuerte', 'NS/NR')
  ),
  dim_financiamiento TEXT NOT NULL DEFAULT 'NS/NR' CHECK (
    dim_financiamiento IN ('Muy difícil', 'Difícil', 'Medio', 'Fácil', 'NS/NR')
  ),
  dim_regeneracion TEXT NOT NULL DEFAULT 'NS/NR' CHECK (
    dim_regeneracion IN ('Bajo', 'Medio', 'Alto', 'NS/NR')
  ),
  dim_importancia_lugar TEXT DEFAULT '',
  
  -- Auditoría
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT titulo_not_empty CHECK (LENGTH(TRIM(titulo)) > 0),
  CONSTRAINT descripcion_not_empty CHECK (LENGTH(TRIM(descripcion)) > 0)
);

-- Índices
CREATE INDEX idx_obs_punto ON public.observaciones(punto_id);
CREATE INDEX idx_obs_autor ON public.observaciones(autor_id);
CREATE INDEX idx_obs_tipo ON public.observaciones(tipo);
CREATE INDEX idx_obs_created_at ON public.observaciones(created_at DESC);
CREATE INDEX idx_obs_dim_agua ON public.observaciones(dim_agua);
CREATE INDEX idx_obs_dim_entorno ON public.observaciones(dim_entorno);

-- Row Level Security
ALTER TABLE public.observaciones ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view all observaciones" 
  ON public.observaciones 
  FOR SELECT 
  USING (TRUE);

CREATE POLICY "Authenticated users can create observaciones" 
  ON public.observaciones 
  FOR INSERT 
  WITH CHECK (auth.uid() IS NOT NULL AND autor_id = auth.uid());

CREATE POLICY "Users can update own observaciones" 
  ON public.observaciones 
  FOR UPDATE 
  USING (autor_id = auth.uid());

CREATE POLICY "Users can delete own observaciones" 
  ON public.observaciones 
  FOR DELETE 
  USING (autor_id = auth.uid());


-- ============================================
-- 4. TABLA: geometrias_bna (Caché de geometrías)
-- ============================================
CREATE TABLE public.geometrias_bna (
  id SERIAL PRIMARY KEY,
  
  tipo TEXT NOT NULL CHECK (tipo IN ('Cuenca', 'Subcuenca', 'Subsubcuenca')),
  nombre TEXT NOT NULL,
  codigo TEXT UNIQUE,
  
  geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  UNIQUE(tipo, nombre)
);

-- Índices
CREATE INDEX idx_geom_bna_tipo ON public.geometrias_bna(tipo);
CREATE INDEX idx_geom_bna_geom ON public.geometrias_bna USING GIST(geom);

-- Row Level Security
ALTER TABLE public.geometrias_bna ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view BNA geometries" 
  ON public.geometrias_bna 
  FOR SELECT 
  USING (TRUE);

CREATE POLICY "Only service role can insert BNA geometries"
  ON public.geometrias_bna
  FOR INSERT
  WITH CHECK (FALSE);  -- Solo via servicio backend


-- ============================================
-- 5. FUNCIONES Y TRIGGERS
-- ============================================

-- Función: Actualizar timestamp updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: users_profiles
CREATE TRIGGER update_users_profiles_updated_at
BEFORE UPDATE ON public.users_profiles
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Trigger: observaciones
CREATE TRIGGER update_observaciones_updated_at
BEFORE UPDATE ON public.observaciones
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- 6. VISTAS (Opcionales, para análisis)
-- ============================================

-- Vista: Observaciones con detalles de punto
CREATE OR REPLACE VIEW public.observaciones_con_ubicacion AS
SELECT 
  o.id,
  o.titulo,
  o.descripcion,
  o.tipo,
  o.created_at,
  o.dim_agua,
  o.dim_entorno,
  o.dim_social,
  p.lat,
  p.lon,
  p.cuenca,
  p.subcuenca,
  p.subsubcuenca,
  p.comuna_nombre,
  p.region_nombre,
  u.nombre as autor_nombre,
  u.tipo_actor
FROM public.observaciones o
JOIN public.puntos p ON o.punto_id = p.id
JOIN public.users_profiles u ON o.autor_id = u.auth_user_id;

-- Vista: Estadísticas por cuenca
CREATE OR REPLACE VIEW public.stats_by_cuenca AS
SELECT 
  p.cuenca,
  COUNT(DISTINCT o.id) as total_observaciones,
  COUNT(DISTINCT CASE WHEN o.tipo = 'Conflicto' THEN o.id END) as conflictos,
  COUNT(DISTINCT CASE WHEN o.tipo = 'Iniciativa' THEN o.id END) as iniciativas,
  COUNT(DISTINCT CASE WHEN o.tipo = 'Actor' THEN o.id END) as actores,
  COUNT(DISTINCT CASE WHEN o.tipo = 'Oportunidad' THEN o.id END) as oportunidades,
  COUNT(DISTINCT p.id) as puntos_totales
FROM public.puntos p
LEFT JOIN public.observaciones o ON p.id = o.punto_id
WHERE p.cuenca IS NOT NULL AND p.cuenca != 'N/A'
GROUP BY p.cuenca;


-- ============================================
-- 7. PERMISOS Y AUDITORÍA (Opcional)
-- ============================================

-- Ver si necesitas auditoría completa, descomenta:
-- CREATE TABLE public.audit_log (
--   id BIGSERIAL PRIMARY KEY,
--   tabla TEXT,
--   accion TEXT,  -- INSERT, UPDATE, DELETE
--   usuario UUID,
--   datos_anteriores JSONB,
--   datos_nuevos JSONB,
--   creado_at TIMESTAMP DEFAULT NOW()
-- );

-- ============================================
-- 8. VERIFICACIÓN FINAL
-- ============================================
-- Ejecuta esto para verificar que todo se creó:
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public';
-- Deberías ver:
-- - users_profiles
-- - puntos
-- - observaciones
-- - geometrias_bna

-- Verifica índices:
-- SELECT * FROM pg_indexes WHERE schemaname = 'public';

-- Verifica policies:
-- SELECT * FROM pg_policies WHERE schemaname = 'public';
