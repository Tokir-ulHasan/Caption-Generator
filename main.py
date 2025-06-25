import streamlit as st
import cohere
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION ---
COHERE_API_KEY = "5iGDe8RaqvvXZiRY7c9Eo6pCp705LAUGC6L4xLtZ"  # ← Replace this with your actual key
GOOGLE_SHEET_NAME = "Instagram Caption Generator"

# --- SETUP COHERE ---
co = cohere.Client(COHERE_API_KEY)


# --- GOOGLE SHEET SETUP ---
def connect_to_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    return sheet


# --- CAPTION GENERATION ---
def generate_caption(topic):
    response = co.generate(
        model='command',
        prompt=f"Write a short, fun Instagram caption about: {topic}",
        max_tokens=50,
        temperature=0.7,
    )
    return response.generations[0].text.strip()


# --- SAVE TO SHEET ---
def save_to_sheet(topic, caption):
    sheet = connect_to_sheet()
    sheet.append_row([topic, caption])


# --- STREAMLIT UI ---
def main():
    st.title("📸 AI Instagram Caption Generator")
    topic = st.text_input("Enter a topic or keyword:")

    if st.button("✨ Generate Caption"):
        if topic:
            caption = generate_caption(topic)
            st.success("✅ Caption Generated!")
            st.write(f"**📝 Caption:** {caption}")
            save_to_sheet(topic, caption)
        else:
            st.warning("⚠️ Please enter a topic!")

    # Show previous captions
    st.subheader("📜 Caption History")
    try:
        sheet = connect_to_sheet()
        records = sheet.get_all_records()
        for row in reversed(records[-5:]):  # Show last 5 captions
            st.write(f"- **{row['topic']}** → {row['caption']}")
    except Exception as e:
        st.error(f"Couldn't load sheet: {e}")


if __name__ == "__main__":
    main()
