import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# If TOGETHER_API_KEY is missing or not set, raise an error
if not TOGETHER_API_KEY:
    st.error("API Key is missing. Please set the TOGETHER_API_KEY in the .env file.")

# API URL for Together API
API_URL = "https://api.together.xyz/v1/completions"  # Replace with the actual URL of the Together API

# Function to fetch response from Together API
def fetch_together_response(prompt, max_tokens=100, temperature=0.7):
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1.0,
        "stop": ["<|eot_id|>", "<|eom_id|>"]
    }
    
    try:
        response = requests.post(API_URL, json=data, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            raise Exception(f"API call failed with status code {response.status_code}")
    except Exception as e:
        st.error(f"Error fetching data from Together API: {e}")
        return "Error"

# Fetch daily word
def fetch_daily_word():
    prompt = "Suggest a word related to learning and provide an example sentence."
    response = fetch_together_response(prompt, max_tokens=50)
    if response != "Error":
        try:
            word, sentence = response.split("\n", 1)
            return word.strip(), sentence.strip()
        except ValueError:
            return "Unknown Word", "No sentence available."
    return "Error", "Error"

# Fetch word details
def fetch_word_details(word):
    prompt = f"Provide details about the word '{word}' and an example sentence using it."
    response = fetch_together_response(prompt, max_tokens=100)
    if response != "Error":
        return {'word': word, 'sentence': response.strip()}
    return {'word': 'Error', 'sentence': 'Error'}

# Generate quiz options
def generate_quiz(word):
    prompt = f"Create a multiple-choice quiz with 4 options for the word '{word}'. Provide options in a list format."
    response = fetch_together_response(prompt, max_tokens=150)
    if response != "Error":
        return [option.strip() for option in response.split('\n') if option.strip()]
    return []

# Show progress tracker
def show_progress(words_learned, total_words):
    progress = words_learned / total_words if total_words > 0 else 0
    st.metric("Words Learned", f"{words_learned} / {total_words}")
    st.progress(progress)

# Main UI
with st.sidebar:
    st.header("Menu")
    menu_option = st.radio("Navigate", ["Word of the Day", "Word Details", "Quiz", "Progress Tracker"])

if menu_option == "Word of the Day":
    st.subheader("🌟 Word of the Day")
    daily_word, example_sentence = fetch_daily_word()
    st.write(f"### **{daily_word}**")
    st.write(f"**Example Sentence:** {example_sentence}")

elif menu_option == "Word Details":
    st.subheader("🔍 Word Details")
    word_input = st.text_input("Enter a word", placeholder="Type a word to fetch details...")
    if st.button("Fetch Details"):
        if word_input:
            details = fetch_word_details(word_input)
            st.write(f"### Word: **{details['word']}**")
            st.write(f"**Example Sentence:** {details['sentence']}")
        else:
            st.warning("Please enter a word.")

elif menu_option == "Quiz":
    st.subheader("📝 Take a Quiz")
    quiz_word = st.text_input("Enter a word for the quiz", placeholder="Type a word...")
    if st.button("Generate Quiz"):
        if quiz_word:
            quiz = generate_quiz(quiz_word)
            if quiz:
                st.write("### Quiz Options:")
                for i, option in enumerate(quiz, start=1):
                    st.write(f"{i}. {option}")
        else:
            st.warning("Please enter a word.")

elif menu_option == "Progress Tracker":
    st.subheader("📈 Your Progress")
    st.write("Track your learning progress below.")
    words_learned = st.number_input("Words Learned", min_value=0, step=1, key="learned")
    total_words = st.number_input("Total Words", min_value=1, step=1, value=10, key="total")
    show_progress(words_learned, total_words)
    if st.button("Save Progress"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"Progress saved at {timestamp}.")
