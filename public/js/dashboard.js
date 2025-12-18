// File: /home/nicodeme/Bureau/Box-AI/frontend/public/js/dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    const dashboardDataContainer = document.getElementById('dashboard-data');

    function fetchDashboardData() {
        fetch('/api/dashboard') // Adjust the endpoint as necessary
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                displayDashboardData(data);
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });
    }

    function displayDashboardData(data) {
        dashboardDataContainer.innerHTML = ''; // Clear previous data
        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'dashboard-item';
            div.innerHTML = `<h3>${item.title}</h3><p>${item.description}</p>`;
            dashboardDataContainer.appendChild(div);
        });
    }

    fetchDashboardData();
});