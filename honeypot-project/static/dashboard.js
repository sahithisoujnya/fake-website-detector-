document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('attackChart').getContext('2d');
    
    // Initialize empty chart
    let attackChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['SQL Injection', 'Brute Force', 'Failed Login'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(245, 158, 11, 0.8)', // Warning (SQLi)
                    'rgba(239, 68, 68, 0.8)',  // Danger (Brute)
                    'rgba(148, 163, 184, 0.8)' // Gray (Failed)
                ],
                borderColor: [
                    '#f59e0b',
                    '#ef4444',
                    '#94a3b8'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#f8fafc', font: { family: 'Inter' } }
                }
            }
        }
    });

    function formatTime(timestampStr) {
        const date = new Date(timestampStr);
        return date.toLocaleString();
    }

    function getBadgeClass(type) {
        if (type === 'SQL Injection') return 'badge-sqli';
        if (type === 'Brute Force') return 'badge-brute';
        return 'badge-failed';
    }

    async function fetchLogs() {
        try {
            // Append the secret query param
            const response = await fetch('/api/logs?secret=superadmin123');
            if (!response.ok) throw new Error("Unauthorized");
            const data = await response.json();
            
            updateTable(data);
            updateChart(data);
        } catch (error) {
            console.error('Error fetching logs:', error);
        }
    }

    function updateTable(logs) {
        const tbody = document.getElementById('logsBody');
        tbody.innerHTML = '';
        
        logs.forEach(log => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${formatTime(log.timestamp)}</td>
                <td style="font-family: monospace;">${log.ip_address}</td>
                <td><span class="badge ${getBadgeClass(log.attack_type)}">${log.attack_type}</span></td>
                <td>${log.username || '-'}</td>
                <td>${log.password_attempt ? '********' : '-'}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function updateChart(logs) {
        let sqli = 0, brute = 0, failed = 0;
        
        logs.forEach(log => {
            if (log.attack_type === 'SQL Injection') sqli++;
            else if (log.attack_type === 'Brute Force') brute++;
            else failed++;
        });
        
        attackChart.data.datasets[0].data = [sqli, brute, failed];
        attackChart.update();
    }

    // Fetch initially and then every 2 seconds for dynamic feel
    fetchLogs();
    setInterval(fetchLogs, 2000);
});
