#!/usr/bin/env python3
"""
MongoDB용 샘플 데이터 생성 스크립트
"""

import random
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# MongoDB 설정
MONGO_URI = os.getenv("MONGO_URI", "mongodb://15.164.219.145:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "finance_app")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "purchase_history")

def create_sample_database():
    """MongoDB에 샘플 데이터 생성"""
    
    try:
        # MongoDB 연결
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # 기존 데이터 삭제 (선택사항)
        collection.delete_many({})
        print("기존 데이터 삭제 완료")
        
        # 샘플 데이터 설정 - 새로운 라벨 구조에 맞게 수정
        categories_with_labels = {
            '먹이': {
                'label': 'FOOD',
                'products': ['고급 사료', '영양 간식', '비타민', '칼슘 보충제', '프리미엄 먹이', '특수 영양식']
            },
            '간식': {
                'label': 'SNACK', 
                'products': ['초코송이', '사탕', '과자', '아이스크림', '젤리', '과일', '견과류', '요구르트']
            },
            '오락': {
                'label': 'ENTERTAINMENT',
                'products': ['TV 시청 1시간권', '게임시간', '유튜브 시청권', '영화감상권', '만화책', '보드게임']
            },
            '장난감': {
                'label': 'TOY',
                'products': ['레고', '인형', '자동차 장난감', '퍼즐', '슬라임', '로봇', '블록', '피규어']
            },
            '교육 및 문구': {
                'label': 'EDUCATION',
                'products': ['책', '문구세트', '학습지', '교육앱 이용권', '사전', '지도', '계산기', '노트']
            },
            '기타': {
                'label': 'ETC',
                'products': ['스티커', '색연필', '만들기키트', '포스터', '장식품', '열쇠고리', '뱃지', '카드']
            }
        }
        
        children = [
            'd0a188a3-e24e-4772-95f7-07e59ce8885e',  # 실제 데이터의 childId 형식에 맞춤
            'a1b2c3d4-e5f6-7890-abcd-ef1234567890',
            'b2c3d4e5-f6g7-8901-bcde-f23456789012'
        ]
        
        # 샘플 데이터 생성 (최근 90일)
        now = datetime.now()
        sample_data = []
        
        for child_id in children:
            for i in range(200):  # 아이당 200개 데이터
                # 날짜 생성 (최근 90일 내)
                days_ago = random.randint(0, 90)
                timestamp = now - timedelta(days=days_ago)
                
                # 시간대별 가중치 (방과 후 시간에 더 많은 구매)
                hour = random.randint(0, 23)
                hour_weight = 0.3
                if 15 <= hour <= 21:  # 오후 3시~밤 9시
                    hour_weight = 0.8
                elif 7 <= hour <= 14:  # 아침 7시~오후 2시
                    hour_weight = 0.5
                    
                # 가중치에 따라 데이터 생성 여부 결정
                if random.random() < hour_weight:
                    timestamp = timestamp.replace(hour=hour, minute=random.randint(0, 59))
                    
                    # 카테고리와 상품 선택
                    category_korean = random.choice(list(categories_with_labels.keys()))
                    category_info = categories_with_labels[category_korean]
                    product = random.choice(category_info['products'])
                    
                    # 가격 설정 (카테고리별 차등)
                    price_ranges = {
                        '먹이': (100, 300),
                        '간식': (30, 150),
                        '오락': (50, 300),
                        '장난감': (100, 1000),
                        '교육 및 문구': (80, 500),
                        '기타': (20, 200)
                    }
                    min_price, max_price = price_ranges[category_korean]
                    price = random.randint(min_price, max_price)
                    
                    # 수량 (대부분 1개, 간혹 2-3개)
                    cnt = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
                    
                    # MongoDB 구조에 맞는 데이터 생성
                    sample_data.append({
                        'type': 'npc',  # 실제 데이터 구조에 맞춤
                        'name': product,
                        'price': price,
                        'cnt': cnt,
                        'timestamp': timestamp,  # MongoDB에서는 datetime 객체를 직접 저장
                        'childId': child_id,  # camelCase 사용
                        'productId': f'product_{random.randint(10000, 99999)}',  # 랜덤 productId
                        'label': category_info['label'],  # FOOD, SNACK 등
                        '_class': 'com.popoworld.backend.market.entity.PurchaseHistory'  # Spring Data MongoDB 클래스
                    })
        
        # MongoDB에 데이터 삽입
        if sample_data:
            result = collection.insert_many(sample_data)
            print(f"✅ {len(result.inserted_ids)}건의 데이터가 MongoDB에 삽입되었습니다.")
        
        # 인덱스 생성 - childId 필드명 수정
        collection.create_index([("childId", 1), ("timestamp", -1)])
        collection.create_index([("timestamp", -1)])
        print("✅ 인덱스 생성 완료")
        
        print(f"📊 총 {len(sample_data)}건의 구매 데이터가 생성되었습니다.")
        print(f"👶 아이 목록: {', '.join(children)}")
        print(f"🏷️ 카테고리: {', '.join(list(categories_with_labels.keys()))}")
        print(f"🗄️ MongoDB URI: {MONGO_URI}")
        print(f"🗄️ Database: {MONGO_DB_NAME}")
        print(f"🗄️ Collection: {COLLECTION_NAME}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    create_sample_database()
