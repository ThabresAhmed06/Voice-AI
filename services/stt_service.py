import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)


def transcribe_audio(audio_stream):
    """
    Transcribe audio using Whisper.
    Works with both Flask uploads and evaluation files.
    """

    response = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_stream,
        language="en",
        temperature=0
    )

    return response.text.strip()