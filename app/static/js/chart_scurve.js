/* Chart S-Curve — panggil dengan data dari /api/chart/scurve/:id */
window.initSCurve = function (elementId, data) {
  return new ApexCharts(document.getElementById(elementId), {
    series: [
      { name: 'Rencana', data: data.rencana },
      { name: 'Realisasi', data: data.realisasi }
    ],
    chart: { type: 'area', height: 280, toolbar: { show: false } },
    colors: ['#667eea', '#38ef7d'],
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth', width: 3 },
    fill: {
      type: 'gradient',
      gradient: { shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05 }
    },
    xaxis: { categories: data.labels },
    yaxis: { title: { text: 'Progres (%)' }, max: 100, min: 0 },
    title: {
      text: `${data.no_kontrak} — Fisik: ${data.progres_fisik}% | Bayar: ${data.progres_bayar}%`,
      align: 'left',
      style: { fontSize: '12px', color: '#666' }
    },
    legend: { position: 'top' },
    tooltip: { y: { formatter: v => v != null ? v + '%' : '-' } }
  });
};