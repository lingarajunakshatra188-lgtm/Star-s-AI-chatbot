import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
import io
import zipfile
from PIL import Image
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

from database import (
    create_chat,
    get_chats,
    save_message,
    load_messages,
    delete_chat,
    update_chat_title
)

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Star's AI Chatbot",
    page_icon="💫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# LOAD CSS
# ==========================================

def load_css():

    if os.path.exists("style.css"):

        with open("style.css", "r", encoding="utf-8") as f:

            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )

load_css()
# ==========================================
# EXPORT FUNCTIONS
# ==========================================


def create_txt_export(messages):

    text = "Star's AI Chatbot\n"
    text += "=" * 30 + "\n\n"

    text += (
        "Exported On: "
        + str(datetime.now())
        + "\n\n"
    )


    for msg in messages:

        text += (
            msg["role"].upper()
            + ":\n"
        )

        text += (
            msg["content"]
            + "\n\n"
        )


    return text



def create_pdf_export(messages):

    buffer = io.BytesIO()

    pdf = SimpleDocTemplate(
        buffer
    )


    styles = getSampleStyleSheet()

    elements = []


    elements.append(
        Paragraph(
            "Star's AI Chatbot",
            styles["Title"]
        )
    )


    elements.append(
        Spacer(1,20)
    )


    for msg in messages:

        content = (
            msg["role"].upper()
            + ": "
            + msg["content"]
        )


        elements.append(
            Paragraph(
                content.replace(
                    "\n",
                    "<br/>"
                ),
                styles["Normal"]
            )
        )


        elements.append(
            Spacer(1,10)
        )


    pdf.build(elements)


    buffer.seek(0)

    return buffer

# ==========================================
# LOAD ENV
# ==========================================
# ==========================================
# EXPORT SOURCE CODE
# ==========================================

def create_code_zip():

    buffer = io.BytesIO()

    with zipfile.ZipFile(
        buffer,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:


        files = [
            "app.py",
            "database.py",
            "style.css"
        ]


        for file in files:

            if os.path.exists(file):

                zip_file.write(file)


    buffer.seek(0)

    return buffer
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:

    st.error("GOOGLE_API_KEY not found.")

    st.stop()

genai.configure(api_key=api_key)

# Latest supported model
model = genai.GenerativeModel(
    "models/gemini-3.5-flash"
)

# ==========================================
# SESSION STATE
# ==========================================

if "session_id" not in st.session_state:

    chats = get_chats()

    if chats:

        st.session_state.session_id = chats[0][0]

    else:

        st.session_state.session_id = create_chat()

if "messages" not in st.session_state:

    st.session_state.messages = []

    rows = load_messages(
        st.session_state.session_id
    )

    for role, message in rows:

        st.session_state.messages.append(
            {
                "role": role,
                "content": message
            }
        )

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("💫 Star's AI")

    st.caption("Your Personal AI Assistant")

    st.divider()

    # -----------------------
    # New Chat
    # -----------------------

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        st.session_state.session_id = create_chat()

        st.session_state.messages = []

        st.rerun()

    st.divider()

    # -----------------------
    # Upload Image
    # -----------------------

    uploaded_image = st.file_uploader(
        "🖼 Upload Image",
        type=["png", "jpg", "jpeg"]
    )

    if uploaded_image:

        st.image(
            uploaded_image,
            use_container_width=True
        )

    st.divider()

    # -----------------------
    # Upload Voice
    # -----------------------

    uploaded_audio = st.file_uploader(
        "🎤 Upload Voice",
        type=["mp3", "wav", "m4a"]
    )

    if uploaded_audio:

        st.audio(uploaded_audio)

    st.divider()
    

    # -----------------------
    # Recent Chats
    # -----------------------

    st.subheader("Recent Chats")

    chats = get_chats()

    for chat_id, title in chats:

        col1, col2 = st.columns([4,1])

        with col1:

            if st.button(
                f"💬 {title}",
                key=f"chat_{chat_id}",
                use_container_width=True
            ):

                st.session_state.session_id = chat_id

                st.session_state.messages = []

                rows = load_messages(chat_id)

                for role, msg in rows:

                    st.session_state.messages.append(
                        {
                            "role": role,
                            "content": msg
                        }
                    )

                st.rerun()

        with col2:

            if st.button(
                "🗑",
                key=f"delete_{chat_id}"
            ):

                delete_chat(chat_id)

                chats = get_chats()

                if chats:

                    st.session_state.session_id = chats[0][0]

                    st.session_state.messages = []

                    rows = load_messages(
                        st.session_state.session_id
                    )

                    for role, msg in rows:

                        st.session_state.messages.append(
                            {
                                "role": role,
                                "content": msg
                            }
                        )

                else:

                    st.session_state.session_id = create_chat()

                    st.session_state.messages = []

                st.rerun()
    

    st.divider()

    st.button(
        "⚙️ Settings",
        use_container_width=True
    )


# ==========================================
# TITLE SECTION
# ==========================================

st.title("💫 Star's AI Chatbot")

st.write(
    "Your AI Universe Starts Here.."
)


st.divider()

st.subheader("📄 Export Chat")


code_zip = create_code_zip()


st.download_button(
    label="⬇ Download Source Code",
    data=code_zip,
    file_name="Stars_AI_Chatbot_Source_Code.zip",
    mime="application/zip",
    use_container_width=True
)

txt_data = create_txt_export(
    st.session_state.messages
)


st.download_button(
    label="⬇ Download TXT",
    data=txt_data,
    file_name="star_ai_chat.txt",
    mime="text/plain",
    use_container_width=True
)



pdf_data = create_pdf_export(
    st.session_state.messages
)


st.download_button(
    label="⬇ Download PDF",
    data=pdf_data,
    file_name="star_ai_chat.pdf",
    mime="application/pdf",
    use_container_width=True
)
# ==========================================
# DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ==========================================
# CHAT INPUT
# ==========================================

user_input = st.chat_input(
    "Ask something..."
)


if user_input:


    # -------------------------
    # Display User Message
    # -------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )


    save_message(
        st.session_state.session_id,
        "user",
        user_input
    )


    with st.chat_message("user"):

        st.markdown(user_input)



    # -------------------------
    # Auto Rename Chat
    # -------------------------

    messages = load_messages(
        st.session_state.session_id
    )


    if len(messages) == 1:


        chat_title = user_input[:35]


        if len(user_input) > 35:

            chat_title += "..."


        update_chat_title(
            st.session_state.session_id,
            chat_title
        )



    # -------------------------
    # Gemini Response
    # -------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Thinking..."
        ):


            try:

                conversation = []


                for msg in st.session_state.messages:

                    conversation.append(
                        {
                            "role": msg["role"],
                            "parts": [
                                msg["content"]
                            ]
                        }
                    )


                response = model.generate_content(
                    conversation
                )


                bot_response = response.text



            except Exception as e:


                bot_response = (
                    "Sorry, I encountered an error:\n\n"
                    + str(e)
                )



        st.markdown(
            bot_response
        )



    # -------------------------
    # Save Assistant Response
    # -------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": bot_response
        }
    )


    save_message(
        st.session_state.session_id,
        "assistant",
        bot_response
    )


    st.rerun()
