"""
supabase_client.py — v2.0. Signup via trigger metadata. Search support. Enlaces.
"""
import streamlit as st
from typing import Optional, Dict, List
from config import SUPABASE_URL, SUPABASE_KEY

def _get_client():
    if "sb_client" not in st.session_state:
        if not SUPABASE_URL or not SUPABASE_KEY: return None
        try:
            from supabase import create_client
            st.session_state.sb_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e: st.error(f"Error Supabase: {e}"); return None
    return st.session_state.sb_client

def test_connection():
    c = _get_client()
    if not c: return False
    try: c.table("users_profiles").select("id").limit(1).execute(); return True
    except: return False

def signup_user(email, password, nombre, tipo_actor):
    c = _get_client()
    if not c: return {"success": False, "error": "Sin conexión"}
    try:
        r = c.auth.sign_up({"email": email, "password": password, "options": {"data": {"nombre": nombre, "tipo_actor": tipo_actor}}})
        if not r.user: return {"success": False, "error": "No se pudo crear usuario"}
        try: c.auth.sign_out()
        except: pass
        msg = f"Cuenta creada para {nombre}." + ("" if r.session else " Revisa tu email para confirmar.")
        return {"success": True, "message": msg}
    except Exception as e:
        err = str(e)
        try: c.auth.sign_out()
        except: pass
        if "already registered" in err.lower(): return {"success": False, "error": "Email ya registrado"}
        if "rate limit" in err.lower(): return {"success": False, "error": "Demasiados intentos. Espera unos minutos."}
        return {"success": False, "error": f"Error: {err}"}

def login_user(email, password):
    c = _get_client()
    if not c: return {"success": False, "error": "Sin conexión"}
    try:
        r = c.auth.sign_in_with_password({"email": email, "password": password})
        if not r.user: return {"success": False, "error": "Credenciales inválidas"}
        p = get_user_profile(r.user.id)
        if not p: return {"success": False, "error": "Perfil no encontrado"}
        return {"success": True, "user_id": r.user.id, "profile": p}
    except Exception as e:
        err = str(e)
        if "invalid" in err.lower(): return {"success": False, "error": "Email o contraseña incorrectos"}
        if "not confirmed" in err.lower(): return {"success": False, "error": "Confirma tu email primero"}
        return {"success": False, "error": f"Error: {err}"}

def get_user_profile(uid):
    c = _get_client()
    if not c: return None
    try: return c.table("users_profiles").select("*").eq("auth_user_id", uid).single().execute().data
    except: return None

def update_user_profile(uid, updates):
    c = _get_client()
    if not c: return False
    try: c.table("users_profiles").update(updates).eq("auth_user_id", uid).execute(); return True
    except: return False

def create_punto(uid, lat, lon, cuenca="N/A", subcuenca="N/A", subsubcuenca="N/A", precision="Aproximada", comuna="N/A"):
    c = _get_client()
    if not c: return None
    try:
        r = c.table("puntos").insert({"lat": float(lat), "lon": float(lon), "cuenca": cuenca or "N/A",
            "subcuenca": subcuenca or "N/A", "subsubcuenca": subsubcuenca or "N/A",
            "precision_ubicacion": precision, "comuna_nombre": comuna or "N/A", "created_by": uid}).execute()
        return r.data[0]["id"] if r.data else None
    except Exception as e: st.error(f"Error punto: {e}"); return None

def get_all_puntos():
    c = _get_client()
    if not c: return []
    try: return c.table("puntos").select("*").execute().data or []
    except: return []

def create_observacion(uid, punto_id, tipo, titulo, descripcion, dimensiones, modulo=None, enlaces=None):
    c = _get_client()
    if not c: return None
    try:
        payload = {"punto_id": punto_id, "autor_id": uid, "tipo": tipo, "titulo": titulo, "descripcion": descripcion,
            "dim_agua": dimensiones.get("agua", "NS/NR"), "dim_entorno": dimensiones.get("entorno", "NS/NR"),
            "dim_social": dimensiones.get("social", "NS/NR"), "dim_gobernanza": dimensiones.get("gobernanza", "NS/NR"),
            "dim_financiamiento": dimensiones.get("financiamiento", "NS/NR"), "dim_regeneracion": dimensiones.get("regeneracion", "NS/NR"),
            "dim_importancia_lugar": dimensiones.get("importancia_lugar", "")}
        if enlaces: payload["enlaces"] = enlaces
        if modulo and tipo == "Conflicto":
            payload.update({"conflicto_actores_involucrados": modulo.get("actores"), "conflicto_gravedad": modulo.get("gravedad"),
                           "conflicto_duracion": modulo.get("duracion"), "conflicto_dialogo": modulo.get("dialogo")})
        elif modulo and tipo == "Iniciativa":
            payload.update({"iniciativa_tipos": modulo.get("tipos", []), "iniciativa_estado": modulo.get("estado"), "iniciativa_escala": modulo.get("escala")})
        elif modulo and tipo == "Actor":
            payload.update({"actor_nombre": modulo.get("nombre"), "actor_tipo": modulo.get("tipo")})
        elif modulo and tipo == "Oportunidad":
            payload.update({"oportunidad_viabilidad": modulo.get("viabilidad"), "oportunidad_urgencia": modulo.get("urgencia"),
                           "oportunidad_brechas": modulo.get("brechas", [])})
        r = c.table("observaciones").insert(payload).execute()
        return r.data[0]["id"] if r.data else None
    except Exception as e: st.error(f"Error obs: {e}"); return None

def get_all_observaciones():
    c = _get_client()
    if not c: return []
    try: return c.table("observaciones").select("*").order("created_at", desc=True).execute().data or []
    except: return []

def get_observaciones_by_user(uid):
    c = _get_client()
    if not c: return []
    try: return c.table("observaciones").select("*").eq("autor_id", uid).order("created_at", desc=True).execute().data or []
    except: return []

def delete_observacion(oid, uid):
    c = _get_client()
    if not c: return False
    try: c.table("observaciones").delete().eq("id", oid).eq("autor_id", uid).execute(); return True
    except: return False

def get_dashboard_stats():
    try:
        obs = get_all_observaciones(); puntos = get_all_puntos()
        bt = {}
        for o in obs: bt[o.get("tipo", "?")] = bt.get(o.get("tipo", "?"), 0) + 1
        cs = set(p.get("cuenca", "N/A") for p in puntos if p.get("cuenca") and p["cuenca"] != "N/A")
        dims = {d: {} for d in ["agua", "entorno", "social", "gobernanza", "financiamiento", "regeneracion"]}
        for o in obs:
            for d in dims:
                v = o.get(f"dim_{d}", "NS/NR"); dims[d][v] = dims[d].get(v, 0) + 1
        return {"total": len(obs), "total_puntos": len(puntos), "by_tipo": bt,
                "cuencas_unicas": len(cs), "cuencas_list": sorted(cs),
                "dimensiones": dims, "observaciones": obs, "puntos": puntos}
    except: return {}
