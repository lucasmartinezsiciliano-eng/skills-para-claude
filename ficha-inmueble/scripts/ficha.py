#!/usr/bin/env python3
"""ficha-inmueble: lo que dicen los registros públicos de un inmueble en España.

Le das la dirección (o la referencia catastral) y consulta EN VIVO:
  1. Catastro (toda España salvo País Vasco y Navarra): inmuebles del portal,
     m² construidos, año, usos, suelo de la parcela, coordenadas y foto.
  2. Solo en Cataluña: certificado energético (ICAEN) y cédula de
     habitabilidad (Agència de l'Habitatge), los dos en datos abiertos.

Solo lee servicios oficiales y gratuitos. No pide claves, no guarda nada y no
busca al propietario: el Catastro no da el titular en la consulta libre.

Uso:
  python ficha.py --municipio Tarragona --calle "Plaza de la Font" --numero 1
  python ficha.py --municipio Madrid --calle "Calle de Alcala" --numero 1 --planta 2 --puerta A
  python ficha.py --rc 3534212CF5533D
Saca un JSON por pantalla. Python 3.8 o más, sin instalar nada.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import date

CAT = "https://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCallejero.svc/json"
COORD = "https://ovc.catastro.meh.es/OVCServWeb/OVCWcfCallejero/COVCCoordenadas.svc/json/Consulta_CPMRC"
FOTO = "https://ovc.catastro.meh.es/OVCServWeb/OVCWcfLibres/OVCFotoFachada.svc/RecuperarFotoFachadaGet?ReferenciaCatastral={}"
CEE = "https://analisi.transparenciacatalunya.cat/resource/j6ii-t3w2.json"
CED = "https://analisi.transparenciacatalunya.cat/resource/3pqu-s3ga.json"
UA = "Mozilla/5.0 (compatible; ficha-inmueble/1.0; +https://github.com/lucasmartinezsiciliano-eng/skills-para-claude)"

CATALUNYA = {8, 17, 25, 43}            # Barcelona, Girona, Lleida, Tarragona
FORALES = {"ALAVA", "ARABA", "BIZKAIA", "VIZCAYA", "GIPUZKOA", "GUIPUZCOA", "NAVARRA", "NAFARROA"}
CONECTORES = {"Y", "I", "E", "DE", "DEL", "DELS", "LA", "EL", "LES", "LOS", "LAS", "D", "L", "DA", "DO", "DAS", "DOS", "A"}
SIGLAS = {
    "CALLE": "CL", "CARRER": "CL", "C": "CL", "CL": "CL", "CR": "CR",
    "AVENIDA": "AV", "AVINGUDA": "AV", "AVDA": "AV", "AV": "AV",
    "PLAZA": "PZ", "PLACA": "PZ", "PL": "PZ", "PZ": "PZ",
    "PASEO": "PS", "PASSEIG": "PS", "PG": "PS", "PS": "PS",
    "RAMBLA": "RB", "RB": "RB", "CARRETERA": "CR", "CTRA": "CR",
    "CAMINO": "CM", "CAMI": "CM", "CM": "CM", "RONDA": "RD", "RD": "RD",
    "TRAVESIA": "TR", "TRAVESSERA": "TR", "TR": "TR", "PASAJE": "PJ", "PASSATGE": "PJ", "PJ": "PJ",
    "URBANIZACION": "UR", "UR": "UR", "GLORIETA": "GL", "GL": "GL",
}
BAJO = {"0", "BJ", "BAJO", "BAJ", "PB", "BX", "BAIXOS"}

avisos: list[str] = []


# ---------------------------------------------------------------- utilidades

def get(url: str, params: dict | None = None):
    if params:
        url += "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def mayus(s) -> str:
    """Mayúsculas sin tildes, pero con Ñ y Ç: el Catastro las necesita."""
    s = str(s or "").upper().replace("Ñ", "\x01").replace("Ç", "\x02")
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    return s.replace("\x01", "Ñ").replace("\x02", "Ç")


def palabras(s) -> list[str]:
    """Palabras con peso, para comparar nombres escritos de formas distintas."""
    s = mayus(s).replace("Ñ", "N").replace("Ç", "C")
    return [t for t in re.split(r"[^A-Z0-9]+", s) if t and t not in CONECTORES]


def parecido(a: list[str], b: list[str]) -> float:
    A, B = set(a), set(b)
    return len(A & B) / len(A | B) if A and B else 0.0


def lista(x) -> list:
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def error_cat(lerr) -> str:
    if isinstance(lerr, dict):
        lerr = lerr.get("err", lerr)
    return "; ".join(str(e.get("des", e)) if isinstance(e, dict) else str(e) for e in lista(lerr))


def rc_de(d: dict) -> str:
    return "".join(str((d or {}).get(k, "")) for k in ("pc1", "pc2", "car", "cc1", "cc2"))


def num(x):
    try:
        f = float(str(x).replace(",", "."))
        return int(f) if f.is_integer() else round(f, 2)
    except (TypeError, ValueError):
        return None


def norm_planta(x) -> str:
    s = re.sub(r"[^A-Z0-9]", "", mayus(x).replace("º", "").replace("ª", ""))
    s = s.lstrip("0") or ("0" if s else "")
    return "0" if s in BAJO else s


def norm_puerta(x) -> str:
    s = re.sub(r"[^A-Z0-9]", "", mayus(x).replace("º", "").replace("ª", ""))
    return s.lstrip("0") or ("0" if s else "")


def misma_planta(a, b) -> bool:
    return norm_planta(a) == norm_planta(b)


def misma_puerta(a, b) -> bool:
    return norm_puerta(a) == norm_puerta(b)


def coincide(fila_pis, fila_porta, planta, puerta) -> bool:
    if planta and not misma_planta(fila_pis, planta):
        return False
    if puerta and not misma_puerta(fila_porta, puerta):
        return False
    return True


# ------------------------------------------------------------------ catastro

PROV_ALIAS = {
    "ALICANTE": "ALACANT", "CASTELLON": "CASTELLO", "BALEARES": "ILLES BALEARS", "BALEARS": "ILLES BALEARS",
    "MALLORCA": "ILLES BALEARS", "GERONA": "GIRONA", "LERIDA": "LLEIDA", "ORENSE": "OURENSE",
    "CORUNA": "A CORUÑA", "TENERIFE": "S.C. TENERIFE", "RIOJA": "LA RIOJA", "PALMAS": "LAS PALMAS",
    "GRAN CANARIA": "LAS PALMAS",
}


def resolver_provincia(texto: str) -> str | None:
    pal = palabras(texto)
    if set(pal) & FORALES:
        return None
    alias = PROV_ALIAS.get(" ".join(pal)) or next((v for k, v in PROV_ALIAS.items() if k in pal), None)
    if alias:
        return alias
    provs = get(CAT + "/ObtenerProvincias")["consulta_provincieroResult"]["provinciero"]["prov"]
    mejor = max(lista(provs), key=lambda p: parecido(pal, palabras(p["np"])))
    return mejor["np"] if parecido(pal, palabras(mejor["np"])) >= 0.5 else None


def resolver_municipio(provincia: str, texto: str) -> dict:
    pal = palabras(texto)
    if not pal:
        return {"error": "falta el municipio"}
    res = get(CAT + "/ObtenerMunicipios", {"Provincia": provincia, "Municipio": max(pal, key=len)})
    res = res.get("consulta_municipieroResult", {})
    if res.get("lerr"):
        return {"error": "Catastro: " + error_cat(res["lerr"])}
    munis = lista(res.get("municipiero", {}).get("muni"))
    puntuados = sorted(((parecido(pal, palabras(m["nm"])), m["nm"]) for m in munis), reverse=True)
    if not puntuados or puntuados[0][0] < 0.5:
        return {"error": "no encuentro ese municipio en la provincia", "candidatos": [n for _, n in puntuados[:8]]}
    if len(puntuados) > 1 and puntuados[1][0] == puntuados[0][0]:
        return {"error": "hay varios municipios con ese nombre", "candidatos": [n for p, n in puntuados if p == puntuados[0][0]]}
    return {"nombre": puntuados[0][1]}


def resolver_via(provincia: str, municipio: str, calle: str, sigla: str | None) -> dict:
    trozos = calle.split()
    primera = (palabras(trozos[0]) or [""])[0] if trozos else ""
    if primera in SIGLAS and len(trozos) > 1:
        sigla = sigla or SIGLAS[primera]
        trozos = trozos[1:]
    pal = palabras(" ".join(trozos))
    if not pal:
        return {"error": "falta el nombre de la calle"}
    # La búsqueda del Catastro es «contiene»: se prueba con las palabras más
    # largas, una a una, hasta que alguna devuelva calles.
    claves = sorted({t for t in re.split(r"[^A-ZÑÇ0-9]+", mayus(" ".join(trozos))) if t and t not in CONECTORES},
                    key=len, reverse=True)
    res = {}
    for clave in claves[:3]:
        res = get(CAT + "/ObtenerCallejero", {"Provincia": provincia, "Municipio": municipio, "NomVia": clave})
        res = res.get("consulta_callejeroResult", {})
        if not res.get("lerr"):
            break
    if res.get("lerr"):
        return {"error": "Catastro: " + error_cat(res["lerr"]) + " (revisa la ñ y cómo se escribe la calle)"}
    cands = []
    for c in lista(res.get("callejero", {}).get("calle")):
        d = c.get("dir", {})
        nombres = [d.get("nv", ""), (c.get("dirine") or {}).get("deine", "")]
        p = max(parecido(pal, palabras(n)) for n in nombres if n)
        cands.append({"p": p, "tipo": d.get("tv"), "nombre": d.get("nv")})
    if not cands:
        return {"error": "el Catastro no encuentra esa calle"}
    cands.sort(key=lambda c: (c["p"], c["tipo"] == sigla), reverse=True)
    top = [c for c in cands if c["p"] == cands[0]["p"]]
    if sigla and len(top) > 1 and any(c["tipo"] == sigla for c in top):
        top = [c for c in top if c["tipo"] == sigla]
    if cands[0]["p"] < 0.5 or len(top) > 1:
        return {"error": "no sé cuál de estas calles es", "candidatos": [f"{c['tipo']} {c['nombre']}" for c in cands[:10]]}
    elegida = top[0]
    if elegida["p"] < 1:
        avisos.append(f"Calle entendida como «{elegida['tipo']} {elegida['nombre']}»: compruébalo.")
    return {"tipo": elegida["tipo"], "nombre": elegida["nombre"]}


def unidad(rcdnp: dict) -> dict:
    lourb = (rcdnp.get("dt", {}).get("locs", {}).get("lous", {}) or {}).get("lourb", {}) or {}
    loint = lourb.get("loint", {}) or {}
    debi = rcdnp.get("debi", {}) or {}
    return {
        "rc": rc_de(rcdnp.get("rc") or rcdnp.get("idbi", {}).get("rc")),
        "escalera": loint.get("es"), "planta": loint.get("pt"), "puerta": loint.get("pu"),
        "uso": debi.get("luso"), "m2_construidos": num(debi.get("sfc")),
        "participacion_pct": num(debi.get("cpt")), "anno": num(debi.get("ant")),
    }


def detalle(rc: str) -> dict:
    """Ficha completa de un inmueble (referencia de 20) o de un portal (de 14)."""
    res = get(CAT + "/Consulta_DNPRC", {"RefCat": rc}).get("consulta_dnprcResult", {})
    if res.get("lerr"):
        return {"error": "Catastro: " + error_cat(res["lerr"])}
    if "bico" not in res:
        filas = lista(res.get("lrcdnp", {}).get("rcdnp"))
        return {"unidades": [unidad(u) for u in filas], "dt": (filas or [{}])[0].get("dt", {})}
    return leer_bico(res["bico"])


def leer_bico(bico: dict) -> dict:
    bi = bico.get("bi", {})
    u = unidad({"rc": bi.get("idbi", {}).get("rc"), "dt": bi.get("dt", {}), "debi": bi.get("debi", {})})
    u["direccion"] = bi.get("ldt")
    finca = bico.get("finca", {}) or {}
    partes = []
    for c in lista(bico.get("lcons")):
        loint = (c.get("dt", {}).get("lourb", {}) or {}).get("loint", {}) or {}
        partes.append({
            "que": c.get("lcd"), "planta": loint.get("pt"), "puerta": loint.get("pu"),
            "m2": num((c.get("dfcons") or {}).get("stl")), "tipo": (c.get("dvcons") or {}).get("dtip"),
        })
    u["desglose"] = partes
    u["finca"] = {
        "tipo": finca.get("ltp"),
        "suelo_parcela_m2": num((finca.get("dff") or {}).get("ss")),
        "mapa": (finca.get("infgraf") or {}).get("igraf"),
    }
    return {"unidades": [u], "dt": bi.get("dt", {})}


def por_direccion(provincia: str, municipio: str, tipo: str, calle: str, numero: str) -> dict:
    res = get(CAT + "/Consulta_DNPLOC", {
        "Provincia": provincia, "Municipio": municipio, "Sigla": tipo, "Calle": calle, "Numero": numero,
    }).get("consulta_dnplocResult", {})
    if res.get("lerr"):
        out = {"error": f"Catastro: {error_cat(res['lerr'])} en {tipo} {calle}"}
        cerca = sorted({n.get("num", {}).get("pnp") for n in lista(res.get("numerero", {}).get("nump"))} - {None},
                       key=lambda x: int(x) if str(x).isdigit() else 0)
        if cerca:                           # el Catastro sugiere los números que sí existen cerca
            out["numeros_cercanos"] = cerca
        return out
    if "bico" in res:                       # una sola finca en el portal: viene ya completa
        return leer_bico(res["bico"])
    return {"unidades": [unidad(u) for u in lista(res.get("lrcdnp", {}).get("rcdnp"))],
            "dt": (lista(res.get("lrcdnp", {}).get("rcdnp")) or [{}])[0].get("dt", {})}


def ubicacion(rc14: str) -> dict:
    try:
        res = get(COORD, {"RefCat": rc14, "SRS": "EPSG:4326"}).get("Consulta_CPMRCResult", {})
        geo = lista(res.get("coordenadas", {}).get("coord"))[0]["geo"]
        lat, lon = round(float(geo["ycen"]), 6), round(float(geo["xcen"]), 6)
    except Exception as e:                  # sin coordenadas no se cae la ficha
        return {"error": f"{type(e).__name__}: {e}"}
    return {
        "lat": lat, "lon": lon,
        "google_maps": f"https://www.google.com/maps/search/?api=1&query={lat},{lon}",
        "street_view": f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lon}",
        "foto_fachada_catastro": FOTO.format(rc14),
    }


# ------------------------------------------------------- Cataluña: CEE + cédula

def tipo_motivo(m) -> str:
    m = mayus(m)
    if "COMPRAV" in m:
        return "venta"
    if "LLOGUER" in m or "ALQUILER" in m:
        return "alquiler"
    if "NOVA CONSTR" in m or "NUEVA CONSTR" in m:
        return "obra nueva"
    if "AJUT" in m or "AYUDA" in m:
        return "ayudas"
    return "otro"


def socrata(url: str, rc14: str, direccion: dict) -> list:
    filas = get(url, {"$where": f"starts_with(referencia_cadastral,'{rc14}')", "$limit": "500"})
    if filas or not direccion:
        return filas
    # Plan B por dirección: los conectores (y/i, de/del) cambian de idioma
    # dentro del propio registro, así que se buscan solo las palabras con peso.
    q = " ".join(t for t in palabras(direccion["calle"]) if len(t) > 2)
    campos = ({"poblacio": direccion["municipio"].title(), "numero": direccion["numero"]} if url == CEE
              else {"municipi": direccion["municipio"].title(), "numinici": direccion["numero"]})
    filas = get(url, {**campos, "$q": q, "$limit": "500"})
    if filas:
        avisos.append("El registro catalán no traía la referencia catastral: se ha buscado por dirección.")
    return filas


def caduca_cee(entrada: str, letra: str) -> str | None:
    try:
        y, m, d = (int(x) for x in entrada[:10].split("-"))
    except ValueError:
        return None
    y += 5 if letra == "G" else 10          # RD 390/2021: 10 años; con letra G, 5
    return f"{y:04d}-{m:02d}-{min(d, 28) if m == 2 else d:02d}"


def certificados(rc14, rc20, planta, puerta, direccion) -> dict:
    try:
        filas = socrata(CEE, rc14, direccion)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
    filas.sort(key=lambda f: f.get("data_entrada", ""), reverse=True)
    hoy = date.today().isoformat()
    actividad: dict = {}
    for f in filas:
        anyo = (f.get("data_entrada") or "")[:4]
        if anyo and int(anyo) >= date.today().year - 5:
            t = tipo_motivo(f.get("motiu_de_la_certificacio"))
            if t in ("venta", "alquiler"):
                actividad.setdefault(anyo, Counter())[t] += 1
    out = {
        "n_certificados_edificio": len(filas),
        "letras_edificio": dict(Counter((f.get("qualificaci_de_consum_d") or "?").strip().upper() for f in filas)),
        "certificados_para_vender_o_alquilar_por_anyo": {k: dict(v) for k, v in sorted(actividad.items())},
        "vivienda": None,
    }
    if not (rc20 or planta or puerta):
        return out
    propios = [f for f in filas if rc20 and f.get("referencia_cadastral") == rc20]
    if not propios and (planta or puerta):
        propios = [f for f in filas if coincide(f.get("pis"), f.get("porta"), planta, puerta)]
    if not propios:
        out["vivienda"] = {"consta": False}
        return out
    c = propios[0]
    letra = (c.get("qualificaci_de_consum_d") or "").strip().upper()
    caduca = caduca_cee(c.get("data_entrada") or "", letra)
    out["vivienda"] = {
        "consta": True,
        "letra_consumo": letra, "letra_emisiones": (c.get("qualificacio_d_emissions") or "").strip().upper(),
        "consumo_kwh_m2_anyo": num(c.get("energia_prim_ria_no_renovable")),
        "emisiones_kgco2_m2_anyo": num(c.get("emissions_de_co2")),
        "m2_del_certificado": num(c.get("metres_cadastre")),
        "registrado": (c.get("data_entrada") or "")[:10], "caduca_aprox": caduca,
        "vigente": bool(caduca and caduca >= hoy),
        "motivo": c.get("motiu_de_la_certificacio"),
        "fachada_transmitancia": num(c.get("valor_aillaments")), "fachada_limite_cte": num(c.get("valor_aillaments_cte")),
        "ventanas_transmitancia": num(c.get("valor_finestres")), "ventanas_limite_cte": num(c.get("valor_finestres_cte")),
        "rehabilitacion_energetica": c.get("rehabilitacio_energetica"),
        "historial": [
            {"fecha": (f.get("data_entrada") or "")[:10], "letra": (f.get("qualificaci_de_consum_d") or "").upper(),
             "motivo": tipo_motivo(f.get("motiu_de_la_certificacio"))}
            for f in propios
        ],
    }
    return out


def cedulas(rc14, rc20, planta, puerta, direccion) -> dict:
    try:
        filas = socrata(CED, rc14, direccion)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}
    filas.sort(key=lambda f: f.get("data_resolucio", ""), reverse=True)
    utiles = [num(f.get("superficie_util")) for f in filas if num(f.get("superficie_util"))]
    out = {
        "n_cedulas_edificio": len(filas),
        "superficie_util_edificio": {"min": min(utiles), "max": max(utiles)} if utiles else None,
        "vivienda": None,
    }
    if not (rc20 or planta or puerta):
        return out
    propias = [f for f in filas if rc20 and f.get("referencia_cadastral") == rc20]
    if not propias and (planta or puerta):
        propias = [f for f in filas if coincide(f.get("pis"), f.get("porta"), planta, puerta)]
    if not propias:
        out["vivienda"] = {"consta": False}
        return out
    c = propias[0]
    fin = (c.get("data_fi_vigencia") or "")[:10]
    estado = (c.get("estat_cedula") or "").strip()
    out["vivienda"] = {
        "consta": True, "numero": c.get("numero_cedula"), "estado": estado,
        "concedida": (c.get("data_resolucio") or "")[:10], "fin_vigencia": fin or None,
        "vigente": bool(fin and fin >= date.today().isoformat() and estado.lower() == "atorgada"),
        "superficie_util_m2": num(c.get("superficie_util")), "ocupacion_maxima": num(c.get("num_persones")),
    }
    return out


# ---------------------------------------------------------------------- main

def ficha(a) -> dict:
    planta, puerta = (a.planta or "").strip(), (a.puerta or "").strip()
    salida: dict = {"consultado": date.today().isoformat(), "pedido": {k: v for k, v in vars(a).items() if v}}

    if a.rc:
        rc = re.sub(r"[^0-9A-Z]", "", a.rc.upper())
        if len(rc) not in (14, 18, 20):
            return {**salida, "error": "la referencia catastral tiene 14 o 20 caracteres"}
        cat = detalle(rc)
    else:
        if not (a.municipio and a.calle and a.numero):
            return {**salida, "error": "hace falta municipio, calle y número (o la referencia catastral)"}
        prov_txt = a.provincia or a.municipio
        provincia = resolver_provincia(prov_txt)
        if provincia is None and set(palabras(prov_txt)) & FORALES:
            return {**salida, "error": "País Vasco y Navarra tienen su propio catastro (foral); este no los cubre"}
        if provincia is None:
            return {**salida, "error": "no sé de qué provincia es: dímelo con --provincia"}
        m = resolver_municipio(provincia, a.municipio)
        if "error" in m:
            return {**salida, **m}
        v = resolver_via(provincia, m["nombre"], a.calle, (a.sigla or "").upper() or None)
        if "error" in v:
            return {**salida, **v}
        numero = re.match(r"\d+", str(a.numero))
        if not numero:
            return {**salida, "error": "el número del portal tiene que ser un número"}
        if numero.group() != str(a.numero).strip():
            avisos.append(f"El Catastro solo busca el número {numero.group()}; lo demás («{a.numero}») se ha ignorado.")
        cat = por_direccion(provincia, m["nombre"], v["tipo"], v["nombre"], numero.group())

    if "error" in cat:
        return {**salida, **cat}
    unidades = cat["unidades"]
    if not unidades:
        return {**salida, "error": "el Catastro no devuelve inmuebles para ese portal"}
    rc14 = unidades[0]["rc"][:14]

    # El inmueble pedido: el de la referencia de 20, o el de planta y puerta.
    if a.rc and len(re.sub(r"[^0-9A-Z]", "", a.rc.upper())) >= 18:
        objetivo = unidades
    elif planta or puerta:
        objetivo = [u for u in unidades if coincide(u["planta"], u["puerta"], planta, puerta)]
    else:
        objetivo = unidades if len(unidades) == 1 else []
    inmueble = None
    if len(objetivo) == 1:
        if "desglose" in objetivo[0]:
            inmueble = objetivo[0]
        else:
            d = detalle(objetivo[0]["rc"])
            inmueble = (d.get("unidades") or [objetivo[0]])[0]
    elif len(objetivo) > 1:
        avisos.append("Hay varios inmuebles con esa planta y puerta (¿escaleras distintas?): elige uno por su referencia.")
    elif planta or puerta:
        avisos.append("No hay ningún inmueble con esa planta y puerta en el Catastro: mira la lista del portal.")

    # Datos del portal (parcela y mapa) aunque no se haya pedido un piso.
    finca = (inmueble or {}).get("finca")
    if finca is None:
        primero = detalle(unidades[0]["rc"])
        finca = (primero.get("unidades") or [{}])[0].get("finca") if "error" not in primero else None
    dt = cat.get("dt") or {}
    lourb = (dt.get("locs", {}).get("lous", {}) or {}).get("lourb", {}) or {}
    dir_cat = lourb.get("dir", {}) or {}
    cod_prov = num((dt.get("loine") or {}).get("cp"))
    usos = Counter(u["uso"] or "?" for u in unidades)
    annos = Counter(u["anno"] for u in unidades if u["anno"])
    salida["catastro"] = {
        "portal": f"{dir_cat.get('tv', '')} {dir_cat.get('nv', '')} {dir_cat.get('pnp', '')}".strip(),
        "codigo_postal": lourb.get("dp"), "municipio": dt.get("nm"), "provincia": dt.get("np"),
        "rc_portal": rc14, "anno_construccion": annos.most_common(1)[0][0] if annos else None,
        "n_inmuebles": len(unidades), "usos": dict(usos), "finca": finca,
        "inmuebles": [
            f"{u['rc']} · esc {u['escalera'] or '-'} · planta {u['planta']} · puerta {u['puerta']} · {u['uso']} · {u['m2_construidos']} m²"
            for u in unidades[:120]
        ] + ([f"... y {len(unidades) - 120} más"] if len(unidades) > 120 else []),
        "inmueble_pedido": inmueble,
    }
    salida["ubicacion"] = ubicacion(rc14)

    if cod_prov in CATALUNYA:
        direccion = {"calle": dir_cat.get("nv", ""), "numero": str(dir_cat.get("pnp", "")), "municipio": dt.get("nm", "")}
        rc20 = (inmueble or {}).get("rc")
        planta_cee = planta or norm_planta((inmueble or {}).get("planta"))
        puerta_cee = puerta or norm_puerta((inmueble or {}).get("puerta"))
        salida["certificado_energetico"] = certificados(rc14, rc20, planta_cee, puerta_cee, direccion)
        salida["cedula_habitabilidad"] = cedulas(rc14, rc20, planta_cee, puerta_cee, direccion)
    else:
        salida["certificado_energetico"] = {"no_aplica": "Solo Cataluña publica este registro en abierto."}
        salida["cedula_habitabilidad"] = {"no_aplica": "La cédula solo existe así en algunas comunidades; este registro abierto es de Cataluña."}

    salida["avisos"] = avisos
    salida["fuentes"] = [
        "Catastro, Sede Electrónica (servicios libres OVC)",
        *(["Registre de certificats d'eficiència energètica (ICAEN, dades obertes)",
           "Registre de cèdules d'habitabilitat (Agència de l'Habitatge de Catalunya, dades obertes)"]
          if cod_prov in CATALUNYA else []),
    ]
    return salida


def main() -> int:
    p = argparse.ArgumentParser(description="Lo que dicen los registros públicos de un inmueble en España.")
    p.add_argument("--rc", help="referencia catastral (14 caracteres = portal, 20 = inmueble)")
    p.add_argument("--municipio")
    p.add_argument("--provincia", help="si no se pone, se usa el municipio")
    p.add_argument("--calle", help="nombre de la calle; puede empezar por «calle», «avenida»...")
    p.add_argument("--sigla", help="tipo de vía del Catastro: CL, AV, PZ, PS...")
    p.add_argument("--numero")
    p.add_argument("--planta")
    p.add_argument("--puerta")
    a = p.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        out = ficha(a)
    except urllib.error.URLError as e:
        out = {"error": f"sin conexión con el registro: {e.reason}",
               "pista": "Si estás en claude.ai: Settings → Capabilities → activa «Allow network egress». "
                        "En planes Team o Enterprise lo decide el administrador: tiene que permitir "
                        "ovc.catastro.meh.es y analisi.transparenciacatalunya.cat"}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 1 if "error" in out else 0


if __name__ == "__main__":
    sys.exit(main())
