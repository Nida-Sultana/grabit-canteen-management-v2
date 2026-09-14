import streamlit as st
import json
import os

ORDERS_FILE = "orders.json"
REQUESTS_FILE = "requests.json"
INVENTORY_FILE = "inventory.json"

# --- Helper Functions ---
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

# --- Initialize Inventory if not exists ---
if not os.path.exists(INVENTORY_FILE):
    default_inventory = [
        {"name": "Samosa 🥟", "price": 15, "available": True, "category": "Food"},
        {"name": "Cold Coffee 🧋", "price": 30, "available": True, "category": "Food"},
        {"name": "Blue Ball Pen 🖋️", "price": 10, "available": True, "category": "Stationary"},
        {"name": "Lab Record Notebook 📖", "price": 40, "available": True, "category": "Stationary"}
    ]
    save_json(INVENTORY_FILE, default_inventory)

# --- Streamlit Config ---
st.set_page_config(page_title="GRABIT", layout="wide", initial_sidebar_state="collapsed")
st.title("🏪 GRABIT: File-Based Sync Prototype")
st.caption("Expo Demo: Student side local, Canteen side shared JSON sync")
st.markdown("---")

role = st.radio("Login as:", ["Student/College User", "Canteen Manager"])

# ==========================================
# STUDENT SIDE (Local Orders + Shared Write)
# ==========================================
if role == "Student/College User":
    st.success("✅ Logged in as Student/College User")
    inventory = load_json(INVENTORY_FILE)
    cart = {}

    st.write("### Store Catalog")
    for item in inventory:
        if item["available"]:
            qty = st.number_input(f"{item['name']} (₹{item['price']})", min_value=0, max_value=5, value=0, key=f"st_{item['name']}")
            if qty > 0:
                cart[item["name"]] = {"qty": qty, "price": item["price"]}
        else:
            st.text(f"❌ {item['name']} (Out of Stock)")

    total_bill = sum(details["qty"] * details["price"] for details in cart.values())
    if total_bill > 0:
        st.write(f"### Total Bill: **₹{total_bill}**")
        if st.button("🛒 Place Order"):
            orders = load_json(ORDERS_FILE)
            new_order = {
                "id": len(orders) + 1,
                "items": {item: {"qty": details["qty"], "status": "Pending"} for item, details in cart.items()},
                "status": "⌛ Processing"
            }
            orders.append(new_order)
            save_json(ORDERS_FILE, orders)
            st.success(f"🎉 Order placed! Token #{new_order['id']}")
            st.balloons()

    st.write("### 📦 My Orders (Local View)")
    orders = load_json(ORDERS_FILE)
    for order in orders:
        st.write(f"Token #{order['id']} → {order['status']}")
        for item, details in order["items"].items():
            st.write(f"{details['qty']}x {item} ({details['status']})")

    st.write("### 💡 Request Custom Item")
    req_name = st.text_input("Suggest an item:")
    if st.button("🚀 Send Request"):
        requests = load_json(REQUESTS_FILE)
        requests.append(req_name)
        save_json(REQUESTS_FILE, requests)
        st.success(f"Request '{req_name}' sent to manager!")

# ==========================================
# CANTEEN SIDE (Shared JSON Sync)
# ==========================================
else:
    st.success("✅ Logged in as Canteen Manager")
    tab_orders, tab_inventory, tab_requests = st.tabs(["📥 Orders", "⚙️ Inventory", "📥 Requests"])

    # --- Orders ---
    with tab_orders:
        st.write("### Active Orders")
        orders = load_json(ORDERS_FILE)
        if not orders:
            st.info("No active orders.")
        else:
            for order in orders:
                st.markdown(f"#### Token #{order['id']} - {order['status']}")
                for item, details in order["items"].items():
                    st.write(f"{details['qty']}x {item} → {details['status']}")
                if st.button(f"Mark Ready #{order['id']}"):
                    order["status"] = "📦 Ready"
                    save_json(ORDERS_FILE, orders)
                    st.experimental_rerun()
                if st.button(f"Mark Collected #{order['id']}"):
                    order["status"] = "✅ Collected"
                    save_json(ORDERS_FILE, orders)
                    st.experimental_rerun()
                st.markdown("---")

    # --- Inventory ---
    with tab_inventory:
        st.write("### Manage Inventory")
        inventory = load_json(INVENTORY_FILE)
        new_name = st.text_input("Item Name")
        new_price = st.number_input("Price (₹)", min_value=1, value=10)
        new_cat = st.selectbox("Category", ["Stationary", "Food"])
        if st.button("➕ Add Item"):
            inventory.append({"name": new_name, "price": new_price, "available": True, "category": new_cat})
            save_json(INVENTORY_FILE, inventory)
            st.success(f"Added {new_name} to catalog.")

        for item in inventory:
            st.write(f"{item['name']} - ₹{item['price']} - {item['category']} - {'In Stock' if item['available'] else 'Out'}")

    # --- Requests ---
    with tab_requests:
        st.write("### Student Requests")
        requests = load_json(REQUESTS_FILE)
        if not requests:
            st.info("No requests yet.")
        else:
            for idx, req in enumerate(requests):
                st.warning(f"🚨 Student requested: {req}")
                if st.button(f"Add {req} to Inventory", key=f"req_{idx}"):
                    inventory = load_json(INVENTORY_FILE)
                    inventory.append({"name": req, "price": 20, "available": True, "category": "Stationary"})
                    save_json(INVENTORY_FILE, inventory)
                    requests.pop(idx)
                    save_json(REQUESTS_FILE, requests)
                    st.success(f"Added {req} to catalog.")
                    st.experimental_rerun()
