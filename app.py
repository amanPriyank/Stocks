"""
Stock Price Viewer - Flask Backend
A web application for viewing stock prices and comparing multiple stocks.
Uses Alpha Vantage API for both historical and current price data.
"""

import os
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, render_template
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
ALPHA_VANTAGE_BASE_URL = os.getenv('ALPHA_VANTAGE_BASE_URL', 'https://www.alphavantage.co/query')

if not ALPHA_VANTAGE_API_KEY:
    raise ValueError("ALPHA_VANTAGE_API_KEY not found in environment variables")


@app.route('/')
def index():
    """Serve the main application page."""
    return render_template('index.html')


@app.route('/api/stock_data', methods=['GET'])
def get_stock_data():
    """
    Fetch stock data for a single symbol.
    
    Returns:
        JSON response with stock price data including current price,
        real historical data, and price changes.
    """
    symbol = request.args.get('symbol', '').upper().strip()
    range_type = request.args.get('range', '1M')
    
    if not symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400
    
    try:
        # Get historical data from Alpha Vantage
        historical_data = _fetch_historical_data(symbol, range_type)
        if not historical_data:
            return jsonify({'error': f'No data available for {symbol}. This could be due to API rate limits (25 calls/day for free tier) or invalid symbol.'}), 400
        
        return jsonify({
            'symbol': symbol,
            'dates': historical_data['dates'],
            'prices': historical_data['prices'],
            'volumes': historical_data['volumes'],
            'current_price': historical_data['current_price'],
            'change': historical_data['change'],
            'percent_change': historical_data['percent_change'],
            'high': historical_data['high'],
            'low': historical_data['low'],
            'open': historical_data['open']
        })
        
    except requests.RequestException:
        return jsonify({'error': 'Failed to fetch stock data'}), 500
    except Exception:
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/multiple_stocks', methods=['POST'])
def get_multiple_stocks():
    """
    Fetch and compare data for multiple stock symbols.
    
    Returns:
        JSON response with stock data for all valid symbols.
    """
    data = request.get_json()
    symbols = data.get('symbols', [])
    range_type = data.get('range', '1M')
    
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400
    
    if len(symbols) > 5:
        return jsonify({'error': 'Maximum 5 stocks can be compared'}), 400
    
    stocks_data = []
    
    for symbol in symbols:
        try:
            symbol = symbol.upper().strip()
            
            # Fetch data for each symbol
            historical_data = _fetch_historical_data(symbol, range_type)
            if not historical_data:
                continue
            
            stocks_data.append({
                'symbol': symbol,
                'dates': historical_data['dates'],
                'prices': historical_data['prices'],
                'current_price': historical_data['current_price'],
                'change': historical_data['change'],
                'percent_change': historical_data['percent_change']
            })
            
        except Exception:
            # Skip failed symbols and continue with others
            continue
    
    return jsonify({'stocks': stocks_data})


