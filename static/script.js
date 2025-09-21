let stockChart = null;

function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('error').style.display = 'none';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message, isWarning = false) {
    const errorDiv = document.getElementById('error');
    const errorMessage = document.getElementById('errorMessage');
    
    errorMessage.textContent = message;
    errorDiv.style.display = 'block';
    
    if (isWarning) {
        errorDiv.style.background = '#fff3cd';
        errorDiv.style.color = '#856404';
        errorDiv.style.border = '1px solid #ffeaa7';
    } else {
        errorDiv.style.background = '#f8d7da';
        errorDiv.style.color = '#721c24';
        errorDiv.style.border = '1px solid #f5c6cb';
    }
    
    hideLoading();
    
    setTimeout(() => {
        hideError();
    }, 5000);
}

function hideError() {
    document.getElementById('error').style.display = 'none';
}

function showChart() {
    document.getElementById('chartContainer').style.display = 'block';
}

function hideChart() {
    document.getElementById('chartContainer').style.display = 'none';
    document.getElementById('stocksSummaryHeader').style.display = 'none';
}

function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(price);
}

function formatDate(timestamp) {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
    });
}

function formatChange(change, percentChange) {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${formatPrice(change)} (${sign}${percentChange.toFixed(2)}%)`;
}

function getChangeClass(change) {
    return change >= 0 ? 'positive' : 'negative';
}

async function fetchStockData() {
    const symbol = document.getElementById('stockSymbol').value.trim().toUpperCase();
    const range = document.getElementById('rangeSelect').value;
    const button = document.getElementById('getDataBtn');
    
    if (!symbol) {
        showError('Please enter a stock ticker symbol');
        return;
    }
    
    button.disabled = true;
    button.innerHTML = '<div class="button-spinner"></div> Loading...';
    showLoading();
    hideError();
    
    try {
        const response = await fetch(`/api/stock_data?symbol=${symbol}&range=${range}`);
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        hideStocksSummary();
        showChart();
        document.getElementById('stocksSummaryHeader').style.display = 'none';
        displayStockInfo(data);
        createChart([data]);
        
        document.querySelector('.main-content').classList.add('translated');
        
    } catch (error) {
        console.error('Error fetching stock data:', error);
        showError('Failed to fetch stock data. Please try again.');
    } finally {
        hideLoading();
        button.disabled = false;
        button.innerHTML = 'Get Stock Data';
    }
}

async function fetchMultipleStocks() {
    const symbolsInput = document.getElementById('multipleSymbols').value.trim();
    const range = document.getElementById('rangeSelect').value;
    const button = document.getElementById('getMultipleBtn');
    
    if (!symbolsInput) {
        showError('Please enter stock ticker symbols (comma-separated)');
        return;
    }
    
    const symbols = symbolsInput.split(',').map(s => s.trim().toUpperCase()).filter(s => s);
    
    if (symbols.length === 0) {
        showError('Please enter valid stock ticker symbols');
        return;
    }
    
    if (symbols.length > 5) {
        showError('Maximum 5 stocks can be compared at once');
        return;
    }
    
    const uniqueSymbols = [...new Set(symbols)];
    if (uniqueSymbols.length !== symbols.length) {
        showError('Please enter unique stock symbols. Duplicate symbols are not allowed.');
        return;
    }
    
    button.disabled = true;
    button.innerHTML = '<div class="button-spinner"></div> Loading...';
    showLoading();
    hideError();
    
    try {
        const response = await fetch('/api/multiple_stocks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                symbols: symbols,
                range: range
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            showError(data.error);
            return;
        }
        
        if (data.stocks.length === 0) {
            showError('No valid stock data found for the provided symbols');
            return;
        }
        
        if (data.invalid_symbols && data.invalid_symbols.length > 0) {
            showError(`Invalid symbols: ${data.invalid_symbols.join(', ')}. Showing data for valid symbols only.`, true);
        }
        
        hideStockInfo();
        showChart();
        displayStocksSummaryHeader(data.stocks);
        createChart(data.stocks);
        
        document.querySelector('.main-content').classList.add('translated');
        
    } catch (error) {
        console.error('Error fetching multiple stocks data:', error);
        showError('Failed to fetch stock data. Please try again.');
    } finally {
        hideLoading();
        button.disabled = false;
        button.innerHTML = 'Compare Stocks';
    }
}

function displayStockInfo(data) {
    const stockInfo = document.getElementById('stockInfo');
    const currentSymbol = document.getElementById('currentSymbol');
    const currentPrice = document.getElementById('currentPrice');
    const priceChange = document.getElementById('priceChange');
    
    currentSymbol.textContent = data.symbol;
    currentPrice.textContent = formatPrice(data.current_price);
    
    const changeText = formatChange(data.change, data.percent_change);
    priceChange.textContent = changeText;
    priceChange.className = `price-change ${getChangeClass(data.change)}`;
    
    stockInfo.style.display = 'block';
}

function hideStockInfo() {
    document.getElementById('stockInfo').style.display = 'none';
}

function hideStocksSummary() {
    document.getElementById('stocksSummary').style.display = 'none';
    document.getElementById('stocksSummaryHeader').style.display = 'none';
}

function createChart(stocksData) {
    const ctx = document.getElementById('stockChart').getContext('2d');
    
    if (stockChart) {
        stockChart.destroy();
    }
    
    const colors = [
        'rgba(102, 126, 234, 1)',
        'rgba(255, 99, 132, 1)',
        'rgba(54, 162, 235, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)'
    ];
    
    const datasets = stocksData.map((stock, index) => {
        const color = colors[index % colors.length];
        
        return {
            label: stock.symbol,
            data: stock.prices,
            borderColor: color,
            backgroundColor: color.replace('1)', '0.1)'),
            borderWidth: 2,
            fill: false,
            tension: 0.1,
            pointRadius: 3,
            pointHoverRadius: 6,
            pointBackgroundColor: color,
            pointBorderColor: color
        };
    });
    
    const labels = stocksData[0] ? stocksData[0].dates.map(formatDate) : [];
    
    const config = {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: stocksData.length === 1 
                        ? `${stocksData[0].symbol} Stock Price Chart`
                        : 'Stock Price Comparison',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: stocksData.length > 1,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            const dataset = context.dataset;
                            const value = context.parsed.y;
                            return `${dataset.label}: ${formatPrice(value)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: true,
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Price (USD)',
                        font: {
                            weight: 'bold'
                        }
                    },
                    grid: {
                        display: true,
                        color: 'rgba(0,0,0,0.1)'
                    },
                    ticks: {
                        callback: function(value) {
                            return formatPrice(value);
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    };
    
    stockChart = new Chart(ctx, config);
}

function displayStocksSummaryHeader(stocksData) {
    const headerDiv = document.getElementById('stocksSummaryHeader');
    const stocksGrid = document.getElementById('stocksGrid');
    
    stocksGrid.innerHTML = '';
    
    stocksData.forEach(stock => {
        const card = document.createElement('div');
        card.className = 'stock-summary-card';
        
        const symbol = document.createElement('div');
        symbol.className = 'stock-symbol';
        symbol.textContent = stock.symbol;
        
        const price = document.createElement('div');
        price.className = 'stock-price';
        price.textContent = formatPrice(stock.current_price);
        
        const change = document.createElement('div');
        change.className = `stock-change ${getChangeClass(stock.change)}`;
        change.textContent = formatChange(stock.change, stock.percent_change);
        
        card.appendChild(symbol);
        card.appendChild(price);
        card.appendChild(change);
        stocksGrid.appendChild(card);
    });
    
    headerDiv.style.display = 'block';
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('stockSymbol').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fetchStockData();
        }
    });
    
    document.getElementById('multipleSymbols').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fetchMultipleStocks();
        }
    });
    
    document.getElementById('stockSymbol').addEventListener('input', function() {
        if (this.value.trim()) {
            document.getElementById('multipleSymbols').value = '';
        }
    });
    
    document.getElementById('multipleSymbols').addEventListener('input', function() {
        if (this.value.trim()) {
            document.getElementById('stockSymbol').value = '';
        }
    });
    
    document.getElementById('rangeSelect').addEventListener('change', function() {
        const singleSymbol = document.getElementById('stockSymbol').value.trim();
        const multipleSymbols = document.getElementById('multipleSymbols').value.trim();
        
        if (singleSymbol) {
            fetchStockData();
        } else if (multipleSymbols) {
            fetchMultipleStocks();
        }
    });
});

window.addEventListener('load', function() {
    console.log('MarketLens loaded successfully!');
});