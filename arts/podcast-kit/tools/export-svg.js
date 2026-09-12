/*
 * Export the brand objects as SVG.
 *
 * The site needs the same clouds, servers and terminals that the openers use.
 * Rather than redraw them by hand — which drifts the moment the kit changes —
 * this runs the kit's own drawing code against a recording context that emits
 * SVG instead of pixels. One source of truth, and the wobble survives: the
 * shapes are already quadratic curves, which map onto SVG `Q` one for one.
 *
 *   node tools/export-svg.js                    # every object → ../../pages/objects/
 *   node tools/export-svg.js cloud server       # just these
 *   node tools/export-svg.js --out somewhere/
 */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const DEFAULT_OUT = path.resolve(ROOT, '../../pages/objects');

// name → the kit call. Objects are drawn around 0,0 at whatever size the kit
// gives them; the viewBox is measured from the result rather than guessed,
// because a hardcoded box crops the drawing the moment a shape changes.
const OBJECTS = [
  { name: 'cloud',    call: 'oCloud(7)' },
  { name: 'server',   call: 'oServer(3)' },
  { name: 'terminal', call: 'oTerm(11)' },
  { name: 'db',       call: 'oDb(5)' },
  { name: 'gear',     call: 'oGear(13)' },
  { name: 'bolt',     call: 'oBolt(2)' },
  { name: 'rocket',   call: 'oRocket(17)' },
  { name: 'wifi',     call: 'oWifi(23)' },
  { name: 'box',      call: 'oBox(29)' },
  { name: 'plug',     call: 'oPlug(31)' },

  // Rules and underlines. The brand has no straight lines anywhere, so the
  // site's dividers are drawn with the same trembling stroke as everything else.
  { name: 'rule',      call: "stroke([[-500,0],[-250,3],[0,-3],[250,2],[500,0]],false,41,{lw:5})" },
  { name: 'underline', call: "paint([[-160,0],[-80,4],[0,-3],[80,3],[160,0]],false,17,null,{lw:14,ink:'#FFD447',amp:4})" },
];

// A 2D context that records paths instead of painting them. Only the calls the
// kit actually makes are implemented; anything else would fail loudly rather
// than silently drop a shape.
const RECORDER = `(() => {
  const out = [];
  const mul = (m, n) => [
    m[0]*n[0] + m[2]*n[1], m[1]*n[0] + m[3]*n[1],
    m[0]*n[2] + m[2]*n[3], m[1]*n[2] + m[3]*n[3],
    m[0]*n[4] + m[2]*n[5] + m[4], m[1]*n[4] + m[3]*n[5] + m[5],
  ];
  let m = [1, 0, 0, 1, 0, 0];
  const stack = [];
  let d = '';
  const state = { fillStyle: '#000', strokeStyle: '#000', lineWidth: 1,
                  lineJoin: 'round', lineCap: 'round', globalAlpha: 1 };
  const num = v => Math.round(v * 100) / 100;
  const emit = (kind) => {
    if (!d.trim()) return;
    out.push({
      d: d.trim(),
      transform: \`matrix(\${m.map(num).join(' ')})\`,
      fill: kind === 'fill' ? state.fillStyle : 'none',
      stroke: kind === 'stroke' ? state.strokeStyle : 'none',
      width: state.lineWidth,
      alpha: state.globalAlpha,
      join: state.lineJoin, cap: state.lineCap,
    });
  };
  const ctx = {
    get fillStyle() { return state.fillStyle; }, set fillStyle(v) { state.fillStyle = v; },
    get strokeStyle() { return state.strokeStyle; }, set strokeStyle(v) { state.strokeStyle = v; },
    get lineWidth() { return state.lineWidth; }, set lineWidth(v) { state.lineWidth = v; },
    get lineJoin() { return state.lineJoin; }, set lineJoin(v) { state.lineJoin = v; },
    get lineCap() { return state.lineCap; }, set lineCap(v) { state.lineCap = v; },
    get globalAlpha() { return state.globalAlpha; }, set globalAlpha(v) { state.globalAlpha = v; },
    save() { stack.push([m.slice(), { ...state }]); },
    restore() { const s = stack.pop(); if (s) { m = s[0]; Object.assign(state, s[1]); } },
    translate(x, y) { m = mul(m, [1, 0, 0, 1, x, y]); },
    scale(x, y) { m = mul(m, [x, 0, 0, y, 0, 0]); },
    rotate(a) { const c = Math.cos(a), s = Math.sin(a); m = mul(m, [c, s, -s, c, 0, 0]); },
    setTransform(a, b, c, dd, e, f) { m = [a, b, c, dd, e, f]; },
    beginPath() { d = ''; },
    closePath() { d += ' Z'; },
    moveTo(x, y) { d += \` M \${num(x)} \${num(y)}\`; },
    lineTo(x, y) { d += \` L \${num(x)} \${num(y)}\`; },
    quadraticCurveTo(cx, cy, x, y) { d += \` Q \${num(cx)} \${num(cy)} \${num(x)} \${num(y)}\`; },
    bezierCurveTo(a, b, c, dd, x, y) {
      d += \` C \${num(a)} \${num(b)} \${num(c)} \${num(dd)} \${num(x)} \${num(y)}\`;
    },
    arc(x, y, r, s, e) {
      // Only full circles appear in the kit; anything else would need splitting.
      d += \` M \${num(x - r)} \${num(y)} A \${num(r)} \${num(r)} 0 1 0 \${num(x + r)} \${num(y)}\` +
           \` A \${num(r)} \${num(r)} 0 1 0 \${num(x - r)} \${num(y)}\`;
    },
    fill() { emit('fill'); },
    stroke() { emit('stroke'); },
    clearRect() {}, fillRect() {}, drawImage() {},
  };
  return { ctx, out };
})()`;

