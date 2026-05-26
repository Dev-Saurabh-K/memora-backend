import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional

load_dotenv()

apikey = os.getenv("GOOGLE_API_KEY2")


class Subnotes(BaseModel):
    info: str = Field(
        description="The core definition or primary short note explaining the keyword based strictly on the context."
        )
    note: Optional[str] = Field(
        default=None,
        description="Additional context, usage notes, or secondary insights regarding the keyword. Optional."
    )
    fact:Optional[str] = Field(
        default=None,
        description="An interesting, objective fact or key takeaway explicitly stated about the keyword. Optional."
    )

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert, concise digital dictionary. Your task is to provide clear, "
        "easy-to-understand definitions or short notes for a given keyword.\n\n"
        "CRITICAL RULES:\n"
        "1. Accuracy: Your explanation MUST align perfectly with the provided context.\n"
        "2. Scope: Do not assume or extrapolate meanings outside of the given context.\n"
        "3. Tone: Keep it objective, professional, and accessible."
    ),
    (
        "human",
        "Please provide a short note and definition based on the following details:\n\n"
        "## Keyword\n"
        "{keyword}\n\n"
        "## Provided Context\n"
        "{context}\n\n"
        "## Expected Output\n"
        "Provide a concise summary/definition matching the context above."
    )
])

llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash-lite", temperature = 0)

structured_llm = llm.with_structured_output(Subnotes)

chain = prompt | structured_llm 


def generate_sub_notes(keyword: str, context: str ) -> Subnotes:
    return chain.invoke({"keyword": keyword, "context": context})

# print(generate_sub_notes("gazed-and", "The waves beside them danced; but they Out-did the sparkling waves in glee: A poet could not but be gay,In such a jocund company: I gazed—and gazed—but little thought What wealth the show to me had brought:"))
