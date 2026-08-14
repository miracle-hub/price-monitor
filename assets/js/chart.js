// ECharts 趋势图：涨用红、跌用绿（与看板一致）
function renderTrend(domId, dates, prices) {
  const chart = echarts.init(document.getElementById(domId));
  const first = prices[0];
  const last = prices[prices.length - 1];
  const color = last >= first ? '#e24b4a' : '#639922';
  chart.setOption({
    grid: { left: 56, right: 18, top: 20, bottom: 48 },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: { rotate: 45, fontSize: 11, color: '#888780' },
      axisLine: { lineStyle: { color: '#d3d1c7' } }
    },
    yAxis: {
      type: 'value',
      scale: true,
      axisLabel: { color: '#888780' },
      splitLine: { lineStyle: { color: '#ececf0' } }
    },
    series: [{
      type: 'line',
      data: prices,
      smooth: true,
      showSymbol: false,
      itemStyle: { color: color },
      lineStyle: { color: color, width: 2 },
      areaStyle: { color: color, opacity: 0.08 }
    }]
  });
  window.addEventListener('resize', () => chart.resize());
}
