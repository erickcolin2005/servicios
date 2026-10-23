// Movimiento con función, nada de adorno: las cifras suben hasta su valor cuando aparecen en
// pantalla, y una línea neón recorre la carpeta de EAx como la IA en el video 01.
// Sin JavaScript, o para quien pide movimiento reducido, todo se ve quieto y con su valor final:
// el número escrito en la página es siempre el real, y la animación solo llega hasta él.
// Va dentro de un bloque: videos.js también declara `reducido` y comparten el ámbito global.
{
const reducido = matchMedia('(prefers-reduced-motion: reduce)').matches;

const contar = (el) => {
  const hasta = Number(el.dataset.hasta);
  const final = el.textContent;
  const molde = final.replace(String(hasta), '{n}');
  const inicio = performance.now();
  const dura = 1200;
  const paso = (ahora) => {
    const t = Math.min(1, (ahora - inicio) / dura);
    const suave = 1 - (1 - t) ** 3;
    el.textContent = t < 1 ? molde.replace('{n}', Math.round(hasta * suave)) : final;
    if (t < 1) requestAnimationFrame(paso);
  };
  requestAnimationFrame(paso);
};

if (!reducido && 'IntersectionObserver' in window) {
  const vigia = new IntersectionObserver((entradas) => {
    for (const { target, isIntersecting } of entradas) {
      if (!isIntersecting) continue;
      vigia.unobserve(target);
      if (target.dataset.hasta) contar(target);
      else target.classList.add('leyendo');
    }
  }, { threshold: 0.6 });

  document.querySelectorAll('[data-hasta]').forEach((el) => vigia.observe(el));
  const arbol = document.querySelector('.arbol');
  if (arbol) {
    arbol.querySelectorAll('li').forEach((li, i) => li.style.setProperty('--i', i));
    vigia.observe(arbol);
  }
}
}
