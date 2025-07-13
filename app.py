import streamlit as st
import requests
from bs4 import BeautifulSoup
import openai
import os

# Set your OpenAI key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]

def get_news(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    headlines = [a.text for a in soup.find_all("a") if a.text and len(a.text) > 40]
    return headlines[:7]

def generate_insight(ticker, articles):
    joined = "\n\n".join([f"Title: {a['title']}\nSnippet: {a['snippet']}" for a in articles])
    prompt = f"""
You are a financial analyst. Analyze this news about {ticker.upper()} and return ONE insight in the following structure:

1. <Most important headline title>  
Signal: <Emoji + summary (e.g. 🟡 Anticipatory Bullish - Sector-specific)>  
📊Impact on You: <What traders/investors might expect, including stats, historical analogs, ETF impact>  
🧠What to Consider: <Key strategic thoughts – e.g., whether to fade the hype, rotation signals, position sizing ideas, or peer confirmations>

Keep it tight, sharp, and market-aware. Avoid generic sentiment. Be useful.
    
{joined}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()

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
                        st.markdown(f"- [{a['title']}]({a['url']})")
        except Exception as e:
            st.error(f"Error: {e}")
