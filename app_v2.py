import streamlit as st
import json
import os
from glob import glob
import requests

# Add custom CSS for styling
def add_custom_css():
    st.markdown(
        """
        <style>
        /* Center the app title */
        .title {
            text-align: center;
        }
        /* Style for product cards */
        .card {
            background-color: #f9f9f9;
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.1);
        }
        /* Image styling */
        .product-image {
            border-radius: 8px;
            margin-right: 15px;
            width: 100%;
        }
        /* Product information container */
        .product-info {
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
        }
        /* Style for the product name */
        .product-name {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        /* Price styling */
        .price {
            color: #ff4b4b;
            font-size: 1.1rem;
        }
        /* Original price and discount styling */
        .original-price {
            text-decoration: line-through;
            color: #888;
            margin-right: 10px;
        }
        /* Add a margin below elements */
        .mb-10 {
            margin-bottom: 10px;
        }
        /* Button styling */
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            border-radius: 5px;
            border: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Load the latest product data
def load_latest_product_data():
    # Define the directory to search for JSON files
    json_directory = 'json'

    # Find the latest JSON file in the 'json' directory
    json_files = glob(os.path.join(json_directory, 'products_*.json'))
    if not json_files:
        return []
    
    # Find the latest file based on the creation time
    latest_file = max(json_files, key=os.path.getctime)
    with open(latest_file, 'r', encoding='utf-8') as file:
        products = json.load(file)
    
    return products

# Helper function to convert price strings to float
def parse_price(price_str):
    try:
        # Remove commas and convert to float
        return float(price_str.replace(',', ''))
    except (ValueError, AttributeError):
        # Return None if conversion fails
        return None

# Helper function to check if the image URL is valid
def is_valid_image_url(url):
    try:
        # Send a HEAD request to check if the URL is valid and returns an image
        response = requests.head(url)
        content_type = response.headers.get('content-type')
        # Check if the content type is an image
        return content_type is not None and 'image' in content_type.lower()
    except requests.RequestException:
        return False

# Apply custom CSS
add_custom_css()

# Load products
products = load_latest_product_data()

# Streamlit UI
st.title('🛍️ Daily Product List', anchor='title')

# Sidebar for filters
st.sidebar.header('Filter Products')

# Search bar for product name with like search
search_term = st.sidebar.text_input('🔍 Search by name (like search)').lower()

# Get the min and max prices for the slider
if products:
    min_price = min([parse_price(p['Discounted Price']) for p in products if parse_price(p['Discounted Price']) is not None])
    max_price = max([parse_price(p['Discounted Price']) for p in products if parse_price(p['Discounted Price']) is not None])
else:
    min_price = 0
    max_price = 1000

# Price range filter
price_range = st.sidebar.slider('💰 Price range', min_value=min_price, max_value=max_price, value=(min_price, max_price))

# Filter products based on search term and price range
filtered_products = []
for product in products:
    product_name = product['Product Name'].lower()
    product_price = parse_price(product['Discounted Price'])
    
    if (search_term in product_name) and (product_price is not None) and (price_range[0] <= product_price <= price_range[1]):
        filtered_products.append(product)

# Display products
st.subheader(f"Showing {len(filtered_products)} products")

for product in filtered_products:
    # Create a two-column layout
    col1, col2 = st.columns([1, 3])

    # Left column: Product image
    with col1:
        image_url = product.get('Image', None)
        if image_url:
            image_url = 'https:' + image_url  # Construct the full URL
            if is_valid_image_url(image_url):
                st.image(image_url, width=150)
            else:
                st.image("https://via.placeholder.com/150", width=150)
        else:
            st.image("https://via.placeholder.com/150", width=150)

    # Right column: Product details
    with col2:
        st.markdown(f"""
            <div class='card product-info'>
                <div class='product-name'>{product['Product Name']}</div>
                <div class='price'>💰 {product['Discounted Price']} 원</div>
                <div class='original-price'>Original: {product['Original Price']} 원</div>
                <div class='mb-10'>Discount Rate: {product['Discount Rate']}</div>
                <div class='mb-10'>Review Score: {product['Review Score']} (from {product['Review Count']} reviews)</div>
                <a href='{product['Link']}' target='_blank'>👉 View Product</a>
            </div>
        """, unsafe_allow_html=True)

    st.write('---')  # Add a horizontal line between products
