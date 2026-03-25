-- ============================================
-- MIGRATION_V2.sql — Ejecutar en Supabase SQL Editor
-- Incluye: trigger de signup + campo enlaces + policies
-- ============================================

-- ===== LIMPIAR POLICIES =====
DO $$ DECLARE pol RECORD; BEGIN
    FOR pol IN SELECT policyname, tablename FROM pg_policies WHERE schemaname='public' AND tablename IN ('users_profiles','puntos','observaciones') LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', pol.policyname, pol.tablename);
    END LOOP;
END; $$;

-- ===== TRIGGER SIGNUP =====
CREATE OR REPLACE FUNCTION public.handle_new_user() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users_profiles (auth_user_id, nombre, email, tipo_actor)
    VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'nombre','Sin nombre'), COALESCE(NEW.email,''), COALESCE(NEW.raw_user_meta_data->>'tipo_actor','Otro'));
    RETURN NEW;
EXCEPTION WHEN unique_violation THEN RETURN NEW;
END; $$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created AFTER INSERT ON auth.users FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ===== AGREGAR CAMPO ENLACES (si no existe) =====
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='public' AND table_name='observaciones' AND column_name='enlaces') THEN
        ALTER TABLE public.observaciones ADD COLUMN enlaces JSONB DEFAULT '{}';
    END IF;
END; $$;

-- ===== AGREGAR CAMPO PRECISION si no existe con check correcto =====
-- (el schema original ya lo tiene en puntos, pero verificamos)

-- ===== RLS =====
ALTER TABLE public.users_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.puntos ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.observaciones ENABLE ROW LEVEL SECURITY;

-- users_profiles
CREATE POLICY "p_sel" ON public.users_profiles FOR SELECT USING (true);
CREATE POLICY "p_ins" ON public.users_profiles FOR INSERT WITH CHECK (true);
CREATE POLICY "p_upd" ON public.users_profiles FOR UPDATE USING (auth_user_id = auth.uid());

-- puntos
CREATE POLICY "pt_sel" ON public.puntos FOR SELECT USING (true);
CREATE POLICY "pt_ins" ON public.puntos FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);
CREATE POLICY "pt_upd" ON public.puntos FOR UPDATE USING (created_by = auth.uid());

-- observaciones
CREATE POLICY "ob_sel" ON public.observaciones FOR SELECT USING (true);
CREATE POLICY "ob_ins" ON public.observaciones FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);
CREATE POLICY "ob_upd" ON public.observaciones FOR UPDATE USING (autor_id = auth.uid());
CREATE POLICY "ob_del" ON public.observaciones FOR DELETE USING (autor_id = auth.uid());

-- ===== FIX HUÉRFANOS =====
INSERT INTO public.users_profiles (auth_user_id, nombre, email, tipo_actor)
SELECT au.id, COALESCE(au.raw_user_meta_data->>'nombre','Sin nombre'), COALESCE(au.email,''), COALESCE(au.raw_user_meta_data->>'tipo_actor','Otro')
FROM auth.users au LEFT JOIN public.users_profiles up ON au.id = up.auth_user_id
WHERE up.id IS NULL ON CONFLICT (auth_user_id) DO NOTHING;

-- ===== VERIFICAR =====
SELECT tablename, policyname, cmd FROM pg_policies WHERE schemaname='public' ORDER BY 1,2;
