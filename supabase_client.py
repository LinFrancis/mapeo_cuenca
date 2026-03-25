"""
supabase_client.py — Cliente Supabase para Inteligencia Territorial
Inicialización lazy. Signup con sesión activa para pasar RLS.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from config import SUPABASE_URL, SUPABASE_KEY


# ============================================
# INICIALIZACIÓN LAZY
# ============================================
def _get_client():
    if "sb_client" not in st.session_state:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return None
        try:
            from supabase import create_client
            st.session_state.sb_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            st.error(f"Error al conectar con Supabase: {e}")
            return None
    return st.session_state.sb_client


def test_connection() -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        client.table("users_profiles").select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False


# ============================================
# AUTENTICACIÓN
# ============================================
def signup_user(email: str, password: str, nombre: str, tipo_actor: str) -> Dict[str, Any]:
    """
    Signup:
      1) auth.sign_up → crea usuario en auth.users
      2) INSERT perfil en users_profiles
         (la RLS policy permite INSERT con WITH CHECK (true) — ver FIX_RLS.sql)
      3) Si hay sesión activa, cerrarla para que el usuario haga login explícito
    """
    client = _get_client()
    if not client:
        return {"success": False, "error": "Sin conexión a Supabase"}
    try:
        # 1. Crear usuario en Auth
        auth_resp = client.auth.sign_up({"email": email, "password": password})
        if not auth_resp.user:
            return {"success": False, "error": "No se pudo crear el usuario"}

        user_id = auth_resp.user.id

        # 2. Insertar perfil
        #    Con la policy "WITH CHECK (true)" en FIX_RLS.sql, esto funciona
        #    independientemente de si hay sesión activa o confirm email habilitado.
        client.table("users_profiles").insert({
            "auth_user_id": user_id,
            "nombre": nombre,
            "email": email,
            "tipo_actor": tipo_actor,
        }).execute()

        # 3. Limpiar sesión si quedó abierta
        try:
            client.auth.sign_out()
        except Exception:
            pass

        # Mensaje según si hay confirmación de email
        has_session = auth_resp.session is not None
        if has_session:
            msg = f"Cuenta creada para {nombre}. Ya puedes iniciar sesión."
        else:
            msg = f"Cuenta creada para {nombre}. Revisa tu email para confirmar y luego inicia sesión."

        return {"success": True, "user_id": user_id, "message": msg}

    except Exception as e:
        err = str(e)
        try:
            client.auth.sign_out()
        except Exception:
            pass

        if "already registered" in err.lower() or "already been registered" in err.lower():
            return {"success": False, "error": "Este email ya está registrado"}
        if "row-level security" in err.lower() or "42501" in err:
            return {
                "success": False,
                "error": (
                    "Error de permisos. Ejecuta FIX_RLS.sql en el SQL Editor "
                    "de Supabase (Dashboard → SQL Editor → pega el contenido → Run)."
                ),
            }
        if "email" in err.lower() and "confirm" in err.lower():
            return {
                "success": False,
                "error": (
                    "Email requiere confirmación. Desactiva 'Confirm email' en "
                    "Supabase → Authentication → Settings → Email, o confirma tu email."
                ),
            }
        return {"success": False, "error": f"Error: {err}"}


def login_user(email: str, password: str) -> Dict[str, Any]:
    client = _get_client()
    if not client:
        return {"success": False, "error": "Sin conexión a Supabase"}
    try:
        auth_resp = client.auth.sign_in_with_password({"email": email, "password": password})
        if not auth_resp.user:
            return {"success": False, "error": "Credenciales inválidas"}

        user_id = auth_resp.user.id
        profile = get_user_profile(user_id)

        if not profile:
            return {"success": False, "error": "No se encontró perfil de usuario"}

        return {"success": True, "user_id": user_id, "profile": profile}
    except Exception as e:
        msg = str(e)
        if "invalid" in msg.lower() or "credentials" in msg.lower():
            return {"success": False, "error": "Email o contraseña incorrectos"}
        return {"success": False, "error": f"Error: {msg}"}


# ============================================
# PERFILES
# ============================================
def get_user_profile(user_id: str) -> Optional[Dict]:
    client = _get_client()
    if not client:
        return None
    try:
        resp = client.table("users_profiles").select("*").eq("auth_user_id", user_id).single().execute()
        return resp.data
    except Exception:
        return None


def update_user_profile(user_id: str, updates: Dict) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        client.table("users_profiles").update(updates).eq("auth_user_id", user_id).execute()
        return True
    except Exception:
        return False


# ============================================
# PUNTOS
# ============================================
def create_punto(user_id: str, lat: float, lon: float,
                 cuenca: str = "N/A", subcuenca: str = "N/A",
                 subsubcuenca: str = "N/A") -> Optional[int]:
    client = _get_client()
    if not client:
        return None
    try:
        resp = client.table("puntos").insert({
            "lat": float(lat), "lon": float(lon),
            "cuenca": cuenca or "N/A",
            "subcuenca": subcuenca or "N/A",
            "subsubcuenca": subsubcuenca or "N/A",
            "precision_ubicacion": "Aproximada",
            "created_by": user_id,
        }).execute()
        return resp.data[0]["id"] if resp.data else None
    except Exception as e:
        st.error(f"Error al crear punto: {e}")
        return None


def get_all_puntos() -> List[Dict]:
    client = _get_client()
    if not client:
        return []
    try:
        return client.table("puntos").select("*").execute().data or []
    except Exception:
        return []


# ============================================
# OBSERVACIONES
# ============================================
def create_observacion(user_id: str, punto_id: int, tipo: str,
                       titulo: str, descripcion: str,
                       dimensiones: Dict, modulo_datos: Dict = None) -> Optional[int]:
    client = _get_client()
    if not client:
        return None
    try:
        payload = {
            "punto_id": punto_id, "autor_id": user_id,
            "tipo": tipo, "titulo": titulo, "descripcion": descripcion,
            "dim_agua": dimensiones.get("agua", "NS/NR"),
            "dim_entorno": dimensiones.get("entorno", "NS/NR"),
            "dim_social": dimensiones.get("social", "NS/NR"),
            "dim_gobernanza": dimensiones.get("gobernanza", "NS/NR"),
            "dim_financiamiento": dimensiones.get("financiamiento", "NS/NR"),
            "dim_regeneracion": dimensiones.get("regeneracion", "NS/NR"),
            "dim_importancia_lugar": dimensiones.get("importancia_lugar", ""),
        }
        if modulo_datos and tipo == "Conflicto":
            payload.update({
                "conflicto_actores_involucrados": modulo_datos.get("actores"),
                "conflicto_gravedad": modulo_datos.get("gravedad"),
                "conflicto_duracion": modulo_datos.get("duracion"),
                "conflicto_dialogo": modulo_datos.get("dialogo"),
            })
        elif modulo_datos and tipo == "Iniciativa":
            payload.update({
                "iniciativa_tipos": modulo_datos.get("tipos", []),
                "iniciativa_estado": modulo_datos.get("estado"),
                "iniciativa_escala": modulo_datos.get("escala"),
            })
        elif modulo_datos and tipo == "Actor":
            payload.update({
                "actor_nombre": modulo_datos.get("nombre"),
                "actor_tipo": modulo_datos.get("tipo"),
            })
        elif modulo_datos and tipo == "Oportunidad":
            payload.update({
                "oportunidad_viabilidad": modulo_datos.get("viabilidad"),
                "oportunidad_urgencia": modulo_datos.get("urgencia"),
                "oportunidad_brechas": modulo_datos.get("brechas", []),
            })

        resp = client.table("observaciones").insert(payload).execute()
        return resp.data[0]["id"] if resp.data else None
    except Exception as e:
        st.error(f"Error al crear observación: {e}")
        return None


def get_all_observaciones() -> List[Dict]:
    client = _get_client()
    if not client:
        return []
    try:
        return client.table("observaciones").select("*").order("created_at", desc=True).execute().data or []
    except Exception:
        return []


def get_observaciones_by_user(user_id: str) -> List[Dict]:
    client = _get_client()
    if not client:
        return []
    try:
        return (client.table("observaciones").select("*")
                .eq("autor_id", user_id).order("created_at", desc=True)
                .execute()).data or []
    except Exception:
        return []


def delete_observacion(obs_id: int, user_id: str) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        client.table("observaciones").delete().eq("id", obs_id).eq("autor_id", user_id).execute()
        return True
    except Exception:
        return False


# ============================================
# ESTADÍSTICAS
# ============================================
def get_dashboard_stats() -> Dict:
    client = _get_client()
    if not client:
        return {}
    try:
        obs = get_all_observaciones()
        puntos = get_all_puntos()

        by_tipo = {}
        for o in obs:
            t = o.get("tipo", "Otro")
            by_tipo[t] = by_tipo.get(t, 0) + 1

        cuencas = set()
        for p in puntos:
            c = p.get("cuenca", "N/A")
            if c and c != "N/A":
                cuencas.add(c)

        dims = {d: {} for d in ["agua", "entorno", "social", "gobernanza", "financiamiento", "regeneracion"]}
        for o in obs:
            for d in dims:
                val = o.get(f"dim_{d}", "NS/NR")
                dims[d][val] = dims[d].get(val, 0) + 1

        return {
            "total": len(obs),
            "total_puntos": len(puntos),
            "by_tipo": by_tipo,
            "cuencas_unicas": len(cuencas),
            "cuencas_list": sorted(cuencas),
            "dimensiones": dims,
            "observaciones": obs,
            "puntos": puntos,
        }
    except Exception as e:
        print(f"Stats error: {e}")
        return {}
