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

  // 示例数据提示
  const note = document.getElementById('sample-note');
  if (item.isSample && note) {
    note.hidden = false;
    note.textContent = '⚠️ 本品种为「示例 / 估算」数据，非真实成交价，仅用于演示。';
  }

  // 信息面板：均价 / 报价条数 / 厂家数 / 规格 / 区域 / 来源 / 更新日期
  const info = document.getElementById('info-grid');
  if (info) {
    const rows = [
      ['当日最低/参考价', `${fmtNum(item.price)} ${item.unit || ''}`],
      ['近30日均价', item.avgPrice ? `${fmtNum(item.avgPrice)} ${item.unit || ''}` : '—'],
      ['报价条数', item.quoteCount != null ? item.quoteCount : '—'],
      ['厂家数', item.brandCount != null ? item.brandCount : '—'],
      ['规格', item.spec || '—'],
      ['区域', item.region || '—'],
      ['来源', item.source || '—'],
      ['更新日期', item.updatedAt || '—'],
    ];
    info.innerHTML = rows.map(([k, v]) =>
      `<div class="info-cell"><span class="info-k">${k}</span><b class="info-v">${v}</b></div>`
    ).join('');
  }

  const series = (history[item.name] || []).slice(-30);
  const dates = series.map(p => p.date);
  const prices = series.map(p => p.price);
  renderTrend('trend', dates, prices);

  document.getElementById('recent').innerHTML =
    '<tr><th>日期</th><th>价格</th></tr>' +
    series.slice().reverse().map(p =>
      `<tr><td>${p.date}</td><td>${fmtNum(p.price)} ${item.unit || ''}</td></tr>`
    ).join('');
}

init();
