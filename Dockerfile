# ✅ 1. Base image
FROM python:3.10-slim

# ✅ 2. 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    git \
    curl \
    && apt-get clean

# ✅ 3. 작업 디렉토리 설정
WORKDIR /app

# ✅ 4. requirements.txt 복사 및 설치
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ✅ 5. 앱 소스 코드 전체 복사
COPY . .

# ✅ 6. 환경 변수 설정
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true \
    CONFIG_PATH="/app/config.toml"

# ✅ 7. 포트 설정 (Streamlit + FastAPI 동시 지원 시)
EXPOSE 8501 8000

# ✅ 8. 시작 커맨드: Streamlit or FastAPI 선택적 실행
# -- 아래 중 하나만 활성화하거나, supervisord 구조로 병렬 실행할 수 있음
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# 👉 필요 시 FastAPI 서버로 전환:
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]