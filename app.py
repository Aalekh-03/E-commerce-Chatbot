from flask import Flask, render_template, request, jsonify
import os
import logging
import re
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- API Setup (Optional - Gemini API) ----------------

# import google.generativeai as genai
# API_KEY = os.getenv("GEMINI_API_KEY")
# if not API_KEY:
#     API_KEY = "your_api_key_here"  # Replace with your actual key

# try:
#     genai.configure(api_key=API_KEY)
#     model = genai.GenerativeModel("gemini-1.5-flash")
#     chat = model.start_chat()
#     logger.info("Gemini API configured successfully")
# except Exception as e:
#     logger.error(f"Failed to configure Gemini API: {e}")
#     model = None
#     chat = None

# model = None  # Disable Gemini for this demo

# ---------------- Product Catalog ----------------
product_catalog = [
    # Shoes
    {
        "id": 1,
        "name": "Nike Air Zoom",
        "category": "shoes",
        "price": 2800,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300&h=300&fit=crop&crop=center",
        "description": "Premium Nike Air Zoom with responsive cushioning technology. Perfect for running and daily wear.",
        "brand": "Nike",
        "tags": ["running", "sports", "comfortable"]
    },
    {
        "id": 2,
        "name": "Adidas UltraBoost",
        "category": "shoes",
        "price": 3200,
        "image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=300&h=300&fit=crop&crop=center",
        "description": "Adidas UltraBoost with superior energy return and comfort for all-day wear.",
        "brand": "Adidas",
        "tags": ["running", "boost", "energy"]
    },
    {
        "id": 3,
        "name": "Puma RS-X",
        "category": "shoes",
        "price": 2900,
        "image": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=300&h=300&fit=crop&crop=center",
        "description": "Retro-inspired Puma RS-X with bold design and excellent cushioning.",
        "brand": "Puma",
        "tags": ["retro", "fashion", "casual"]
    },
    {
        "id": 4,
        "name": "Reebok Classic",
        "category": "shoes",
        "price": 2500,
        "image": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=300&h=300&fit=crop&crop=center",
        "description": "Timeless Reebok Classic leather shoes with vintage appeal and modern comfort.",
        "brand": "Reebok",
        "tags": ["classic", "leather", "vintage"]
    },

    # Clothing
    {
        "id": 5,
        "name": "Premium Cotton T-Shirt",
        "category": "clothing",
        "price": 899,
        "image": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=300&fit=crop&crop=center",
        "description": "100% premium cotton t-shirt available in multiple colors. Soft, breathable, and durable.",
        "brand": "Generic",
        "tags": ["cotton", "casual", "comfort"]
    },
    {
        "id": 6,
        "name": "Slim Fit Denim Jeans",
        "category": "clothing",
        "price": 1999,
        "image": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=300&h=300&fit=crop&crop=center",
        "description": "Classic blue denim jeans with slim fit design. Made from high-quality denim fabric.",
        "brand": "Generic",
        "tags": ["denim", "jeans", "slim-fit"]
    },
    {
        "id": 7,
        "name": "Genuine Leather Jacket",
        "category": "clothing",
        "price": 4999,
        "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=300&fit=crop&crop=center",
        "description": "Premium genuine leather jacket with modern cut. Perfect for style and warmth.",
        "brand": "Generic",
        "tags": ["leather", "jacket", "premium"]
    },
    {
        "id": 8,
        "name": "Sports Hoodie",
        "category": "clothing",
        "price": 1599,
        "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=300&h=300&fit=crop&crop=center",
        "description": "Comfortable fleece hoodie perfect for workouts or casual wear. Features kangaroo pocket.",
        "brand": "Generic",
        "tags": ["hoodie", "sports", "fleece"]
    },

    # Electronics
    {
        "id": 9,
        "name": "Wireless Earbuds Pro",
        "category": "electronics",
        "price": 2499,
        "image": "https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?w=300&h=300&fit=crop&crop=center",
        "description": "Premium wireless earbuds with active noise cancellation and 24-hour battery life.",
        "brand": "TechBrand",
        "tags": ["wireless", "earbuds", "noise-cancelling"]
    },
    {
        "id": 10,
        "name": "Smartwatch Pro Max",
        "category": "electronics",
        "price": 7999,
        "image": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop&crop=center",
        "description": "Advanced smartwatch with fitness tracking, heart rate monitor, GPS, and cellular connectivity.",
        "brand": "TechBrand",
        "tags": ["smartwatch", "fitness", "gps"]
    },
    {
        "id": 11,
        "name": "Portable Bluetooth Speaker",
        "category": "electronics",
        "price": 3999,
        "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=300&h=300&fit=crop&crop=center",
        "description": "High-quality Bluetooth speaker with 360-degree sound and waterproof design.",
        "brand": "AudioTech",
        "tags": ["speaker", "bluetooth", "waterproof"]
    },
    {
        "id": 12,
        "name": "4K HD Webcam",
        "category": "electronics",
        "price": 1899,
        "image": "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=300&h=300&fit=crop&crop=center",
        "description": "Professional 4K HD webcam with auto-focus and built-in microphone for video calls.",
        "brand": "TechVision",
        "tags": ["webcam", "4k", "video-calls"]
    },

    # Accessories
    {
        "id": 13,
        "name": "RFID Leather Wallet",
        "category": "accessories",
        "price": 999,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300&h=300&fit=crop&crop=center",
        "description": "Premium leather wallet with RFID blocking technology and multiple card slots.",
        "brand": "LeatherCraft",
        "tags": ["wallet", "leather", "rfid"]
    },
    {
        "id": 14,
        "name": "Aviator Sunglasses",
        "category": "accessories",
        "price": 1499,
        "image": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=300&h=300&fit=crop&crop=center",
        "description": "Classic aviator sunglasses with UV400 protection and polarized lenses.",
        "brand": "SunStyle",
        "tags": ["sunglasses", "aviator", "uv-protection"]
    },
    {
        "id": 15,
        "name": "Performance Sports Cap",
        "category": "accessories",
        "price": 599,
        "image": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=300&h=300&fit=crop&crop=center",
        "description": "Adjustable sports cap with moisture-wicking fabric perfect for outdoor activities.",
        "brand": "SportGear",
        "tags": ["cap", "sports", "moisture-wicking"]
    },
    {
        "id": 16,
        "name": "Travel Backpack 40L",
        "category": "accessories",
        "price": 2599,
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300&h=300&fit=crop&crop=center",
        "description": "Spacious 40L travel backpack with multiple compartments, laptop sleeve, and USB charging port.",
        "brand": "TravelPro",
        "tags": ["backpack", "travel", "laptop"]
    }
]

