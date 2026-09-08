#!/usr/bin/env node
/**
 * Рендерит сцену покадрово в PNG и собирает mp4.
 *
 *   node tools/render-video.js kids
 *   node tools/render-video.js styles noir
 *   node tools/render-video.js styles garage --crf 20
 *   node tools/render-video.js kids --frames 30      (быстрый тест: только 30 кадров)
 *
 * Кадры кладутся в out/frames/<имя>/, готовое видео — в out/<имя>.mp4
 */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
const scene = argv[0] || 'kids';
const theme = (argv[1] && !argv[1].startsWith('--')) ? argv[1] : null;
const flag = (name, def) => {
  const i = argv.indexOf('--' + name);
  return i >= 0 ? argv[i + 1] : def;
};

const SCENES = { kids: 'src/scene-kids.html', styles: 'src/scene-styles.html' };
if (!SCENES[scene]) {
  console.error(`Неизвестная сцена "${scene}". Доступны: ${Object.keys(SCENES).join(', ')}`);
  process.exit(1);
}

const name    = theme ? `${scene}-${theme}` : scene;
const framesD = path.join(ROOT, 'out', 'frames', name);
const outFile = path.join(ROOT, 'out', `${name}.mp4`);
const crf     = flag('crf', '18');
const limit   = flag('frames', null);

(async () => {
  fs.mkdirSync(framesD, { recursive: true });
  const browser = await chromium.launch({ args: ['--force-color-profile=srgb'] });
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.log('ОШИБКА В СЦЕНЕ:', e.message));

  await page.goto('file://' + path.join(ROOT, SCENES[scene]));
  await page.waitForTimeout(600);

  if (theme) {
    const list = await page.evaluate(() => window.THEME_LIST || []);
    if (!list.includes(theme)) {
      console.error(`Тема "${theme}" не найдена. Есть: ${list.join(', ')}`);
      process.exit(1);
    }
    await page.evaluate(t => window.setTheme(t), theme);
  }

  const total = limit ? Number(limit) : await page.evaluate(() => window.TOTAL || 510);
  const fps   = await page.evaluate(() => window.FPS || 30);
  console.log(`${name}: ${total} кадров при ${fps} fps`);

  const t0 = Date.now();
  for (let n = 0; n < total; n++) {
    const fp = path.join(framesD, `f_${String(n).padStart(4, '0')}.png`);
    await page.evaluate(k => window.drawFrame(k), n);
    await page.screenshot({ path: fp });
    if (n % 50 === 0) process.stdout.write(`  кадр ${n}/${total}\r`);
  }
  await browser.close();
  console.log(`\nкадры готовы за ${((Date.now() - t0) / 1000).toFixed(0)} с`);

  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  execFileSync('ffmpeg', [
    '-loglevel', 'error', '-y',
    '-framerate', String(fps),
    '-i', path.join(framesD, 'f_%04d.png'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', crf,
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    outFile,
  ], { stdio: 'inherit' });

  const mb = (fs.statSync(outFile).size / 1048576).toFixed(1);
  console.log(`готово: ${path.relative(ROOT, outFile)}  (${mb} МБ)`);
})();