# ==========================================
# IMAGE CHAT
# ==========================================

if uploaded_image:


    image = Image.open(
        uploaded_image
    )


    image_prompt = st.chat_input(
        "Ask something about this image..."
    )


    if image_prompt:


        # -------------------------
        # Show User Image
        # -------------------------

        with st.chat_message(
            "user"
        ):

            st.image(
                image,
                width=300
            )

            st.markdown(
                image_prompt
            )


        # -------------------------
        # Save User Message
        # -------------------------

        save_message(
            st.session_state.session_id,
            "user",
            "[IMAGE] " + image_prompt
        )


        st.session_state.messages.append(
            {
                "role": "user",
                "content": "[IMAGE] " + image_prompt
            }
        )



        # -------------------------
        # Gemini Vision
        # -------------------------

        with st.chat_message(
            "assistant"
        ):

            with st.spinner(
                "Analyzing image..."
            ):


                try:

                    response = model.generate_content(
                        [
                            image_prompt,
                            image
                        ]
                    )


                    image_response = response.text



                except Exception as e:


                    image_response = (
                        "Error analyzing image:\n"
                        + str(e)
                    )



            st.markdown(
                image_response
            )



        # -------------------------
        # Save AI Response
        # -------------------------

        save_message(
            st.session_state.session_id,
            "assistant",
            image_response
        )


        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": image_response
            }
        )


        st.rerun()
# ==========================================
# VOICE CHAT
# ==========================================


if uploaded_audio:


    st.audio(
        uploaded_audio
    )


    if st.button(
        "🎧 Convert Voice"
    ):


        with st.spinner(
            "Converting speech to text..."
        ):


            try:


                # Save uploaded audio temporarily

                audio_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".wav"
                )


                audio_file.write(
                    uploaded_audio.read()
                )


                audio_file.close()



                # Convert audio

                audio = AudioSegment.from_file(
                    audio_file.name
                )


                wav_path = (
                    audio_file.name
                    + ".wav"
                )


                audio.export(
                    wav_path,
                    format="wav"
                )



                # Speech Recognition

                recognizer = sr.Recognizer()


                with sr.AudioFile(
                    wav_path
                ) as source:


                    audio_data = recognizer.record(
                        source
                    )



                voice_text = recognizer.recognize_google(
                    audio_data
                )



                st.success(
                    "Converted Text:"
                )


                st.write(
                    voice_text
                )



            except Exception as e:


                st.error(
                    "Voice conversion failed:"
                )

                st.write(e)



        # -------------------------
        # Send Text to Gemini
        # -------------------------


        if "voice_text" in locals():


            save_message(
                st.session_state.session_id,
                "user",
                "[VOICE] " + voice_text
            )


            st.session_state.messages.append(
                {
                    "role":"user",
                    "content":"[VOICE] " + voice_text
                }
            )



            with st.chat_message(
                "assistant"
            ):


                with st.spinner(
                    "Thinking..."
                ):


                    response = model.generate_content(
                        voice_text
                    )


                    voice_response = response.text



                st.markdown(
                    voice_response
                )



            save_message(
                st.session_state.session_id,
                "assistant",
                voice_response
            )


            st.session_state.messages.append(
                {
                    "role":"assistant",
                    "content":voice_response
                }
            )


            st.rerun()
# ==========================================
# EXPORT FUNCTIONS
# ==========================================


def create_txt_export(messages):

    text = ""

    text += "Star's AI Chatbot\n"
    text += "=" * 30 + "\n\n"


    text += (
        "Exported On: "
        + str(datetime.now())
        + "\n\n"
    )


    for msg in messages:

        text += (
            msg["role"].upper()
            + ":\n"
        )

        text += (
            msg["content"]
            + "\n\n"
        )


    return text



