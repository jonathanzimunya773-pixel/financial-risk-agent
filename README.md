# 📊 Financial Risk Agent - Multi-Agent System

A complete, production-ready Financial Risk Analysis system built with **Streamlit** and designed for deployment on **Streamlit Cloud**.

## 🎯 Features

### 4 Intelligent Agents

1. **Data Collector Agent** 🔍
   - Fetches 3 years of historical stock data using yfinance
   - Caches data for 1 hour to optimize performance
   - Returns current price, daily returns, and closing prices
   - Robust error handling for invalid tickers

2. **Risk Calculator Agent** 📊
   - Historical Value at Risk (VaR) at 95% and 99% confidence levels
   - Conditional Value at Risk (CVaR) / Expected Shortfall
   - Parametric VaR using normal distribution (scipy)
   - Annualized volatility
   - Sharpe Ratio (risk-adjusted returns)
   - Maximum Drawdown analysis
   - Dollar amount risk exposures

3. **Monte Carlo Simulator Agent** 🎲
   - 500 simulations using Geometric Brownian Motion (GBM)
   - Vectorized numpy operations (no loops) for speed
   - Projects 1-year forward price distribution
   - Calculates 5th, 50th, 95th percentile prices
   - Computes probability of loss
   - Optimized for Streamlit Cloud performance

4. **Report Generator Agent** 📋
   - Generates risk ratings (LOW/MEDIUM/HIGH) based on VaR thresholds
   - Investment recommendations (BUY/SELL/HOLD)
   - Detailed natural language summary
   - No external APIs or LLMs required
   - Interpretation thresholds for each metric

## 🚀 Quick Start

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/financial-risk-agent.git
cd financial-risk-agent
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the Streamlit app:**
```bash
streamlit run app.py
```

5. **Open in browser:**
The app will automatically open at `http://localhost:8501`

### Deploy to Streamlit Cloud

1. **Push to GitHub:**
```bash
git add .
git commit -m "Deploy Financial Risk Agent"
git push origin main
```

2. **Deploy via Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Click "New app"
   - Select your repository and branch
   - Set main file path to `app.py`
   - Click "Deploy"

## 📋 Project Structure

```
financial-risk-agent/
├── app.py                 # Main application (all code in one file)
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
└── README.md             # This file
```

## 🔧 Technical Details

### Risk Metrics Explained

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **VaR 95%** | 5th percentile of returns | Max daily loss 95% of the time |
| **VaR 99%** | 1st percentile of returns | Max daily loss 99% of the time |
| **CVaR** | Mean of returns ≤ VaR | Average loss in worst-case scenarios |
| **Volatility** | Std Dev × √252 | Annualized price fluctuation |
| **Sharpe Ratio** | (Return × √252) / Volatility | Risk-adjusted return quality |
| **Max Drawdown** | Min(Cumulative / Max - 1) | Worst peak-to-trough decline |

### Monte Carlo Simulation

Uses Geometric Brownian Motion (GBM) for stock price paths:

```
S_t = S_0 * exp((μ - σ²/2)dt + σ * √dt * Z)
```

Where:
- `S_0` = Current price
- `μ` = Mean daily return
- `σ` = Std dev of returns
- `dt` = 1/252 (trading days)
- `Z` ~ N(0,1) (standard normal random variable)

### Performance Optimization

- **Vectorized Operations**: All simulations use numpy arrays (no Python loops)
- **Data Caching**: @st.cache_data decorator with 1-hour TTL
- **Efficient Simulations**: 500 paths instead of expensive 10,000+
- **Streamlit Cloud Ready**: No external APIs, databases, or GPU requirements

## 🎨 User Interface

### Tabs

1. **Risk Metrics** 📈
   - Color-coded metric cards
   - VaR, CVaR, Volatility, Sharpe Ratio
   - Max Drawdown (red-highlighted if severe)
   - Dollar risk amounts

2. **Monte Carlo** 🎲
   - Interactive histogram of simulated prices
   - Percentile markers (5th, 50th, 95th)
   - Probability of loss gauge
   - Statistical summary

