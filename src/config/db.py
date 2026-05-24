from sqlalchemy import create_engine, Column, Integer,String, ForeignKey, DateTime
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



class Chat(Base):
    __tablename__="chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    usermessage = Column(String)
    modelmessage = Column(String)
    created_at = Column(DateTime)
    
Base.metadata.create_all(bind=engine)

def get_chatdb():
    chatdb = sessionLocal()
    try:
        yield chatdb
    finally:
        chatdb.close()


def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()
