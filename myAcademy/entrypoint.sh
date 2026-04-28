#!/bin/sh
set -e

echo "PostgreSQL 연결 대기 중..."

python <<'PY'
import os
import time
import psycopg2

host = os.getenv("POSTGRES_HOST", "postgres_academy")
port = os.getenv("POSTGRES_PORT", "5432")
dbname = os.getenv("POSTGRES_DB", "academydb")
user = os.getenv("POSTGRES_USER", "academyuser")
password = os.getenv("POSTGRES_PASSWORD", "academypass")

for i in range(30):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        conn.close()
        print("PostgreSQL 연결 성공")
        break
    except Exception:
        print(f"DB 준비 대기 중... {i + 1}/30")
        time.sleep(2)
else:
    raise SystemExit("PostgreSQL 연결 실패")
PY

echo "Django 마이그레이션 실행..."
python manage.py makemigrations academy
python manage.py migrate

echo "정적 파일 수집..."
python manage.py collectstatic --noinput

echo "Gunicorn 서버 실행..."
gunicorn --bind 0.0.0.0:8000 academy_project.wsgi:application
