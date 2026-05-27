from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

load_dotenv()

class NotesStruct(BaseModel):
    paragraph: str = Field(
        description=(
            "A comprehensive, highly detailed notes paragraph explaining the core concepts. "
            "The style must be encyclopedic, factual, and informative, structured similarly to a Wikipedia article entry."
        )
    )
    keywords: List[str] = Field(
        description=(
            "A list of key terms, specific terminology, or named entities extracted directly from "
            "the paragraph. Focus on words holding strong technical, historical, or context-specific meaning. "
            "Examples: 'transpiration', 'sparkling', 'William Shakespeare'."
        ),
        min_length=1 
    )

prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        "You are an authoritative textbook containing exhaustive knowledge. "
        "Your goal is to provide comprehensive, factual information on the user's requested topic."
    ),
    (
        "human", 
        "Generate a highly detailed encyclopedic note with its core technical keywords for the topic: {topic} and subject: {subject}"
    )
])


llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash-lite", temperature = 0)
structured_llm = llm.with_structured_output(NotesStruct, method="json_schema")

chain = prompt | structured_llm
def notes_generator(topic: str, subject: str) -> str:
    result_object = chain.invoke({"topic":topic, "subject":subject})
    return result_object.model_dump_json(indent=4)
    # return result_object

# print(notes_generator("autotrophs","biology"))

    

