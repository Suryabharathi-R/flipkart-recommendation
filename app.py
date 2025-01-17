import streamlit as st
import pandas as pd
import cohere

# Initialize Cohere (Replace with your Cohere API Key)
cohere_api_key = 'tmTAsBk7rvfgbR0Wz9HukHMlksabCZDfGRZi1XlD'  # Replace with your actual API key
co = cohere.Client(cohere_api_key)

# Function to process the data and return top recommended products
def get_top_recommended_products(file):
    df = pd.read_csv(file)

    # Check if the necessary columns exist
    if 'Sentiment' not in df.columns or 'Product_Name' not in df.columns or 'Sentiment_Score' not in df.columns or 'Reviews' not in df.columns:
        st.error("CSV file must contain 'Sentiment', 'Product_Name', 'Sentiment_Score', and 'Reviews' columns.")
        return None

    # Fill NaN values in 'Reviews' column with empty string (or another placeholder text)
    df['Reviews'] = df['Reviews'].fillna('')

    # Filter products with positive sentiment
    positive_reviews_df = df[df['Sentiment'] == 'Positive']

    # Group by Product_Name and calculate the average sentiment score
    average_sentiment_scores = positive_reviews_df.groupby('Product_Name')['Sentiment_Score'].mean().reset_index()

    # Rank the products by their average sentiment score in descending order
    top_recommended_products = average_sentiment_scores.sort_values(by='Sentiment_Score', ascending=False)

    # Select top N recommended products
    top_n = 10  # You can change this to any number of top recommendations you want
    top_n_recommended_products = top_recommended_products.head(top_n)

    return top_n_recommended_products

# Function to recommend products based on user query
def recommend_products(query, sentiment_data):
    # Analyze the user's input using Cohere
    response = co.generate(prompt=query, model='command-xlarge-nightly')

    # Process response (you can also use a custom NLP method if needed)
    search_keywords = response.generations[0].text.strip().split()

    # Filter sentiment data based on query analysis (e.g., find related product names or positive reviews)
    mask = sentiment_data['Reviews'].str.contains('|'.join(search_keywords), case=False, na=False)
    recommendations = sentiment_data[mask]

    # Sort products by sentiment score
    recommendations = recommendations.sort_values(by='Sentiment_Score', ascending=False)

    # Return top 5 products
    return recommendations[['Product_Name', 'Sentiment_Score']].head(5)

# Streamlit app layout
st.set_page_config(page_title="Product Recommendation Engine", layout="wide")
st.title("🌟 Product Recommendation Engine 🌟")
st.markdown("### Find the best products based on your preferences!")
st.markdown("Enter your product preferences or query below, then click **Search**.")

# File path for CSV (directly inserted)
csv_file_path = r"C:\Users\surya\Downloads\products_reviews_with_sentiment.csv"

# Attempt to load the CSV file
try:
    sentiment_data = pd.read_csv(csv_file_path)
    st.write(f"Data from CSV file loaded successfully. Preview of data:")
    st.write(sentiment_data.head())

    # Input for user query
    user_query = st.text_input("What are you looking for? (e.g., best camera phone, lightweight, etc.)", "")

    # Search button
    if st.button("Search"):
        if user_query:  # Check if the user has entered a query
            # Get top 5 product recommendations based on the query
            recommended_products = recommend_products(user_query, sentiment_data)

            if not recommended_products.empty:
                st.markdown("### Recommended Products:")
                # Display recommended products in a well-formatted manner
                for index, row in recommended_products.iterrows():
                    st.markdown(f"- **{row['Product_Name']}** with Sentiment Score: {row['Sentiment_Score']:.2f}")
            else:
                st.warning("No recommendations found based on your query. Please try a different query.")
        else:
            st.warning("Please enter a product preference or query before clicking the search button.")

    # Option to download the recommended products as a CSV
    top_recommended_products = get_top_recommended_products(csv_file_path)
    if top_recommended_products is not None:
        csv = top_recommended_products[['Product_Name', 'Sentiment_Score']].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Top Recommended Products",
            data=csv,
            file_name='top_recommended_products.csv',
            mime='text/csv'
        )

except Exception as e:
    st.error(f"Error reading the CSV file: {e}")

# Footer
st.markdown("---")
st.markdown("### Need Help?")
st.markdown("Feel free to reach out if you have any questions or need assistance!")
