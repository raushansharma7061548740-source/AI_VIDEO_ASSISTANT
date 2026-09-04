# AI Video Assistant

AI Video Assistant is a Python project that helps users understand long videos or audio files quickly.

The user can provide a YouTube URL or a local audio/video file. The application processes the audio, converts it into smaller chunks, transcribes it using Sarvam AI, and then uses Mistral AI to generate useful information from the transcript.

It can generate:

- Title
- Summary
- Action items
- Key decisions
- Open questions

The project also includes a RAG system that allows users to ask questions about the video content.

## How it works

1. User provides a YouTube URL or local file.
2. The audio is downloaded or converted to WAV format.
3. The audio is split into smaller chunks.
4. Sarvam AI converts the audio into text.
5. All transcription chunks are combined into a complete transcript.
6. Mistral AI analyzes the transcript.
7. The transcript is stored in ChromaDB for RAG-based question answering.

## Tech Used

- Python
- LangChain
- Sarvam AI
- Mistral AI
- ChromaDB
- Hugging Face Embeddings
- yt-dlp
- FFmpeg
- Pydub

## Project Structure

```text
AI_VIDEO_ASSISTANT/
│
├── core/
│   ├── transcriber.py
│   ├── summarize.py
│   ├── extractor.py
│   ├── vector_stores.py
│   └── rag_engine.py
│
├── utlis/
│   └── audio_processing.py
│
├── main.py
├── requirements.txt
├── .env
└── .gitignore