3. **Report** 📋
   - Risk rating badge (LOW/MEDIUM/HIGH)
   - Investment recommendation (BUY/SELL/HOLD)
   - Detailed analysis summary
   - Interpretation rules table
   - PDF download button

4. **Historical Data** 📊
   - 90-day price chart
   - Recent 10-day price table
   - Daily change calculations

### Quick Features

- **Quick Buttons**: AAPL, MSFT, TSLA, GOOGL, NVDA, AMZN
- **Sidebar**: Agent descriptions, mathematical models, credits
- **Responsive Design**: Works on desktop, tablet, mobile
- **Dark Theme**: Plotly dark template for eye comfort

## 📦 Dependencies

```
streamlit>=1.28.0       # Web framework
yfinance>=0.2.32        # Stock data
pandas>=2.0.0           # Data manipulation
numpy>=1.24.0           # Numerical computing
scipy>=1.10.0           # Statistical functions
plotly>=5.17.0          # Interactive charts
fpdf2>=2.7.0            # PDF generation
```

## ✅ Quality Assurance

### Testing on Streamlit Cloud

The app is production-ready and tested for:
- ✅ Invalid ticker handling
- ✅ Network error recovery
- ✅ Empty data handling
- ✅ PDF generation on cloud environment
- ✅ Performance with 500 Monte Carlo simulations
- ✅ Data caching and TTL management
- ✅ Session state management
- ✅ Responsive UI on all screen sizes

### Error Messages

All errors display user-friendly messages:
- "Ticker 'XYZ' not found. Try MSFT, AAPL, TSLA..."
- "Error fetching data: [specific reason]"
- "Failed to calculate risk metrics for [ticker]"

## 🔒 Security

- No API keys required
- No external authentication
- Uses only public stock market data
- All processing done on Streamlit's infrastructure
- No data persistence or logging

## 📊 Sample Output

### Risk Metrics Example (AAPL)
```
Current Price: $150.25
VaR 95%: -1.50%
VaR 99%: -2.89%
CVaR 95%: -2.15%
Volatility: 24.3%
Sharpe Ratio: 1.42
Max Drawdown: -28.5%
```

### Recommendation Example
```
RISK RATING: 🟢 LOW RISK
RECOMMENDATION: → BUY
PROBABILITY OF LOSS: 45.2%
```

## 🚀 Deployment Tips

1. **Streamlit Cloud Free Tier:**
   - Good for demo and development
   - 1 GB memory limit
   - No GPU needed

2. **Optimize Performance:**
   - Data caching is already enabled
   - 500 simulations balances accuracy vs speed
   - Consider reducing simulations to 250 if running slow

3. **Monitor App:**
   - Check Streamlit Cloud dashboard
   - Monitor cache hits
   - Adjust TTL based on usage patterns

## 📚 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Value at Risk (Wikipedia)](https://en.wikipedia.org/wiki/Value_at_risk)
- [Sharpe Ratio](https://www.investopedia.com/terms/s/sharperatio.asp)
- [Monte Carlo Simulation](https://en.wikipedia.org/wiki/Monte_Carlo_method)
- [Geometric Brownian Motion](https://en.wikipedia.org/wiki/Geometric_Brownian_motion)

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional risk models (GARCH, Historical Simulation)
- Option pricing integrations
- Portfolio analysis
- Real-time data feeds
- Advanced charting

## 📄 License

MIT License - Use freely in personal and commercial projects

## 👨‍💻 Author

**Jonathan Zimunya**
- Education: MUST (Financial Mathematics)
- Built with: GitHub Copilot
- Hackathon: Agents League

## ⚠️ Disclaimer

This tool is for educational and informational purposes only. It should not be considered as financial advice. Always consult with a qualified financial advisor before making investment decisions. Past performance does not guarantee future results.

---

**Questions or Issues?**
- Check the error messages in the app
- Verify your internet connection
- Try a different ticker
- Refresh the browser

**Happy Analyzing! 📊**
