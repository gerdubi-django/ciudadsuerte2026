(function () {
    // Draw a simple progress line that represents the seconds until data is saved.
    const DEFAULT_SECONDS = 3;
    const REFRESH_MS = 180;

    const buildChart = (canvas) => {
        if (!window.Chart || !canvas) return null;
        const context = canvas.getContext("2d");
        return new Chart(context, {
            type: "line",
            data: {
                datasets: [
                    {
                        label: "Progreso de guardado",
                        data: [],
                        borderColor: "#10316b",
                        backgroundColor: "rgba(16, 49, 107, 0.12)",
                        borderWidth: 3,
                        fill: true,
                        pointRadius: 0,
                        tension: 0.35,
                    },
                ],
            },
            options: {
                animation: false,
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        type: "linear",
                        min: 0,
                        ticks: { stepSize: 1, color: "#0f172a" },
                        grid: { color: "rgba(16, 49, 107, 0.08)" },
                        title: { display: true, text: "Segundos", color: "#10316b" },
                    },
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { callback: (value) => `${value}%`, color: "#0f172a" },
                        grid: { color: "rgba(16, 49, 107, 0.08)" },
                        title: { display: true, text: "Avance", color: "#10316b" },
                    },
                },
            },
        });
    };

    const updateStatus = (statusEl, message) => {
        if (statusEl) statusEl.textContent = message;
    };

    const startTimeline = (chart, statusEl, seconds) => {
        if (!chart) return;
        let elapsed = 0;
        chart.data.datasets[0].data = [];
        const timer = setInterval(() => {
            elapsed += REFRESH_MS / 1000;
            const progress = Math.min((elapsed / seconds) * 100, 100);
            chart.data.datasets[0].data.push({ x: Number(elapsed.toFixed(2)), y: progress });
            chart.update();
            updateStatus(
                statusEl,
                progress >= 100
                    ? "Datos guardados. Redirigiendo..."
                    : `Guardando datos... ${Math.max(seconds - elapsed, 0).toFixed(1)}s restantes`
            );
            if (progress >= 100) {
                clearInterval(timer);
                setTimeout(() => startTimeline(chart, statusEl, seconds), seconds * 600);
            }
        }, REFRESH_MS);
    };

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll("[data-save-timeline]").forEach((panel) => {
            const canvas = panel.querySelector("[data-save-chart]");
            const statusEl = panel.querySelector("[data-save-status]");
            const seconds = Number(panel.dataset.saveSeconds || DEFAULT_SECONDS);
            const chart = buildChart(canvas);
            if (!chart) return;

            const form = panel.closest("form");
            const startCycle = () => startTimeline(chart, statusEl, seconds);
            startCycle();
            if (form) {
                form.addEventListener("submit", () => {
                    updateStatus(statusEl, "Confirmando y guardando datos...");
                });
            }
        });
    });
})();