user_sessions = {}

# ---------------- Helper Functions ----------------

def get_user_cart(session_id="default"):
    """Get user's cart, create if doesn't exist"""
    if session_id not in user_sessions:
        user_sessions[session_id] = {"cart": [], "order_history": []}
    return user_sessions[session_id]["cart"]

def add_to_cart(product_id, session_id="default", quantity=1):
    """Add product to cart"""
    cart = get_user_cart(session_id)
    product = next((p for p in product_catalog if p["id"] == product_id), None)
    
    if not product:
        return False, "Product not found"
    
    # Check if product already in cart
    existing_item = next((item for item in cart if item["id"] == product_id), None)
    if existing_item:
        existing_item["quantity"] += quantity
    else:
        cart_item = product.copy()
        cart_item["quantity"] = quantity
        cart.append(cart_item)
    
    return True, f"Added {product['name']} to cart"

def search_products(query):
    """Enhanced product search with multiple criteria"""
    query = query.lower().strip()
    results = []
    
    # Remove common stop words for better matching
    stop_words = {"show", "me", "find", "search", "for", "get", "buy", "purchase", "looking", "want"}
    query_words = [word for word in query.split() if word not in stop_words and len(word) > 2]
    
    for product in product_catalog:
        score = 0
        
        # Exact category match (highest priority)
        if query in product["category"].lower() or product["category"].lower() in query:
            score += 10
        
        # Brand match
        if product.get("brand", "").lower() in query:
            score += 8
        
        # Name word match
        name_words = product["name"].lower().split()
        for query_word in query_words:
            for name_word in name_words:
                if query_word in name_word or name_word in query_word:
                    score += 5
        
        # Description match
        if any(word in product["description"].lower() for word in query_words):
            score += 3
        
        # Tags match
        if "tags" in product:
            for tag in product["tags"]:
                if any(word in tag.lower() for word in query_words):
                    score += 4
        
        # Price range queries
        if "cheap" in query or "budget" in query or "affordable" in query:
            if product["price"] < 1500:
                score += 3
        elif "expensive" in query or "premium" in query or "luxury" in query:
            if product["price"] > 3000:
                score += 3
        
        if score > 0:
            results.append((product, score))
    
    # Sort by relevance score
    results.sort(key=lambda x: x[1], reverse=True)
    return [product for product, score in results]

def format_price(price):
    """Format price in Indian Rupees"""
    return f"₹{price:,}"

