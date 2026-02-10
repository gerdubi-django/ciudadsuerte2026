(function () {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.Chart || !window.dashboardDataset) {
            return;
        }

        const dataset = window.dashboardDataset;
        const charts = {
            rooms: renderRoomChart(dataset),
            sources: renderSourceChart(dataset),
            cashiers: renderCashierChart(dataset)
        };

        const refreshButton = document.querySelector('[data-refresh-charts]');
        if (refreshButton) {
            refreshButton.addEventListener('click', () => {
                refreshButton.disabled = true;
                setTimeout(() => {
                    refreshAllCharts(charts, dataset, false);
                    refreshButton.disabled = false;
                }, 240);
            });
        }

        // Refresh colors when the admin theme changes dynamically.
        document.addEventListener('admin:theme-change', () => {
            refreshAllCharts(charts, dataset, true);
        });
    });

    function refreshAllCharts(charts, dataset, updateColors) {
        updateRoomChart(charts.rooms, dataset, updateColors);
        updateSourceChart(charts.sources, dataset, updateColors);
        updateCashierChart(charts.cashiers, dataset, updateColors);
    }

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
            options: buildCartesianOptions()
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
            options: buildDoughnutOptions()
        });
    }

    function renderCashierChart(dataset) {
        const ctx = document.getElementById('chartCashiers');
        if (!ctx) { return null; }
        const labels = dataset.cashierLabels || [];
        const values = dataset.cashierValues || [];

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels.length ? labels : ['Sin datos'],
                datasets: [{
                    label: 'Cupones por cambista (24h)',
                    data: values.length ? values : [0],
                    backgroundColor: buildGradientPalette(labels.length || 1),
                    borderRadius: 10,
                    borderSkipped: false
                }]
            },
            options: buildCartesianOptions(true)
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

    function updateCashierChart(chart, dataset, updateColors = false) {
        if (!chart) { return; }
        chart.data.labels = (dataset.cashierLabels || []).length ? dataset.cashierLabels : ['Sin datos'];
        chart.data.datasets[0].data = (dataset.cashierValues || []).length ? dataset.cashierValues : [0];
        if (updateColors) {
            chart.data.datasets[0].backgroundColor = buildGradientPalette(chart.data.labels.length);
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

    function buildCartesianOptions(horizontal = false) {
        return {
            indexAxis: horizontal ? 'y' : 'x',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0 } }
            }
        };
    }

    function buildDoughnutOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '58%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { usePointStyle: true }
                }
            }
        };
    }

    function buildGradientPalette(length) {
        // Build a dynamic palette from current theme colors.
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

    // Convert hex or rgb values to rgba while preserving color semantics.
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
