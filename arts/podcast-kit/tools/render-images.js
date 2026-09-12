#!/usr/bin/env node
/**
 * Рендерит статичную графику (обложки, аватарки, шапки) из src/pack.html.
 *
 *   node tools/render-images.js              — все файлы
 *   node tools/render-images.js apple_podcasts_3000 avatar_512_telegram
 *   node tools/render-images.js youtube_thumb_1280x720 --ep 01 --lines "ЕСЛИ БЫ|КУБЕР|СЕГОДНЯ"
 *
 * --ep    номер выпуска в красном кружке
 * --lines строки темы через | ; кегль подбирается под ширину автоматически
 *
 * Результат — в out/images/
 *
 * Чтобы добавить свой формат: допишите строку в ASSETS ниже.
 *   n      — имя файла без расширения
 *   w,h    — реальный размер в пикселях
 *   bw,bh  — размер «холста рисования»: макет пишется в этих координатах,
 *            а потом равномерно масштабируется до w,h
 *   layout — имя функции из объекта LAYOUT в src/pack.html
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const ROOT = path.resolve(__dirname, '..');

const ASSETS = [
  { n: 'cover_square_1080',         w: 1080, h: 1080, bw: 1080, bh: 1080, layout: 'cover'  },
  { n: 'apple_podcasts_3000',       w: 3000, h: 3000, bw: 1080, bh: 1080, layout: 'cover'  },
  { n: 'instagram_post_1080',       w: 1080, h: 1080, bw: 1080, bh: 1080, layout: 'cover'  },
  { n: 'avatar_512_telegram',       w:  512, h:  512, bw:  512, bh:  512, layout: 'avatar' },
  { n: 'avatar_800_youtube',        w:  800, h:  800, bw:  512, bh:  512, layout: 'avatar' },
  { n: 'avatar_1080_instagram',     w: 1080, h: 1080, bw:  512, bh:  512, layout: 'avatar' },
  { n: 'youtube_banner_2560x1440',  w: 2560, h: 1440, bw: 1280, bh:  720, layout: 'banner' },
  { n: 'youtube_thumb_1280x720',    w: 1280, h:  720, bw: 1280, bh:  720, layout: 'thumb'  },
  { n: 'telegram_post_1280x720',    w: 1280, h:  720, bw: 1280, bh:  720, layout: 'tgpost' },
  { n: 'instagram_story_1080x1920', w: 1080, h: 1920, bw: 1080, bh: 1920, layout: 'story'  },
  { n: 'episode_cover_1280x720',    w: 1280, h:  720, bw: 1280, bh:  720, layout: 'epcover'},
  { n: 'episode_square_1080',       w: 1080, h: 1080, bw: 1080, bh: 1080, layout: 'epsquare'},
  { n: 'episode_podcast_3000',      w: 3000, h: 3000, bw: 1080, bh: 1080, layout: 'epsquare'},
];

const argv = process.argv.slice(2);
const opts = {};
const flag = (name) => { const i = argv.indexOf('--' + name); if (i < 0) return null;
  const v = argv[i + 1]; argv.splice(i, 2); return v; };
const ep = flag('ep');   if (ep) opts.num = ep;
const ln = flag('lines'); if (ln) opts.lines = ln.split('|').map(s => s.trim()).filter(Boolean);
const suffix = flag('suffix') || '';
const only = argv;
const list = only.length ? ASSETS.filter(a => only.includes(a.n)) : ASSETS;
if (!list.length) { console.error('Ничего не выбрано. Имена:', ASSETS.map(a => a.n).join(', ')); process.exit(1); }

(async () => {
  const outD = path.join(ROOT, 'out', 'images');
  fs.mkdirSync(outD, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  page.on('pageerror', e => console.log('ОШИБКА В МАКЕТЕ:', e.message));
  await page.goto('file://' + path.join(ROOT, 'src/pack.html'));
  await page.waitForTimeout(400);

  // фотографии ведущих: отдаём в страницу как data-URI
  const hostsDir = path.join(ROOT, 'assets', 'hosts');
  if (fs.existsSync(hostsDir)) {
    const map = {};
    for (const f of fs.readdirSync(hostsDir).filter(f => f.endsWith('.png')))
      map[path.basename(f, '.png')] =
        'data:image/png;base64,' + fs.readFileSync(path.join(hostsDir, f)).toString('base64');
    await page.evaluate(m => window.loadHosts(m), map);
    console.log(`  ведущих загружено: ${Object.keys(map).length}`);
  }

  for (const a of list) {
    const data = await page.evaluate(a => window.render(a), { ...a, opts });
    const file = path.join(outD, `${a.n}${suffix}.png`);
    fs.writeFileSync(file, Buffer.from(data.split(',')[1], 'base64'));
    console.log(`  ${a.n}${suffix}.png  ${a.w}x${a.h}`);
  }
  await browser.close();
  console.log(`готово: out/images/ (${list.length} шт.)`);
})();
