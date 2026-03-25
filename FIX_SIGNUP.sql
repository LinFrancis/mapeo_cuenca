-- ============================================
-- FIX_SIGNUP.sql
-- EJECUTAR COMPLETO EN SUPABASE SQL EDITOR
--
-- PROBLEMA: El signup falla con FK violation porque auth.sign_up()
-- y el INSERT en users_profiles son operaciones separadas, y con
-- las nuevas API keys (sb_publishable_) la sesión puede no estar
-- sincronizada.
--
-- SOLUCIÓN: Crear un trigger en auth.users que AUTOMÁTICAMENTE
-- crea el perfil en users_profiles cuando se registra un usuario.
-- El signup en Python solo necesita llamar auth.sign_up() con
-- metadata, y el trigger hace el resto.
-- ============================================


-- =============================================
-- PASO 1: BORRAR TODAS LAS POLICIES EXISTENTES
-- =============================================
DO $$
DECLARE
    pol RECORD;
BEGIN
    FOR pol IN
        SELECT policyname, tablename
        FROM pg_policies
        WHERE schemaname = 'public'
        AND tablename IN ('users_profiles', 'puntos', 'observaciones')
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', pol.policyname, pol.tablename);
    END LOOP;
END;
$$;


-- =============================================
-- PASO 2: CREAR TRIGGER PARA AUTO-CREAR PERFIL
-- =============================================

-- Función que se ejecuta automáticamente al crear usuario en auth.users
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users_profiles (auth_user_id, nombre, email, tipo_actor)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'nombre', 'Sin nombre'),
        COALESCE(NEW.email, ''),
        COALESCE(NEW.raw_user_meta_data->>'tipo_actor', 'Otro')
    );
    RETURN NEW;
EXCEPTION
    WHEN unique_violation THEN
        -- El perfil ya existe, ignorar
        RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Eliminar trigger si ya existe
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Crear trigger
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();


-- =============================================
-- PASO 3: HABILITAR RLS
-- =============================================
ALTER TABLE public.users_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.puntos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.observaciones ENABLE ROW LEVEL SECURITY;


-- =============================================
-- PASO 4: POLICIES — users_profiles
-- =============================================

-- SELECT: Todos pueden ver perfiles (necesario para dashboard)
CREATE POLICY "profiles_select"
  ON public.users_profiles FOR SELECT
  USING (true);

-- UPDATE: Solo el dueño edita su perfil
CREATE POLICY "profiles_update"
  ON public.users_profiles FOR UPDATE
  USING (auth_user_id = auth.uid());

-- INSERT: El trigger se encarga, pero dejamos abierto por si acaso
CREATE POLICY "profiles_insert"
  ON public.users_profiles FOR INSERT
  WITH CHECK (true);


-- =============================================
-- PASO 5: POLICIES — puntos
-- =============================================

CREATE POLICY "puntos_select"
  ON public.puntos FOR SELECT USING (true);

CREATE POLICY "puntos_insert"
  ON public.puntos FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "puntos_update"
  ON public.puntos FOR UPDATE
  USING (created_by = auth.uid());


-- =============================================
-- PASO 6: POLICIES — observaciones
-- =============================================

CREATE POLICY "obs_select"
  ON public.observaciones FOR SELECT USING (true);

CREATE POLICY "obs_insert"
  ON public.observaciones FOR INSERT
  WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "obs_update"
  ON public.observaciones FOR UPDATE
  USING (autor_id = auth.uid());

CREATE POLICY "obs_delete"
  ON public.observaciones FOR DELETE
  USING (autor_id = auth.uid());


-- =============================================
-- PASO 7: LIMPIAR USUARIOS HUÉRFANOS
-- (usuarios en auth.users sin perfil en users_profiles)
-- =============================================

-- Esto crea perfiles para usuarios que ya existen pero no tienen perfil
INSERT INTO public.users_profiles (auth_user_id, nombre, email, tipo_actor)
SELECT
    au.id,
    COALESCE(au.raw_user_meta_data->>'nombre', 'Sin nombre'),
    COALESCE(au.email, ''),
    COALESCE(au.raw_user_meta_data->>'tipo_actor', 'Otro')
FROM auth.users au
LEFT JOIN public.users_profiles up ON au.id = up.auth_user_id
WHERE up.id IS NULL
ON CONFLICT (auth_user_id) DO NOTHING;


-- =============================================
-- PASO 8: VERIFICAR
-- =============================================
SELECT 'POLICIES' as tipo, tablename, policyname, cmd
FROM pg_policies WHERE schemaname = 'public'
UNION ALL
SELECT 'TRIGGER', 'auth.users', trigger_name, event_manipulation
FROM information_schema.triggers
WHERE trigger_name = 'on_auth_user_created'
ORDER BY 1, 2;
