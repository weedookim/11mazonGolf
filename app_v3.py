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
        /* Align columns at the top */
        .stColumn > div {
            display: flex;
            align-items: flex-start;
        }
        /* Image styling */
        .product-image {
            border-radius: 8px;
            margin-right: 15px;
            display: block;
            max-width: 100%; /* Ensure image fits within the column */
            height: auto; /* Maintain aspect ratio */
        }
        /* Set a fixed height for images if needed to maintain consistent layout */
        .fixed-height-image {
            height: 150px; /* Set a fixed height for all images */
            object-fit: cover; /* Ensure the image covers the space */
        }
        /* Product information container */
        .product-info {
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
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
        /* Button styling for sorting buttons */
        .sort-button {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 5px;
            border: 2px solid #ddd;
            margin: 5px 0;
            cursor: pointer;
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            width: 100%; /* Full width inside the sidebar */
            text-decoration: none;
        }
        .sort-button.red {
            border-color: #e74c3c;
            color: #e74c3c;
        }
        .sort-button.green {
            border-color: #27ae60;
            color: #27ae60;
        }
        /* Hover effect */
        .sort-button:hover {
            background-color: #f4f4f4;
        }
        /* Custom font size for price range */
        .price-range-label,
        .search-label,
        .selected-range-label {
            font-size: 1.2rem; /* Adjust font size here */
            font-weight: bold;
            margin-bottom: 10px;
        }
        /* Attempt to change slider font size (this might not work across all browsers) */
        input[type="range"] {
            font-size: 1.1rem !important;
        }
        .promotion-button {
            display: inline-block;
            padding: 5px 10px;
            margin: 5px 5px 0 0;
            border-radius: 20px;
            background-color: #f0f0f0;
            color: #333;
            font-size: 0.9rem;
            text-align: center;
            border: 1px solid #ddd;
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

# Helper function to format numbers with commas
def format_price(value):
    return f"{value:,.0f}"

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

# Add spacing between filter sections
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Search bar for product name with like search
st.sidebar.markdown("<div class='search-label'>🔍 Search by name (like search)</div>", unsafe_allow_html=True)
search_term = st.sidebar.text_input('Search', '', label_visibility="collapsed").lower()

# Add spacing between filter sections
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Get the min and max prices for the slider
if products:
    min_price = min([parse_price(p['Discounted Price']) for p in products if parse_price(p['Discounted Price']) is not None])
    max_price = max([parse_price(p['Discounted Price']) for p in products if parse_price(p['Discounted Price']) is not None])
else:
    min_price = 0
    max_price = 1000

# Price range filter
# Custom label for the slider with formatted values
st.sidebar.markdown("<div class='price-range-label'>💰 Price Range</div>", unsafe_allow_html=True)
price_range = st.sidebar.slider(
    'Price Range',
    min_value=int(min_price), 
    max_value=int(max_price), 
    value=(int(min_price), int(max_price))
)

# Display the selected range with commas
st.sidebar.markdown(f"<div class='selected-range-label'>Selected range: {format_price(price_range[0])} - {format_price(price_range[1])}</div>", unsafe_allow_html=True)

# Add spacing between filter sections
st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Filter products based on search term and price range
filtered_products = [
    product for product in products
    if (search_term in product['Product Name'].lower() and
        price_range[0] <= parse_price(product['Discounted Price']) <= price_range[1])
]

# Sorting buttons in the sidebar
st.sidebar.markdown("### Sort by Price")
sort_order = st.sidebar.radio(
    "Sort Order", 
    ('가격 높은순', '가격 낮은순'), 
    index=0,
    key="sort_order",
    horizontal=False
)

# Determine the sort order based on the sidebar selection
if sort_order == '가격 낮은순':
    filtered_products.sort(key=lambda x: parse_price(x['Discounted Price']) if parse_price(x['Discounted Price']) is not None else 0)
elif sort_order == '가격 높은순':
    filtered_products.sort(key=lambda x: parse_price(x['Discounted Price']) if parse_price(x['Discounted Price']) is not None else 0, reverse=True)

# Display products
st.subheader(f"Showing {len(filtered_products)} products")

for product in filtered_products:
    # Create a two-column layout
    col1, col2 = st.columns([1, 3])

    # Left column: Product image
    with col1:
        image_url = product.get('Image URL', None)
        if image_url:
            image_url = 'https:' + image_url  # Construct the full URL
            if is_valid_image_url(image_url):
                st.markdown(f"<div><img src='{image_url}' class='product-image fixed-height-image'/></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div><img src='https://via.placeholder.com/150' class='product-image fixed-height-image'/></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div><img src='https://via.placeholder.com/150' class='product-image fixed-height-image'/></div>", unsafe_allow_html=True)

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

        # Display promotion texts as rounded buttons
        promotion_texts = product.get('Promotion Texts', '')
        if promotion_texts:
            st.markdown('<div>', unsafe_allow_html=True)  # Open a div to contain promotion buttons
            for text in promotion_texts.split(', '):
                st.markdown(f"<span class='promotion-button'>{text}</span>", unsafe_allow_html=True)
                
    st.write('---')  # Add a horizontal line between products
