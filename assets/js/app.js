const CAT_LABEL = { vitamin: '维生素', solvent: '有机溶剂' };
let ALL = [];
let CUR = 'all';

async function load() {
  try {
    const res = await fetch('./data/latest.json', { cache: 'no-store' });
    ALL = await res.json();
  } catch (e) {
    document.getElementById('board').innerHTML =
      '<p class="err">数据加载失败，请通过本地服务器或 GitHub Pages 访问（见 README）。</p>';
    return;
  }
  const upd = ALL[0] && ALL[0].updatedAt;
  document.getElementById('updated').textContent = upd ? '更新日期：' + upd : '';
  render();
}

function render() {
  const list = CUR === 'all' ? ALL : ALL.filter(x => x.category === CUR);
  const board = document.getElementById('board');
  if (!list.length) { board.innerHTML = '<p class="err">暂无数据</p>'; return; }
  board.innerHTML = list.map(item => {
    const c = formatChange(item.changeRate);
    const sample = item.isSample ? '<span class="badge sample">示例</span>' : '';
    const cap = item.isSample ? '参考价（示例）' : '当日最低报价';
    const avg = item.avgPrice ? `<span>均价 ${fmtNum(item.avgPrice)}</span>` : '';
    const brands = item.brandCount ? `<span>${item.brandCount} 家厂</span>` : '';
    const quotes = item.quoteCount ? `<span>${item.quoteCount} 条报价</span>` : '';
    const metaBits = [item.spec, item.region].filter(Boolean).join(' · ');
    return `<a class="card" href="detail.html?name=${encodeURIComponent(item.name)}">
      <div class="card-top">
        <span class="cat">${CAT_LABEL[item.category] || ''}</span>
        ${sample}
        <span class="badge ${c.cls}">${c.text}</span>
      </div>
      <div class="name">${item.name}</div>
      <div class="meta">${metaBits}</div>
      <div class="price"><b>${fmtNum(item.price)}</b> <span class="unit">${item.unit || ''}</span></div>
      <div class="price-cap">${cap}</div>
      <div class="price-meta">${avg}${brands}${quotes}</div>
      <div class="src">来源：${item.source || '—'}</div>
    </a>`;
  }).join('');
}

document.getElementById('tabs').addEventListener('click', e => {
  const btn = e.target.closest('.tab');
  if (!btn) return;
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  CUR = btn.dataset.cat;
  render();
});

load();
