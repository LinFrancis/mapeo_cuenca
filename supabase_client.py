"""
supabase_client.py — Cliente Supabase
Signup usa metadata en sign_up → el trigger en Supabase crea el perfil automáticamente.
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from config import SUPABASE_URL, SUPABASE_KEY


def _get_client():
    if "sb_client" not in st.session_state:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return None
        try:
            from supabase import create_client
            st.session_state.sb_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            st.error(f"Error Supabase: {e}")
            return None
    return st.session_state.sb_client


def test_connection():
    client = _get_client()
    if not client:
        return False
    try:
        client.table("users_profiles").select("id").limit(1).execute()
        return True
    except Exception:
        return False


# ============================================
# AUTH
# ============================================
def signup_user(email, password, nombre, tipo_actor):
    """
    Signup usando metadata. El trigger handle_new_user() en Supabase
    lee nombre y tipo_actor desde raw_user_meta_data y crea el perfil
    automáticamente. No necesitamos hacer INSERT manual.
    """
    client = _get_client()
    if not client:
        return {"success": False, "error": "Sin conexión a Supabase"}
    try:
        auth_resp = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "nombre": nombre,
                    "tipo_actor": tipo_actor,
                }
            }
        })
        if not auth_resp.user:
            return {"success": False, "error": "No se pudo crear el usuario"}

        # Limpiar sesión si quedó abierta
        try:
            client.auth.sign_out()
        except Exception:
            pass

        has_session = auth_resp.session is not None
        if has_session:
            return {"success": True, "message": f"Cuenta creada para {nombre}. Ya puedes iniciar sesión."}
        else:
            return {"success": True, "message": f"Cuenta creada. Revisa tu email ({email}) para confirmar y luego inicia sesión."}

    except Exception as e:
        err = str(e)
        try:
            client.auth.sign_out()
        except Exception:
            pass
        if "already registered" in err.lower():
            return {"success": False, "error": "Este email ya está registrado. Intenta iniciar sesión."}
        if "rate limit" in err.lower():
            return {"success": False, "error": "Demasiados intentos. Espera unos minutos y vuelve a intentar."}
        return {"success": False, "error": f"Error: {err}"}


def login_user(email, password):
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
            # El trigger debería haberlo creado, pero por si acaso
            return {"success": False, "error": "Perfil no encontrado. Contacta al administrador."}

        return {"success": True, "user_id": user_id, "profile": profile}
    except Exception as e:
        err = str(e)
        if "invalid" in err.lower() or "credentials" in err.lower():
            return {"success": False, "error": "Email o contraseña incorrectos"}
        if "email not confirmed" in err.lower():
            return {"success": False, "error": "Debes confirmar tu email antes de iniciar sesión. Revisa tu bandeja."}
        return {"success": False, "error": f"Error: {err}"}


# ============================================
# PERFILES
# ============================================
def get_user_profile(user_id):
    client = _get_client()
    if not client:
        return None
    try:
        return client.table("users_profiles").select("*").eq("auth_user_id", user_id).single().execute().data
    except Exception:
        return None


def update_user_profile(user_id, updates):
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
def create_punto(user_id, lat, lon, cuenca="N/A", subcuenca="N/A", subsubcuenca="N/A"):
    client = _get_client()
    if not client:
        return None
    try:
        resp = client.table("puntos").insert({
            "lat": float(lat), "lon": float(lon),
            "cuenca": cuenca or "N/A", "subcuenca": subcuenca or "N/A",
            "subsubcuenca": subsubcuenca or "N/A",
            "precision_ubicacion": "Aproximada", "created_by": user_id,
        }).execute()
        return resp.data[0]["id"] if resp.data else None
    except Exception as e:
        st.error(f"Error punto: {e}")
        return None


def get_all_puntos():
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
def create_observacion(user_id, punto_id, tipo, titulo, descripcion, dimensiones, modulo=None):
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
        if modulo and tipo == "Conflicto":
            payload.update({"conflicto_actores_involucrados": modulo.get("actores"),
                           "conflicto_gravedad": modulo.get("gravedad"),
                           "conflicto_duracion": modulo.get("duracion"),
                           "conflicto_dialogo": modulo.get("dialogo")})
        elif modulo and tipo == "Iniciativa":
            payload.update({"iniciativa_tipos": modulo.get("tipos", []),
                           "iniciativa_estado": modulo.get("estado"),
                           "iniciativa_escala": modulo.get("escala")})
        elif modulo and tipo == "Actor":
            payload.update({"actor_nombre": modulo.get("nombre"), "actor_tipo": modulo.get("tipo")})
        elif modulo and tipo == "Oportunidad":
            payload.update({"oportunidad_viabilidad": modulo.get("viabilidad"),
                           "oportunidad_urgencia": modulo.get("urgencia"),
                           "oportunidad_brechas": modulo.get("brechas", [])})
        resp = client.table("observaciones").insert(payload).execute()
        return resp.data[0]["id"] if resp.data else None
    except Exception as e:
        st.error(f"Error observación: {e}")
        return None


def get_all_observaciones():
    client = _get_client()
    if not client:
        return []
    try:
        return client.table("observaciones").select("*").order("created_at", desc=True).execute().data or []
    except Exception:
        return []


def get_observaciones_by_user(user_id):
    client = _get_client()
    if not client:
        return []
    try:
        return client.table("observaciones").select("*").eq("autor_id", user_id).order("created_at", desc=True).execute().data or []
    except Exception:
        return []


def delete_observacion(obs_id, user_id):
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
def get_dashboard_stats():
    try:
        obs = get_all_observaciones()
        puntos = get_all_puntos()
        by_tipo = {}
        for o in obs:
            t = o.get("tipo", "Otro")
            by_tipo[t] = by_tipo.get(t, 0) + 1
        cuencas = set(p.get("cuenca", "N/A") for p in puntos if p.get("cuenca") and p["cuenca"] != "N/A")
        dims = {d: {} for d in ["agua", "entorno", "social", "gobernanza", "financiamiento", "regeneracion"]}
        for o in obs:
            for d in dims:
                val = o.get(f"dim_{d}", "NS/NR")
                dims[d][val] = dims[d].get(val, 0) + 1
        return {"total": len(obs), "total_puntos": len(puntos), "by_tipo": by_tipo,
                "cuencas_unicas": len(cuencas), "cuencas_list": sorted(cuencas),
                "dimensiones": dims, "observaciones": obs, "puntos": puntos}
    except Exception:
        return {}
