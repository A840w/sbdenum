use rust_socketio::{ClientBuilder, Payload};
use std::time::Duration;

fn main() {
    // Connect to Coindcx Socket.IO server
    let mut socket = ClientBuilder::new("https://stream.coindcx.com")
        .on("connect", |_, _| {
            println!("[COINDCX] Connected. Subscribing to LTP stream...");
        })
        .on("event", |payload, _| {
            if let Payload::String(data) = payload {
                println!("Received event: {}", data);
            }
        })
        .connect()
        .expect("Connection failed");

    // Subscribe to channel (similar to sio.emit in Python)
    socket.emit("join", "B-TON_USDT@prices-futures").unwrap();

    // Keep alive for demo
    std::thread::sleep(Duration::from_secs(30));
}
