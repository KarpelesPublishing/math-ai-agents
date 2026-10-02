'use strict';
// DOM harness for built readers. No dependencies beyond Node itself.
//
// Parses the built reader.html into a small DOM, checks what a reader sees
// before any script runs (defaults, labels, noscript text), then runs the
// page's own inline script and drives every control through every
// precomputed state. It is a controlled harness, not a browser: it does not
// test layout, painting or real keyboard events. Keyboard operability is
// checked structurally (native labelled <select> and <button> elements that
// are not removed from the tab order).
//
// Usage: node dom_harness.js path/to/reader.html [more readers...]
// Prints one JSON report per file; exits 1 on the first failed check.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const VOID = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr']);
const RAW = new Set(['script', 'style', 'textarea', 'title']);

function decode(text) {
  return text.replace(/&(#x[0-9a-f]+|#\d+|amp|lt|gt|quot|apos|#39);/gi, (m, e) => {
    const k = e.toLowerCase();
    if (k === 'amp') return '&'; if (k === 'lt') return '<'; if (k === 'gt') return '>';
    if (k === 'quot') return '"'; if (k === 'apos' || k === '#39') return "'";
    if (k.startsWith('#x')) return String.fromCodePoint(parseInt(k.slice(2), 16));
    return String.fromCodePoint(parseInt(k.slice(1), 10));
  });
}

class Text { constructor(data, parent) { this.nodeType = 3; this.data = data; this.parentNode = parent; } get textContent() { return this.data; } }

