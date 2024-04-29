function debounce(func, delay) {
    let debounceTimer;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(context, args), delay);
    };
}


// use the fetch api to request the autocomplete api for the StockName search
function updateStockOptions(input) {
    var selectElement = document.getElementById('stockName');
    selectElement.innerHTML = ''; // Clear existing options

    if (!input) { return false; }

    // Fetch data from your server's autocomplete endpoint
    fetch(`/autocomplete`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `search=${input}`
    })
    .then(console.log(`fetching autocomplete data ${input}`))
    .then(response => response.json())
    .then(data => {
        if (data && data.length) {
            data.forEach(function(item) {
                var option = document.createElement("option");
                option.value = item.symbol;
                option.text = `${item.symbol} - ${item.name}`;
                selectElement.appendChild(option);
            });
        }
    })
    .catch(error => {
        console.error('Error fetching stock data:', error);
    });
}



// Wrap updateStockOptions with debounce
const debouncedUpdateStockOptions = debounce(updateStockOptions, 300); // Adjust 300ms to your preference


updateStockOptions(document.getElementById('stockInput').value); // Initial load of options list

// Event listener for changes in the input field
document.getElementById('stockInput').addEventListener('input', function() {
    debouncedUpdateStockOptions(this.value);
});

