# 🚀 Deployment Guide - Financial Risk Agent

Complete step-by-step instructions for deploying to Streamlit Cloud.

## Prerequisites

- GitHub account with a repository
- Streamlit Cloud account (free at share.streamlit.io)
- Git installed locally

## Step 1: Prepare Your Repository

### 1.1 Create a GitHub Repository

```bash
# Initialize git if not already done
git init

# Add all files
git add .
git add .streamlit/

# Commit
git commit -m "Initial commit: Financial Risk Agent"

# Push to GitHub (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/financial-risk-agent.git
git branch -M main
git push -u origin main
```

### 1.2 Verify File Structure

Your repository should have:
```
financial-risk-agent/
├── app.py
├── requirements.txt
├── README.md
├── DEPLOYMENT_GUIDE.md
└── .streamlit/
    └── config.toml
```

**Command to verify:**
```bash
ls -la
cat requirements.txt
```

## Step 2: Deploy to Streamlit Cloud

### 2.1 Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click the **"New app"** button (top-right)
3. Sign in with your GitHub account if prompted
4. Grant Streamlit access to your repositories

### 2.2 Configure Your App

Fill in the deployment form:

| Field | Value |
|-------|-------|
| **Repository** | YOUR_USERNAME/financial-risk-agent |
| **Branch** | main |
| **Main file path** | app.py |

### 2.3 Click "Deploy"

The deployment will take 2-5 minutes. You'll see:
```
Building...
Pushing...
Deploying...
✅ Your app is live!
```

## Step 3: Verify Deployment

### 3.1 Test Core Features

- [ ] App loads without errors
- [ ] Sidebar displays correctly
- [ ] AAPL ticker loads successfully
- [ ] Risk metrics appear on Tab 1
- [ ] Monte Carlo chart displays on Tab 2
- [ ] PDF download works on Tab 3
- [ ] Historical data loads on Tab 4
- [ ] Quick buttons (MSFT, TSLA, etc.) work

### 3.2 Check Performance

Expected load times:
- Initial load: 3-5 seconds
- Ticker analysis: 5-10 seconds
- Chart rendering: <2 seconds

If slow, check Streamlit Cloud logs for cache hits.

## Step 4: Troubleshooting

### Issue: "App is not responding"

**Solution:**
```bash
# Check logs on Streamlit Cloud dashboard
# Logs → View logs → Filter for errors
```

### Issue: "ModuleNotFoundError: No module named 'yfinance'"

**Solution:**
- Verify `requirements.txt` has all dependencies
- Redeploy from Streamlit Cloud dashboard
- Click "Rerun" in the app

### Issue: "PDF download not working"

**Solution:**
- Use FPDF2 (not FPDF): `pip install fpdf2`
- Update requirements.txt: `fpdf2>=2.7.0`
- Redeploy

### Issue: "ValueError: No data found for ticker 'XYZ'"

**This is normal** - displays friendly error message to user. Expected behavior.

### Issue: "Timeout on Monte Carlo"

**Solution:**
- Reduce simulations from 500 to 250 in `MonteCarloSimulator.simulate()`
- Or increase Streamlit timeout in `.streamlit/config.toml`:
```toml
[client]
toolbarMode = "viewer"

[logger]
level = "info"

[theme]
# ... theme settings
```

## Step 5: Advanced Configuration

### 5.1 Custom Domain (Optional)

1. Go to Streamlit Cloud dashboard
2. Select your app
3. Settings → Custom domain
4. Follow instructions for DNS setup

### 5.2 Manage Secrets (if needed)

`.streamlit/secrets.toml` (local, never commit):
```toml
# Example - not needed for this app
# api_key = "your-key-here"
```

### 5.3 App Sharing

Share your app:
- Default URL: `https://share.streamlit.io/YOUR_USERNAME/financial-risk-agent/main`
- Or custom domain if configured
- Anyone can use - no authentication required

## Step 6: Continuous Deployment

### 6.1 Auto-Update on Push

