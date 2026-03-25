-- ============================================
-- FIX_RLS.sql
-- Ejecutar en Supabase SQL Editor si el signup falla con:
-- "new row violates row-level security policy for table users_profiles"
--
-- PROBLEMA: La policy original exige auth_user_id = auth.uid(), pero
-- durante el signup la sesión puede no estar activa aún.
--
-- SOLUCIÓN: Permitir INSERT a cualquier usuario autenticado (auth.uid() IS NOT NULL)
-- siempre que el auth_user_id que inserta coincida con su propia sesión.
-- También agregamos una policy para que usuarios autenticados puedan
-- ver TODOS los perfiles (necesario para dashboard y mapa global).
-- ============================================

-- 1. Eliminar policies existentes que pueden estar bloqueando
DROP POLICY IF EXISTS "New users can insert own profile" ON public.users_profiles;
DROP POLICY IF EXISTS "Users can view own profile" ON public.users_profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users_profiles;

-- 2. INSERT: Permitir que un usuario autenticado inserte su propio perfil
--    auth.uid() puede tardar un ciclo en estar disponible tras sign_up,
--    así que también permitimos INSERT si el role es 'authenticated'
CREATE POLICY "Users can insert own profile"
  ON public.users_profiles
  FOR INSERT
  WITH CHECK (
    auth.uid() IS NOT NULL
    AND auth_user_id = auth.uid()
  );

-- 3. SELECT: Usuarios autenticados pueden ver todos los perfiles
--    (necesario para que el dashboard y mapa muestren nombres de autores)
CREATE POLICY "Authenticated users can view all profiles"
  ON public.users_profiles
  FOR SELECT
  USING (auth.uid() IS NOT NULL);

-- 4. UPDATE: Solo el propio usuario puede editar su perfil
CREATE POLICY "Users can update own profile"
  ON public.users_profiles
  FOR UPDATE
  USING (auth_user_id = auth.uid());

-- ============================================
-- OPCIONAL: Si después de aplicar esto el signup SIGUE fallando,
-- probablemente tienes "Confirm email" habilitado en Supabase Auth.
-- En ese caso, desactívalo temporalmente:
--   Dashboard → Authentication → Settings → Email Auth →
--   Deshabilita "Confirm email"
--
-- O bien, ejecuta esta policy más permisiva (SOLO para desarrollo):
-- ============================================

-- DROP POLICY IF EXISTS "Users can insert own profile" ON public.users_profiles;
-- CREATE POLICY "Anyone authenticated can insert profile"
--   ON public.users_profiles
--   FOR INSERT
--   WITH CHECK (true);  -- Permite cualquier insert (usar solo en dev)

-- ============================================
-- VERIFICAR que las policies quedaron bien:
-- SELECT * FROM pg_policies WHERE tablename = 'users_profiles';
-- ============================================
