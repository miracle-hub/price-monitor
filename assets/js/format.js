// 红涨绿跌 格式化：返回 {text, cls}
function formatChange(rate) {
  const r = Number(rate) || 0;
  const sign = r > 0 ? '+' : '';
  const cls = r > 0 ? 'up' : (r < 0 ? 'down' : 'flat');
  return { text: sign + r.toFixed(2) + '%', cls: cls };
}

// 数值千分位格式化；空值返回「—」
function fmtNum(n, digits) {
  if (n === null || n === undefined || n === '' || isNaN(Number(n))) return '—';
  const d = (digits === undefined) ? 2 : digits;
  return Number(n).toLocaleString('zh-CN', {
    minimumFractionDigits: d, maximumFractionDigits: d
  });
}
