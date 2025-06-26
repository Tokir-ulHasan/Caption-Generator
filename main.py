import streamlit as st
import cohere
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components  # for embedding html/js

# --- CONFIGURATION FROM SECRETS ---
COHERE_API_KEY = st.secrets["COHERE_API_KEY"]
GOOGLE_SHEET_CREDS = json.loads(st.secrets["GOOGLE_SHEET_CREDS"])
GOOGLE_SHEET_NAME = "Instagram Caption Generator"  # Make sure this matches your sheet name

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

    # Input for the topic
    topic = st.text_input("Enter a topic or keyword:")

    # Generate Caption Button
    if st.button("✨ Generate Caption"):
        if topic.strip():  # Ensure topic is not empty or just spaces
            with st.spinner("Generating..."):
                try:
                    caption = generate_caption(topic)
                    save_to_sheet(topic, caption)
                    st.success("✅ Caption Generated and Saved!")

                    # Display the caption in a text area for easy manual selection
                    st.markdown("**📝 Caption:**")
                    st.text_area("Generated Caption", value=caption, height=100, key="generated_caption")

                    # Copy to clipboard button using JavaScript
                    copy_button_code = f"""
                    <script>
                    function copyToClipboard() {{
                        const text = `{caption.replace('`', '\\`')}`;
                        navigator.clipboard.writeText(text).then(() => {{
                            alert('Caption copied to clipboard!');
                        }});
                    }}
                    </script>

                    <button onclick="copyToClipboard()">📋 Copy Caption</button>
                    """
                    components.html(copy_button_code, height=50)

                except Exception as e:
                    st.error(f"❌ Something went wrong: {e}")
        else:
            st.warning("⚠️ Please enter a valid topic!")

    # Display recent caption history
    st.subheader("📜 Caption History (Last 5)")
    try:
        sheet = connect_to_sheet()
        records = sheet.get_all_records()
        if records:
            for row in reversed(records[-5:]):
                st.markdown(f"- **{row.get('topic', 'N/A')}** → {row.get('caption', 'N/A')}")
        else:
            st.info("No captions saved yet.")
    except Exception as e:
        st.error(f"❌ Couldn't load sheet: {e}")

# Run the app
if __name__ == "__main__":
    main()
