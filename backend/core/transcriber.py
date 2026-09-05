import os

from dotenv import load_dotenv
from sarvamai import SarvamAI


load_dotenv()

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

if not SARVAM_API_KEY:
    raise ValueError("SARVAM_API_KEY is not set")


client = SarvamAI(
    api_subscription_key=SARVAM_API_KEY
)


MODEL_NAME = "saaras:v3"


def transcribe_chunk(chunk_path: str) -> str:

    print(f"Transcribing: {chunk_path}")

    with open(chunk_path, "rb") as audio_file:

        response = client.speech_to_text.transcribe(
            file=audio_file,
            model=MODEL_NAME,
            language_code="unknown"
        )

    return response.transcript


def transcribe_all(chunks: list[str]) -> str:

    transcripts = []

    for i, chunk in enumerate(chunks):

        print(f"Transcribing chunk {i + 1}/{len(chunks)}")

        text = transcribe_chunk(chunk)

        transcripts.append(text)

    full_transcript = " ".join(transcripts)

    print("Transcription completed!")

    return full_transcript