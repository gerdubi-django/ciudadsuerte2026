(function () {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.Chart || !window.dashboardDataset) {
            return;
        }

        const dataset = window.dashboardDataset;
        const charts = {};

        charts.rooms = renderRoomChart(dataset);
        charts.sources = renderSourceChart(dataset);
        charts.timeline = renderTimelineChart(dataset);

        const refreshButton = document.querySelector('[data-refresh-charts]');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                refreshButton.disabled = true;
                setTimeout(() => {
                    updateRoomChart(charts.rooms, dataset);
                    updateSourceChart(charts.sources, dataset);
                    updateTimelineChart(charts.timeline, dataset);
                    refreshButton.disabled = false;
                }, 240);
            });
        }

        // Refresh chart colors when the theme switches dynamically.
        document.addEventListener('admin:theme-change', () => {
            updateRoomChart(charts.rooms, dataset, true);
            updateSourceChart(charts.sources, dataset, true);
            updateTimelineChart(charts.timeline, dataset, true);
        });
    });

    function renderRoomChart(dataset) {
        const ctx = document.getElementById('chartRooms');
        if (!ctx) { return null; }
        const labels = dataset.roomLabels || [];
        const values = dataset.roomValues || [];
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels.length ? labels : ['Sin datos'],
                datasets: [{
                    label: 'Cupones por sala',
                    data: values.length ? values : [0],
                    backgroundColor: buildGradientPalette(labels.length || 1),
                    borderRadius: 12,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
    }

    function renderSourceChart(dataset) {
        const ctx = document.getElementById('chartSources');
        if (!ctx) { return null; }
        const sourceData = aggregateCounts(dataset.sourceLabels || []);
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: sourceData.labels.length ? sourceData.labels : ['Sin datos'],
                datasets: [{
                    label: 'Origen de cupones',
                    data: sourceData.values.length ? sourceData.values : [1],
                    backgroundColor: buildGradientPalette(sourceData.labels.length || 1),
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '62%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { usePointStyle: true }
                    }
                }
            }
        });
    }

    function renderTimelineChart(dataset) {
        const ctx = document.getElementById('chartTimeline');
        if (!ctx) { return null; }
        const timelineData = aggregateTimeline(dataset.recentDates || []);
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: timelineData.labels.length ? timelineData.labels : ['Sin datos'],
                datasets: [{
                    label: 'Cupones por día',
                    data: timelineData.values.length ? timelineData.values : [0],
                    fill: true,
                    tension: 0.36,
                    borderColor: chartLineColor(),
                    backgroundColor: chartAreaColor(),
                    pointRadius: 4,
                    pointBackgroundColor: chartLineColor()
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
    }

    function updateRoomChart(chart, dataset, updateColors = false) {
        if (!chart) { return; }
        chart.data.labels = (dataset.roomLabels || []).length ? dataset.roomLabels : ['Sin datos'];
        chart.data.datasets[0].data = (dataset.roomValues || []).length ? dataset.roomValues : [0];
        if (updateColors) {
            chart.data.datasets[0].backgroundColor = buildGradientPalette(chart.data.labels.length);
        }
        chart.update();
    }

    function updateSourceChart(chart, dataset, updateColors = false) {
        if (!chart) { return; }
        const sourceData = aggregateCounts(dataset.sourceLabels || []);
        chart.data.labels = sourceData.labels.length ? sourceData.labels : ['Sin datos'];
        chart.data.datasets[0].data = sourceData.values.length ? sourceData.values : [1];
        if (updateColors) {
            chart.data.datasets[0].backgroundColor = buildGradientPalette(chart.data.labels.length);
        }
        chart.update();
    }

    function updateTimelineChart(chart, dataset, updateColors = false) {
        if (!chart) { return; }
        const timelineData = aggregateTimeline(dataset.recentDates || []);
        chart.data.labels = timelineData.labels.length ? timelineData.labels : ['Sin datos'];
        chart.data.datasets[0].data = timelineData.values.length ? timelineData.values : [0];
        if (updateColors) {
            chart.data.datasets[0].borderColor = chartLineColor();
            chart.data.datasets[0].backgroundColor = chartAreaColor();
            chart.data.datasets[0].pointBackgroundColor = chartLineColor();
        }
        chart.update();
    }

    function aggregateCounts(list) {
        const totals = list.reduce((acc, entry) => {
            const key = entry || 'Sin datos';
            acc[key] = (acc[key] || 0) + 1;
            return acc;
        }, {});
        const labels = Object.keys(totals);
        const values = labels.map(label => totals[label]);
        return { labels, values };
    }

    function aggregateTimeline(list) {
        const totals = list.reduce((acc, entry) => {
            if (!entry) { return acc; }
            acc[entry] = (acc[entry] || 0) + 1;
            return acc;
        }, {});
        const labels = Object.keys(totals).sort((a, b) => new Date(a) - new Date(b));
        const values = labels.map(label => totals[label]);
        return { labels, values };
    }

    function buildGradientPalette(length) {
        // Build a dynamic palette using the current theme colors.
        const root = getComputedStyle(document.documentElement);
        const primary = root.getPropertyValue('--admin-color-primary').trim() || '#6366f1';
        const accent = root.getPropertyValue('--admin-color-accent').trim() || '#22d3ee';
        const baseColors = [primary, accent, '#f472b6', '#f97316', '#34d399', '#22d3ee'];
        const palette = [];
        for (let index = 0; index < length; index += 1) {
            const color = baseColors[index % baseColors.length];
            palette.push(applyOpacity(color, 0.82));
        }
        return palette;
    }

    // Resolve the chart line color from CSS custom properties.
    function chartLineColor() {
        const root = getComputedStyle(document.documentElement);
        return root.getPropertyValue('--admin-color-primary').trim() || '#6366f1';
    }

    // Create a translucent fill color for the timeline chart.
    function chartAreaColor() {
        const line = chartLineColor();
        return applyOpacity(line, 0.18);
    }

    // Convert color values to RGBA preserving the requested opacity.
    function applyOpacity(color, opacity) {
        if (color.startsWith('#')) {
            const hex = color.replace('#', '');
            const normalized = hex.length === 3
                ? hex.split('').map(char => char + char).join('')
                : hex;
            const bigint = parseInt(normalized, 16);
            const r = (bigint >> 16) & 255;
            const g = (bigint >> 8) & 255;
            const b = bigint & 255;
            return `rgba(${r}, ${g}, ${b}, ${opacity})`;
        }
        if (color.startsWith('rgb(')) {
            return color.replace('rgb(', 'rgba(').replace(')', `, ${opacity})`);
        }
        return color;
    }
})();
