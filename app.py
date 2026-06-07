import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
from fpdf import FPDF
import base64
from io import BytesIO
from scipy import stats

# ============================================================================
# AGENT 1: DATA COLLECTOR
# ============================================================================
class DataCollector:
    """Agent 1: Fetches historical stock data using yfinance"""
    
    @staticmethod
    @st.cache_data(ttl=3600)
    def fetch_data(ticker, period="3y"):
        """
        Fetch 3 years of daily data for a stock ticker
        Returns: (current_price, returns_array, closing_prices_array) or (None, None, None)
        """
        try:
            # Download data
            data = yf.download(ticker, period=period, progress=False)
            
            if data.empty:
                return None, None, None, f"No data found for ticker '{ticker}'"
            
            # Get closing prices
            closing_prices = data['Close'].values
            current_price = closing_prices[-1]
            
            # Calculate daily returns
            returns = np.diff(closing_prices) / closing_prices[:-1]
            
            return current_price, returns, closing_prices, None
            
        except Exception as e:
            return None, None, None, f"Error fetching data for '{ticker}': {str(e)}"


# ============================================================================
# AGENT 2: RISK CALCULATOR
# ============================================================================
class RiskCalculator:
    """Agent 2: Calculates financial risk metrics from returns data"""
    
    @staticmethod
    def calculate_metrics(returns, current_price):
        """
        Calculate comprehensive risk metrics
        Input: returns array (numpy), current_price (float)
        Output: dictionary with all risk metrics
        """
        try:
            # Handle edge cases
            if returns is None or len(returns) == 0:
                return None
            
            # Historical VaR (Value at Risk)
            historical_var_95 = np.percentile(returns, 5)
            historical_var_99 = np.percentile(returns, 1)
            
            # CVaR (Conditional VaR) - Expected Shortfall
            cvar_95 = np.mean(returns[returns <= historical_var_95])
            
            # Parametric VaR using normal distribution
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            parametric_var_95 = stats.norm.ppf(0.05) * std_return + mean_return
            
            # Volatility (annualized)
            volatility_annualized = std_return * np.sqrt(252)
            
            # Sharpe Ratio (assuming 0% risk-free rate)
            if std_return != 0:
                sharpe_ratio = (mean_return * np.sqrt(252)) / volatility_annualized
            else:
                sharpe_ratio = 0
            
            # Maximum Drawdown
            cumulative_returns = np.cumprod(1 + returns)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = np.min(drawdown)
            
            # VaR in dollar amounts
            var_95_amount = current_price * historical_var_95
            var_99_amount = current_price * historical_var_99
            
            return {
                'historical_var_95': historical_var_95,
                'historical_var_99': historical_var_99,
                'cvar_95': cvar_95,
                'parametric_var_95': parametric_var_95,
                'volatility_annualized': volatility_annualized,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'var_95_amount': var_95_amount,
                'var_99_amount': var_99_amount,
                'mean_daily_return_pct': mean_return * 100,
                'std_daily_return_pct': std_return * 100
            }
            
        except Exception as e:
            return None


# ============================================================================
# AGENT 3: MONTE CARLO SIMULATOR
# ============================================================================
class MonteCarloSimulator:
    """Agent 3: Simulates future price paths using Monte Carlo method"""
    
    @staticmethod
    def simulate(current_price, mean_return, std_return, days=252, simulations=500):
        """
        Monte Carlo simulation using Geometric Brownian Motion
        Formula: S_t = S_0 * exp((μ - σ²/2)dt + σ * sqrt(dt) * Z)
        
        Input: current_price, mean_return, std_return, days, simulations
        Output: dictionary with simulation results
        """
        try:
            dt = 1/252  # Daily time step
            
            # Vectorized simulation (NO LOOPS)
            # Shape: (simulations, days)
            Z = np.random.standard_normal((simulations, days))
            
            # Calculate price paths using vectorized operations
            price_paths = current_price * np.exp(
                np.cumsum(
                    (mean_return - 0.5 * std_return**2) * dt + std_return * np.sqrt(dt) * Z,
                    axis=1
                )
            )
            
            # Extract final prices
            final_prices = price_paths[:, -1]
            
            # Calculate statistics
            percentile_5 = np.percentile(final_prices, 5)
            percentile_50 = np.percentile(final_prices, 50)
            percentile_95 = np.percentile(final_prices, 95)
            probability_of_loss = np.sum(final_prices < current_price) / len(final_prices)
            
            return {
                'final_prices': final_prices,
                'percentile_5': percentile_5,
                'percentile_50': percentile_50,
                'percentile_95': percentile_95,
                'probability_of_loss': probability_of_loss,
                'histogram_data': final_prices
            }
            
        except Exception as e:
            return None


