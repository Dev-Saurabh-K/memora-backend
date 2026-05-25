
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

def create_rag_chain():
    
    loader = TextLoader("data/notes.txt")
    documents = loader.load()


    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap=200
    )

    splits = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

    retriever = vectorstore.as_retriever(search_kwargs={"k":3})


    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer , say that you don't know.\n\n"
        "Context:\n{context}"
    )

    # question = input("ask: \n")

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}"),
    ])
    return (
        {
            "context": retriever | format_docs, "question": RunnablePassthrough() 
        } 
        | prompt 
        | llm 
        | StrOutputParser()
    )

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = create_rag_chain()

def ask_question(query: str) -> str:
    response = rag_chain.invoke(query)
    return response


# print(ask_question("what is amoni acids?"))