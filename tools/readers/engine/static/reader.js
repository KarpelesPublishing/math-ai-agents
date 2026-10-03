(function () {
  'use strict';
  var dataNode = document.getElementById('reader-data');
  if (!dataNode) { return; }
  var payload = JSON.parse(dataNode.textContent);

  function selectFor(section, control) {
    return section.querySelector('select[data-control="' + control.key + '"]');
  }

  function clear(node) {
    while (node.firstChild) { node.removeChild(node.firstChild); }
  }

  function each(list, fn) {
    Array.prototype.forEach.call(list, fn);
  }

  function setClass(node, name, on) {
    var list = String(node.className || '').split(/\s+/).filter(function (c) { return c && c !== name; });
    if (on) { list.push(name); }
    node.className = list.join(' ');
  }

  // A figure or equation wider than its column scrolls sideways; show the hint only then.
  function overflows(node) {
    return Number(node.scrollWidth) > Number(node.clientWidth) + 1;
  }

  function updateHints(section) {
    var frame = section.querySelector('.figure-frame');
    var hint = section.querySelector('.figure-hint');
    if (frame && hint) { setClass(hint, 'is-needed', overflows(frame)); }
    var equationHint = section.querySelector('.equation-hint');
    if (equationHint) {
      var wide = false;
      each(section.querySelectorAll('.equation'), function (node) { if (overflows(node)) { wide = true; } });
      setClass(equationHint, 'is-needed', wide);
    }
  }

  function stepperControl(demo) {
    var found = null;
    demo.controls.forEach(function (control) { if (control.key === demo.stepper) { found = control; } });
    return found;
  }

  function renderSteps(section, state) {
    var list = section.querySelector('ol.steps');
    if (!list || !state.steps) { return; }
    clear(list);
    state.steps.forEach(function (text) {
      var item = document.createElement('li');
      item.textContent = text;
      list.appendChild(item);
    });
  }

  function renderStepper(section, demo) {
    var control = demo.stepper ? stepperControl(demo) : null;
    var box = section.querySelector('div.stepper');
    if (!control || !box) { return; }
    var index = Number(selectFor(section, control).value);
    var last = control.values.length - 1;
    var back = box.querySelector('button.step-back');
    var next = box.querySelector('button.step-next');
    back.disabled = index <= 0;
    next.disabled = index >= last;
    // Keep keyboard focus on a usable button when the other end is reached.
    if (next.disabled && document.activeElement === next && typeof back.focus === 'function') { back.focus(); }
    if (back.disabled && document.activeElement === back && typeof next.focus === 'function') { next.focus(); }
    var status = box.querySelector('.step-status');
    var text = 'Step ' + (index + 1) + ' of ' + (last + 1) + ': ' + control.label + ': ' + control.values[index];
    // Write only on a change, so loading the page announces nothing.
    if (status.textContent !== text) { status.textContent = text; }
  }

  function render(section, demo) {
    var key = demo.controls.map(function (control) { return selectFor(section, control).value; }).join(',');
    var state = demo.states[key];
    var interpretation = section.querySelector('.interpretation');
    renderStepper(section, demo);
    if (!state) {
      interpretation.textContent = 'This combination of values was not calculated in advance.';
      return;
    }
    var image = section.querySelector('.plot img');
    image.setAttribute('src', state.image);
    image.setAttribute('alt', state.alt);
    // The smallest width at which the figure's text stays legible; narrower frames scroll.
    if (state.min_width) { image.setAttribute('style', 'min-width:' + state.min_width + 'px'); } else { image.removeAttribute('style'); }
    var metrics = section.querySelector('.metrics');
    clear(metrics);
    state.metrics.forEach(function (pair) {
      var group = document.createElement('div');
      group.className = 'metric';
      var term = document.createElement('dt');
      term.textContent = pair[0];
      var value = document.createElement('dd');
      value.textContent = pair[1];
      group.appendChild(term);
      group.appendChild(value);
      metrics.appendChild(group);
    });
    interpretation.textContent = state.interpretation;
    section.querySelector('.selected-parameters').textContent = state.selected;
    renderSteps(section, state);
    updateHints(section);
  }

  function setupStepper(section, demo) {
    var control = demo.stepper ? stepperControl(demo) : null;
    var box = section.querySelector('div.stepper');
    if (!control || !box) { return; }
    var select = selectFor(section, control);
    function move(delta) {
      var index = Number(select.value) + delta;
      if (index < 0 || index > control.values.length - 1) { return; }
      select.value = String(index);
      render(section, demo);
    }
    var back = box.querySelector('button.step-back');
    var next = box.querySelector('button.step-next');
    back.hidden = false;
    next.hidden = false;
    box.querySelector('.step-status').hidden = false;
    back.addEventListener('click', function () { move(-1); });
    next.addEventListener('click', function () { move(1); });
  }

  function setupPrediction(section, demo) {
    var feedback = section.querySelector('.prediction-feedback');
    if (!demo.predict || !feedback) { return; }
    each(section.querySelectorAll('fieldset.predict-options input'), function (radio) {
      radio.disabled = false;
      radio.addEventListener('change', function () {
        var right = Number(radio.value) === demo.predict.answer;
        feedback.textContent = right ? 'Correct. ' + demo.predict.correct : 'Not quite. ' + demo.predict.incorrect;
        feedback.className = 'prediction-feedback ' + (right ? 'is-correct' : 'is-incorrect');
      });
    });
  }

  var sections = [];
  payload.demos.forEach(function (demo) {
    var section = document.getElementById(demo.id);
    if (!section) { return; }
    demo.controls.forEach(function (control) {
      var select = selectFor(section, control);
      select.disabled = false;
      select.addEventListener('change', function () { render(section, demo); });
    });
    var reset = section.querySelector('button.reset');
    if (reset) {
      reset.hidden = false;
      reset.addEventListener('click', function () {
        demo.controls.forEach(function (control) { selectFor(section, control).value = String(control.default); });
        render(section, demo);
      });
    }
    setupStepper(section, demo);
    setupPrediction(section, demo);
    each(section.querySelectorAll('img'), function (img) { img.addEventListener('load', function () { updateHints(section); }); });
    render(section, demo);
    sections.push(section);
  });
  function updateAll() { sections.forEach(updateHints); }
  if (typeof window.addEventListener === 'function') {
    window.addEventListener('resize', updateAll);
    window.addEventListener('load', updateAll);
  }
  document.documentElement.className = document.documentElement.className.replace('no-js', 'js');
  document.documentElement.setAttribute('data-ready', 'true');
}());
