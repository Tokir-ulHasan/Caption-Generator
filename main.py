import streamlit as st
import cohere
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# --- CONFIGURATION FROM SECRETS ---
COHERE_API_KEY = st.secrets["COHERE_API_KEY"]
GOOGLE_SHEET_CREDS = json.loads(st.secrets["GOOGLE_SHEET_CREDS"])
GOOGLE_SHEET_NAME = "AI Captions"  # Make sure this matches your sheet name

# --- SETUP COHERE ---
co = cohere.Client(COHERE_API_KEY)

# --- GOOGLE SHEET SETUP ---
def connect_to_sheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEET_CREDS, scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    return sheet

# --- CAPTION GENERATION ---
def generate_caption(topic):
    response = co.generate(
        model='command',  # If you're using Cohere's older "generate" endpoint
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
    st.set_page_config(page_title="Instagram Caption Generator", page_icon="📸")
    st.title("📸 AI Instagram Caption Generator")

    topic = st.text_input("Enter a topic or keyword:")

    if st.button("✨ Generate Caption"):
        if topic:
            with st.spinner("Generating..."):
                try:
                    caption = generate_caption(topic)
                    save_to_sheet(topic, caption)
                    st.success("✅ Caption Generated and Saved!")
                    st.write(f"**📝 Caption:** {caption}")
                except Exception as e:
                    st.error(f"Something went wrong: {e}")
        else:
            st.warning("⚠️ Please enter a topic!")

    # Show caption history
    st.subheader("📜 Caption History (Last 5)")
    try:
        sheet = connect_to_sheet()
        records = sheet.get_all_records()
        if records:
            for row in reversed(records[-5:]):
                st.markdown(f"- **{row['topic']}** → {row['caption']}")
        else:
            st.info("No captions saved yet.")
    except Exception as e:
        st.error(f"Couldn't load sheet: {e}")

if __name__ == "__main__":
    main()
