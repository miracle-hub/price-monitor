// 红涨绿跌 格式化：返回 {text, cls}
function formatChange(rate) {
  const r = Number(rate) || 0;
  const sign = r > 0 ? '+' : '';
  const cls = r > 0 ? 'up' : (r < 0 ? 'down' : 'flat');
  return { text: sign + r.toFixed(2) + '%', cls: cls };
}
