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