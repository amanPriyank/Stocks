import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
API_URL = os.getenv('ALPHA_VANTAGE_BASE_URL')
PORT = int(os.getenv('PORT'))

if not API_KEY:
    raise ValueError("Alpha Vantage API key not found")


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/stock_data', methods=['GET'])
def get_stock_data():
    # Fetch single stock data with price history
    symbol = request.args.get('symbol', '').upper().strip()
    range_type = request.args.get('range', '1M')
    
    if not symbol:
        return jsonify({'error': 'Stock symbol is required'}), 400
    
    try:
        data = fetch_stock_data(symbol, range_type)
        if not data:
            return jsonify({'error': f'No data available for {symbol}. Check if symbol is valid or try again later.'}), 400
        
        if isinstance(data, dict) and 'error' in data:
            if data['error'] == 'rate_limit':
                return jsonify({'error': data['message']}), 429
            elif data['error'] == 'invalid_symbol':
                return jsonify({'error': data['message']}), 400
        
        return jsonify({
            'symbol': symbol,
            'dates': data['dates'],
            'prices': data['prices'],
            'current_price': data['current_price'],
            'change': data['change'],
            'percent_change': data['percent_change']
        })
        
    except requests.RequestException:
        return jsonify({'error': 'Failed to fetch stock data'}), 500
    except Exception:
        return jsonify({'error': 'Something went wrong'}), 500


@app.route('/api/multiple_stocks', methods=['POST'])
def get_multiple_stocks():
    # Compare multiple stocks on a single chart
    data = request.get_json()
    symbols = data.get('symbols', [])
    range_type = data.get('range', '1M')
    
    if not symbols:
        return jsonify({'error': 'No symbols provided'}), 400
    
    if len(symbols) > 5:
        return jsonify({'error': 'Maximum 5 stocks can be compared'}), 400
    
    unique_symbols = list(set(symbols))
    if len(unique_symbols) != len(symbols):
        return jsonify({'error': 'Duplicate symbols are not allowed'}), 400
    
    stocks_data = []
    invalid_symbols = []
    rate_limit_hit = False
    
    for symbol in symbols:
        try:
            symbol = symbol.upper().strip()
            stock_data = fetch_stock_data(symbol, range_type)
            
            if not stock_data:
                continue
            
            if isinstance(stock_data, dict) and 'error' in stock_data:
                if stock_data['error'] == 'rate_limit':
                    rate_limit_hit = True
                    break
                elif stock_data['error'] == 'invalid_symbol':
                    invalid_symbols.append(symbol)
                    continue
            
            stocks_data.append({
                'symbol': symbol,
                'dates': stock_data['dates'],
                'prices': stock_data['prices'],
                'current_price': stock_data['current_price'],
                'change': stock_data['change'],
                'percent_change': stock_data['percent_change']
            })
            
        except Exception:
            continue
    
    response_data = {'stocks': stocks_data}
    
    if rate_limit_hit:
        response_data['error'] = 'API rate limit exceeded. Please try again later.'
        return jsonify(response_data), 429
    elif invalid_symbols:
        response_data['invalid_symbols'] = invalid_symbols
        response_data['message'] = f'Invalid symbols: {", ".join(invalid_symbols)}'
    
    return jsonify(response_data)


def fetch_stock_data(symbol, range_type):
    # Fetch historical data 
    try:
        if range_type == '6M':
            function = 'TIME_SERIES_WEEKLY'
        else:
            function = 'TIME_SERIES_DAILY'
        
        params = {
            'function': function,
            'symbol': symbol,
            'apikey': API_KEY,
            'outputsize': 'compact',
            'datatype': 'json'
        }
        
        response = requests.get(API_URL, params=params, timeout=15)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        if 'Error Message' in data:
            return {'error': 'invalid_symbol', 'message': f'Invalid symbol: {symbol}'}
        if 'Note' in data:
            return {'error': 'rate_limit', 'message': 'API rate limit exceeded. Please try again later.'}
        if 'Information' in data and 'rate limit' in data['Information'].lower():
            return {'error': 'rate_limit', 'message': 'API rate limit exceeded. Please try again later.'}
        
        time_series_key = None
        for key in data.keys():
            if 'Time Series' in key:
                time_series_key = key
                break
        
        if not time_series_key or not data.get(time_series_key):
            return None
        
        time_series = data[time_series_key]
        
        dates = []
        prices = []
        
        sorted_dates = sorted(time_series.keys())
        
        today = datetime.now().date()
        
        if range_type == '1W':
            cutoff_date = today - timedelta(days=7)
        elif range_type == '1M':
            if today.month == 1:
                cutoff_date = today.replace(year=today.year-1, month=12)
            else:
                cutoff_date = today.replace(month=today.month-1)
        elif range_type == '6M':
            months_back = 6
            year = today.year
            month = today.month - months_back
            if month <= 0:
                month += 12
                year -= 1
            cutoff_date = today.replace(year=year, month=month)
        else:
            if today.month == 1:
                cutoff_date = today.replace(year=today.year-1, month=12)
            else:
                cutoff_date = today.replace(month=today.month-1)

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
        
        for date_str in sorted_dates:
            date_data = time_series[date_str]
            
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                timestamp = int(date_obj.timestamp())
                dates.append(timestamp)
                
                close_price = float(date_data.get('4. close', 0))
                prices.append(round(close_price, 2))
                
            except (ValueError, KeyError):
                pass
        
        if not dates:
            return None
        
        current_price = prices[-1] if prices else 0
        
        if len(prices) >= 2:
            period_start_price = prices[0]
            change = round(current_price - period_start_price, 2)
            percent_change = round((change / period_start_price) * 100, 2)
        else:
            change = 0
            percent_change = 0
        
        return {
            'dates': dates,
            'prices': prices,
            'current_price': current_price,
            'change': change,
            'percent_change': percent_change
        }
        
    except Exception:
        return None


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)