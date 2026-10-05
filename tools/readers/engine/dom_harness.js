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
// Engine 1.2.0 optional features are checked when a page uses them: the
// "Ask the chapter skill" callout, prediction options with feedback, worked
// steps per state, the Back/Next stepper, and the misconception and scope
// note panels.
//
// Engine 1.3.0: every figure carries its legible minimum width (min-width in
// CSS pixels, from the state data) and a sideways-scroll hint, and every
// equation is an image or a clean text form, never raw TeX.
//
// Engine 1.4.0: when a page has the previous/next chapter pager, it must be a
// labelled nav whose links each name the chapter (span) and its title (b) and
// point at a sibling reader. The look (theme) is not checked here.
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
  const report = { file, equations_checked: 0, demos: 0, states_checked: 0, control_changes: 0, resets_checked: 0, no_script_defaults: 0, labelled_controls: 0,
    ask_skill: 0, predictions_checked: 0, steps_checked: 0, stepper_moves: 0, panels_checked: 0 };
  const stepsShown = section => { const list = section.querySelector('ol.steps'); return list ? list.querySelectorAll('li').map(li => li.textContent) : null; };

  // Structure and accessibility before any script runs.
  assert.equal(root.getAttribute('lang') !== null, true, 'html lang missing');
  const skip = doc.querySelector('a.skip'); assert.ok(skip && skip.getAttribute('href') === '#main' && byId('main'), 'skip link to #main missing');
  const levels = doc.descendants().filter(e => /^H[1-6]$/.test(e.tagName)).map(e => Number(e.tagName[1]));
  assert.equal(levels[0], 1, 'first heading must be h1');
  levels.forEach((l, k) => { if (k) assert.ok(l <= levels[k - 1] + 1, 'heading level skipped: h' + levels[k - 1] + ' to h' + l); });
  const noscript = doc.querySelector('noscript'); assert.ok(noscript && noscript.textContent.trim().length > 20, 'noscript explanation missing');
  const payloadNode = byId('reader-data'); assert.ok(payloadNode, 'payload script missing');
  const payload = JSON.parse(payloadNode.textContent);
  // Engine 1.5.0: a web build has no engine version in its data; it may link (never load) https pages.
  const web = !('engine' in payload);
  if (web) {
    assert.ok(!/src="(https?:)?\/\//.test(html) && !/href="(http:)?\/\//.test(html), 'network resource loaded or insecure link');
    assert.ok(!/name="generator"/.test(html), 'web page must not carry the generator meta tag');
    assert.ok(!doc.querySelector('aside.ask-skill'), 'web page must not carry the ask-skill callout');
    assert.ok(!/offline|precomputed|calculated in advance/i.test(noscript.textContent), 'web noscript note uses download-package wording');
  } else {
    assert.ok(!/(src|href)="(https?:)?\/\//.test(html), 'network resource referenced');
  }
  const pager = doc.querySelector('nav.chapter-pager');
  if (pager) {
    assert.equal(pager.getAttribute('aria-label'), 'Previous and next chapter', 'chapter pager needs its label');
    const links = pager.querySelectorAll('a');
    assert.ok(links.length >= 1 && links.length <= 2, 'chapter pager needs one or two links');
    for (const a of links) {
      assert.ok(a.classList.includes('prev') || a.classList.includes('next'), 'pager link must be .prev or .next');
      assert.ok(/^\.\.\/[^/]+\/reader\.html$/.test(a.getAttribute('href') || ''), 'pager link must point at a sibling reader');
      const span = a.querySelector('span'); const title = a.querySelector('b');
      assert.ok(span && /Chapter \d+/.test(span.textContent), 'pager link must name the chapter number');
      assert.ok(title && title.textContent.trim(), 'pager link must give the chapter title');
    }
    report.pager_links = links.length;
  }
  const ask = doc.querySelector('aside.ask-skill');
  if (ask) {
    const heading = ask.querySelector('h2');
    assert.ok(heading && heading.textContent === 'Ask the chapter skill', 'ask-skill callout needs its heading');
    assert.equal(ask.getAttribute('aria-labelledby'), heading.id, 'ask-skill callout must be labelled by its heading');
    assert.ok(ask.querySelector('.ask-skill-name').textContent.trim().length > 'Chapter skill: '.length, 'ask-skill callout must name the skill');
    assert.ok(ask.querySelector('p.ask-prompt').textContent.trim(), 'ask-skill prompt is empty');
    report.ask_skill++;
  }

  for (const demo of payload.demos) {
    const section = byId(demo.id); assert.ok(section, 'section ' + demo.id + ' missing');
    const defaults = demo.controls.map(c => c.default).join(',');
    const state = demo.states[defaults]; assert.ok(state, 'default state missing for ' + demo.id);
    const img = section.querySelector('figure.plot img');
    assert.equal(img.getAttribute('src'), state.image, demo.id + ': default figure not in HTML');
    assert.equal(img.getAttribute('alt'), state.alt, demo.id + ': default alt text');
    assert.equal(img.getAttribute('style'), state.min_width ? 'min-width:' + state.min_width + 'px' : null, demo.id + ': default figure minimum width');
    assert.ok(Object.values(demo.states).every(s => s.min_width === undefined || (Number.isInteger(s.min_width) && s.min_width > 0)), demo.id + ': min_width must be a positive integer');
    const hint = section.querySelector('figure.plot p.figure-hint');
    assert.ok(hint && hint.classList.includes('scroll-hint') && /scroll sideways/i.test(hint.textContent), demo.id + ': figure needs a sideways-scroll hint');
    const frame = section.querySelector('figure.plot div.figure-frame');
    assert.ok(frame && frame.querySelector('img') === img && frame.getAttribute('tabindex') === '0', demo.id + ': figure must sit in a focusable scrolling frame');
    for (const eq of section.querySelectorAll('div.formula p.equation')) {
      const eqImg = eq.querySelector('img');
      if (eqImg) {
        assert.ok(eqImg.getAttribute('alt').startsWith('Equation') && (eqImg.getAttribute('data-tex') || eqImg.getAttribute('data-typeset-tex')), demo.id + ': equation image needs alt text and data-tex or data-typeset-tex');
        const style = eqImg.getAttribute('style') || '';
        assert.ok(/^width:[\d.]+em;min-width:[\d.]+em$/.test(style) || /^height:[\d.]+em;max-width:none$/.test(style), demo.id + ': equation image size ' + style);
      } else {
        assert.ok(eq.classList.includes('text') && eq.getAttribute('data-typeset-tex'), demo.id + ': equation without an image must be the text form');
        assert.ok(eq.textContent.trim() && !/[\\{}]/.test(eq.textContent), demo.id + ': equation shown as raw TeX: ' + eq.textContent);
      }
      report.equations_checked++;
    }
    const altPrefix = 'Figure: ' + demo.title + (/[.?!]$/.test(demo.title.trimEnd()) ? ' ' : '. ');
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
    // Worked steps: shown for the default state without scripts, or absent everywhere.
    const hasSteps = Object.values(demo.states).filter(s => Array.isArray(s.steps)).length;
    assert.ok(hasSteps === 0 || hasSteps === Object.keys(demo.states).length, demo.id + ': steps given for some states only');
    if (hasSteps) {
      assert.ok(section.querySelector('div.steps-panel h3'), demo.id + ': worked steps panel needs a heading');
      assert.deepEqual(stepsShown(section), state.steps, demo.id + ': default worked steps not in HTML');
      assert.ok(state.steps.length >= 2 && state.steps.length <= 8, demo.id + ': 2 to 8 worked steps');
    } else {
      assert.equal(section.querySelector('ol.steps'), null, demo.id + ': steps panel without steps');
    }
    // Prediction options: a labelled radio group, disabled until the script runs, and a live feedback line.
    const radios = section.querySelectorAll('fieldset.predict-options input');
    if (demo.predict) {
      const fieldset = section.querySelector('fieldset.predict-options');
      assert.ok(fieldset.querySelector('legend') && fieldset.querySelector('legend').textContent.trim(), demo.id + ': prediction group needs a legend');
      assert.ok(radios.length >= 2 && radios.length <= 4, demo.id + ': 2 to 4 prediction options');
      assert.ok(Number.isInteger(demo.predict.answer) && demo.predict.answer >= 0 && demo.predict.answer < radios.length, demo.id + ': prediction answer out of range');
      radios.forEach((r, k) => {
        assert.equal(r.getAttribute('type'), 'radio', demo.id + ': prediction options must be radio buttons');
        assert.equal(r.getAttribute('name'), demo.id + '-prediction', demo.id + ': radio group name');
        assert.equal(r.getAttribute('value'), String(k), demo.id + ': radio values must be option indices');
        assert.ok(r.disabled, demo.id + ': prediction options must be disabled until the script runs');
        assert.ok(r.parentNode.tagName === 'LABEL' && r.parentNode.textContent.trim(), demo.id + ': each prediction option needs a label');
      });
      const feedback = section.querySelector('.prediction-feedback');
      assert.ok(feedback && feedback.getAttribute('aria-live') === 'polite', demo.id + ': prediction feedback must be aria-live polite');
      assert.equal(feedback.textContent, '', demo.id + ': prediction feedback must start empty');
    } else {
      assert.equal(radios.length, 0, demo.id + ': prediction options without feedback data');
    }
    // Stepper: Back/Next native buttons, hidden until the script runs, and a live status line.
    const stepper = section.querySelector('div.stepper');
    if (demo.stepper) {
      const control = demo.controls.find(c => c.key === demo.stepper);
      assert.ok(control && stepper && stepper.getAttribute('data-stepper') === demo.stepper, demo.id + ': stepper must name a control');
      assert.ok(stepper.getAttribute('aria-label'), demo.id + ': stepper group needs a label');
      for (const cls of ['step-back', 'step-next']) {
        const button = stepper.querySelector('button.' + cls);
        assert.ok(button && button.getAttribute('type') === 'button' && button.hidden, demo.id + ': ' + cls + ' must be a hidden native button before the script runs');
      }
      const status = stepper.querySelector('.step-status');
      assert.ok(status && status.getAttribute('aria-live') === 'polite', demo.id + ': stepper status must be aria-live polite');
      const k = control.default;
      assert.equal(status.textContent, 'Step ' + (k + 1) + ' of ' + control.values.length + ': ' + control.label + ': ' + control.values[k], demo.id + ': stepper status text');
    } else {
      assert.equal(stepper, null, demo.id + ': stepper buttons without a stepper control');
    }
    // Misconception and scope note panels.
    for (const cls of ['misconception', 'scope-note']) {
      const panel = section.querySelector('details.' + cls);
      if (!panel) continue;
      assert.ok(panel.querySelector('summary') && panel.querySelector('summary').textContent.trim(), demo.id + ': ' + cls + ' needs a summary');
      assert.ok(panel.querySelector('div.answer') && panel.querySelector('div.answer').textContent.trim(), demo.id + ': ' + cls + ' is empty');
      report.panels_checked++;
    }
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
      assert.equal(img.getAttribute('style'), state.min_width ? 'min-width:' + state.min_width + 'px' : null, where + ': figure minimum width');
      assert.equal(section.querySelector('.interpretation').textContent, state.interpretation, where + ': interpretation');
      const shown = section.querySelectorAll('.metrics .metric').map(g => [g.querySelector('dt').textContent, g.querySelector('dd').textContent]);
      assert.deepEqual(shown, state.metrics, where + ': metrics');
      assert.equal(section.querySelector('.selected-parameters').textContent, state.selected, where + ': selected values');
      if (state.steps) { assert.deepEqual(stepsShown(section), state.steps, where + ': worked steps'); report.steps_checked++; }
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

    if (demo.predict) {
      const radios = section.querySelectorAll('fieldset.predict-options input');
      const feedback = section.querySelector('.prediction-feedback');
      radios.forEach((r, k) => {
        assert.ok(!r.disabled, demo.id + ': prediction option still disabled after script');
        assert.ok(r.dispatch('change') >= 1, demo.id + ': no change listener on prediction option');
        const right = k === demo.predict.answer;
        assert.equal(feedback.textContent, right ? 'Correct. ' + demo.predict.correct : 'Not quite. ' + demo.predict.incorrect, demo.id + ': feedback for option ' + k);
        assert.ok(feedback.classList.includes(right ? 'is-correct' : 'is-incorrect'), demo.id + ': feedback class for option ' + k);
        report.predictions_checked++;
      });
    }

    if (demo.stepper) {
      const c = demo.controls.findIndex(x => x.key === demo.stepper);
      const control = demo.controls[c];
      const stepper = section.querySelector('div.stepper');
      const back = stepper.querySelector('button.step-back');
      const next = stepper.querySelector('button.step-next');
      const status = stepper.querySelector('.step-status');
      assert.ok(!back.hidden && !next.hidden && !status.hidden, demo.id + ': stepper still hidden after script');
      const here = () => {
        const index = Number(selects[c].value);
        const key = selects.map(s => s.value).join(',');
        expect(demo.states[key], demo.id + ' stepper at ' + key);
        assert.equal(status.textContent, 'Step ' + (index + 1) + ' of ' + control.values.length + ': ' + control.label + ': ' + control.values[index], demo.id + ': stepper status');
        assert.equal(back.disabled, index === 0, demo.id + ': Back must be disabled only at the first value');
        assert.equal(next.disabled, index === control.values.length - 1, demo.id + ': Next must be disabled only at the last value');
        return index;
      };
      while (here() > 0) { back.dispatch('click'); report.stepper_moves++; }
      back.dispatch('click');
      assert.equal(here(), 0, demo.id + ': Back must not wrap past the first value');
      for (let k = 1; k < control.values.length; k++) {
        next.dispatch('click'); report.stepper_moves++;
        assert.equal(here(), k, demo.id + ': Next must advance one value');
      }
      next.dispatch('click');
      assert.equal(here(), control.values.length - 1, demo.id + ': Next must not wrap past the last value');
      reset.dispatch('click');
      assert.equal(here(), control.default, demo.id + ': reset must return the stepper to the default');
    }
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