class Element {
  constructor(tag, attrs, parent) {
    this.nodeType = 1; this.tagName = tag.toUpperCase(); this.attrs = attrs; this.parentNode = parent;
    this.childNodes = []; this.listeners = {};
  }
  get children() { return this.childNodes.filter(n => n.nodeType === 1); }
  get firstChild() { return this.childNodes[0] || null; }
  getAttribute(n) { return Object.prototype.hasOwnProperty.call(this.attrs, n) ? this.attrs[n] : null; }
  setAttribute(n, v) { this.attrs[n] = String(v); }
  hasAttribute(n) { return Object.prototype.hasOwnProperty.call(this.attrs, n); }
  removeAttribute(n) { delete this.attrs[n]; }
  get id() { return this.getAttribute('id') || ''; }
  get className() { return this.getAttribute('class') || ''; }
  set className(v) { this.setAttribute('class', v); }
  get classList() { return this.className.split(/\s+/).filter(Boolean); }
  get disabled() { return this.hasAttribute('disabled'); }
  set disabled(v) { if (v) this.setAttribute('disabled', ''); else this.removeAttribute('disabled'); }
  get hidden() { return this.hasAttribute('hidden'); }
  set hidden(v) { if (v) this.setAttribute('hidden', ''); else this.removeAttribute('hidden'); }
  get options() { return this.querySelectorAll('option'); }
  get value() {
    if (this.tagName === 'SELECT') {
      const opts = this.options; const chosen = opts.find(o => o.selectedFlag) || opts.find(o => o.hasAttribute('selected')) || opts[0];
      return chosen ? chosen.getAttribute('value') : '';
    }
    return this.getAttribute('value') || '';
  }
  set value(v) {
    if (this.tagName !== 'SELECT') { this.setAttribute('value', v); return; }
    const opts = this.options; assert.ok(opts.some(o => o.getAttribute('value') === String(v)), 'no option with value ' + v);
    opts.forEach(o => { o.selectedFlag = o.getAttribute('value') === String(v); });
  }
  get textContent() { return this.childNodes.map(n => n.textContent).join(''); }
  set textContent(v) { this.childNodes = [new Text(String(v), this)]; }
  appendChild(node) { node.parentNode = this; this.childNodes.push(node); return node; }
  append(...nodes) { nodes.forEach(n => this.appendChild(n)); }
  removeChild(node) { this.childNodes = this.childNodes.filter(n => n !== node); node.parentNode = null; return node; }
  replaceChildren(...nodes) { this.childNodes = []; this.append(...nodes); }
  addEventListener(type, fn) { (this.listeners[type] = this.listeners[type] || []).push(fn); }
  dispatch(type) { (this.listeners[type] || []).forEach(fn => fn.call(this, {type, target: this})); return (this.listeners[type] || []).length; }
  descendants() { const out = []; const walk = n => n.children.forEach(c => { out.push(c); walk(c); }); walk(this); return out; }
  querySelectorAll(selector) { return selectAll(this, selector); }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

function parseCompound(text) {
  const m = { tag: null, id: null, classes: [], attrs: [] };
  const re = /^([a-z][a-z0-9]*)|#([\w-]+)|\.([\w-]+)|\[([\w-]+)(?:="([^"]*)")?\]/gi;
  let match, used = 0;
  while ((match = re.exec(text)) !== null) {
    if (match.index !== used) break;
    used = re.lastIndex;
    if (match[1]) m.tag = match[1].toUpperCase(); else if (match[2]) m.id = match[2];
    else if (match[3]) m.classes.push(match[3]); else m.attrs.push([match[4], match[5]]);
  }
  if (used !== text.length) throw new Error('Harness selector engine does not support: ' + text);
  return m;
}
function matches(el, c) {
  if (c.tag && el.tagName !== c.tag) return false;
  if (c.id && el.id !== c.id) return false;
  if (c.classes.some(k => !el.classList.includes(k))) return false;
  return c.attrs.every(([n, v]) => el.hasAttribute(n) && (v === undefined || el.getAttribute(n) === v));
}
function selectAll(root, selector) {
  const parts = selector.trim().split(/\s+/).map(parseCompound);
  return root.descendants().filter(el => {
    if (!matches(el, parts[parts.length - 1])) return false;
    let node = el.parentNode;
    for (let i = parts.length - 2; i >= 0; i--) {
      while (node && node !== root.parentNode && !(node.nodeType === 1 && matches(node, parts[i]))) node = node.parentNode;
      if (!node || node === root.parentNode) return false;
      node = node.parentNode;
    }
    return true;
  });
}

function parse(html) {
  const doc = new Element('#document', {}, null);
  let current = doc, i = 0;
  const tagRe = /<\/?([a-zA-Z][a-zA-Z0-9]*)((?:\s+[^\s=>\/]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?)*)\s*\/?>/y;
  while (i < html.length) {
    if (html.startsWith('<!--', i)) { i = html.indexOf('-->', i) + 3; continue; }
    if (html.startsWith('<!', i)) { i = html.indexOf('>', i) + 1; continue; }
    if (html[i] === '<') {
      tagRe.lastIndex = i; const m = tagRe.exec(html);
      if (m) {
        const tag = m[1].toLowerCase(); i = tagRe.lastIndex;
        if (m[0][1] === '/') {
          let node = current; while (node && node.tagName !== tag.toUpperCase()) node = node.parentNode;
          if (node) current = node.parentNode;
          continue;
        }
        const attrs = {}; const attrRe = /([^\s=>\/]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g; let a;
        while ((a = attrRe.exec(m[2])) !== null) attrs[a[1].toLowerCase()] = decode(a[2] ?? a[3] ?? a[4] ?? '');
        const el = current.appendChild(new Element(tag, attrs, current));
        if (RAW.has(tag)) {
          const end = html.toLowerCase().indexOf('</' + tag, i);
          el.appendChild(new Text(html.slice(i, end), el)); i = html.indexOf('>', end) + 1;
        } else if (!VOID.has(tag) && !m[0].endsWith('/>')) current = el;
        continue;
      }
    }
    const next = html.indexOf('<', i + 1); const end = next === -1 ? html.length : next;
    current.appendChild(new Text(decode(html.slice(i, end)), current)); i = end;
  }
  return doc;
}

function checkReader(file) {
  const html = fs.readFileSync(file, 'utf8');
  const doc = parse(html);
  const root = doc.querySelector('html');
  const byId = id => doc.descendants().find(e => e.id === id) || null;
  const report = { file, demos: 0, states_checked: 0, control_changes: 0, resets_checked: 0, no_script_defaults: 0, labelled_controls: 0 };

  // Structure and accessibility before any script runs.
  assert.equal(root.getAttribute('lang') !== null, true, 'html lang missing');
  const skip = doc.querySelector('a.skip'); assert.ok(skip && skip.getAttribute('href') === '#main' && byId('main'), 'skip link to #main missing');
  const levels = doc.descendants().filter(e => /^H[1-6]$/.test(e.tagName)).map(e => Number(e.tagName[1]));
  assert.equal(levels[0], 1, 'first heading must be h1');
  levels.forEach((l, k) => { if (k) assert.ok(l <= levels[k - 1] + 1, 'heading level skipped: h' + levels[k - 1] + ' to h' + l); });
  const noscript = doc.querySelector('noscript'); assert.ok(noscript && noscript.textContent.trim().length > 20, 'noscript explanation missing');
  const payloadNode = byId('reader-data'); assert.ok(payloadNode, 'payload script missing');
  const payload = JSON.parse(payloadNode.textContent);
  assert.ok(!/(src|href)="(https?:)?\/\//.test(html), 'network resource referenced');

  for (const demo of payload.demos) {
    const section = byId(demo.id); assert.ok(section, 'section ' + demo.id + ' missing');
    const defaults = demo.controls.map(c => c.default).join(',');
    const state = demo.states[defaults]; assert.ok(state, 'default state missing for ' + demo.id);
    const img = section.querySelector('figure.plot img');
    assert.equal(img.getAttribute('src'), state.image, demo.id + ': default figure not in HTML');
    assert.equal(img.getAttribute('alt'), state.alt, demo.id + ': default alt text');
    const altPrefix = 'Figure: ' + demo.title + '. ';
    assert.ok(state.alt.startsWith(altPrefix) && state.alt.trim().length > altPrefix.length, demo.id + ': alt text must name the figure and describe it');
    assert.equal(section.querySelector('.interpretation').textContent, state.interpretation, demo.id + ': default interpretation not in HTML');
    assert.equal(section.querySelector('.interpretation').getAttribute('aria-live'), 'polite');
    const shown = section.querySelectorAll('.metrics .metric').map(g => [g.querySelector('dt').textContent, g.querySelector('dd').textContent]);
    assert.deepEqual(shown, state.metrics, demo.id + ': default metrics not in HTML');
    for (const control of demo.controls) {
      const select = section.querySelector('select[data-control="' + control.key + '"]');
      assert.ok(select, demo.id + ': select ' + control.key + ' missing');
      assert.ok(select.disabled, demo.id + ': select must be disabled until the script runs');
      assert.equal(select.value, String(control.default), demo.id + ': default option not selected in HTML');
      const label = doc.querySelectorAll('label').find(l => l.getAttribute('for') === select.id);
      assert.ok(select.id && label && label.textContent.trim(), demo.id + ': select ' + control.key + ' has no label');
      assert.ok(select.getAttribute('tabindex') === null || Number(select.getAttribute('tabindex')) >= 0, 'select removed from tab order');
      assert.equal(select.options.length, control.values.length);
      report.labelled_controls++;
    }
    const reset = section.querySelector('button.reset');
    assert.ok(reset && reset.getAttribute('type') === 'button', demo.id + ': reset must be a native button');
    report.no_script_defaults++;
  }

  // Run the page's own script.
  const scripts = doc.querySelectorAll('script').filter(s => !s.getAttribute('type') && !s.getAttribute('src'));
  const code = scripts[scripts.length - 1].textContent;
  const document = {
    documentElement: root, getElementById: byId, createElement: tag => new Element(tag, {}, null),
    querySelector: s => doc.querySelector(s), querySelectorAll: s => doc.querySelectorAll(s),
  };
  vm.runInContext(code, vm.createContext({ document, window: {}, console }), { timeout: 2000 });
  assert.equal(root.getAttribute('data-ready'), 'true', 'script did not finish');
  assert.ok(!root.classList.includes('no-js'), 'no-js class not removed');

  for (const demo of payload.demos) {
    report.demos++;
    const section = byId(demo.id);
    const selects = demo.controls.map(c => section.querySelector('select[data-control="' + c.key + '"]'));
    selects.forEach(s => assert.ok(!s.disabled, 'select still disabled after script'));
    const reset = section.querySelector('button.reset'); assert.ok(!reset.hidden, 'reset still hidden');
    const expect = (state, where) => {
      const img = section.querySelector('figure.plot img');
      assert.equal(img.getAttribute('src'), state.image, where + ': image');
      assert.equal(img.getAttribute('alt'), state.alt, where + ': alt');
      assert.equal(section.querySelector('.interpretation').textContent, state.interpretation, where + ': interpretation');
      const shown = section.querySelectorAll('.metrics .metric').map(g => [g.querySelector('dt').textContent, g.querySelector('dd').textContent]);
      assert.deepEqual(shown, state.metrics, where + ': metrics');
      assert.equal(section.querySelector('.selected-parameters').textContent, state.selected, where + ': selected values');
    };
    const keys = Object.keys(demo.states);
    const expected = demo.controls.reduce((n, c) => n * c.values.length, 1);
    assert.equal(keys.length, expected, demo.id + ': not every combination is precomputed');
    const distinctImages = new Set(keys.map(k => demo.states[k].image)).size;
    assert.ok(distinctImages > 1, demo.id + ': every state shows the same figure');
    for (const key of keys) {
      const indices = key.split(',');
      // Change one control at a time, firing its change event, until the state is reached.
      selects.forEach((s, k) => { s.value = indices[k]; assert.ok(s.dispatch('change') >= 1, 'no change listener'); report.control_changes++; });
      expect(demo.states[key], demo.id + ' state ' + key);
      report.states_checked++;
    }
    reset.dispatch('click');
    expect(demo.states[demo.controls.map(c => c.default).join(',')], demo.id + ' after reset');
    report.resets_checked++;
  }
  return report;
}

const files = process.argv.slice(2);
if (!files.length) { console.error('usage: node dom_harness.js reader.html [...]'); process.exit(2); }
try {
  const reports = files.map(checkReader);
  process.stdout.write(JSON.stringify({ method: 'shipped reader script in a parsed DOM harness (not a browser)', reports }, null, 2) + '\n');
} catch (err) {
  console.error(String(err && err.stack || err));
  process.exit(1);
}
