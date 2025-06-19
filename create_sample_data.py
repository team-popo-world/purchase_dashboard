#!/usr/bin/env python3
"""
샘플 데이터 생성 스크립트
"""

import sqlite3
import random
from datetime import datetime, timedelta
import os

def create_sample_database():
    """샘플 데이터베이스와 데이터 생성"""
    
    # 데이터베이스 파일 경로
    db_path = os.path.join(os.path.dirname(__file__), 'purchase_data.db')
    
    # 기존 파일이 있으면 삭제
    if os.path.exists(db_path):
        os.remove(db_path)
        
    # 데이터베이스 연결
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 테이블 생성
    cursor.execute('''
        CREATE TABLE purchasehistory (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            cnt INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            child_id TEXT NOT NULL
        )
    ''')
    
    # 샘플 데이터 설정
    categories = ['간식', '오락', '장난감', '교육', '기타']
    products_by_category = {
        '간식': ['초코송이', '사탕', '과자', '아이스크림', '젤리', '과일', '견과류', '요구르트'],
        '오락': ['TV 시청 1시간권', '게임시간', '유튜브 시청권', '영화감상권', '만화책', '보드게임'],
        '장난감': ['레고', '인형', '자동차 장난감', '퍼즐', '슬라임', '로봇', '블록', '피규어'],
        '교육': ['책', '문구세트', '학습지', '교육앱 이용권', '사전', '지도', '계산기', '노트'],
        '기타': ['스티커', '색연필', '만들기키트', '포스터', '장식품', '열쇠고리', '뱃지', '카드']
    }
    
    children = ['child_001', 'child_002', 'child_003']
    
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
                category = random.choice(categories)
                product = random.choice(products_by_category[category])
                
                # 가격 설정 (카테고리별 차등)
                price_ranges = {
                    '간식': (30, 150),
                    '오락': (50, 300),
                    '장난감': (100, 1000),
                    '교육': (80, 500),
                    '기타': (20, 200)
                }
                min_price, max_price = price_ranges[category]
                price = random.randint(min_price, max_price)
                
                # 수량 (대부분 1개, 간혹 2-3개)
                cnt = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
                
                sample_data.append({
                    'id': f'purchase_{child_id}_{i}_{timestamp.strftime("%Y%m%d%H%M%S")}',
                    'type': category,
                    'name': product,
                    'price': price,
                    'cnt': cnt,
                    'timestamp': timestamp.isoformat(),
                    'child_id': child_id
                })
    
    # 데이터베이스에 삽입
    for data in sample_data:
        cursor.execute('''
            INSERT INTO purchasehistory 
            (id, type, name, price, cnt, timestamp, child_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id'], data['type'], data['name'], 
            data['price'], data['cnt'], data['timestamp'], data['child_id']
        ))
    
    # 커밋 및 연결 종료
    conn.commit()
    conn.close()
    
    print(f"✅ 샘플 데이터베이스가 생성되었습니다: {db_path}")
    print(f"📊 총 {len(sample_data)}건의 구매 데이터가 생성되었습니다.")
    print(f"👶 아이 목록: {', '.join(children)}")
    print(f"🏷️ 카테고리: {', '.join(categories)}")

if __name__ == "__main__":
    create_sample_database()
