from flask import Flask, request, jsonify
import MetaTrader5 as mt5

app = Flask(__name__)

# Initialize MT5 connection
if not mt5.initialize():
    print("Failed to initialize MT5:", mt5.last_error())
    exit()

@app.route("/")
def index():
    return jsonify({"message": "Trading Bot API is running!"})

@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.json
    action = data.get("action")
    symbol = data.get("symbol")
    volume = data.get("volume", 0.01)
    sl = data.get("sl")
    tp = data.get("tp")

    if action == "buy":
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    elif action == "sell":
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    else:
        return jsonify({"error": "Invalid action. Use 'buy' or 'sell'."}), 400

    request_data = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": f"{action.capitalize()} order via API",
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request_data)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return jsonify({"error": f"Order failed. Error: {result.retcode}"}), 400
    return jsonify({"message": f"{action.capitalize()} order placed successfully!", "order": result.order})

@app.route("/shutdown", methods=["POST"])
def shutdown():
    mt5.shutdown()
    return jsonify({"message": "MT5 connection closed."})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