def handle_user_input(user_input, session_id="default"):
    """Enhanced user input handler with better responses"""
    query = user_input.lower().strip()
    cart = get_user_cart(session_id)
    
    logger.info(f"Processing query: '{query}' for session: {session_id}")
    
    # Greeting responses
    query_word=query.split()
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    if any(greeting in query_word for greeting in greetings):
        return """
        <div style='text-align: center; padding: 20px;'>
            <h3>👋 Hello! Welcome to our store!</h3>
            <p>I'm your personal shopping assistant. Here's what I can help you with:</p>
            <div style='margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 10px;'>
                🔍 <strong>Search Products:</strong> "show me shoes", "find electronics"<br>
                🛒 <strong>Manage Cart:</strong> "show my cart", "checkout"<br>
                📋 <strong>Get Info:</strong> "return policy", "shipping info"
            </div>
            <p>What would you like to explore today?</p>
        </div>
        """
    
    # Cart management
    if "cart" in query:
        if any(word in query for word in ["show", "view", "check", "see", "display"]):
            if not cart:
                return """
                <div style='text-align: center; padding: 20px;'>
                    <h3>🛒 Your Cart is Empty</h3>
                    <p>Start shopping by searching for products!</p>
                    <div style='margin-top: 15px;'>
                        <button class='quick-btn' onclick='sendQuickMessage("show me shoes")'>👟 Browse Shoes</button>
                        <button class='quick-btn' onclick='sendQuickMessage("electronics")'>📱 Electronics</button>
                    </div>
                </div>
                """
            
            total = sum(item['price'] * item['quantity'] for item in cart)
            response = f"""
            <div style='padding: 20px; background: #f8f9fa; border-radius: 10px;'>
                <h3>🛒 Your Shopping Cart ({len(cart)} items)</h3>
            """
            
            for item in cart:
                subtotal = item['price'] * item['quantity']
                response += f"""
                <div style='display: flex; align-items: center; margin: 10px 0; padding: 10px; background: white; border-radius: 8px;'>
                    <img src='{item['image']}' width='60' height='60' style='border-radius: 5px; margin-right: 10px;' />
                    <div style='flex: 1;'>
                        <strong>{item['name']}</strong><br>
                        <small>Quantity: {item['quantity']} × {format_price(item['price'])} = {format_price(subtotal)}</small>
                    </div>
                </div>
                """
            
            response += f"""
                <hr style='margin: 15px 0;'>
                <div style='text-align: right;'>
                    <h3>Total: {format_price(total)}</h3>
                    <button onclick='sendQuickMessage("checkout")' style='background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;'>
                        💳 Proceed to Checkout
                    </button>
                    <button onclick='sendQuickMessage("clear cart")' style='background: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px;'>
                        🗑️ Clear Cart
                    </button>
                </div>
            </div>
            """
            return response
        
        elif "clear" in query or "empty" in query:
            cart.clear()
            return "✅ Your cart has been cleared!"
    
    # Checkout process
    if "checkout" in query or "buy" in query:
        if not cart:
            return "❌ Your cart is empty! Add some items before checkout."
        
        total = sum(item['price'] * item['quantity'] for item in cart)
        order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Move to order history
        if session_id not in user_sessions:
            user_sessions[session_id] = {"cart": [], "order_history": []}
        
        user_sessions[session_id]["order_history"].append({
            "order_id": order_id,
            "items": cart.copy(),
            "total": total,
            "date": datetime.now().isoformat()
        })
        
        cart.clear()
        
        return f"""
        <div style='text-align: center; padding: 20px; background: #e8f5e8; border-radius: 10px;'>
            <h2>✅ Order Confirmed!</h2>
            <p><strong>Order ID:</strong> {order_id}</p>
            <p><strong>Total Amount:</strong> {format_price(total)}</p>
            <hr style='margin: 15px 0;'>
            <p>🚚 Your order will be delivered within 3-5 business days</p>
            <p>📧 Confirmation email sent to your registered address</p>
            <div style='margin-top: 15px;'>
                <button onclick='sendQuickMessage("track order")' class='quick-btn'>📦 Track Order</button>
                <button onclick='sendQuickMessage("continue shopping")' class='quick-btn'>🛍️ Continue Shopping</button>
            </div>
        </div>
        """
    
    # Return policy
    if "return" in query and "policy" in query:
        return """
        <div style='padding: 20px; background: #fff3cd; border-radius: 10px;'>
            <h3>📋 Return Policy</h3>
            <ul style='margin: 10px 0; padding-left: 20px;'>
                <li>✅ <strong>30-day return window</strong> from delivery date</li>
                <li>✅ Items must be in original condition with tags</li>
                <li>✅ Free return pickup for orders above ₹1000</li>
                <li>✅ Full refund processed within 5-7 business days</li>
                <li>❌ Personal care items and electronics opened packages may have restrictions</li>
            </ul>
            <p><strong>To initiate a return:</strong> Contact our support team or use the 'Return Item' option in your order history.</p>
        </div>
        """
    
    # Product search
    search_results = search_products(query)
    
    if search_results:
        response = f"""
        <div style='margin-bottom: 15px;'>
            <h3>🔍 Found {len(search_results)} product(s) for "{user_input}"</h3>
        </div>
        """
        
        for product in search_results:  # No limit to search
            response += f"""
            <div style='display: flex; margin: 15px 0; padding: 15px; background: white; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);'>
                <img src='{product['image']}' width='100' height='100' style='border-radius: 8px; margin-right: 15px; object-fit: cover;' 
                     onerror="this.src='https://via.placeholder.com/100x100?text=No+Image'" />
                <div style='flex: 1;'>
                    <h4 style='margin: 0 0 5px 0; color: #333;'>{product['name']}</h4>
                    <p style='margin: 5px 0; color: #666; font-size: 0.9em;'><strong>Brand:</strong> {product.get('brand', 'Generic')}</p>
                    <p style='margin: 5px 0; color: #666; font-size: 0.9em;'>{product['description'][:100]}...</p>
                    <p style='margin: 8px 0; font-size: 1.2em;'><strong style='color: #4CAF50;'>{format_price(product['price'])}</strong></p>
                    <button onclick="addToCart({product['id']})" 
                            style="background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 8px 16px; border: none; border-radius: 20px; cursor: pointer; font-weight: 600;">
                        🛒 Add to Cart
                    </button>
                </div>
            </div>
            """
        
        if len(search_results) > 6:
            response += f"<p style='text-align: center; margin: 15px 0;'><em>And {len(search_results) - 6} more products... Try a more specific search!</em></p>"
        
        return response
    
    # No products found
    return f"""
    <div style='text-align: center; padding: 20px;'>
        <h3>😔 No products found for "{user_input}"</h3>
        <p>Try searching for:</p>
        <div style='margin: 15px 0;'>
            <button class='quick-btn' onclick='sendQuickMessage("shoes")'>👟 Shoes</button>
            <button class='quick-btn' onclick='sendQuickMessage("clothing")'>👕 Clothing</button>
            <button class='quick-btn' onclick='sendQuickMessage("electronics")'>📱 Electronics</button>
            <button class='quick-btn' onclick='sendQuickMessage("accessories")'>👜 Accessories</button>
        </div>
        <p>Or try specific brands like Nike, Adidas, or price ranges like "budget shoes"</p>
    </div>
    """

