// Muro de videos: se reproducen solos, en silencio y en bucle cuando aparecen en pantalla, y se
// pausan al salir. El botón de cada video lo pone con sonido desde el inicio y silencia los demás.
// Quien pide movimiento reducido los ve quietos (con su portada) y los inicia con el botón.
const reducido = matchMedia('(prefers-reduced-motion: reduce)').matches;
const videos = [...document.querySelectorAll('.muro video')];

const cargar = (v) => {
  if (!v.getAttribute('src')) v.src = v.dataset.src;
};

const vigia = new IntersectionObserver((entradas) => {
  for (const { target: v, isIntersecting } of entradas) {
    if (isIntersecting) {
      cargar(v);
      if (!reducido || !v.muted) v.play().catch(() => {});
    } else {
      v.pause();
    }
  }
}, { threshold: 0.35 });
videos.forEach((v) => vigia.observe(v));

for (const boton of document.querySelectorAll('.muro__sonido')) {
  boton.addEventListener('click', () => {
    const v = boton.closest('.muro__item').querySelector('video');
    const encender = v.muted;
    for (const otro of document.querySelectorAll('.muro__sonido')) otro.setAttribute('aria-pressed', 'false');
    videos.forEach((otro) => { otro.muted = true; });
    cargar(v);
    if (encender) {
      v.muted = false;
      v.currentTime = 0;
      boton.setAttribute('aria-pressed', 'true');
      v.play().catch(() => {});
    } else if (reducido) {
      v.pause();
    }
  });
}
