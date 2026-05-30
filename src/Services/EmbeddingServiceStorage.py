from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()


def storeTextInVectorStore(text_notes: str, collection_name:str):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    
    splits = text_splitter.split_text(text_notes)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    
    vectorstore = Chroma.from_texts(
        texts=splits,
        embedding=embeddings,
        persist_directory="./chroma_db",
        collection_name=collection_name
    )

    return vectorstore


print(storeTextInVectorStore("hi i am saurabh kumar", "user123"))

def retrieveAnswersFromTexts(query: str, collection_name:str)-> str:
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )

    retriver = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3},
        collection_name=collection_name
    )

    docs = retriver.invoke(query)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    messages = [
        SystemMessage(content=f"You are a help AI assistant which answer users question for a using only the given data only.  data:{docs}"),
        HumanMessage(content=f"Question:{query}")
    ]

    result = llm.invoke(messages)
    return result
    # return docs

print(retrieveAnswersFromTexts("who am i?", "hi"))

# def textResponseLLM(info: list[Document], question: str, )