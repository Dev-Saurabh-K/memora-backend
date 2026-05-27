from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
# from pdf import getRagOverVectorDb

load_dotenv()

class TopicCard(BaseModel):
    index: int = Field(
        description="The strict sequential order number of this specific topic, starting at 1 and incrementing by 1 for each subsequent topic (e.g., 1, 2, 3... N). No duplicates or gaps allowed."
    )
    title: str = Field(
        description="The atomic title of a single topic or sub-topic (e.g., 'Introduction to Cells', 'Cell Wall', 'Prokaryotic Cells'). Do not combine multiple concepts here."
    )
    subject: str = Field(
        description="The subject for which current topic belongs (e.g., 'Biology','Maths','DSA')"
    )

class SyllabusPlan(BaseModel):
    topics: List[TopicCard] = Field(description="An ordered list of all extracted topics parsed from the input text.")

prompt = ChatPromptTemplate.from_messages([
    (
        "system", 
        "You are an expert syllabus and notes analyzer. Your task is to break down the provided text into a highly granular, logical learning sequence of individual topics.\n\n"
        "Strict Formatting Rules:\n"
        "1. Break down complex text into individual, atomic topics. Each topic must represent exactly ONE discrete concept.\n"
        "2. Do NOT group multiple distinct concepts into a single index.\n"
        "3. The 'index' field must represent the strict chronological teaching sequence. It MUST start at 1 for the first topic, 2 for the second, 3 for the third, and seamlessly continue to whatever number is required to cover the text (e.g., up to 10, 15, or more).\n"
        "4. Ensure there are no gaps, jumps, or duplicates in the index sequence."
    ),
    ("human", "{unstructured_input}")
])

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

structured_llm = llm.with_structured_output(SyllabusPlan)

chain = prompt | structured_llm

def generateTopic(input: str) -> List[TopicCard]:
    return chain.invoke({"unstructured_input": input})

# print(generateTopic("half adder circuit"))


# print(generateTopic(getRagOverVectorDb("physics 1st year syllabus")[0].page_content))

