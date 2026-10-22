"""La página publicada pasa la revisión, y cada regla atrapa lo que dice atrapar.

Las pruebas de mutación copian la página, le meten el defecto a propósito y exigen que la
regla que corresponde lo marque: una regla que no puede ponerse en rojo no revisa nada.
"""
import hashlib
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import revisar_pagina  # noqa: E402
from revisar_pagina import revisar  # noqa: E402

DOCS = Path(__file__).resolve().parent.parent / "docs"


class LaPagina(unittest.TestCase):
    def test_pasa_todas_las_reglas(self):
        self.assertEqual(revisar(DOCS), [])

    def test_tiene_los_cuatro_servicios_y_los_tres_casos_de_implementacion(self):
        html = (DOCS / "index.html").read_text(encoding="utf-8")
        for id_ in ("implementacion", "diagnostico", "capacitacion", "consultoria"):
            self.assertIn(f'id="{id_}"', html)
        for sitio in ("jabonesrocio.com.co", "sosnaturalcolombia.com", "verdevivoessentials.com"):
            self.assertIn(f"https://{sitio}", html)


class CadaReglaAtrapaSuDefecto(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.copia = self.dir / "docs"
        shutil.copytree(DOCS, self.copia)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def mutar(self, archivo, cambio):
        ruta = self.copia / archivo
        original = ruta.read_text(encoding="utf-8")
        nuevo = cambio(original)
        self.assertNotEqual(original, nuevo, "la mutación no cambió nada")
        ruta.write_text(nuevo, encoding="utf-8")

    def marca(self, codigo):
        problemas = revisar(self.copia)
        self.assertTrue(any(p.startswith(codigo) for p in problemas), f"{codigo} no se puso en rojo: {problemas}")

    def antes_del_cierre(self, texto):
        return lambda h: h.replace("</main>", f"<p>{texto}</p></main>", 1)

    def test_r01_palabra_vetada(self):
        self.mutar("index.html", self.antes_del_cierre("Una revolución para tu negocio"))
        self.marca("R01")

    def test_r01_jerga(self):
        self.mutar("index.html", self.antes_del_cierre("Te ayudamos con tu workflow"))
        self.marca("R01")

    def test_r02_precio(self):
        self.mutar("index.html", self.antes_del_cierre("Desde $1.500.000"))
        self.marca("R02")

    def test_r03_cifra_sin_respaldo(self):
        self.mutar("index.html", self.antes_del_cierre("Las ventas subieron 70 %"))
        self.marca("R03")

    def test_r04_numero_viejo(self):
        self.mutar("index.html", lambda h: h.replace("573103761189", "573205065780", 1))
        self.marca("R04")

    def test_r05_color_fuera_de_los_tokens(self):
        self.mutar("estilos.css", lambda c: c + "\n.extra { color: #123456; }\n")
        self.marca("R05")

    def test_r06_imagen_sin_texto_alternativo(self):
        self.mutar("index.html", lambda h: re.sub(r'alt="[^"]+"', 'alt=""', h, count=1))
        self.marca("R06")

    def test_r07_recurso_de_otro_servidor(self):
        self.mutar("index.html", lambda h: h.replace("</head>", '<script src="https://cdn.example.com/x.js"></script></head>', 1))
        self.marca("R07")

    def test_r08_nombre_sin_permiso(self):
        # Con un nombre de prueba: el real no se escribe en un repositorio público.
        huella = hashlib.sha256("clientadeprueba".encode()).hexdigest()
        revisar_pagina.NOMBRES_PRIVADOS.add(huella)
        try:
            self.mutar("index.html", self.antes_del_cierre("Clientadeprueba aprendió a usar la IA"))
            self.marca("R08")
        finally:
            revisar_pagina.NOMBRES_PRIVADOS.discard(huella)

    def test_r10_vista_previa_sin_imagen(self):
        self.mutar("index.html", lambda h: re.sub(r'<meta property="og:image"[^>]*>', "", h, count=1))
        self.marca("R10")

    def test_r11_sin_foco_visible(self):
        self.mutar("estilos.css", lambda c: c.replace(":focus-visible", ":focus"))
        self.marca("R11")

    def test_r12_transicion_de_todo(self):
        self.mutar("estilos.css", lambda c: c + "\n.extra { transition: all 0.3s; }\n")
        self.marca("R12")

    def test_r13_pestana_nueva_sin_noopener(self):
        self.mutar("index.html", lambda h: h.replace('rel="noopener"', 'rel="external"', 1))
        self.marca("R13")


if __name__ == "__main__":
    unittest.main()
