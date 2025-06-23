// MongoDB 초기화 스크립트
// 데이터베이스 및 기본 컬렉션 생성

// 데이터베이스 생성 및 선택
db = db.getSiblingDB('purchase_dashboard');

// 사용자 생성 (앱에서 사용할 계정)
db.createUser({
  user: 'app_user',
  pwd: 'app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'purchase_dashboard'
    }
  ]
});

// 기본 컬렉션 생성
db.createCollection('purchases');
db.createCollection('analytics');
db.createCollection('users');

// 인덱스 생성
db.purchases.createIndex({ "user_id": 1 });
db.purchases.createIndex({ "purchase_date": 1 });
db.purchases.createIndex({ "category": 1 });

// 샘플 데이터 삽입 (개발용)
db.purchases.insertMany([
  {
    user_id: "user_001",
    item_name: "아이 장난감",
    category: "완구",
    price: 25000,
    purchase_date: new Date("2024-01-15"),
    child_age: 5
  },
  {
    user_id: "user_001", 
    item_name: "학습 교재",
    category: "교육",
    price: 15000,
    purchase_date: new Date("2024-01-20"),
    child_age: 5
  }
]);

print("MongoDB 초기화 완료!");
