from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite 데이터베이스 설정
DATABASE_URL = "sqlite:///./purchase_data.db"

# 데이터베이스 엔진 생성
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite 전용 설정
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 데이터베이스 모델
class PurchaseHistory(Base):
    __tablename__ = "purchasehistory"
    
    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)  # 카테고리
    name = Column(String, nullable=False)  # 상품명
    price = Column(Integer, nullable=False)  # 개별가격
    cnt = Column(Integer, nullable=False)  # 구매개수
    timestamp = Column(DateTime, nullable=False)
    child_id = Column(String, nullable=False)

# 데이터베이스 의존성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
