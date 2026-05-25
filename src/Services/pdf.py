from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
# from GeneratePlan import generateTopic

load_dotenv()

# loader = PyPDFLoader("data/syllabus.pdf")
# docs = loader.load()
# print(generateTopic(docs))
# def store_vector():
#     loader = PyPDFLoader("data/syllabus.pdf")
#     docs = loader.load()


#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200

#     )

#     chunks = splitter.split_documents(docs)


#     embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

#     Chroma.from_documents(
#         documents=chunks,
#         embedding=embeddings,
#         persist_directory="./db"
#     )
#     print("vector db created")





def getRagOverVectorDb(query: str):
    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vectorstore = Chroma(persist_directory="./db", embedding_function=embeddings)
    results = vectorstore.similarity_search(query=query, k=3)
    # print(results[0].page_content)
    return results

# print(getRagOverVectorDb("syllabus topic of mathematics semester 1"))