# ============================================================================
# AGENT 4: REPORT GENERATOR
# ============================================================================
class ReportGenerator:
    """Agent 4: Generates risk ratings and recommendations (NO API, NO LLM)"""
    
    @staticmethod
    def generate_report(risk_metrics, ticker, current_price):
        """
        Generate investment recommendation based on risk metrics
        Input: risk_metrics dict, ticker, current_price
        Output: dictionary with rating, recommendation, and interpretation
        """
        try:
            var_95 = risk_metrics['historical_var_95']
            sharpe_ratio = risk_metrics['sharpe_ratio']
            max_drawdown = risk_metrics['max_drawdown']
            volatility = risk_metrics['volatility_annualized']
            
            # Risk Rating
            if var_95 > -0.02:
                risk_rating = "LOW"
                risk_color = "🟢"
            elif var_95 > -0.05:
                risk_rating = "MEDIUM"
                risk_color = "🟡"
            else:
                risk_rating = "HIGH"
                risk_color = "🔴"
            
            # Recommendation
            if var_95 > -0.02 and sharpe_ratio > 1:
                recommendation = "BUY"
                rec_color = "green"
            elif var_95 < -0.05 or max_drawdown < -0.30:
                recommendation = "SELL"
                rec_color = "red"
            else:
                recommendation = "HOLD"
                rec_color = "orange"
            
            # Summary text
            summary_text = f"""
            **Analysis for {ticker}** (Current Price: ${current_price:.2f})
            
            **Risk Assessment:**
            The 95% Value at Risk (VaR) is {var_95*100:.2f}%, meaning there's a 95% chance the daily loss won't exceed {var_95*100:.2f}%. 
            The stock exhibits {volatility*100:.2f}% annualized volatility. The Sharpe Ratio of {sharpe_ratio:.2f} indicates 
            {'strong risk-adjusted returns' if sharpe_ratio > 1 else 'weak risk-adjusted returns'}.
            
            **Historical Performance:**
            Maximum drawdown recorded was {max_drawdown*100:.2f}%, reflecting the worst peak-to-trough decline. 
            This is {'within acceptable ranges' if max_drawdown > -0.30 else 'concerning and suggests high drawdown risk'}.
            
            **Recommendation:**
            Based on the risk metrics analysis, the recommendation is to **{recommendation}** this stock.
            This is a {risk_rating} risk investment suitable for {'conservative investors' if risk_rating == 'LOW' else 'aggressive investors' if risk_rating == 'HIGH' else 'moderate investors'}.
            """
            
            # Interpretation rules
            interpretation_rules = {
                'VaR 95% Threshold': '-2% (Good) to -5% (Moderate) to ≤-5% (High)',
                'Sharpe Ratio': '>1 (Strong) to 0-1 (Moderate) to <0 (Weak)',
                'Max Drawdown': '>-30% (Good) to -30% to -50% (Moderate) to <-50% (High)',
                'Volatility': '<20% (Low) to 20-40% (Moderate) to >40% (High)'
            }
            
            return {
                'risk_rating': risk_rating,
                'risk_color': risk_color,
                'recommendation': recommendation,
                'recommendation_color': rec_color,
                'summary_text': summary_text,
                'interpretation_rules': interpretation_rules
            }
            
        except Exception as e:
            return None


# ============================================================================
# ORCHESTRATOR FUNCTION
# ============================================================================
def analyze_stock(ticker):
    """
    Orchestrator: Runs all 4 agents in sequence
    Returns full results dict or error dict
    """
    # Agent 1: Data Collection
    current_price, returns, closing_prices, error = DataCollector.fetch_data(ticker)
    if error:
        return {'error': error, 'success': False}
    
    # Agent 2: Risk Calculation
    risk_metrics = RiskCalculator.calculate_metrics(returns, current_price)
    if risk_metrics is None:
        return {'error': f'Failed to calculate risk metrics for {ticker}', 'success': False}
    
    # Agent 3: Monte Carlo Simulation
    mc_results = MonteCarloSimulator.simulate(
        current_price,
        risk_metrics['mean_daily_return_pct'] / 100,
        risk_metrics['std_daily_return_pct'] / 100,
        days=252,
        simulations=500
    )
    if mc_results is None:
        return {'error': f'Failed to run Monte Carlo simulation for {ticker}', 'success': False}
    
    # Agent 4: Report Generation
    report = ReportGenerator.generate_report(risk_metrics, ticker, current_price)
    if report is None:
        return {'error': f'Failed to generate report for {ticker}', 'success': False}
    
    return {
        'success': True,
        'ticker': ticker,
        'current_price': current_price,
        'risk_metrics': risk_metrics,
        'mc_results': mc_results,
        'report': report,
        'closing_prices': closing_prices
    }


