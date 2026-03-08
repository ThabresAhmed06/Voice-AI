import io


def save_audio_file(audio_file):
    """
    Convert uploaded audio into a memory stream
    and attach filename so Whisper recognizes format.
    """

    audio_bytes = audio_file.read()

    audio_stream = io.BytesIO(audio_bytes)

    # IMPORTANT: give the stream a filename
    audio_stream.name = "speech.webm"

    return audio_stream