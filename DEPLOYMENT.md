# Docker Compose 배포 가이드

## EC2 환경 설정

### 1. EC2 인스턴스 준비
```bash
# Docker 설치
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 프로젝트 배포
```bash
# 프로젝트 클론
git clone <your-repository-url>
cd purchase_dashboard

# 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 실제 값으로 변경

# 개발 환경 실행
docker-compose up -d

# 프로덕션 환경 실행
docker-compose -f docker-compose.prod.yml up -d
```

### 3. 보안 그룹 설정
- Port 80 (HTTP): 0.0.0.0/0
- Port 443 (HTTPS): 0.0.0.0/0  
- Port 22 (SSH): 관리자 IP만
- Port 8001 (API): 선택사항 (Nginx를 통해 프록시하는 경우 불필요)

### 4. SSL 인증서 설정 (선택사항)
```bash
# Let's Encrypt 사용 예시
sudo yum install -y certbot
sudo certbot certonly --standalone -d your-domain.com

# 인증서를 ssl 디렉토리로 복사
mkdir -p ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown ec2-user:ec2-user ssl/*
```

## 유용한 명령어

### 컨테이너 관리
```bash
# 로그 확인
docker-compose logs -f app
docker-compose logs -f mongodb

# 컨테이너 상태 확인
docker-compose ps

# 서비스 재시작
docker-compose restart app

# 전체 중지
docker-compose down

# 볼륨까지 삭제
docker-compose down -v
```

### 데이터베이스 접근
```bash
# MongoDB 컨테이너 접속
docker-compose exec mongodb mongo

# 특정 데이터베이스 접속
docker-compose exec mongodb mongo purchase_dashboard
```

### 백업 및 복원
```bash
# MongoDB 백업
docker-compose exec mongodb mongodump --db purchase_dashboard --out /data/backup/

# MongoDB 복원
docker-compose exec mongodb mongorestore --db purchase_dashboard /data/backup/purchase_dashboard/
```

## 모니터링

### 헬스 체크
- API 헬스 체크: http://your-domain.com/health
- MongoDB 연결 확인: 컨테이너 로그 검토

### 로그 모니터링
```bash
# 실시간 로그 모니터링
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f app
```

## 트러블슈팅

### 일반적인 문제
1. **포트 충돌**: 다른 서비스가 같은 포트를 사용하는 경우
2. **메모리 부족**: EC2 인스턴스 타입 확인
3. **권한 문제**: Docker 그룹 권한 확인
4. **네트워크 연결**: 보안 그룹 설정 확인

### 문제 해결 명령어
```bash
# 컨테이너 리소스 사용량 확인
docker stats

# 네트워크 확인
docker network ls
docker-compose exec app ping mongodb

# 이미지 재빌드
docker-compose build --no-cache app
```
