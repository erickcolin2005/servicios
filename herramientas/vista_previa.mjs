// Saca la imagen que muestra WhatsApp al compartir el enlace (og:image): la portada a 1200x630.
// Uso: npm run vista-previa
import puppeteer from 'puppeteer-core';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const CHROME = process.env.CHROME ?? 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const navegador = await puppeteer.launch({ executablePath: CHROME, headless: true });
try {
  const pagina = await navegador.newPage();
  await pagina.setViewport({ width: 1200, height: 630 });
  await pagina.goto(pathToFileURL(resolve('docs/index.html')).href, { waitUntil: 'networkidle0' });
  await pagina.evaluate(() => document.fonts.ready);
  await pagina.screenshot({ path: 'docs/img/vista-previa.jpg', type: 'jpeg', quality: 86 });
} finally {
  await navegador.close();
}
