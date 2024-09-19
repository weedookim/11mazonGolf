import streamlit as st
import json
import os
from glob import glob
import requests

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
    print(latest_file)

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
        #print(content_type)
        # Check if the content type is an image
        return content_type is not None and 'image' in content_type.lower()
    except requests.RequestException:
        return False

# Load products
products = load_latest_product_data()

# Streamlit UI
st.title('🛍️ Daily Product List')

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
    # Use the image URL directly, handling the case where 'imageUrl' may be missing
    image_url = product.get('Image URL', None)  # Use .get() to avoid KeyError
    if image_url:
        # If imageUrl is present, construct the full URL
        image_url = 'https:' + image_url  # Assuming imageUrl field is a relative URL (e.g., '//cdn.example.com/image.jpg')
        
        # Check if the image URL is valid
        if is_valid_image_url(image_url):
            st.image(image_url, width=150)  # Display image from URL
        else:
            # If the image URL is not valid, display a placeholder image
            st.image("https://via.placeholder.com/150", width=150)
    else:
        # If imageUrl is missing, display a placeholder image
        st.image("https://via.placeholder.com/150", width=150)

    # Display product details in a styled container
    with st.container():
        st.markdown(f"**Name:** {product['Product Name']}")
        st.markdown(f"**Price:** {product['Discounted Price']} 원")
        st.markdown(f"**Original Price:** {product['Original Price']} 원")
        st.markdown(f"**Discount Rate:** {product['Discount Rate']}")
        st.markdown(f"**Review Score:** {product['Review Score']} (from {product['Review Count']} reviews)")
        st.markdown(f"[👉 View Product]({product['Link']})", unsafe_allow_html=True)
        st.write('---')
