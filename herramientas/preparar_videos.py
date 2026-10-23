"""Pasa los reels aprobados de EAx a versiones livianas para la página, con su portada.

Los originales (1080x1350, 25-35 MB) viven en EAx_MARCA_PERSONAL/02_PRODUCCION/REMOTION/VIDEOS/.
Aquí salen a 720x900 (unos 3-6 MB) con el índice al inicio, para que el celular empiece a
reproducir sin bajar el archivo entero. Solo entran videos que Erick ya aprobó y que llevan
los datos de clientes difuminados dentro del video.

    python herramientas/preparar_videos.py
    (FFMPEG=<ruta> si no se usa el ffmpeg que trae Remotion)
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

EAX = Path("E:/CLAUDE/PROYECTOS/EAx_MARCA_PERSONAL")
FFMPEG = os.environ.get(
    "FFMPEG", str(EAX / "02_PRODUCCION/REMOTION/eax-video/node_modules/@remotion/compositor-win32-x64-msvc/ffmpeg.exe"))
ORIGEN = EAX / "02_PRODUCCION/REMOTION/VIDEOS"
SALIDA = Path(__file__).resolve().parent.parent / "docs" / "video"

# nombre en la página: (carpeta del reel aprobado, segundo que se usa de portada)
VIDEOS = {
    "en-un-minuto": ("BR-01", 0.5),       # aprobado por Erick el 2026-10-22
    "donde-cae-el-pedido": ("DM-02", 4.0),  # visto bueno de Erick el 2026-09-27
    "el-panel-por-dentro": ("DM-03", 8.0),  # visto bueno de Erick el 2026-09-27
    "dos-tiendas-con-carrito": ("DM-01", 0.0),  # visto bueno de Erick el 2026-09-27
    # Caso EAx: hechos en código (Remotion, src/piezas/CE_caso_eax), sin voz ni datos de clientes.
    # Pedidos por Erick el 2026-10-22; se publican cuando él los vea.
    "la-carpeta": ("CE-01", 2.6),
    "las-decisiones": ("CE-02", 2.0),
    "el-envio-con-frenos": ("CE-03", 2.6),
    "en-tu-negocio": ("CE-04", 4.0),
}


def correr(*args: str) -> None:
    subprocess.run([FFMPEG, "-v", "error", "-y", *args], check=True)


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    for nombre, (carpeta, segundo) in VIDEOS.items():
        fuente = ORIGEN / carpeta / "reel_feed.mp4"
        video = SALIDA / f"{nombre}.mp4"
        correr("-i", str(fuente), "-vf", "scale=720:900", "-c:v", "libx264", "-preset", "slow", "-crf", "27",
               "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
               "-c:a", "aac", "-b:a", "96k", str(video))
        with tempfile.TemporaryDirectory() as tmp:
            cuadro = Path(tmp) / "cuadro.jpg"
            correr("-ss", str(segundo), "-i", str(fuente), "-frames:v", "1", "-vf", "scale=720:900", "-q:v", "2", str(cuadro))
            with Image.open(cuadro) as img:
                img.convert("RGB").save(SALIDA / f"{nombre}.webp", "WEBP", quality=80, method=6)
        print(f"{nombre}: {video.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
