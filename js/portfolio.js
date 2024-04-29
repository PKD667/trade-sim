document.addEventListener('DOMContentLoaded', function() {
    fetchPortfolioData();
});

function fetchPortfolioData() {
    fetch('/portfolioTable') // Replace with your actual API URL
        .then(response => response.json())
        .then(data => {
            updatePortfolioTable(data);
        })
        .catch(error => console.error('Error fetching portfolio data:', error));
}

function updatePortfolioTable(data) {
    const table = document.createElement('table');
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');

    // Assuming data is an array of portfolio items
    thead.innerHTML = `<tr>
        <th>Stock</th>
        <th>Shares</th>
        <th>Price</th>
        <th>Total Value</th>
    </tr>`;

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `<td>${item.stock}</td>
                         <td>${item.shares}</td>
                         <td>${item.price}</td>
                         <td>${item.totalValue}</td>`;
        tbody.appendChild(row);
    });

    table.appendChild(thead);
    table.appendChild(tbody);
    document.getElementById('portfolioTable').appendChild(table);
}
