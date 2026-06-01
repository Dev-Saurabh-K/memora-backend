from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert teacher.

        Rules:
        1. Generate exactly 10 questions.
        2. Each question must have exactly 4 options.
        3. Only one option must be correct.
        4. Questions should match the difficulty level of the class.
        """
    ),
    (
        "human",
        """
        Please generate a multiple-choice quiz based on the following details:
        
        Topic Text: {topic}
        Subject: {subject}
        Class: {class_name}
        """
    )
])

class QuestionModel(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

class QuizModel(BaseModel):
    questions: List[QuestionModel]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

structured_llm = llm.with_structured_output(QuizModel)

chain = prompt | structured_llm

def generateQuiz(topic: str, subject: str, studying_at: str) ->QuizModel:
    return chain.invoke({
        "topic": topic,
        "subject": subject,
        "class_name": studying_at
    })

# quiz = generateQuiz(
#     "Half Adder Circuit",
#     "Computer Organization",
#     "B.Tech 2nd Year"
# )

# print(quiz.model_dump_json(indent=2))

# print(generateQuiz("half adder circuit","computer organization", "Btech 2nd year"))