import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# Set your OpenAI key securely
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_news(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    headlines = [a.text for a in soup.find_all("a") if a.text and len(a.text) > 40]
    return headlines[:7]

def generate_insight(ticker, articles):
    joined = "\n\n".join([f"Title: {a}" for a in articles])
    prompt = f"""
You are a financial analyst. Analyze this news about {ticker.upper()} and return ONE insight in the following structure:

1. <Most important headline title>  
Signal: <Emoji + summary (e.g. 🟡 Anticipatory Bullish - Sector-specific)>  
📊Impact on You: <What traders/investors might expect, including stats, historical analogs, ETF impact>  
🧠What to Consider: <Key strategic thoughts – e.g., whether to fade the hype, rotation signals, position sizing ideas, or peer confirmations>

Keep it tight, sharp, and market-aware. Avoid generic sentiment. Be useful.
    
{joined}
"""

    response = client.responses.create(
        model="gpt-4.1",
        input=prompt
    )

    return response.output_text.strip()

# Streamlit UI
st.title("📰 Stock Sentiment Scanner (GPT-4 Enhanced)")
ticker = st.text_input("Enter stock ticker or company name:", "Nvidia")

if st.button("Generate Market Insight"):
    with st.spinner("Fetching headlines and analyzing..."):
        try:
            articles = get_news(ticker)
            if not articles:
                st.error("Couldn't find relevant news.")
            else:
                insight = generate_insight(ticker, articles)
                st.markdown(insight)
                with st.expander("Sources"):
                    for a in articles:
                        st.markdown(f"- [{a}]")
        except Exception as e:
            st.error(f"Error: {e}")
