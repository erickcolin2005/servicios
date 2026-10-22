// Captura las tiendas de los casos como las ve un cliente, después de cerrar los avisos
// que salen al entrar (bienvenida, cookies, cierres por temporada).
// Solo páginas públicas de la tienda: nunca paneles ni cuentas, que traen datos de personas.
// Uso: npm run capturas   (CHROME=<ruta> si Chrome no está en la ruta de siempre)
import puppeteer from 'puppeteer-core';

const CHROME = process.env.CHROME ?? 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const TIENDAS = [
  ['jabones-rocio', 'https://jabonesrocio.com.co'],
  ['sos-natural', 'https://sosnaturalcolombia.com/productos-terminados/jabones-solidos'],
  ['verde-vivo-producto', 'https://verdevivoessentials.com/catalogo/shampoo-solido-manzanilla/'],
];

// Quita lo que tapa la tienda: ventanas que ocupan buena parte de la pantalla y avisos de cookies.
// El botón flotante de WhatsApp se queda: es parte de cómo vende la tienda.
function quitarAvisos() {
  const area = innerWidth * innerHeight;
  for (const el of document.querySelectorAll('body *')) {
    const s = getComputedStyle(el);
    if (s.position !== 'fixed' && s.position !== 'sticky') continue;
    const r = el.getBoundingClientRect();
    const tapa = r.width * r.height > area * 0.25 && s.position === 'fixed';
    const dialogo = el.getAttribute('role') === 'dialog' || el.getAttribute('aria-modal') === 'true';
    const cookies = /cookies/i.test(el.textContent ?? '') && r.height < innerHeight * 0.5;
    if (tapa || dialogo || cookies) el.remove();
  }
  for (const el of [document.documentElement, document.body]) {
    el.style.overflow = 'auto';
    el.style.filter = 'none';
  }
}

const navegador = await puppeteer.launch({ executablePath: CHROME, headless: true });
try {
  for (const [nombre, url] of TIENDAS) {
    const pagina = await navegador.newPage();
    await pagina.setViewport({ width: 1280, height: 800 });
    await pagina.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });
    await new Promise((r) => setTimeout(r, 2500));
    await pagina.keyboard.press('Escape');
    await pagina.evaluate(quitarAvisos);
    await new Promise((r) => setTimeout(r, 800));
    await pagina.screenshot({ path: `docs/img/${nombre}.webp`, type: 'webp', quality: 78 });
    console.log(nombre, url);
    await pagina.close();
  }
} finally {
  await navegador.close();
}
