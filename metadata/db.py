from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# SQLite DB
DATABASE_URL = "sqlite:///../metadata/papers.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Model for paper metadata
class Paper(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text)
    keywords = Column(Text)
    filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create the table
def init_db():
    Base.metadata.create_all(bind=engine)

# Utility to add a paper
def add_paper(paper_id, title, summary, keywords, filename):
    session = SessionLocal()
    paper = Paper(
        id=paper_id,
        title=title,
        summary=summary,
        keywords=",".join(keywords),
        filename=filename
    )
    session.add(paper)
    session.commit()
    session.close()

# Utility to get all papers
def list_papers():
    session = SessionLocal()
    papers = session.query(Paper).all()
    session.close()
    return papers

# Utility to fetch paper by ID
def get_paper(paper_id):
    session = SessionLocal()
    paper = session.query(Paper).filter(Paper.id == paper_id).first()
    session.close()
    return paper
