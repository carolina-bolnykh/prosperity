import itertools

def simulate_trades(start_currency, end_currency, start_amount, max_steps, rates):

    # Initialize states: List of tuples (current_path, current_amount)
    # Path starts with the initial currency
    states = [([start_currency], start_amount)]
    best_final_amount = -1.0  # Initialize with a value lower than any possible outcome
    best_path_found = None

    # Iterate for the exact number of steps (trades)
    for step in range(max_steps):
        next_states = []
        for path, amount in states:
            current_currency = path[-1]

            # Check if trades *from* the current currency are defined
            if current_currency in rates:
                # Explore possible trades to the next currency
                for next_currency, rate in rates[current_currency].items():
                    new_path = path + [next_currency]
                    new_amount = amount * rate
                    next_states.append((new_path, new_amount))

        states = next_states # Update states for the next iteration
        # Optional: Pruning could be added here if states grow too large,
        # but for 5 steps it should be manageable.

    # After completing max_steps trades, find the best result ending in the target currency
    for path, amount in states:
        if path[-1] == end_currency: # Check if the final currency is the desired one
            if amount > best_final_amount:
                best_final_amount = amount
                best_path_found = path

    if best_path_found:
        return best_path_found, best_final_amount
    else:
        return None, None

# --- Configuration ---
rates = {
    'Snowballs': {'Pizzas': 1.45, 'Silicon Nuggets': 0.52, 'Seashells': 0.72},
    'Pizzas': {'Snowballs': 0.7, 'Silicon Nuggets': 0.31, 'Seashells': 0.48},
    'Silicon Nuggets': {'Snowballs': 1.95, 'Pizzas': 3.1, 'Seashells': 1.49},
    'Seashells': {'Snowballs': 1.34, 'Pizzas': 1.98, 'Silicon Nuggets': 0.64}
}
currencies = list(rates.keys())
start_currency = 'Seashells'
end_currency = 'Seashells'
start_amount = 500000.0

num_steps = 5

# --- Simulation ---
best_path, best_amount = simulate_trades(start_currency, end_currency, start_amount, num_steps, rates)

# --- Output ---
print(f"\n--- Results for {num_steps} Steps ---")
if best_path:
    profit = best_amount - start_amount
    print(f"Starting Amount: {start_amount:,.2f} {start_currency}")
    print(f"Best Path Found:")
    print(f"  {' -> '.join(best_path)}")
    print(f"Final Amount:    {best_amount:,.2f} {end_currency}")
    print(f"Profit:          {profit:,.2f} {end_currency}")
else:
    print(f"No profitable path found ending in {end_currency} after exactly {num_steps} steps.")
