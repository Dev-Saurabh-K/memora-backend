from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

def storeTextInVectorStore(text_notes: str, collection_name: str):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    
    splits = text_splitter.split_text(text_notes)
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    
    # Correctly initializing with collection_name
    vectorstore = Chroma.from_texts(
        texts=splits,
        embedding=embeddings,
        persist_directory="./chroma_db",
        collection_name=collection_name
    )
    return vectorstore


def retrieveAnswersFromTexts(query: str, collection_name: str) -> str:
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    # FIX: Pass the collection_name here so Chroma knows WHICH collection to load
    vectorstore = Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings,
        collection_name=collection_name  
    )

    # as_retriever now automatically searches only within the collection specified above
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    docs = retriever.invoke(query)
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    messages = [
        SystemMessage(content=f"You are a helpful AI assistant which answers user's questions using only the given data. Data: {docs}"),
        HumanMessage(content=f"Question: {query}")
    ]

    result = llm.invoke(messages)
    return result.content  # .content extracts just the string text from the AI Message object


# # --- TESTING THE ISOLATION ---

# # 1. Store data in "user123"
# storeTextInVectorStore("hi i am saurabh kumar", "user123")

# # 2. Querying "user123" -> This will work because the data exists here!
# print("Querying user123:")
# print(retrieveAnswersFromTexts("who am i?", "user123")) 

# print("\n" + "-"*30 + "\n")

# # 3. Querying "guest_collection" -> This will NOT find Saurabh because it's isolated.
# print("Querying guest_collection:")
# print(retrieveAnswersFromTexts("who am i?", "guest_collection"))