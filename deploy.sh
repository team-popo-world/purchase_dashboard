#!/bin/bash

# AWS EC2에서 Docker Compose를 사용한 자동 배포 스크립트

set -e

echo "🚀 Purchase Dashboard 배포 시작..."

# 환경 변수 설정
ENVIRONMENT=${1:-development}
COMPOSE_FILE="docker-compose.yml"

if [ "$ENVIRONMENT" = "production" ]; then
    COMPOSE_FILE="docker-compose.prod.yml"
fi

echo "📝 환경: $ENVIRONMENT"
echo "📄 Docker Compose 파일: $COMPOSE_FILE"

# Docker 및 Docker Compose 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    echo "다음 명령어를 실행하여 Docker를 설치하세요:"
    echo "sudo yum update -y && sudo yum install -y docker"
    echo "sudo service docker start"
    echo "sudo usermod -a -G docker ec2-user"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다."
    echo "다음 명령어를 실행하여 Docker Compose를 설치하세요:"
    echo 'sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose'
    echo "sudo chmod +x /usr/local/bin/docker-compose"
    exit 1
fi

# 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하여 .env 파일을 생성합니다."
    cp .env.example .env
    echo "📝 .env 파일을 편집하여 실제 값으로 변경해주세요."
    echo "nano .env"
    read -p "계속하시겠습니까? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 기존 컨테이너 정지
echo "🔄 기존 컨테이너 정지 중..."
docker-compose -f $COMPOSE_FILE down

# 이미지 빌드
echo "🔨 Docker 이미지 빌드 중..."
docker-compose -f $COMPOSE_FILE build

# 컨테이너 시작
echo "🚢 컨테이너 시작 중..."
docker-compose -f $COMPOSE_FILE up -d

# 헬스 체크
echo "🔍 서비스 상태 확인 중..."
sleep 10

# 컨테이너 상태 확인
docker-compose -f $COMPOSE_FILE ps

# API 헬스 체크
echo "🏥 API 헬스 체크..."
timeout=30
counter=0

while [ $counter -lt $timeout ]; do
    if curl -s http://localhost/health > /dev/null; then
        echo "✅ API 서버가 정상적으로 실행 중입니다!"
        echo "🌐 API 주소: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
        break
    else
        echo "⏳ API 서버 시작 대기 중... ($counter/$timeout)"
        sleep 2
        counter=$((counter + 2))
    fi
done

if [ $counter -eq $timeout ]; then
    echo "❌ API 서버 헬스 체크 실패"
    echo "📋 로그 확인:"
    docker-compose -f $COMPOSE_FILE logs app
    exit 1
fi

echo "🎉 배포 완료!"
echo ""
echo "📊 유용한 명령어:"
echo "  로그 확인: docker-compose -f $COMPOSE_FILE logs -f"
echo "  컨테이너 상태: docker-compose -f $COMPOSE_FILE ps"
echo "  서비스 재시작: docker-compose -f $COMPOSE_FILE restart"
echo "  전체 중지: docker-compose -f $COMPOSE_FILE down"
echo ""
echo "🔗 접속 URL:"
echo "  API: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "  Docs: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/docs"
