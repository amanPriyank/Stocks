# MarketLens

A modern web application for viewing and comparing stock prices using real-time data from Alpha Vantage API.

## Features

- Real-time stock price visualization with interactive charts
- Multiple stock comparison on a single chart
- Flexible time ranges: 1 week, 1 month, 6 months
- Responsive design optimized for all devices
- Professional error handling and user feedback

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MarketLens
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Create a `.env` file in the root directory
   - Add your Alpha Vantage API key:
     ```
     ALPHA_VANTAGE_API_KEY=your_api_key_here
     ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## API Key Setup

1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Sign up for a free account
3. Generate your API key
4. Add the key to your `.env` file

## Project Structure

```
MarketLens/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── styles.css        # CSS styles
    └── script.js         # Frontend JavaScript
```


## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Chart.js
- **API**: Alpha Vantage
- **Styling**: Custom CSS with modern design principles

## License

This project is open source and available under the MIT License.