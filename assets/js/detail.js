async function init() {
  const name = new URLSearchParams(location.search).get('name') || '';
  let latest = [], history = {};
  try {
    [latest, history] = await Promise.all([
      fetch('./data/latest.json', { cache: 'no-store' }).then(r => r.json()),
      fetch('./data/history.json', { cache: 'no-store' }).then(r => r.json())
    ]);
  } catch (e) {
    document.getElementById('title').textContent = '加载失败';
    return;
  }

  const item = latest.find(x => x.name === name) || latest[0];
  if (!item) return;

  document.getElementById('title').textContent = item.name;
  document.getElementById('d-name').textContent = item.name;
  document.getElementById('d-meta').textContent =
    `${item.spec || ''} · ${item.region || ''} · 来源：${item.source || '—'}`;
  document.getElementById('d-price').textContent = item.price;
  document.getElementById('d-unit').textContent = item.unit || '';

  const c = formatChange(item.changeRate);
  const el = document.getElementById('d-change');
  el.className = 'd-change badge ' + c.cls;
  el.textContent = '当日涨跌 ' + c.text;

  const series = (history[item.name] || []).slice(-30);
  const dates = series.map(p => p.date);
  const prices = series.map(p => p.price);
  renderTrend('trend', dates, prices);

  document.getElementById('recent').innerHTML =
    '<tr><th>日期</th><th>价格</th></tr>' +
    series.slice().reverse().map(p =>
      `<tr><td>${p.date}</td><td>${p.price} ${item.unit || ''}</td></tr>`
    ).join('');
}

init();
