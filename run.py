import os
import sys
import datetime
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
from openai import OpenAI

client = OpenAI()
from audio_recorder_streamlit import audio_recorder

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

def transcribe(audio_file):
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    return transcription

def save_audio_file(audio_bytes, file_extension):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"audio_{timestamp}.{file_extension}"

    with open(file_name, "wb") as f:
        f.write(audio_bytes)

    return file_name

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = transcribe(audio_file)

    return transcript.text

def main():
    st.title("Whisper Transcription")

    tab1, tab2 = st.columns(2)

    # Record Audio tab
    with tab1:
        audio_bytes = audio_recorder()
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            save_audio_file(audio_bytes, "mp3")

    # Upload Audio tab
    with tab2:
        audio_file = st.file_uploader("Upload Audio", type=["mp3", "mp4", "wav", "m4a"])
        if audio_file:
            file_extension = audio_file.type.split('/')[1]
            save_audio_file(audio_file.read(), file_extension)

    # Transcribe button action
    if st.button("Transcribe"):
        audio_file_path = max(
            [f for f in os.listdir(".") if f.startswith("audio")],
            key=os.path.getctime,
        )

        transcript_text = transcribe_audio(audio_file_path)

        st.header("Transcript")
        st.write(transcript_text)

        with open("transcript.txt", "w") as f:
            f.write(transcript_text)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=transcript_text,
        )
        response.stream_to_file("output.mp3")

        # Display the generated audio
        st.audio("output.mp3", format="audio/mp3")

        st.download_button("Download Transcript", transcript_text)

if __name__ == "__main__":
    working_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(working_dir)
    main()
