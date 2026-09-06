# AI Video Assistant

This is a small project I built to save time on watching long videos or meeting recordings. You give it a YouTube link or a video/audio file, and it gives you back:

- a short title
- a summary
- action items (with who's responsible and the deadline, if mentioned)
- key decisions that were made
- open questions that still need answers
- and a chat box at the end where you can ask questions about the video and get answers based only on what was actually said

## Why I built it this way

I started this with LangChain and it worked fine, but two things kept annoying me:

1. I was running Whisper locally for transcription and it was just too slow, especially on longer videos.
2. I was using Mistral for the summarizing/extracting part, and I kept running into two problems — rate limit errors (too many requests too fast) and the model running out of context space on longer transcripts.

So I switched things around:
- Whisper (local) → Sarvam AI's speech-to-text API. It's fast and honestly does a better job with Hindi/Hinglish audio than Whisper does.
- Mistral → Gemini 2.5 Flash. It has a much bigger context window, so long transcripts don't break it, and I've had way fewer rate limit issues.

For the long transcripts, instead of throwing the whole thing at the model in one go, I split it into smaller pieces, summarize each piece separately, and then combine those mini-summaries into one final result. This is usually called a "map-reduce" approach and it's the reason a 40-minute video doesn't crash the pipeline.

## What it actually does, step by step

1. You give it a YouTube link or a local file.
2. If it's a YouTube link, it downloads just the audio. If it's a local file, it converts it to a clean `.wav` file.
3. That audio gets cut into smaller chunks (long audio needs to be split up before sending it for transcription).
4. Each chunk gets transcribed by Sarvam AI, and all the pieces get joined back into one full transcript.
5. From that transcript, it generates the title, summary, action items, decisions, and open questions — these all happen using the transcript, mostly done in parallel since they don't depend on each other.
6. The transcript also gets stored in a vector database (Chroma) so you can ask it questions afterward and get answers grounded in the actual content, not the model just guessing.

## What it's built with

- **LangChain** – ties all the pieces (prompts, models, chains) together
- **Gemini 2.5 Flash** – the LLM doing the summarizing, extracting, and answering questions
- **Sarvam AI (Saaras model)** – converts speech to text
- **Chroma** – stores the transcript so it can be searched later for the chat feature
- **HuggingFace embeddings** (`all-MiniLM-L6-v2`) – turns text into vectors for Chroma to search
- **yt-dlp** – downloads audio from YouTube
- **pydub + ffmpeg** – handles audio conversion and chunking
- **uv** – manages the Python packages for this project

## Folder layout

```
AI-VIDEO-ASSISTANT/
├── core/
│   ├── extractor.py       # pulls out action items, decisions, questions
│   ├── summarize.py       # builds the summary and the title
│   ├── transcriber.py     # talks to Sarvam AI to get the transcript
│   ├── rag_engine.py      # handles the "chat with your video" part
│   └── vector_stores.py   # sets up and loads the Chroma database
├── utils/
│   └── audio_processing.py   # download, convert, and chunk the audio
├── downloads/             # where audio files get saved (not committed to git)
├── vector_db/             # the saved Chroma database (not committed to git)
├── main.py                # run this file to start everything
├── .env                   # your API keys go here (not committed to git)
└── README.md
```


## Things worth knowing before you use it

- If a video is long (30+ minutes), the summarizing and extracting steps break the transcript into chunks first, so it doesn't overload the model. This is intentional, not a bug.
- The audio chunks made during processing need to stay reasonably short, otherwise Sarvam's transcription API might reject them. If you're processing really long files, look into Sarvam's batch API instead of the regular one.
- The Chroma database (`vector_db/`) doesn't reset automatically between runs. If you want to start fresh with a new file, delete that folder first.
- If you start seeing "429 rate limit" errors, it usually means you're sending requests to the API faster than it allows. Adding a small delay or a rate limiter between calls fixes it.

## Stuff I still want to add
- it will work very good at vs code terminal but when i deployed this i face many problems like ai cannot use the youtube link.so i decided to step down currently
- A way to process multiple files at once instead of one at a time
- Figuring out who said what (speaker labels) in the transcript
- Being able to export the summary and action items as a PDF
