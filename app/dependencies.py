from collections.abc import Generator
from sqlmodel import Session, SQLModel, create_engine, text

engine = create_engine("sqlite:///data/development.db", echo=True)

def initialize_database():
    from app.database import schema
    
    SQLModel.metadata.create_all(engine)
    
    with engine.connect() as connection:
        _ = connection.execute(text("PRAGMA foreign_key=ON"))

def get_session() -> Generator[Session]:
    with Session(engine) as session:
        yield session