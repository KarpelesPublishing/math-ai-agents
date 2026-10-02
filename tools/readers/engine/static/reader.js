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

  function render(section, demo) {
    var key = demo.controls.map(function (control) { return selectFor(section, control).value; }).join(',');
    var state = demo.states[key];
    var interpretation = section.querySelector('.interpretation');
    if (!state) {
      interpretation.textContent = 'This combination of values was not calculated in advance.';
      return;
    }
    var image = section.querySelector('.plot img');
    image.setAttribute('src', state.image);
    image.setAttribute('alt', state.alt);
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
  }

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
    render(section, demo);
  });
  document.documentElement.className = document.documentElement.className.replace('no-js', 'js');
  document.documentElement.setAttribute('data-ready', 'true');
}());
