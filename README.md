# 📈 Stock Price Viewer

A modern web application that allows users to view stock price charts and compare multiple stocks using real-time data from the Finnhub API.

## ✨ Features

- **Single Stock Analysis**: Enter a stock ticker to view price charts with current price and percentage change
- **Multiple Stock Comparison**: Compare up to 5 stocks on a single chart
- **Time Range Filters**: View data for 1 week, 1 month, or 6 months
- **Real-time Data**: Uses Alpha Vantage API for both historical and current stock prices
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Interactive Charts**: Built with Chart.js for smooth, interactive visualizations

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- Alpha Vantage API key (free at [alphavantage.co](https://www.alphavantage.co/support/#api-key))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd MarketLens
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   
   Create a `.env` file in the project root with your API key:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` and replace the API key with your own:
   ```
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   
   Navigate to `http://localhost:5000` to view the application.

## 🎯 How to Use

### Single Stock View
1. Enter a stock ticker symbol (e.g., AAPL, GOOGL, MSFT)
2. Select your preferred time range
3. Click "Get Stock Data"
4. View the chart with current price and percentage change

### Multiple Stock Comparison
1. Enter multiple stock tickers separated by commas (e.g., AAPL,GOOGL,MSFT)
2. Select your preferred time range
3. Click "Compare Stocks"
4. View all stocks on a single comparative chart

### Time Ranges
- **1 Week**: Last 7 days of trading data
- **1 Month**: Last 30 days of trading data
- **6 Months**: Last 180 days of trading data

## 🛠️ Technical Details

### Backend (Python/Flask)
- **Framework**: Flask
- **API Integration**: Finnhub API for real-time stock data
- **Endpoints**:
  - `/` - Main application page
  - `/api/stock_data` - Single stock data
  - `/api/multiple_stocks` - Multiple stocks comparison

### Frontend
- **HTML5**: Semantic markup with responsive design
- **CSS3**: Modern styling with gradients and animations
- **JavaScript**: Vanilla JS with Chart.js for data visualization
- **Chart.js**: Interactive line charts with tooltips and legends

### API Usage
The application uses Alpha Vantage API:

**Alpha Vantage API:**
- `TIME_SERIES_DAILY` - Daily historical price data for 1W and 1M ranges
- `TIME_SERIES_WEEKLY` - Weekly historical price data for 6M range

**Data Sources:**
- **1 Week**: Last 7 days of daily data
- **1 Month**: Last 30 days of daily data  
- **6 Months**: Last 26 weeks of weekly data
- **Current Prices**: Latest close price from historical data
- **Price Changes**: Calculated from previous day/week

## 📁 Project Structure

```
MarketLens/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── .env                  # Environment variables (API keys)
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore rules
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── styles.css        # CSS styling
    └── script.js         # Frontend JavaScript
```

## 🔧 Configuration

### API Key Setup
1. **Alpha Vantage**: Register at [alphavantage.co](https://www.alphavantage.co/support/#api-key)
2. Copy `.env.example` to `.env` and replace the API key:
   ```bash
   cp .env.example .env
   # Edit .env and replace the API key with your actual key
   ```

### Customization
- **Colors**: Modify the color scheme in `static/styles.css`
- **Chart Options**: Adjust chart settings in `static/script.js`
- **API Endpoints**: Customize API calls in `app.py`

## 🌟 Bonus Features Implemented

- ✅ **Multiple Stocks on One Graph**: Compare up to 5 stocks simultaneously
- ✅ **Current Price + % Change**: Display real-time price information
- ✅ **Range Filters**: 1 week, 1 month, and 6-month views
- ✅ **Responsive Design**: Mobile-friendly interface
- ✅ **Interactive Charts**: Hover effects and tooltips
- ✅ **Error Handling**: User-friendly error messages
- ✅ **Loading States**: Visual feedback during data fetching

## 🚨 Troubleshooting

### Common Issues

1. **"Invalid stock symbol" error**
   - Ensure the ticker symbol is valid (e.g., AAPL, not APPL)
   - Some symbols may not be available in the free API tier

2. **"API request failed" or "No data available" error**
   - Check your internet connection
   - Verify the API key is correct
   - Check if you've exceeded API rate limits (25 calls/day for free tier)
   - Try again after some time or consider upgrading to premium plan

3. **Chart not displaying**
   - Ensure JavaScript is enabled in your browser
   - Check browser console for any errors
   - Verify Chart.js CDN is loading properly

### Rate Limits
**Alpha Vantage API:**
- 5 calls per minute
- 25 calls per day (free tier)
- 500 calls per day (premium plans available)

### API Features
- **Historical Data**: Real historical prices from Alpha Vantage (free tier provides 100 most recent data points)
- **Current Prices**: Latest close price from historical data
- **Price Changes**: Calculated from previous day/week comparison
- **Multiple Timeframes**: Daily data for 1W/1M ranges, weekly data for 6M range
- **OHLC Data**: Open, High, Low, Close prices available

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the Finnhub API documentation
3. Open an issue in the repository

---

**Happy Trading! 📊**
