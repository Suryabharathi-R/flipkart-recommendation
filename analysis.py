import pandas as pd
import streamlit as st

# Function to process the data and return top N recommended products
def get_top_recommended_products(df, top_n):
    # Step 1: Filter products with positive sentiment
    positive_reviews_df = df[df['Sentiment'] == 'Positive']

    # Step 2: Group by the correct column (e.g., 'Product_Name') and calculate the average sentiment score
    average_sentiment_scores = positive_reviews_df.groupby('Product_Name')['Sentiment_Score'].mean().reset_index()

    # Step 3: Rank the products by their average sentiment score in descending order
    top_recommended_products = average_sentiment_scores.sort_values(by='Sentiment_Score', ascending=False)

    # Step 4: Select the top N products
    top_n_recommended_products = top_recommended_products.head(top_n)

    return top_n_recommended_products

# Streamlit UI elements
st.title("Product Sentiment Analysis - Top Recommended Products")
st.write(
    "This application helps you identify the top recommended products based on positive sentiment analysis from reviews."
)

# Path to the predefined file
file_path = r"C:\Users\Surya\Downloads\products_reviews_with_sentiment.csv"

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file containing product reviews and sentiment analysis", type=["csv"])

# Select number of top products to display
top_n = st.slider("Select number of top recommended products", min_value=1, max_value=20, value=10)

# Load dataset based on file input
if uploaded_file is not None:
    # Read the uploaded CSV file
    df = pd.read_csv(uploaded_file)
    st.write(f"Using the uploaded file: {uploaded_file.name}")
else:
    # Load the predefined file from the given path
    df = pd.read_csv(file_path)
    st.write(f"Using the predefined file from path: {file_path}")

# Check the column names to guide the user
st.write("Columns in the dataset:", df.columns)

# Process the data to get top recommended products
try:
    top_n_recommended_products = get_top_recommended_products(df, top_n)

    # Product search bar
    search_query = st.text_input("Search for a product", "")
    
    if search_query:
        # Filter products that contain the search query (case insensitive)
        search_results = top_n_recommended_products[top_n_recommended_products['Product_Name'].str.contains(search_query, case=False, na=False)]
    else:
        search_results = top_n_recommended_products

    # Display search results
    if not search_results.empty:
        st.write(f"Search Results for: '{search_query}'")
        st.dataframe(search_results[['Product_Name', 'Sentiment_Score']])
    else:
        st.write("No products found based on your search.")

    # Option to download the recommended products as CSV
    output_file = st.download_button(
        label="Download Top Recommended Products as CSV",
        data=top_n_recommended_products.to_csv(index=False),
        file_name="top_recommended_products.csv",
        mime="text/csv"
    )

except KeyError as e:
    st.error(f"Error processing the data: {e}. Please ensure the dataset contains 'Sentiment', 'Product_Name', and 'Sentiment_Score' columns.")
