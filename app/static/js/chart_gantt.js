/* Chart Gantt — dipanggil dengan data dari /api/chart/gantt */
window.initGantt = function (elementId, tasks, viewMode) {
  const gantt = new Gantt('#' + elementId, tasks, {
    view_mode: viewMode || 'Week',
    language: 'id',
    bar_height: 22,
    padding: 14,
    custom_popup_html: task => `
      <div style="padding:8px;">
        <strong>${task.name}</strong><br>
        <small>${task.start} → ${task.end}</small><br>
        <small>Progres: ${task.progress}%</small>
      </div>
    `
  });
  return gantt;
};