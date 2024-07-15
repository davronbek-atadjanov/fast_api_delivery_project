from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# PostgreSQL ma'lumotlar bazasiga bog'lanish uchun engine yaratamiz
engine = create_engine('postgresql://postgres:12345@localhost/delivery_db', echo=True)

# Declarative base yaratamiz
Base = declarative_base()

# Session yaratamiz
session = sessionmaker()
# session = session(bind=engine) # buni database da ham yozak bo'ladi hamma vaqt route da yozmaslik uchun