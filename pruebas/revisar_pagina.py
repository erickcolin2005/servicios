"""Revisa la página antes de publicarla: lo que la marca y la evidencia de EAx no permiten.

Cada regla devuelve los problemas que encuentra, con su código al inicio. Las reglas salen de:
  - el repositorio de EAx: palabras prohibidas (EAx_MARCA_PERSONAL.MD), frases prohibidas
    (EAx_POSICIONAMIENTO.md §5), jerga (regla del 2026-08-17), cifras solo verificadas
    (REF_casos.md), precios solo del Playbook (por eso aquí no va ninguno) y el WhatsApp de D26;
  - el control contra el diseño genérico de xloop: colores solo desde los tokens, foco visible
    para teclado y movimiento con alternativa reducida.

    python pruebas/revisar_pagina.py docs

Sale con 0 si no hay problemas y con 1 si hay alguno.
"""
from __future__ import annotations

import hashlib
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

BASE = "https://erickcolin2005.github.io/servicios/"
WHATSAPP = "573103761189"  # D26, desde el 2026-09-30
NUMEROS_VIEJOS = ["3205065780", "320 506 5780"]
# El único resultado con cifra verificada: −40 % en tiempos de respuesta de Jabones Rocío (REF_casos, caso 1).
PORCENTAJES_PERMITIDOS = {"40"}
PROHIBIDAS = [
    # marca
    "revolucion", "revolucionario", "futuro", "magia", "magico", "hack definitivo", "secreto",
    "ia lo cambia todo", "disruptivo", "game changer", "game-changer",
    # posicionamiento
    "agencia", "experto en inteligencia artificial", "experto en ia", "soluciones integrales", "360",
    "todos los tamanos",
    # jerga que se dice en español llano
    "retail", "triage", "reporteria", "ticket", "incidente", "agente conversacional", "retrabajo",
    "workflow", "lead", "leads", "funnel", "embudo",
]
# Personas de casos cuyo permiso para nombrarlas no está confirmado (REF_casos, caso 5).
# Van como huella (sha256 de la palabra en minúsculas y sin tildes): el repositorio es público
# y el nombre no se escribe aquí.
NOMBRES_PRIVADOS = {"9e88b067408182d0bd525120e9ba2607e19b0dfa17b48582d2d405fc52dc4a1a"}
LIMITE_VIDEO = 8_000_000  # bytes: un minuto a 720x900 pesa unos 4 MB
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB = re.compile(r"\brgba?\(")


