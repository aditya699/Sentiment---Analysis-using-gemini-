import streamlit as st
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os
import google.generativeai as genai
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

def classify_sentiment(comment):
    prompt = f"""Classify the sentiment of the following comment as either 'positive', 'negative', or 'neutral'. 
    Respond with ONLY ONE of these three words, nothing else.
    
    Comment: '{comment}'
    
    Classification:"""
    
    response = model.generate_content(prompt)
    sentiment = response.text.strip().lower()
    
    # Ensure only valid responses are returned
    if sentiment not in ['positive', 'negative', 'neutral']:
        sentiment = 'neutral'  # Default to neutral if response is unexpected
    
    return sentiment

def process_file(file):
    df = pd.read_csv(file)
    df['Sentiment'] = df['Comments'].apply(classify_sentiment)
    return df

def create_wordcloud(text):
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    return fig

def main():
    st.title("Sentiment Analysis with Gemini 1.5 Flash")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        df = process_file(uploaded_file)

        st.write("Processed Data:")
        st.write(df)

        # Save processed data to CSV
        output_filename = "sentiment_analysis_results.csv"
        df.to_csv(output_filename, index=False)
        st.success(f"Results saved to {output_filename}")

        # Create and display sentiment distribution chart
        sentiment_counts = df['Sentiment'].value_counts()
        fig = px.bar(x=sentiment_counts.index, y=sentiment_counts.values,
                     labels={'x': 'Sentiment', 'y': 'Count'},
                     title='Sentiment Distribution')
        st.plotly_chart(fig)

        # Create and display word cloud
        st.subheader("Word Cloud of Comments")
        all_comments = " ".join(df['Comments'])
        wordcloud_fig = create_wordcloud(all_comments)
        st.pyplot(wordcloud_fig)

if __name__ == "__main__":
    main()