# finsight_agent/tools.py
# ADK function tool docs:
# https://google.github.io/adk-docs/tools-custom/function-tools/

import yfinance as yf

def get_market_data(ticker: str) -> dict:
    """
    Fetches the latest market data for a given stock ticker symbol.
    
    Use this when the user asks about a stock price, market data, or financial 
    information for a specific ticker such as AAPL, TSLA, GOOGL, or BTC-USD.
    
    Args:
        ticker: The stock or crypto ticker symbol, e.g. 'AAPL', 'BTC-USD'.
        
    Returns:
        A dict with 'status' and either 'data' (on success) or 'error_message' (on failure).
    """
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        # Extract the fields most useful for a finance agent
        data = {
            "ticker": ticker.upper(),
            "name": info.get("longName", "N/A"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "previous_close": info.get("previousClose"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "volume": info.get("volume"),
            "market_cap": info.get("marketCap"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "pe_ratio": info.get("trailingPE"),
            "currency": info.get("currency", "USD"),
        }
        return {"status": "success", "data": data}
        
    except Exception as e:
        return {
            "status": "error",
            "error_message": f"Could not fetch data for '{ticker}': {str(e)}",
        }
    
def compute_risk_metrics(market_data: dict) -> dict:
    """Computes basic risk metrics from a market data dictionary returned by get_market_data.

    Use this when you need to evaluate the risk level of a stock given its price
    range, volume, and PE ratio.

    Args:
        market_data: The 'data' dict from a get_market_data result, containing
          current_price, 52_week_high, 52_week_low, volume, and pe_ratio fields.

    Returns:
        A dict with 'status' and either 'metrics' (on success) or
        'error_message' (on failure).
    """
    try:
        price = float(market_data.get("current_price") or 0)
        high_52 = float(market_data.get("52_week_high") or 0)
        low_52 = float(market_data.get("52_week_low") or 0)
        volume = int(market_data.get("volume") or 0)
        pe = market_data.get("pe_ratio")

        if price <= 0:
            return {
                "status": "error",
                "error_message": "Invalid price in market data.",
            }

        # Volatility: 52-week range as % of current price
        volatility = round((high_52 - low_52) / price * 100, 2)

        # Simple risk classification
        if volatility > 60:
            risk_level = "high"
        elif volatility > 30:
            risk_level = "moderate"
        else:
            risk_level = "low"

        metrics = {
            "volatility_pct": volatility,
            "risk_level": risk_level,
            "pe_ratio": pe,
            "volume": volume,
            "price_range_52w": f"{low_52} - {high_52}",
        }

        return {"status": "success", "metrics": metrics}

    except Exception as e:
        return {"status": "error", "error_message": str(e)}