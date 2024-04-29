document.getElementById('stockForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const stockName = document.getElementById('stockName').value;
    const timeFrame = document.getElementById('timeFrame').value;
    const graphContainer = document.getElementById('graphContainer');

    // get graph container size
    var width = graphContainer.offsetWidth;
    var height = graphContainer.offsetHeight;

    // Construct the POST request
    fetch('/graph', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `timeframe=${timeFrame}&stock=${stockName}&width=${width}&height=${height}`
    })
    .then(response => response.blob())
    .then(blob => {
        // Assuming the server responds with an image
        const imageUrl = URL.createObjectURL(blob);
        graphContainer.innerHTML = `<img src="${imageUrl}" alt="Stock Graph">`;
    })
    .catch(error => {
        console.error('Error fetching graph:', error);
        graphContainer.innerHTML = `<p>Error loading graph.</p>`;
    });
});

