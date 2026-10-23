# Portafolio de servicios de EAx

Página pública con los cuatro servicios de EAx (implementación, diagnóstico, capacitación y consultoría) y sus casos reales, para mandarla por WhatsApp a quien pregunta qué hacemos.

- **Dirección:** https://erickcolin2005.github.io/servicios/
- **Qué se publica:** solo la carpeta `docs/` (GitHub Pages, rama `main`, carpeta `/docs`). Es HTML y CSS, con dos scripts cortos (`videos.js` para los videos y `movimiento.js` para las cifras que suben y la línea que recorre la carpeta), sin nada cargado de otro servidor.

## Cómo se cambia

1. Se edita `docs/index.html` (textos) o `docs/estilos.css` (diseño; los colores solo en `:root`).
2. Se revisa: `npm test` (o `python -m unittest discover -s pruebas -v`). La revisión dice qué regla rompe cada cambio.
3. Si las tiendas cambiaron: `npm run capturas` vuelve a sacar sus imágenes. Si cambió la portada: `npm run vista-previa` saca la imagen que muestra WhatsApp al compartir el enlace. Si cambia un video aprobado: `python herramientas/preparar_videos.py` saca su versión liviana (720x900) y su portada. Los cuatro del caso EAx se hacen con código en el proyecto de Remotion de EAx (`02_PRODUCCION/REMOTION/eax-video`, composiciones `CE-01` a `CE-04`).
4. Se sube a `main`; GitHub Pages lo publica en uno o dos minutos.

Requiere Python 3.10 o más para la revisión, y Node con `npm install` y Google Chrome para las capturas.

## Qué revisa `pruebas/revisar_pagina.py`

| Regla | Qué no deja pasar |
|---|---|
| R01 | Palabras que la marca no usa y jerga |
| R02 | Precios (se dan por WhatsApp, desde el Playbook) |
| R03 | Porcentajes que no estén verificados (hoy solo el 40 % de Jabones Rocío) |
| R04 | Un WhatsApp que no sea el 310 376 1189 |
| R05 | Colores escritos fuera de los tokens de `:root` |
| R06 | Imágenes sin texto alternativo, sin tamaño o que no existen |
| R07 | Archivos que no existen o recursos cargados de otro servidor |
| R08 | Nombres de personas sin permiso para nombrarlas |
| R09 | Fuentes que faltan o sin licencia |
| R10 | Metadatos y la imagen para compartir |
| R11 | Falta del foco visible para quien navega con teclado |
| R12 | Movimiento sin alternativa reducida, una animación sin fin que no se apaga para quien pide menos movimiento, o `transition: all` |
| R13 | Enlaces a otra pestaña sin `rel="noopener"` |
| R14 | Videos sin portada, sin descripción, que se descargan antes de verse, de más de 8 MB, o un script que los reproduce sin respetar a quien pide menos movimiento |
| R15 | Una cifra que sube hasta un número distinto del que está escrito en la página (sin JavaScript se ve el escrito) |

Cada regla tiene una prueba que le mete su defecto a propósito y exige que la marque.