# ---------------- Flask App ----------------
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("./index.html")

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    try:
        data = request.get_json()
        user_input = data.get("message", "").strip()
        session_id = data.get("session_id", "default")
        
        if not user_input:
            return jsonify({"error": "Empty message"}), 400
        
        response = handle_user_input(user_input, session_id)
        
        return jsonify({
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "error": "Something went wrong. Please try again.",
            "response": "😔 I'm having trouble processing your request. Please try again or contact support."
        }), 500

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart_endpoint():
    try:
        data = request.get_json()
        product_id = data.get("product_id")
        session_id = data.get("session_id", "default")
        quantity = data.get("quantity", 1)
        
        if not product_id:
            return jsonify({"success": False, "message": "Product ID is required"}), 400
        
        success, message = add_to_cart(product_id, session_id, quantity)
        
        return jsonify({
            "success": success,
            "message": message,
            "cart_count": len(get_user_cart(session_id))
        })
        
    except Exception as e:
        logger.error(f"Error in add_to_cart endpoint: {e}")
        return jsonify({"success": False, "message": "Failed to add item to cart"}), 500

@app.route("/get_cart", methods=["GET"])
def get_cart():
    try:
        session_id = request.args.get("session_id", "default")
        cart = get_user_cart(session_id)
        total = sum(item['price'] * item['quantity'] for item in cart)
        
        return jsonify({
            "cart": cart,
            "total": total,
            "count": len(cart)
        })
        
    except Exception as e:
        logger.error(f"Error in get_cart endpoint: {e}")
        return jsonify({"error": "Failed to retrieve cart"}), 500

@app.route("/products", methods=["GET"])
def get_products():
    try:
        category = request.args.get("category")
        if category:
            filtered_products = [p for p in product_catalog if p["category"].lower() == category.lower()]
            return jsonify({"products": filtered_products})
        
        return jsonify({"products": product_catalog})
        
    except Exception as e:
        logger.error(f"Error in products endpoint: {e}")
        return jsonify({"error": "Failed to retrieve products"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    print(" Starting Flask E-commerce Chatbot...")
    print(" Server will be available at: http://127.0.0.1:5500")
    print(" Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='127.0.0.1', port=5500)