use serde_json::Value;
use anyhow::Result;

// API function - separate from main
async fn fetch_ticker_reqwest(symbol: &str) -> Result<(String, String)> {
    let url = format!("https://api.coincap.io/v2/assets/{}", symbol);
    println!("📡 Fetching from: {}", url);
    
    let response = reqwest::get(&url).await?;
    
    if !response.status().is_success() {
        anyhow::bail!("HTTP error: {}", response.status());
    }
    
    let json: Value = response.json().await?;
    
    let price = json["data"]["priceUsd"]
        .as_str()
        .unwrap_or("0")
        .to_string();
    
    let symbol_from_api = json["data"]["symbol"]
        .as_str()
        .unwrap_or("N/A")
        .to_string();
    
    Ok((symbol_from_api, price))
}

#[tokio::main]
async fn main() -> Result<()> {
    println!("=== REQWEST EXAMPLE ===\n");
    
    // Call the API function
    match fetch_ticker_reqwest("bitcoin").await {
        Ok((symbol, price)) => {
            println!("✅ Success!");
            println!("Symbol: {}", symbol);
            println!("Price: ${}", price);
        }
        Err(e) => {
            println!("❌ Error: {}", e);
        }
    }
    
    // Fetch multiple tickers
    let tickers = vec!["ethereum", "cardano", "dogecoin"];
    println!("\n--- Fetching multiple tickers ---");
    
    for ticker in tickers {
        match fetch_ticker_reqwest(ticker).await {
            Ok((symbol, price)) => println!("{}: ${}", symbol, price),
            Err(e) => println!("Failed to fetch {}: {}", ticker, e),
        }
    }
    
    Ok(())
}