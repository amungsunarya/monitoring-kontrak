/* Chart Heatmap — dipanggil dengan data dari /api/chart/heatmap */
window.initHeatmap = function (elementId, matrix) {
  const bulan = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];
  const tahunSet = [...new Set(matrix.map(m => m.tahun))].sort();
  const series = tahunSet.map(t => ({
    name: String(t),
    data: bulan.map((b, i) => {
      const found = matrix.find(m => m.tahun === t && m.bulan === i);
      return { x: b, y: found ? found.jml : 0 };
    })
  }));

  return new ApexCharts(document.getElementById(elementId), {
    series: series,
    chart: { type: 'heatmap', height: 220 },
    plotOptions: {
      heatmap: {
        shadeIntensity: 0.5,
        colorScale: {
          ranges: [
            { from: 0, to: 0, color: '#f0f0f0', name: 'Kosong' },
            { from: 1, to: 3, color: '#b3d9ff', name: 'Sedikit' },
            { from: 4, to: 6, color: '#66b3ff', name: 'Sedang' },
            { from: 7, to: 10, color: '#3385ff', name: 'Banyak' },
            { from: 11, to: 999, color: '#0052cc', name: 'Sangat Banyak' }
          ]
        }
      }
    },
    dataLabels: { enabled: true, style: { fontSize: '9px' } },
    xaxis: { type: 'category' }
  });
};