import json
import os

STATE_FILE = "state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"highest_price": None}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def get_highest_price():
    return load_state().get("highest_price")

def update_highest_price(price):
    state = load_state()
    current = state.get("highest_price")
    if current is None or price > current:
        state["highest_price"] = price
        save_state(state)
        return price
    return current

def reset_highest_price():
    state = load_state()
    state["highest_price"] = None
    save_state(state)
