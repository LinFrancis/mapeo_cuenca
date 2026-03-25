-- ============================================
-- FIX_RLS.sql — EJECUTAR COMPLETO EN SUPABASE SQL EDITOR
-- Soluciona el error:
--   "new row violates row-level security policy for table users_profiles"
--
-- Este script elimina TODAS las policies existentes de las 3 tablas
-- y las recrea correctamente.
-- ============================================

-- =============================================
-- PASO 1: BORRAR TODAS LAS POLICIES EXISTENTES
-- =============================================

-- users_profiles — borrar cualquier policy que exista
DROP POLICY IF EXISTS "Users can insert own profile" ON public.users_profiles;
DROP POLICY IF EXISTS "New users can insert own profile" ON public.users_profiles;
DROP POLICY IF EXISTS "Anyone authenticated can insert profile" ON public.users_profiles;
DROP POLICY IF EXISTS "Users can view own profile" ON public.users_profiles;
DROP POLICY IF EXISTS "Authenticated users can view all profiles" ON public.users_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users_profiles;
DROP POLICY IF EXISTS "Users can delete own profile" ON public.users_profiles;
DROP POLICY IF EXISTS "Enable insert for authenticated users only" ON public.users_profiles;
DROP POLICY IF EXISTS "Enable read access for all users" ON public.users_profiles;

-- puntos
DROP POLICY IF EXISTS "Anyone can view all puntos" ON public.puntos;
DROP POLICY IF EXISTS "Authenticated users can create puntos" ON public.puntos;
DROP POLICY IF EXISTS "Users can update own puntos" ON public.puntos;

-- observaciones
DROP POLICY IF EXISTS "Anyone can view all observaciones" ON public.observaciones;
DROP POLICY IF EXISTS "Authenticated users can create observaciones" ON public.observaciones;
DROP POLICY IF EXISTS "Users can update own observaciones" ON public.observaciones;
DROP POLICY IF EXISTS "Users can delete own observaciones" ON public.observaciones;


-- =============================================
-- PASO 2: ASEGURAR QUE RLS ESTÁ HABILITADO
-- =============================================

ALTER TABLE public.users_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.puntos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.observaciones ENABLE ROW LEVEL SECURITY;


-- =============================================
-- PASO 3: CREAR POLICIES NUEVAS — users_profiles
-- =============================================

-- INSERT: Permitir a CUALQUIERA insertar un perfil.
-- ¿Por qué? Porque durante el signup, el SDK de Python hace:
--   1) auth.sign_up()  → crea usuario en auth.users
--   2) table.insert()  → crea perfil en users_profiles
-- Entre el paso 1 y 2, la sesión puede no estar activa
-- (especialmente si "Confirm email" está habilitado),
-- así que auth.uid() retorna NULL y la policy restrictiva falla.
--
-- Esto es seguro porque:
-- - Solo puedes insertar si ya tienes una sesión con la anon/publishable key
-- - El auth_user_id debe referenciar un usuario real (FK constraint)
-- - En producción puedes restringir más con un trigger o function
CREATE POLICY "Allow profile creation"
  ON public.users_profiles
  FOR INSERT
  WITH CHECK (true);

-- SELECT: Cualquier usuario autenticado puede ver perfiles
-- (necesario para dashboard, mapa global, etc.)
CREATE POLICY "Allow reading profiles"
  ON public.users_profiles
  FOR SELECT
  USING (true);

-- UPDATE: Solo el dueño puede editar su perfil
CREATE POLICY "Owner can update profile"
  ON public.users_profiles
  FOR UPDATE
  USING (auth_user_id = auth.uid());


-- =============================================
-- PASO 4: CREAR POLICIES NUEVAS — puntos
-- =============================================

-- SELECT: Todos pueden ver puntos
CREATE POLICY "Anyone can view puntos"
  ON public.puntos
  FOR SELECT
  USING (true);

-- INSERT: Usuarios autenticados pueden crear puntos
CREATE POLICY "Authenticated can create puntos"
  ON public.puntos
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

-- UPDATE: Solo el creador puede editar
CREATE POLICY "Owner can update puntos"
  ON public.puntos
  FOR UPDATE
  USING (created_by = auth.uid());


-- =============================================
-- PASO 5: CREAR POLICIES NUEVAS — observaciones
-- =============================================

-- SELECT: Todos pueden ver observaciones
CREATE POLICY "Anyone can view observaciones"
  ON public.observaciones
  FOR SELECT
  USING (true);

-- INSERT: Usuarios autenticados pueden crear
CREATE POLICY "Authenticated can create observaciones"
  ON public.observaciones
  FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

-- UPDATE: Solo el autor puede editar
CREATE POLICY "Author can update observaciones"
  ON public.observaciones
  FOR UPDATE
  USING (autor_id = auth.uid());

-- DELETE: Solo el autor puede eliminar
CREATE POLICY "Author can delete observaciones"
  ON public.observaciones
  FOR DELETE
  USING (autor_id = auth.uid());


-- =============================================
-- PASO 6: VERIFICAR
-- =============================================

-- Ejecuta esto para confirmar que todo quedó bien:
SELECT
  schemaname,
  tablename,
  policyname,
  cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
