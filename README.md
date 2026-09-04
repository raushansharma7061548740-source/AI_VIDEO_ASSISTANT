# AI Video Assistant

AI Video Assistant is a Python project that helps users understand long videos or audio files quickly.

A Python-based application that processes YouTube videos or local audio/video files and converts them into useful, searchable information.

The application extracts audio, splits it into manageable chunks, transcribes the content using Sarvam AI, and uses an LLM to generate summaries and extract important information such as action items, key decisions, and open questions.

The transcript is also stored in a vector database, allowing users to ask questions about the video using a RAG pipeline.

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

YouTube URL / Local File
            │
            ▼
     Audio Processing
            │
            ▼
      Audio Chunking
            │
            ▼
   Sarvam AI Transcription
            │
            ▼
     Full Transcript
            │
      ┌─────┴──────┐
      ▼            ▼
 LLM Analysis    ChromaDB
      │            │
      ▼            ▼
Summary, Title    RAG Question Answering
Action Items
Decisions
Questions


Current Limitations

Long videos can take time because audio chunks are transcribed individually.
Processing speed depends on the API response time.
YouTube downloading depends on yt-dlp and YouTube restrictions.
API rate limits may affect processing large transcripts.

Author

Raushan Kumar
