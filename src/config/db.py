from sqlalchemy import create_engine, Column, Integer,String,Text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread": False})
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    emailid = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    studyingAt = Column(String)
    # created_at 

class QuizModel(Base):
    """Quiz table"""
    __tablename__ = "quizzes"
    
    user_id = Column(Integer, primary_key=True)
    topic = Column(String, index=True)
    difficulty = Column(String, default="medium")
 
class QuestionModel(Base):
    __tablename__ = "questions"
    
    user_id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer)
    question_text = Column(Text)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String)
 
class AnswerModel(Base):
    __tablename__ = "answers"
    
    user_id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer)
    question_id = Column(Integer)
    user_answer = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
