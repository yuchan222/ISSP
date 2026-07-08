#!/bin/bash

# ISSP 자동 실행 스크립트
# 환경변수 로드 및 Streamlit 백그라운드 실행

echo "====================================="
echo " ISSP 시작 - $(date)"
echo "====================================="

# 프로젝트 경로
PROJECT_DIR="/home/yuchan/issp"
LOG_FILE="$PROJECT_DIR/logs/issp.log"

# 가상환경 활성화
source "$PROJECT_DIR/venv/bin/activate"

# 환경변수 로드
set -a
source "$PROJECT_DIR/.env"
set +a

# 기존 실행 중인 Streamlit 종료
pkill -f "streamlit run" 2>/dev/null
sleep 1

# Streamlit 백그라운드 실행 (nohup)
nohup streamlit run "$PROJECT_DIR/app.py" \
    --server.port 8501 \
    --server.headless true \
    >> "$LOG_FILE" 2>&1 &

echo "ISSP 실행됨 (PID: $!)"
echo "로그: $LOG_FILE"
echo "접속: http://localhost:8501"

# 신호 감지 및 자동 알림
cd "$PROJECT_DIR" && python3 -m modules.alert