Streamlit Cloud automatically redeploys when you push to GitHub:

```bash
# Make changes locally
echo "# Updated" >> README.md

# Commit and push
git add README.md
git commit -m "Update documentation"
git push origin main

# Wait 2-5 minutes → App updates automatically
```

### 6.2 Manual Rerun (Emergency)

If app is broken:
1. Go to Streamlit Cloud dashboard
2. Select the app
3. Click "Rerun" or "Redeploy"

## Step 7: Monitoring & Maintenance

### 7.1 Check App Health

**Dashboard Metrics:**
- Memory usage: Should be <500MB
- CPU usage: Should be <50%
- Cache hits: Should be >70%
- Error rate: Should be 0%

### 7.2 View Logs

1. Dashboard → Select app
2. "Logs" button (top-right)
3. Filter for errors or warnings

**Common log messages:**
```
INFO - App started
INFO - Cache hit for yfinance data
INFO - User analyzed AAPL
```

### 7.3 Update Dependencies

When updating packages:

```bash
# Update locally
pip install --upgrade yfinance plotly streamlit

# Update requirements
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

## Step 8: Performance Optimization

### 8.1 Cache Management

Current caching strategy:
- Data: 1 hour TTL (3600 seconds)
- Chart rendering: Streamlit automatic

To adjust in `app.py`:
```python
@st.cache_data(ttl=7200)  # Change 3600 to desired seconds
def fetch_data(ticker, period="3y"):
    # ...
```

### 8.2 Simulation Optimization

For slower connections, reduce simulations in `MonteCarloSimulator.simulate()`:
```python
def simulate(current_price, mean_return, std_return, days=252, simulations=250):  # Changed from 500
```

## Step 9: Backup & Version Control

### 9.1 Regular Commits

```bash
# After any changes
git add .
git commit -m "Descriptive message"
git push origin main

# Streamlit Cloud automatically redeploys
```

### 9.2 Rollback If Needed

```bash
# View commit history
git log --oneline

# Revert to previous version
git revert HEAD
git push origin main

# Streamlit Cloud redeploys with old version
```

## Step 10: Share with Others

### 10.1 Public Sharing

Your app is live at:
```
https://share.streamlit.io/YOUR_USERNAME/financial-risk-agent/main
```

Share the URL:
- Twitter: "Check out my Financial Risk Agent!"
- LinkedIn: "Built with Streamlit + GitHub Copilot"
- GitHub: Add to your portfolio
- Forums: Share in relevant communities

### 10.2 Embed in Website (Optional)

```html
<!-- Add to your website -->
<iframe 
  src="https://share.streamlit.io/YOUR_USERNAME/financial-risk-agent/main"
  width="100%" 
  height="800"
  style="border: none;"
></iframe>
```

## Appendix: Quick Commands

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/financial-risk-agent.git
cd financial-risk-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Commit changes
git add .
git commit -m "Description"
git push origin main

# View deployed app
# Go to: https://share.streamlit.io/YOUR_USERNAME/financial-risk-agent/main
```

## Support

- **Streamlit Docs:** https://docs.streamlit.io/
- **Streamlit Cloud:** https://share.streamlit.io/
- **GitHub Issues:** Create in your repository
- **Community:** Streamlit Slack, Reddit r/streamlit

## ✅ Deployment Checklist

- [ ] GitHub repository created and connected
- [ ] All files committed (app.py, requirements.txt, .streamlit/config.toml, README.md)
- [ ] App deployed to Streamlit Cloud
- [ ] Initial ticker (AAPL) loads successfully
- [ ] All 4 tabs work correctly
- [ ] PDF download functions
- [ ] Error handling works (test with invalid ticker)
- [ ] Quick buttons work
- [ ] Sidebar info displays
- [ ] Performance acceptable (<10 seconds per analysis)

---

**🎉 Congratulations! Your Financial Risk Agent is live on Streamlit Cloud!**

Visit: `https://share.streamlit.io/YOUR_USERNAME/financial-risk-agent/main`