# ============================================================================
# PDF GENERATOR
# ============================================================================
def create_pdf(results, ticker):
    """
    Generate PDF report with all metrics
    Returns PDF as bytes for download
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        
        # Title
        pdf.cell(0, 10, f"Financial Risk Report - {ticker}", ln=True, align="C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        pdf.ln(5)
        
        # Current Price
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Current Price: ${results['current_price']:.2f}", ln=True)
        pdf.ln(3)
        
        # Risk Metrics
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Risk Metrics:", ln=True)
        pdf.set_font("Arial", "", 10)
        
        metrics = results['risk_metrics']
        pdf.cell(0, 8, f"Historical VaR 95%: {metrics['historical_var_95']*100:.4f}%", ln=True)
        pdf.cell(0, 8, f"Historical VaR 99%: {metrics['historical_var_99']*100:.4f}%", ln=True)
        pdf.cell(0, 8, f"CVaR 95%: {metrics['cvar_95']*100:.4f}%", ln=True)
        pdf.cell(0, 8, f"Parametric VaR 95%: {metrics['parametric_var_95']*100:.4f}%", ln=True)
        pdf.cell(0, 8, f"Volatility (Annualized): {metrics['volatility_annualized']*100:.2f}%", ln=True)
        pdf.cell(0, 8, f"Sharpe Ratio: {metrics['sharpe_ratio']:.4f}", ln=True)
        pdf.cell(0, 8, f"Max Drawdown: {metrics['max_drawdown']*100:.2f}%", ln=True)
        pdf.cell(0, 8, f"VaR 95% Amount: ${metrics['var_95_amount']:.2f}", ln=True)
        pdf.cell(0, 8, f"VaR 99% Amount: ${metrics['var_99_amount']:.2f}", ln=True)
        pdf.ln(3)
        
        # Recommendation
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Recommendation:", ln=True)
        pdf.set_font("Arial", "", 10)
        
        report = results['report']
        pdf.cell(0, 8, f"Risk Rating: {report['risk_rating']}", ln=True)
        pdf.cell(0, 8, f"Recommendation: {report['recommendation']}", ln=True)
        pdf.ln(3)
        
        # Summary
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Summary:", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, report['summary_text'].replace('**', '').replace('\n', ' '))
        
        # Convert to bytes
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        return pdf_bytes
        
    except Exception as e:
        return None


# ============================================================================
# STREAMLIT UI
# ============================================================================
st.set_page_config(
    page_title="Financial Risk Agent",
    layout="wide",
    page_icon="📊"
)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 About This App")
    st.markdown("""
    **Financial Risk Agent** - A multi-agent system for comprehensive stock risk analysis.
    
    **4 Intelligent Agents:**
    1. **Data Collector**: Fetches 3 years of historical data
    2. **Risk Calculator**: Computes VaR, CVaR, Sharpe Ratio, Volatility
    3. **Monte Carlo Simulator**: Projects 1-year forward price distribution
    4. **Report Generator**: Generates investment recommendations
    
    **Mathematical Models:**
    - **Value at Risk (VaR)**: Historical & Parametric
    - **Conditional VaR**: Expected Shortfall
    - **Sharpe Ratio**: Risk-adjusted returns
    - **Geometric Brownian Motion**: Price simulation
    """)
    
    st.markdown("---")
    st.markdown("""
    **Built by:** Jonathan Zimunya - MUST (Financial Mathematics)
    
    **Built with:** GitHub Copilot
    """)

# Main title
st.markdown("# 📊 Financial Risk Agent")
st.markdown("### Multi-Agent System for Stock Risk Analysis | Built for Agents League Hackathon")

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    ticker_input = st.text_input("Enter Stock Ticker:", value="AAPL", placeholder="e.g., MSFT, TSLA, GOOGL")
with col2:
    st.write("")
    analyze_btn = st.button("📊 Analyze", use_container_width=True, key="analyze_btn")

# Quick buttons
st.markdown("#### Quick Analysis:")
quick_tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "NVDA", "AMZN"]
cols = st.columns(6)
for idx, quick_ticker in enumerate(quick_tickers):
    with cols[idx]:
        if st.button(quick_ticker, use_container_width=True, key=f"quick_{quick_ticker}"):
            ticker_input = quick_ticker
            analyze_btn = True

# Analysis
if analyze_btn or 'results' in st.session_state:
    if analyze_btn:
        with st.spinner("🔄 4 agents analyzing... This may take a moment"):
            results = analyze_stock(ticker_input.upper())
            st.session_state.results = results
            st.session_state.ticker = ticker_input.upper()
    else:
        results = st.session_state.results
    
    if not results.get('success', False):
        st.error(f"❌ {results.get('error', 'Unknown error occurred')}")
        st.info(f"💡 Try one of these tickers: AAPL, MSFT, TSLA, GOOGL, NVDA, AMZN")
    else:
        ticker = results['ticker']
        current_price = results['current_price']
        risk_metrics = results['risk_metrics']
        mc_results = results['mc_results']
        report = results['report']
        
        # Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Risk Metrics", "🎲 Monte Carlo", "📋 Report", "📊 Historical Data"])
        
        # TAB 1: Risk Metrics
        with tab1:
            st.markdown(f"## Risk Metrics for {ticker}")
            st.markdown(f"**Current Price:** ${current_price:.2f}")
            
            # Create metric cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                var_95_pct = risk_metrics['historical_var_95'] * 100
                color = "🔴" if var_95_pct < -5 else "🟡" if var_95_pct < -2 else "🟢"
                st.metric(
                    f"{color} VaR 95%",
                    f"{var_95_pct:.2f}%",
                    delta=f"${risk_metrics['var_95_amount']:.2f}"
                )
            
            with col2:
                var_99_pct = risk_metrics['historical_var_99'] * 100
                st.metric(
                    "VaR 99%",
                    f"{var_99_pct:.2f}%",
                    delta=f"${risk_metrics['var_99_amount']:.2f}"
                )
            
            with col3:
                cvar_pct = risk_metrics['cvar_95'] * 100
                st.metric("CVaR 95%", f"{cvar_pct:.2f}%")
            
            with col4:
                vol_pct = risk_metrics['volatility_annualized'] * 100
                st.metric("Volatility", f"{vol_pct:.2f}%")
            
            col5, col6, col7, col8 = st.columns(4)
            
            with col5:
                sharpe = risk_metrics['sharpe_ratio']
                color = "🟢" if sharpe > 1 else "🟡" if sharpe > 0 else "🔴"
                st.metric(f"{color} Sharpe Ratio", f"{sharpe:.4f}")
            
            with col6:
                max_dd = risk_metrics['max_drawdown'] * 100
                color = "🟢" if max_dd > -30 else "🟡" if max_dd > -50 else "🔴"
                st.metric(f"{color} Max Drawdown", f"{max_dd:.2f}%")
            
            with col7:
                mean_ret = risk_metrics['mean_daily_return_pct']
                st.metric("Mean Daily Return", f"{mean_ret:.4f}%")
            
            with col8:
                std_ret = risk_metrics['std_daily_return_pct']
                st.metric("Std Dev (Daily)", f"{std_ret:.4f}%")
            
            # Parametric VaR
            st.markdown("---")
            col_param1, col_param2 = st.columns(2)
            with col_param1:
                param_var = risk_metrics['parametric_var_95'] * 100
                st.metric("Parametric VaR 95% (Normal Dist)", f"{param_var:.2f}%")
            with col_param2:
                st.info("📌 Parametric VaR assumes normal distribution. Historical VaR is more robust for non-normal returns.")
        
        # TAB 2: Monte Carlo Simulation
        with tab2:
            st.markdown(f"## 1-Year Price Forecast (Monte Carlo Simulation)")
            st.markdown(f"**Based on:** 500 simulations | **Current Price:** ${current_price:.2f}")
            
            # Histogram
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=mc_results['histogram_data'],
                nbinsx=50,
                name="Simulated Prices",
                marker=dict(color='rgba(0, 150, 255, 0.7)')
            ))
            fig.add_vline(x=mc_results['percentile_5'], line_dash="dash", line_color="red", 
                         annotation_text=f"5th %ile: ${mc_results['percentile_5']:.2f}")
            fig.add_vline(x=mc_results['percentile_50'], line_dash="dash", line_color="green",
                         annotation_text=f"50th %ile: ${mc_results['percentile_50']:.2f}")
            fig.add_vline(x=mc_results['percentile_95'], line_dash="dash", line_color="gold",
                         annotation_text=f"95th %ile: ${mc_results['percentile_95']:.2f}")
            fig.add_vline(x=current_price, line_dash="solid", line_color="black",
                         annotation_text=f"Current: ${current_price:.2f}")
            
            fig.update_layout(
                title="Distribution of Simulated 1-Year Prices",
                xaxis_title="Price ($)",
                yaxis_title="Frequency",
                template="plotly_dark",
                hovermode="x unified",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("5th Percentile", f"${mc_results['percentile_5']:.2f}",
                         delta=f"{((mc_results['percentile_5']/current_price - 1)*100):.1f}%")
            with col2:
                st.metric("50th Percentile", f"${mc_results['percentile_50']:.2f}",
                         delta=f"{((mc_results['percentile_50']/current_price - 1)*100):.1f}%")
            with col3:
                st.metric("95th Percentile", f"${mc_results['percentile_95']:.2f}",
                         delta=f"{((mc_results['percentile_95']/current_price - 1)*100):.1f}%")
            with col4:
                prob_loss = mc_results['probability_of_loss'] * 100
                st.metric("Prob. of Loss", f"{prob_loss:.1f}%")
            
            # Probability bar
            st.markdown("---")
            st.markdown("**Probability of Loss (Price < Current):**")
            st.progress(mc_results['probability_of_loss'])
            st.caption(f"{mc_results['probability_of_loss']*100:.1f}% chance of loss within 1 year")
        
        # TAB 3: Report
        with tab3:
            st.markdown(f"## Investment Analysis Report")
            
            # Risk Rating Badge
            st.markdown("### Risk Rating")
            color_map = {"LOW": "green", "MEDIUM": "orange", "HIGH": "red"}
            badge_color = color_map.get(report['risk_rating'], 'gray')
            st.markdown(
                f"<h2 style='color: {badge_color}; font-size: 2.5em;'>{report['risk_color']} {report['risk_rating']} RISK</h2>",
                unsafe_allow_html=True
            )
            
            # Recommendation
            st.markdown("### Investment Recommendation")
            rec_color_map = {"BUY": "green", "SELL": "red", "HOLD": "orange"}
            rec_color = rec_color_map.get(report['recommendation'], 'gray')
            st.markdown(
                f"<h2 style='color: {rec_color}; font-size: 2em;'>→ {report['recommendation']}</h2>",
                unsafe_allow_html=True
            )
            
            # Summary
            st.markdown("---")
            st.markdown("### Analysis Summary")
            st.markdown(report['summary_text'])
            
            # Interpretation Rules
            st.markdown("---")
            st.markdown("### Interpretation Rules")
            rules_df = pd.DataFrame(list(report['interpretation_rules'].items()), 
                                   columns=['Metric', 'Thresholds'])
            st.table(rules_df)
            
            # Download PDF
            st.markdown("---")
            pdf_bytes = create_pdf(results, ticker)
            if pdf_bytes:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"Financial_Risk_Report_{ticker}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("⚠️ PDF generation encountered an issue")
        
        # TAB 4: Historical Data
        with tab4:
            st.markdown(f"## Historical Price Data - {ticker}")
            
            # Get last 90 days for chart
            closing_prices = results['closing_prices']
            if len(closing_prices) > 90:
                chart_prices = closing_prices[-90:]
            else:
                chart_prices = closing_prices
            
            # Create line chart
            df_chart = pd.DataFrame({
                'Price': chart_prices
            })
            
            fig_chart = go.Figure()
            fig_chart.add_trace(go.Scatter(
                y=df_chart['Price'],
                mode='lines',
                name='Close Price',
                line=dict(color='#1f77b4', width=2)
            ))
            fig_chart.update_layout(
                title="Last 90 Days Price Chart",
                yaxis_title="Price ($)",
                xaxis_title="Days",
                template="plotly_dark",
                height=400,
                hovermode="x unified"
            )
            st.plotly_chart(fig_chart, use_container_width=True)
            
            # Recent prices table
            st.markdown("### Recent Prices (Last 10 Days)")
            if len(closing_prices) > 10:
                recent_prices = closing_prices[-10:]
            else:
                recent_prices = closing_prices
            
            df_recent = pd.DataFrame({
                'Day': range(1, len(recent_prices) + 1),
                'Price': recent_prices,
                'Change': [np.nan] + list(np.diff(recent_prices))
            })
            
            st.dataframe(
                df_recent.style.format({
                    'Price': '${:.2f}',
                    'Change': '${:+.2f}'
                }),
                use_container_width=True
            )

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>"
    "Built with GitHub Copilot | "
    "4 Agents: Data Collector → Risk Calculator → Monte Carlo → Report Generator"
    "</div>",
    unsafe_allow_html=True
)

if __name__ == "__main__":
    pass
