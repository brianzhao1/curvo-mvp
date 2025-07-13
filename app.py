import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

def get_news(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    headlines = [a.text for a in soup.find_all("a") if a.text and len(a.text) > 40]
    return headlines[:5]

def analyze_sentiment(texts):
    polarity = sum(TextBlob(text).sentiment.polarity for text in texts) / len(texts)
    if polarity > 0.1:
        return "📈 Bullish", polarity
    elif polarity < -0.1:
        return "📉 Bearish", polarity
    else:
        return "😐 Neutral", polarity

st.title("📰 Stock Sentiment Scanner")
ticker = st.text_input("Enter stock ticker (e.g. AAPL, TSLA):", "AAPL")

if st.button("Analyze"):
    with st.spinner("Fetching news..."):
        try:
            news = get_news(ticker.upper())
            if news:
                sentiment, score = analyze_sentiment(news)
                st.subheader(f"Sentiment: {sentiment}")
                st.markdown(f"**Score:** {score:.2f}")
                st.write("**Top headlines:**")
                for headline in news:
                    st.write(f"- {headline}")
            else:
                st.warning("No headlines found.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")
