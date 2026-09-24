/* Chart Gauge — bisa dipakai standalone */
window.initGaugeChart = function (elementId, value, label, color) {
  return new ApexCharts(document.getElementById(elementId), {
    series: [value],
    chart: { type: 'radialBar', height: 220 },
    plotOptions: {
      radialBar: {
        hollow: { size: '60%' },
        dataLabels: {
          name: { fontSize: '14px' },
          value: { fontSize: '26px', fontWeight: 'bold' }
        }
      }
    },
    labels: [label],
    colors: [color || '#667eea']
  });
};