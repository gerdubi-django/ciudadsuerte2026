(function () {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.Chart || !window.dashboardDataset) {
            return;
        }

        const dataset = window.dashboardDataset;
        const charts = {
            rooms: renderRoomChart(dataset),
            sources: renderSourceChart(dataset),
            timeline: renderTimelineChart(dataset),
            terminals: renderTerminalChart(dataset),
            weekday: renderWeekdayChart(dataset),
            status: renderStatusChart(dataset)
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
        updateTimelineChart(charts.timeline, dataset, updateColors);
        updateTerminalChart(charts.terminals, dataset, updateColors);
        updateWeekdayChart(charts.weekday, dataset, updateColors);
        updateStatusChart(charts.status, dataset, updateColors);
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
            options: buildCartesianOptions()
        });
    }

    function renderTerminalChart(dataset) {
        const ctx = document.getElementById('chartTerminals');
        if (!ctx) { return null; }
        const terminalData = topItems(dataset.terminalLabels || [], 6);
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: terminalData.labels.length ? terminalData.labels : ['Sin datos'],
                datasets: [{
                    label: 'Cupones por terminal',
                    data: terminalData.values.length ? terminalData.values : [0],
                    backgroundColor: buildGradientPalette(terminalData.labels.length || 1),
                    borderRadius: 10,
                    borderSkipped: false
                }]
            },
            options: buildCartesianOptions(true)
        });
    }

    function renderWeekdayChart(dataset) {
        const ctx = document.getElementById('chartWeekday');
        if (!ctx) { return null; }
        const weekdayData = aggregateWeekday(dataset.recentDates || []);
        return new Chart(ctx, {
            type: 'radar',
            data: {
                labels: weekdayData.labels,
                datasets: [{
                    label: 'Cupones por día de semana',
                    data: weekdayData.values,
                    borderColor: chartLineColor(),
                    backgroundColor: chartAreaColor(),
                    pointBackgroundColor: chartLineColor(),
                    pointRadius: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: { precision: 0 },
                        pointLabels: { color: chartTextColor() }
                    }
                }
            }
        });
    }

    function renderStatusChart(dataset) {
        const ctx = document.getElementById('chartStatus');
        if (!ctx) { return null; }
        const comparison = aggregateComparisonTimeline(dataset.recentDates || [], dataset.burnedRecentDates || []);
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: comparison.labels.length ? comparison.labels : ['Sin datos'],
                datasets: [
                    {
                        label: 'Cupones emitidos',
                        data: comparison.couponValues.length ? comparison.couponValues : [0],
                        borderColor: chartLineColor(),
                        backgroundColor: chartAreaColor(),
                        pointBackgroundColor: chartLineColor(),
                        tension: 0.34,
                        fill: false
                    },
                    {
                        label: 'Vouchers quemados',
                        data: comparison.burnedValues.length ? comparison.burnedValues : [0],
                        borderColor: '#ef4444',
                        backgroundColor: applyOpacity('#ef4444', 0.22),
                        pointBackgroundColor: '#ef4444',
                        tension: 0.34,
                        fill: false
                    }
                ]
            },
            options: {
                ...buildCartesianOptions(),
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { usePointStyle: true }
                    }
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

    function updateTerminalChart(chart, dataset, updateColors = false) {
        if (!chart) { return; }
        const terminalData = topItems(dataset.terminalLabels || [], 6);
        chart.data.labels = terminalData.labels.length ? terminalData.labels : ['Sin datos'];
        chart.data.datasets[0].data = terminalData.values.length ? terminalData.values : [0];
        if (updateColors) {
            chart.data.datasets[0].backgroundColor = buildGradientPalette(chart.data.labels.length);
        }
        chart.update();
    }

    function updateWeekdayChart(chart, dataset, updateColors = false) {
        if (!chart) { return; }
        const weekdayData = aggregateWeekday(dataset.recentDates || []);
        chart.data.labels = weekdayData.labels;
        chart.data.datasets[0].data = weekdayData.values;
        if (updateColors) {
            chart.data.datasets[0].borderColor = chartLineColor();
            chart.data.datasets[0].backgroundColor = chartAreaColor();
            chart.data.datasets[0].pointBackgroundColor = chartLineColor();
            chart.options.scales.r.pointLabels.color = chartTextColor();
        }
        chart.update();
    }

    function updateStatusChart(chart, dataset, updateColors = false) {
        if (!chart) { return; }
        const comparison = aggregateComparisonTimeline(dataset.recentDates || [], dataset.burnedRecentDates || []);
        chart.data.labels = comparison.labels.length ? comparison.labels : ['Sin datos'];
        chart.data.datasets[0].data = comparison.couponValues.length ? comparison.couponValues : [0];
        chart.data.datasets[1].data = comparison.burnedValues.length ? comparison.burnedValues : [0];
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

    function topItems(list, limit) {
        const counts = aggregateCounts(list);
        const entries = counts.labels.map((label, index) => [label, counts.values[index]]);
        const sorted = entries.sort((a, b) => b[1] - a[1]).slice(0, limit);
        return {
            labels: sorted.map(item => item[0]),
            values: sorted.map(item => item[1])
        };
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


    function aggregateComparisonTimeline(couponDates, burnedDates) {
        const couponTotals = aggregateTimeline(couponDates || []);
        const burnedTotals = aggregateTimeline(burnedDates || []);
        const mergedLabels = Array.from(new Set([...couponTotals.labels, ...burnedTotals.labels]))
            .sort((a, b) => new Date(a) - new Date(b));
        const couponMap = Object.fromEntries(couponTotals.labels.map((label, index) => [label, couponTotals.values[index]]));
        const burnedMap = Object.fromEntries(burnedTotals.labels.map((label, index) => [label, burnedTotals.values[index]]));
        return {
            labels: mergedLabels,
            couponValues: mergedLabels.map(label => couponMap[label] || 0),
            burnedValues: mergedLabels.map(label => burnedMap[label] || 0)
        };
    }

    function aggregateWeekday(list) {
        const weekdayLabels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
        const values = [0, 0, 0, 0, 0, 0, 0];
        list.forEach((entry) => {
            if (!entry) { return; }
            const parsed = new Date(`${entry}T00:00:00`);
            if (Number.isNaN(parsed.getTime())) { return; }
            const dayIndex = parsed.getDay();
            const mondayFirstIndex = dayIndex === 0 ? 6 : dayIndex - 1;
            values[mondayFirstIndex] += 1;
        });
        return { labels: weekdayLabels, values };
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

    // Resolve the chart line color from css custom properties.
    function chartLineColor() {
        const root = getComputedStyle(document.documentElement);
        return root.getPropertyValue('--admin-color-primary').trim() || '#6366f1';
    }

    // Resolve chart text color to keep labels legible in both themes.
    function chartTextColor() {
        const root = getComputedStyle(document.documentElement);
        return root.getPropertyValue('--admin-color-text').trim() || '#0f172a';
    }

    // Create a translucent area color derived from line color.
    function chartAreaColor() {
        const line = chartLineColor();
        return applyOpacity(line, 0.18);
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
