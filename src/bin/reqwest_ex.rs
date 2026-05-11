use serde_json::Value;
use anyhow::Result;
use colored::*;
async fn fetch_ticker_req(symbol: &str) -> Result<(String, String)> {
    // Implementation for fetching ticker data
    let url = format!("https://api.binance.com/api/v3/ticker/price?symbol={}", symbol);
    println!("fetching ticker data from: {}", url);
    let response = reqwest::get(&url).await?;
    Ok((url, symbol.into()))
}