function measure(paths) {
  // Control points are included, so the box is never too small — at worst a
  // curve leaves a little more air around it than strictly needed.
  let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity, pad = 0;
  for (const p of paths) {
    const m = p.transform.match(/matrix\(([^)]+)\)/);
    const [a, b, c, d, e, f] = m ? m[1].trim().split(/\s+/).map(Number) : [1, 0, 0, 1, 0, 0];
    const nums = p.d.match(/-?\d+(?:\.\d+)?/g) || [];
    for (let i = 0; i + 1 < nums.length; i += 2) {
      const px = Number(nums[i]), py = Number(nums[i + 1]);
      const tx = a * px + c * py + e, ty = b * px + d * py + f;
      if (tx < x0) x0 = tx; if (tx > x1) x1 = tx;
      if (ty < y0) y0 = ty; if (ty > y1) y1 = ty;
    }
    pad = Math.max(pad, (p.width || 0) / 2 + 2);   // widest stroke, applied once
  }
  if (!Number.isFinite(x0)) return { x: -100, y: -100, w: 200, h: 200 };
  return { x: x0 - pad, y: y0 - pad, w: x1 - x0 + pad * 2, h: y1 - y0 + pad * 2 };
}

function toSvg(paths) {
  const b = measure(paths);
  const r = v => Math.round(v * 10) / 10;
  const body = paths.map(p => {
    const attrs = [
      `d="${p.d}"`,
      `transform="${p.transform}"`,
      `fill="${p.fill}"`,
      p.stroke !== 'none' ? `stroke="${p.stroke}"` : null,
      p.stroke !== 'none' ? `stroke-width="${p.width}"` : null,
      p.stroke !== 'none' ? `stroke-linejoin="${p.join}"` : null,
      p.stroke !== 'none' ? `stroke-linecap="${p.cap}"` : null,
      p.alpha !== 1 ? `opacity="${p.alpha}"` : null,
    ].filter(Boolean).join(' ');
    return `  <path ${attrs}/>`;
  }).join('\n');
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${r(b.x)} ${r(b.y)} ${r(b.w)} ${r(b.h)}" fill="none">\n` +
         `  <!-- Generated by tools/export-svg.js from src/pack.html. Do not edit by hand. -->\n` +
         `${body}\n</svg>\n`;
}

(async () => {
  const args = process.argv.slice(2);
  let out = DEFAULT_OUT;
  const outAt = args.indexOf('--out');
  if (outAt !== -1) { out = path.resolve(args[outAt + 1]); args.splice(outAt, 2); }
  const wanted = args.length ? OBJECTS.filter(o => args.includes(o.name)) : OBJECTS;
  if (!wanted.length) {
    console.error('нет таких объектов; доступны: ' + OBJECTS.map(o => o.name).join(', '));
    process.exit(1);
  }

  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(ROOT, 'src/pack.html'));

  for (const obj of wanted) {
    const paths = await page.evaluate(([recorderSrc, call]) => {
      const rec = eval(recorderSrc);
      window.__withCtx(rec.ctx, () => { eval(call); });
      return rec.out;
    }, [RECORDER, obj.call]);

    if (!paths.length) {
      console.error(`  ${obj.name}: ничего не нарисовалось — пропускаю`);
      continue;
    }
    const file = path.join(out, `${obj.name}.svg`);
    fs.writeFileSync(file, toSvg(paths));
    console.log(`  ${obj.name.padEnd(9)} ${String(paths.length).padStart(3)} контуров  ${path.relative(process.cwd(), file)}`);
  }

  await browser.close();
})();