def _fetch_historical_data(symbol, range_type):
    """
    Fetch real historical data from Alpha Vantage API.
    
    Args:
        symbol (str): Stock symbol
        range_type (str): Time range (1W, 1M, 6M)
        
    Returns:
        dict: Historical data with dates, prices, and volumes
    """
    try:
        # Map range types to Alpha Vantage functions
        if range_type == '6M':
            function = 'TIME_SERIES_WEEKLY'
        else:
            function = 'TIME_SERIES_DAILY'
        
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': ALPHA_VANTAGE_API_KEY,
            'outputsize': 'compact',
            'datatype': 'json'
        }
        
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=15)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        # Check for API errors
        if 'Error Message' in data:
            return None
        if 'Note' in data:
            return None  # API limit exceeded
        if 'Information' in data and 'rate limit' in data['Information'].lower():
            return None  # API rate limit exceeded
        
        # Extract time series data
        time_series_key = None
        for key in data.keys():
            if 'Time Series' in key:
                time_series_key = key
                break
        
        if not time_series_key or not data.get(time_series_key):
            return None
        
        time_series = data[time_series_key]
        
        # Process the data based on range type
        dates = []
        prices = []
        volumes = []
        
        # Sort dates in ascending order (oldest first)
        sorted_dates = sorted(time_series.keys())
        
        # Filter data based on range type using actual date calculations
        today = datetime.now().date()
        
        if range_type == '1W':
            # Last 7 calendar days
            cutoff_date = today - timedelta(days=7)
        elif range_type == '1M':
            # Last 30 calendar days  
            cutoff_date = today - timedelta(days=30)
        elif range_type == '6M':
            # Last 26 weeks (approximately 6 months)
            cutoff_date = today - timedelta(weeks=26)
        else:
            cutoff_date = today - timedelta(days=30)  # default to 1 month

        # Filter dates to only include data from cutoff_date onwards
        filtered_dates = []
        for date_str in sorted_dates:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                if date_obj >= cutoff_date:
                    filtered_dates.append(date_str)
            except ValueError:
                continue

        sorted_dates = filtered_dates
        
        if not sorted_dates:
            return None
        
        # For daily and monthly data, fill in missing dates with previous day's data
        if range_type in ['1W', '1M']:
            # Create a complete date range and fill missing dates
            start_date = datetime.strptime(sorted_dates[0], '%Y-%m-%d').date()
            end_date = today
            
            # Create dictionary of available data
            available_data = {}
            for date_str in sorted_dates:
                available_data[date_str] = time_series[date_str]
            
            # Generate all dates in range and fill missing ones
            current_date = start_date
            last_price = None
            last_volume = None
            
            while current_date <= end_date:
                date_str = current_date.strftime('%Y-%m-%d')
                
                if date_str in available_data:
                    # Use actual data if available
                    date_data = available_data[date_str]
                    last_price = float(date_data.get('4. close', 0))
                    last_volume = int(date_data.get('5. volume', 0))
                elif last_price is not None:
                    # Use previous day's data if no data for this date
                    date_data = {'4. close': last_price, '5. volume': last_volume}
                else:
                    # Skip if no data available yet
                    current_date += timedelta(days=1)
                    continue
                
                try:
                    date_obj = datetime.combine(current_date, datetime.min.time())
                    timestamp = int(date_obj.timestamp())
                    dates.append(timestamp)
                    
                    prices.append(last_price)
                    volumes.append(last_volume)
                    
                except (ValueError, TypeError):
                    pass
                
                current_date += timedelta(days=1)
        else:
            # For 6M data (weekly), use original logic without filling
            for date_str in sorted_dates:
                date_data = time_series[date_str]
                
                try:
                    # Convert date string to timestamp
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    timestamp = int(date_obj.timestamp())
                    dates.append(timestamp)
                    
                    # Extract price and volume data
                    close_price = float(date_data.get('4. close', 0))
                    volume = int(date_data.get('5. volume', 0))
                    
                    prices.append(round(close_price, 2))
                    volumes.append(volume)
                    
                except (ValueError, KeyError):
                    pass
        
        if not dates:
            return None
        
        # Get current price (latest close price)
        current_price = prices[-1] if prices else 0
        
        # Calculate period change (from start of period to current)
        if len(prices) >= 2:
            period_start_price = prices[0]  # First price in the period
            change = round(current_price - period_start_price, 2)
            percent_change = round((change / period_start_price) * 100, 2)
        else:
            change = 0
            percent_change = 0
        
        # Get OHLC data from latest available entry
        if sorted_dates:
            latest_data = time_series[sorted_dates[-1]]
            high = float(latest_data.get('2. high', current_price))
            low = float(latest_data.get('3. low', current_price))
            open_price = float(latest_data.get('1. open', current_price))
        else:
            high = low = open_price = current_price
        
        return {
            'dates': dates,
            'prices': prices,
            'volumes': volumes,
            'current_price': current_price,
            'change': change,
            'percent_change': percent_change,
            'high': high,
            'low': low,
            'open': open_price
        }
        
    except Exception:
        return None


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true', 
            host='0.0.0.0', port=5000)