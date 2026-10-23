// Muros de videos: se reproducen solos, en silencio y en bucle cuando aparecen en pantalla, y se
// pausan al salir. En el primer muro, el botón de cada video lo pone con sonido desde el inicio y
// silencia los demás. Los del caso EAx no tienen voz: su botón los pausa o los vuelve a poner.
// Quien pide movimiento reducido los ve quietos (con su portada) y los inicia con el botón.
const reducido = matchMedia('(prefers-reduced-motion: reduce)').matches;
const videos = [...document.querySelectorAll('video[data-src]')];

const cargar = (v) => {
  if (!v.getAttribute('src')) v.src = v.dataset.src;
};

// Se reproduce solo si nadie lo pausó y, con movimiento reducido, si la persona lo pidió.
const puedeSonar = (v) => !v.dataset.pausado && (!reducido || !v.muted || v.dataset.pedido === '1');

const vigia = new IntersectionObserver((entradas) => {
  for (const { target: v, isIntersecting } of entradas) {
    if (isIntersecting) {
      cargar(v);
      if (puedeSonar(v)) v.play().catch(() => {});
    } else {
      v.pause();
    }
  }
}, { threshold: 0.35 });
videos.forEach((v) => vigia.observe(v));

for (const boton of document.querySelectorAll('.muro__sonido:not(.muro__pausa)')) {
  boton.addEventListener('click', () => {
    const item = boton.closest('.muro__item');
    const v = item.querySelector('video');
    const encender = v.muted;
    for (const otro of document.querySelectorAll('.muro__sonido:not(.muro__pausa)')) otro.setAttribute('aria-pressed', 'false');
    document.querySelectorAll('.muro__item.sonando').forEach((otro) => otro.classList.remove('sonando'));
    videos.forEach((otro) => { otro.muted = true; });
    cargar(v);
    if (encender) {
      v.muted = false;
      v.currentTime = 0;
      boton.setAttribute('aria-pressed', 'true');
      item.classList.add('sonando');
      v.play().catch(() => {});
    } else if (reducido) {
      v.pause();
    }
  });
}

for (const boton of document.querySelectorAll('.muro__pausa')) {
  const v = boton.closest('.muro__item').querySelector('video');
  if (reducido) boton.setAttribute('aria-pressed', 'true');
  boton.addEventListener('click', () => {
    cargar(v);
    if (boton.getAttribute('aria-pressed') === 'true') {
      delete v.dataset.pausado;
      v.dataset.pedido = '1';
      boton.setAttribute('aria-pressed', 'false');
      v.play().catch(() => {});
    } else {
      v.dataset.pausado = '1';
      boton.setAttribute('aria-pressed', 'true');
      v.pause();
    }
  });
}
