from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough,RunnableLambda

import os

from langchain_core.rate_limiters import InMemoryRateLimiter

#rate_limiter = InMemoryRateLimiter(
#   requests_per_second=0.5,  # 1 request every 2 seconds
 #   max_bucket_size=1,
#)

def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2,
    )

def split_transcript(transcript : str)-> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=300
    )

    return splitter.split_text(transcript)

def summarize(transcript : str) -> str:
    llm = get_llm()

    map_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "summarize this portion of a metting transcript concisely."),
            ("human","{text}")
        ]
    )

    map_chain = map_prompt | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    chunk_summaries = [map_chain.invoke({"text" : chunk}) for chunk in chunks]

    combined = "\n\n".join(chunk_summaries)


    combined_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "you are an expert meeting summarizer. combine these partial summaries"
                "into one final professional meeting summary in bullet points.",
            ),
            ("human","{text}")
        ]
    )

    combined_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x : {"text" : x}) | combined_prompt | llm |StrOutputParser()
    )

    return combined_chain.invoke(combined)


def generate_title(transcript : str)->str:
    llm = get_llm()

    title_chain = (
         RunnablePassthrough() | RunnableLambda(lambda x : {"text" : x}) 
         | ChatPromptTemplate. from_messages([
            (
                "system",
                "based on the message transcript, generate a short profrssional meeting title"
                "(max 8 words ). only return the title , nothing else",
            ),
            ("human","{text}"),
         ])
         |llm | StrOutputParser()
    )

    return title_chain.invoke(transcript[:2000])