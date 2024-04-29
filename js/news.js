document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('stockForm');
    const stockName = document.getElementById('stockName');
    //const stockInput = document.getElementById('stockInput');
    const newsList = document.getElementById('newsList');

    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const stockValue = stockName.value;
        fetchNews(stockValue);
    });

    function fetchNews(stock) {
        fetch('/news/stock', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: `stock=${stock}`
        })
        // log the response from the server
        .then(response => response.json())
        .then(data => updateNews(data))
        .catch(error => console.error('Error:', error));
    }

    function updateNews(data) {
        // Clear existing news
        newsList.innerHTML = '';

        // Assuming data is an array of news articles
        data.forEach(article => {
            const articleDiv = document.createElement('div');
            articleDiv.className = 'news-article';

            const headline = document.createElement('h3');
            headline.textContent = article.headline;

            const description = document.createElement('p');
            description.textContent = article.description;

            const image = document.createElement('img');
            image.src = article.image;
            image.alt = 'News Image';

            const link = document.createElement('a');
            link.href = "https://reuters.com" + article.url;
            link.textContent = 'Read more';
            link.target = '_blank';

            articleDiv.appendChild(headline);
            articleDiv.appendChild(description);
            if (article.image) articleDiv.appendChild(image);
            articleDiv.appendChild(link);

            newsList.appendChild(articleDiv);
        });
    }
});