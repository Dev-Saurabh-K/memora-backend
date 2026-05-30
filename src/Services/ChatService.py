from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

load_dotenv()

messages = [
    SystemMessage(content="You are a helpful AI tutor, answer the question asked in 1 or 2 precise sentence or in a one single paraghraph if instructed or needed"),
    ]

def store_vector_from_notes(notes: str)


def chat(query:str) -> str:
    model = ChatGoogleGenerativeAI(model='gemini-2.5-flash-lite', temperature = 0.1)
    # messages=[
    #     SystemMessage(content="You are a helpful AI tutor, answer the question asked in 1 or 2 precise sentence or in a one single paraghraph if instructed or needed"),
    #     HumanMessage(content=query)
    #     ]
    messages.append(
        HumanMessage(content=query))
    result = model.invoke(messages)

    messages.append(AIMessage(content=result.content))

    return result.content