def sin_tildes(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


class Lector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.texto: list[str] = []
        self.etiquetas: list[tuple[str, dict[str, str]]] = []
        self.lang = ""
        self.titulo = ""
        self._en_titulo = False
        self._ignorar = 0

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        self.etiquetas.append((tag, a))
        if tag == "html":
            self.lang = a.get("lang", "")
        if tag == "title":
            self._en_titulo = True
        if tag in ("script", "style"):
            self._ignorar += 1
        for clave in ("alt", "aria-label", "title"):
            if a.get(clave):
                self.texto.append(a[clave])
        if tag == "meta" and a.get("content") and (a.get("name") or a.get("property", "")).startswith(("description", "og:t", "og:d")):
            self.texto.append(a["content"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._en_titulo = False
        if tag in ("script", "style"):
            self._ignorar -= 1

    def handle_data(self, data):
        if self._en_titulo:
            self.titulo += data
        if not self._ignorar:
            self.texto.append(data)


def fuera_de_root(css: str) -> str:
    """El CSS sin el bloque :root, que es la única capa donde se escriben colores."""
    return re.sub(r":root\s*\{[^}]*\}", "", css)


def local(carpeta: Path, ruta: str) -> Path:
    return carpeta / ruta.split("#")[0].split("?")[0]


def es_externa(ruta: str) -> bool:
    return ruta.startswith(("http://", "https://", "//"))


def revisar(carpeta: Path) -> list[str]:
    carpeta = Path(carpeta)
    html_crudo = (carpeta / "index.html").read_text(encoding="utf-8")
    hojas = [p for p in carpeta.glob("*.css")]
    css = "\n".join(p.read_text(encoding="utf-8") for p in hojas)
    lector = Lector()
    lector.feed(html_crudo)
    texto = re.sub(r"\s+", " ", " ".join(lector.texto))
    plano = sin_tildes(texto)
    problemas: list[str] = []

    # R01 · lenguaje de la marca
    for palabra in PROHIBIDAS:
        if re.search(rf"(?<![\w-]){re.escape(palabra)}(?![\w-])", plano):
            problemas.append(f"R01 palabra vetada por la marca: «{palabra}»")

    # R02 · precios: solo salen del Playbook, y esta página no los muestra
    for m in re.finditer(r"\$\s?\d|\bCOP\b|\bUSD\b|\bpesos\b", texto):
        problemas.append(f"R02 precio en la página: «{texto[max(0, m.start() - 20):m.end() + 20]}»")

    # R03 · porcentajes: solo los verificados en REF_casos
    for m in re.finditer(r"(\d+(?:[.,]\d+)?)\s?%", texto):
        if m.group(1) not in PORCENTAJES_PERMITIDOS:
            problemas.append(f"R03 porcentaje sin respaldo en REF_casos: «{m.group(0)}»")

    # R04 · WhatsApp: el número vigente en todos los enlaces y ninguno viejo
    enlaces = [a.get("href", "") for t, a in lector.etiquetas if t == "a"]
    wa = [h for h in enlaces if "wa.me" in h or "whatsapp.com" in h]
    if not wa:
        problemas.append("R04 no hay ningún enlace a WhatsApp")
    for h in wa:
        if not re.match(rf"https://wa\.me/{WHATSAPP}(\?|$)", h):
            problemas.append(f"R04 enlace de WhatsApp a otro número: {h}")
    for viejo in NUMEROS_VIEJOS:
        if viejo in html_crudo or viejo in css:
            problemas.append(f"R04 aparece el número viejo {viejo}")

    # R05 · color: solo en los tokens de :root
    for m in HEX.finditer(fuera_de_root(css)):
        problemas.append(f"R05 color escrito fuera de los tokens: {m.group(0)}")
    if RGB.search(fuera_de_root(css)):
        problemas.append("R05 rgb()/rgba() escrito fuera de los tokens")
    html_sin_tema = re.sub(r'<meta name="theme-color"[^>]*>', "", html_crudo)
    for m in HEX.finditer(re.sub(r"<style[\s\S]*?</style>", "", html_sin_tema)):
        problemas.append(f"R05 color escrito en el HTML: {m.group(0)}")

    # R06 · imágenes: texto alternativo, tamaño declarado y archivo presente
    for t, a in lector.etiquetas:
        if t != "img":
            continue
        src = a.get("src", "")
        if not a.get("alt", "").strip():
            problemas.append(f"R06 imagen sin texto alternativo: {src}")
        if not (a.get("width") and a.get("height")):
            problemas.append(f"R06 imagen sin ancho y alto: {src}")
        if not es_externa(src) and not local(carpeta, src).is_file():
            problemas.append(f"R06 imagen que no existe: {src}")

    # R07 · recursos: los locales existen y nada se carga de otro servidor
    for t, a in lector.etiquetas:
        for clave in ("href", "src", "data-src", "poster"):
            ruta = a.get(clave, "")
            if not ruta or ruta.startswith(("#", "mailto:", "tel:")):
                continue
            if es_externa(ruta):
                if t in ("script", "img") or (t == "link" and a.get("rel") in ("stylesheet", "preload", "icon")):
                    problemas.append(f"R07 recurso cargado de otro servidor: {ruta}")
            elif not local(carpeta, ruta).exists():
                problemas.append(f"R07 enlace a un archivo que no existe: {ruta}")
    if re.search(r"@import|url\(\s*['\"]?https?:", css):
        problemas.append("R07 el CSS carga algo de otro servidor")

    # R08 · personas que no se pueden nombrar
    palabras = set(re.findall(r"[a-zñ]+", plano + " " + sin_tildes(html_crudo)))
    for palabra in palabras:
        huella = hashlib.sha256(palabra.encode()).hexdigest()
        if huella in NOMBRES_PRIVADOS:
            problemas.append(f"R08 aparece el nombre de una persona sin permiso (huella {huella[:10]})")

    # R09 · fuentes alojadas en el proyecto, con su licencia
    for ruta in re.findall(r"url\(\s*['\"]?([^'\")]+)", css):
        if not es_externa(ruta) and not (carpeta / ruta).is_file():
            problemas.append(f"R09 fuente que no existe: {ruta}")
    if not (carpeta / "fuentes" / "LICENCIAS.txt").is_file():
        problemas.append("R09 falta fuentes/LICENCIAS.txt")

    # R10 · metadatos para buscadores y para la vista previa al compartir por WhatsApp
    metas = {(a.get("name") or a.get("property")): a.get("content", "") for t, a in lector.etiquetas if t == "meta"}
    if lector.lang != "es":
        problemas.append("R10 <html> sin lang=\"es\"")
    if not lector.titulo.strip():
        problemas.append("R10 falta el <title>")
    for clave in ("viewport", "description", "og:title", "og:description", "og:image", "og:url"):
        if not metas.get(clave):
            problemas.append(f"R10 falta la etiqueta {clave}")
    imagen = metas.get("og:image", "")
    if imagen and not (imagen.startswith(BASE) and (carpeta / imagen[len(BASE):]).is_file()):
        problemas.append(f"R10 og:image no es una imagen de esta página publicada: {imagen}")

    # R11 · foco visible para quien navega con teclado
    if ":focus-visible" not in css:
        problemas.append("R11 falta :focus-visible")

    # R12 · movimiento: propiedades nombradas y alternativa para quien lo pide reducido
    if re.search(r"transition\s*:\s*all\b", css):
        problemas.append("R12 transition: all")
    if re.search(r"\b(transition|animation)\s*:", css) and "prefers-reduced-motion" not in css:
        problemas.append("R12 hay movimiento sin prefers-reduced-motion")

    # R13 · los enlaces que abren otra pestaña no le dan acceso a la página original
    for t, a in lector.etiquetas:
        if t == "a" and a.get("target") == "_blank" and "noopener" not in a.get("rel", ""):
            problemas.append(f"R13 target=_blank sin rel=noopener: {a.get('href')}")

    # R14 · videos: livianos, en silencio hasta que se pida el sonido, con portada y descripción,
    # y sin reproducirse solos para quien pide movimiento reducido
    videos = [a for t, a in lector.etiquetas if t == "video"]
    for a in videos:
        fuente = a.get("data-src") or a.get("src", "")
        nombre = fuente or "(sin archivo)"
        for clave in ("muted", "playsinline"):
            if clave not in a:
                problemas.append(f"R14 video sin {clave}: {nombre}")
        if a.get("preload") != "none":
            problemas.append(f"R14 video que se descarga antes de verse (preload): {nombre}")
        if not a.get("aria-label", "").strip():
            problemas.append(f"R14 video sin descripción (aria-label): {nombre}")
        if not (a.get("poster") and local(carpeta, a["poster"]).is_file()):
            problemas.append(f"R14 video sin portada: {nombre}")
        archivo = local(carpeta, fuente) if fuente and not es_externa(fuente) else None
        if archivo is None or not archivo.is_file():
            problemas.append(f"R14 video que no existe: {nombre}")
        elif archivo.stat().st_size > LIMITE_VIDEO:
            problemas.append(f"R14 video de más de {LIMITE_VIDEO // 1_000_000} MB: {nombre}")
    if videos:
        guiones = " ".join((carpeta / a["src"]).read_text(encoding="utf-8") for t, a in lector.etiquetas
                           if t == "script" and a.get("src") and not es_externa(a["src"]) and (carpeta / a["src"]).is_file())
        if "prefers-reduced-motion" not in guiones:
            problemas.append("R14 los videos se reproducen solos sin respetar prefers-reduced-motion")

    return problemas


if __name__ == "__main__":
    carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else "docs")
    encontrados = revisar(carpeta)
    for p in encontrados:
        print(p)
    print(f"{len(encontrados)} problemas" if encontrados else "La página pasa las 14 reglas")
    sys.exit(1 if encontrados else 0)
