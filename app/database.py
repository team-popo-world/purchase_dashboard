from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import asyncio
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# MongoDB 설정
MONGO_URI = os.getenv("MONGO_URI", "mongodb://15.164.219.145:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "finance_app")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "purchase_history")

# MongoDB 클라이언트 (동기)
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection = db[COLLECTION_NAME]

# MongoDB 클라이언트 (비동기)
async_client = AsyncIOMotorClient(MONGO_URI)
async_db = async_client[MONGO_DB_NAME]
async_collection = async_db[COLLECTION_NAME]

# 라벨 매핑
LABEL_MAPPING = {
    "FOOD": "먹이",
    "SNACK": "간식", 
    "ENTERTAINMENT": "오락",
    "TOY": "장난감",
    "EDUCATION": "교육 및 문구",
    "ETC": "기타"
}

# 데이터 모델
class PurchaseHistory(BaseModel):
    _id: Optional[str] = None  # MongoDB ObjectId
    type: str  # npc, item 등
    name: str  # 상품명
    price: int  # 개별가격
    cnt: int  # 구매개수
    timestamp: datetime
    childId: str  # camelCase 유지
    productId: str  # 상품 ID
    label: str  # FOOD, SNACK, ENTERTAINMENT, TOY, EDUCATION, ETC
    _class: Optional[str] = None  # Spring Data MongoDB 클래스 정보
    
    class Config:
        # MongoDB의 _id 필드 처리
        populate_by_name = True

# MongoDB 연결 테스트 및 초기화
def init_db():
    """MongoDB 연결 테스트 및 인덱스 생성"""
    try:
        # 연결 테스트
        client.admin.command('ping')
        print("MongoDB 연결 성공")
        
        # 인덱스 생성
        collection.create_index([("childId", 1), ("timestamp", -1)])
        collection.create_index([("timestamp", -1)])
        print("인덱스 생성 완료")
    except Exception as e:
        print(f"MongoDB 연결 오류: {e}")

# 데이터베이스 의존성 (호환성을 위해 유지)
def get_db():
    """MongoDB 컬렉션 반환"""
    return collection

def get_purchase_data(child_id: Optional[str] = None, days: int = 7) -> pd.DataFrame:
    """
    구매 데이터를 DataFrame으로 반환
    
    Args:
        child_id: 특정 아이 ID (None이면 모든 아이)
        days: 조회할 일수
    
    Returns:
        pd.DataFrame: 구매 데이터
    """
    try:
        # 날짜 필터 생성
        start_date = datetime.now() - timedelta(days=days)
        
        # MongoDB 쿼리 조건
        query = {"timestamp": {"$gte": start_date}}
        
        # child_id가 지정된 경우 필터 추가
        if child_id:
            query["childId"] = child_id
        
        # MongoDB에서 데이터 조회
        cursor = collection.find(query).sort("timestamp", -1)
        documents = list(cursor)
        
        if not documents:
            return pd.DataFrame(columns=['_id', 'type', 'name', 'price', 'cnt', 'timestamp', 'childId', 'productId', 'label', 'label_korean'])
        
        # DataFrame으로 변환
        df = pd.DataFrame(documents)
        
        # _class 필드 제거 (Spring Data MongoDB 필드)
        if '_class' in df.columns:
            df = df.drop('_class', axis=1)
        
        # label을 한국어로 매핑한 컬럼 추가
        if 'label' in df.columns:
            df['label_korean'] = df['label'].map(LABEL_MAPPING).fillna(df['label'])
        
        # 카테고리 컬럼 추가 (type을 한국어로 매핑)
        if 'type' in df.columns:
            df['category'] = df['type']  # 기본적으로 type 값 사용
        
        # 호환성을 위해 child_id 컬럼 추가 (childId를 복사)
        if 'childId' in df.columns:
            df['child_id'] = df['childId']
        
        # 데이터 타입 변환
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0).astype(int)
        if 'cnt' in df.columns:
            df['cnt'] = pd.to_numeric(df['cnt'], errors='coerce').fillna(0).astype(int)
        
        return df
        
    except Exception as e:
        print(f"데이터 조회 오류: {e}")
        return pd.DataFrame(columns=['_id', 'type', 'name', 'price', 'cnt', 'timestamp', 'childId', 'productId', 'label', 'label_korean', 'category', 'child_id'])


# 비동기 함수들
async def get_purchase_data_async(child_id: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
    """
    비동기적으로 구매 데이터 조회
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        query = {"timestamp": {"$gte": start_date}}
        
        if child_id:
            query["childId"] = child_id
        
        cursor = async_collection.find(query).sort("timestamp", -1)
        documents = await cursor.to_list(length=None)
        
        # _id 필드를 문자열로 변환하고 _class 필드 제거
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            if '_class' in doc:
                del doc['_class']
            # 한국어 라벨 추가
            if 'label' in doc:
                doc['label_korean'] = LABEL_MAPPING.get(doc['label'], doc['label'])
        
        return documents
        
    except Exception as e:
        print(f"비동기 데이터 조회 오류: {e}")
        return []

async def insert_purchase_data_async(data: Dict[str, Any]) -> bool:
    """
    비동기적으로 구매 데이터 삽입
    """
    try:
        result = await async_collection.insert_one(data)
        return result.inserted_id is not None
    except Exception as e:
        print(f"데이터 삽입 오류: {e}")
        return False

def insert_purchase_data(data: Dict[str, Any]) -> bool:
    """
    동기적으로 구매 데이터 삽입
    """
    try:
        result = collection.insert_one(data)
        return result.inserted_id is not None
    except Exception as e:
        print(f"데이터 삽입 오류: {e}")
        return False
