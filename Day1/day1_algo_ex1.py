from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState
from typing import *
import jsonpickle
import json

# Define constants
POSITION_LIMIT = 50
DEFAULT_FAIR_VALUES = {
    "RAINFOREST_RESIN": 100,
    "KELP": 100,
    "SQUID_INK": 100
}

# Define thresholds for deviation from fair value for each product.
# These thresholds indicate the minimum relative deviation to trigger a trade.
THRESHOLDS = {
    "RAINFOREST_RESIN": 0.005,  # 0.5% deviation (stable)
    "KELP": 0.01,              # 1% deviation (moderate)
    "SQUID_INK": 0.02          # 2% deviation (volatile)
}

class Trader:
    
    def run(self, state: TradingState):
        # Print traderData and observations for debugging/logging.
        print("traderData:", state.traderData)
        print("Observations:", state.observations)
        
        result = {}
        
        # Attempt to load previous trader state from traderData.
        # We store a dictionary with structure: {"averages": {product: {"avg": float, "count": int}, ...}}
        try:
            trader_info = jsonpickle.decode(state.traderData)
            if not isinstance(trader_info, dict) or "averages" not in trader_info:
                trader_info = {"averages": {}}
        except Exception as e:
            trader_info = {"averages": {}}
        
        averages = trader_info["averages"]
        
        # Loop through each product available in the current state.
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            # Get current position (defaulting to 0 if not present)
            current_position = state.position.get(product, 0)
            
            # Compute the mid-price from the order book if available.
            mid_price = None
            if order_depth.buy_orders and order_depth.sell_orders:
                best_bid = max(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = (best_bid + best_ask) / 2
            elif order_depth.buy_orders:
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = best_bid
            elif order_depth.sell_orders:
                best_ask = min(order_depth.sell_orders.keys())
                mid_price = best_ask
            
            # Update our moving average estimate for the product.
            # If mid_price is available, update the moving average.
            if mid_price is not None:
                if product in averages:
                    prev_avg = averages[product]["avg"]
                    count = averages[product]["count"]
                    new_count = count + 1
                    new_avg = (prev_avg * count + mid_price) / new_count
                    averages[product]["avg"] = new_avg
                    averages[product]["count"] = new_count
                else:
                    averages[product] = {"avg": mid_price, "count": 1}
            
            # Use the moving average as fair value if available, else default.
            fair_value = averages.get(product, {}).get("avg", DEFAULT_FAIR_VALUES.get(product, 100))
            threshold = THRESHOLDS.get(product, 0.01)
            
            # --- BUY ORDER LOGIC (taking advantage if the market sell price is well below our fair value) ---
            if order_depth.sell_orders:
                best_ask_price = min(order_depth.sell_orders.keys())
                ask_volume = order_depth.sell_orders[best_ask_price]
                # ask_volume is negative; use its absolute value.
                available_volume = abs(ask_volume)
                # Check if the best ask is lower than the threshold-adjusted fair value.
                if best_ask_price < fair_value * (1 - threshold):
                    # Calculate maximum volume allowed (cannot exceed position limit when buying).
                    max_buy_allowed = POSITION_LIMIT - current_position
                    trade_volume = min(available_volume, max_buy_allowed)
                    if trade_volume > 0:
                        print("PRODUCT:", product, "- BUY", trade_volume, "at", best_ask_price, "since",
                              best_ask_price, "<", fair_value, "*(1 -", threshold, ")")
                        orders.append(Order(product, best_ask_price, trade_volume))
            
            # --- SELL ORDER LOGIC (taking advantage if the market buy price is well above our fair value) ---
            if order_depth.buy_orders:
                best_bid_price = max(order_depth.buy_orders.keys())
                bid_volume = order_depth.buy_orders[best_bid_price]
                # For buy orders, bid_volume is positive.
                available_volume = bid_volume
                # Check if the best bid is higher than the threshold-adjusted fair value.
                if best_bid_price > fair_value * (1 + threshold):
                    # Calculate maximum volume allowed for selling.
                    # For a sell order, we can sell up to (POSITION_LIMIT + current_position) units.
                    max_sell_allowed = POSITION_LIMIT + current_position
                    trade_volume = min(available_volume, max_sell_allowed)
                    if trade_volume > 0:
                        print("PRODUCT:", product, "- SELL", trade_volume, "at", best_bid_price, "since",
                              best_bid_price, ">", fair_value, "*(1 +", threshold, ")")
                        # A sell order is placed with a negative quantity.
                        orders.append(Order(product, best_bid_price, -trade_volume))
            
            result[product] = orders
        
        # Optionally, one might implement a conversion strategy.
        # For the manual challenge part (trading foreign currencies), one might want
        # to perform conversion requests here. In this baseline, we set conversions to 0.
        conversions = 0

        # Store our updated trader info back into traderData.
        trader_data = jsonpickle.encode(trader_info)

        return result, conversions, trader_data
