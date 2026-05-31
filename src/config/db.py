from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text, JSON, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
# from datetime import datetime

engine = create_engine(
    "sqlite:///users.db",
    connect_args={"check_same_thread": False}
)

sessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    emailid = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    studying_at = Column(String)

# class History(Base):
#     __tablename__="history"
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     created_at = Column(DateTime, server_default=func.now())


class Topics(Base):
    __tablename__="topics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    history_group = Column(Integer)
    collection = Column(String)
    topic_text = Column(String)
    topic_notes = Column(String)
    keywords = Column(JSON)
    subject = Column(String)

class Chat(Base):
    __tablename__="chats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer)
    usermessage = Column(String)
    modelmessage = Column(String)
    created_at = Column(DateTime)

class SubNotes(Base):
    __tablename__="subnotes"
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(String, ForeignKey("topics.id"))
    text = Column(String)


    
Base.metadata.create_all(bind=engine)


def get_db():
    db = sessionLocal()

    try:
        yield db

    finally:
        db.close()