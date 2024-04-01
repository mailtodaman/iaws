document.addEventListener('DOMContentLoaded', function() {
    const chartConfigs = [
        {
            contextId: 'chartCostOverview',
            label: 'Cost Overview & Trends',
            data: [1200, 1350, 1500, 1450, 1600],
            borderColor: 'rgb(75, 192, 192)'
        },
        {
            contextId: 'chartSecurityPosture',
            label: 'Security Posture',
            data: [95, 90, 92, 85, 97],
            borderColor: 'rgb(255, 99, 132)'
        },
        {
            contextId: 'chartResourceUtilization',
            label: 'Resource Utilization',
            data: [70, 75, 80, 65, 90],
            borderColor: 'rgb(255, 159, 64)'
        },
        {
            contextId: 'chartServiceHealth',
            label: 'Service Health',
            data: [99, 98, 99, 97, 99],
            borderColor: 'rgb(153, 102, 255)'
        },
        {
            contextId: 'chartEnvironmentalImpact',
            label: 'Environmental Impact',
            data: [40, 42, 38, 41, 40],
            borderColor: 'rgb(75, 192, 192)'
        },
        {
            contextId: 'chartNetworkTraffic',
            label: 'Network Traffic',
            data: [500, 700, 650, 850, 800],
            borderColor: 'rgb(54, 162, 235)'
        },
        {
            contextId: 'chartComplianceStatus',
            label: 'Compliance Status',
            data: [100, 100, 95, 90, 100],
            borderColor: 'rgb(255, 206, 86)'
        },
        {
            contextId: 'chartServiceDependencies',
            label: 'Service Dependencies',
            data: [50, 47, 55, 60, 52],
            borderColor: 'rgb(255, 99, 132)'
        },
        {
            contextId: 'chartAnomalyDetection',
            label: 'Anomaly Detection',
            data: [2, 1, 0, 3, 4], // Assuming these numbers represent the count of anomalies detected each month
            borderColor: 'rgb(153, 102, 255)'
        }
    ];

    chartConfigs.forEach((config) => {
        const ctx = document.getElementById(config.contextId).getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['January', 'February', 'March', 'April', 'May'],
                datasets: [{
                    label: config.label,
                    data: config.data,
                    fill: false,
                    borderColor: config.borderColor,
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });
});
